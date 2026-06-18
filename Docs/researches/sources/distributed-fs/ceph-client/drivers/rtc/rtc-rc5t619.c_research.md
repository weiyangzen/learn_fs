# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rc5t619.c

Purpose: supports the Ricoh RC5T619/RN5T618-family PMIC RTC. It provides time read/write with 12-hour and 24-hour handling, full date alarms, alarm IRQ/wake support when the MFD IRQ domain is available, and one-time power-on cleanup.

Important APIs/types/functions: `struct rc5t619_rtc` stores IRQ, RTC, and parent MFD pointer. `rtc5t619_12hour_bcd2bin()` and `rtc5t619_12hour_bin2bcd()` convert 12-hour encoded values. `rc5t619_rtc_periodic_disable()` and `rc5t619_rtc_pon_setup()` clear periodic/PON state. `rc5t619_rtc_read_time()` rejects PON invalid state; `rc5t619_rtc_set_time()` runs setup if PON is set. `rc5t619_rtc_read_alarm()`, `rc5t619_rtc_set_alarm()`, and `rc5t619_rtc_alarm_enable()` handle alarms. `rc5t619_rtc_irq()` clears alarm flags and reports events.

Control flow: probe gets the parent `rn5t618`, resolves the virtual RTC IRQ if an IRQ domain exists, reads CTRL2, disables periodic functions, clears alarm flags after PON, allocates RTC, sets 1900-2099 range, requests a threaded IRQ if available and enables IRQ wake, otherwise disables alarm interrupt and warns, then registers the RTC.

State and persistence: PMIC registers store time, month century flag, alarm, PON/voltage flags, 12/24-hour mode, periodic settings, and alarm enable/status. Driver state only remembers IRQ availability and parent pointers.

Dependencies and integration: depends on the `rn5t618` MFD, regmap, regmap IRQ domain, platform bus, RTC core, and IRQ wake handling.

Risks: `rc5t619_rtc_set_alarm()` increments `alrm->time.tm_mon` in place, mutating the caller's alarm structure. Probe calls `enable_irq_wake()` directly and does not pair it with PM helpers or disable on remove. If PON is set, reads fail until a set-time path initializes the chip. Test signals include PON invalid/read recovery, 12/24-hour conversions for midnight/noon, alarm month mutation, no-IRQ mode, IRQ flag clearing, wake behavior, and century flag around 1999/2000.
