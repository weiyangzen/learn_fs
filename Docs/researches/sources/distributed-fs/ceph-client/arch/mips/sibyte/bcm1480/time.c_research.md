# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/time.c

Purpose: BCM1480 platform time initialization glue.

Important APIs and control flow: `plat_time_init()` calls external `sb1480_clocksource_init()` and `sb1480_clockevent_init()` in order.

State, persistence, and integration: state is created by the common BCM1480 clocksource/clockevent implementation outside this file. Dependencies include the selected `CEVT_BCM1480` and `CSRC_BCM1480` providers. Risks are limited to missing external clock functions or wrong init ordering. Test signals are registered BCM1480 clocksource/clockevent devices and functioning timer interrupts.
