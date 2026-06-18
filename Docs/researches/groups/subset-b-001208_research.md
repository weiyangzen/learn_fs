# subset-b-001208 research

This grouped report covers Linux CPUFreq core, demand-based governors, simple governors, stats/table helpers, and several platform cpufreq drivers under `sources/distributed-fs/ceph-client/drivers/cpufreq`. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq.c

Purpose: implements the CPUFreq core: global cpufreq driver registration, per-policy lifetime, sysfs policy attributes, frequency transition notification, governor registration/switching, CPU hotplug, suspend/resume, boost handling, frequency invariance hooks, and policy refresh/update entry points used by drivers, governors, thermal cooling, scheduler code, and user space.

Important APIs and control flow: exported APIs include `disable_cpufreq()`, `get_cpu_idle_time()`, `cpufreq_generic_init()`, `cpufreq_cpu_get()/put()`, transition helpers `cpufreq_freq_transition_begin()/end()`, `cpufreq_driver_resolve_freq()`, `cpufreq_driver_target()`, notifier registration, fast-switch helpers, `cpufreq_register_governor()/unregister_governor()`, `cpufreq_update_policy()`, `cpufreq_update_limits()`, boost helpers, and `cpufreq_register_driver()/unregister_driver()`. Driver registration validates callback combinations, creates boost sysfs if supported, enables scheduler frequency invariance for target-style drivers, registers a CPU subsystem interface, initializes online CPU policies, and installs CPU hotplug callbacks. Policy online allocates or revives a `cpufreq_policy`, invokes driver `init`/`online`, validates frequency tables, creates QoS requests and sysfs files, registers stats/cooling/energy-model hooks, initializes the governor or setpolicy mode, and emits uevents. Target changes resolve the requested frequency against policy limits and frequency tables, then call driver `target`, `target_index`, optional intermediate callbacks, or fast-switch paths with transition notifications as required.

State and persistence behavior: global state includes `cpufreq_driver`, per-CPU `cpufreq_cpu_data`, active/inactive policy list, governor list, notifier chains, global cpufreq kobject, `default_governor`, suspend flag, fast-switch count, and per-CPU `cpufreq_pressure`. Per-policy state persists in kobjects, cpumasks, frequency constraints, current/min/max frequencies, governor data, stats, boost requests, transition lock/wait state, and cached frequency-table resolution. Sysfs writes persist through policy QoS requests rather than directly overwriting min/max. Hotplug preserves `last_governor` or `last_policy` across lightweight offline/online where the driver supports it.

Dependencies and integration points: depends on CPU subsystem devices, PM QoS/frequency constraints, cpumasks, kobjects/sysfs, SRCU and blocking notifier chains, scheduler frequency scale/trace hooks, `cpu_cooling`, energy model registration, cpuhp, clocks through generic drivers, and governor modules. It is the central integration point consumed by all files in this group plus external cpufreq drivers and governors.

Risks and test signals: risks include callback-combination validation gaps in third-party drivers, races around concurrent policy min/max reads during updates, governor replacement rollback failures, notifier incompatibility with fast switching, stale current-frequency detection for drivers with imprecise `get`, sysfs lifetime races if policy inactivity checks fail, and boost rollback if one policy rejects a global boost transition. Test signals include boot with a target-index driver, online/offline of all CPUs in shared and per-CPU policies, sysfs min/max/governor/setspeed writes, transition notifier ordering, stats updates, suspend/resume governor stop/start, boost sysfs toggling, frequency invariance enabled/disabled on driver register/unregister, and absence of policy kobject leaks after CPU removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_conservative.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_conservative.c

Purpose: implements the `conservative` dynamic CPUFreq governor. It reuses the common demand-based-switching engine but changes frequency gradually by configurable percentage steps, making it less aggressive than `ondemand` and oriented toward battery-sensitive systems.

Important APIs and control flow: `cs_dbs_update()` obtains maximum policy load from `dbs_update()`, bounds cached `requested_freq` against current policy limits, applies idle-period catch-up decreases, increases by `freq_step` when load exceeds `up_threshold`, and decreases by `freq_step` after `sampling_down_factor` intervals below `down_threshold`. Sysfs stores validate `sampling_down_factor`, `up_threshold`, `down_threshold`, `ignore_nice_load`, and `freq_step`; threshold stores maintain `down_threshold < up_threshold`. `cs_alloc/free/init/exit/start/limits` provide the `dbs_governor` callbacks, and `cpufreq_governor_init/exit` registers the governor.

State and persistence behavior: per-policy `cs_policy_dbs_info` stores `down_skip` and `requested_freq`; common `dbs_data` stores sampling rate, ignore-nice flag, up threshold, and `cs_dbs_tuners`. Tunables may be per-policy or shared globally depending on the cpufreq driver flag handled by common governor code. Runtime frequency intent persists as `requested_freq` and is reset to `policy->cur` on start and policy-limit changes.

