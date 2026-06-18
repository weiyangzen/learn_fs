# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-esdhc-mcf.h

## Purpose
`mmc-esdhc-mcf.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mcf_esdhc_platform_data`; enumerations such as `enum cd_types` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_PLATFORM_DATA_MCF_ESDHC_H__`. Types: `struct mcf_esdhc_platform_data`,
`enum cd_types`. Declared or inline functions: none visible in this header. Important struct
details: struct mcf_esdhc_platform_data fields include `int max_bus_width`, `int cd_type`. Important
enum details: enum cd_types values include `ESDHC_CD_NONE`, `ESDHC_CD_CONTROLLER`,
`ESDHC_CD_PERMANENT`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/m68k/coldfire/device.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-
esdhc-mcf.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/m68k/coldfire/device.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-
esdhc-mcf.c`. It integrates through `struct platform_device` platform data, board files, MFD child
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-esdhc-mcf.h` completely for this pass (17 lines, 447 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-esdhc-mcf.h_research.md`.
