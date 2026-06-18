# sources/distributed-fs/ceph-client/drivers/clocksource/arc_timer.c

Purpose: supports ARC core timers as clocksources and per-CPU clockevents, including 32-bit TIMER0/TIMER1 and optional 64-bit RTC/GFRC counters.

Important APIs/types/functions: `arc_get_timer_clk()`, `arc_cs_setup_gfrc()`, `arc_cs_setup_rtc()`, `arc_cs_setup_timer1()`, `arc_clockevent_setup()`, per-CPU `arc_clockevent_device`, and `arc_of_timer_init()`.

Control flow: DT declarations initialize either a clockevent node or a clocksource node. Clockevents use TIMER0 with a per-CPU IRQ and CPU hotplug callbacks. Clocksources use TIMER1 for legacy UP or RTC/GFRC for ARCv2 depending on hardware capability and SMP suitability.

State and persistence: global timer frequency and IRQ persist; per-CPU clockevent devices are registered on CPU bring-up. Counter hardware state is programmed through ARC auxiliary registers.

Dependencies and integration points: depends on ARC auxiliary register helpers, MCIP/GFRC support, OF clock/IRQ parsing, sched_clock, and clockevents.

Risks: local TIMER1 and RTC are rejected for SMP. GFRC reads disable local IRQs around MCIP commands. Missing or disabled parent clocks abort initialization. Timer interrupt acknowledgement differs across ARC generations.

Test signals: DT compatible probing for `snps,arc-timer`, RTC/GFRC compatibles, CPU hotplug, SMP versus UP selection, and periodic/oneshot event delivery.
