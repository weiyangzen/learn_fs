# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/Makefile

## Purpose
Builds the ASIX AX88796C SPI Ethernet driver object when `CONFIG_SPI_AX88796C` is enabled.

## Important APIs, Types, and Functions
The composite object `ax88796c.o` is assembled from `ax88796c_main.o`, `ax88796c_ioctl.o`, and `ax88796c_spi.o`.

## Control Flow and State
There is no runtime control flow. The Makefile expresses module composition: main netdev/SPI driver logic, ethtool/MDIO/ioctl helpers, and low-level SPI transaction helpers are linked into one driver.

## Dependencies and Integration Points
The Makefile is selected from the parent Ethernet vendor build and relies on the Kconfig symbol. It mirrors include dependencies among the files, where `ax88796c_main.h` and `ax88796c_spi.h` expose shared structs and register definitions.

## Risks and Test Signals
The practical test is that all three objects are linked for both built-in and module builds. Omitting any object would leave unresolved symbols such as `ax88796c_ethtool_ops`, `ax88796c_mdio_read()`, or `axspi_read_reg()`.
