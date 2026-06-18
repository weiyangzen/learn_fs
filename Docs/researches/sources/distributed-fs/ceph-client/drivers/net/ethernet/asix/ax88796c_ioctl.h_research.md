# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_ioctl.h

## Purpose
Declares the ioctl, ethtool, and MDIO interfaces implemented by `ax88796c_ioctl.c` for use by the AX88796C main driver.

## Important APIs, Types, and Functions
The header exports `ax88796c_ethtool_ops`, `ax88796c_mdio_read()`, `ax88796c_mdio_write()`, and `ax88796c_ioctl()`. It includes `linux/ethtool.h`, `linux/mii.h`, and `linux/netdevice.h`, matching its public interfaces.

## Control Flow and State
There is no runtime control flow in the header. It establishes linkage between `ax88796c_main.c`, which assigns netdev/MDIO operation tables, and the implementation file.

## Dependencies and Integration Points
Used by `ax88796c_main.c` to populate `ndev->ethtool_ops`, `ndo_eth_ioctl`, and `mii_bus` callbacks. The function signatures are standard kernel netdev and PHYLIB contracts.

## Risks and Test Signals
Risk is low and mostly about signature drift if kernel APIs change. Build tests catch mismatches immediately. Functional tests are inherited from the implementation: ethtool stats/register access, MII ioctl behavior, and MDIO PHY discovery.
