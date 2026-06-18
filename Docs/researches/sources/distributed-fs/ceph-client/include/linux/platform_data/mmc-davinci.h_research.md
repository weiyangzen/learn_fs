# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-davinci.h

## Purpose
`mmc-davinci.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct davinci_mmc_config`; enumerations such as `anonymous enum` into the matching driver at probe
time.

## Important APIs, types, and functions
Macros/constants: `_DAVINCI_MMC_H`. Types: `struct davinci_mmc_config`, `anonymous enum`. Declared
or inline functions: `int`, `void`, `davinci_setup_mmc`. Important struct details: struct
davinci_mmc_config fields include `int (*get_cd)(int module)`, `int (*get_ro)(int module)`, `void
(*set_power)(int module, bool on)`, `u8 wires`, `u32 max_freq`, `u32 caps`, `u8 nr_sg`. Important
enum details: anonymous enum values include `MMC_CTLR_VERSION_1`, `MMC_CTLR_VERSION_2`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mmc/host/davinci_mmc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`, `linux/mmc/host.h`. Direct source-tree consumers found by include
search are `sources/distributed-fs/ceph-client/drivers/mmc/host/davinci_mmc.c`. It integrates
through `struct platform_device` platform data, board files, MFD child registration, and legacy non-
DT setup paths; many modern systems may replace parts of this contract with Device Tree, ACPI, or
software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-davinci.h` completely for this pass (37 lines, 736 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-davinci.h_research.md`.
