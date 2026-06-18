# sources/distributed-fs/ceph-client/drivers/input/misc/sc27xx-vibra.c

## Purpose
`sc27xx-vibra.c` exposes Spreadtrum/Unisoc SC27xx PMIC vibrator control as a memless force-feedback rumble device. It turns PMIC LDO power-down bits on or off based on rumble strength and performs variant-specific initialization.

## Important APIs, Types, and Functions
`struct sc27xx_vibra_data` describes per-compatible bit masks. `struct vibra_info` stores input, work, regmap, data, base register, strength, and enabled flag. `sc27xx_vibra_set()` clears or sets LDO power-down and sleep power-down bits. `sc27xx_vibra_hw_init()` clears current-drive calibration bits for variants that need it. `sc27xx_vibra_play()` stores weak rumble magnitude and schedules work.

## Control Flow
Probe gets match data, parent regmap, base register from `reg`, allocates input, initializes hardware, creates a memless `FF_RUMBLE` input device, and registers it. Playback stores the weak magnitude and schedules work. The worker enables hardware only when strength is nonzero and currently disabled, or disables it when strength becomes zero and currently enabled. Close cancels work and disables if needed.

## State and Persistence Behavior
`strength` and `enabled` are persistent driver state. PMIC power-down and calibration bits persist in registers. The driver does not scale amplitude; strength is only on/off. Hardware is left disabled on close but not otherwise automatically on remove unless input close has run.

## Dependencies and Integration Points
It depends on parent PMIC regmap, OF compatibles `sprd,sc2721-vibrator`, `sprd,sc2730-vibrator`, and `sprd,sc2731-vibrator`, input FF core, workqueues, and `reg` property for the base address.

## Risks and Edge Cases
Only weak rumble magnitude is used, ignoring strong magnitude. Regmap update return values in `sc27xx_vibra_set()` are ignored, so state may claim enabled despite failed writes. No suspend/resume handling is present. Missing or wrong `reg` property fails probe. Strength changes are not protected by a mutex against close/work races.

## Test Signals
Test each compatible's bit masks, base-register parsing, weak/strong rumble behavior, zero stop, regmap failure injection, close while active, repeated enable/disable cycles, and suspend/resume on systems using this device.
