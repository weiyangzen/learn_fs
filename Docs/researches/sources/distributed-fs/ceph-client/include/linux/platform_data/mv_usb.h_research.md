# sources/distributed-fs/ceph-client/include/linux/platform_data/mv_usb.h

## Purpose
`mv_usb.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mv_usb_addon_irq`; enumerations such as `anonymous enum` into the matching driver at probe
time.

## Important APIs, types, and functions
Macros/constants: `__MV_PLATFORM_USB_H`. Types: `struct mv_usb_addon_irq`, `struct
mv_usb_platform_data`, `anonymous enum`. Declared or inline functions: `int`, `void`. Important
struct details: struct mv_usb_addon_irq fields include `unsigned int irq`, `int (*poll)(void)`;
struct mv_usb_platform_data fields include `struct mv_usb_addon_irq *id`, `struct mv_usb_addon_irq
*vbus`, `unsigned int mode`, `unsigned int disable_otg_clock_gating:1`, `unsigned int
otg_force_a_bus_req:1`, `int (*phy_init)(void __iomem *regbase)`, `void (*phy_deinit)(void __iomem
*regbase)`, `int (*set_vbus)(unsigned int vbus)`. Important enum details: anonymous enum values
include `MV_USB_MODE_OTG`, `MV_USB_MODE_HOST`; anonymous enum values include `VBUS_LOW`,
`VBUS_HIGH`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/host/ehci-mv.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/usb/host/ehci-mv.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mv_usb.h` completely for this pass (40 lines, 900 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mv_usb.h_research.md`.
