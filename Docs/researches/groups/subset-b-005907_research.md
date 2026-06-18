# Research: subset-b-005907

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_domain.h -->
# sources/distributed-fs/ceph-client/include/linux/pm_domain.h

Purpose: defines the generic device power-domain interface, including genpd domain topology, domain governors, per-device attachment data, OF provider registration, performance-state control, wakeup timing, and the generic `dev_pm_domain_*()` attach/detach surface used by drivers.

Important APIs and types: `struct generic_pm_domain` is the central state container with embedded `struct dev_pm_domain`, parent/child lists, attached device list, governor data, power callbacks, power-state table, OPP table, performance-state hooks, device attach/detach hooks, hardware-mode hooks, flags, timing counters, and sleep/irq-safe locking variants. `struct generic_pm_domain_data` stores per-device domain timing, notifier, CPU, performance state, OPP token, hardware-mode, runtime-always-on, and private data. `struct genpd_power_state`, `struct dev_power_governor`, `struct gpd_link`, `struct genpd_onecell_data`, and `struct dev_pm_domain_list` define idle states, governor callbacks, subdomain links, OF one-cell providers, and multi-domain attachment results. APIs include `pm_genpd_init()`, `pm_genpd_add_device()`, subdomain add/remove, notifier add/remove, `dev_pm_genpd_set_performance_state()`, `dev_pm_genpd_set_hwmode()`, `dev_pm_genpd_rpm_always_on()`, OF provider helpers, and `dev_pm_domain_attach*()`.

Control flow: a genpd provider initializes `generic_pm_domain`, sets flags and callbacks, registers an OF/simple/onecell provider, and devices attach by DT phandle, ID, name, or generic PM-domain attach calls. Runtime/system PM paths aggregate attached device constraints, child-domain status, wakeup timestamps, and requested performance states before invoking provider `power_on`/`power_off` or device `start`/`stop` hooks. Multi-PD attach can create device links, optionally power domains on at attach, assign required OPP devices, and power off at detach depending on `PD_FLAG_*`.

State and persistence: state is in-memory kernel PM topology: domain status, child-domain counts, attached devices, governor caches, timing residency/accounting, wakeup deadlines, selected idle state, performance state, sync-state/stay-on boot behavior, and per-device runtime metadata. Nothing is persisted across boot, but incorrect state affects runtime power, suspend, and device-link ordering.

Dependencies and integration points: integrates with the driver core, `struct device` PM state, OF/fwnode parsing, OPP/performance-state tables, PM QoS governors, CPU idle, wakeup timing, notifier chains, workqueues, device links, and optional `CONFIG_PM_GENERIC_DOMAINS`, `CONFIG_PM_GENERIC_DOMAINS_OF`, and sleep support. Disabled configs provide no-op or `-EOPNOTSUPP`/`-ENOSYS` stubs, so callers must handle feature absence.

Risks and test signals: risks include mismatched provider flags before `pm_genpd_init()`, sleeping callbacks marked IRQ-safe, unbalanced attach/detach or subdomain links, stale required-OPP mappings, performance-state aggregation bugs, boot `sync_state`/`stay_on` regressions, and config-stub assumptions. Test with OF provider registration, multi-domain attach by name/ID, device-link power ordering, runtime/system suspend with wakeup devices, CPU-domain idle residency, OPP performance-state translation, and compile matrices with genpd/OF/sleep disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_opp.h -->
# sources/distributed-fs/ceph-client/include/linux/pm_opp.h

Purpose: declares the Operating Performance Points framework API used by device, CPU, interconnect, regulator, clock, power-domain, and energy-model code to describe, query, select, and mutate supported performance points.

Important APIs and types: `struct dev_pm_opp_supply`, `struct dev_pm_opp_config`, `struct dev_pm_opp_data`, and `struct dev_pm_opp_key` describe regulator/power data, device-specific configuration, dynamic OPP additions, and key-based lookup. Core APIs get/put OPP tables and OPP references, query bandwidth/voltage/power/frequency/level/required pstate/turbo state, count OPPs, lookup exact/floor/ceil OPPs by frequency, level, key, or bandwidth, add/remove/enable/disable/adjust dynamic OPPs, register notifiers, set/clear configuration, set rates or full OPPs, share CPU tables, sync regulators, and remove tables. OF and cpufreq helpers populate tables from DT and convert OPP tables to cpufreq data.

Control flow: a driver configures clock names, regulators, supported hardware, property suffixes, required devices, or custom clock/regulator callbacks, then loads OPP data from firmware/OF or adds dynamic entries. Runtime scaling code resolves a target frequency, level, or bandwidth to a referenced `dev_pm_opp`, then calls `dev_pm_opp_set_rate()` or `dev_pm_opp_set_opp()` to coordinate clocks, regulators, interconnect/required OPPs, and performance state. The header also provides convenience helpers that create a temporary config struct and return a token later cleared with `dev_pm_opp_clear_config()`.

State and persistence: OPP tables and OPP entries are reference-counted runtime kernel objects owned by the OPP core, with notifier state, configuration tokens, sharing CPU masks, dynamic-entry flags, and OF/firmware-derived metadata. There is no persistent storage here; persistent policy comes from firmware/DT and board data.

Dependencies and integration points: depends on the PM OPP core, device core, clocks, regulators, cpufreq, cpumask, OF, interconnect bandwidth metadata, energy model registration, PM domains via required OPP/performance-state translation, and scoped cleanup helpers (`DEFINE_FREE`). When `CONFIG_PM_OPP`, `CONFIG_OF`, or `CONFIG_CPU_FREQ` is disabled, APIs collapse to explicit stubs, usually `-EOPNOTSUPP`, `-EINVAL`, `0`, or NULL-like values.

Risks and test signals: risks include leaked OPP/table references, ignoring `ERR_PTR` from lookup helpers, stale config tokens, wrong regulator units, scaling-down callback ordering, cpufreq sharing-mask mistakes, required-OPP index mismatches, and disabled-config stubs hiding missing scaling. Test DT and dynamic OPP population, exact/floor/ceil lookups, regulator/clock transitions in both directions, notifier delivery, cpufreq table generation/removal, required OPP translation, EM registration, and compile variants with OPP/OF/cpufreq disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_opp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_qos.h -->
# sources/distributed-fs/ceph-client/include/linux/pm_qos.h

Purpose: defines Power Management QoS constraints for CPU latency, device resume latency, latency tolerance, frequency min/max bounds, and device PM flags.

Important APIs and types: `struct pm_qos_constraints`, `struct pm_qos_request`, `struct pm_qos_flags`, and `struct pm_qos_flags_request` implement plist-backed scalar constraints and list-backed flag aggregation. `struct freq_constraints` and `struct freq_qos_request` wrap min/max frequency constraints. `struct dev_pm_qos_request` and `struct dev_pm_qos` bind QoS requests, notifiers, resume latency, latency tolerance, frequency, and flags to a device. APIs include `pm_qos_update_target()`, `pm_qos_update_flags()`, CPU latency request helpers, `dev_pm_qos_add/update/remove_request()`, notifier registration, sysfs exposure helpers, user latency tolerance updates, raw/requested read helpers, and frequency QoS add/update/remove/apply/notifier calls.

Control flow: request owners allocate request objects, add them to a constraint set, update values as requirements change, and remove them on teardown. Scalar constraints compute either min or max target values from plist priority, while flags aggregate status against a mask. Device PM and frequency clients use notifiers to react to changed effective values, and runtime PM/genpd can use resume-latency and no-power-off flags to block deeper idle states.

State and persistence: QoS state is live kernel state attached to global CPU latency containers, `freq_constraints`, or `dev->power.qos`; it includes active plist nodes, flag list nodes, cached 32-bit target/effective values, default/no-constraint values, request ownership, and notifier heads. It is not persistent and must be explicitly cleaned up by request owners.

Dependencies and integration points: depends on plist ordering, blocking notifiers, device power state, CPU idle, PM core, and frequency scaling paths. The header documents that lockless readers rely on atomic 32-bit access to `target_value` and `effective_flags`. Disabled PM/CPU-idle configs provide default/no-op semantics.

Risks and test signals: risks include uninitialized request objects, double add/remove, leaking request nodes across driver detach, wrong min-vs-max constraint type, notifier recursion, assuming 64-bit lockless values are safe, and relying on PM QoS when config stubs return defaults. Test add/update/remove ordering, notifier firing only on effective changes, frequency min/max clamping, device resume-latency sysfs exposure, no-power-off flags, CPU idle latency limits, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_runtime.h -->
# sources/distributed-fs/ceph-client/include/linux/pm_runtime.h

