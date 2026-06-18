# subset-b-005850 Research

Grouped source research for Linux CPU topology, hotplug, power-management, cpumask/cpuset, crash/kdump, CRC, credential, Ceph CRUSH, crypto, CS5535, ctype, and CUDA interface headers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cper.h -->
# sources/distributed-fs/ceph-client/include/linux/cper.h

## Purpose

`cper.h` defines Linux's in-kernel representation of UEFI Common Platform Error Record data. It is the ABI-facing contract for firmware-first hardware error records, including record headers, section descriptors, processor, memory, PCIe, firmware-reference, ARM, IA, CXL, and DMAR section identifiers. The source was read as a complete 615-line file.

## Important APIs, Types, and Functions

Key constants include `CPER_SIG_RECORD`, `CPER_RECORD_REV`, `CPER_REC_LEN`, severity values, validation masks, record/section flag masks, notification GUIDs, section GUIDs, and memory extension bit helpers. Packed structs include `cper_record_header`, `cper_section_descriptor`, `cper_sec_proc_generic`, `cper_sec_proc_ia`, `cper_ia_err_info`, `cper_ia_proc_ctx`, `cper_sec_proc_arm`, `cper_arm_err_info`, `cper_arm_ctx_info`, `cper_sec_mem_err_old`, `cper_sec_mem_err`, `cper_mem_err_compact`, `cper_sec_pcie`, and `cper_sec_fw_err_rec_ref`. Public helpers include `cper_next_record_id()`, severity and memory error string helpers, `cper_print_bits()`, `cper_bits_to_str()`, memory pack/unpack/location helpers, processor printers, `cper_estatus_print()`, `cper_estatus_check_header()`, `cper_estatus_check()`, and `cxl_cper_print_prot_err()`.

## Control Flow

This header is mostly layout and parser/printer declaration. Firmware or ACPI paths receive error status records, validate the record and section headers, identify section types by GUID, and dispatch to CPER printers or packers. `cper_get_mem_extension()` is the only inline data path; it derives extended row bits when the memory error valid mask indicates an extended row field.

## State and Persistence Behavior

The file does not own storage, but the packed structs mirror persistent firmware-provided error records and must remain byte-exact. `cper_mem_err_compact` is a kernel trace-friendly compact representation used after extracting a full memory section.

## Dependencies and Integration Points

It depends on `linux/uuid.h` and `linux/trace_seq.h`, and integrates with ACPI HEST/GHES, RAS reporting, EDAC-like memory-error handling, tracepoints, CXL CPER protocol error printing, and userspace-facing error summaries.

## Risks and Edge Cases

The main risk is ABI drift: packing, field order, GUID values, validation masks, and endian-sized integer fields must match UEFI/CXL specifications. Callers must honor validation bits before interpreting optional fields. Memory extension helpers only make sense with the matching `CPER_MEM_VALID_ROW_EXT` bit. Record length and section offsets need strict bounds checking by implementations to avoid malformed firmware input.

## Test Signals

Useful signals include build coverage for ACPI/GHES/RAS/CXL paths, fixture-based parsing of valid and malformed CPER blobs, exact struct size/offset checks when specs change, validation-bit tests for optional memory and PCIe fields, trace formatting tests for compact memory errors, and injected firmware-first error records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu.h

## Purpose

`cpu.h` is the generic CPU device, topology, hotplug, idle, suspend, and CPU mitigation interface. It exposes the `devices/system/cpu` model, architecture hooks, sysfs vulnerability reporting hooks, and common wrappers around CPU bringup/offline and idle entry. The source was read as a complete 236-line file.

## Important APIs, Types, and Functions

`struct cpu` stores `node_id`, `hotpluggable`, and an embedded `struct device`. Registration and lookup APIs include `register_cpu()`, `unregister_cpu()`, `get_cpu_device()`, `cpu_device_create()`, `arch_register_cpu()`, `arch_unregister_cpu()`, `arch_cpu_is_hotpluggable()`, and OF physical-ID matching helpers. Sysfs integration uses `cpu_add_dev_attr()`, `cpu_remove_dev_attr()`, group variants, and many `cpu_show_*()` vulnerability reporters. Hotplug and suspend APIs include `add_cpu()`, `remove_cpu()` through `cpuhplock.h`, `cpu_device_up()`, `notify_cpu_starting()`, `cpu_maps_update_begin()`, `cpu_maps_update_done()`, `freeze_secondary_cpus()`, `thaw_secondary_cpus()`, and `suspend_disable_secondary_cpus()`. Idle and mitigation APIs include `cpu_startup_entry()`, `cpu_idle_poll_ctrl()`, `arch_cpu_idle*()`, `play_idle_precise()`, `cpuhp_report_idle_dead()`, `enum cpu_attack_vectors`, and `enum smt_mitigations`.

## Control Flow

CPU boot starts through boot/init hooks, then CPU devices are registered and exported. Online/offline paths pass through CPU hotplug states and map-update locks. Suspend paths freeze secondary CPUs and thaw them later. Idle flow enters `cpu_startup_entry()`, calls architecture idle hooks, and may report dead idle for hotplug teardown.

## State and Persistence Behavior

Persistent kernel state is external: per-CPU `cpu_devices`, CPU bus objects, CPU masks, hotplug task-freeze state, and mitigation mode. This header declares and gates access; it does not allocate storage.

## Dependencies and Integration Points

It includes `node.h`, `compiler.h`, `cpuhotplug.h`, `cpuhplock.h`, and `cpu_smt.h`. It integrates with driver core sysfs, architecture CPU discovery, SMP/hotplug, PM sleep, scheduler idle, tick broadcast, security mitigation reporting, and architecture `prctl` controls for branch landing pad state.

## Risks and Edge Cases

Misusing hotplug locks can race CPU masks and device registration. Sysfs vulnerability reporters must remain aligned with mitigation state. Non-SMP and !HOTPLUG builds intentionally compile many APIs to no-ops, so callers must tolerate success without real CPU changes. Suspend code must respect the optional nonzero primary CPU configuration.

## Test Signals

Signals include CPU online/offline stress, sysfs CPU device and vulnerability attribute checks, suspend/resume with secondary CPU freeze, non-SMP and !HOTPLUG builds, architecture CPU ID matching tests, and idle/dead CPU hotplug teardown coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_cooling.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu_cooling.h

## Purpose

`cpu_cooling.h` declares the bridge between CPU frequency/idle frameworks and the thermal cooling-device framework. It lets cpufreq policies and cpuidle drivers appear as thermal actuators. The source was read as a complete 72-line file.

## Important APIs, Types, and Functions

For `CONFIG_CPU_FREQ_THERMAL`, it declares `cpufreq_cooling_register()`, `cpufreq_cooling_unregister()`, and `of_cpufreq_cooling_register()`. Without that config, registration returns `ERR_PTR(-ENOSYS)` or `NULL`, and unregister is a no-op. For `CONFIG_CPU_IDLE_THERMAL`, it declares `cpuidle_cooling_register()`, otherwise a no-op inline is supplied.

## Control Flow

CPU frequency drivers register a cooling device after a policy is available; thermal zones can then throttle maximum frequency through that cooling device. Device-tree-aware platforms use the OF registration helper to bind cooling maps. Cpuidle drivers can register idle-state based cooling when supported.

## State and Persistence Behavior

The header owns no state. Registered `struct thermal_cooling_device` objects and their links to cpufreq policies or cpuidle drivers are managed by implementation files and persist until explicitly unregistered or driver removal occurs.

## Dependencies and Integration Points

It depends on `linux/of.h`, `linux/thermal.h`, and forward declarations of `struct cpufreq_policy` and `struct cpuidle_driver`. It integrates cpufreq, cpuidle, thermal governors, and device tree cooling maps.

## Risks and Edge Cases

Callers must handle disabled-config stubs and not assume a non-NULL cooling device. Unregister must only receive valid devices from successful registration. Thermal throttling correctness depends on cpufreq policy sharing, OPP data, and cooling maps matching the actual CPU domain.

## Test Signals

Signals include build coverage with and without CPU thermal configs, DT thermal-zone cooling-map binding, cpufreq policy removal cleanup, thermal governor requests reducing CPU max frequency, and cpuidle cooling registration on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_cooling.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_pm.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu_pm.h

## Purpose

`cpu_pm.h` defines notifier events used when CPUs or CPU power domains enter and leave low-power states that may reset local or cluster hardware context. The source was read as a complete 100-line file.

## Important APIs, Types, and Functions

`enum cpu_pm_event` defines `CPU_PM_ENTER`, `CPU_PM_ENTER_FAILED`, `CPU_PM_EXIT`, `CPU_CLUSTER_PM_ENTER`, `CPU_CLUSTER_PM_ENTER_FAILED`, and `CPU_CLUSTER_PM_EXIT`. When `CONFIG_CPU_PM` is enabled, it declares notifier registration plus `cpu_pm_enter()`, `cpu_pm_exit()`, `cpu_cluster_pm_enter()`, and `cpu_cluster_pm_exit()`. Disabled builds provide zero-return stubs.

## Control Flow

Platform idle, suspend, and hotplug code calls CPU events on the affected CPU with interrupts disabled. Once all CPUs in a shared power domain have been notified, cluster events notify drivers that global context may be lost. Exit and failed-enter notifications restore or unwind state.

## State and Persistence Behavior

Notifier registrations persist in the CPU PM notifier chain. The header itself owns no context; registered drivers are responsible for saving/restoring per-CPU and cluster hardware state.