Dependencies and integration points: depends on `cpufreq_governor.c` for utilization hooks, load sampling, work scheduling, tunable kobjects, and common governor lifecycle. It calls `__cpufreq_driver_target()` directly, so it requires target-style cpufreq drivers and participates in the core governor callback contract.

Risks and test signals: risks include very small `freq_step` falling back to a fixed 5 kHz-like default in `get_freq_step()`, `freq_step=0` intentionally freezing changes, stale requested frequency after external hardware changes until limits/start reset it, threshold misconfiguration rejection affecting userspace expectations, and slow reaction to bursty loads compared with schedutil/ondemand. Test signals include sysfs validation for threshold ordering, gradual step-up/step-down behavior under synthetic load, reset of `requested_freq` after min/max writes, ignore-nice recalibration, and no workqueue activity after governor stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_conservative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor.c

Purpose: provides common infrastructure for demand-based CPUFreq governors such as `ondemand` and `conservative`: tunable allocation, per-policy sampling state, scheduler utilization hooks, irq_work/workqueue dispatch, CPU load computation, and shared/per-policy sysfs lifecycle.

Important APIs and control flow: `sampling_rate_store()` validates the minimum sampling interval and forces immediate resampling when the rate shrinks. `gov_update_cpu_data()` seeds idle/nice counters for all CPUs covered by a tunable set. `dbs_update()` computes maximum load across policy CPUs from idle time deltas, optional iowait-busy behavior, optional nice-as-idle accounting, and wake-from-long-idle reuse of previous load. `dbs_update_util_handler()` is installed as each CPU's utilization hook, filters by elapsed sample delay, coordinates shared-policy CPUs with `work_count`, queues `irq_work`, and ultimately runs `dbs_work_handler()` to call the concrete governor's `gov_dbs_update()`. Lifecycle functions allocate policy data, share or allocate `dbs_data`, create tunable kobjects, start/stop hooks, and reapply limits.

State and persistence behavior: static per-CPU `cpu_dbs_info` stores previous idle/update/nice/load values plus the utilization hook. `policy_dbs_info` persists per policy with update mutex, last sample time, sample delay, irq work, work item, shared `dbs_data`, rate multiplier, idle-period count, and work-in-progress flags. Shared `dbs_data` can be global per governor unless `CPUFREQ_HAVE_GOVERNOR_PER_POLICY` is set. Kobject release calls the governor-specific `exit()` and frees `dbs_data`.

Dependencies and integration points: depends on cpufreq core governor callbacks, `cpufreq_add_update_util_hook()`/`remove_update_util_hook()`, idle-time helpers from `cpufreq.c`, kernel cpustat, sysfs governor attribute helpers, workqueues, irq_work, RCU synchronization, and concrete `dbs_governor` implementations.

Risks and test signals: risks include subtle memory-order dependencies between sample delay and utilization hook reads, shared-policy duplicate work if atomic coordination breaks, races in tunable updates if callers bypass `gov_attr_set` locking, load distortion on platforms with jiffy idle accounting, integer truncation in percentage load math, and lifecycle bugs if work or irq_work survives stop/exit. Test signals include enabling ondemand/conservative on shared and per-policy systems, rapid sampling-rate changes, CPU hotplug while work is pending, ignore-nice and io-is-busy recalibration, RCU-safe hook removal, and lockdep-clean governor limit updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor.h

Purpose: defines the shared data model and callback contract for legacy demand-based CPUFreq governors, including common tunables, per-policy/per-CPU sampling structures, the `dbs_governor` wrapper around `struct cpufreq_governor`, and helper macros for sysfs attributes and governor initialization.

Important APIs and control flow: `struct dbs_data` holds shared tunables and governor-specific tuner storage. `struct policy_dbs_info` holds per-policy sampling/work state and links into a tunable set. `struct cpu_dbs_info` stores per-CPU load-sampling history and the scheduler update hook. `struct dbs_governor` embeds the public governor plus callbacks for update, allocation, init/exit/start/limits, and optional shared global data. Macros `gov_show_one`, `gov_show_one_common`, `gov_attr_ro/rw`, and `CPUFREQ_DBS_GOVERNOR_INITIALIZER` reduce boilerplate. The header declares common lifecycle functions, `dbs_update()`, powersave-bias hooks, `sampling_rate_store()`, and `gov_update_cpu_data()`.

State and persistence behavior: the header owns no runtime state but fixes the in-memory contract used by `cpufreq_governor.c`, `cpufreq_ondemand.c`, and `cpufreq_conservative.c`. The `gov_attr_set` inside `dbs_data` is the persistent sysfs/tunable anchor, and `policy_dbs_info.list` joins policy instances to that anchor.

