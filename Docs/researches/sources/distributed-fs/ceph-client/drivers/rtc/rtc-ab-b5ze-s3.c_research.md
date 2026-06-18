# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab-b5ze-s3.c

## Purpose

`rtc-ab-b5ze-s3.c` drives the Abracon AB-RTCMC-32.768kHz-B5ZE-S3 I2C RTC/alarm chip. It supports BCD calendar time, alarm interrupts, battery-low detection, oscillator-integrity checking, and a hybrid alarm implementation that uses Timer A for short second-precision alarms and normal alarm registers for longer minute-granularity alarms.

## Important APIs, types, and functions

`struct abb5zes3_rtc_data` stores the RTC device, regmap, IRQ, battery-low state, and `timer_alarm` selector. Important helpers include `abb5zes3_i2c_validate_chip()`, `_abb5zes3_rtc_read_time()`, `abb5zes3_rtc_set_time()`, `_abb5zes3_rtc_read_timer()`, `_abb5zes3_rtc_read_alarm()`, `_abb5zes3_rtc_set_timer()`, `_abb5zes3_rtc_set_alarm()`, `abb5zes3_rtc_set_alarm()`, `abb5zes3_rtc_check_setup()`, and `_abb5zes3_rtc_interrupt()`. `rtc_ops` wires read/set time, read/set alarm, and alarm IRQ enable.

## Control flow

Probe checks I2C capabilities, initializes regmap, validates fixed-zero register bits, allocates driver state, runs setup, allocates the RTC, optionally requests a shared threaded IRQ, configures wakeup, sets range 2000-2099, enables battery-low IRQ if safe, and registers. Setup disables clockout and timer outputs, disables existing alarms, enables RTC 24-hour mode, clears interrupt status, enables battery detection, and reports oscillator or battery failures. Alarm set first disables both normal alarm and timer interrupt. If the target is within 240 seconds and in the future, Timer A is programmed at 1 Hz; otherwise normal minute/date alarm registers are used.

## State and persistence behavior

Hardware persists BCD calendar registers, normal alarm registers, Timer A settings, control bits, oscillator status, and battery flags. Software state `timer_alarm` is required to know whether `read_alarm()` and `alarm_irq_enable()` should address Timer A or alarm registers. A driver reload can lose that distinction if hardware still has a timer-based alarm.

## Dependencies and integration points

The driver depends on I2C, regmap, BCD helpers, IRQ threading, OF compatible `"abracon,abb5zes3"`, RTC class APIs, and PM sleep wake IRQ enable/disable. It uses `device_init_wakeup()` only when an IRQ is available.

## Risks and edge cases

There appears to be a setup bug: the code attempts to disable alarm field matching by calling `regmap_update_bits()` on `ABB5ZES3_REG_CTRL2` with alarm-register enable-bit masks; those masks belong to alarm registers `0x0a` through `0x0d`, not CTRL2. Short-alarm state depends on volatile `timer_alarm`. Normal alarms have no seconds field and are limited to about one month. The IRQ handler disables battery-low interrupts because the flag cannot be cleared until battery replacement. Time reads return `-ENODATA` if oscillator integrity failed.

## Test signals

Test chip validation masks, set/read time in 24-hour mode, oscillator-stop reporting, battery-low startup and IRQ handling, normal alarms beyond 240 seconds, timer alarms under 240 seconds, suspend wake, and driver reload with a pending Timer A alarm. Static review should verify the alarm-disable register address in setup.
