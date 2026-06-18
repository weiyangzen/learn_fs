# sources/distributed-fs/ceph-client/drivers/power/reset/spacemit-p1-reboot.c

## Purpose
SpacemiT P1 PMIC reboot/poweroff driver.

## Important APIs, Types, and Functions
poweroff/restart sys-off callbacks set `PWR_CTRL2_SHUTDOWN` or `PWR_CTRL2_RST` through parent regmap.

## Control Flow
probe gets parent regmap and registers both poweroff and restart handlers using helper wrappers; callbacks set the requested bit and return notifier status.

## State and Persistence Behavior
regmap callback data is devm-managed; PMIC control bits persist and should trigger final action.

## Dependencies and Integration Points
MFD_SPACEMIT_P1, regmap, platform IDs, sys-off helpers.

## Risks and Edge Cases
assumes parent regmap exists; bit definitions must match PMIC revision; write failures prevent handler success but may leave partial state.

## Test Signals
platform ID probe, poweroff/restart bits, regmap failure injection, and real PMIC behavior.
