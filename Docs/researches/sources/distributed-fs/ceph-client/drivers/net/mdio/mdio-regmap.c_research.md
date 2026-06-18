<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-regmap.c

Purpose: library that exposes a regmap-backed, nontraditional MDIO device as a virtual Clause 22 mii_bus.

Important APIs/types/functions: `struct mdio_regmap_priv` stores regmap and the one valid PHY address. Exported `devm_mdio_regmap_register` consumes `struct mdio_regmap_config` and returns the registered mii_bus. Callbacks are `mdio_regmap_read_c22` and `mdio_regmap_write_c22`.

Control flow: registration validates `config->parent`, allocates a devm mii_bus under the parent, stores regmap/address, assigns name/id/parent and callbacks, sets `phy_mask` for optional autoscan of the valid address only or no autoscan, and calls `devm_mdiobus_register`. Reads/writes reject all addresses except `valid_addr`, then map MDIO register numbers directly to regmap offsets.

State and persistence: runtime state is the regmap pointer, valid address, bus object, and underlying register contents. No independent persistent storage exists.

Dependencies/integration: depends on REGMAP, phylib, MDIO consumers that build the config, and optional OF MDIO users. It is library-style and exports GPL symbol.

Risks and test signals: risks include direct register-number-to-regmap-offset assumptions, only Clause 22 support, autoscan mask mistakes, and parent/dev mismatch in devm allocation. Tests should cover invalid address rejection, autoscan masks, read/write error propagation, and registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-regmap.c -->