Dependencies and integration points: depends on cpufreq core types, scheduler cpufreq hooks, kernel stats, sysfs/kobject support, mutexes, irq_work, atomics, and module ownership. It integrates concrete governors with the CPUFreq core through standard governor callbacks and with sysfs through `governor_sysfs_ops`.

Risks and test signals: risks include ABI-style coupling between embedded structures and `container_of()` helpers, governor-specific tuner type mismatches in macros, shared tunables being unexpectedly global when drivers do not request per-policy governors, and misuse of exported lifecycle functions outside the intended DBS governors. Test signals include clean compile of both ondemand and conservative, correct sysfs file display/store dispatch, successful per-policy and shared governor tunable lifetimes, and no stale per-CPU `policy_dbs` pointers after governor exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor_attr_set.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor_attr_set.c

Purpose: implements the generic sysfs attribute-set helper for CPUFreq governor tunables. It dispatches governor attribute show/store callbacks and reference-counts shared tunable kobjects across one or more policies.

Important APIs and control flow: `governor_show()` maps an attribute to `struct governor_attr` and calls its show method with the owning `gov_attr_set`. `governor_store()` locks `attr_set->update_lock`, rejects writes once `usage_count` has reached zero, and calls the attribute store method. `gov_attr_set_init()` initializes the policy list, mutex, usage count, and first policy node. `gov_attr_set_get()` increments usage and links another policy. `gov_attr_set_put()` removes a policy, decrements usage, destroys the mutex and drops the kobject when the last user exits.

State and persistence behavior: state is embedded in each `gov_attr_set`: a policy list, update mutex, kobject, and usage count. The usage count controls whether sysfs writes are live and when the backing kobject can be released.

Dependencies and integration points: depends on `cpufreq_governor.h` definitions, sysfs `struct sysfs_ops`, kobject lifetime rules, list management, and mutexes. It is used by demand-based governors to expose shared or per-policy tunables under either the global cpufreq kobject or a policy kobject.

Risks and test signals: risks include show callbacks not checking `usage_count`, store callbacks assuming the policy list remains stable beyond the update lock, list-node misuse by callers, and kobject release ordering bugs if `gov_attr_set_put()` is not balanced. Test signals include sysfs read/write while multiple policies share a governor, hotplug removal of one policy from a shared tunable set, final policy exit freeing the kobject exactly once, and `-EBUSY` on stores after usage teardown begins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor_attr_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_ondemand.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_ondemand.c

Purpose: implements the `ondemand` dynamic CPUFreq governor. It reacts aggressively to high CPU load by jumping to maximum frequency, scales proportionally at lower load, and optionally alternates high/low frequencies to approximate a powersave-biased average.

Important APIs and control flow: `generic_powersave_bias_target()` maps a desired frequency to high/low table entries and computes split delays. `dbs_freq_increase()` targets max or a powersave-biased frequency. `od_update()` calls `dbs_update()`, compares load against `up_threshold`, applies `sampling_down_factor` when running at max, or computes proportional `freq_next`. `od_dbs_update()` handles normal and sub-sample phases for powersave bias. Sysfs stores manage `io_is_busy`, `up_threshold`, `sampling_down_factor`, `ignore_nice_load`, and `powersave_bias`. `od_register_powersave_bias_handler()` and `od_unregister_powersave_bias_handler()` let external code replace the bias target function and update active policies.

State and persistence behavior: per-policy `od_policy_dbs_info` stores low/high frequency delay state and sample type. Shared/common `dbs_data` stores sampling and load tunables; `od_dbs_tuners` stores `powersave_bias`. `default_powersave_bias` persists across new governor instances. Runtime bias state is reset on governor start and powersave-bias changes.

Dependencies and integration points: depends on common DBS infrastructure, frequency table helpers, CPU idle accounting, tick/nohz state for default thresholds, scheduler cpufreq hooks, sysfs governor attributes, and the cpufreq core target path. On x86, `od_should_io_be_busy()` defaults `io_is_busy` true on Intel Family 6 and newer.

Risks and test signals: risks include abrupt jumps to max causing power spikes, proportional target using cpuinfo min/max rather than current policy min/max before core clamping, powersave-bias delay arithmetic depending on non-empty frequency tables and monotonic lookups, external bias handler changes without per-policy locking in `od_set_powersave_bias()`, and very large `sampling_down_factor` delaying downscaling. Test signals include max-frequency jump above threshold, proportional downscale below threshold, powersave-bias sub-sample alternation, sysfs validation boundaries, io/nice accounting recalibration, external bias handler register/unregister, and stable behavior with no frequency table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_ondemand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_ondemand.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_ondemand.h

