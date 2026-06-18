# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-xgene.c

## Purpose
This file implements the Applied Micro X-Gene SoC MDIO platform driver. It supports both RGMII and XFI MDIO register layouts, maps SoC CSR blocks, resets/initializes the Ethernet management block, and exposes an `mii_bus` to PHYLIB using either OF child enumeration or ACPI child PHY registration.

## Important APIs, Types, and Functions
The driver revolves around `struct xgene_mdio_pdata`, which is allocated in probe and carries mapped MAC, MDIO, and diagnostic CSR bases, a clock pointer, the MDIO variant id, a MAC spinlock, and the registered bus. Exported helpers include `xgene_mdio_rd_mac()`, `xgene_mdio_wr_mac()`, `xgene_mdio_rgmii_read()`, `xgene_mdio_rgmii_write()`, and `xgene_enet_phy_register()`. XFI accesses use `xgene_xfi_mdio_read()` and `xgene_xfi_mdio_write()`. Probe selects the variant from OF or ACPI match data, maps resource 0, initializes the hardware through `xgene_mdio_reset()`, allocates `struct mii_bus`, installs callbacks, and registers it with `of_mdiobus_register()` or `mdiobus_register()` plus ACPI namespace walking.

## Control Flow
RGMII reads and writes program MAC management registers through serialized MAC CSR read/write helpers, poll the MII management busy indicator, and return either PHY data or `-EBUSY`. XFI paths write MIIM field/command CSRs directly, poll `MIIM_INDICATOR_ADDR`, clear the command register, and return data or an error for read timeout. Hardware reset toggles the OF clock or invokes ACPI `_RST`, releases diagnostic RAM shutdown through `xgene_enet_ecc_init()`, and resets GMAC. Probe configures the appropriate callback set and bus id, registers the bus, then stores it in `pdata`. Remove unregisters/frees the bus and disables the clock for OF-backed devices.

## State and Persistence
Runtime state lives in `pdata`, the allocated `mii_bus`, and the hardware CSR state. The RGMII MAC lock serializes shared MAC command registers. ACPI child devices receive `adev->driver_data = phy_dev` during manual PHY registration. The driver has no persistent storage; all state is rebuilt on probe. Clock enable state is persistent while the OF device remains probed and is disabled on remove or reset failure.

## Dependencies and Integration Points
The file integrates with platform device matching, OF, ACPI, clock framework, PHYLIB, MDIO core, and the X-Gene register definitions in `<linux/mdio/mdio-xgene.h>`. It exports several functions for other X-Gene Ethernet code to reuse. OF compatibles are `apm,xgene-mdio-rgmii` and `apm,xgene-mdio-xfi`; ACPI IDs are `APMC0D65` and `APMC0D66`.

## Risks and Edge Cases
The XFI write path does not report timeout as an error, unlike the XFI read and RGMII paths. Several polling loops use small fixed retry counts, making timing-sensitive failures possible on slow hardware. ACPI registration masks all PHYs then manually registers children with a `phy-channel` property, so malformed ACPI properties silently skip PHYs. Error unwinding after `mhi`-style registration is not relevant here, but in this file `mdiobus_alloc()` is unmanaged and must be freed on every failure path, which the probe handles via `out_mdiobus`. Clock toggling assumes a valid OF clock and may leave hardware reset state platform-specific under ACPI.

## Test Signals
Validation should include OF and ACPI boot paths, both RGMII and XFI variants, successful PHY reads/writes, timeout/error handling for busy indicators, clock enable/disable balance, and removal after partially populated buses. Good test observations are registered MDIO bus ids `xgene-mii-rgmii` or `xgene-mii-xfi`, registered PHY devices under expected addresses, and successful link negotiation by consumers of the bus.
