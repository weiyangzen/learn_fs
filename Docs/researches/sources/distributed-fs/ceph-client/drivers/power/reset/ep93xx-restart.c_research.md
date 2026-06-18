# sources/distributed-fs/ceph-client/drivers/power/reset/ep93xx-restart.c

## Purpose
Cirrus EP93xx restart driver using syscon auxiliary-device glue.

## Important APIs, Types, and Functions
auxiliary probe state, restart handler, syscon regmap writes to device configuration and software-lock registers.

## Control Flow
the syscon MFD/auxiliary path instantiates the restart driver; probe registers restart, and callback writes the EP93xx unlock/key sequence to request software reset.

## State and Persistence Behavior
state is device-managed; reset request registers persist until reset.

## Dependencies and Integration Points
MFD_SYSCON, auxiliary bus, sys-off/restart, EP93xx architecture defaults.

## Risks and Edge Cases
depends on correct auxiliary creation and register offsets; restart writes are irreversible and lightly checked.

## Test Signals
EP93xx compile/probe, auxiliary binding, restart sequence trace, and reset failure logging.
