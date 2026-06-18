# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/Kconfig

## Purpose
Defines Kconfig entries for non-USB ASIX Ethernet drivers, currently the AX88796C SPI Fast Ethernet adapter and its optional SPI transfer compression setting.

## Important APIs, Types, and Functions
`NET_VENDOR_ASIX` gates the vendor subtree. `SPI_AX88796C` is a tristate driver option that depends on `SPI` and `GPIOLIB` and selects `PHYLIB`. `SPI_AX88796C_COMPRESSION` is a boolean default for runtime SPI compression behavior, depending on `SPI_AX88796C`.

## Control Flow and State
The file only controls build-time configuration. If the vendor option is disabled, the AX88796C prompts are hidden. Compression is compiled as a default module parameter value in `ax88796c_main.c`, then can be changed per interface through ethtool private flags when the interface is down.

## Dependencies and Integration Points
The Kconfig dependencies match the code: the driver needs SPI transport, reset GPIO, and PHYLIB for the embedded PHY. The compression option feeds `IS_ENABLED(CONFIG_SPI_AX88796C_COMPRESSION)` in the driver.

## Risks and Test Signals
Build coverage should test `m`, `y`, and disabled combinations, plus `COMPILE_TEST` only where parent menus allow it. Runtime test signals for the compression option are correct default `SPICompression` private flag state at probe and successful toggling via ethtool while the netdev is stopped.