Purpose: declares ondemand-specific policy state, tuners, and default I/O-busy selection helper layered on top of the shared DBS governor infrastructure.

Important APIs and control flow: `struct od_policy_dbs_info` embeds `policy_dbs_info` and adds low/high frequency delay fields plus `sample_type` for normal versus sub-sample operation. `to_dbs_info()` converts common policy data to ondemand data. `struct od_dbs_tuners` stores `powersave_bias`. `od_should_io_be_busy()` chooses the initial `io_is_busy` default, returning true on Intel x86 Family 6+ and false elsewhere.

State and persistence behavior: this header owns no standalone runtime state but defines the layout allocated by `od_alloc()` and accessed by `cpufreq_ondemand.c`. The `sample_type` bit and delay fields persist between DBS work invocations to implement powersave-bias frequency alternation.

Dependencies and integration points: depends on `cpufreq_governor.h` and, for x86 builds, CPU vendor/model helpers from `asm/cpu_device_id.h`. It provides the structure contract used by ondemand's sysfs and update paths.

Risks and test signals: risks include `container_of()` layout coupling, x86 default I/O-busy policy being a broad heuristic, and non-x86 platforms requiring userspace to opt into I/O-busy accounting if desired. Test signals include correct allocation size, bias sub-sample state preserved across updates, default `io_is_busy` value on Intel x86 versus ARM/other platforms, and no build issues with or without `CONFIG_X86`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_ondemand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_performance.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_performance.c

Purpose: implements the simple `performance` governor, which drives each policy to its maximum allowed frequency whenever limits are applied.

Important APIs and control flow: `cpufreq_gov_performance_limits()` calls `__cpufreq_driver_target(policy, policy->max, CPUFREQ_RELATION_H)`. The static governor advertises name `performance`, module ownership, strict-target semantics, and the limits callback. It can provide `cpufreq_default_governor()` under `CONFIG_CPU_FREQ_DEFAULT_GOV_PERFORMANCE` and `cpufreq_fallback_governor()` for built-in non-module configurations.

State and persistence behavior: no governor-private state is allocated. Runtime behavior is entirely determined by current policy max and cpufreq core/driver state.

Dependencies and integration points: depends on cpufreq core governor registration macros and target-style drivers. The fallback hook integrates with `cpufreq.c` when dynamic switching governors are disallowed by a driver.

