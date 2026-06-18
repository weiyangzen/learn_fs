# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac_mdio.c

Purpose: MDIO bus implementation for the Xilinx LocalLink TEMAC driver.

Important APIs: `temac_mdio_read()` writes PHY address/register to `XTE_LSW0_OFFSET`, reads `XTE_MIIMAI_OFFSET` through the locked indirect helper, and returns the PHY register value. `temac_mdio_write()` writes the value to `XTE_MGTDR_OFFSET` and initiates a write through `XTE_MIIMAI_OFFSET`. `temac_mdio_setup()` computes an MDIO clock divisor from DT `clock-frequency` or platform data, enables MDIO in `XTE_MC_OFFSET`, allocates/configures an `mii_bus`, derives a bus ID from resource or platform ID, and registers it with `of_mdiobus_register()`. `temac_mdio_teardown()` unregisters the bus.

Control flow and integration: setup is called from `temac_probe()` before PHY lookup/connection. MDIO transactions share `lp->indirect_lock` with other indirect TEMAC register access because the hardware supports only one indirect operation at a time.

State and dependencies: stores the bus pointer in `lp->mii_bus`. Depends on PHYLIB, OF MDIO, OF address parsing, platform data, and indirect access helpers from `ll_temac_main.c`.

Risks and tests: risks include divisor underflow/overflow, missing bus ID for unusual platform data, sleeping expectations around spin-locked indirect access, and teardown when setup failed. Test MDIO scan, PHY read/write via ethtool, DT and platform-data configurations, and concurrent link adjustment plus MDIO access.
