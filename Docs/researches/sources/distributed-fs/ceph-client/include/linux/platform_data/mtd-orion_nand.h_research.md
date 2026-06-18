# sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-orion_nand.h

## Purpose
`mtd-orion_nand.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct orion_nand_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__MTD_ORION_NAND_H`. Types: `struct orion_nand_data`. Declared or inline
functions: none visible in this header. Important struct details: struct orion_nand_data fields
include `struct mtd_partition *parts`, `u32 nr_parts`, `u8 ale`, `u8 cle`, `u8 width`, `u8
chip_delay`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-orion5x/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
orion5x/kurobox_pro-setup.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c`,
`sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/orion_nand.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-orion5x/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
orion5x/kurobox_pro-setup.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c`,
`sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/orion_nand.c`. It integrates through
`struct platform_device` platform data, board files, MFD child registration, and legacy non-DT setup
paths; many modern systems may replace parts of this contract with Device Tree, ACPI, or software-
node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-orion_nand.h` completely for this pass (23 lines, 520 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-orion_nand.h_research.md`.