Purpose: provides the inline runtime PM API used by drivers to manage per-device active/suspended state, usage counts, autosuspend, PM workqueue dispatch, supplier links, and system-sleep handoff.

Important APIs and types: flag bits `RPM_ASYNC`, `RPM_NOWAIT`, `RPM_GET_PUT`, `RPM_AUTO`, and `RPM_TRANSPARENT` parameterize core `__pm_runtime_idle/suspend/resume()`. Public helpers include synchronous and asynchronous idle/suspend/resume calls, `pm_runtime_get*()` and `pm_runtime_put*()` usage-count wrappers, autosuspend helpers, status setters, enable/disable/block/unblock, no-callback/irq-safe markers, autosuspend-delay control, memalloc-noio, supplier get/put, link lifecycle hooks, device-managed enable/get helpers, and scoped guards such as `PM_RUNTIME_ACQUIRE()`.

Control flow: drivers enable runtime PM, initialize status while disabled, increment usage before accessing hardware, resume the device if needed, mark last busy, then drop usage using idle/autosuspend/suspend variants. The inline wrappers translate common patterns into core calls with the right flags; some variants intentionally leave usage counts incremented on errors while `pm_runtime_resume_and_get()` unwinds failures. Force suspend/resume bridges runtime PM callbacks into system sleep via `DEFINE_RUNTIME_DEV_PM_OPS()`.

State and persistence: state lives in `dev->power`: runtime status, usage count, disable depth, child dependencies, autosuspend delay/last busy, irq-safe/no-callback flags, supplier links, and blocked status. No persistent data is stored, but incorrect counters or status can permanently pin devices on/off until reprobe.

Dependencies and integration points: integrates with the device core, PM workqueue `pm_wq`, system sleep callbacks, devres, device links/suppliers, PM domains, PM QoS resume constraints, jiffies/ktime, and cleanup guard macros. With `CONFIG_PM` disabled, most operations are no-ops or return fixed values; with sleep disabled, force-resume returns `-ENXIO`.

Risks and test signals: risks include unbalanced get/put, using `pm_runtime_get_sync()` without unwinding errors, changing status while PM is enabled, autosuspend not disabled on manual teardown, IRQ-safe callbacks that sleep, supplier link ordering bugs, and guard misuse without checking `PM_RUNTIME_ACQUIRE_ERR()`. Test runtime suspend/resume callback paths, error unwinding, autosuspend expiration, system sleep force suspend/resume, devm cleanup, supplier dependency behavior, IRQ-safe devices, and builds with PM disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_runtime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_wakeirq.h -->
# sources/distributed-fs/ceph-client/include/linux/pm_wakeirq.h

Purpose: declares helpers for associating a device with a wake IRQ used by PM wakeup handling.

Important APIs and types: APIs include `dev_pm_set_wake_irq()`, dedicated wake IRQ variants including reverse ordering, `dev_pm_clear_wake_irq()`, and devres-managed `devm_pm_set_wake_irq()`. The actual `struct wake_irq` is opaque and maintained by the PM core.

Control flow: a driver discovers its normal or dedicated wake interrupt, registers it with the device PM core, then clears it on removal or relies on devm cleanup. During suspend/resume, PM core can enable the IRQ for wakeup and coordinate ordering relative to runtime/system PM callbacks.

State and persistence: wake IRQ association is runtime device PM state tied to `struct device`; no persistent data is defined here.

Dependencies and integration points: integrates with `struct device`, IRQ wakeup configuration, PM sleep/runtime flows, and wakeup-source state. With `CONFIG_PM` disabled, all helpers are successful no-ops.

Risks and test signals: risks include wrong IRQ lifetime, registering a shared functional IRQ as a dedicated wake IRQ, clear/register imbalance, and relying on wake IRQ behavior in PM-disabled builds. Test suspend wake from the device, probe/remove cleanup, runtime suspend with wake IRQs, IRQ wake enable failure handling, and PM-disabled compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_wakeirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_wakeup.h -->
# sources/distributed-fs/ceph-client/include/linux/pm_wakeup.h

Purpose: defines the device wakeup-source interface used to mark devices as wake-capable, enable or disable system wakeup, account wake events, and prevent autosleep while events are active.

Important APIs and types: `struct wakeup_source` records name/id, list linkage, spinlock, optional `wake_irq`, timer, active/prevent-sleep timing, event/active/relax/expire/wakeup counters, sysfs device, active flag, and autosleep flag. Helpers expose `device_can_wakeup()`, `device_may_wakeup()`, wakeup-path and out-of-band flags, wakeup source register/unregister/walk, `device_wakeup_enable/disable()`, `device_set_wakeup_capable()`, `__pm_stay_awake()`, `pm_stay_awake()`, `__pm_relax()`, and wakeup event helpers including hard events and `devm_device_init_wakeup()`.

Control flow: drivers mark wake-capable devices, optionally enable wakeup by default, call stay-awake or wakeup-event helpers when hardware reports activity, and relax once work is drained. The PM core uses the wakeup-source active state and wakeup path flags to abort or shape suspend/autosleep transitions. `device_init_wakeup()` combines capability and enable state; the devm wrapper installs a cleanup action.

State and persistence: runtime state is held in `dev->power` and `struct wakeup_source`: wake enablement, path markers, event counters, timers, and aggregate active/prevent-sleep time. No persistent storage is used.

Dependencies and integration points: included via `device.h`, and integrates with PM sleep, wake IRQs, timers, spinlocks, wakeup-source sysfs statistics, autosleep, and device-managed actions. Without `CONFIG_PM_SLEEP`, wakeup-source allocation and event accounting are no-ops, but basic capability/should-wakeup booleans remain available.

Risks and test signals: risks include not relaxing active wakeup sources, enabling wakeup for devices that cannot signal wake, racing event timers with suspend entry, missing hard wakeup events, and code assuming wakeup-source statistics exist in no-sleep builds. Test wakeup enable/disable sysfs, autosleep aborts, timed events, hard wake events, devm cleanup, wake IRQ association, and disabled sleep configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_wakeup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pmbus.h -->
# sources/distributed-fs/ceph-client/include/linux/pmbus.h

Purpose: provides board/platform data and quirk flags for PMBus hardware-monitoring and regulator support.

Important APIs and types: `struct pmbus_platform_data` carries device-specific `flags`, `num_regulators`, and regulator init data. Flags include skip status checks, write-protected devices, missing CAPABILITY or WRITE_PROTECT registers, controller reset via status read after failed checks, coefficient-command direct-mode setup, and OPERATION/VOUT protection quirks.

Control flow: board or device registration passes platform data to the PMBus core; the PMBus driver interprets flags during register detection, write-protection checks, direct-mode coefficient setup, and regulator registration.

State and persistence: no runtime state is stored here beyond platform data supplied at probe. Persistent behavior comes from board wiring and chip quirks.

Dependencies and integration points: depends on `linux/bits.h` and regulator init data declarations used by PMBus hwmon/regulator drivers.

Risks and test signals: risks include wrong quirk flags causing false register detection, unsafe writes to protected chips, missing regulator init data, and direct-mode coefficient errors. Test probe on affected PMBus chips, register-detection failures, write-protection behavior, regulator registration, and hwmon readings under quirk combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pmbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/pmu.h

Purpose: declares the PowerMac PMU interface for ADB-request based communication with the microcontroller handling battery charging, RTC, backlight, restart/shutdown, and power status on older PowerBook systems.

Important APIs and types: functions include PMU discovery, request submission/queueing/poll/wait, suspend/resume, IR LED, RTC get/set, restart/shutdown/unlock, presence/model queries, and backlight sleep/init controls. `struct pmu_battery_info` exports battery flags, charge/max charge, amperage, voltage, and time remaining. Globals expose battery count, battery info array, power flags, and suspend state.

Control flow: platform code discovers the PMU, drivers enqueue ADB requests and wait or poll for completion, power-management code brackets long interrupt-disabled regions with `pmu_suspend()`/`pmu_resume()`, and battery/RTC/backlight users query exported state or invoke helper commands.

State and persistence: state is global PMU driver runtime state: queued requests, battery snapshots, AC-present flags, model/presence data, RTC values, and suspend flag. The RTC itself persists in hardware; the header only declares accessors.

Dependencies and integration points: integrates with ADB request handling, PowerPC platform PM, RTC core, backlight code, xmon polling, battery status, and UAPI PMU commands. Suspend/resume stubs are empty without `CONFIG_ADB_PMU`.

