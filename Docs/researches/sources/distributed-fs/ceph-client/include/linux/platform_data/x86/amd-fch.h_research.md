# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/amd-fch.h

## Purpose
`amd-fch.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing macros, constants,
or function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_ASM_X86_AMD_FCH_H_`, `FCH_PM_BASE`, `FCH_PM_DECODEEN`,
`FCH_PM_DECODEEN_SMBUS0SEL`, `FCH_PM_SCRATCH`, `FCH_PM_S5_RESET_STATUS`. Types: none visible in this
header. Declared or inline functions: none visible in this header.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/amd/pmc/pmc-quirks.c`, `sources/distributed-fs/ceph-
client/drivers/i2c/busses/i2c-piix4.c`, `sources/distributed-fs/ceph-
client/arch/x86/kernel/cpu/amd.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/amd/pmc/pmc-quirks.c`, `sources/distributed-fs/ceph-
client/drivers/i2c/busses/i2c-piix4.c`, `sources/distributed-fs/ceph-
client/arch/x86/kernel/cpu/amd.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/amd-fch.h` completely for this pass (13 lines, 349 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/amd-fch.h_research.md`.
