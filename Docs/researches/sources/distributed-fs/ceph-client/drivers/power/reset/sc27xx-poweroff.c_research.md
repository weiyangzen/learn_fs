# sources/distributed-fs/ceph-client/drivers/power/reset/sc27xx-poweroff.c

## Purpose
Spreadtrum/Unisoc SC27xx PMIC poweroff driver.

## Important APIs, Types, and Functions
global regmap, syscore shutdown hook, `sc27xx_poweroff_do_poweroff()`, and probe.

## Control Flow
probe obtains parent regmap, installs `pm_power_off`, and registers a syscore op; syscore shutdown prepares for late poweroff, and callback writes sleep-control and hardware power-down bits.

## State and Persistence Behavior
global regmap and poweroff hook persist; PMIC bits persist into final shutdown.

## Dependencies and Integration Points
MFD_SC27XX_PMIC, regmap, syscore, legacy poweroff.

## Risks and Edge Cases
global singleton rejects second instance; comments note CPU shutdown to avoid regmap/SPI mutex races, so late ordering is delicate; no remove cleanup of global hook.

## Test Signals
SC27xx board poweroff, duplicate probe, regmap absence, syscore ordering, and PMIC write trace.
