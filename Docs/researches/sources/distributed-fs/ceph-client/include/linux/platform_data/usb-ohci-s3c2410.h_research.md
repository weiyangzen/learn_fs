# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-s3c2410.h

## Purpose
`usb-ohci-s3c2410.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct s3c2410_hcd_port` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__ASM_ARCH_USBCONTROL_H`, `S3C_HCDFLG_USED`. Types: `struct s3c2410_hcd_port`,
`struct s3c2410_hcd_info`. Declared or inline functions: `void`, `s3c_ohci_set_platdata`,
`s3c2410_usb_report_oc`. Important struct details: struct s3c2410_hcd_port fields include `unsigned
char flags`, `unsigned char power`, `unsigned char oc_status`, `unsigned char oc_changed`; struct
s3c2410_hcd_info fields include `struct usb_hcd *hcd`, `struct s3c2410_hcd_port port[2]`, `void
(*power_control)(int port, int to)`, `void (*enable_oc)(struct s3c2410_hcd_info *, int on)`, `void
(*report_oc)(struct s3c2410_hcd_info *, int ports)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-s3c2410.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-s3c2410.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-s3c2410.h` completely for this pass (40 lines, 941 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-s3c2410.h_research.md`.
