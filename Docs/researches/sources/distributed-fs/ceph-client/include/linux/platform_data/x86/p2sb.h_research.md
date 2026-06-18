# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/p2sb.h

## Purpose
`p2sb.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing macros, constants, or
function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_PLATFORM_DATA_X86_P2SB_H`. Types: none visible in this header. Declared or
inline functions: `p2sb_bar`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/edac/pnd2_edac.c`, `sources/distributed-fs/ceph-client/drivers/platform/x86/p2sb.c`,
`sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-i801.c`, `sources/distributed-fs/ceph-
client/drivers/watchdog/simatic-ipc-wdt.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/errno.h`, `linux/kconfig.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/p2sb.c`, `sources/distributed-fs/ceph-
client/drivers/i2c/busses/i2c-i801.c`, `sources/distributed-fs/ceph-client/drivers/watchdog/simatic-
ipc-wdt.c`, `sources/distributed-fs/ceph-client/drivers/mfd/lpc_ich.c`. It integrates through
`struct platform_device` platform data, board files, MFD child registration, and legacy non-DT setup
paths; many modern systems may replace parts of this contract with Device Tree, ACPI, or software-
node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/p2sb.h` completely for this pass (28 lines, 575 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/p2sb.h_research.md`.