## Dependencies and Integration Points

It depends on `linux/kernel.h` and `linux/notifier.h`. Integration points include cpuidle low-level entry macros, architecture suspend/hotplug paths, interrupt controller drivers, timer/counter drivers, cache/FPU context code, and SoC power-domain management.

## Risks and Edge Cases

Notifications must run with interrupts disabled and on the affected CPU for per-CPU events. Failing to send failed-enter events can leave drivers thinking state was lost. Cluster events must be ordered after per-CPU events. Disabled-config stubs mean callers cannot rely on notifier side effects in all builds.

## Test Signals

Signals include low-power entry/exit tests with notifier ordering instrumentation, suspend/resume on platforms that power down CPU domains, hotplug play-dead flows, failure-injection for failed enter notifications, and builds with `CONFIG_CPU_PM=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_rmap.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu_rmap.h

## Purpose

`cpu_rmap.h` declares CPU affinity reverse maps, which map each CPU to the nearest object, commonly an IRQ or queue, based on affinity masks. The source was read as a complete 67-line file.

## Important APIs, Types, and Functions

`struct cpu_rmap` contains a `kref`, object count, object pointer array, and per-CPU `near[]` entries with object index and distance. `CPU_RMAP_DIST_INF` marks infinite distance. APIs include `alloc_cpu_rmap()`, `cpu_rmap_get()`, `cpu_rmap_put()`, `cpu_rmap_add()`, `cpu_rmap_update()`, `cpu_rmap_lookup_index()`, `cpu_rmap_lookup_obj()`, `alloc_irq_cpu_rmap()`, `free_irq_cpu_rmap()`, `irq_cpu_rmap_add()`, and `irq_cpu_rmap_remove()`.

## Control Flow

A driver allocates a map for a fixed number of objects, adds objects, updates each object's CPU affinity, then fast paths look up the nearest object for a CPU. IRQ-specific helpers allocate with `GFP_KERNEL` and bind IRQ affinities into the same map.

## State and Persistence Behavior

The map persists through reference counts. The per-CPU nearest-object cache must be updated when affinity changes. It is in-memory state only and has no disk persistence.

## Dependencies and Integration Points

It depends on cpumask types, GFP flags, slab allocation, and krefs. It integrates with IRQ affinity, networking queue steering, block/network multiqueue-like placement, and drivers that need CPU-local object selection.

## Risks and Edge Cases

Lookups assume a valid CPU index and initialized `near[]` entries. Affinity changes must call `cpu_rmap_update()` or stale routing can persist. Object count is fixed at allocation, and reference ownership must be balanced with `cpu_rmap_put()`.

## Test Signals

Signals include allocation/free leak tests, update tests for changing cpumasks, lookup correctness for empty/far affinity, IRQ add/remove lifecycle coverage, CPU hotplug affinity update tests, and KASAN/KCSAN runs for flexible-array bounds and races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_rmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_smt.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu_smt.h

## Purpose

`cpu_smt.h` declares the CPU hotplug control surface for simultaneous multithreading. It tracks whether SMT is enabled, disabled, force-disabled, unsupported, or not implemented. The source was read as a complete 33-line file.

## Important APIs, Types, and Functions

`enum cpuhp_smt_control` defines `CPU_SMT_ENABLED`, `CPU_SMT_DISABLED`, `CPU_SMT_FORCE_DISABLED`, `CPU_SMT_NOT_SUPPORTED`, and `CPU_SMT_NOT_IMPLEMENTED`. With `CONFIG_SMP` and `CONFIG_HOTPLUG_SMT`, it exposes `cpu_smt_control`, `cpu_smt_num_threads`, `cpu_smt_disable()`, `cpu_smt_set_num_threads()`, `cpu_smt_possible()`, `cpuhp_smt_enable()`, and `cpuhp_smt_disable()`. Other builds define inert constants and stubs.

## Control Flow

Boot or mitigation code sets SMT policy, then hotplug code enables or disables sibling threads accordingly. Thread-count configuration restricts how many SMT siblings may stay online.

## State and Persistence Behavior

Global SMT state persists in kernel variables for the boot lifetime. It can be influenced by boot parameters, architecture support, and security mitigation policy, but the header owns no storage.

## Dependencies and Integration Points

It integrates with CPU hotplug, SMP topology, sysfs SMT controls, and CPU mitigation code in `cpu.h`. It intentionally has no includes beyond the guard and relies on consumers having basic type definitions.

## Risks and Edge Cases

Force-disabled SMT should not be re-enabled through ordinary paths. Disabled-config stubs can make callers think a transition succeeded without hardware effect. Thread-count limits must match topology or sibling CPUs may be wrongly offlined or exposed.

## Test Signals

Signals include SMT sysfs enable/disable tests, boot-parameter mitigation tests, hotplug of sibling threads, force-disabled re-enable rejection, topology variations with different thread counts, and !HOTPLUG_SMT builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_smt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpufeature.h -->
# sources/distributed-fs/ceph-client/include/linux/cpufeature.h

## Purpose

`cpufeature.h` provides a generic module autoprobed-by-CPU-feature helper when architectures enable `CONFIG_GENERIC_CPU_AUTOPROBE`. The source was read as a complete 58-line file.

## Important APIs, Types, and Functions

The central API is `module_cpu_feature_match(feature, initfunc)`. It emits a `struct cpu_feature` match table, exports it via `MODULE_DEVICE_TABLE(cpu, ...)`, and wraps module initialization so the module returns `-ENODEV` if `cpu_have_feature(cpu_feature(feature))` is false. It relies on architecture-provided `cpu_feature()`, `cpu_have_feature()`, `MAX_CPU_FEATURES`, and optional `CPU_FEATURE_TYPEFMT`/`CPU_FEATURE_TYPEVAL`.

## Control Flow

For supported architectures, module loading or udev autoloading matches CPU feature modalias data. During module init, the wrapper checks the feature again before calling the real init function, preventing manual load on unsupported CPUs.

## State and Persistence Behavior

The header creates static const match tables in modules. It owns no runtime mutable state.

## Dependencies and Integration Points

It includes `linux/init.h`, `linux/mod_devicetable.h`, and `asm/cpufeature.h` only under `CONFIG_GENERIC_CPU_AUTOPROBE`. It integrates with module autoloading, architecture CPU feature enumeration, and feature-specific drivers or accelerators.

## Risks and Edge Cases

The macro depends on legal architecture feature names. Generated symbol names include the feature token, so unusual macro arguments can break compilation. Runtime feature checks must match modalias feature enumeration or autoload and manual-load behavior diverge.

## Test Signals

Signals include module build tests on architectures with and without generic autoprobe, modalias generation checks, manual insmod on unsupported feature returning `-ENODEV`, and successful init on CPUs with the feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpufreq.h -->
# sources/distributed-fs/ceph-client/include/linux/cpufreq.h

## Purpose

`cpufreq.h` is the main kernel interface for CPU dynamic voltage/frequency scaling. It defines cpufreq policy state, driver and governor contracts, transition notifiers, frequency-table helpers, boost handling, fast switching, thermal integration flags, and OF performance-domain sharing helpers. The source was read as a complete 1,250-line file.

## Important APIs, Types, and Functions

Core types include `struct cpufreq_cpuinfo`, `struct cpufreq_policy`, `struct cpufreq_policy_data`, `struct cpufreq_freqs`, `struct freq_attr`, `struct cpufreq_driver`, `struct cpufreq_governor`, `struct gov_attr_set`, `struct governor_attr`, and `struct cpufreq_frequency_table`. Policy APIs include `cpufreq_cpu_get_raw()`, `cpufreq_cpu_policy()`, `cpufreq_cpu_get()`, `cpufreq_cpu_put()`, `cpufreq_get()`, `cpufreq_quick_get()`, `cpufreq_update_policy()`, `cpufreq_update_limits()`, fast-switch helpers, pressure access, and guard/free helpers for policy locks and references. Driver/governor APIs include `cpufreq_register_driver()`, `cpufreq_unregister_driver()`, `cpufreq_driver_target()`, `cpufreq_driver_fast_switch()`, `cpufreq_driver_adjust_perf()`, `cpufreq_register_governor()`, `cpufreq_start_governor()`, and `cpufreq_stop_governor()`. Table helpers cover iteration, validation, target resolution, efficient-frequency filtering, and sorted ascending/descending search.

## Control Flow

A cpufreq driver registers a `struct cpufreq_driver`, initializes policies per related CPU domain, verifies limits, exposes sysfs attributes, and starts a governor. Governors compute targets and invoke driver callbacks through core wrappers. Frequency transitions notify `PRECHANGE` and `POSTCHANGE`, update policy `cur`, and synchronize through `transition_lock` and `transition_wait`. Table target helpers clamp target frequencies to min/max, choose relation `L/H/C`, optionally skip inefficient entries, and retry without efficiency filtering if needed.

## State and Persistence Behavior

`struct cpufreq_policy` is the persistent in-memory state for a frequency domain: CPU masks, limits, current/suspend frequency, governor data, QoS requests, frequency table, sysfs kobject, policy list node, rwsem, fast-switch and boost flags, cached resolution, transition state, stats, driver data, thermal cooling device pointer, and notifier blocks. No file-backed persistence is owned here, but sysfs exposes mutable policy state.

## Dependencies and Integration Points

It depends on clk, CPU/core, cpumask, completions, kobjects, notifiers, OF, OPP, PM QoS, spinlocks, sysfs, and min/max helpers. Integration points include schedutil and scheduler frequency invariance, energy-aware scheduling, thermal cooling, OPP energy models, CPU hotplug, sysfs governors, architecture frequency read/scale hooks, and device-tree performance domains.

## Risks and Edge Cases

Policy locking and reference lifetimes are critical because hotplug can remove policies while readers inspect them. Fast switch callbacks run in scheduler-sensitive contexts and must avoid sleeping. Frequency table helpers assume correct sorting metadata; unsorted tables use a separate path. Efficient-frequency filtering must retry if filtering makes min/max impossible. Notifier ordering and async notification flags must match driver behavior. Disabled `CONFIG_CPU_FREQ` stubs return zeros or unsupported errors, so consumers must handle absent cpufreq.

## Test Signals

Signals include cpufreq selftests, driver registration/unregistration, policy hotplug stress, sysfs min/max/governor changes, notifier ordering traces, fast-switch scheduler tests, boost enable/disable, frequency-table target tests for ascending/descending/unsorted tables, inefficient-frequency selection tests, thermal cooling integration, OF sharing mask parsing, and builds with cpufreq disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpufreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuhotplug.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuhotplug.h

## Purpose

`cpuhotplug.h` defines the CPU hotplug state machine and registration APIs for startup and teardown callbacks. It is the ordering contract that kernel subsystems use to run per-CPU setup and cleanup as CPUs transition offline, starting, online, active, and dead. The source was read as a complete 526-line file.

## Important APIs, Types, and Functions

`enum cpuhp_state` defines ordered states across PREPARE, STARTING, and ONLINE sections, including dynamic ranges `CPUHP_BP_PREPARE_DYN` and `CPUHP_AP_ONLINE_DYN`. Registration APIs include `__cpuhp_setup_state()`, `__cpuhp_setup_state_cpuslocked()`, wrappers `cpuhp_setup_state()`, `cpuhp_setup_state_cpuslocked()`, nocalls variants, `cpuhp_setup_state_multi()`, instance add/remove helpers, `cpuhp_remove_state()`, `cpuhp_remove_state_nocalls()`, `cpuhp_remove_multi_state()`, and `cpuhp_online_idle()`. Architecture synchronization hooks include `cpuhp_ap_sync_alive()`, `arch_cpuhp_sync_state_poll()`, `arch_cpuhp_cleanup_kick_cpu()`, `arch_cpuhp_kick_ap_alive()`, `arch_cpuhp_init_parallel_bringup()`, `cpuhp_ap_report_dead()`, and `arch_cpuhp_cleanup_dead_cpu()`.

## Control Flow

CPU online invokes startup callbacks sequentially from `CPUHP_OFFLINE + 1` to `CPUHP_ONLINE`. CPU offline invokes teardown callbacks in reverse from `CPUHP_ONLINE - 1` down to offline. PREPARE callbacks run on a control CPU, STARTING callbacks run on the hotplugged CPU with interrupts disabled, and ONLINE callbacks run from the per-CPU hotplug thread with interrupts and preemption enabled. Multi-instance states add per-object callbacks after a state is prepared.

## State and Persistence Behavior

The hotplug core stores callback registrations and per-instance hlist nodes outside this header. Dynamic state allocations and registered instances persist until removed. The enum values are effectively a global ordering ABI inside the kernel.

## Dependencies and Integration Points

It depends on `linux/types.h` and forward-declared hlist/task types through included context. Integration points span scheduler, RCU, timers, IRQ controllers, perf, workqueues, block, networking, cpuidle, ACPI, architecture timers, watchdogs, random, KVM, and architecture bringup/dead-CPU synchronization.

## Risks and Edge Cases

Wrong state choice can run callbacks under the wrong CPU, interrupt, or preemption context. Startup failures must be unwound in reverse order. Multi-instance states require all instances to be removed before the state callback is removed. Dynamic states avoid unnecessary enum growth, but explicit ordering constraints must be modeled in the enum. Cpuslocked variants must only be used while the CPU read lock is held.

## Test Signals

Signals include CPU hotplug torture, callback ordering instrumentation, failure-injection in startup callbacks, multi-instance add/remove tests, dynamic state allocation exhaustion, !SMP builds, architecture parallel bringup tests, and lockdep validation for cpuslocked variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuhotplug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuhplock.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuhplock.h

## Purpose

`cpuhplock.h` declares CPU hotplug locking and offlining control helpers. It gives callers read/write serialization around CPU map and hotplug state changes. The source was read as a complete 50-line file.

## Important APIs, Types, and Functions

It declares lockdep predicates `lockdep_is_cpus_held()` and `lockdep_is_cpus_write_held()`. With `CONFIG_HOTPLUG_CPU`, APIs include `cpus_write_lock()`, `cpus_write_unlock()`, `cpus_read_lock()`, `cpus_read_unlock()`, `cpus_read_trylock()`, `lockdep_assert_cpus_held()`, `cpu_hotplug_disable_offlining()`, `cpu_hotplug_disable()`, `cpu_hotplug_enable()`, `clear_tasks_mm_cpumask()`, `remove_cpu()`, `cpu_device_down()`, and `smp_shutdown_nonboot_cpus()`. Disabled builds provide no-op stubs or `-EPERM` for `remove_cpu()`. It also defines a scoped lock guard for `cpus_read_lock`.

## Control Flow

Readers take the CPU read lock before inspecting CPU masks or policy state that hotplug might change. Writers take the write lock before adding/removing CPUs or disabling hotplug. Device offline paths route through `cpu_device_down()` and `remove_cpu()`.

## State and Persistence Behavior

The actual lock and disabled/offlining counters live in implementation files. This header only declares access and a scoped cleanup helper.

## Dependencies and Integration Points

It depends on cleanup helpers and errno definitions. It integrates with CPU core, cpumask readers, cpufreq/cpuidle policy code, scheduler domains, memory-management per-task CPU masks, and system shutdown.

## Risks and Edge Cases

Missing read locks can observe transient CPU masks. Write lock misuse can deadlock hotplug callbacks. Disabled-config stubs make lock assertions no-ops, so code must still be logically correct in hotplug builds.

## Test Signals

Signals include lockdep coverage, CPU hotplug stress under cpus read/write lock users, failed `remove_cpu()` on !HOTPLUG builds, shutdown nonboot CPU paths, and scoped guard compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuhplock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuidle.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuidle.h

## Purpose

`cpuidle.h` defines the generic CPU idle power-management framework: idle state descriptors, per-CPU idle device state, driver registration, governor registration, state selection/entry, suspend-to-idle helpers, and CPU PM wrapped idle entry macros. The source was read as a complete 356-line file.

## Important APIs, Types, and Functions

Important types include `struct cpuidle_state_usage`, `struct cpuidle_state`, `struct cpuidle_device`, `struct cpuidle_driver`, and `struct cpuidle_governor`. APIs include `disable_cpuidle()`, `cpuidle_select()`, `cpuidle_enter()`, `cpuidle_reflect()`, `cpuidle_register_driver()`, `cpuidle_register_device()`, `cpuidle_register()`, pause/resume helpers, `cpuidle_enable_device()`, `cpuidle_disable_device()`, `cpuidle_play_dead()`, `cpuidle_get_cpu_driver()`, `cpuidle_get_device()`, `cpuidle_find_deepest_state()`, `cpuidle_enter_s2idle()`, `cpuidle_use_deepest_state()`, `sched_idle_set_state()`, `default_idle_call()`, and governor registration. Macros include `CPU_PM_CPU_IDLE_ENTER*()` variants.

## Control Flow

Drivers register ordered idle states and devices. Governors select a state based on latency/residency and tick-stop constraints. `cpuidle_enter()` invokes the selected state's `enter`, `enter_dead`, or `enter_s2idle` callback. The CPU PM idle macros handle index zero by calling `cpu_do_idle()`, otherwise optionally send CPU PM notifications, enter/exit context tracking, invoke the low-level idle function, and return either the state index or `-1`.

## State and Persistence Behavior

`struct cpuidle_device` persists per CPU and tracks registration/enabled flags, last state, residency, poll limits, usage counters, sysfs kobjects, and coupled idle state. `struct cpuidle_driver` persists registered state metadata, safe state, cpumask, and governor preference. State usage counters are in-memory statistics exposed by the framework.

## Dependencies and Integration Points

It depends on percpu storage, lists, hrtimers, and context tracking. It integrates with scheduler idle, CPU PM notifiers, RCU/context tracking, tick broadcast, sysfs, suspend-to-idle, architecture idle instructions, coupled idle states, and governors.

## Risks and Edge Cases

`enter_s2idle` must not re-enable interrupts or manipulate clock event state when timekeeping is suspended. State flags such as `TIMER_STOP`, `RCU_IDLE`, and `COUPLED` must match callback behavior. Disabled-config stubs return `-ENODEV`. Coupled idle requires careful multi-CPU barriers. Context-tracking enter/exit ordering is lockdep-sensitive.

## Test Signals

Signals include cpuidle driver registration, state selection and reflect tests, sysfs usage counters, suspend-to-idle on deep states, CPU hotplug play-dead, RCU idle warnings, tick-stop behavior, coupled idle tests, and builds with `CONFIG_CPU_IDLE=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuidle_haltpoll.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuidle_haltpoll.h

