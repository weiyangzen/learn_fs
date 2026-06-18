# sources/distributed-fs/ceph-client/drivers/power/reset/tps65086-restart.c

## Purpose
TI TPS65086 PMIC restart driver.

## Important APIs, Types, and Functions
`tps65086_restart_notify()` and probe using parent `struct tps65086`.

## Control Flow
probe gets parent MFD data and registers high-priority restart; callback writes `TPS65086_FORCESHUTDN`, delays, and warns if still running.

## State and Persistence Behavior
parent PMIC pointer persists as callback data; PMIC force-shutdown bit persists into reset.

## Dependencies and Integration Points
MFD_TPS65086, regmap, platform IDs, sys-off restart.

## Risks and Edge Cases
parent drvdata is assumed valid; write failure logs but returns done; force-shutdown semantics may power-cycle rather than clean reset depending on board.

## Test Signals
platform child probe, regmap failure, restart behavior, and timeout warning.