Risks and test signals: risks include request lifetime while asynchronous completion is pending, non-stackable suspend calls, stale global battery snapshots, architecture/config misuse, and RTC conversion errors. Test PMU discovery on supported hardware, request completion ordering, suspend/resume, RTC set/get, shutdown/restart commands, backlight behavior, and non-PMU build compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pnp.h -->
# sources/distributed-fs/ceph-client/include/linux/pnp.h

Purpose: defines the Linux Plug and Play bus interface for PNP devices, cards, protocols, resource accessors, driver registration, and protocol-specific ACPI/ISA/BIOS integration.

Important APIs and types: `struct pnp_dev`, `struct pnp_card`, `struct pnp_driver`, `struct pnp_card_driver`, `struct pnp_protocol`, `struct pnp_card_link`, `struct pnp_id`, and `struct pnp_fixup` model devices, multi-function cards, protocol backends, and quirks. Inline helpers expose IO/MEM/IRQ/DMA resource start/end/flags/valid/len, driver data, name and list traversal macros, capability tests, protocol identity checks, and ACPI device extraction. APIs register/unregister drivers and card drivers, attach/detach devices, request/release card devices, auto-configure/start/stop/activate/disable devices, check active/reserved ranges, compare IDs, and identify PNP devices.

Control flow: protocol backends enumerate devices/cards, fill resources/options and IDs, and register with the PNP core. Drivers match against PNP IDs, probe, request resources or card functions, and use activation/configuration helpers unless flags ask not to change resource state. Suspend/resume flows go through driver and protocol callbacks with console-device safeguards.

State and persistence: state is in-memory bus state: global and per-protocol device/card lists, resources/options, active/status/capability flags, card links, proc entries, driver data, and protocol data such as ACPI handles. PNP resources may reflect firmware/hardware configuration but are not persisted by this header.

Dependencies and integration points: integrates with the driver model, `struct resource`, ACPI PNP, ISA PNP, PNPBIOS, console suspend policy, procfs entries, resource reservation, and module driver registration. With `CONFIG_PNP` disabled, registration/configuration helpers return `-ENODEV` or inert defaults, while resource reads return absent values.

Risks and test signals: risks include resource helpers returning sentinel `0` or `-1`, changing resources for console or non-configurable devices, protocol callback NULL checks, card-device lifetime, stale proc entries, and config-disabled callers not handling `-ENODEV`. Test PNPACPI enumeration, resource access for each type, driver probe/remove, card multi-device request/release, suspend/resume with console devices, auto-configuration, and disabled-PNP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pnp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/poison.h -->
# sources/distributed-fs/ceph-client/include/linux/poison.h

Purpose: centralizes debug poison pointer and byte constants used by lists, timers, memory allocators, slab, journals, DMA pools, networking, BPF, VFS, stack depot, io_uring, and security code.

Important APIs and types: defines `POISON_POINTER_DELTA`, pointer sentinels such as `LIST_POISON1/2`, `TIMER_ENTRY_STATIC`, `TAIL_MAPPING`, `MUTEX_POISON_WW_CTX`, `SKB_LIST_POISON_NEXT`, `NET_PTR_POISON`, `BPF_PTR_POISON`, `VFS_PTR_POISON`, `STACK_DEPOT_POISON`, and `IO_URING_PTR_POISON`, plus byte patterns such as `PAGE_POISON`, `SLUB_RED_*`, `POISON_INUSE`, `POISON_FREE`, `POISON_END`, and subsystem-specific free markers.

Control flow: subsystems assign these constants to freed, inactive, or invalidated pointers/memory so accidental reuse faults early or is recognizable in memory dumps. Architectures may offset poison pointers with `CONFIG_ILLEGAL_POINTER_VALUE`.

State and persistence: no state is held; constants influence debug/runtime memory contents.

Dependencies and integration points: used by list manipulation, timer setup, page/slab allocators, journal code, DMA pool, networking, mutex debugging, key destruction, BPF, VFS, stack depot, and io_uring.

Risks and test signals: risks include choosing poison values that become valid mapped addresses, collisions with subsystem bit packing such as page-pool signatures, and tests relying on exact poison values across architectures. Test list/slab/page poisoning, KASAN/KFENCE-style diagnostics, freed object detection, and architecture illegal-pointer offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/poison.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/poll.h -->
# sources/distributed-fs/ceph-client/include/linux/poll.h

Purpose: defines kernel poll/select support structures and helpers used by file `->poll()` implementations and the core select/poll syscalls.

Important APIs and types: `poll_table`, `poll_queue_proc`, `struct poll_table_entry`, and `struct poll_wqueues` describe wait registration and syscall-side wait queues. Helpers include `poll_wait()`, `poll_requested_events()`, `init_poll_funcptr()`, `file_can_poll()`, `vfs_poll()`, `poll_initwait()`, `poll_freewait()`, `select_estimate_accuracy()`, `core_sys_select()`, `poll_select_set_timeout()`, and `mangle_poll()`/`demangle_poll()` for POLL/EPOLL bit translation.

Control flow: a syscall initializes `poll_wqueues`, calls each file's `->poll()` via `vfs_poll()`, and file implementations call `poll_wait()` to register wait queues before returning readiness masks. `poll_wait()` invokes the queue proc and issues a memory barrier paired with waitqueue sleeper checks so readiness checks are ordered after queue insertion.

State and persistence: syscall wait state is stack/temporary memory in `poll_wqueues`, including inline entries sized by stack-budget macros and optional page-backed table entries. No persistent state is stored here.

Dependencies and integration points: integrates with VFS file operations, wait queues, user fd sets, uaccess, ktime/timeouts, UAPI poll and eventpoll masks, and select/poll syscall implementations.

Risks and test signals: risks include missing `poll_wait()` before readiness tests, incorrect readiness mask conversion, stack budget regressions, `file->f_op->poll` NULL handling, and memory-ordering races with wakeups. Test driver poll implementations, epoll/select/poll equivalence, timeout conversion, wake-after-register races, and files without poll support returning default masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/polynomial.h -->
# sources/distributed-fs/ceph-client/include/linux/polynomial.h

Purpose: declares a small polynomial evaluator interface for drivers that model hardware calibration or conversion curves.

Important APIs and types: `struct polynomial_term` stores degree, coefficient, per-degree divider, and leftover divider. `struct polynomial` stores a total divider and flexible array of terms, with the last term required to have degree 0. `polynomial_calc()` evaluates the polynomial for an input value.

Control flow: callers define a static term array ordered for evaluation, terminate it with degree 0, and pass input data to `polynomial_calc()` to receive a scaled integer result.

State and persistence: no mutable state is held; descriptors are caller-owned and may be static platform/calibration data.

Dependencies and integration points: standalone Linux header using integer types; intended for sensor, power, or platform drivers needing integer polynomial conversion without floating point.

Risks and test signals: risks include missing degree-0 terminator, overflow from high-degree/coefficient combinations, incorrect divider distribution, and sign/rounding surprises. Test known calibration vectors, boundary values, negative coefficients, divider leftovers, and static descriptor termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/polynomial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix-clock.h -->
# sources/distributed-fs/ceph-client/include/linux/posix-clock.h

Purpose: declares the dynamic POSIX clock character-device framework used by PTP and similar clock drivers.

Important APIs and types: `struct posix_clock_operations` exposes clock methods (`clock_adjtime`, `clock_gettime`, `clock_getres`, `clock_settime`) and optional character-device file operations (`open`, `release`, `ioctl`, `read`, `poll`). `struct posix_clock` embeds ops, `cdev`, backing device, rwsem, and zombie flag. `struct posix_clock_context` passes per-open context, file pointer, and driver private file data. APIs register and unregister dynamic clocks.

Control flow: a driver embeds and initializes `struct posix_clock`, provides an initialized device with release method, and calls `posix_clock_register()`. The clock device layer owns initial file-operation dispatch, checks zombie/lifetime state, then forwards clock and optional character operations to driver callbacks. Unregister marks the clock inactive while outstanding references drain.

State and persistence: runtime state includes the cdev/device lifetime, zombie flag under rwsem, and per-open context private data. Hardware clock time persists only if the device provides it; this header stores no persistent time.

Dependencies and integration points: integrates with cdev, device model lifetime, VFS file operations, poll, POSIX timer clock IDs, rwsems, modules, and dynamic clock consumers such as PTP.