Risks and test signals: risks are mostly integration-related: strict-target max requests may expose driver table/limit bugs, and fallback availability depends on build configuration. Test signals include governor registration, selecting `performance` through sysfs, max-frequency target on min/max limit changes, default-governor selection when configured, and fallback use with `CPUFREQ_NO_AUTO_DYNAMIC_SWITCHING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_performance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_powersave.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_powersave.c

Purpose: implements the simple `powersave` governor, which drives each policy to its minimum allowed frequency whenever limits are applied.

Important APIs and control flow: `cpufreq_gov_powersave_limits()` calls `__cpufreq_driver_target(policy, policy->min, CPUFREQ_RELATION_L)`. The static governor advertises name `powersave`, module ownership, strict-target semantics, and a limits callback. It can provide `cpufreq_default_governor()` under `CONFIG_CPU_FREQ_DEFAULT_GOV_POWERSAVE`.

State and persistence behavior: no governor-private state is allocated. The target frequency is derived from current policy min at each limits callback.

Dependencies and integration points: depends on cpufreq core governor registration macros and target-style drivers. It appears in `scaling_available_governors` like other registered governors and can be selected by user space or default configuration.

Risks and test signals: risks include performance regressions if selected unexpectedly, strict-target min requests exposing incorrect policy min verification, and no support for drivers that only expose `setpolicy` beyond the cpufreq core's built-in policy names. Test signals include governor registration, sysfs selection, min-frequency target after policy limit changes, default-governor selection when configured, and stable unload/reload when built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_powersave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_stats.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_stats.c

Purpose: implements per-policy CPUFreq statistics exposed under each policy's `stats` sysfs group: total transitions, time spent in each frequency state, reset, and a transition matrix.

Important APIs and control flow: `cpufreq_stats_create_table()` counts valid frequency-table entries, allocates one block for `time_in_state`, unique `freq_table`, and `trans_table`, records the initial frequency index, and creates the sysfs group. `cpufreq_stats_record_transition()` handles deferred reset, maps old/new frequencies to state indexes, updates elapsed time from `local_clock()`, increments matrix and total counters, and skips unknown or unchanged states. `store_reset()` records a reset timestamp and defers table clearing until the next transition to reduce races. Show functions render total transitions, time-in-state with pending-reset handling, and the transition table with PAGE_SIZE guarding.

State and persistence behavior: `struct cpufreq_stats` is attached to `policy->stats` and persists for policy lifetime. It stores counters, last timestamp, state count, last index, frequency list, transition matrix, and deferred reset fields. Statistics reset is observable immediately in sysfs through pending-reset branches even before the next transition finalizes it.

Dependencies and integration points: depends on cpufreq core policy lifecycle, frequency tables, sysfs `freq_attr` support, `local_clock()`, and transition recording calls from `cpufreq_notify_transition()` and fast-switch paths. It is created by `cpufreq_policy_online()` after sysfs setup and freed during policy teardown.

Risks and test signals: risks include no explicit locking around stats reads versus transition updates, transition table output exceeding one page for large frequency tables, duplicate unsorted frequency entries requiring uniqueness filtering, `last_index == -1` causing early transition skips until a known frequency is reached, and deferred reset ordering relying on memory barriers. Test signals include non-empty stats directory on table-backed policies, increasing time-in-state and transition counts across target changes, reset behavior, warning and `-EFBIG` for oversized matrices, and clean removal during policy free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_userspace.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_userspace.c

Purpose: implements the `userspace` governor, which lets user space write an explicit target frequency through the standard `scaling_setspeed` policy attribute.

Important APIs and control flow: `cpufreq_set()` locks the governor-private mutex, rejects writes while the policy is not managed, stores the requested speed, and calls `__cpufreq_driver_target()` with relation L. `show_speed()` returns the last requested speed. Lifecycle callbacks allocate/free `struct userspace_policy`, mark management active on start with `setspeed = policy->cur`, clear it on stop, and reapply/clamp the saved target in `cpufreq_userspace_policy_limits()` when policy min/max changes.

State and persistence behavior: per-policy `userspace_policy` stores `is_managed`, `setspeed`, and a mutex. `setspeed` persists across limit callbacks while the governor is active but is reset to zero on stop and freed on exit.

Dependencies and integration points: depends on cpufreq core governor callbacks, `scaling_setspeed` dispatch in `cpufreq.c`, target-style drivers, and policy locking supplied by the core. It advertises strict-target behavior.

Risks and test signals: risks include user-requested speeds being rounded by driver/frequency-table relation semantics, writes failing during governor stop/start windows, `show_speed()` using `sprintf` rather than `sysfs_emit`, no validation before storing `setspeed` beyond target call behavior, and `BUG_ON(!policy->cur)` if started without a current frequency. Test signals include selecting userspace, reading/writing `scaling_setspeed`, clamping after min/max updates, rejection after governor stop, and correct per-policy allocation/free under hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_userspace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/davinci-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/davinci-cpufreq.c

Purpose: provides a platform-data based CPUFreq driver for TI DaVinci SoCs. It changes the ARM clock rate, optionally restores an async clock rate, and optionally delegates voltage changes to board/platform callbacks.

Important APIs and control flow: `davinci_target()` reads the selected table entry, raises voltage before scaling up through `pdata->set_voltage(idx)`, calls `clk_set_rate()` on `armclk`, reapplies `asyncclk` rate if present, and lowers voltage after scaling down. `davinci_cpu_init()` restricts operation to CPU0, runs optional platform initialization, stores `policy->clk`, and calls `cpufreq_generic_init()` with a 2 ms transition latency. `davinci_cpufreq_probe()` validates platform data and table, gets `arm` and optional `async` clocks, records the async rate, and registers `davinci_driver`.

State and persistence behavior: a single static `struct davinci_cpufreq` stores device and clock pointers plus original async rate. Frequency table and voltage policy live in platform data. Hardware clock and voltage settings persist until changed again by cpufreq or platform code.

Dependencies and integration points: depends on legacy platform data `davinci_cpufreq_config`, the common clock framework, cpufreq generic table verification/get/init helpers, and `platform_driver_probe()`. It is initialized through exported `davinci_cpufreq_init()` rather than a normal module macro in this file.

Risks and test signals: risks include global singleton state limiting multiple instances, no rollback of raised voltage if `clk_set_rate()` fails, ignored errors from voltage lowering, optional async clock rate restore failures after ARM clock change, platform-data lifetime assumptions, and CPU0-only support. Test signals include probe with valid platform data, frequency-table validation, voltage-before-up and voltage-after-down ordering, async clock retention, initial unlisted-frequency correction through `CPUFREQ_NEED_INITIAL_FREQ_CHECK`, and clean clock puts on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/davinci-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/e_powersaver.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/e_powersaver.c

Purpose: implements a legacy x86 CPUFreq driver for VIA/Centaur C7 Enhanced PowerSaver processors using MSR multiplier/voltage controls and optional ACPI BIOS-limit checks.

Important APIs and control flow: `eps_get()` reads `MSR_IA32_PERF_STATUS` and returns FSB times current multiplier. `eps_set_state()` waits for transition-busy bits to clear, writes the low 16 bits of the destination multiplier/voltage to `MSR_IA32_PERF_CTL`, and polls for completion. `eps_target()` selects the encoded table state. `eps_cpu_init()` detects supported brand/model, enables Enhanced SpeedStep/PowerSaver in `MSR_IA32_MISC_ENABLE`, validates current/max/min multipliers and voltages, enforces failsafe checks unless module parameters disable them, derives FSB from `cpu_khz`, optionally checks ACPI BIOS limit, constructs a two-state or multi-state frequency table, and attaches it to the policy. Module init gates on Centaur family 6 EST-capable CPUs.

State and persistence behavior: per-CPU pointer `eps_cpu[NR_CPUS]` stores FSB, optional BIOS limit, and a flexible frequency table. Module parameters persist failsafe behavior and optional maximum voltage override. Hardware MSR state persists after transitions; comments explicitly warn about overclock/change-after-unload scenarios.

Dependencies and integration points: depends on x86 CPU identification, MSR access, TSC/cpu_khz, optional ACPI processor performance registration, cpufreq generic frequency-table helpers, and CPU0-only policy assumptions.

Risks and test signals: risks include direct voltage programming with limited platform validation, CPU0-only support despite `NR_CPUS` array, failsafe module parameters enabling unsafe operation, ACPI helper minimalism, polling timeouts returning `-ENODEV`, FSB derivation from current multiplier accuracy, and no transition notifier wrapping in the driver itself because core target-index path handles notifications. Test signals include matching only supported VIA C7 systems, successful MSR feature enable, generated frequency table matching min/max multipliers, ACPI limit rejection when applicable, target transitions completing within polls, and cleanup freeing `eps_cpu[0]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/e_powersaver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/elanfreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/elanfreq.c

