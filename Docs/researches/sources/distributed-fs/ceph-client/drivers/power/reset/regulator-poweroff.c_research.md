# sources/distributed-fs/ceph-client/drivers/power/reset/regulator-poweroff.c

## Purpose
generic regulator-disable poweroff driver.

## Important APIs, Types, and Functions
`regulator_poweroff_do_poweroff()` and probe obtaining `cpu` regulator.

## Control Flow
probe gets the named regulator and registers poweroff; callback disables the regulator, waits up to three seconds, and warns if the system remains alive.

## State and Persistence Behavior
regulator handle is devm-managed; regulator enable state persists and should cut CPU/system power.

## Dependencies and Integration Points
OF, regulator consumer API, sys-off poweroff.

## Risks and Edge Cases
only appropriate when disabling the regulator really powers the board off; shared regulators can affect unexpected domains; failure to cut power leaves kernel running after regulator state change.

## Test Signals
DT supply lookup, regulator disable failure, timeout warning, and board poweroff.
