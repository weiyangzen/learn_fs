# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_pci_mdio.c

## Purpose
Provides a PCI driver for standalone ENETC/NETC central external MDIO controllers and enables/disables the LS1028A ERR050089 static-key workaround for affected devices.

## Important APIs, Types, and Functions
Important functions are `enetc_pci_mdio_probe`, `enetc_pci_mdio_remove`, `enetc_emdio_enable_err050089`, and `enetc_emdio_disable_err050089`. It defines the exported static key `enetc_has_err050089` and matches Freescale ENETC MDIO plus NETC EMDIO PCI IDs.

## Control Flow
Probe maps BAR0, allocates an `enetc_hw`, allocates an MDIO bus with `enetc_mdio_priv`, assigns Clause 22/45 read/write callbacks, performs FLR, enables PCI memory access, requests the BAR, increments the erratum static key for affected ENETC MDIO devices, registers the OF MDIO bus, and stores the bus as drvdata. Remove unregisters the bus, decrements the workaround key, unmaps registers, releases the region, and disables the PCI device.

## State and Persistence
State includes PCI BAR mapping, MDIO bus registration, `mdio_priv->mdio_base = ENETC_EMDIO_BASE`, and the global static branch controlling erratum locking in `enetc_hw.h`. Hardware state is reset by FLR and later configured by MDIO transactions.

## Dependencies and Integration Points
Depends on `enetc_mdio.c` callbacks, `enetc_hw_alloc`, PCI core, OF MDIO registration, and the global register accessor erratum path. It can coexist with port-local MDIO buses used by PF drivers.

## Risks
Probe order and static-key reference counting matter: enabling the erratum changes locking behavior globally for all ENETC accessors. Error unwinding must disable the key only after it has been incremented. `pci_iomap` occurs before `pci_enable_device_mem`, so platform quirks around BAR mapping can surface.

## Test Signals
Register central MDIO with DT PHY children, unload/reload the module while other ENETC devices run, confirm static-key enable/disable messages and reference counts across multiple devices, test Clause 22/45 transactions, and validate all error unwind paths under forced allocation/registration failures.
