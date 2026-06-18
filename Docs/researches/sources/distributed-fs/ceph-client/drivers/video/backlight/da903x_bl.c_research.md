# sources/distributed-fs/ceph-client/drivers/video/backlight/da903x_bl.c

## Purpose
This platform driver exposes DA9030 and DA9034 PMIC WLED outputs as raw Linux backlights. It handles the different brightness ranges and enable mechanisms of the two PMIC variants.

## Important APIs, Types, and Functions
`struct da903x_backlight_data` caches the parent PMIC device, platform ID, and current brightness. `da903x_backlight_set()` is the main hardware path: DA9034 updates `DA9034_WLED_CONTROL1` and toggles `DA9034_WLED_BOOST_EN`, while DA9030 writes trim bits plus charge-pump enable to `DA9030_WLED_CONTROL`. `da903x_backlight_update_status()` forwards `backlight_get_brightness()`, and `get_brightness()` returns the cache.

## Control Flow
Probe validates `pdev->id` against DA9030/DA9034 WLED IDs, selects max brightness, applies optional DA9034 output-current platform data, registers a raw backlight named from `pdev->name`, sets initial brightness to the maximum, and calls `backlight_update_status()`. Runtime updates write brightness first and then enable or disable the relevant boost/charge-pump path based on transitions to or from zero.

## State and Persistence
Only `current_brightness` is tracked in memory. Hardware register state persists in the PMIC until overwritten, but the driver does not reread it after probe except through its own update path.

## Dependencies and Integration Points
The driver depends on the DA903x MFD register helpers (`da903x_update`, `da903x_write`, `da903x_set_bits`, `da903x_clr_bits`) and platform-device IDs from `linux/mfd/da903x.h`. It integrates with legacy board platform data for output current.

## Risks
The DA9034 output-current write is attempted without checking the return value. `get_brightness()` can report stale cached state if firmware or another driver changes WLED registers. Unsupported IDs fail probe, but no default case in `da903x_backlight_set()` reports an error if corrupted state reaches runtime.

## Test Signals
Exercise both PMIC IDs, max brightness selection, DA9034 boost enable/disable transitions, DA9030 charge-pump enable behavior, optional output-current platform data, suspend/resume through `BL_CORE_SUSPENDRESUME`, and I2C/MFD write failures.
