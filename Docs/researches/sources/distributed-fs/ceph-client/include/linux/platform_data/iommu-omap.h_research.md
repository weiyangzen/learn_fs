# sources/distributed-fs/ceph-client/include/linux/platform_data/iommu-omap.h

## Purpose
`iommu-omap.h` is a Linux kernel IOMMU platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
iommu_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: none visible in this header. Types: `struct iommu_platform_data`. Declared or
inline functions: `int`. Important struct details: struct iommu_platform_data fields include `const
char *reset_name`, `int (*assert_reset)(struct platform_device *pdev, const char *name)`, `int
(*deassert_reset)(struct platform_device *pdev, const char *name)`, `int (*device_enable)(struct
platform_device *pdev)`, `int (*device_idle)(struct platform_device *pdev)`, `u8 *pwrst)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/iommu/omap-iommu-debug.c`, `sources/distributed-fs/ceph-client/drivers/iommu/omap-
iommu.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-quirks.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu-debug.c`, `sources/distributed-fs/ceph-
client/drivers/iommu/omap-iommu.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-
quirks.c`. It integrates through `struct platform_device` platform data, board files, MFD child
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/iommu-omap.h` completely for this pass (20 lines, 618 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/iommu-omap.h_research.md`.
