# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rc5t583.c

Purpose: implements RTC support for the Ricoh RC5T583 PMIC MFD. It provides BCD time read/write, year-alarm support, alarm IRQ notification, wake capability, and suspend/resume preservation of interrupt enables.

Important APIs/types/functions: `struct rc5t583_rtc` stores the RTC and saved interrupt-enable register. `rc5t583_rtc_read_time()` and `rc5t583_rtc_set_time()` bulk-transfer time registers through the parent regmap. `rc5t583_rtc_read_alarm()` and `rc5t583_rtc_set_alarm()` manage the year-alarm register range. `rc5t583_rtc_alarm_irq_enable()` updates the Y-alarm enable bit. `rc5t583_rtc_interrupt()` reads and clears Y-alarm status and calls `rtc_update_irq()`.

Control flow: probe clears pending RTC interrupts and adjust register, derives the IRQ from platform data `irq_base + RC5T583_IRQ_YALE`, requests a threaded low-trigger IRQ, marks wakeup capable, and registers the RTC. Remove disables the alarm. Suspend caches `RTC_CTL1`; resume restores it.

State and persistence: time and alarm live in PMIC RTC registers. The driver assumes years are 2000-2099. `irqen` is runtime state used only across system sleep.

Dependencies and integration: depends on the `rc5t583` MFD parent, its regmap, platform data IRQ base, RTC core, and threaded IRQs.

Risks: probe dereferences platform data without a null check, so DT-only or malformed MFD setup can fault. The interrupt handler calls `rtc_update_irq()` even if no Y-alarm status was present, with events zero. Alarm seconds are not supported and read back as zero. Test signals include platform-data IRQ derivation, alarm enable/status clear, suspend/resume register restore, missing IRQ handling, BCD conversion, and years outside 2000-2099.
