# sources/distributed-fs/ceph-client/include/linux/platform_data/spi-omap2-mcspi.h

## Purpose
`spi-omap2-mcspi.h` is a Linux kernel SPI controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct omap2_mcspi_platform_config` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_OMAP2_MCSPI_H`, `OMAP4_MCSPI_REG_OFFSET`, `MCSPI_PINDIR_D0_IN_D1_OUT`,
`MCSPI_PINDIR_D0_OUT_D1_IN`. Types: `struct omap2_mcspi_platform_config`, `struct
omap2_mcspi_device_config`. Declared or inline functions: none visible in this header. Important
struct details: struct omap2_mcspi_platform_config fields include `unsigned short num_cs`, `unsigned
int regs_offset`, `unsigned int pin_dir:1`, `size_t max_xfer_len`; struct omap2_mcspi_device_config
fields include `unsigned turbo_mode:1`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/board-n8x0.c`, `sources/distributed-fs/ceph-client/drivers/spi/spi-
omap2-mcspi.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/board-n8x0.c`, `sources/distributed-fs/ceph-client/drivers/spi/spi-
omap2-mcspi.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/spi-omap2-mcspi.h` completely for this pass (21 lines, 406 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/spi-omap2-mcspi.h_research.md`.