Risks and test signals: risks include missing device release callback, freeing embedded private structures before open references close, failing to handle zombie state in callbacks, and access-mode mistakes in ioctl/read. Test register/unregister with open fds, adjtime/gettime/settime/res callbacks, poll/read/ioctl paths, module refcounting, and device removal races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix-timers.h -->
# sources/distributed-fs/ceph-client/include/linux/posix-timers.h

Purpose: defines kernel POSIX timer and CPU-timer internals, clockid encoding helpers, timer reference management, and CPU timer lifecycle hooks.

Important APIs and types: clock helpers create process/thread CPU clock IDs and convert file descriptors to dynamic clock IDs. `struct cpu_timer` wraps timerqueue node/head, PID, expiry list, firing/nanosleep flags, and handling task. `struct k_itimer` is the main POSIX timer object with hash/list nodes, timer id, clock id, signal target, clock operations pointer, spinlock, status, overrun accounting, signal sequence fields, interval, pid/process pointer, embedded sigqueue, rcuref, and real/cpu/alarm timer union. APIs initialize CPU timer containers, enqueue/dequeue CPU timers, rearm itimers, initialize/send/deliver sigqueue, free timers, handle prctl controls, run/exit CPU timers, set CPU timers, and update CPU rlimits.

Control flow: timer creation allocates `k_itimer`, initializes signal queue and clock-specific storage, inserts it into process timer state, and arms hrtimer/cpu timer/alarm timer backends. Expiry queues signals, manages overrun counters and sequence numbers, and uses rcuref to keep timer memory alive while sigqueue delivery is in flight. CPU timers are queued in per-task or per-signal `posix_cputimers` timerqueues and processed from scheduler/task-work hooks.

State and persistence: state is runtime per-task/per-signal timer state: timerqueues, next-event caches, active/expiry flags, timer hash/list membership, signal ownership, references, overruns, and backend timer objects. POSIX timers are process lifetime objects and do not persist across exec/exit beyond normal kernel semantics.

Dependencies and integration points: integrates with hrtimers, alarmtimers, timerqueue, signals, PIDs, task_struct/signal_struct, RCU, rcuref, spinlocks, CPU accounting, rlimits, task work, and dynamic POSIX clocks. Disabled `CONFIG_POSIX_TIMERS` and task-work configs provide empty stubs.

Risks and test signals: risks include reference leaks or premature frees during signal delivery, CPU timer dequeue/enqueue races, overrun sequence mistakes, invalid encoded clock IDs, task exit cleanup bugs, and nanosleep vs regular timer confusion. Test timer_create/delete, periodic overrun accounting, process and thread CPU timers, rlimit CPU timer updates, signal delivery under deletion races, clockfd timers, nanosleep timers, and POSIX_TIMERS-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix-timers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix-timers_types.h -->
# sources/distributed-fs/ceph-client/include/linux/posix-timers_types.h

Purpose: provides lightweight POSIX CPU timer type definitions and clockid bitfield macros for use in task and signal structures.

Important APIs and types: macros decode CPU clock IDs into PID, per-thread bit, and clock type (`CPUCLOCK_PROF`, `CPUCLOCK_VIRT`, `CPUCLOCK_SCHED`, `CLOCKFD`). `struct posix_cputimer_base` stores next event and timerqueue head per CPU clock type. `struct posix_cputimers` groups the three bases plus active/expiry flags. `struct posix_cputimers_work` stores task-work callback, mutex, and scheduled flag for task-work based expiry.

Control flow: scheduler and POSIX timer code use the bitfield macros to classify clock IDs and use `posix_cputimers` containers embedded in task/signal state to queue and locate CPU timers efficiently.

State and persistence: runtime per-task/per-signal CPU timer state only. With `CONFIG_POSIX_TIMERS` disabled, `struct posix_cputimers` is empty.

Dependencies and integration points: depends on mutex and timerqueue type headers, and is included by task/signal/timer code that must avoid the heavier POSIX timer implementation header.

Risks and test signals: risks include clockid encoding drift, next-event cache not initialized to `U64_MAX`, active/expiry flag races, and code assuming non-empty structs in disabled builds. Test CPU timer clockid encoding/decoding, task and process timer initialization, task-work expiry scheduling, and disabled POSIX timer builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix-timers_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix_acl.h -->
# sources/distributed-fs/ceph-client/include/linux/posix_acl.h

Purpose: declares in-kernel POSIX ACL representation, reference management, VFS ACL operations, inode ACL cache helpers, and filesystem helper callbacks.

Important APIs and types: `struct posix_acl_entry` stores tag, permission bits, and UID/GID union. `struct posix_acl` stores refcount, entry count, RCU head, and counted flexible entries. Helpers include `FOREACH_ACL_ENTRY`, `posix_acl_dup()`, `posix_acl_release()`, allocation/init/clone/from-mode/equiv-mode/create/chmod/update helpers, `get_posix_acl()`, `set_posix_acl()`, cached ACL get/set/forget helpers, validation, permission checking, `simple_set_acl`, `simple_acl_create`, VFS get/set/remove/listxattr APIs, and `get_inode_acl()`.

Control flow: filesystem and VFS code allocate or fetch ACLs, refcount them when sharing, validate entries against user namespaces, use create/chmod helpers to adjust inode modes and default/access ACLs, cache ACLs in inode fields, and release references through RCU-safe freeing. VFS xattr operations route POSIX ACL names to filesystem `get_acl`/`set_acl` equivalents.

State and persistence: ACL objects are reference-counted in-memory structures; persistent ACL data lives in filesystem xattrs or on-disk metadata. Inode ACL caches hold runtime references and must be invalidated on changes.

Dependencies and integration points: integrates with VFS inodes/dentries, mount idmaps, user namespaces, xattrs, RCU, refcounts, slab allocation, and UAPI POSIX ACL tags. With `CONFIG_FS_POSIX_ACL` disabled, ACL creation returns no ACLs and VFS ACL operations return `-EOPNOTSUPP` or no-op.

Risks and test signals: risks include refcount leaks, use-after-free without `posix_acl_dup()`, stale inode ACL cache after xattr updates, mode/ACL equivalence mistakes, idmapped mount translation errors, invalid entry ordering, and disabled-config assumptions. Test ACL create/chmod, permission checks, xattr get/set/remove/list, cache invalidation, idmapped mounts, RCU cached lookups, and no-POSIX-ACL builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix_acl_xattr.h -->
# sources/distributed-fs/ceph-client/include/linux/posix_acl_xattr.h

Purpose: declares conversion helpers between in-kernel POSIX ACLs and extended-attribute wire format.

Important APIs and types: `posix_acl_xattr_size()` calculates serialized size for a count, `posix_acl_xattr_count()` validates and decodes entry count from a byte size, `posix_acl_from_xattr()` parses xattr data, `posix_acl_to_xattr()` serializes ACLs, `posix_acl_xattr_name()` maps ACL type to xattr name, `posix_acl_type()` maps xattr name to ACL type, and legacy no-op xattr handlers are declared.

Control flow: VFS/filesystem xattr paths receive an ACL xattr buffer, validate its size/count, parse it into a `struct posix_acl`, validate/use it, and serialize kernel ACLs back to user-visible xattr format for reads.

State and persistence: no state is stored here. The xattr byte representation is the persistent filesystem/user ABI; kernel ACL objects are temporary or cached elsewhere.

Dependencies and integration points: integrates UAPI xattr and POSIX ACL xattr layouts with `linux/posix_acl.h`, user namespace ID translation, and filesystem xattr handlers. Parsing returns `-EOPNOTSUPP` when POSIX ACL support is disabled.

Risks and test signals: risks include accepting malformed sizes, wrong ACL type/name mapping, UID/GID namespace conversion mistakes, buffer sizing errors, and use of legacy no-op handlers in new code. Test xattr round trips, malformed xattr lengths, access/default name mapping, idmapped mount ACL serialization, and disabled ACL builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/posix_acl_xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq2415x_charger.h -->
# sources/distributed-fs/ceph-client/include/linux/power/bq2415x_charger.h

Purpose: defines platform data and charger mode constants for TI bq2415x charger devices.

Important APIs and types: `enum bq2415x_mode` identifies off, unknown/100mA, USB host/hub, dedicated charger, and boost modes. `struct bq2415x_platform_data` supplies current limit, weak-battery voltage, regulation voltage, charge current, termination current, sense resistor value, and optional notify power-supply device name.

Control flow: board data passes defaults to the charger driver at probe. The driver uses `-1` fields to keep datasheet defaults, uses `resistor_sense` to decide whether charge/termination current programming is possible, and can use `notify_device` for automode current-limit updates through power-supply notifications.

