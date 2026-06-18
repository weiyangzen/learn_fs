<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-sun4i.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-sun4i.c

Purpose: Allwinner sun4i EMAC MDIO controller driver.

Important APIs/types/functions: `struct sun4i_mdio_data` stores MMIO base and optional PHY regulator. Core callbacks are `sun4i_mdio_read`, `sun4i_mdio_write`, probe, and remove.

Control flow: probe allocates mii_bus/private data, maps registers, obtains/enables optional `phy` regulator, assigns callbacks, registers with OF MDIO, and stores the bus. Reads and writes program PHY/register address, set MCMD to start, poll MIND busy with a 100 ms jiffies timeout and 1 ms sleep, clear MCMD, then read MRDD or write MWTD.

State and persistence: runtime state is MMIO register values, optional regulator enable state, and bus private data. Remove unregisters, disables regulator, and frees bus.

Dependencies/integration: depends on ARCH_SUNXI or compile test, OF MDIO, regulator framework, platform MMIO, and phylib. Compatible strings include `allwinner,sun4i-a10-mdio` and deprecated `allwinner,sun4i-mdio`.

Risks and test signals: risks include regulator optional/defer handling, polling while sleeping, read/write command ordering, and no Clause 45 support. Tests should cover regulator paths, timeout, OF registration, remove cleanup, and deprecated compatible coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-sun4i.c -->
