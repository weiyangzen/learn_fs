# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cv1800.c

## Purpose
Sophgo CV1800 RTC platform driver. It exposes a syscon/regmap-backed seconds counter and alarm register as a 32-bit-range RTC.

## Important APIs, types, and functions
- `struct cv1800_rtc_priv` stores RTC device, parent regmap, enabled clock, and alarm IRQ.
- `cv1800_rtc_enabled()` checks `SEL_SEC_PULSE` in `SEC_PULSE_GEN`; `cv1800_rtc_enable()` selects internally generated second pulses.
- `cv1800_rtc_read_time()` reads `SEC_CNTR_VAL` and returns `-EINVAL` if not enabled.
- `cv1800_rtc_set_time()` writes `SET_SEC_CNTR_VAL`, triggers `SET_SEC_CNTR_TRIG`, mirrors seconds into `MACRO_RG_SET_T`, and enables the RTC.
- Alarm ops read/write `ALARM_TIME` and `ALARM_ENABLE`.
- `cv1800_rtc_irq_handler()` reports `RTC_AF` and disables the alarm.
- Probe gets parent syscon regmap and parent `"rtc"` clock, enables wakeup, requests a high-trigger alarm IRQ, sets `range_max = U32_MAX`, and registers the RTC.

## Control flow
The driver relies on the parent node regmap rather than mapping its own resource. Setting time also initializes persistent backup-domain macro state and enables internal second pulses.

## State and persistence behavior
Time, alarm, enable, and macro retention fields live in the parent RTC register block. Software state is minimal. Alarm IRQ is one-shot in practice because the handler writes `ALARM_ENABLE = 0`.

## Dependencies and integration points
Depends on parent MFD/syscon regmap, parent `"rtc"` clock, platform IRQ, RTC class, and wakeup support. Binds by platform device ID `"cv1800b-rtc"` with driver name `"sophgo-cv1800-rtc"`.

## Risks
- Regmap read/write return values are mostly ignored after probe, so bus/register failures may be silent.
- `alarm_irq_enable()` writes the raw `enabled` value rather than masking to bit 0.
- Range is 32-bit seconds, and alarm time is truncated to `u32` on read.
- Driver has no PM callbacks despite calling `device_init_wakeup()`.

## Test signals
Parent regmap/clock probe failures, read before enable returning `-EINVAL`, set/read time round trip, alarm IRQ one-shot behavior, and wakealarm exposure.
