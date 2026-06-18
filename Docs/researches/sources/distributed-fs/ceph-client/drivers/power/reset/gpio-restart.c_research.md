# sources/distributed-fs/ceph-client/drivers/power/reset/gpio-restart.c

## Purpose
generic GPIO-driven restart driver.

## Important APIs, Types, and Functions
`struct gpio_restart`, `gpio_restart_notify()`, and probe parse GPIO, priority, active/inactive delays, and open-source mode.

## Control Flow
probe configures GPIO output and registers a restart handler; callback toggles active/inactive/active with requested delays to trigger external reset circuitry.

## State and Persistence Behavior
GPIO descriptor and timing state are devm-managed; line level persists until reset.

## Dependencies and Integration Points
OF, GPIO descriptors, sys-off restart.

## Risks and Edge Cases
timing/polarity mistakes can fail reset; open-source handling depends on board pull-ups; callback assumes sleeping delays are acceptable in sys-off context.

## Test Signals
DT property combinations, active-low/open-source, priority ordering, and scope/logic-analyzer reset pulse tests.
