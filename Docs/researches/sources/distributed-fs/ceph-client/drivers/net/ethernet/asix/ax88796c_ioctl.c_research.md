# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_ioctl.c

## Purpose
Provides ethtool operations, MDIO callbacks, and MII ioctl forwarding for the ASIX AX88796C SPI Ethernet driver.

## Important APIs, Types, and Functions
Exports `const struct ethtool_ops ax88796c_ethtool_ops`, `ax88796c_mdio_read()`, `ax88796c_mdio_write()`, and `ax88796c_ioctl()`. Private ethtool flag `SPICompression` maps to `AX_CAP_COMP`. Pause configuration updates `ax88796c_device.flowctrl` and PHY asymmetric pause settings. Register dump support reads AX88796C register space while honoring `ax88796c_no_regs_mask`, then appends PHY registers.

## Control Flow and State
EtHTool getters read driver state such as `msg_enable`, `flowctrl`, and `priv_flags`. `set_pauseparam()` either delegates pause advertisement to PHY autonegotiation or directly updates `P0_MACCR` under `spi_lock`. Compression flag changes are rejected with `-EBUSY` while the netdev is running because a soft reset is needed to reprogram SPI compression. MDIO reads/writes serialize SPI access, program `P2_MDIOCR`/`P2_MDIODR`, and poll for `MDIOCR_VALID`.

## Dependencies and Integration Points
Integrates with PHYLIB (`phy_ethtool_*`, `phy_mii_ioctl()`, `phy_set_asym_pause()`), the shared SPI access macros, and netdev ethtool plumbing. Register dumps depend on masks initialized in `ax88796c_main.c`.

## Risks and Test Signals
MDIO polling uses `read_poll_timeout()` around SPI register reads; timeouts and bad SPI return values are key risks. Pause update paths should be tested with autoneg on/off and link up/down. Compression flag tests should verify `-EBUSY` while running and successful soft-reset application on next open.
