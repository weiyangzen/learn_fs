# sources/distributed-fs/ceph-client/drivers/clocksource/clksrc-dbx500-prcmu.c

Purpose: uses ST-Ericsson DBx500 PRCMU timer 4 in the always-on domain as a 32 kHz clocksource.

Important APIs/types/functions: `clksrc_dbx500_prcmu_read()`, `clocksource_dbx500_prcmu`, and `clksrc_dbx500_prcmu_init()`.

Control flow: DT init maps the timer, ensures it is configured as a continuous down-counter with max reload if firmware did not do so, and registers a 32-bit continuous suspend-nonstop clocksource at 32768 Hz.

State and persistence: a global MMIO base persists. Hardware timer mode/ref registers may be initialized once and then left running.

Dependencies and integration points: depends on OF mapping and the clocksource core; no clockevent or clock framework dependency appears in this file.

Risks: `of_iomap()` is not checked for failure. The fixed rate assumes the PRCMU timer always runs at 32 kHz. Read uses two consecutive reads to avoid unstable values, then bitwise-negates the decrementing counter.

Test signals: DB8500 DT probe, suspend/resume timekeeping, continuous-mode register state, and 32-bit wrap behavior.
