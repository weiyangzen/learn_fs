# sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm860x.c

## Purpose

`rtc-88pm860x.c` drives the RTC block in Marvell 88PM860x PMICs. Like the 88PM80x driver, it represents wall time as a free-running 32-bit counter plus a writable base, and it adds optional VRTC calibration using PMIC measurement hardware.

## Important APIs, types, and functions

`struct pm860x_rtc_info` holds the parent chip, selected I2C client, RTC device, delayed calibration work, IRQ, and configured VRTC target. RTC operations include `pm860x_rtc_read_time()`, `pm860x_rtc_set_time()`, `pm860x_rtc_read_alarm()`, `pm860x_rtc_set_alarm()`, and `pm860x_rtc_alarm_irq_enable()`. `calibrate_vrtc_work()` periodically samples VRTC, compares against the configured target voltage, adjusts `PM8607_RTC_MISC1`, and disables measurement when converged.

## Control flow

Probe allocates state, selects the primary or companion I2C client based on chip ID, requests the alarm IRQ, programs page address registers for the base value, reads optional `marvell,88pm860x-vrtc`, registers the RTC with `range_max = U32_MAX`, enables XO clock selection, starts VRTC measurement and delayed calibration, and enables wakeup. Read time bulk-reads the four base bytes through page registers, reads the counter, adds them, and converts to `rtc_time`. Set time writes a new base. Alarm operations convert between base-relative expiry and absolute seconds while toggling alarm enable, wakeup, and status bits.

## State and persistence behavior

Hardware persists counter, base, alarm, control, and VRTC trim state inside the PMIC. Software persists only the delayed work item and the selected `vrtc` target while the driver is loaded. Remove cancels calibration work and disables VRTC measurement.

## Dependencies and integration points

The driver uses the 88PM860x MFD helpers (`pm860x_bulk_read`, `pm860x_set_bits`, page-register access), OF parsing, platform IRQs, RTC class APIs, delayed work, and PM sleep hooks. Suspend/resume toggles a wakeup flag in the parent chip when wakeup is enabled.

## Risks and edge cases

Several PMIC access helpers are used without checking all return values. VRTC calibration is compiled in unconditionally by a local `#define`, so probe always enables measurement and delayed work. Alarm math assumes the target time is representable relative to the stored base; past alarms can underflow into a large unsigned delta. Device tree parsing failure silently defaults `vrtc` to 0, implying 2.7 V.

## Test signals

Validate time set/read, alarm set/read/IRQ, suspend wake flag behavior, remove cancellation of calibration work, OF VRTC values, and PMIC register writes for XO and measurement enable. Long-running tests should confirm calibration converges and disables measurement.
