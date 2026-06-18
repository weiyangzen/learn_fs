# sources/distributed-fs/ceph-client/drivers/power/reset/axxia-reset.c

## Purpose
LSI Axxia syscon restart driver.

## Important APIs, Types, and Functions
`axxia_restart_handler()` and `axxia_reset_probe()` use a `syscon` phandle regmap and write critical-key, latch, efuse-status, and reset-control registers.

## Control Flow
probe resolves the syscon regmap and registers a restart sys-off handler at priority 128; handler unlocks writes, sets reset latch, clears efuse done, and requests system/chip reset.

## State and Persistence Behavior
no local persistent data beyond devm handler callback data; syscon register writes persist until reset.

## Dependencies and Integration Points
OF, syscon/regmap, platform driver, sys-off restart.

## Risks and Edge Cases
handler ignores intermediate regmap errors and always returns done; wrong syscon phandle can write unrelated registers.

## Test Signals
DT phandle validation, restart on Axxia hardware, and regmap error tracing.
