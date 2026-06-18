<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-realtek-rtl9300.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-realtek-rtl9300.c

Purpose: MDIO controller for Realtek RTL9300-family switch SoCs where MDIO access is abstracted through switch port polling hardware.

Important APIs/types/functions: `struct rtl9300_mdio_priv` stores regmap, HW mutex, valid port bitmap, per-port SMI bus/address maps, C45 mode per SMI bus, and bus pointers. `struct rtl9300_mdio_chan` binds a child mii_bus to one SMI bus. Key functions are C22/C45 read/write callbacks, `rtl9300_mdiobus_map_ports`, `rtl9300_mdiobus_probe_one`, `rtl9300_mdiobus_init`, and probe.

Control flow: probe obtains parent syscon regmap, maps switch `ethernet-ports` to MDIO bus/address using `phy-handle`, creates one mii_bus per child MDIO node, detects whether each SMI bus must operate in C45 mode, then programs port address, polling selection, and global interface mode registers. Access callbacks map PHY address to switch port, lock hardware, program control/data registers, wait for command clear, and return data or fail status.

State and persistence: runtime state includes port maps, bus C45 mode, regmap hardware configuration, and mutex-protected access. The programmed switch registers persist until reset or reconfiguration.

Dependencies/integration: depends on Realtek RTL platform, MFD syscon, OF/fwnode graph properties, phylib, and switch-port DT layout.

Risks and test signals: risks include incorrect port-to-PHY mapping, no mixed C22/C45 on the same SMI bus, tight polling timeouts, and hardware access shared with switch subsystems. Tests should cover DT mapping validation, duplicate/illegal ports, C22/C45 buses, fail bit handling, and concurrent reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-realtek-rtl9300.c -->
