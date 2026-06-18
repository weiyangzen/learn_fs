<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-aspeed.c

Purpose: MDIO bus controller for the independent ASPEED AST2600 MDIO block, exposing Clause 22 and Clause 45 callbacks to phylib.

Important APIs/types/functions: `struct aspeed_mdio` stores MMIO base and optional reset. `aspeed_mdio_op` emits a hardware operation; `aspeed_mdio_get_data` reads completed data; C22/C45 callbacks and `aspeed_mdio_probe/remove` implement bus lifecycle.

Control flow: probe allocates a devm mii_bus, maps registers, obtains optional shared reset, deasserts reset, installs read/write callbacks, and registers via `of_mdiobus_register`. Operations encode start type, op code, PHY address, register/devad, and write data into `ASPEED_MDIO_CTRL`, issue a dummy read to avoid stale read-after-write state, poll `FIRE` clear, and for reads poll `DATA_IDLE` before returning data.

State and persistence: runtime-only state is MMIO registers, reset line state, and registered bus. Remove asserts reset and unregisters the bus.

Dependencies/integration: depends on OF MDIO, HAS_IOMEM, reset controller, iopoll, and phylib. Compatible string is `aspeed,ast2600-mdio`.

Risks and test signals: risks include timeout tuning, stale-data workaround regressions, reset sharing side effects, and C45 address phase mistakes. Test signals include register-level emulation, reset probe/remove, C22 and C45 reads/writes, and failed `of_mdiobus_register` cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-aspeed.c -->
