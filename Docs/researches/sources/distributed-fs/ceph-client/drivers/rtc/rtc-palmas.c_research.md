# sources/distributed-fs/ceph-client/drivers/rtc/rtc-palmas.c

Purpose: implements RTC support for TI Palmas/TPS65913/TPS65914 PMIC-family devices through the parent Palmas MFD register helpers, with BCD time, alarm IRQ, wake support, and backup-battery charging configuration.

Important APIs/types/functions: `struct palmas_rtc` stores RTC device, device pointer, and IRQ. `palmas_rtc_read_time()` latches time with `GET_TIME` then bulk-reads seconds through years. `palmas_rtc_set_time()` stops the RTC, bulk-writes BCD time, and restarts it. Alarm callbacks use `PALMAS_ALARM_SECONDS_REG` through year plus `PALMAS_RTC_INTERRUPTS_REG`. `palmas_clear_interrupts()` read/write-clears `PALMAS_RTC_STATUS_REG`, and `palmas_rtc_interrupt()` reports `RTC_AF`.

Control flow: probe reads DT backup-battery charge properties, allocates state, clears pending interrupts, optionally configures backup battery charge current and enable bits, starts the RTC, gets IRQ 0, marks wake-capable, registers the RTC, and requests a low-triggered threaded IRQ. Set-alarm disables alarm interrupts before programming alarm registers and re-enables when requested. Remove disables alarm IRQ; suspend/resume toggle IRQ wake if wake-capable.

State and persistence: PMIC registers persist BCD time, alarm, RTC stop/control, interrupt enable/status, and backup-battery charging configuration. Driver state is minimal and contains no cache.

Dependencies and integration: depends on Palmas MFD parent data and register helper APIs, OF compatible `ti,palmas-rtc`, platform IRQ, PM wake hooks, and RTC class.

Risks and test signals: `platform_get_irq()` return is stored but not checked before wake setup and IRQ request, so negative IRQ handling relies on later APIs. Stop/start polarity is non-obvious: setting `STOP_RTC` starts in this driver's usage and clearing it stops. Backup-battery configuration is persistent and should be intentional from DT. Test parent regmap errors, pending status clear, backup charge low/high current properties, alarm disable-before-write, IRQ request failure with missing IRQ, suspend wake, and 2000-2099 BCD range.
