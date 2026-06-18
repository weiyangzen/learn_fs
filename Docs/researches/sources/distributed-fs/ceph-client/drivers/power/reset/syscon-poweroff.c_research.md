# sources/distributed-fs/ceph-client/drivers/power/reset/syscon-poweroff.c

## Purpose
generic syscon/regmap poweroff driver.

## Important APIs, Types, and Functions
`struct syscon_poweroff_data`, `syscon_poweroff()`, and probe parsing `regmap`, `offset`, `value`, and `mask`.

## Control Flow
probe resolves regmap by phandle or parent syscon, parses offset/value/mask with legacy mask-as-value fallback, and registers a poweroff handler; callback updates the register then delays/warns if still alive.

## State and Persistence Behavior
driver data persists via devm; target syscon bits persist into shutdown.

## Dependencies and Integration Points
OF, MFD_SYSCON, regmap, sys-off poweroff.

## Risks and Edge Cases
binding mistakes can write wrong syscon bits; legacy fallback semantics are subtle; no success confirmation except actual power loss.

## Test Signals
DT variants with value/mask/legacy mask, parent versus phandle regmap, write failure injection, and poweroff.
