# sources/distributed-fs/ceph-client/drivers/net/ethernet/micrel/Kconfig

## Purpose
`drivers/net/ethernet/micrel/Kconfig` defines the Linux kernel configuration menu for Micrel Ethernet device drivers. It gates visibility of individual Micrel drivers and declares their bus, PHY, CRC, EEPROM, and optional PTP dependencies.

## Important APIs, Types, And Functions
This is Kconfig data, not C code. Symbols are `NET_VENDOR_MICREL`, `KS8842`, `KS8851`, `KS8851_MLL`, and `KSZ884X_PCI`. The vendor symbol is a boolean menu gate defaulting to `y`. Driver symbols are tristate module/built-in selections for platform bus, SPI, memory-mapped, and PCI variants.

## Control Flow
When `NET_VENDOR_MICREL` is enabled, Kconfig presents the device-specific options. `KS8842` depends on `HAS_IOMEM && DMA_ENGINE`. `KS8851` depends on `SPI` and optional PTP support, selecting MII, CRC32, EEPROM_93CX6, PHYLIB, and MICREL_PHY. `KS8851_MLL` depends on HAS_IOMEM and optional PTP support with similar selects. `KSZ884X_PCI` depends on PCI and selects MII and CRC32.

## State And Persistence
Selected symbols persist in the kernel `.config` and drive object inclusion through the adjacent Makefile. Tristate values determine built-in versus module output.

## Dependencies And Integration Points
The file integrates with the top-level Ethernet vendor menu and `drivers/net/ethernet/micrel/Makefile`. It also selects PHY and helper subsystems needed by the corresponding drivers.

## Risks
Incorrect dependencies can expose drivers on unsupported platforms or hide valid hardware. Missing `select` entries can cause link failures or runtime probe failures. The broad vendor dependency expression is permissive because child symbols do precise gating.

## Test Signals
Run Kconfig allmodconfig/allyesconfig/targeted configs, verify expected prompts appear only under `NET_VENDOR_MICREL`, and verify selected objects in the Makefile match the chosen symbols.