## Purpose

`cpuidle_haltpoll.h` provides architecture hooks for enabling and disabling haltpoll cpuidle behavior on a CPU. The source was read as a complete 16-line file.

## Important APIs, Types, and Functions

With `CONFIG_ARCH_CPUIDLE_HALTPOLL`, it includes `asm/cpuidle_haltpoll.h`. Otherwise it defines no-op `arch_haltpoll_enable(unsigned int cpu)` and `arch_haltpoll_disable(unsigned int cpu)`.

## Control Flow

Haltpoll cpuidle code calls the architecture enable/disable hooks when CPUs or drivers activate haltpoll behavior. Architectures that need model-specific setup provide the implementation in asm headers.

## State and Persistence Behavior

The header owns no state. Architecture code may maintain per-CPU haltpoll controls, but unsupported builds do nothing.

## Dependencies and Integration Points

It integrates with cpuidle haltpoll drivers and architecture idle/halt controls.

## Risks and Edge Cases

Callers must tolerate no-op behavior on architectures without haltpoll support. Architecture implementations must be CPU-hotplug safe because hooks take a CPU number.

## Test Signals

Signals include build coverage with and without `CONFIG_ARCH_CPUIDLE_HALTPOLL`, haltpoll driver enable/disable on CPU hotplug, and architecture-specific idle behavior validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuidle_haltpoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask.h -->
# sources/distributed-fs/ceph-client/include/linux/cpumask.h

