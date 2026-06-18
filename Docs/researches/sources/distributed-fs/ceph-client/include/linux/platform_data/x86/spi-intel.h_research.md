# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/spi-intel.h

## Purpose
`spi-intel.h` is a Linux kernel SPI controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct intel_spi_boardinfo`; enumerations such as `enum intel_spi_type` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `SPI_INTEL_PDATA_H`. Types: `struct intel_spi_boardinfo`, `enum intel_spi_type`.
Declared or inline functions: `bool`. Important struct details: struct intel_spi_boardinfo fields
include `enum intel_spi_type type`, `bool (*set_writeable)(void __iomem *base, void *data)`, `void
*data`. Important enum details: enum intel_spi_type values include `INTEL_SPI_BYT`, `INTEL_SPI_LPT`,
`INTEL_SPI_BXT`, `INTEL_SPI_CNL`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/include/linux/mfd/lpc_ich.h`, `sources/distributed-fs/ceph-client/drivers/spi/spi-intel.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/include/linux/mfd/lpc_ich.h`, `sources/distributed-fs/ceph-client/drivers/spi/spi-intel.h`.
It integrates through `struct platform_device` platform data, board files, MFD child registration,
and legacy non-DT setup paths; many modern systems may replace parts of this contract with Device
Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/spi-intel.h` completely for this pass (31 lines, 756 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/spi-intel.h_research.md`.
