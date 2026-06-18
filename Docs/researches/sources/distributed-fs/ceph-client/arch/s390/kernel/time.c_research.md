## sources/distributed-fs/ceph-client/arch/s390/kernel/time.c

Purpose: Owns s390 TOD-based timekeeping, clocksource registration, per-CPU clock comparator event devices, persistent clock reads, Server Time Protocol synchronization, and STP sysfs controls.

Important APIs and functions: `time_early_init()`, `sched_clock_noinstr()`, `sched_clock()`, `clock_comparator_work()`, `init_cpu_timer()`, `read_persistent_clock64()`, `read_persistent_wall_and_boot_offset()`, `clocksource_default_clock()`, `time_init()`, `get_phys_clock()`, `stp_enabled()`, `stp_sync_check()`, `stp_island_check()`, `stp_queue_work()`, and STP sysfs attribute handlers.

Control flow: Early init records TOD delta for vDSO, queries PTFF for LPAR offset/leap seconds, and later `time_init()` resets STP, registers external interrupts, registers the TOD clocksource, and initializes boot CPU timers. Per-CPU comparator setup registers a one-shot clockevent and enables control-register bits. STP timing alerts and machine checks queue work; the worker controls STP attachment, reads STP info, and uses `stop_machine()` to disable/enable per-CPU sync bits, apply global TOD deltas under vDSO update protection, adjust per-CPU comparator/last-update timestamps, and retry on failure.

State and persistence: Boot-preserved `tod_clock_base` and `clock_comparator_max`, per-CPU `comparators` and sync words, global `clock_sync_flags`, `lpar_offset`, `initial_leap_seconds`, `stp_info`, `stp_page`, `stp_online`, timers/workqueue, and the exported epoch-delta notifier chain are persistent runtime state.

Dependencies and integration: Integrates with vDSO time data, clocksource/clockevents, external IRQ registry, CHSC STP calls, PTFF, vtime, CIO/STP machine checks, sysfs bus registration, and atomic notifier users that react to TOD epoch changes.

Risks and test signals: Risks include clock jumps without matching vDSO updates, comparator adjustment races during STP sync, STP state changes under hotplug, and sysfs returning stale or invalid STP fields. Test signals include clocksource registration, clockevent interrupts, `get_phys_clock()` return codes under synced/unsynced modes, STP sysfs values, timing-alert interrupt handling, leap-second reporting, and monotonic sched-clock stability after STP sync.
