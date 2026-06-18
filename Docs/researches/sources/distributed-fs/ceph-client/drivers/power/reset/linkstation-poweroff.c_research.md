# sources/distributed-fs/ceph-client/drivers/power/reset/linkstation-poweroff.c

## Purpose
Buffalo LinkStation PHY-based poweroff driver.

## Important APIs, Types, and Functions
MDIO/PHY lookup helpers, GPIO-like PHY output programming, and poweroff handler that manipulates Ethernet PHY output for WoL-compatible shutdown.

## Control Flow
probe locates the configured PHY through OF MDIO/PHYLIB, configures output state, and registers poweroff; callback writes PHY registers to signal board power controller.

## State and Persistence Behavior
state holds PHY device and output bit information; PHY register state persists across shutdown and may enable wake-on-LAN behavior.

## Dependencies and Integration Points
ARCH_MVEBU/OF_MDIO/PHYLIB, sys-off poweroff, DT PHY references.

## Risks and Edge Cases
depends on board-specific PHY wiring; MDIO failures during late poweroff can leave system on; shared PHY configuration can interact with network driver state.

## Test Signals
LS421D/E DTs, PHY lookup failure, WoL behavior, MDIO error injection, and physical shutdown.
