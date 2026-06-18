# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap.h

## Purpose
`usb-omap.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct usbtll_omap_platform_data`; enumerations such as `enum usbhs_omap_port_mode`, `enum
musb_interface` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `OMAP3_HS_USB_PORTS`. Types: `struct usbtll_omap_platform_data`, `struct
ehci_hcd_omap_platform_data`, `struct ohci_hcd_omap_platform_data`, `struct
usbhs_omap_platform_data`, `struct omap_musb_board_data`, `enum usbhs_omap_port_mode`, `enum
musb_interface`. Declared or inline functions: `void`. Important struct details: struct
usbtll_omap_platform_data fields include `enum usbhs_omap_port_mode port_mode[OMAP3_HS_USB_PORTS]`;
struct ehci_hcd_omap_platform_data fields include `enum usbhs_omap_port_mode
port_mode[OMAP3_HS_USB_PORTS]`, `int reset_gpio_port[OMAP3_HS_USB_PORTS]`, `struct regulator
*regulator[OMAP3_HS_USB_PORTS]`, `unsigned phy_reset:1`; struct ohci_hcd_omap_platform_data fields
include `enum usbhs_omap_port_mode port_mode[OMAP3_HS_USB_PORTS]`, `unsigned es2_compatibility:1`;
struct usbhs_omap_platform_data fields include `int nports`, `enum usbhs_omap_port_mode
port_mode[OMAP3_HS_USB_PORTS]`, `int reset_gpio_port[OMAP3_HS_USB_PORTS]`, `struct regulator
*regulator[OMAP3_HS_USB_PORTS]`, `struct ehci_hcd_omap_platform_data *ehci_data`, `struct
ohci_hcd_omap_platform_data *ohci_data`, `unsigned single_ulpi_bypass:1`, `unsigned
es2_compatibility:1`; struct omap_musb_board_data fields include `u8 interface_type`, `u8 mode`,
`u16 power`, `unsigned extvbus:1`, `void (*set_phy_power)(u8 on)`, `void (*clear_irq)(void)`, `void
(*set_mode)(u8 mode)`, `void (*reset)(void)`. Important enum details: enum usbhs_omap_port_mode
values include `OMAP_USBHS_PORT_MODE_UNUSED`, `OMAP_EHCI_PORT_MODE_PHY`, `OMAP_EHCI_PORT_MODE_TLL`,
`OMAP_EHCI_PORT_MODE_HSIC`, `OMAP_OHCI_PORT_MODE_PHY_6PIN_DATSE0`,
`OMAP_OHCI_PORT_MODE_PHY_6PIN_DPDM`, `OMAP_OHCI_PORT_MODE_PHY_3PIN_DATSE0`,
`OMAP_OHCI_PORT_MODE_PHY_4PIN_DPDM`; enum musb_interface values include `MUSB_INTERFACE_ULPI`,
`MUSB_INTERFACE_UTMI`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/usb-tusb6010.c`, `sources/distributed-fs/ceph-client/drivers/mfd/omap-
usb-tll.c`, `sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-host.c`, `sources/distributed-
fs/ceph-client/drivers/usb/host/ehci-omap.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/usb-tusb6010.c`, `sources/distributed-fs/ceph-client/drivers/mfd/omap-
usb-tll.c`, `sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-host.c`, `sources/distributed-
fs/ceph-client/drivers/usb/host/ehci-omap.c`, `sources/distributed-fs/ceph-
client/drivers/usb/musb/omap2430.h`, `sources/distributed-fs/ceph-
client/drivers/usb/musb/musb_dsps.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap.h` completely for this pass (74 lines, 1981 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap.h_research.md`.
