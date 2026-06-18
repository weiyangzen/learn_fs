# sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-omap2.h

## Purpose
`mtd-nand-omap2.h` is a Linux kernel NAND flash controller board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct gpmc_nand_regs`; enumerations such as `enum nand_io`, `enum omap_ecc` into the matching
driver at probe time.

## Important APIs, types, and functions
Macros/constants: none visible in this header. Types: `struct gpmc_nand_regs`, `enum nand_io`, `enum
omap_ecc`. Declared or inline functions: none visible in this header. Important struct details:
struct gpmc_nand_regs fields include `void __iomem *gpmc_nand_command`, `void __iomem
*gpmc_nand_address`, `void __iomem *gpmc_nand_data`, `void __iomem *gpmc_prefetch_config1`, `void
__iomem *gpmc_prefetch_config2`, `void __iomem *gpmc_prefetch_control`, `void __iomem
*gpmc_prefetch_status`, `void __iomem *gpmc_ecc_config`. Important enum details: enum nand_io values
include `NAND_OMAP_PREFETCH_POLLED`, `NAND_OMAP_POLLED`, `NAND_OMAP_PREFETCH_DMA`,
`NAND_OMAP_PREFETCH_IRQ`; enum omap_ecc values include `/*`, `OMAP_ECC_HAM1_CODE_SW`, `/*`,
`OMAP_ECC_HAM1_CODE_HW`, `OMAP_ECC_BCH4_CODE_HW_DETECTION_SW`, `OMAP_ECC_BCH4_CODE_HW`,
`OMAP_ECC_BCH8_CODE_HW_DETECTION_SW`, `OMAP_ECC_BCH8_CODE_HW`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mtd/nand/raw/omap2.c`, `sources/distributed-fs/ceph-client/drivers/memory/omap-
gpmc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/mtd/partitions.h`, `linux/mod_devicetable.h`. Direct source-tree consumers found
by include search are `sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap2.c`,
`sources/distributed-fs/ceph-client/drivers/memory/omap-gpmc.c`. It integrates through `struct
platform_device` platform data, board files, MFD child registration, and legacy non-DT setup paths;
many modern systems may replace parts of this contract with Device Tree, ACPI, or software-node
properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-omap2.h` completely for this pass (72 lines, 2244 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-omap2.h_research.md`.