## Purpose

`cpumask.h` is the core bitmap API for representing sets of CPU IDs and the global possible, present, enabled, online, active, and dying CPU masks. It provides fast inline scan, set, clear, parse, print, allocate, and iteration helpers. The source was read as a complete 1,421-line file.

## Important APIs, Types, and Functions

It exposes `nr_cpu_ids`, `set_nr_cpu_ids()`, mask size constants, global masks `cpu_possible_mask`, `cpu_present_mask`, `cpu_enabled_mask`, `cpu_online_mask`, `cpu_active_mask`, and `cpu_dying_mask`, plus counters such as `__num_online_cpus` and `__num_possible_cpus`. Helpers include `cpumask_first*()`, `cpumask_next*()`, `cpumask_any*()`, `cpumask_nth*()`, `for_each_cpu*()` macros, `cpumask_set_cpu()`, `cpumask_clear_cpu()`, `cpumask_test_cpu()`, atomic test/set/clear helpers, boolean operations, equality/subset/intersection, weight, shifts, copy, parse/print helpers, off-stack allocation helpers, `get_cpu_mask()`, `num_*_cpus()`, `cpu_*()` predicates, `set_cpu_*()` mutators, and `cpumap_print_*()` sysfs helpers.

## Control Flow

Most helpers are inline wrappers over generic bitmap operations using an optimized bit count: fixed constants for small masks, `nr_cpu_ids` for runtime-sized masks, or `NR_CPUS` for larger clearing/copying. CPU hotplug and boot code update global masks, while readers iterate or query those masks to route scheduling, interrupts, memory policy, and device affinity.

## State and Persistence Behavior

Global cpumasks represent boot-lifetime CPU topology and dynamic hotplug state. `cpu_possible_mask` is fixed after boot sizing; present/online/active/enabled/dying masks vary with platform discovery and hotplug. `cpumask_var_t` may be heap-backed with `CONFIG_CPUMASK_OFFSTACK`, otherwise it is an on-stack one-element array wrapper.

## Dependencies and Integration Points

It depends on atomic, bitmap, cleanup, cpumask types, GFP types, NUMA, thread limits, generic types, and asm bug checks. It is foundational for scheduler, CPU hotplug, cpufreq, cpuidle, IRQ affinity, cpuset, NUMA, workqueues, and sysfs CPU-list exports.

## Risks and Edge Cases

Only `nr_cpu_ids` bits are valid for most masks. Direct assignment or dereference of `cpumask_var_t` can corrupt memory when off-stack allocation uses only `nr_cpumask_bits`. Iterators return `>= nr_cpu_ids` when no CPU is found. Global mask snapshots are racy without CPU hotplug locking. UP builds hardcode many predicates to CPU0, so modifying masks has no practical effect.

## Test Signals

Signals include cpumask unit tests for scan/next/wrap/nth operations, parse/print round trips, off-stack allocation failure paths, hotplug mask transitions under lockdep, UP/SMP build variants, sysfs cpulist/cpumap output size checks, and KASAN tests for allocation sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask_api.h -->
# sources/distributed-fs/ceph-client/include/linux/cpumask_api.h

## Purpose

`cpumask_api.h` is a one-line compatibility/include shim that includes `linux/cpumask.h`. The source was read as a complete 1-line file.

## Important APIs, Types, and Functions

It introduces no new APIs, types, macros, or functions. Consumers receive the complete `cpumask.h` API by including this file.

## Control Flow

There is no runtime control flow. Preprocessor inclusion forwards to `cpumask.h`.

## State and Persistence Behavior

No state is owned by this header. All state behavior is inherited from `cpumask.h`.

## Dependencies and Integration Points

It depends solely on `linux/cpumask.h`. Its integration role is source compatibility for code that includes `cpumask_api.h`.

## Risks and Edge Cases

The only risk is include-order or stale-include confusion. Any semantic behavior or ABI risk belongs to `cpumask.h`.

## Test Signals

Signals include compile coverage for users including `cpumask_api.h` directly and include-what-you-use checks ensuring no hidden APIs beyond `cpumask.h` are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask_types.h -->
# sources/distributed-fs/ceph-client/include/linux/cpumask_types.h

## Purpose

`cpumask_types.h` defines the fundamental `struct cpumask`, `cpumask_t`, `cpumask_bits()`, and `cpumask_var_t` type model. The source was read as a complete 66-line file.

## Important APIs, Types, and Functions

`typedef struct cpumask { DECLARE_BITMAP(bits, NR_CPUS); } cpumask_t` is the fixed-size mask type. `cpumask_bits(maskp)` exposes the bitmap storage. `cpumask_var_t` is either `struct cpumask *` when `CONFIG_CPUMASK_OFFSTACK=y`, or `struct cpumask[1]` otherwise.

## Control Flow

There is no runtime control flow. The preprocessor chooses pointer or array semantics at build time based on off-stack cpumask configuration.

## State and Persistence Behavior

Fixed `cpumask_t` objects contain `NR_CPUS` bits. Allocated `cpumask_var_t` objects may contain only `nr_cpumask_bits` worth of storage when off-stack, which is smaller than `NR_CPUS` on some systems.

## Dependencies and Integration Points

It depends on `linux/bitops.h` and `linux/threads.h`. It is included by `cpumask.h` and any code needing declarations without the whole API.

## Risks and Edge Cases

The header explicitly warns not to assign or return whole cpumask objects casually. Dereferencing `cpumask_var_t` and copying it by value can overrun allocation in off-stack builds. Per-CPU `cpumask_var_t` access must use `this_cpu_cpumask_var_t` style helpers from `cpumask.h`.

## Test Signals

Signals include builds with `CONFIG_CPUMASK_OFFSTACK` both enabled and disabled, static analysis for direct `*mask` copies, KASAN checks for allocated mask size, and compile tests for per-CPU cpumask variable access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuset.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuset.h

## Purpose

`cpuset.h` declares the kernel-internal cpuset/cgroup interface for constraining task CPU and memory-node placement. It provides static-key gates, lock helpers, allowed-mask queries, memory allocation retry sequencing, scheduler-domain rebuild hooks, and no-op fallbacks when cpusets are disabled. The source was read as a complete 308-line file.

## Important APIs, Types, and Functions

With `CONFIG_CPUSETS`, it exposes static keys `cpusets_pre_enable_key`, `cpusets_enabled_key`, and `cpusets_insane_config_key`, plus `cpusets_enabled()`, `cpuset_inc()`, `cpuset_dec()`, and `cpusets_insane_config()`. Core APIs include `cpuset_init()`, `cpuset_init_smp()`, `cpuset_force_rebuild()`, `cpuset_update_active_cpus()`, `cpuset_lock()`, `cpuset_unlock()`, `cpuset_cpus_allowed*()`, `cpuset_mems_allowed()`, `cpuset_current_node_allowed()`, `cpuset_zone_allowed()`, `cpuset_mems_allowed_intersects()`, memory pressure hooks, proc/status output hooks, spread-page helpers, deadline accounting rebuilds, scheduler-domain rebuild/reset, `read_mems_allowed_begin()`, `read_mems_allowed_retry()`, `set_mems_allowed()`, and `cpuset_nodes_allowed()`.

## Control Flow

Cpuset setup enables static branches in a deliberate order so memory-allocation retry loops do not deadlock when static-branch text patching is partially applied. Allocation code snapshots `mems_allowed_seq`, attempts an operation, and retries if cpuset memory policy changed concurrently. CPU hotplug and cpuset changes rebuild scheduler domains and active CPU masks.

## State and Persistence Behavior

Persistent state lives in cgroups, task `mems_allowed`, task spreading flags, static keys, and scheduler-domain partitions. `set_mems_allowed()` updates current task memory policy under task lock, IRQ save/restore, and seqcount protection.

## Dependencies and Integration Points

It depends on scheduler, topology, task, cpumask, nodemask, mm, mmu context, and jump labels. It integrates with cgroups, page allocator, NUMA policy, scheduler domains, procfs task status, deadline scheduler accounting, and CPU hotplug.

## Risks and Edge Cases

Static-key enable/disable ordering is subtle; reversing it can break retry loops. Allocation paths must retry only when appropriate after `read_mems_allowed_retry()`. Disabled-cpuset fallbacks return broad possible masks and all memory nodes, which can hide bugs in cpuset-enabled builds. Scheduler-domain rebuilds must be synchronized with hotplug and cgroup changes.

