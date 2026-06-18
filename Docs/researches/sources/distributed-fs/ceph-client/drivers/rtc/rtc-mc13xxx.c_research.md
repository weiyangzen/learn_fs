# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mc13xxx.c

Purpose: supports Freescale/NXP MC13xxx PMIC RTCs, using separate day and time-of-day registers plus PMIC IRQs for alarm and RTC reset detection.

Important APIs and types: `struct mc13xxx_rtc` stores the RTC device, parent `mc13xxx`, and validity flag. RTC callbacks include `mc13xxx_rtc_read_time()`, `mc13xxx_rtc_set_time()`, `mc13xxx_rtc_read_alarm()`, `mc13xxx_rtc_set_alarm()`, and `mc13xxx_rtc_alarm_irq_enable()`. IRQ handlers are `mc13xxx_rtc_alarm_handler()` and `mc13xxx_rtc_reset_handler()`.

Control flow: probe allocates RTC state, requests reset and time-of-day alarm IRQs under the parent lock, sets range to 15-bit days, and registers the RTC. Reads sample day, seconds, day until day is stable. Setting time invalidates an active alarm seconds register, writes seconds zero, writes days, writes seconds, restores alarm seconds, unmasks reset IRQ if this makes the RTC valid, and updates `valid`. Alarm set disables the alarm by writing an invalid seconds value, masks/unmasks the alarm IRQ, then writes alarm day and seconds.

State and persistence: PMIC registers store days, seconds, alarm day/seconds, and IRQ status. Software `valid` is cleared by RTC reset IRQ and restored after a successful set-time.

Dependencies and integration: MC13xxx MFD register and IRQ APIs, parent lock discipline, platform IDs for MC13783/MC13892/MC34708, RTC class, and PMIC IRQ status APIs.

Risks: all public operations return `-ENODATA` while invalid until time is set. Day/seconds split requires careful ordering to avoid false alarms; the driver explicitly invalidates alarm seconds during updates. Alarm read uses current day plus alarm seconds and may not represent the programmed alarm day register. Probe error cleanup frees both IRQs even if only one request succeeded.

Test signals: reset IRQ invalidation, set-time restoring validity, day rollover during read, alarm false-trigger prevention, invalid alarm seconds behavior, IRQ mask/unmask status, and 15-bit day range limit.
