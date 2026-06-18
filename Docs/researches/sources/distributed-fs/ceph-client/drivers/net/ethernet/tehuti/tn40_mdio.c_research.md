# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_mdio.c

## Purpose
This file implements the TN40xx clause 45 MDIO bus backend and software-node registration for AQR105-based cards. It gives phylib/phylink a normal `mii_bus` interface even though the PHY is reached through TN40 MMIO MDIO registers, and it advertises AQR105 PHY firmware `tehuti/aqr105-tn40xx.cld`.

## Important APIs, Types, and Functions
Public functions are `tn40_mdiobus_init` and `tn40_swnodes_cleanup`. Internal helpers include `tn40_mdio_set_speed`, `tn40_mdio_wait_nobusy`, `tn40_mdio_read`, `tn40_mdio_write`, `tn40_mdio_read_c45`, `tn40_mdio_write_c45`, and `tn40_swnodes_register`. MDIO command encoding uses `TN40_MDIO_CMD_VAL`, `TN40_MDIO_CMD_READ`, device/address masks, and busy/error field helpers from `tn40_regs.h`.

## Control Flow and State
`tn40_mdiobus_init` allocates a devm MDIO bus, assigns clause 45 read/write callbacks, stores it in `priv->mdio`, conditionally registers software nodes for TN9510/AQR105 cards, configures MDIO speed to 6 MHz, and registers the bus. Reads wait for non-busy, write device/port and register address, issue a read command, wait again, and return low 16 bits of `TN40_REG_MDIO_DATA`. Writes perform the same address setup, write data, wait for completion, and fail if the MDIO read-error bit is set. Cleanup removes firmware-node references only for cards that installed software nodes.

## Dependencies and Integration Points
The file depends on `tn40.h`, Linux PCI, netdevice, phylink, software-node, and MDIO APIs. The software node describes a child `ethernet-phy@1` with compatible `ethernet-phy-id03a1.b4a3`, `reg = 1`, and firmware name, enabling phylib to discover and configure the PHY without firmware/DT/ACPI platform description.

## Risks and Test Signals
Risks include atomic polling timeouts, cleanup ordering for software nodes, hard-coded PHY address/compatible, AQR105-only assumptions tied to PCI device ID, and MDIO error reporting only after writes. Tests should cover MDIO read/write timeouts, successful PHY discovery, firmware-name propagation, probe failure after software-node registration, remove cleanup, and TN9510 versus non-TN9510 behavior.