## Test Signals

Signals include cgroup cpuset selftests, memory-node update race tests, page allocation retry under concurrent cpuset changes, CPU hotplug with cpuset partitions, proc/status allowed mask output, v1 memory pressure tests, and builds with `CONFIG_CPUSETS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_core.h -->
# sources/distributed-fs/ceph-client/include/linux/crash_core.h

## Purpose

`crash_core.h` declares core crash-kexec and crash-dump helpers, crash memory range representation, crash hotplug event constants, and optional crash dm-crypt key export support. The source was read as a complete 99-line file.

## Important APIs, Types, and Functions

`struct crash_mem` stores a flexible array of memory `range` entries with current and maximum counts. With `CONFIG_CRASH_DUMP`, APIs include `crash_shrink_memory()`, `crash_get_memory_size()`, `crash_check_hotplug_support()`, `crash_exclude_mem_range()`, `crash_prepare_elf64_headers()`, `__crash_kexec()`, `crash_kexec()`, `kexec_should_crash()`, `kexec_crash_loaded()`, `crash_save_cpu()`, and `kimage_crash_copy_vmcoreinfo()`. Architecture-overridable hooks include crash memory protection and crash hotplug support. Hotplug action constants cover CPU and memory add/remove. `CONFIG_CRASH_DM_CRYPT` adds `crash_load_dm_crypt_keys()` and `dm_crypt_keys_read()`.

## Control Flow

On panic or fatal conditions, crash paths decide whether a crash kernel is loaded, save CPU state, prepare vmcore information, and jump through kexec. Crash dump setup filters reserved ranges and builds ELF headers. Hotplug support updates crash kernel metadata when CPUs or memory change.

## State and Persistence Behavior

Crash memory ranges and vmcoreinfo are in-memory metadata used by the crash kernel. Architecture protection hooks can protect the reserved crash kernel memory after loading. dm-crypt key data may be copied into crash image metadata when configured.

## Dependencies and Integration Points

It depends on linkage and ELF core definitions. It integrates with kexec, panic handling, CPU register capture, memory hotplug, crashkernel reservation, architecture memory protection, vmcoreinfo, and dm-crypt crash key handling.

## Risks and Edge Cases

Crash paths run in failure contexts where locking and allocation options are limited. Range exclusion and ELF header generation must avoid overlapping or invalid memory. Hotplug metadata must stay synchronized with loaded crash images. Disabled-config stubs silently do nothing, so callers must not assume crash functionality exists.

## Test Signals

Signals include kdump boot tests, crashkernel reserved memory protection checks, crash range exclusion unit tests, ELF64 header validation, CPU/memory hotplug update tests, dm-crypt key copy/read tests, and builds with `CONFIG_CRASH_DUMP=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_dump.h -->
# sources/distributed-fs/ceph-client/include/linux/crash_dump.h

## Purpose

`crash_dump.h` declares second-kernel vmcore access, ELF core header state, old-memory copying, vmcore callbacks, device dump registration, and helpers that identify whether the running kernel is a kdump kernel. The source was read as a complete 192-line file.

## Important APIs, Types, and Functions

Global addresses include `elfcorehdr_addr`, `elfcorehdr_size`, and `dm_crypt_keys_addr`, with sentinel values `ELFCORE_ADDR_MAX` and `ELFCORE_ADDR_ERR`. Crash-dump APIs include `elfcorehdr_alloc()`, `elfcorehdr_free()`, `elfcorehdr_read()`, `elfcorehdr_read_notes()`, `elfcorehdr_fill_device_ram_ptload_elf64()`, `remap_oldmem_pfn_range()`, `copy_oldmem_page()`, `copy_oldmem_page_encrypted()`, `vmcore_cleanup()`, architecture ELF checks, `is_kdump_kernel()`, `is_vmcore_usable()`, and `vmcore_unusable()`. `struct vmcore_cb` lets drivers validate PFNs or contribute device RAM ranges. `struct vmcore_range` plus `vmcore_alloc_add_range()` and `vmcore_free_ranges()` manage ranges. `struct vmcoredd_data` supports device-specific dumps via `vmcore_add_device_dump()`. `read_from_oldmem()` backs proc vmcore reads.

## Control Flow

The kdump kernel receives an ELF core header address, validates usability, exposes `/proc/vmcore`, and maps/copies pages from old memory on read. Registered callbacks can reject non-RAM PFNs or add device-managed RAM ranges. Device dump callbacks append driver-specific data to the vmcore.

## State and Persistence Behavior

The key persistent state for the kdump kernel is the ELF core header address/size and optional dm-crypt key address. Vmcore callbacks and range lists are runtime state. `vmcore_unusable()` preserves the fact this is a kdump kernel while preventing vmcore use.

## Dependencies and Integration Points

It depends on kexec, procfs, ELF, page tables, and UAPI vmcore definitions. It integrates with `/proc/vmcore`, memory hotplug/device memory drivers, encrypted memory reads, vmcore device dumps, architecture ELF checks, and old-memory remapping.

## Risks and Edge Cases

Sentinel address handling is critical because `-1ULL` and `-2ULL` have different meanings. Old memory reads must avoid non-RAM or ballooned/device memory pages unless callbacks allow them. Device dump callbacks must provide bounded data. Encrypted reads must choose the correct old-memory copy helper.

## Test Signals

Signals include kdump vmcore read tests, invalid elfcore header sentinel tests, vmcore callback register/unregister coverage, device dump collection tests, encrypted old-memory read tests, vmcore range allocation/free leak tests, and `CONFIG_PROC_VMCORE` disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_reserve.h -->
# sources/distributed-fs/ceph-client/include/linux/crash_reserve.h

## Purpose

`crash_reserve.h` declares crashkernel reservation resources, command-line parsing, optional CMA-backed crash ranges, and generic architecture reservation defaults. The source was read as a complete 66-line file.

## Important APIs, Types, and Functions

Global resources include `crashk_res`, `crashk_low_res`, `crashk_cma_ranges[]`, and optionally `crashk_cma_cnt`. `parse_crashkernel()` parses crashkernel command-line sizing, base, low memory, CMA size, and high/low mode. `reserve_crashkernel_cma()` handles CMA reservation. With generic crashkernel reservation support, defaults include `arch_add_crash_res_to_iomem()`, `DEFAULT_CRASH_KERNEL_LOW_SIZE`, `CRASH_ALIGN`, `CRASH_ADDR_LOW_MAX`, `CRASH_ADDR_HIGH_MAX`, and `reserve_crashkernel_generic()`.

## Control Flow

Early boot parses crashkernel parameters, chooses crash/high/low/CMA sizes, reserves resources, and optionally reports them in iomem. Generic reservation code is used when the architecture opts in, otherwise the generic function is a no-op.

## State and Persistence Behavior

Crashkernel memory is represented by global `struct resource` objects and optional CMA ranges for the boot lifetime. These reservations protect memory for the capture kernel.

## Dependencies and Integration Points

It depends on linkage, ELF core definitions, optional architecture crash reservation headers, resources, ranges, memblock, and CMA configuration. It integrates with boot command-line parsing, iomem resources, kexec/kdump, and architecture memory layout constraints.

## Risks and Edge Cases

Crashkernel sizing must respect low-memory requirements, high-memory limits, alignment, and reserved resource overlap. CMA crash ranges only exist with both CMA and generic architecture support. Architecture defaults may be overridden and must match platform addressing.

## Test Signals

Signals include boot tests for `crashkernel=` variants, resource tree inspection, low/high reservation boundary tests, CMA crashkernel reservation tests, architecture override builds, and kdump load/boot validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_reserve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-ccitt.h -->
# sources/distributed-fs/ceph-client/include/linux/crc-ccitt.h

## Purpose

`crc-ccitt.h` declares the kernel's table-driven CRC-CCITT helper. The source was read as a complete 16-line file.

## Important APIs, Types, and Functions

It exposes `crc_ccitt_table[256]`, `crc_ccitt(u16 crc, const u8 *buffer, size_t len)`, and inline `crc_ccitt_byte(u16 crc, const u8 c)`, which advances the CRC by one byte using `(crc >> 8) ^ table[(crc ^ c) & 0xff]`.

## Control Flow

Callers seed a CRC, process buffers through `crc_ccitt()`, or process single bytes through the inline helper. Incremental callers feed the previous returned CRC back into the next call.

## State and Persistence Behavior

The only shared state is the constant lookup table. No mutable state or persistence is owned.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with drivers/protocols that require CCITT-style 16-bit CRCs.

## Risks and Edge Cases

Correctness depends on matching the expected seed, byte order, and final XOR convention of the protocol. The helper does not validate buffer pointers or lengths beyond normal C behavior.

## Test Signals

Signals include known-vector CRC tests, incremental versus one-shot comparisons, zero-length input, and protocol driver checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-ccitt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-itu-t.h -->
# sources/distributed-fs/ceph-client/include/linux/crc-itu-t.h

## Purpose

`crc-itu-t.h` declares CRC ITU-T V.41 helpers for a 16-bit `0x1021` polynomial with initial value 0. The source was read as a complete 26-line file.

## Important APIs, Types, and Functions

It exposes `crc_itu_t_table[256]`, `crc_itu_t(u16 crc, const u8 *buffer, size_t len)`, and inline `crc_itu_t_byte(u16 crc, const u8 data)`, which advances the CRC with `(crc << 8) ^ table[((crc >> 8) ^ data) & 0xff]`.

