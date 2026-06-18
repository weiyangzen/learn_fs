# sources/distributed-fs/ceph-client/drivers/power/reset/as3722-poweroff.c

## Purpose
ams AS3722 PMIC poweroff child driver.

## Important APIs, Types, and Functions
`struct as3722_poweroff`, `as3722_pm_power_off()`, and `as3722_poweroff_probe()` update `AS3722_RESET_CONTROL_REG` through the parent MFD.

## Control Flow
probe requires parent OF node with `ams,system-power-controller`, stores parent driver data, and registers a default-priority poweroff sys-off handler; callback sets `AS3722_POWER_OFF`.

## State and Persistence Behavior
devm state is per platform child; PMIC reset-control bit persists in hardware for final shutdown.

## Dependencies and Integration Points
MFD AS3722, OF property, platform bus, sys-off API.

## Risks and Edge Cases
silently does nothing when the DT property is absent; assumes parent drvdata is valid; callback only logs PMIC write failure.

## Test Signals
probe with/without system-power-controller, regmap failure injection, and real PMIC poweroff.
