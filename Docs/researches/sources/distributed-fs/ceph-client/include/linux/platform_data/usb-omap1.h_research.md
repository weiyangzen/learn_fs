# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap1.h

## Purpose
`usb-omap1.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct omap_usb_config` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_USB_OMAP1_H`. Types: `struct omap_usb_config`. Declared or inline
functions: `u32`, `int`, `void`. Important struct details: struct omap_usb_config fields include
`unsigned register_host:1`, `unsigned register_dev:1`, `u8 otg`, `const char *extcon`, `u8
hmc_mode`, `u8 rwc`, `u8 pins[3]`, `struct platform_device *udc_device`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/usb.h`, `sources/distributed-fs/ceph-
client/drivers/usb/gadget/udc/omap_udc.c`, `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-omap.c`, `sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-
otg.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.h`, `sources/distributed-fs/ceph-
client/drivers/usb/gadget/udc/omap_udc.c`, `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-omap.c`, `sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-
otg.c`. It integrates through `struct platform_device` platform data, board files, MFD child
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap1.h` completely for this pass (57 lines, 1567 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap1.h_research.md`.
