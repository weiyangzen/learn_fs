# sources/distributed-fs/ceph-client/include/linux/platform_data/lenovo-yoga-c630.h

## Purpose
`lenovo-yoga-c630.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing macros, constants,
or function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LENOVO_YOGA_C630_DATA_H`, `YOGA_C630_MOD_NAME`, `YOGA_C630_DEV_UCSI`,
`YOGA_C630_DEV_PSY`, `YOGA_C630_UCSI_WRITE_SIZE`, `YOGA_C630_UCSI_CCI_SIZE`,
`YOGA_C630_UCSI_DATA_SIZE`, `YOGA_C630_UCSI_READ_SIZE`, `LENOVO_EC_EVENT_USB`,
`LENOVO_EC_EVENT_UCSI`, `LENOVO_EC_EVENT_HPD`, `LENOVO_EC_EVENT_BAT_STATUS`,
`LENOVO_EC_EVENT_BAT_INFO`, `LENOVO_EC_EVENT_BAT_ADPT_STATUS`. Types: none visible in this header.
Declared or inline functions: `yoga_c630_ec_read8`, `yoga_c630_ec_read16`,
`yoga_c630_ec_register_notify`, `yoga_c630_ec_unregister_notify`, `yoga_c630_ec_ucsi_get_version`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/power/supply/lenovo_yoga_c630_battery.c`, `sources/distributed-fs/ceph-
client/drivers/platform/arm64/lenovo-yoga-c630.c`, `sources/distributed-fs/ceph-
client/drivers/usb/typec/ucsi/ucsi_yoga_c630.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/power/supply/lenovo_yoga_c630_battery.c`, `sources/distributed-fs/ceph-
client/drivers/platform/arm64/lenovo-yoga-c630.c`, `sources/distributed-fs/ceph-
client/drivers/usb/typec/ucsi/ucsi_yoga_c630.c`. It integrates through `struct platform_device`
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lenovo-yoga-c630.h` completely for this pass (44 lines, 1350 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lenovo-yoga-c630.h_research.md`.
