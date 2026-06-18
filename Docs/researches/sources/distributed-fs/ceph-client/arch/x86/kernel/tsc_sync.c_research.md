# sources/distributed-fs/ceph-client/arch/x86/kernel/tsc_sync.c

Purpose: validates and repairs TSC synchronization across CPUs, primarily through the `MSR_IA32_TSC_ADJUST` register and a two-CPU warp measurement during CPU bringup.

Important APIs/functions: `mark_tsc_async_resets()`, `tsc_verify_tsc_adjust()`, `tsc_store_and_check_tsc_adjust()`, and `check_tsc_sync_target()`. Internal paths include the periodic `tsc_sync_check_timer`, `check_tsc_warp()`, `check_tsc_sync_source()`, and work item `tsc_sync_work`.

Control flow: boot and CPU bringup record each CPU's TSC_ADJUST value, normalize first-package values where allowed, compare sibling values, and optionally skip expensive sync tests when the package is already fixed. Otherwise the new CPU asks an online CPU to run a synchronized warp test. Both CPUs repeatedly read ordered TSC values under a raw arch spinlock; backward motion increments warp counters. If TSC_ADJUST exists, the target may retry up to three times after compensating its adjust value. Terminal random or persistent warp schedules work to mark the TSC unstable.

State and persistence: per-CPU `struct tsc_adjust` stores boot and adjusted values, next check time, and warning state. Global atomics, warp counters, `sync_lock`, `last_tsc`, timer state, and `tsc_async_resets` coordinate checks. MSR writes persist in hardware until changed or reset.

Dependencies and integration: used by `tsc.c` during `tsc_enable_sched_clock()`, TSC clocksource resume, CPU bringup, idle/periodic checks, and TSC reliability decisions. It depends on SMP, topology core masks, TSC_ADJUST MSR support, timers, workqueues, and NMI watchdog touching during tight loops.

Risks: bad firmware that writes TSC_ADJUST, asynchronous socket resets, hotplugged packages, or unreliable topology can trigger false instability or leave CPUs skewed. The raw lock measurement is intentionally tight; bugs here can affect CPU bringup timing and global clocksource selection.

Test signals: warnings for TSC_ADJUST differences, compensation messages, synchronization pass/fail logs, and TSC unstable logs are the key signals. Exercise CPU hotplug, multi-socket systems, resume, and systems with/without TSC_ADJUST.