Purpose: implements a legacy x86 CPUFreq driver for AMD Elan family SoCs by programming chip setup/control I/O ports for clock divider and hyperspeed modes.

Important APIs and control flow: `elanfreq_get_cpu_frequency()` reads indexed register `0x80` through ports `0x22/0x23`, decodes normal 1-33 MHz states and hyperspeed 66/99 MHz states, and returns the current frequency. `elanfreq_target()` disables hyperspeed, delays for pipeline cleanup, writes the selected CPU clock speed register value and PMU force-mode register value from `elan_multiplier`, then delays for settle. `elanfreq_cpu_init()` validates AMD family/model, initializes `max_freq` from current speed if unset, invalidates table entries above max, and attaches `elanfreq_table`. Built-in boot parameter parsing supports deprecated `elanfreq=`.

State and persistence behavior: static `max_freq`, multiplier table, and cpufreq table define available states. The target function persists hardware state in Elan internal registers. Invalidated table entries remain modified for the module lifetime.

Dependencies and integration points: depends on x86 CPU identification, legacy I/O port access, local IRQ disabling around register access, cpufreq generic table verification, and cpufreq core target-index notifications. The driver sets `CPUFREQ_NO_AUTO_DYNAMIC_SWITCHING`, so the core should fall back from dynamic governors.

Risks and test signals: risks include global mutation of the static frequency table, CPU0-only hardware assumptions, long IRQ-off and udelay sections, no explicit error checking for I/O writes, current-frequency fallback making maximum frequency depend on boot state, and deprecated boot-parameter behavior. Test signals include driver matching only AMD 486 model 10, correct current frequency decoding, table invalidation above `max_freq`, successful transitions to normal and hyperspeed states, and fallback to non-dynamic governor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/elanfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/freq_table.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/freq_table.c

Purpose: implements generic CPUFreq frequency-table helpers for policy cpuinfo derivation, policy verification, target-index resolution, available-frequency sysfs attributes, boost-frequency filtering, and table sort validation.

Important APIs and control flow: `cpufreq_frequency_table_cpuinfo()` scans valid table entries, filters boost entries when global or local boost is disabled, and updates policy min/max/cpuinfo. `cpufreq_frequency_table_verify()` clamps policy min/max to CPU limits and ensures at least one table frequency is available, falling back to the previous smaller value when needed. `cpufreq_generic_frequency_table_verify()` requires a table before verifying. `cpufreq_table_index_unsorted()` selects an index for relation H/L/C with optimal and suboptimal candidates. `cpufreq_frequency_table_get_index()` finds exact frequency indexes. `show_available_freqs()` renders normal or boost entries. `cpufreq_table_validate_and_sort()` recomputes cpuinfo, detects boost support, accepts pre-marked sorted tables, or calls `set_freq_table_sorted()` to reject duplicates and mark ascending/descending/unsorted.

State and persistence behavior: helpers update fields inside `struct cpufreq_policy`, including `min`, `max`, `cpuinfo`, `boost_supported`, and `freq_table_sorted`. They do not allocate persistent state. Available-frequency sysfs attributes are global `freq_attr` objects consumed by `cpufreq.c`.