State and persistence: only static board configuration is defined here; runtime charger state is in the driver/chip.

Dependencies and integration points: integrates with the power-supply class, sysfs-configurable charger properties, board files, and charger-detection/automode logic.

Risks and test signals: risks include wrong current/voltage units, missing or invalid sense resistor disabling current programming, stale notify device name, and unsafe default charger mode. Test probe with default and explicit platform values, current-limit changes, boost mode, automode notifications, and sysfs property updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq2415x_charger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq24190_charger.h -->
# sources/distributed-fs/ceph-client/include/linux/power/bq24190_charger.h

Purpose: provides platform data for the TI bq24190 charger driver.

Important APIs and types: `struct bq24190_platform_data` carries a pointer to regulator init data used when the charger exposes or consumes regulator functionality.

Control flow: platform registration supplies the regulator constraints during probe; the charger driver forwards them to regulator registration/configuration.

State and persistence: no runtime state is held; the struct is static probe-time configuration.

Dependencies and integration points: depends on `linux/regulator/machine.h` and integrates the bq24190 charger driver with regulator core policy.

Risks and test signals: risks include NULL or mismatched regulator constraints, lifetime of platform data, and board files diverging from DT/ACPI properties. Test charger probe with regulator init data, regulator enable/current constraints, and builds without board-data users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq24190_charger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq24735-charger.h -->
# sources/distributed-fs/ceph-client/include/linux/power/bq24735-charger.h

Purpose: defines board/platform configuration for the TI bq24735 charger driver.

Important APIs and types: `struct bq24735_platform` supplies charge current, charge voltage, input current, power-supply name, external-control flag, and supplied-to battery names/count.

Control flow: the charger driver reads this data at probe to configure initial charge/input limits, name the power-supply instance, decide whether hardware is externally controlled, and publish supplicant relationships.

State and persistence: no live state is held by the header; values are static board defaults.

Dependencies and integration points: integrates with `power_supply` naming/supplicant relationships and charger hardware programming.

Risks and test signals: risks include current/voltage unit mismatches, misdeclared external control causing unexpected charging, and invalid supplied-to arrays. Test probe, power_supply registration, limit programming, external-control mode, and charger-to-battery supply links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq24735-charger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq25890_charger.h -->
# sources/distributed-fs/ceph-client/include/linux/power/bq25890_charger.h

Purpose: provides minimal platform data for the TI bq25890 charger driver.

Important APIs and types: `struct bq25890_platform_data` contains regulator init data for charger regulator integration.

Control flow: board data passes regulator constraints at probe; the driver uses them when registering or configuring charger-related regulators.

State and persistence: static probe-time platform data only.

Dependencies and integration points: forward-declares `struct regulator_init_data` and integrates bq25890 charger support with regulator core policy.

Risks and test signals: risks include wrong regulator constraints, missing platform data on non-DT systems, and lifetime assumptions. Test probe with regulator configuration, regulator constraints, charger enable/disable, and compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq25890_charger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq27xxx_battery.h -->
# sources/distributed-fs/ceph-client/include/linux/power/bq27xxx_battery.h

Purpose: declares the shared bq27xxx fuel-gauge core interface and device data used by bus-specific drivers.

Important APIs and types: `enum bq27xxx_chip` enumerates supported TI gauge variants. `struct bq27xxx_access_methods` defines bus callbacks for byte/word and bulk reads/writes. `struct bq27xxx_reg_cache` caches capacity and flags. `struct bq27xxx_device_info` stores device pointer, chip type, options, name, data-memory registers, unseal key, bus methods, cache, design charge/voltage limits, removed flag, update timestamp, last status, delayed work, registered battery power_supply, global list node, mutex, and register map pointer. APIs update, setup, teardown the battery and expose PM ops.

Control flow: an I2C/HDQ/platform bus driver fills `bq27xxx_device_info` with chip identity and access callbacks, calls setup to register the power_supply and delayed polling, then update reads gauge registers into cache/status. Teardown marks removal, cancels work, and unregisters state.

State and persistence: runtime gauge state includes cached properties, delayed update work, removal flag, power_supply handle, lock, and bus callbacks. Gauge calibration/state may persist in chip data flash, but this header only describes kernel access.

Dependencies and integration points: integrates with the power_supply class, delayed work, bus-specific read/write implementations, chip data-memory definitions, mutex/list management, and PM suspend/resume hooks.

Risks and test signals: risks include bus callback failures, stale cache after removal, delayed work racing teardown, wrong chip register map, unseal-key misuse, and power_supply property unit mistakes. Test setup/teardown, periodic update, suspend/resume, all bus access paths, removal during work, chip variant register selection, and power_supply property reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/bq27xxx_battery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/charger-manager.h -->
# sources/distributed-fs/ceph-client/include/linux/power/charger-manager.h

Purpose: defines the charger-manager framework data model for coordinating multiple charger regulators, cable/extcon events, fuel-gauge status, thermal limits, and suspend-aware charging policy behind one power_supply.

Important APIs and types: enums classify battery-present data source, polling mode, and battery temperature state. `struct charger_cable` binds extcon connector data, work item, notifier, attached state, current limits, parent regulator, and manager. `struct charger_regulator` stores regulator name/consumer, external-control flag, cable array, sysfs attributes, and manager pointer. `struct charger_desc` describes full-battery thresholds, polling, battery-present source, charger status supplies, charger regulators, fuel gauge, thermal zone, temperature limits/hysteresis, measurement source, and max charging/discharging durations. `struct charger_manager` stores runtime list/device/desc, thermal zone, charger state, emergency stop, power_supply desc/instance, charge timing, and battery status.

Control flow: platform code describes chargers, extcon cables, fuel gauge, thermal zone, and thresholds. The charger manager registers a synthetic power_supply, listens for extcon changes, adjusts charger regulators and current limits from cable state, polls or reacts to charger/fuel-gauge changes, stops charging on thermal/emergency/full/duration constraints, and can monitor while suspended using alarms.

State and persistence: runtime state includes attached cable booleans, regulator consumers, sysfs attributes, charger-enabled/emergency-stop flags, timing counters, battery status, work items, notifiers, and power_supply handles. Policy is static platform data; no persistence is stored here.

Dependencies and integration points: integrates with power_supply, extcon, regulator core, alarmtimer, thermal framework, sysfs, workqueues, charger/fuel-gauge supplies, and suspend-to-RAM monitoring.

Risks and test signals: risks include extcon notifier lifetime, regulator current-limit mismatch per cable, hysteresis errors around thermal thresholds, full-battery restart logic, charging duration overflow, externally controlled chargers left disabled/enabled unexpectedly, and missing fuel-gauge/charger supplies. Test cable attach/detach, multi-charger regulator enable/disable, thermal stop/restart, full-charge voltage/SOC/capacity thresholds, suspend alarm monitoring, emergency stop, and sysfs state toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/charger-manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/gpio-charger.h -->
# sources/distributed-fs/ceph-client/include/linux/power/gpio-charger.h

Purpose: defines platform data for simple GPIO-detected charger power_supply devices.

Important APIs and types: `struct gpio_charger_platform_data` supplies power_supply name, charger type, supplied-to battery list, and supplicant count.

Control flow: the gpio-charger driver reads platform data at probe, creates a power_supply with the supplied name/type, and uses GPIO state to report charger presence/online state while linking to supplied batteries.

State and persistence: static platform metadata only; live GPIO and power_supply state are owned by the driver.

Dependencies and integration points: integrates with power_supply type and supplicant arrays plus board GPIO wiring.

Risks and test signals: risks include wrong charger type, invalid supplied-to arrays, and GPIO polarity handled outside this struct. Test probe, online property transitions, supplicant links, and name/type exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/gpio-charger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/jz4740-battery.h -->
# sources/distributed-fs/ceph-client/include/linux/power/jz4740-battery.h

Purpose: defines platform data for JZ4740 battery monitoring.

Important APIs and types: `struct jz_battery_platform_data` embeds generic `power_supply_info`, a charger-state GPIO, and active-low flag.

Control flow: the driver consumes static battery design metadata and reads the charger GPIO with configured polarity to expose charging status through power_supply.

State and persistence: no mutable state in the header; static board data describes battery and GPIO wiring.

Dependencies and integration points: integrates with generic power_supply_info, platform GPIOs, and the JZ4740 battery driver.

