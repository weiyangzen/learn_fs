# sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/Kconfig

## Purpose
This Kconfig file introduces the LiteX Ethernet vendor menu and the `LITEX_LITEETH` driver option. It allows kernel configuration to expose LiteX FPGA soft-SoC Ethernet support without affecting other Ethernet vendors when disabled.

## Important Symbols
`NET_VENDOR_LITEX` is a `bool` menu gate, defaults to `y`, and follows the standard Ethernet vendor pattern: disabling it hides LiteX-specific questions rather than directly disabling common networking. `LITEX_LITEETH` is a `tristate` option named "LiteX Ethernet support" and depends on `OF && HAS_IOMEM`, matching the platform driver's Device Tree and MMIO requirements.

## Control Flow
Kconfig evaluation first offers the vendor gate. If enabled, it offers `LITEX_LITEETH`; choosing built-in or module controls whether `litex_liteeth.o` is compiled by the sibling Makefile. The help text identifies LiteX as an FPGA-oriented soft SoC and LiteEth as the target Ethernet core.

## State And Persistence
The selected symbols persist in the kernel `.config`. `LITEX_LITEETH=m` leads to a loadable module, `y` links it into the kernel image, and `n` omits the driver object.

## Dependencies And Integration Points
This file integrates with the parent Ethernet Kconfig hierarchy and with `drivers/net/ethernet/litex/Makefile`. The `OF` dependency mirrors `of_device_id` matching in `litex_liteeth.c`; `HAS_IOMEM` mirrors use of MMIO resource mapping and LiteX CSR accessors.

## Risks
The vendor gate defaults to enabled, so LiteX options appear broadly in configs even when no FPGA LiteX hardware exists. The driver depends only on `OF` and `HAS_IOMEM`; if future code adds PHY, MDIO, DMA, or PTP dependencies, this Kconfig must be updated or compile/runtime failures may appear under randconfig.

## Test Signals
Useful checks are `allnoconfig`, `defconfig`, `allyesconfig`, `allmodconfig`, and randconfig builds with `OF` or `HAS_IOMEM` disabled/enabled. Confirm that `CONFIG_LITEX_LITEETH=m` emits a module and `CONFIG_NET_VENDOR_LITEX=n` hides the driver option.
