# sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl12022.c

Purpose: supports the Intersil/Renesas ISL12022 I2C RTC with calendar, alarm, battery voltage reporting, optional IRQ, fixed 32 kHz clock output, and hwmon temperature exposure.

Important APIs/types/functions: `struct isl12022` stores RTC, regmap, IRQ, and IRQ-enabled state. `isl12022_rtc_read_time()`/`set_time()` use regmap bulk operations and write-enable bit `WRTC`. `isl12022_rtc_read_alarm()`/`set_alarm()` program six alarm registers whose MSBs enable matching. `isl12022_rtc_ioctl()` implements `RTC_VL_READ`. `isl12022_register_clock()`, `isl12022_set_trip_levels()`, and `isl12022_hwmon_register()` integrate clock, battery thresholds, and temperature.

Control flow: probe validates I2C, creates regmap, registers/possibly disables clock output, configures battery trip thresholds, registers hwmon, allocates RTC, sets 2000-2099 range, configures IRQ if present, and registers the RTC. Alarm setup disables past alarms, writes a temporary nonmatching weekday to avoid false matches, then bulk-writes all alarm fields. IRQ reads SR, reports alarm events, and relies on configured automatic reset/single-event mode.

State and persistence: time, alarm, temperature, status, battery thresholds, and clock output are chip state. `irq_enabled` mirrors Linux IRQ masking.

Dependencies and integration: depends on I2C, regmap, RTC, hwmon, common clock, OF properties (`#clock-cells`, `isil,battery-trip-levels-microvolt`), and threaded IRQs.

Risks and test signals: `alarm_irq_enable()` masks/unmasks the Linux IRQ rather than changing chip alarm bits; setup initially leaves IRQ enabled. Temperature conversion uses raw 10-bit half-Kelvin units from little-endian registers. Test past/future alarm programming, IRQ masking, voltage ioctl, trip-level mapping, F_OUT behavior with/without clock provider, hwmon enable failure, and 2000/2099 range limits.
