# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ixp4xx.c

Purpose: Intel IXP4xx OS timer driver for timestamp clocksource/sched_clock/delay timer, timer1 clockevent, and watchdog child platform-device creation.

Important APIs/types/functions: `struct ixp4xx_timer` stores base, latch, clockevent, and optional ARM delay timer. `ixp4xx_timer_register()` initializes hardware and framework devices. Clockevent callbacks program `OSRT1`; `ixp4xx_clocksource_read()` uses `OSTS`; `ixp4xx_timer_probe()` registers `ixp4xx-watchdog`.

Control flow: OF init maps MMIO, parses IRQ, then calls register with a hard-coded 66.666 MHz frequency. Registration resets timer1 and timestamp counter, registers custom clocksource, requests timer1 IRQ, registers clockevent, sched_clock, and delay timer. Periodic mode writes a latch rounded to the hardware’s ignored low bits; oneshot writes enable/one-shot bits and later reload value.

State/persistence: singleton `local_ixp4xx_timer` backs fast reads and watchdog platform data. Hardware timer registers are shared with watchdog code.

Dependencies/integration: compatible `intel,ixp4xx-timer`, platform driver for child device, ARM delay timer, clocksource/clockevents, fixed platform timer frequency.

Risks: hard-coded clock frequency until DT fixed clocks exist; no watchdog probe guard if timer init failed other than singleton use; clocksource registration errors are not checked; raw MMIO access and shared watchdog registers require careful ownership. Test signals include timer tick, clocksource stability, watchdog registration, and correct latch behavior at HZ boundaries.