## Control Flow

Callers compute a full-buffer CRC or update one byte at a time, supplying either the initial seed or previous CRC for incremental operation.

## State and Persistence Behavior

Only the constant lookup table is shared. No mutable state is maintained.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with kernel protocol implementations that require ITU-T V.41 CRC semantics.

## Risks and Edge Cases

CRC variants are easy to confuse: seed, bit direction, polynomial representation, and final XOR must match the protocol. Byte helper users must preserve the returned CRC between chunks.

## Test Signals

Signals include protocol known vectors, byte-at-a-time versus buffer equivalence, zero-length input, and cross-checks against documented ITU-T V.41 examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-itu-t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-t10dif.h -->
# sources/distributed-fs/ceph-client/include/linux/crc-t10dif.h

## Purpose

`crc-t10dif.h` declares the T10 DIF CRC helper used for storage data integrity fields. The source was read as a complete 14-line file.

## Important APIs, Types, and Functions

It declares `crc_t10dif_update(u16 crc, const u8 *p, size_t len)` and inline `crc_t10dif(const u8 *p, size_t len)`, which computes from seed 0 by calling the update helper.

## Control Flow

Storage code can compute a one-shot T10 DIF CRC with `crc_t10dif()` or continue an existing CRC with `crc_t10dif_update()`.

## State and Persistence Behavior

The header owns no state. Any table or optimized state lives in the implementation.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with block/SCSI/NVMe integrity paths and protection information code.

## Risks and Edge Cases

Seed choice must match the storage protocol. Incremental boundaries must preserve the intermediate CRC exactly. Hardware-offload paths should match this software helper.

## Test Signals

Signals include T10 DIF known vectors, block integrity metadata validation, hardware/software CRC equivalence, incremental chunking tests, and zero-length buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc-t10dif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc16.h -->
# sources/distributed-fs/ceph-client/include/linux/crc16.h

## Purpose

`crc16.h` declares the standard CRC-16 helper using polynomial `0x8005` and initial value 0. The source was read as a complete 21-line file.

## Important APIs, Types, and Functions

It declares `u16 crc16(u16 crc, const u8 *p, size_t len)`.

## Control Flow

Callers pass a seed or previous CRC and a buffer. The implementation returns the updated CRC, supporting one-shot and incremental use.

## State and Persistence Behavior

No state is stored by the header. Implementation lookup tables, if any, are shared read-only.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with drivers and protocols requiring this CRC-16 variant.

## Risks and Edge Cases

Protocols often differ in bit order, initial value, and final inversion; using this helper for a different CRC-16 variant will silently produce wrong checksums.

## Test Signals

Signals include known-vector checks, incremental equivalence tests, zero-length input, and protocol-level checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32.h -->
# sources/distributed-fs/ceph-client/include/linux/crc32.h

## Purpose

`crc32.h` declares IEEE CRC-32, CRC-32C, optimization reporting, and Ethernet CRC helpers. The source was read as a complete 110-line file.

## Important APIs, Types, and Functions

APIs include `crc32_le()`, alias `crc32()`, `crc32_be()`, `crc32c()`, and optional `crc32_optimizations()`. Optimization flags are `CRC32_LE_OPTIMIZATION`, `CRC32_BE_OPTIMIZATION`, and `CRC32C_OPTIMIZATION`. Ethernet helpers are `ether_crc(length, data)` and `ether_crc_le(length, data)`.

## Control Flow

Callers seed a CRC, process a buffer, and optionally invert before/after according to protocol. LE and BE helpers implement different bit orders for the same IEEE polynomial, while `crc32c()` implements Castagnoli. Ethernet helpers seed with `~0` and bit-reverse where needed.

## State and Persistence Behavior

The header owns no mutable state. Architecture-specific optimized implementations may be selected by the implementation and reported by `crc32_optimizations()`.

## Dependencies and Integration Points

It depends on `linux/types.h` and `linux/bitrev.h`. It integrates with networking, filesystems, storage, crypto/hash code, and architecture CRC acceleration.

## Risks and Edge Cases

The helpers do not perform automatic initial/final inversion except Ethernet macros. CRC-32 and CRC-32C are distinct and not interchangeable. Runtime optimization flags depend on both config and CPU features.

## Test Signals

Signals include IEEE and CRC-32C known vectors, LE/BE distinction tests, Ethernet hash table generation checks, architecture optimized versus generic comparisons, and zero-length/incremental tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32c.h -->
# sources/distributed-fs/ceph-client/include/linux/crc32c.h

## Purpose

`crc32c.h` is a compatibility wrapper that includes `linux/crc32.h` for CRC-32C access. The source was read as a complete 7-line file.

## Important APIs, Types, and Functions

It introduces no new API. Consumers get `crc32c()` and related CRC32 declarations from `crc32.h`.

## Control Flow

There is no runtime flow; preprocessing forwards to `crc32.h`.

## State and Persistence Behavior

No state is owned by this header.

## Dependencies and Integration Points

It depends only on `linux/crc32.h` and preserves include compatibility for code that historically included `crc32c.h`.

## Risks and Edge Cases

Semantic risks are those of `crc32.h`; this file's main concern is avoiding duplicate or divergent CRC-32C declarations.

## Test Signals

Signals include compile coverage for direct `crc32c.h` inclusion and known-vector tests for `crc32c()` through that include path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32poly.h -->
# sources/distributed-fs/ceph-client/include/linux/crc32poly.h

## Purpose

`crc32poly.h` names the integer polynomial constants used by the kernel CRC-32 helpers. The source was read as a complete 14-line file.

## Important APIs, Types, and Functions

It defines `CRC32_POLY_LE` as `0xedb88320`, `CRC32_POLY_BE` as `0x04c11db7`, and `CRC32C_POLY_LE` as `0x82f63b78`.

## Control Flow

There is no runtime flow. The constants are used at compile time by table generation, tests, or implementations.

## State and Persistence Behavior

No state is owned.

## Dependencies and Integration Points

It has no includes and integrates with CRC32 implementations and table builders.

## Risks and Edge Cases

Polynomial constants encode bit order. Using the LE reflected polynomial in a BE algorithm, or vice versa, produces incompatible CRCs.

## Test Signals

Signals include table-generation tests, cross-checking constants against `crc32.h` documentation, and known-vector CRC validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32poly.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc4.h -->
# sources/distributed-fs/ceph-client/include/linux/crc4.h

## Purpose

`crc4.h` declares a small CRC-4 helper for bit-length bounded inputs. The source was read as a complete 9-line file.

## Important APIs, Types, and Functions

It declares `uint8_t crc4(uint8_t c, uint64_t x, int bits)`.

## Control Flow

Callers pass a current CRC nibble, input bits packed into a 64-bit value, and the number of bits to process. The implementation returns the updated 4-bit CRC in an 8-bit container.

## State and Persistence Behavior

No state is owned.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with compact hardware/protocol fields using CRC-4 checks.

## Risks and Edge Cases

The `bits` argument must match the meaningful bits in `x`; excessive or negative values would be implementation-sensitive. Callers must mask or interpret only the low CRC bits as required by their protocol.

## Test Signals

Signals include known-vector CRC-4 tests, boundary tests for 0, 1, and maximum expected bit counts, and protocol field validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc64.h -->
# sources/distributed-fs/ceph-client/include/linux/crc64.h

## Purpose

`crc64.h` declares CRC64 helpers for big-endian ECMA-182 and CRC64-NVME. The source was read as a complete 28-line file.

## Important APIs, Types, and Functions

It declares `crc64_be(u64 crc, const void *p, size_t len)` and `crc64_nvme(u64 crc, const void *p, size_t len)`. The NVMe helper includes bitwise inversion at the beginning and end.

## Control Flow

Callers pass a seed or previous CRC and a buffer. `crc64_be()` supports ECMA-182 semantics; `crc64_nvme()` follows NVMe NVM Command Set CRC64 behavior including inversion.

## State and Persistence Behavior

No mutable state is owned by the header. Implementations may use constant tables or architecture acceleration.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with storage, NVMe protection, and protocols requiring 64-bit CRCs.

## Risks and Edge Cases

The two helpers have different variant semantics, especially NVMe inversion. Seed values must match the protocol, and incremental use must preserve the correct intermediate value.

## Test Signals

Signals include ECMA-182 and NVMe known vectors, one-shot versus incremental equivalence, zero-length input, and storage metadata validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc7.h -->
# sources/distributed-fs/ceph-client/include/linux/crc7.h

## Purpose

`crc7.h` declares a big-endian CRC-7 helper. The source was read as a complete 8-line file.

## Important APIs, Types, and Functions

It declares `u8 crc7_be(u8 crc, const u8 *buffer, size_t len)`.

## Control Flow

Callers seed the CRC, process a buffer, and receive the updated CRC-7 in an 8-bit container.

## State and Persistence Behavior

No state is owned by the header.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with protocols such as MMC/SD-style command CRC checks that use CRC-7 variants.

## Risks and Edge Cases

Callers must match the protocol's seed and final bit placement. Only the relevant seven bits should be interpreted.

## Test Signals

Signals include known command-vector tests, incremental equivalence, zero-length input, and protocol frame validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc8.h -->
# sources/distributed-fs/ceph-client/include/linux/crc8.h

## Purpose

`crc8.h` declares table population and calculation helpers for configurable CRC-8 polynomials. The source was read as a complete 101-line file.

## Important APIs, Types, and Functions

