# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-sdhci-s3c.h

## Purpose
`mmc-sdhci-s3c.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct s3c_sdhci_platdata`; enumerations such as `enum cd_types` into the matching driver at probe
time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_SDHCI_S3C_H`. Types: `struct s3c_sdhci_platdata`, `enum
cd_types`. Declared or inline functions: `void`. Important struct details: struct s3c_sdhci_platdata
fields include `unsigned int max_width`, `unsigned int host_caps`, `unsigned int host_caps2`,
`unsigned int pm_caps`, `enum cd_types cd_type`, `int ext_cd_gpio`, `bool ext_cd_gpio_invert`, `int
state))`. Important enum details: enum cd_types values include `S3C_SDHCI_CD_INTERNAL`,
`S3C_SDHCI_CD_EXTERNAL`, `S3C_SDHCI_CD_GPIO`, `S3C_SDHCI_CD_NONE`, `S3C_SDHCI_CD_PERMANENT`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/sdhci.h`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/sdhci-s3c.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/sdhci.h`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/sdhci-s3c.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-sdhci-s3c.h` completely for this pass (57 lines, 2278 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-sdhci-s3c.h_research.md`.
