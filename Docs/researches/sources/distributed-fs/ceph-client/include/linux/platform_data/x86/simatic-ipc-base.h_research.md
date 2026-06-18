# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc-base.h

## Purpose
`simatic-ipc-base.h` is a Linux kernel x86 platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct simatic_ipc_platform` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_SIMATIC_IPC_BASE_H`, `SIMATIC_IPC_DEVICE_NONE`,
`SIMATIC_IPC_DEVICE_227D`, `SIMATIC_IPC_DEVICE_427E`, `SIMATIC_IPC_DEVICE_127E`,
`SIMATIC_IPC_DEVICE_227E`, `SIMATIC_IPC_DEVICE_227G`, `SIMATIC_IPC_DEVICE_BX_21A`,
`SIMATIC_IPC_DEVICE_BX_39A`, `SIMATIC_IPC_DEVICE_BX_59A`. Types: `struct simatic_ipc_platform`.
Declared or inline functions: none visible in this header. Important struct details: struct
simatic_ipc_platform fields include `u8 devmode`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/include/linux/platform_data/x86/simatic-ipc.h`, `sources/distributed-fs/ceph-
client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c`, `sources/distributed-fs/ceph-
client/drivers/leds/simatic/simatic-ipc-leds.c`, `sources/distributed-fs/ceph-
client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h`,
`sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c`,
`sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds.c`, `sources/distributed-
fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c`, `sources/distributed-
fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-f7188x.c`, `sources/distributed-fs/ceph-
client/drivers/leds/simatic/simatic-ipc-leds-gpio-core.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/siemens/simatic-ipc-batt.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/siemens/simatic-ipc-batt-f7188x.c`. It integrates through `struct
platform_device` platform data, board files, MFD child registration, and legacy non-DT setup paths;
many modern systems may replace parts of this contract with Device Tree, ACPI, or software-node
properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc-base.h` completely for this pass (31 lines, 768 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc-base.h_research.md`.
