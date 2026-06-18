# sources/distributed-fs/ceph-client/include/linux/platform_data/s3c-hsotg.h

## Purpose
`s3c-hsotg.h` is a Linux kernel Samsung S3C platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct dwc2_hsotg_plat`; enumerations such as `enum dwc2_hsotg_dmamode` into the matching
driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_USB_S3C_HSOTG_H`. Types: `struct dwc2_hsotg_plat`, `enum
dwc2_hsotg_dmamode`. Declared or inline functions: `int`, `dwc2_hsotg_set_platdata`. Important
struct details: struct dwc2_hsotg_plat fields include `enum dwc2_hsotg_dmamode dma`, `unsigned int
is_osc:1`, `int phy_type`, `int (*phy_init)(struct platform_device *pdev, int type)`, `int
(*phy_exit)(struct platform_device *pdev, int type)`. Important enum details: enum
dwc2_hsotg_dmamode values include `S3C_HSOTG_DMA_NONE`, `S3C_HSOTG_DMA_ONLY`, `S3C_HSOTG_DMA_DRV`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/drivers/usb/dwc2/platform.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/drivers/usb/dwc2/platform.c`. It integrates through
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/s3c-hsotg.h` completely for this pass (39 lines, 1064 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/s3c-hsotg.h_research.md`.
