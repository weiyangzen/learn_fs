# sources/distributed-fs/ceph-client/drivers/rtc/rtc-da9063.c

## Purpose
Dialog DA9063/DA9062 compatible PMIC RTC driver. It abstracts register differences across variants, exposes time/alarm operations, enables the RTC and crystal, and uses an optional ALARM IRQ as a wake IRQ.

## Important APIs, types, and functions
- `struct da9063_compatible_rtc_regmap` maps register addresses, masks, and alarm layout for DA9063 AD, DA9063 BB, and DA9062 AA.
- `struct da9063_compatible_rtc` stores RTC device, cached alarm time, parent regmap, selected config, and `rtc_sync` flag.
- `da9063_data_to_tm()` and `da9063_tm_to_data()` convert masked raw register arrays to/from `rtc_time`.
- `da9063_rtc_read_time()` bulk-reads count registers, requires the ready-to-read bit, and contains a synchronization workaround that can return cached alarm time when an alarm fired one second ahead.
- `da9063_rtc_set_time()` bulk-writes count registers.
- Alarm ops read/write variant-specific alarm layouts and toggle the alarm-on bit.
- `da9063_alarm_event()` disables alarm, marks `rtc_sync`, and reports `RTC_AF`.
- Probe selects config from OF/variant, enables RTC and 32 kHz oscillator, clears alarm/tick state, initializes cached alarm, sets minute-resolution feature for AD layout, requests optional threaded ALARM IRQ, configures wake IRQ, and registers RTC with range 2000-2063.

## Control flow
All register access goes through parent regmap and selected config. Alarm setup disables first, writes raw fields starting at the variant-specific offset, caches the programmed alarm time, then optionally enables. IRQ handling is one-shot.

## State and persistence behavior
PMIC registers persist time, alarm, enable, crystal, and event bits. Software caches the most recently programmed alarm and `rtc_sync` to compensate for hardware synchronization delay after an alarm event.

## Dependencies and integration points
Depends on DA9062/DA9063 MFD register definitions, OF match data, parent regmap, platform IRQ by name `"ALARM"`, `dev_pm_set_wake_irq()`, and RTC class.

## Risks
- Many masks/register layouts are variant-specific; wrong match data corrupts time/alarm fields.
- `regmap_update_bits()` in probe uses `DA9063_ALARM_STATUS_ALARM` directly in one place instead of the config status mask, so variant assumptions need testing.
- Optional IRQ absence clears the alarm feature; non-ENXIO errors abort probe.
- Synchronization workaround changes read-time behavior immediately after alarms.

## Test signals
Probe each variant, ready-to-read false path, range validation, minute-resolution feature on AD config, optional IRQ/no-IRQ feature flags, wake IRQ setup, alarm IRQ read-time synchronization, and regmap failure paths.
