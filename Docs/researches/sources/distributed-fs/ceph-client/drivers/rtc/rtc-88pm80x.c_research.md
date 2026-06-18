# sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm80x.c

## Purpose

`rtc-88pm80x.c` is the Marvell 88PM80x PMIC RTC driver. It exposes timekeeping through the RTC class using a 32-bit free-running counter plus a writable base stored in PMIC RTC registers, and supports a single alarm interrupt with wake capability.

## Important APIs, types, and functions

`struct pm80x_rtc_info` stores the parent MFD chip, regmap, RTC device, platform device, and IRQ. The `rtc_class_ops` methods are `pm80x_rtc_read_time()`, `pm80x_rtc_set_time()`, `pm80x_rtc_read_alarm()`, `pm80x_rtc_set_alarm()`, and `pm80x_rtc_alarm_irq_enable()`. `rtc_next_alarm_time()` maps hardware's time-of-day alarm style to the next occurrence within 24 hours. `rtc_update_handler()` acknowledges PMIC alarm bits and reports `RTC_AF`.

## Control flow

Probe validates platform data or device tree, gets the MFD regmap and IRQ, allocates the RTC, requests the PMIC IRQ through `pm80x_request_irq()`, sets `range_max = U32_MAX`, registers the RTC, selects the internal XO for power-down free running, and enables device wakeup. Reading time loads the writable base from `EXPIRE2_*`, reads the counter, adds them, and converts seconds to `rtc_time`. Setting time computes `base = requested - counter` and writes it back. Alarm programming disables alarm, computes current base and counter, normalizes requested time to the next daily occurrence, writes `EXPIRE1_*`, and updates alarm/clear/wakeup bits.

## State and persistence behavior

Persistent state is the PMIC counter, base registers, alarm compare registers, and `PM800_RTC_CONTROL` bits. Software state is limited to the per-device info struct and wake configuration. The base register makes wall-clock time survive as long as the PMIC backup domain and counter remain valid.

## Dependencies and integration points

The driver depends on the 88PM80x MFD core, `linux/regmap.h`, `linux/mfd/88pm80x.h`, platform data for `rtc_wakeup`, and RTC class APIs. PM suspend/resume delegates to `pm80x_dev_suspend()` and `pm80x_dev_resume()`.

## Risks and edge cases

Most `regmap_raw_read()` and write calls ignore return values, so bus errors may be reported as valid zero or stale times. Alarm setting only schedules the next occurrence of the requested hour/min/sec within 24 hours and does not preserve arbitrary date alarms. The remove path frees the PMIC IRQ manually, so probe failure paths must stay aligned with successful request points. Base plus counter arithmetic is 32-bit range-limited.

## Test signals

Test probe with and without platform data/OF node, read/set time across counter rollover boundaries, alarm enabled and disabled paths, wake from suspend, PMIC alarm and wakeup bit clearing, and failure injection for regmap operations if practical. Confirm the internal XO bit is set after registration.
