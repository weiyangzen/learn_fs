# sources/distributed-fs/ceph-client/include/linux/platform_data/mfd-mcp-sa11x0.h

## Purpose
`mfd-mcp-sa11x0.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mcp_plat_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__MFD_MCP_SA11X0_H`. Types: `struct mcp_plat_data`. Declared or inline functions:
none visible in this header. Important struct details: struct mcp_plat_data fields include `u32
mccr0`, `u32 mccr1`, `unsigned int sclk_rate`, `void *codec_pdata`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-sa1100/assabet.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
sa1100/collie.c`, `sources/distributed-fs/ceph-client/drivers/mfd/mcp-sa11x0.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/assabet.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-sa1100/collie.c`, `sources/distributed-fs/ceph-client/drivers/mfd/mcp-
sa11x0.c`. It integrates through `struct platform_device` platform data, board files, MFD child
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mfd-mcp-sa11x0.h` completely for this pass (17 lines, 272 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mfd-mcp-sa11x0.h_research.md`.