Dependencies and integration points: depends on cpufreq core table iteration macros, boost state from `cpufreq_boost_enabled()`, policy verification helpers, and sysfs policy attribute plumbing. Target-index drivers rely on these helpers during policy online and target resolution.

Risks and test signals: risks include `abs()`/unsigned-difference assumptions, `cpufreq_table_index_unsorted()` returning index 0 after warning for invalid tables, duplicate entries rejected only when table is otherwise monotonic, boost filtering producing no valid min if all entries are boost-only, and available-frequency output using `sprintf` without explicit PAGE_SIZE checks. Test signals include sorted/descending/unsorted table detection, duplicate rejection, boost sysfs filtering, target resolution for H/L/C relations, policy verification with empty ranges, and initial-frequency index lookups used by stats and core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/freq_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/gx-suspmod.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/gx-suspmod.c

Purpose: implements a legacy CPUFreq driver for Cyrix MediaGX and NatSemi Geode GX suspend modulation. It exposes effective CPU frequency by programming CS55x0 PCI suspend-modulation ON/OFF counters rather than changing the actual core clock.

Important APIs and control flow: chipset detection scans PCI devices for supported Cyrix 5510/5520/5530 legacy IDs. `gx_get_cpuspeed()` returns stock frequency when modulation is disabled or computes `stock * off / (on + off)`. `gx_validate_speed()` searches ON/OFF counter durations up to `max_duration` for the closest effective rate. `gx_set_cpuspeed()` computes the target, sends cpufreq transition begin/end notifications itself, writes PCI modulation counters and config bits with IRQs disabled, and enables speedup behavior for interrupts/video on CS5530. `cpufreq_gx_verify()` clamps policy min/max to achievable modulation values. `cpufreq_gx_target()` repeatedly adjusts the validated rate into policy bounds and calls `gx_set_cpuspeed()`. `cpufreq_gx_cpu_init()` derives stock frequency from module parameter, `cpu_khz`, or Cyrix DIR multiplier.

State and persistence behavior: global `gx_params` stores cached PCI register values, current on/off durations, and the PCI device. `stock_freq`, `pci_busclk`, and `max_duration` define available range. Hardware state persists in PCI PMER/SUSCFG/MODON/MODOFF registers; original register values are cached but not restored on exit.

Dependencies and integration points: depends on PCI config access, Cyrix processor DIR register helpers, cpufreq core target-driver mode, manual transition notifications, module parameters, and CPU0-only assumptions. It sets `CPUFREQ_NO_AUTO_DYNAMIC_SWITCHING`.

Risks and test signals: risks include effective-frequency throttling being presented as cpufreq, manual notifications in a driver using `target` instead of `target_index`, potential divide-by-zero or zero-duration edge cases if parameters are extreme, no restoration of cached PCI settings on unload, PCI device reference handling, long IRQ-disabled register programming, and hardware marked as needing testing. Test signals include chipset detection, sane `max_duration` clamping, frequency verification near min/max, modulation disabled at stock frequency, transition notifications around PCI writes, and observed effective throughput matching requested rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/gx-suspmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/highbank-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/highbank-cpufreq.c

Purpose: provides Calxeda Highbank/ECX-2000 voltage-change coordination for the generic `cpufreq-dt` driver. It registers a clock notifier that tells the EnergyCore Management Engine to adjust voltage before upward rate changes and after downward rate changes.

Important APIs and control flow: `hb_voltage_change()` sends a PL320 IPC message containing a CPUFreq change note and target frequency in MHz. `hb_cpufreq_clk_notify()` handles `PRE_RATE_CHANGE` for upward transitions and `POST_RATE_CHANGE` for downward transitions, retrying up to `HB_CPUFREQ_VOLT_RETRIES` before returning `NOTIFY_BAD`. Module init checks DT machine compatibility, gets CPU0 device/node and CPU clock, registers the notifier, and instantiates a `cpufreq-dt` platform device.

State and persistence behavior: static notifier block persists for module lifetime. There is no remove path shown; registered notifier and cpufreq-dt device are effectively boot/module lifetime resources.

Dependencies and integration points: depends on OF machine compatibles `calxeda,highbank` and `calxeda,ecx-2000`, CPU0 device DT node, common clock framework notifiers, PL320 IPC firmware interface, and `cpufreq-dt`.

Risks and test signals: risks include missing cleanup/unregister path, retry loops without delay, ignoring `platform_device_register_full()` return value, potential clock reference leak on successful notifier registration, voltage IPC failure blocking clock changes, and no handling for abort-rate-change notifications. Test signals include notifier registration on matching machines only, IPC messages before/after expected rate directions, `NOTIFY_BAD` on repeated ECME failure, successful cpufreq-dt instantiation, and stable CPU voltage during frequency transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/highbank-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/imx-cpufreq-dt.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/imx-cpufreq-dt.c

