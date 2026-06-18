# sources/distributed-fs/ceph-client/include/linux/platform_data/wilco-ec.h

## Purpose
`wilco-ec.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct wilco_ec_device`; enumerations such as `enum wilco_ec_msg_type` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `WILCO_EC_H`, `WILCO_EC_FLAG_NO_RESPONSE`, `EC_MAILBOX_DATA_SIZE`,
`WILCO_EC_PROPERTY_MAX_SIZE`. Types: `struct wilco_ec_device`, `struct wilco_ec_request`, `struct
wilco_ec_message`, `struct wilco_ec_property_msg`, `enum wilco_ec_msg_type`. Declared or inline
functions: `wilco_ec_mailbox`, `wilco_keyboard_leds_init`, `wilco_ec_add_sysfs`,
`wilco_ec_remove_sysfs`. Important struct details: struct wilco_ec_device fields include `struct
device *dev`, `struct mutex mailbox_lock`, `struct resource *io_command`, `struct resource
*io_data`, `struct resource *io_packet`, `void *data_buffer`, `size_t data_size`, `struct
platform_device *debugfs_pdev`; struct wilco_ec_request fields include `u8 struct_version`, `u8
checksum`, `u16 mailbox_id`, `u8 mailbox_version`, `u8 reserved`, `u16 data_size`, `} __packed`, `u8
struct_version`; struct wilco_ec_message fields include `enum wilco_ec_msg_type type`, `u8 flags`,
`size_t request_size`, `void *request_data`, `size_t response_size`, `void *response_data`; struct
wilco_ec_property_msg fields include `u32 property_id`, `int length`, `u8
data[WILCO_EC_PROPERTY_MAX_SIZE]`. Important enum details: enum wilco_ec_msg_type values include
`WILCO_EC_MSG_LEGACY`, `WILCO_EC_MSG_PROPERTY`, `WILCO_EC_MSG_TELEMETRY`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/rtc/rtc-wilco-ec.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/core.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/properties.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/mailbox.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/mutex.h`, `linux/types.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/rtc/rtc-wilco-ec.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/core.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/properties.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/mailbox.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/debugfs.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/keyboard_leds.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/sysfs.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/telemetry.c`. It integrates through `struct platform_device`
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/wilco-ec.h` completely for this pass (225 lines, 7076 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/wilco-ec.h_research.md`.
