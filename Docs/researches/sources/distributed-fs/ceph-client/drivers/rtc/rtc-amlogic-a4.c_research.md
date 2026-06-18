# sources/distributed-fs/ceph-client/drivers/rtc/rtc-amlogic-a4.c

## Purpose

`rtc-amlogic-a4.c` is the Amlogic A4/A5 RTC driver. It supports a 32-bit seconds counter, alarm0, digital second adjustment through the RTC offset API, optional Gray-coded counter storage, and clock source initialization from either 32 kHz or 24 MHz oscillators.

## Important APIs, types, and functions

`struct aml_rtc_config` flags SoC differences, currently `gray_stored` for A4. `struct aml_rtc_data` stores regmap, RTC device, IRQ, oscillator/system clocks, enabled state, and config. RTC callbacks are `aml_rtc_read_time()`, `aml_rtc_set_time()`, `aml_rtc_read_alarm()`, `aml_rtc_set_alarm()`, `aml_rtc_alarm_enable()`, `aml_rtc_read_offset()`, and `aml_rtc_set_offset()`. `gray_to_binary()` and `binary_to_gray()` translate counter storage for A4. `aml_rtc_init()` configures oscillator selection and masks alarms.

## Control flow

Probe maps MMIO through regmap, gets the alarm IRQ, validates the `"osc"` clock rate, enables `"sys"` clock, initializes the hardware, enables wakeup, requests the IRQ, sets range `0..U32_MAX`, and registers the RTC. If the RTC is disabled, read paths fail but `set_time()` first enables it and writes the initial counter. Alarm set enables alarm and unmasks interrupt before writing the alarm register. The IRQ handler clears the alarm register and interrupt status, then reports `RTC_AF`.

## State and persistence behavior

Hardware persists the RTC enable bit, counter, alarm register, oscillator selection, 24 MHz divider programming, interrupt mask/clear state, and second adjustment register. Software caches whether the RTC was enabled at initialization and the SoC config. Offset adjustments persist in `RTC_SEC_ADJUST_REG`.

## Dependencies and integration points

The driver uses platform MMIO, regmap, common clocks, OF match data for `"amlogic,a4-rtc"` and `"amlogic,a5-rtc"`, RTC class APIs, and PM sleep wake IRQ enable/disable.

## Risks and edge cases

`FIELD_GET(RTC_ADJ_VALID, reg_val)` uses a single-bit mask with the generic bitfield macro; this works if mask shape is accepted but is worth static checking. `aml_rtc_set_alarm()` ignores `alarm->enabled` and always enables/unmasks before programming; disable is handled only through `alarm_irq_enable()`. Offset calculation divides by `abs(offset)` and accepts only values that map into the 19-bit match counter. Disabled hardware returns `-EINVAL` on reads until time is set.

## Test signals

Test A4 Gray-coded and A5 binary modes, both oscillator rates, first `set_time()` enabling a disabled RTC, alarm set/read/disable/IRQ clear, suspend wake, offset read/set for positive, negative, zero, too-large, and non-divisor values, and register state after `aml_rtc_init()`.
