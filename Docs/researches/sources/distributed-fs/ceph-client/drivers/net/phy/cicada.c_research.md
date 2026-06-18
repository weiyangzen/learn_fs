# sources/distributed-fs/ceph-client/drivers/net/phy/cicada.c

## Purpose
`cicada.c` is a legacy Cicada/Vitesse Cis8201/Cis8204 PHY driver. It performs basic extended-control initialization and implements vendor interrupt mask/status handling for link, speed, and duplex changes.

## Important APIs, Types, And Functions
The file defines Cicada extended control, interrupt mask/status, and auxiliary status register constants. `cis820x_config_init()` writes initial values to `MII_CIS8201_AUX_CONSTAT` and `MII_CIS8201_EXT_CON1`. `cis820x_ack_interrupt()` clears pending status by reading `MII_CIS8201_ISTAT`. `cis820x_config_intr()` enables or disables the interrupt mask. `cis820x_handle_interrupt()` triggers phylib on speed/link/duplex interrupt status.

## Control Flow
Initialization writes vendor defaults and returns the first error. When enabling interrupts, the driver acknowledges pending status first and writes `MII_CIS8201_IMASK_MASK`; when disabling, it writes zero to the mask register and then acknowledges. The IRQ handler reads status, treats any of the speed/link/duplex status bits as actionable, and calls `phy_trigger_machine()`.

## State And Persistence
There is no private state. Runtime state is only PHY register configuration and phylib link state.

## Dependencies And Integration Points
The driver depends on phylib and standard module/interrupt headers. It registers two PHY IDs through `module_phy_driver()`. Generic PHY code handles autonegotiation and link status outside the vendor interrupt/init paths.

## Risks And Edge Cases
The mask/status register naming is easy to confuse because the same high bits are used in mask and status definitions. The driver has no suspend/resume callbacks and no explicit reset handling. It includes many legacy headers that are not functionally used.

## Test Signals
Test Cis8201 and Cis8204 MDIO IDs, initialization writes, interrupt enable/disable ordering, and IRQ behavior for link, speed, and duplex changes. Polling mode should fall back to generic PHY status.
