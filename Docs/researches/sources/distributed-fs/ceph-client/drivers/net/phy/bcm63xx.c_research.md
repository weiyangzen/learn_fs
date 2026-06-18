# sources/distributed-fs/ceph-client/drivers/net/phy/bcm63xx.c

## Purpose
`bcm63xx.c` is a small driver for Broadcom 63xx SoC internal PHYs. Its main job is to initialize the integrated PHY interrupt register, advertise pause support within documented limits, and let the shared Broadcom interrupt handler drive phylib state changes.

## Important APIs, Types, And Functions
The file defines the BCM63xx interrupt register `MII_BCM63XX_IR` and bits for global enable, duplex, speed, link, and global mask. `bcm63xx_config_init()` programs supported pause and initial interrupt mask/event bits. `bcm63xx_config_intr()` toggles the global mask based on `phydev->interrupts`. The two `phy_driver` entries match two OUI variants of the same internal PHY and use `bcm_phy_handle_interrupt()`.

## Control Flow
On init the driver sets `ETHTOOL_LINK_MODE_Pause_BIT` but deliberately avoids setting asymmetric pause because the datasheet marks that bit read-only. It globally masks interrupts, then writes a register value that globally enables interrupts while unmasking duplex, speed, and link events. When phylib enables interrupts, pending Broadcom interrupt status is acknowledged with `bcm_phy_ack_intr()` before clearing the global mask; disabling sets the global mask first and then acknowledges pending state.

## State And Persistence
The driver keeps no private state. Its state is entirely the PHY interrupt register and phylib fields such as supported link modes. Register state is reset-bound and not persisted outside hardware.

## Dependencies And Integration Points
It depends on phylib and shared helpers from `bcm-phy-lib.h`. It registers through `module_phy_driver()` and supports two MDIO IDs. Link handling is delegated to `bcm_phy_handle_interrupt()` and generic PHY functionality.

## Risks And Edge Cases
The interrupt register combines enable, mask, and status bits with vendor-specific polarity. Incorrect ordering can lose pending link changes. Since no suspend/resume or reset callbacks are provided, platform reset sequencing relies on generic phylib behavior and the MAC/MDIO integration.

## Test Signals
Test by probing both ID variants, confirming initial pause support, checking that link/speed/duplex interrupts trigger `phy_trigger_machine()` through the shared handler, and verifying polling fallback still reads link normally.
