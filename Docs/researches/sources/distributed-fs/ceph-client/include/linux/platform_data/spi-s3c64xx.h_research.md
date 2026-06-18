# sources/distributed-fs/ceph-client/include/linux/platform_data/spi-s3c64xx.h

## Purpose
`spi-s3c64xx.h` is a Linux kernel SPI controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct s3c64xx_spi_csinfo` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__SPI_S3C64XX_H`. Types: `struct s3c64xx_spi_csinfo`, `struct s3c64xx_spi_info`.
Declared or inline functions: `int`, `s3c64xx_spi0_set_platdata`, `s3c64xx_spi0_cfg_gpio`. Important
struct details: struct s3c64xx_spi_csinfo fields include `u8 fb_delay`; struct s3c64xx_spi_info
fields include `int src_clk_nr`, `int num_cs`, `bool no_cs`, `bool polling`, `int
(*cfg_gpio)(void)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-spi-s3c64xx.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410-module.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/dmaengine.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/mach-crag6410.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/setup-spi-s3c64xx.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/mach-crag6410-module.c`, `sources/distributed-fs/ceph-
client/drivers/spi/spi-s3c64xx.c`. It integrates through `struct platform_device` platform data,
board files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace
parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/spi-s3c64xx.h` completely for this pass (58 lines, 1610 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/spi-s3c64xx.h_research.md`.
