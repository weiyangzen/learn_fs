# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab-eoz9.c

## Purpose

`rtc-ab-eoz9.c` drives the Abracon AB-RTCMC-32.768kHz-EOZ9 I2C RTC. It provides BCD timekeeping, optional alarm/wakeup support, trickle charger configuration from device tree, voltage-validity checks, and optional hwmon temperature reporting.

## Important APIs, types, and functions

`struct abeoz9_rtc_data` stores the RTC device, regmap, and optional hwmon device. Key routines are `abeoz9_check_validity()`, `abeoz9_reset_validity()`, `abeoz9_rtc_get_time()`, `abeoz9_rtc_set_time()`, `abeoz9_rtc_read_alarm()`, `abeoz9_rtc_set_alarm()`, `abeoz9_rtc_alarm_irq_enable()`, `abeoz9_rtc_irq()`, `abeoz9_trickle_parse_dt()`, `abeoz9_rtc_setup()`, and `abeoz9_hwmon_register()`. The optional hwmon read path exposes temperature input/min/max.

## Control flow

Probe validates I2C functionality, creates an 8-bit regmap, allocates data, runs setup, allocates the RTC, sets range 2000-2099, initially clears `RTC_FEATURE_ALARM`, requests IRQ if supplied, sets or clears feature bits based on IRQ and `wakeup-source`, registers the RTC, and then registers hwmon when enabled. Time reads first reject invalid data when power-on or voltage-drop flags are set. Set time writes seven BCD registers and clears validity flags. Alarm set clears pending AF, writes seconds/minutes/hours/day fields with alarm-enable bits, and then toggles AIE.

## State and persistence behavior

Hardware persists calendar, alarm, control, EEPROM trickle/temperature-enable bits, validity flags, and interrupt flags. Software state is minimal. The setup path writes CTRL1, clears interrupt registers, and updates EEPROM bits every probe, so probe can alter chip configuration.

## Dependencies and integration points

The driver depends on I2C, regmap, BCD, bitfield helpers, OF compatible `"abracon,abeoz9"`, RTC class APIs, `wakeup-source` firmware property, and optional hwmon. Alarm support is exposed only with an IRQ or wakeup-source.

## Risks and edge cases

The hour decode tests `ABEOZ9_HOURS_PM` as if it selects 12-hour mode and then tests the same bit again for PM; that should be checked against the datasheet. `ABEOZ9_REG_EEPROM_MASK` is `GENMASK(8, 0)` even though registers are 8-bit, which may be harmless through regmap but is suspicious. `abeoz9_rtc_setup()` overwrites interrupt control and EEPROM fields at probe. `read_alarm()` fills only sec/min/hour/mday; the common RTC layer may need to complete missing calendar fields.

## Test signals

Validate power-on and voltage-low invalid time rejection, setting time clears validity flags, alarm IRQ reports and clears AF, no-IRQ systems hide alarm/update interrupt support as expected, trickle resistor values map correctly, hwmon temperature conversion is correct, and probe does not unexpectedly erase board-required EEPROM bits.
