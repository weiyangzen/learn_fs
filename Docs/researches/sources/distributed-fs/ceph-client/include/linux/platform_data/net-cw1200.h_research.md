# sources/distributed-fs/ceph-client/include/linux/platform_data/net-cw1200.h

## Purpose
`net-cw1200.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct cw1200_platform_data_spi` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `CW1200_PLAT_H_INCLUDED`. Types: `struct cw1200_platform_data_spi`, `struct
cw1200_platform_data_sdio`. Declared or inline functions: `cw1200_sdio_set_platform_data`. Important
struct details: struct cw1200_platform_data_spi fields include `u8 spi_bits_per_word`, `u16
ref_clk`, `bool have_5ghz`, `bool enable)`, `bool enable)`, `const u8 *macaddr`, `const char
*sdd_file`; struct cw1200_platform_data_sdio fields include `u16 ref_clk`, `bool have_5ghz`, `bool
no_nptb`, `int irq`, `bool enable)`, `bool enable)`, `const u8 *macaddr`, `const char *sdd_file`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/wireless/st/cw1200/cw1200_sdio.c`, `sources/distributed-fs/ceph-
client/drivers/net/wireless/st/cw1200/cw1200_spi.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/net/wireless/st/cw1200/cw1200_sdio.c`, `sources/distributed-fs/ceph-
client/drivers/net/wireless/st/cw1200/cw1200_spi.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/net-cw1200.h` completely for this pass (77 lines, 2496 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/net-cw1200.h_research.md`.
