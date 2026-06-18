# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mv.c

Purpose: implements the Marvell Orion RTC, using packed BCD MMIO registers for time/date and optional alarm interrupt support.

Important APIs/types/functions: `struct rtc_plat_data` stores RTC device, MMIO base, optional IRQ, and optional clock. `mv_rtc_read_time()`/`set_time()` decode and encode packed time/date registers. `mv_rtc_read_alarm()`/`set_alarm()` handle alarm registers with per-field `RTC_ALARM_VALID` bits. `mv_rtc_alarm_irq_enable()` toggles the alarm mask, and `mv_rtc_interrupt()` clears and reports alarm cause.

Control flow: probe maps MMIO, optionally enables a clock, rejects unsupported 12-hour mode, checks that the RTC is ticking by detecting the stuck reset value over one second, gets an optional IRQ, allocates the RTC, requests the IRQ if available, and clears the alarm feature when no IRQ exists. Time reads/writes access two packed registers. Alarm writes accept `-1` fields as don't-care by omitting valid bits and enable or mask the interrupt.

State and persistence: time, date, alarm, interrupt mask, and interrupt cause live in hardware. Driver state owns optional clock and IRQ. Remove disables wake capability and the clock but leaves RTC time running.

Dependencies and integration: depends on OF compatible `marvell,orion-rtc`, MMIO, optional clock, optional shared IRQ, BCD helpers, and `module_platform_driver_probe()` because remove is in exit text.

Risks and test signals: optional clock enable return is ignored if present; if `clk_prepare_enable()` fails, probe continues. Alarm enabled is reported as true for any nonzero interrupt mask. Probe's ticking check sleeps one second and assumes `0x01000000` means nonfunctional. Test 12-hour rejection, stuck-clock detection, optional/no IRQ behavior with RTC alarm feature cleared, don't-care alarm fields, alarm cause clear, clock failure handling, and BCD range endpoints 2000-2099.
