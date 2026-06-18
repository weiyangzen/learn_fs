# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-realview.c

## Purpose
Applies ARM RealView platform syscon configuration before initializing the GIC on TC11MP/EB11MP systems.

## Important APIs, Types, and Functions
`syscon_pldset_of_match[]` selects the PLD control register offset by syscon compatible. `realview_gic_of_init()` unlocks the system control block, programs interrupt mode, relocks it, and then calls `gic_of_init()`.

## Control Flow
During irqchip init, the driver finds a matching syscon node, obtains its regmap, writes the unlock value, updates PLD interrupt mode bits to "new no DCC", locks the syscon, logs the configuration, and delegates normal GIC initialization to the common ARM GIC driver.

## State and Persistence
Persistent state is the syscon PLD interrupt mode field. No driver-private state remains after init.

## Dependencies and Integration Points
Depends on OF matching, syscon/regmap, ARM GIC OF init, and RealView-specific system-control register definitions. Registered for `arm,tc11mp-gic` and `arm,eb11mp-gic`.

## Risks and Test Signals
Risks include missing/incorrect syscon compatible, wrong PLD offset for board revision, and failure to unlock/relock the syscon. Test signals are the RealView mode setup log, successful subsequent GIC init, and functional interrupt routing without legacy DCC mode.
