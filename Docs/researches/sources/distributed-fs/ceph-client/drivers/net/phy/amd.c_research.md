# sources/distributed-fs/ceph-client/drivers/net/phy/amd.c

## Purpose
Provides a small PHY driver for AMD AM79C874 and Altima AC101L PHYs, mainly to handle their interrupt status/control register.

## Important APIs, Types, and Functions
The driver registers two `struct phy_driver` entries with IDs `PHY_ID_AM79C874` and `PHY_ID_AC101L`. Important functions are `am79c_ack_interrupt`, `am79c_config_init`, `am79c_config_intr`, and `am79c_handle_interrupt`.

## Control Flow and State
Initialization is a no-op. Interrupt enable first acknowledges pending BMSR and vendor interrupt status, then writes link and autoneg-complete enables into register 17. Interrupt disable masks the register then acknowledges pending status. The ISR reads register 17 and triggers the PHY state machine only when link-down or autoneg-done status bits are present.

## Dependencies and Integration Points
Depends on basic Clause 22 phylib reads/writes, `MII_BMSR`, IRQ callbacks in `struct phy_driver`, and MDIO module matching. Generic phylib handles the actual link configuration and status behavior.

## Risks and Test Signals
Risks are limited but include wrong interrupt-mask polarity, losing an interrupt if BMSR/status read order is changed, and no special handling for chip errata outside interrupts. Test signals are compile coverage, probe/autoload by MDIO ID, interrupt-driven link-down and autoneg-complete events, and fallback polling behavior when interrupts are disabled.