Constants include `CRC8_INIT_VALUE`, `CRC8_GOOD_VALUE(table)`, `CRC8_TABLE_SIZE`, and `DECLARE_CRC8_TABLE(table)`. APIs include `crc8_populate_lsb()`, `crc8_populate_msb()`, and `crc8()`.

## Control Flow

Callers allocate a 256-entry table, populate it with the polynomial and bit direction, then call `crc8()` with a data pointer, byte count, and seed or previous CRC. Validation protocols may compare the final value against `CRC8_GOOD_VALUE()`.

## State and Persistence Behavior

CRC tables are caller-owned mutable arrays, often static after population. The header owns no global mutable state.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with device protocols that use custom CRC-8 polynomials.

## Risks and Edge Cases

The caller must choose LSB or MSB table population to match the protocol's bit order. The helper does not complement the generated CRC; callers are responsible for final inversion/insertion. Table size must be exactly 256 entries.

## Test Signals

Signals include table population known-vector tests for LSB and MSB polynomials, one-shot and chunked `crc8()` equivalence, validation of `CRC8_GOOD_VALUE()`, and driver protocol checksum tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cred.h -->
# sources/distributed-fs/ceph-client/include/linux/cred.h

## Purpose

`cred.h` defines Linux task credential structures and helpers for UID/GID, capabilities, keyrings, LSM security, user namespaces, supplementary groups, copy-on-write credential replacement, override/revert credentials, and safe current/task credential access. The source was read as a complete 429-line file.

## Important APIs, Types, and Functions

`struct group_info` stores refcounted supplementary groups. `struct cred` stores real/saved/effective/fs UID/GID, securebits, capability sets, optional keyrings, optional LSM security pointer, user and namespace accounting, supplementary groups, and RCU deletion state. Group APIs include `get_group_info()`, `put_group_info()`, `groups_alloc()`, `groups_free()`, `in_group_p()`, `in_egroup_p()`, `groups_search()`, `set_current_groups()`, `set_groups()`, `may_setgroups()`, and `groups_sort()`. Credential APIs include `prepare_creds()`, `prepare_exec_creds()`, `commit_creds()`, `abort_creds()`, `prepare_kernel_cred()`, `kernel_cred()`, `set_security_override()`, `set_create_files_as()`, `cred_fscmp()`, `cred_init()`, `set_cred_ucounts()`, `override_creds()`, `revert_creds()`, `get_cred*()`, `put_cred*()`, current/task accessor macros, and namespace helpers.

## Control Flow

Credential updates follow copy-on-write: allocate or prepare a mutable credential, modify it, validate invariants such as ambient capabilities, then atomically commit it to the task. Temporary privilege changes use `override_creds()` and `revert_creds()` or scoped wrappers. Readers access current credentials directly or other tasks' objective credentials under RCU or by pinning with `get_task_cred()`.

## State and Persistence Behavior

Credentials are refcounted immutable objects once committed and freed through RCU unless marked non-RCU. Task `real_cred` and `cred` distinguish objective and subjective security context. Supplementary groups are separately refcounted. Keyrings, user namespace, user/ucounts, and LSM security pointers persist through the credential lifetime.

## Dependencies and Integration Points

It depends on capabilities, init, keys, atomic/refcount, uidgid, scheduler, and user accounting. It integrates with VFS permission checks, process management, exec/fork, LSMs, user namespaces, keyrings, capabilities, and multiuser/group management.

## Risks and Edge Cases

Committed credentials should be treated as immutable despite non-const internals for refcounts. Accessing another task's credentials without RCU or a pinned reference is unsafe. Ambient capabilities must remain a subset of permitted and inheritable. Override/revert pairs must be balanced or subjective credentials leak across operations. `CONFIG_MULTIUSER=n` stubs allow all group checks.

## Test Signals

Signals include credentials selftests, setuid/setgid/exec transitions, namespace capability tests, RCU credential lifetime tests, override/revert scoped cleanup tests, supplementary group sorting/search tests, keyring credential propagation, and LSM hook coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/crush.h -->
# sources/distributed-fs/ceph-client/include/linux/crush/crush.h

## Purpose

`crush.h` defines Ceph's CRUSH map data structures, rule language, bucket algorithms, replacement choose-argument structures, map-level tunables, destroy helpers, and mapper workspace layout. The source was read as a complete 360-line file.

## Important APIs, Types, and Functions

Constants include `CRUSH_MAGIC`, maximum depth/rule/device weights, `CRUSH_ITEM_UNDEF`, and `CRUSH_ITEM_NONE`. Rule structures include `crush_rule_step`, `crush_rule_mask`, and `crush_rule`, with opcodes such as `TAKE`, `CHOOSE_FIRSTN`, `CHOOSE_INDEP`, `CHOOSELEAF_*`, `EMIT`, and tunable override steps. Bucket types include uniform, list, tree, straw, and straw2 through `struct crush_bucket` and specialized bucket structs. Replacement data uses `crush_weight_set`, `crush_choose_arg`, and `crush_choose_arg_map`. `struct crush_map` stores bucket/rule arrays, limits, choose tunables, working size, and kernel rbtrees for names/types/choose args. APIs include `crush_bucket_alg_name()`, bucket/rule/map destroy helpers, `crush_get_bucket_item_weight()`, `crush_calc_tree_node()`, `clear_crush_names()`, and `clear_choose_args()`.

## Control Flow

The mapper interprets rules over the immutable map, taking a starting bucket/device, choosing items according to bucket algorithms and weights, descending leaves when requested, and emitting results. Workspace structures store temporary bucket permutations outside the immutable map.

## State and Persistence Behavior

`struct crush_map` is durable in memory as part of Ceph OSD maps and should be treated as immutable by mapping operations. Kernel rbtrees store decoded names and choose args. Workspace is separate per mapping call or reusable per caller and avoids mutating the map.

## Dependencies and Integration Points

In-kernel builds depend on rbtree and Linux types; userspace builds use `crush_compat.h`. It integrates with Ceph OSD map decoding, placement decisions, replicated/erasure-coded object mapping, and CRUSH choose-argument overrides.

## Risks and Edge Cases

Bucket algorithms differ in stability and cost. Tree buckets are legacy and excluded from default allowed legacy algorithms. Fixed-point weights must stay within defined limits. Choose-argument arrays must match bucket counts and straw2 item order. Rule masks and sizes must select the intended rule or placement can change cluster-wide.

## Test Signals

Signals include deterministic CRUSH mapping vectors, map encode/decode round trips, bucket destroy/leak tests, straw2 choose-arg override tests, rule selection tests, failure/out-weight behavior, and comparison with userspace Ceph CRUSH results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/crush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/hash.h -->
# sources/distributed-fs/ceph-client/include/linux/crush/hash.h

## Purpose

`hash.h` declares CRUSH hash identifiers and fixed-arity hash helpers used by Ceph placement calculations. The source was read as a complete 24-line file.

## Important APIs, Types, and Functions

It defines `CRUSH_HASH_RJENKINS1` and `CRUSH_HASH_DEFAULT`. APIs include `crush_hash_name()`, `crush_hash32()`, `crush_hash32_2()`, `crush_hash32_3()`, `crush_hash32_4()`, and `crush_hash32_5()`.

## Control Flow

CRUSH bucket selection calls these hash helpers with stable placement inputs such as object hash, replica index, bucket IDs, and retry counters. The hash type selects the concrete algorithm.

## State and Persistence Behavior

No state is stored. Determinism across kernel and userspace implementations is the key persistence property because object placement must remain stable across boots and clients.

## Dependencies and Integration Points

It uses Linux types in kernel builds or `crush_compat.h` outside the kernel. It integrates with `crush.h` bucket `hash` fields and the CRUSH mapper.

## Risks and Edge Cases

Changing hash behavior or constants changes data placement. Unsupported hash type handling must stay consistent with map decoding and userspace Ceph.

## Test Signals

Signals include fixed hash vectors for each arity, CRUSH mapping determinism tests, kernel/userspace hash comparison, and invalid hash type handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/mapper.h -->
# sources/distributed-fs/ceph-client/include/linux/crush/mapper.h

## Purpose

`mapper.h` declares the CRUSH rule lookup and mapping API that maps an input value to output device IDs using a CRUSH map, weights, workspace, and optional choose arguments. The source was read as a complete 34-line file.

## Important APIs, Types, and Functions

APIs include `crush_find_rule()`, `crush_do_rule()`, `crush_work_size()`, and `crush_init_workspace()`. `crush_do_rule()` accepts a map, rule number, input `x`, result buffer and size, weight array and size, caller-provided workspace, and choose-arg overrides.

## Control Flow

Callers find a rule matching ruleset/type/size, allocate or reuse workspace sized by `crush_work_size()`, initialize it, and invoke `crush_do_rule()` to fill the result array. The rule interpreter uses the immutable map and mutable workspace while honoring per-device weights and optional replacement choose args.

## State and Persistence Behavior

The mapper should not mutate the `crush_map`. Workspace is caller-owned transient state and may be stack, heap, or long-lived per-thread storage if reinitialized appropriately.

## Dependencies and Integration Points

It includes `crush.h` and integrates with Ceph OSD map placement, object locator hashing, and CRUSH tunables.

## Risks and Edge Cases

`result_max` must match caller expectations and workspace sizing. Weight arrays must cover `weight_max` devices. Reusing workspace without initialization can leak previous permutations. Invalid rules or undersized result buffers can produce incomplete placement.

## Test Signals

