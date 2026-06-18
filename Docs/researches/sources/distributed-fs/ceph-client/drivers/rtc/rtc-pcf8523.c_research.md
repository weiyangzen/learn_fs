# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8523.c

Purpose: implements an I2C RTC driver for NXP PCF8523 and Micro Crystal RV8523 devices, including timekeeping, minute-resolution alarms, backup-switch mode reporting/setting, voltage-low reporting, oscillator offset correction, crystal load selection, and wake IRQ support.

Important APIs/types/functions: `struct pcf8523` stores the `rtc_device` and regmap. `pcf8523_rtc_read_time()` reads control and date registers and rejects STOP or oscillator-stop state; `pcf8523_rtc_set_time()` stops the clock, overwrites the OS bit while writing BCD time, and restarts. `pcf8523_rtc_read_alarm()`, `pcf8523_rtc_set_alarm()`, and `pcf8523_irq_enable()` handle minute/day alarm registers. `pcf8523_param_get/set()` map RTC backup-switch modes to `CONTROL3.PM`. `pcf8523_rtc_ioctl()` reports backup-low and invalid-time flags. `pcf8523_rtc_read_offset/set_offset()` implement two-mode offset calibration.

Control flow: probe checks I2C capability, allocates regmap and RTC, loads crystal capacitance from firmware, handles standby mode after oscillator stop, sets RTC operations and feature flags, configures timer/clockout control if an IRQ exists, requests a shared threaded IRQ, enables wake IRQ, marks the device wake capable when IRQ or `wakeup-source` is present, and registers the RTC.

State and persistence: time, alarm, offset, oscillator-stop, battery-low/switch-over, and power-management mode persist in chip registers. The driver keeps only regmap/RTC pointers in memory. Setting time clears the oscillator-stop bit by rewriting seconds.

Dependencies and integration: uses I2C, regmap, RTC class ops, `rtc_param` backup-switch API, PM wake IRQ, OF properties, BCD helpers, and IRQ threading. The alarm feature has minute resolution and no update interrupt.

Risks: the alarm programming buffer is declared as five bytes but only four alarm registers are meaningful, making write length worth checking against device docs. `pcf8523_rtc_set_alarm()` writes `CONTROL2` as zero, clearing more than only AF on future variants. Offset write clamps instead of returning range errors, so callers may not know an exact correction was not representable. Test signals include STOP/OS invalid reads, standby exit on probe, backup-switch mode round trips, IRQ alarm pending/clear behavior, wake suspend/resume, offset extremes, and crystal load defaults.