Risks and test signals: risks include wrong GPIO polarity, inaccurate design capacity/voltage metadata, and missing platform data. Test charger GPIO transitions, reported battery design properties, and charging status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/jz4740-battery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/max17042_battery.h -->
# sources/distributed-fs/ceph-client/include/linux/power/max17042_battery.h

Purpose: defines register maps, constants, characterization/configuration structures, chip types, and platform data for Maxim MAX17042/MAX17047/MAX17050/MAX17055/MAX77759 fuel-gauge drivers.

Important APIs and types: enums list common MAX17042 registers, MAX17055-specific registers, MAX17047-family registers, MAX77759 registers, and chip types. `struct max17042_reg_data` describes initialization register writes. `struct max17042_config_data` is a packed block of sense-resistor value, ADC calibration, alert/status thresholds, app data, model-gauge configuration, save/restore registers, cell technology, voltage/temperature compensation, and a 48-word characterization table. `struct max17042_platform_data` supplies init/config arrays, POR/current-sense booleans, sense resistor, voltage min/max, and temperature min/max defaults.

Control flow: probe code identifies chip type, loads platform or firmware defaults, optionally performs POR initialization, writes init/config registers, programs model/characterization data, and uses register enums for power_supply property reads and alerts.

State and persistence: static platform/config data is defined here; live gauge state is in the driver and chip registers. Some gauge learned/model data may persist in hardware, and save/restore fields help preserve model-gauge state across resets.

Dependencies and integration points: integrates with power_supply technology constants, I2C/regmap-style register access in the driver, Maxim MFD subdevices, alert IRQ handling, and board/firmware battery characterization data.

Risks and test signals: risks include packed config layout drift, wrong register enum for chip variant, unsafe POR initialization overwriting learned data, sense resistor unit mismatch, invalid characterization tables, and temperature/voltage threshold mistakes. Test chip identification, register reads per variant, POR vs non-POR initialization, model table programming, current-sense scaling, alert thresholds, suspend/resume, and power_supply property accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/max17042_battery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/max77705_charger.h -->
# sources/distributed-fs/ceph-client/include/linux/power/max77705_charger.h

Purpose: defines MAX77705 charger register bit fields, regmap field descriptors, current constants, and driver runtime data.

Important APIs and types: macros name interrupt/status bits, detail masks/shifts, configuration fields for charger/OTG/buck/boost/watchdog/protection/timing/current/voltage, AICL delay, and current step/min/max values. `enum max77705_field_idx` indexes regmap fields. `max77705_reg_field[]` maps field indices to charger configuration registers and bit ranges. `struct max77705_charger_data` stores device, regmap, regmap fields, parsed battery info, workqueue, charger input work, and charger power_supply.

Control flow: the charger driver allocates regmap fields from the static descriptors, uses field indices to unlock protection and program mode, charge current, input current, CV voltage, OTG current, watchdog, restart, and skip settings, schedules CHGIN/AICL work, and exposes a power_supply instance backed by `max77705_charger_data`.

State and persistence: runtime state includes regmap field handles, battery info pointer, workqueue/work item, and power_supply handle. Hardware register settings persist only according to chip power/reset behavior.

Dependencies and integration points: depends on regmap/regmap_field, MAX77705 charger register definitions from the broader MFD/regmap layer, power_supply battery info, workqueues, and charger IRQ/status handling.

Risks and test signals: risks include static `reg_field` definitions drifting from register map, off-by-one current scaling, failure to unlock protected fields, mode bit conflicts between OTG/UNO/boost, watchdog clearing mistakes, and workqueue teardown races. Test regmap field allocation, each configurable power_supply property, AICL work, IRQ/status decoding, OTG mode, charger enable/disable, and removal with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/max77705_charger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/power_on_reason.h -->
# sources/distributed-fs/ceph-client/include/linux/power/power_on_reason.h

Purpose: centralizes standard string labels for reporting a platform power-on or reset reason.

Important APIs and types: string macros cover regular power-up, RTC wakeup, watchdog timeout, software reset, reset button, CPU clock failure, crystal oscillator failure, brown-out reset, and unknown reason.

Control flow: platform or PMIC drivers select one of these constants when exposing power-on reason through logs, sysfs, debugfs, or power/reset reporting code.

State and persistence: no state is stored. The actual reset reason is hardware/platform state read by drivers.

Dependencies and integration points: standalone header intended to keep power-on reason wording consistent across drivers.

Risks and test signals: risks are mismatched labels, missing platform-specific reasons, and userspace depending on exact strings. Test reason decoding paths, fallback to unknown, and ABI expectations for exposed strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/power_on_reason.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/sbs-battery.h -->
# sources/distributed-fs/ceph-client/include/linux/power/sbs-battery.h

Purpose: defines platform data for SBS-compliant gas gauge battery drivers.

Important APIs and types: `struct sbs_platform_data` supplies I2C retry count and poll retry count after external change notifications.

Control flow: the SBS battery driver uses platform retry limits while reading gauge registers and while polling for new status after a notification.

State and persistence: static probe-time policy only; runtime battery data is in the driver/gauge.

Dependencies and integration points: integrates with power_supply and I2C/SMBus SBS gas-gauge handling.

Risks and test signals: risks include too few retries causing transient failures, too many retries delaying probe/status updates, and missing platform data. Test I2C error handling, external change notification polling, power_supply property reads, and timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/sbs-battery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/smartreflex.h -->
# sources/distributed-fs/ceph-client/include/linux/power/smartreflex.h

Purpose: defines OMAP SmartReflex register offsets, bit fields, platform data, runtime device state, class-driver hooks, and public enable/disable APIs for adaptive voltage scaling.

Important APIs and types: macros define SmartReflex IP versions, register offsets, bit shifts/masks for sensor enable, error generation, min/max/avg, IRQ status/enable, clock lengths, and OMAP3430 defaults. `struct omap_sr` stores runtime device state including platform device, nvalue table, voltage domain, debugfs dir, IRQ, clock, IP type, calibration/tuning values, MMIO base, autocomp and enabled flags. `sr_test_cond_timeout()` busy-waits with microsecond delay. `struct omap_sr_pmic_data`, `struct omap_smartreflex_dev_attr`, `struct omap_sr_class_data`, `struct omap_sr_nvalue_table`, and `struct omap_sr_data` describe PMIC hooks, device attributes, class operations, efuse n-target data, and platform data. APIs include OMAP voltage-domain enable/disable/reset and class-driver hooks when `CONFIG_POWER_AVS_OMAP` is enabled.

Control flow: platform data describes each SR instance and voltage domain. The SmartReflex driver maps registers, initializes clocks/IRQs/calibration, class driver registers callbacks, and runtime enable/configure paths program sensors/error/minmax generation and notify class code of IRQ events. Voltage-domain code can enable/disable SR or reset voltage through the exported APIs.

State and persistence: runtime state includes register programming, clock/IRQ handles, voltage-domain association, calibration n-values from efuse, autocomp state, debugfs data, and enable bit. Efuse calibration is persistent hardware data; header state itself is live kernel state.

Dependencies and integration points: integrates with OMAP voltage domains, PMIC setup, platform devices, clocks, MMIO, IRQs, debugfs, delay loops, and optional AVS config. Disabled AVS builds provide no-op voltage-domain APIs and omit class hook prototypes.

Risks and test signals: risks include wrong register offsets by IP version, busy-wait timeouts, IRQ status mask mistakes, efuse n-value mismatch to voltage domain, class callback lifetime, voltage reset errors, and no-op stubs masking missing AVS. Test OMAP3/OMAP4 SR enable/disable, IRQ/errorgen/minmax configuration, voltage-domain integration, PMIC init, efuse table parsing, timeout paths, and AVS-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/smartreflex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/twl4030_madc_battery.h -->
# sources/distributed-fs/ceph-client/include/linux/power/twl4030_madc_battery.h

Purpose: defines platform calibration data for simple Li-Ion battery capacity estimation using the TWL4030 MADC.

Important APIs and types: `struct twl4030_madc_bat_calibration` maps voltage in mV to capacity percent and uses voltage `-1` as end marker. `struct twl4030_madc_bat_platform_data` supplies total capacity in uAh plus separate charging and discharging calibration tables and sizes.

Control flow: the battery driver reads MADC voltage, selects charging or discharging calibration curve, interpolates capacity/level, and reports battery properties using the supplied total capacity.

State and persistence: static board calibration data only; measured voltage and reported state are runtime driver data.

Dependencies and integration points: integrates with TWL4030 MADC readings and power_supply reporting.

