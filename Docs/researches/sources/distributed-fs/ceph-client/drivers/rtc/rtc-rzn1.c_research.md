<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rzn1.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rzn1.c

Purpose: implements the Renesas RZ/N1 MMIO RTC with calendar time, week-based alarms, optional one-second alarm refinement, runtime PM, and oscillator offset support when using the standard 32.768 kHz mode.

Important APIs/types/functions: `struct rzn1_rtc` stores the RTC device, MMIO base, spinlock for CTL1 interrupt bits, and cached alarm time. `rzn1_rtc_get_time_snapshot()`, `rzn1_rtc_read_time()`, `rzn1_rtc_set_time()`, `rzn1_rtc_alarm_irq_enable()`, `rzn1_rtc_read_alarm()`, `rzn1_rtc_set_alarm()`, `rzn1_rtc_read_offset()`, and `rzn1_rtc_set_offset()` implement behavior. Ops are split between SUBU offset-capable mode and SCMP external-rate mode.

Control flow: probe maps registers, gets alarm IRQ, enables runtime PM, optionally reads an `xtal` clock, disables the controller, selects SCMP mode if the xtal is valid but not 32768 Hz, programs SCMP or SUBU mode, enables the controller, disables interrupts, requests alarm IRQ, optionally requests PPS IRQ, then registers the RTC. Time reads reject stopped counters and re-snapshot on second mismatch. Set-time waits for stop acknowledgement, writes BCD packed time/calendar registers, and restarts. Alarm enable chooses minute alarm or one-second interrupt depending on how close the target second is.

State and persistence: hardware persists time/calendar, control mode, alarm minute/hour/weekday, second compare, and offset/subtraction registers. The exact requested alarm timestamp is cached in RAM for second-level handling.

Dependencies and integration points: depends on platform MMIO, named IRQs `alarm` and optional `pps`, optional clock `xtal`, runtime PM, RTC core, BCD helpers, and OF compatible `renesas,rzn1-rtc`.

Risks and test signals: alarms cannot be set more than one week ahead and `days_ahead = tm_mday - now_mday` is fragile across month boundaries. Second-precision alarms degrade to minute precision without PPS IRQ. Offset writes with zero steps return without clearing previous offset. Test SCMP/SUBU selection, non-32768 xtal rates, stopped-counter reads, month-boundary alarms, PPS-present and PPS-absent behavior, CTL1 spinlock protection, runtime PM remove path, and offset range/update-busy timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rzn1.c -->
