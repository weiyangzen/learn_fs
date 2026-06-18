# sources/distributed-fs/ceph-client/drivers/power/reset/atc260x-poweroff.c

## Purpose
Actions Semi ATC260x PMIC poweroff and restart driver.

## Important APIs, Types, and Functions
`struct atc260x_pwrc`, chip-specific `atc2603c_do_poweroff()`/`atc2609a_do_poweroff()`, init helpers, and sys-off callbacks.

## Control Flow
probe obtains parent ATC260x/regmap, selects chip-specific function and initialization, registers default poweroff and restart handlers; callbacks program PMU system-control bits differently for shutdown and restart.

## State and Persistence Behavior
driver state is devm-managed; PMIC PMU control bits persist and drive final power state.

## Dependencies and Integration Points
MFD_ATC260X, regmap, platform bus, sys-off API.

## Risks and Edge Cases
chip-type switch must stay aligned with MFD enum; callbacks return `NOTIFY_BAD` on write errors but final state may be partially programmed; init changes wake/power behavior before handlers are used.

## Test Signals
probe each chip type, register-write failure injection, restart versus poweroff PMU bit sequences, and real board shutdown.
