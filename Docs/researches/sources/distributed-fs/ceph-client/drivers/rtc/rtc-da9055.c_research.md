# sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9055.c

## Purpose
Dialog DA9055 PMIC RTC driver. It initializes PMIC RTC power/crystal modes, exposes time and alarm operations, handles alarm IRQs, and preserves alarm state across PM transitions.

## Important APIs, types, and functions
- `struct da9055_rtc` stores RTC device, parent PMIC pointer, and software `alarm_enable`.
- `da9055_rtc_enable_alarm()` updates `DA9055_RTC_ALM_EN` and mirrors the enabled state in software.
- Time/alarm helpers read/write PMIC register groups and decode masked year/month/day/hour/min/sec fields.
- `da9055_rtc_read_time()` first checks `DA9055_RTC_READ`; if not asserted it returns `-EBUSY`.
- `da9055_rtc_device_init()` enables RTC, 32 kHz crystal, power-down RTC mode, optional reset-mode behavior from platform data, and disables tick wake bits.
- Probe initializes hardware, detects preexisting alarm enable state, enables wakeup, registers RTC, and requests threaded `"ALM"` IRQ.
- PM callbacks disable alarm when it is not a wake source, re-enable it on resume/thaw/restore if previously active, and freeze disables it unconditionally.

## Control flow
Alarm IRQ disables the alarm before reporting `RTC_AF`. Setting an alarm disables first, writes fields, then re-enables. PM policy separates wake-capable alarms from ordinary alarms to avoid unwanted wakeups.

## State and persistence behavior
PMIC registers persist time/alarm and mode bits. Software `alarm_enable` mirrors desired alarm state across PM callbacks. Time range is constrained by PMIC year field but not explicitly assigned to `rtc->range_*` in this driver.

## Dependencies and integration points
Depends on DA9055 MFD core/register/platform-data headers, platform IRQ named `"ALM"`, RTC class, and PM callbacks.

## Risks
- Set-time lacks explicit year validation despite a limited PMIC year field.
- `alarm_enable` can diverge if register updates fail after partial state changes.
- `set_alarm()` always re-enables the alarm, ignoring `alrm->enabled`.
- Probe uses older `devm_rtc_device_register()` style and returns IRQ request errors only if request itself fails.

## Test signals
RTC_READ busy path, PM suspend/resume with and without wakeup, alarm IRQ one-shot behavior, platform reset mode, year boundary writes, and disabled-alarm `set_alarm()` semantics.
