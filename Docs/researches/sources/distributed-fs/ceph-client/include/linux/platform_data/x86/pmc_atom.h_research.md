# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pmc_atom.h

## Purpose
`pmc_atom.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing macros, constants,
or function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `PMC_ATOM_H`, `PMC_CLK_CTL_OFFSET`, `PMC_CLK_CTL_SIZE`, `PMC_CLK_NUM`,
`PMC_CLK_CTL_GATED_ON_D3`, `PMC_CLK_CTL_FORCE_ON`, `PMC_CLK_CTL_FORCE_OFF`, `PMC_CLK_CTL_RESERVED`,
`PMC_MASK_CLK_CTL`, `PMC_MASK_CLK_FREQ`, `PMC_CLK_FREQ_XTAL`, `PMC_CLK_FREQ_PLL`, `PMC_PSS_BIT_GBE`,
`PMC_PSS_BIT_SATA`, and 16 more. Types: none visible in this header. Declared or inline functions:
`pmc_atom_read`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/x86/lpss.c`, `sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-
atom.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/bits.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/x86/lpss.c`, `sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-
atom.c`. It integrates through `struct platform_device` platform data, board files, MFD child
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pmc_atom.h` completely for this pass (163 lines, 5026 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pmc_atom.h_research.md`.