Risks and test signals: risks include unsorted or unterminated calibration tables, wrong charging/discharging curve selection, capacity unit mistakes, and inaccurate endpoints. Test capacity interpolation on both curves, end-marker handling, low/full voltage boundaries, and reported charge units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power/twl4030_madc_battery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power_supply.h -->
# sources/distributed-fs/ceph-client/include/linux/power_supply.h

Purpose: defines the universal Linux power_supply class ABI for batteries, chargers, USB/wireless supplies, UPS devices, battery static data, property access, notifier/registration APIs, and helper conversion routines.

Important APIs and types: enums define supply status, charge type, health, technology, capacity level, scope, property IDs, supply type, USB type, charge behavior, and notifier events. `union power_supply_propval`, `struct power_supply_config`, `struct power_supply_desc`, `struct power_supply_ext`, `struct power_supply`, `struct power_supply_info`, OCV/resistance/VBAT-to-Ri/maintenance tables, and `struct power_supply_battery_info` define driver callbacks, runtime class state, extensions, thermal/LED integration, static battery metadata, and rich CC/CV charging and capacity-estimation parameters. APIs cover notifier registration, get/put by name/reference, battery-info parsing and property access, OCV/resistance/capacity conversions, BTI matching, `power_supply_changed()`, supplier queries, property get/set direct and mediated paths, registration/devm registration/unregistration, extension registration, driver data, iteration, amp/watt property classification, and sysfs parsing/show helpers for charge behavior/type.

Control flow: a power-supply driver declares a descriptor with properties and callbacks, registers it with optional config/supplicant data, and responds to class property reads/writes. Drivers call `power_supply_changed()` after hardware state changes, consumers locate supplies by name/reference or iterate supplies, and battery drivers may load standardized battery info from firmware, convert OCV/temp/VBAT data into capacity, and expose charge behavior/type sysfs strings through helper parsers.

State and persistence: runtime state includes registered class device, changed work/deferred registration work, supplied-to/from arrays, driver data, changed/removing/initialized flags, use count, battery info pointer, extension list under rwsem, thermal zone/cooling device, and LED triggers. Persistent battery characteristics come from firmware/DT/board data consumed into `power_supply_battery_info`; the header itself stores no persistent values.

Dependencies and integration points: integrates with device model, workqueues, LEDs, rwsems, lists, spinlocks, notifiers, thermal framework, firmware nodes, sysfs, user ABI property names/units, charger and fuel-gauge drivers, supplier relationships, and optional `CONFIG_POWER_SUPPLY`/`CONFIG_SYSFS`.

Risks and test signals: risks include property unit mismatches, callback access during probe before driver data is ready, missing `power_supply_changed()` notifications, extension locking mistakes, stale battery_info ownership, malformed OCV/resistance tables, charge behavior bitmask mismatches, and stubs returning success in disabled configs. Test registration/unregistration including devm, all property get/set paths, supplier relationships, notifier delivery, battery-info parsing and conversions, charge behavior/type sysfs parse/show, thermal/LED integration, extension add/remove, and disabled POWER_SUPPLY/SYSFS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/power_supply.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/powercap.h -->
# sources/distributed-fs/ceph-client/include/linux/powercap.h

Purpose: declares the sysfs power-capping class interface for control types, hierarchical power zones, and power-limit constraints.

Important APIs and types: `struct powercap_control_type_ops` enables/disables and releases a control type. `struct powercap_control_type` stores class device, child IDR, zone count, ops, mutex, allocation ownership, and global list node. `struct powercap_zone_ops` exposes energy, power, enable, and release callbacks. `struct powercap_zone` stores ID/name, control-type instance, ops, device, child/parent IDRs, private data, sysfs attribute groups, allocation ownership, and constraints. `struct powercap_zone_constraint_ops` defines mandatory limit/window/name callbacks plus min/max bounds. Registration APIs add/remove control types and zones, and helpers get/set zone private data.

Control flow: a driver registers a named control type, then registers top-level and child zones with zone ops and constraint ops. The framework creates devices and sysfs attributes, routes reads/writes to callbacks, and requires child zones be removed before parents and all zones before unregistering a control type.

State and persistence: runtime state includes class devices, IDR trees, mutex-protected hierarchy, attribute arrays, private data pointers, constraints, and ownership flags controlling release behavior. Power limits may persist in hardware depending on the driver; the framework state is live kernel state.

Dependencies and integration points: integrates with device model sysfs, IDR allocation, mutex/list management, RAPL or other power-control drivers, and user-space powercap ABI.

Risks and test signals: risks include missing mandatory callbacks, unregistering parents before children, freeing client-owned memory without release, hierarchy IDR leaks, units confusion between uJ/uW/us, and insufficient callback locking. Test sysfs reads/writes for energy/power/constraints, enable toggles, nested zones, unregister ordering, release callbacks, private data helpers, and error paths for duplicate control-type names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/powercap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ppp-comp.h -->
# sources/distributed-fs/ceph-client/include/linux/ppp-comp.h

Purpose: declares the PPP compression plugin interface used by compressor modules and generic PPP CCP handling.

Important APIs and types: `struct compressor` defines protocol number, compressor/decompressor allocation/free/init/reset callbacks, packet compress/decompress functions, incompressible-packet update hook, stats hooks, module owner, and extra skb space. Constants enable BSD-Compress and Deflate by default, disable Predictor variants, and define decompression error codes `DECOMP_ERROR` and `DECOMP_FATALERROR`. APIs register/unregister compressor implementations.

Control flow: a compressor module registers its callback table, PPP negotiates CCP options, allocates TX/RX compressor state, initializes it with options/unit/debug data, compresses outgoing packets, decompresses incoming packets, updates state on incompressible packets, reports stats, and unregisters on module removal.

State and persistence: per-link compressor state is allocated by callbacks and owned by PPP until freed. Module owner protects implementation lifetime; no persistent state is held in the header.

Dependencies and integration points: depends on PPP compression UAPI, PPP generic layer, sk_buff sizing, module refcounts, and compression algorithm modules.

Risks and test signals: risks include module unregister while state is active, buffer-size/extra-headroom mistakes, decompression fatal vs recoverable error confusion, option parsing bugs, and patent-related CCP reset behavior around fatal errors. Test compressor registration, CCP negotiation, compress/decompress round trips, incompressible updates, stats, error returns, MTU/MRU limits, and module unload with active PPP links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ppp-comp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ppp_channel.h -->
# sources/distributed-fs/ceph-client/include/linux/ppp_channel.h

Purpose: defines the interface between generic PPP code and lower transport channels.

Important APIs and types: `struct ppp_channel_ops` provides `start_xmit`, `ioctl`, and optional forwarding-path fill callbacks. `struct ppp_channel` stores channel private data, ops, MTU, header headroom, opaque generic PPP pointer, speed, and direct-xmit flag. APIs wake PPP output, deliver input packets/errors, register/unregister channels in a network namespace or default namespace, query channel/unit numbers, and get associated device name under RCU.

Control flow: a transport driver initializes `ppp_channel`, registers it with PPP, accepts `start_xmit()` calls for packets/fragments, calls `ppp_input()` for received packets, reports input errors when packet loss may have occurred, wakes output when TX capacity returns, and unregisters only after ensuring no channel callbacks are executing.

State and persistence: runtime state is split between transport-private data, opaque PPP binding, MTU/headroom/speed/direct-xmit metadata, and generic PPP unit associations. No persistence is defined.

Dependencies and integration points: integrates with sk_buffs, net namespaces, poll include dependency, net_device path offload/forwarding, PPP generic core, and RCU for device-name lookup.

Risks and test signals: risks include skb ownership mistakes, unregister races with input/output/ioctl callbacks, wrong MTU/headroom causing corruption, direct-xmit bypass issues, net namespace registration mistakes, and missing RCU when reading device names. Test channel register/unregister, TX backpressure and wakeups, RX packet/error paths, ioctl forwarding, multilink fragmentation, netns teardown, and RCU device-name access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ppp_channel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ppp_defs.h -->
# sources/distributed-fs/ceph-client/include/linux/ppp_defs.h

Purpose: wraps PPP UAPI definitions with kernel helpers for FCS and protocol-field validation.

Important APIs and types: `PPP_FCS()` maps to `crc_ccitt_byte()`. `ppp_proto_is_valid()` checks uncompressed PPP protocol encoding per RFC 1661, and `ppp_skb_is_compressed_proto()` tests whether the protocol field in an skb is compressed.

Control flow: PPP parsing/validation code computes frame check sequence bytes, validates protocol numbers before use, and distinguishes compressed protocol-field packets by inspecting the first data byte.

