# sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9052.c

## Purpose
Dialog DA9052 PMIC RTC driver. It exposes PMIC count/alarm registers through RTC class operations and wires the PMIC alarm IRQ to `rtc_update_irq()`.

## Important APIs, types, and functions
- `struct da9052_rtc` stores RTC device and parent DA9052 MFD pointer.
- `da9052_rtc_enable_alarm()` toggles alarm-on and tick-on bits in `DA9052_ALARM_Y_REG`.
- `da9052_read_alarm()` and `da9052_rtc_read_time()` use repeated group reads until two consecutive register snapshots match, avoiding rollover races.
- `da9052_set_alarm()` rounds any nonzero seconds up to the next minute, then writes minute/hour/day/month/year alarm fields.
- `da9052_rtc_set_time()` validates the 2000-2063 year range and writes six count registers.
- Probe configures battery charging, disables tick alarm, initializes wakeup, allocates/registers RTC with range 2000-2063, and requests the DA9052 ALARM IRQ.

## Control flow
Read operations use double-read retry loops with 20 ms sleeps and five retries. Setting an alarm always disables the alarm, writes fields, and re-enables it. The IRQ handler only reports `RTC_AF`.

## State and persistence behavior
Time and alarm state persist in PMIC registers. Software does not cache alarm enabled state. Alarm resolution is effectively one minute for the AD register layout because seconds are forced to zero.

## Dependencies and integration points
Depends on DA9052 MFD register helpers, platform device child, RTC class, PM wake capability, and DA9052 IRQ registration.

## Risks
- `BUG_ON(rtc_tm->tm_sec)` after rounding is harsh for a driver path and assumes conversion cannot fail.
- Double-read loops can return `-EIO` under register rollover or bus instability.
- Battery charging setup writes a fixed `0xFE` without policy visible in this file.
- No remove/free for `da9052_request_irq()` is visible here, so ownership depends on the parent helper.

## Test signals
Repeated-read stabilization around rollovers, alarm second rounding, 2063 boundary validation, PMIC IRQ delivery, battery-charge register setup, and failed group read/write paths.