Signals include deterministic placement vectors, workspace size/init tests, invalid rule lookup tests, underweight/out device mapping, choose-arg override tests, and kernel/userspace mapper parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/mapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crypto.h -->
# sources/distributed-fs/ceph-client/include/linux/crypto.h

## Purpose

`crypto.h` defines the generic Linux kernel crypto transform and algorithm registration contract. It covers algorithm type/flag masks, transform request flags, algorithm descriptors, async request completion, transform allocation/destruction, and small inline query/request helpers. The source was read as a complete 529-line file.

## Important APIs, Types, and Functions

Constants include `CRYPTO_ALG_TYPE_*`, algorithm state/feature flags such as `CRYPTO_ALG_ASYNC`, `CRYPTO_ALG_NEED_FALLBACK`, `CRYPTO_ALG_INTERNAL`, `CRYPTO_ALG_ALLOCATES_MEMORY`, `CRYPTO_ALG_FIPS_INTERNAL`, `CRYPTO_ALG_REQ_VIRT`, and transform request flags like `CRYPTO_TFM_REQ_MAY_SLEEP`, `MAY_BACKLOG`, and `ON_STACK`. Types include `crypto_completion_t`, `struct crypto_async_request`, `struct cipher_alg`, `struct crypto_alg`, `struct crypto_wait`, and `struct crypto_tfm`. APIs include `crypto_req_done()`, `crypto_wait_req()`, `crypto_init_wait()`, `crypto_has_alg()`, `crypto_alloc_base()`, `crypto_destroy_tfm()`, `crypto_free_tfm()`, transform query helpers, flag setters/clearers, `crypto_tfm_is_async()`, `crypto_req_on_stack()`, `crypto_request_set_callback()`, `crypto_request_set_tfm()`, `crypto_request_clone()`, and `crypto_stack_request_init()`.

## Control Flow

Algorithm providers register `struct crypto_alg` instances with names, flags, priority, context sizes, callbacks, and module owner. Users allocate transforms by algorithm name/type/mask, configure request callbacks, submit operations through type-specific APIs, and handle async completion. `crypto_wait_req()` converts `-EINPROGRESS` or `-EBUSY` into a blocking wait on `struct crypto_wait`.

## State and Persistence Behavior

`struct crypto_alg` persists while registered and is refcounted by users. `struct crypto_tfm` is a user-instantiated transform with flags, NUMA node, optional fallback transform, algorithm pointer, and aligned private context. `struct crypto_async_request` carries per-operation state and callbacks. No disk persistence is involved.

## Dependencies and Integration Points

It depends on completions, errno, refcount types, slab allocation, and common types. It integrates with type-specific crypto APIs such as skcipher, aead, hash, rng, akcipher, kpp, compression, template instances, module loading, self-tests, and hardware accelerators.

## Risks and Edge Cases

Alignment and allocation flags are security/performance-sensitive. Algorithms marked not allocating memory still have documented edge cases unless users satisfy alignment and scatterlist constraints. Async callbacks must handle backlog and completion races. Stack requests must preserve `CRYPTO_TFM_REQ_ON_STACK`. Algorithm flags determine fallback, FIPS/internal visibility, userspace exposure, and module loading behavior.

## Test Signals

Signals include crypto selftests, algorithm registration/unregistration, transform allocation by name/type/mask, async completion and `crypto_wait_req()` behavior, fallback tests, alignment stress, no-allocation request tests, FIPS/internal visibility checks, and hardware/software equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cs5535.h -->
# sources/distributed-fs/ceph-client/include/linux/cs5535.h

## Purpose

`cs5535.h` defines AMD CS5535/CS5536 chipset MSRs, PM/ACPI/GPIO/MFGPT register constants, VSA2 probing helpers, and public GPIO/MFGPT helper declarations. The source was read as a complete 236-line file.

## Important APIs, Types, and Functions

It defines many MSR constants for GLIU, GLCP, LBAR, PIC, MFGPT, RTC, and reset controls. Inline helpers include `cs5535_pic_unreqz_select_high()` and `cs5535_has_vsa2()`. GPIO constants cover output, input, event, lock, edge, filter, and map registers. GPIO APIs include `cs5535_gpio_set()`, `cs5535_gpio_clear()`, `cs5535_gpio_isset()`, `cs5535_gpio_set_irq()`, and `cs5535_gpio_setup_event()`. MFGPT constants describe timers, domains, comparators, events, registers, and setup bits. MFGPT APIs include `cs5535_mfgpt_read()`, `cs5535_mfgpt_write()`, `cs5535_mfgpt_toggle_event()`, `cs5535_mfgpt_set_irq()`, `cs5535_mfgpt_alloc_timer()`, `cs5535_mfgpt_free_timer()`, plus setup/release IRQ inline wrappers.

## Control Flow

Platform drivers read/write model-specific registers to configure chipset blocks, map GPIO events, and allocate MFGPT timers. `cs5535_has_vsa2()` writes VSA virtual-register indexes, reads the signature once, caches the result in a static local, and returns whether AMD or General Software VSA2 is present.

## State and Persistence Behavior

Most state lives in chipset registers and allocated MFGPT timer objects. `cs5535_has_vsa2()` caches probe result in a static `has_vsa2`. Register writes persist in hardware until reset or reconfiguration.

## Dependencies and Integration Points

It depends on `asm/msr.h` and `linux/io.h`. It integrates with x86 Geode/CS5535 platform drivers, GPIO, interrupt routing, ACPI/PM blocks, watchdog/timer users, and firmware/VSA virtual registers.

## Risks and Edge Cases

Register values are hardware-specific; wrong MSR or I/O writes can break interrupt routing or power management. Comments note datasheet errata and dword-only access requirements for PM/PMS blocks. VSA probing uses fixed I/O ports and cached state. Timer allocation and IRQ setup must be balanced.

## Test Signals

Signals include platform boot on CS5535/CS5536 hardware or emulation, GPIO set/clear/read tests, IRQ routing validation, MFGPT allocation/free and comparator IRQ tests, VSA2 signature detection, and suspend/resume PM register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cs5535.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ctype.h -->
# sources/distributed-fs/ceph-client/include/linux/ctype.h

## Purpose

`ctype.h` defines the kernel's byte-oriented character classification and case-conversion helpers. Unlike libc ctype, it does not handle EOF specially. The source was read as a complete 81-line file.

## Important APIs, Types, and Functions

Classification mask bits include `_U`, `_L`, `_D`, `_C`, `_P`, `_S`, `_X`, and `_SP`. `_ctype[]` is the lookup table, and `__ismask(x)` indexes it after casting to unsigned char. Macros include `isalnum`, `isalpha`, `iscntrl`, `isgraph`, `islower`, `isprint`, `ispunct`, `isspace`, `isupper`, `isxdigit`, `isascii`, and `toascii`. `isdigit()` uses `__builtin_isdigit` if available or an inline range check. Case helpers include `__tolower()`, `__toupper()`, `tolower`, `toupper`, fast internal `_tolower()`, and `isodigit()`.

## Control Flow

Classification macros look up `_ctype` masks for a byte. Case conversion checks classification before subtracting ASCII offsets. `_tolower()` is a fast internal helper that blindly ORs bit `0x20`.

## State and Persistence Behavior

The only shared state is the constant `_ctype` table. There is no mutable state.

## Dependencies and Integration Points

It depends on `linux/compiler.h` and is used throughout string parsing, sysfs/procfs input handling, command-line parsing, filesystems, and drivers.

## Risks and Edge Cases

Inputs are byte/ASCII-oriented and not locale-aware. EOF is not special. `_tolower()` must only be used when the caller knows the input is uppercase ASCII or can tolerate bit modification. `isspace()` intentionally returns false for NUL.

## Test Signals

Signals include table-driven classification tests for all 256 byte values, case conversion tests, NUL whitespace behavior, `isodigit()` range tests, and parser tests that depend on ASCII classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ctype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cuda.h -->
# sources/distributed-fs/ceph-client/include/linux/cuda.h

## Purpose

`cuda.h` declares interfaces for Apple CUDA microcontroller support, which controls ADB, power, RTC, and related system functions on supported machines. The source was read as a complete 23-line file.

## Important APIs, Types, and Functions

It declares `find_via_cuda()`, `cuda_request(struct adb_request *req, void (*done)(struct adb_request *), int nbytes, ...)`, `cuda_poll()`, `cuda_get_time()`, and `cuda_set_rtc_time(struct rtc_time *tm)`.

## Control Flow

Platform initialization probes for VIA CUDA. Drivers submit variable-length CUDA/ADB requests with an optional completion callback. Polling services the controller where interrupt-driven flow is unavailable or during early boot. RTC helpers read and set controller-backed time.

## State and Persistence Behavior

Runtime state is maintained by the CUDA driver and request objects, while RTC time persists in controller hardware. The header owns no storage.

## Dependencies and Integration Points

It depends on `linux/rtc.h` and UAPI CUDA definitions, and references `struct adb_request`. It integrates with PowerMac/ADB input, platform power control, RTC, and early machine discovery.

## Risks and Edge Cases

Variable-argument request construction must match CUDA command packet formats. Polling and callback completion must avoid races. RTC conversion must handle controller-specific epoch/range behavior. Unsupported machines should fail probe cleanly.

## Test Signals

Signals include CUDA probe on supported PowerMac hardware, ADB request/response tests, callback completion ordering, polling-mode operation, RTC get/set round trips, and unsupported-platform build/probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cuda.h -->