State and persistence: no state is stored.

Dependencies and integration points: depends on CRC-CCITT helpers, sk_buff data layout, and UAPI PPP definitions.

Risks and test signals: risks include calling compressed-protocol detection when `skb->data` is not positioned at the PPP protocol header, validating already-compressed protocol fields, and CRC compatibility drift. Test PPP frame parsing, protocol compression negotiation, invalid protocol rejection, and FCS vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ppp_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pps_gen_kernel.h -->
# sources/distributed-fs/ceph-client/include/linux/pps_gen_kernel.h

Purpose: declares the kernel PPS generator API for devices that generate Pulse Per Second events.

Important APIs and types: `PPS_GEN_MAX_SOURCES` caps registered generators. `struct pps_gen_source_info` supplies whether the system clock is used, `get_time` and `enable` callbacks, plus private owner/parent device fields. `struct pps_gen_device` stores source info, enabled flag, event/sequence counters, last event, wait queue, ID, cdev, device, fasync queue, and spinlock. APIs register/unregister a source and emit generator events; `pps_gen_groups` declares sysfs attribute groups.

Control flow: a generator driver fills source info and registers it; userspace can open/control the cdev; the driver enables/disables pulse generation through callbacks and calls `pps_gen_event()` when a generator event occurs, waking waiters and async listeners.

State and persistence: runtime state includes enabled status, sequence/event counters, wait queue, async queue, cdev/device lifetime, and spinlock-protected updates. No persistent state is stored.

Dependencies and integration points: integrates with PPS generator UAPI, cdev/device core, wait queues, fasync, sysfs groups, module ownership, and optional hardware or system-clock time sources.

Risks and test signals: risks include exceeding source cap, callback owner lifetime, event sequence races, enable-state mismatch, async notification leaks, and unregister with open cdevs. Test source registration limits, enable/disable, event delivery to read/poll/fasync consumers, unregister while idle/open, and system-clock vs hardware-clock callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pps_gen_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pps_kernel.h -->
# sources/distributed-fs/ceph-client/include/linux/pps_kernel.h

Purpose: declares the kernel PPS source API for timestamping Pulse Per Second assert/clear events and exposing them through character devices.

Important APIs and types: `struct pps_source_info` supplies name, path, allowed modes, echo callback, module owner, and parent device. `struct pps_event_time` stores real and optionally raw timestamps. `struct pps_device` stores source info, current params, assert/clear sequence numbers and timestamps, current mode, last/fetched event IDs, wait queue, source ID, lookup cookie, device, async queue, and spinlock. APIs register/unregister cdevs and sources, emit PPS events, look up devices by cookie, convert timespec to PPS ktime, capture timestamps with `ktime_get_snapshot()`, and subtract known delays.

Control flow: a hardware driver registers a PPS source, captures event timestamps with `pps_get_ts()` at interrupt time, optionally compensates delay with `pps_sub_ts()`, and calls `pps_event()` with assert/clear event data. PPS core updates sequences/timestamps, wakes waiters, emits async notifications, and optionally feeds NTP raw timestamps.

State and persistence: runtime PPS state includes parameters, last assert/clear timestamps, sequences, wait queues, lookup cookie, cdev/device lifetime, and async queue. No persistent state is stored.

Dependencies and integration points: integrates with PPS UAPI, cdev/device core, timekeeping snapshots, optional NTP PPS raw time, wait queues, fasync, and driver echo callbacks.

Risks and test signals: risks include timestamping too late, raw/real timestamp mismatch, sequence races, unregister with consumers, lookup-cookie lifetime, and incorrect delay compensation. Test interrupt timestamp paths, assert/clear modes, poll/read/fasync delivery, NTP PPS integration, unregister/open races, and delay compensation vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pps_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pr.h -->
# sources/distributed-fs/ceph-client/include/linux/pr.h

Purpose: declares block-device persistent reservation data structures and operation callbacks.

Important APIs and types: `struct pr_keys` carries generation, key count, and flexible key array. `struct pr_held_reservation` carries key, generation, and reservation type. `struct pr_ops` defines callbacks for register, reserve, release, preempt, clear, read keys, and read reservation.

Control flow: block-layer or filesystem management code invokes `pr_ops` on a `block_device` to manage SCSI/NVMe-style persistent reservations, and reads key/reservation state for reporting or retry sizing.

State and persistence: reservation keys and held reservation are persistent device-side state; the structs here are transient kernel buffers and callback tables.

Dependencies and integration points: integrates with block devices and UAPI persistent reservation types/flags. Implementations are supplied by lower block transports/drivers.

Risks and test signals: risks include key array sizing/retry bugs, generation mismatch handling, reservation type mismatches, preempt abort semantics, and incomplete driver callback coverage. Test PR register/reserve/release/preempt/clear, read-keys retry with too-small buffer, read-reservation generation/type, multipath/failover behavior, and unsupported-device errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/prandom.h -->
# sources/distributed-fs/ceph-client/include/linux/prandom.h

Purpose: declares the fast pseudo-random state API for deterministic or per-CPU non-cryptographic random generation.

Important APIs and types: `struct rnd_state` stores four 32-bit state words. APIs include `prandom_u32_state()`, `prandom_bytes_state()`, `prandom_seed_full_state()`, `prandom_init_once()` for one-time per-CPU seeding, `__seed()` minimum-value adjustment, and `prandom_seed_state()` which expands a 64-bit seed into the four state words.

Control flow: users allocate state, seed it explicitly or once per CPU, then request u32 values or byte buffers. The seed helper derives a 32-bit value from the 64-bit seed and ensures each state component is above its minimum threshold.

State and persistence: mutable PRNG state is caller-owned or per-CPU and advances as values are generated. It is not cryptographic persistent entropy and should not be used for secrets.

Dependencies and integration points: depends on types, once helpers, percpu storage, and random seeding. Used by networking/tests/subsystems needing fast pseudo-randomness.

Risks and test signals: risks include cryptographic misuse, unseeded/reused deterministic state, per-CPU init races if not using `prandom_init_once()`, and assumptions about sequence stability. Test deterministic sequences after seeding, byte generation length, per-CPU one-time seeding, and static analysis for security-sensitive use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/prandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/preempt.h -->
# sources/distributed-fs/ceph-client/include/linux/preempt.h

Purpose: defines preemption count bit layout, interrupt-context predicates, preempt disable/enable primitives, nested preempt handling for RT, preempt notifiers, scoped guards, and preemption-model queries.

Important APIs and types: bit masks and offsets split `preempt_count()` into preempt, softirq, hardirq, and NMI fields plus need-resched handling. Helpers/macros include `interrupt_context_level()`, `nmi_count()`, `hardirq_count()`, `softirq_count()`, `irq_count()`, `in_nmi()`, `in_hardirq()`, `in_serving_softirq()`, `in_task()`, deprecated `in_softirq()`/`in_interrupt()`, `in_atomic()`, `preempt_disable/enable()`, notrace/no-resched variants, `preempt_check_resched()`, need-resched fold/set helpers, `preempt_disable_nested()/preempt_enable_nested()`, lock guards, `struct preempt_ops`, `struct preempt_notifier`, notifier registration APIs, and preempt model queries including dynamic model support.

Control flow: kernel code increments preempt count before critical sections and decrements on exit; on preemptible kernels `preempt_enable()` schedules if the count reaches zero and resched is pending. Interrupt and softirq entry code manipulates the corresponding count fields. PREEMPT_RT changes softirq/preempt-lock semantics and uses nested preempt disable only where CPU-local serialization is required. Preempt notifiers call registered hooks on task schedule-out/in under documented contexts.

State and persistence: state lives in per-task/arch preempt count, softirq disable count on RT, need-resched flags, and optional notifier lists. It is strictly runtime scheduler/context state.

Dependencies and integration points: depends on arch `asm/preempt.h`, scheduler preemption functions, task flags, IRQ state, lockdep, cleanup guard macros, PREEMPT_RT, PREEMPT_DYNAMIC, modules, and KVM or other users of preempt notifiers.

Risks and test signals: risks include unbalanced preempt counts, scheduling with preemption disabled, sleeping in atomic context, using deprecated context predicates for sleepability, RT semantic drift around spinlocks/softirqs, module misuse of no-resched helpers, notifier lifetime bugs, and dynamic preempt model misclassification. Test lockdep/preempt count debugging, voluntary/full/lazy/RT/none models, nested RT sections, interrupt context predicates, preempt notifier register/unregister around task switches, module builds, and stress tests for schedule-in-atomic warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/preempt.h -->
