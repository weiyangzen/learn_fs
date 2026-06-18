# sources/distributed-fs/ceph-client/drivers/power/reset/odroid-go-ultra-poweroff.c

## Purpose
Odroid Go Ultra board-specific poweroff preparation driver.

## Important APIs, Types, and Functions
data structure with two PMIC regmaps, PMIC lookup helper, `odroid_go_ultra_poweroff_prepare()`, manual platform-device init/exit, and sys-off prepare handler.

## Control Flow
module init registers a singleton platform device/driver; probe finds RK817 and RK818 PMIC devices by compatible, stores regmaps, and registers a poweroff-prepare handler that writes PMIC bits needed before final shutdown.

## State and Persistence Behavior
global platform device pointer and PMIC references persist while module loaded; PMIC register writes persist into shutdown.

## Dependencies and Integration Points
ARCH_MESON/OF/I2C, regmap, sys-off prepare mode, board-specific PMIC compatibles.

## Risks and Edge Cases
board-specific singleton design; PMIC lookup by compatible can bind the wrong instance on unusual systems; preparation failure can compromise poweroff.

## Test Signals
Odroid Go Ultra DT, PMIC lookup failure/defer, prepare writes, module unload cleanup, and full poweroff.
