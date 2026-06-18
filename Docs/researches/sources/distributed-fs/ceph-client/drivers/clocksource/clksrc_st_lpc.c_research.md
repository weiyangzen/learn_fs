# sources/distributed-fs/ceph-client/drivers/clocksource/clksrc_st_lpc.c

Purpose: registers the ST Low Power Controller low-power timer as a clocksource when the LPC mode is configured for clocksource operation.

Important APIs/types/functions: global `ddata`, `st_clksrc_reset()`, `st_clksrc_sched_clock_read()`, `st_clksrc_setup_clk()`, `st_clksrc_init()`, and `st_clksrc_of_register()`.

Control flow: DT init reads `st,lpc-mode`, exits if not clocksource mode, maps registers, enables the LPC clock, resets and starts the low-power timer, registers sched_clock, and registers a 32-bit MMIO clocksource.

State and persistence: global clock pointer and MMIO base persist; timer registers are reset to zero and started on init.

Dependencies and integration points: depends on `dt-bindings/mfd/st-lpc.h`, OF mapping, CCF, sched_clock, and `clocksource_mmio_init`.

Risks: a shared LPC block can be configured for RTC/WDT instead, in which case this driver silently does nothing. Initialization failure after clock enable performs cleanup, but successful resources are permanent. Mode property is mandatory.

Test signals: DT mode selection, clock enable/rate failure paths, sched_clock registration, and monotonic clocksource reads.
