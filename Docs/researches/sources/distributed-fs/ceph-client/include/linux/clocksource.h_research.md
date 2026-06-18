# sources/distributed-fs/ceph-client/include/linux/clocksource.h

Purpose: This header defines the clocksource abstraction for free-running counters used by timekeeping, plus helper math and registration/probe hooks.

Important APIs/types/functions: It defines `struct clocksource`, flags such as `CLOCK_SOURCE_IS_CONTINUOUS`, `CLOCK_SOURCE_MUST_VERIFY`, `CLOCK_SOURCE_WATCHDOG`, `CLOCK_SOURCE_VALID_FOR_HRES`, `CLOCK_SOURCE_UNSTABLE`, `CLOCK_SOURCE_SUSPEND_NONSTOP`, `CLOCK_SOURCE_CAN_INLINE_READ`, and `CLOCK_SOURCE_HAS_COUPLED_CLOCK_EVENT`, macro `CLOCKSOURCE_MASK`, conversion helpers `clocksource_freq2mult`, `clocksource_khz2mult`, `clocksource_hz2mult`, and `clocksource_cyc2ns`, registration/update helpers `clocksource_register_hz`, `clocksource_register_khz`, `__clocksource_register`, `__clocksource_update_freq_hz`, `__clocksource_update_freq_khz`, watchdog and suspend helpers, MMIO helpers, `clocksource_mmio_init`, `clocksource_i8253_init`, timer declaration macros `TIMER_OF_DECLARE` and `TIMER_ACPI_DECLARE`, `timer_probe`, and `struct clocksource_base`.

Control flow: Clocksource drivers fill a `struct clocksource` with a `read` callback, mask, rating, frequency conversion values, flags, and optional enable/disable/suspend/resume/watchdog hooks, then register it. Timekeeping selects a suitable source by rating and validity, caches hot-path fields elsewhere, and uses watchdog validation to mark unstable sources. OF/ACPI timer declarations hook probe functions into early timer discovery.

State and persistence behavior: Runtime state includes registered list nodes, frequency, mask, conversion factors, watchdog last values, selected clocksource identity, suspend timing, and base-clock relationships. The source struct is not itself the timekeeping hot path but persists while registered.

Dependencies and integration points: It includes time, list, timer, init, OF, clocksource ID, architecture division/MMIO, optional architecture clocksource data, and VDSO clocksource mode. Integration points are timekeeping, sched_clock-adjacent counter drivers, watchdog validation, MMIO counter helpers, DT/ACPI timer probing, and VDSO mode selection.

Risks: Counter masks, mult/shift, and frequency units must be correct or system time drifts. Rating inflation can select an inferior source. Sources marked continuous or suspend-nonstop incorrectly can break idle or suspend accounting. Watchdog fields and unstable marking must be honored to avoid bad timekeeping.

Test signals: Timekeeping selftests, NTP/clock drift monitoring, watchdog instability logs, suspend/resume time continuity, high-resolution timer enablement, VDSO clock mode checks, and MMIO counter wrap tests validate behavior.
