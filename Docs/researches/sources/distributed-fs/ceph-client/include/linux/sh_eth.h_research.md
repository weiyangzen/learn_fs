# sources/distributed-fs/ceph-client/include/linux/sh_eth.h

## Purpose

`sh_eth.h` defines platform data for the SuperH/Renesas Ethernet driver. It supplies PHY addressing, PHY interrupt, PHY interface mode, optional MDIO gate control, MAC address, and link-polarity flags.

## Important APIs, Types, And Functions

The only type is `struct sh_eth_plat_data`. Fields are `phy`, `phy_irq`, `phy_interface`, `set_mdio_gate`, `mac_addr[ETH_ALEN]`, `no_ether_link`, and `ether_link_active_low`.

## Control Flow

No functions are implemented. Driver probe consumes this platform data to configure PHY attachment, MDIO access, MAC address setup, and link GPIO/polarity handling. If `set_mdio_gate` is supplied, driver code can open or close an MDIO gate around bus transactions.

## State And Persistence

The platform data is static board or firmware state. Runtime link and PHY state are owned by the Ethernet driver and PHY subsystem. The MAC address may become the persistent network identity for the interface if accepted by the driver.

## Dependencies And Integration Points

Dependencies include PHY interface definitions and Ethernet address length. Integration points are the SH Ethernet MAC driver, phylib, MDIO bus access, board files, and platform data instantiation.

## Risks And Test Signals

Risks include wrong PHY address or IRQ, mismatched PHY interface mode, invalid MAC address, and incorrect active-low link interpretation. Test signals include probe and PHY attach, MDIO reads/writes through gate control, link up/down changes, MAC address reporting, and traffic tests across each supported PHY interface.