Purpose: wraps `cpufreq-dt` for NXP/Freescale i.MX platforms that need speed-grade or market-segment OPP filtering, and provides i.MX7ULP intermediate-clock callbacks for safe frequency switching.

Important APIs and control flow: for i.MX7ULP, `imx7ulp_get_intermediate()` returns the FIRC rate and `imx7ulp_target_intermediate()` reparents SCS selectors to FIRC, switches ARM between normal and high-speed cores based on target frequency, and is passed as `cpufreq_dt_platform_data` when registering `cpufreq-dt`. For other supported i.MX variants, probe requires `cpu-supply`, reads `speed_grade` nvmem, extracts speed grade and market segment with SoC-specific masks, applies early-sample fuse clamping for i.MX8M, calls `dev_pm_opp_set_supported_hw()`, and registers a child `cpufreq-dt` platform device. Remove unregisters the child and releases either OPP supported-hw token or bulk clocks.

State and persistence behavior: static globals hold the registered `cpufreq-dt` platform device, CPU device, and OPP supported-hw token. For i.MX7ULP, bulk clock handles persist until remove. OPP filtering state persists in the PM OPP core until `dev_pm_opp_put_supported_hw()`.

Dependencies and integration points: depends on CPU0 DT node, `cpu-supply`, nvmem cell `speed_grade`, OPP supported-hw bindings, i.MX machine compatibles, common clock bulk APIs, and `cpufreq-dt` platform data callbacks.

Risks and test signals: risks include CPU device/node assumptions without explicit null checks after `get_cpu_device(0)`, SoC-specific fuse masks needing exact alignment with bindings, early-sample clamping hiding real fuse problems, global singleton state, lack of return checking for individual `clk_set_parent()` calls in intermediate switching, and failure if `cpu-supply` is intentionally absent. Test signals include supported-hw masks logged as expected, OPP table filtered to legal frequencies, i.MX7ULP intermediate parent switching during transitions, cpufreq-dt child creation/removal, and correct cleanup on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/imx-cpufreq-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/imx6q-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/imx6q-cpufreq.c

Purpose: implements a full cpufreq driver for i.MX6Q/i.MX6QP/i.MX6UL/i.MX6ULL class SoCs using OPP tables, ARM/SoC/PU regulators, PLL/clock reparenting sequences, speed-grade fuse filtering, cooling-device support, and suspend-frequency handling.

Important APIs and control flow: `imx6q_set_target()` finds the target OPP voltage, raises PU/SOC/ARM regulators before upward transitions, reparents clocks through safe intermediate paths, reprograms PLL1 when needed, sets the ARM clock rate, disables temporary PLL1 use, and lowers voltages after downward transitions. UL/ULL paths use secondary selectors and may halve ARM rate before reparenting; non-UL paths switch through `pll2_pfd2_396m`. `imx6q_cpufreq_init()` calls `cpufreq_generic_init()` and sets suspend frequency to max. Speed-grade helpers read nvmem or OCOTP syscon and disable illegal OPPs. Probe gets CPU0 node, bulk clocks, regulators, OPP table, speed-grade filters, cpufreq table, optional `fsl,soc-operating-points` SOC/PU voltages with defaults, transition latency including regulator ramp times, max/min voltage data, and registers the cpufreq driver.

State and persistence behavior: static globals store regulator handles, bulk clocks, CPU device, cpufreq table, max frequency, transition latency, SoC voltage array, and count. OPP table changes persist in the OPP core while the driver is loaded. Hardware state persists in regulators and clock tree after each target transition.

Dependencies and integration points: depends on OF CPU node properties, OPP bindings, optional `fsl,soc-operating-points`, nvmem or syscon OCOTP, regulator framework, common clock framework, cpufreq generic table helpers, energy model registration with OPP, thermal cooling, and cpufreq generic suspend.

Risks and test signals: risks include complex partial-failure rollback: voltage-up failures abort early but clock-set failures only restore ARM voltage, not necessarily SOC/PU or clock parents; many `clk_set_parent()` calls ignore return values; static singleton state; default SOC voltage fallback may be wrong for boards lacking valid DT data; OPP table ordering assumptions; fuse-read failure blocking probe; and regulator ramp latency only approximate. Test signals include probe on each compatible variant, OPP disabling by fuse grade, valid SOC/PU voltage mapping or fallback warning, upward/downward regulator sequencing, PLL reparenting without glitches, suspend frequency set to max, cooling and EM registration, and clean remove freeing OPP table/regulators/clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/imx6q-cpufreq.c -->
