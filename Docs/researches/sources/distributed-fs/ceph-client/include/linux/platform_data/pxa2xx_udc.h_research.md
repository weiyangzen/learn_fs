# sources/distributed-fs/ceph-client/include/linux/platform_data/pxa2xx_udc.h

## Purpose
`pxa2xx_udc.h` is a Linux kernel Marvell PXA platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct pxa2xx_udc_mach_info` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `PXA2XX_UDC_H`, `pxa27x_clear_otgph`. Types: `struct pxa2xx_udc_mach_info`.
Declared or inline functions: `int`, `void`, `pxa27x_clear_otgph`. Important struct details: struct
pxa2xx_udc_mach_info fields include `int (*udc_is_connected)(void)`, `void (*udc_command)(int cmd)`,
`bool gpio_pullup_inverted`, `int gpio_pullup`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/udc.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/pxa27x_udc.c`, `sources/distributed-
fs/ceph-client/drivers/usb/gadget/udc/pxa25x_udc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/udc.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/pxa27x_udc.c`, `sources/distributed-
fs/ceph-client/drivers/usb/gadget/udc/pxa25x_udc.c`, `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-pxa27x.c`. It integrates through `struct platform_device` platform
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/pxa2xx_udc.h` completely for this pass (34 lines, 1101 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/pxa2xx_udc.h_research.md`.
