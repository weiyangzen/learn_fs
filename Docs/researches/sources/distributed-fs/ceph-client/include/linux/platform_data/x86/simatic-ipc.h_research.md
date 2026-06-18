# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h

## Purpose
`simatic-ipc.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing enumerations such
as `enum simatic_ipc_station_ids` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_SIMATIC_IPC_H`, `SIMATIC_IPC_DMI_ENTRY_OEM`,
`SIMATIC_IPC_DMI_TYPE`, `SIMATIC_IPC_DMI_GROUP`, `SIMATIC_IPC_DMI_ENTRY`, `SIMATIC_IPC_DMI_TID`.
Types: `enum simatic_ipc_station_ids`. Declared or inline functions: `le32_to_cpu`,
`simatic_ipc_get_station_id`. Important enum details: enum simatic_ipc_station_ids values include
`SIMATIC_IPC_INVALID_STATION_ID`, `SIMATIC_IPC_IPC227D`, `SIMATIC_IPC_IPC427D`,
`SIMATIC_IPC_IPC227E`, `SIMATIC_IPC_IPC277E`, `SIMATIC_IPC_IPC427E`, `SIMATIC_IPC_IPC477E`,
`SIMATIC_IPC_IPC127E`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/siemens/simatic-ipc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/dmi.h`, `linux/platform_data/x86/simatic-ipc-base.h`. Direct source-tree
consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/siemens/simatic-ipc.c`. It integrates through `struct platform_device`
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h` completely for this pass (79 lines, 2203 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h_research.md`.
