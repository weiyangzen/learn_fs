# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/time.h

Purpose: Declares Orion timer initialization APIs for the platform clocksource, clockevent, sched_clock, and delay timer implementation.

Important APIs: `orion_time_set_base(void __iomem *timer_base)` records the timer block base. `orion_time_init(void __iomem *bridge_base, u32 bridge_timer1_clr_mask, unsigned int irq, unsigned int tclk)` initializes bridge interrupt handling and timer frequency.

Control flow/state: Machine setup must set the timer base before full time initialization. The implementation stores bases and masks in static globals and registers Linux timekeeping devices.

Dependencies/integration: Depends on Linux `__iomem` and `u32` types from includers. Integrates machine setup with `time.c`.

Risks/tests: Wrong call ordering or incorrect `tclk` skews timekeeping and delays. Boot tests should check clocksource registration, periodic/oneshot timer interrupts, and delay calibration.
