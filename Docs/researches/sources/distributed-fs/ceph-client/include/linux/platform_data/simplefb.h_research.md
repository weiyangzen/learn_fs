# sources/distributed-fs/ceph-client/include/linux/platform_data/simplefb.h

## Purpose
`simplefb.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct simplefb_format` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_SIMPLEFB_H__`, `SIMPLEFB_FORMATS`. Types: `struct
simplefb_format`, `struct simplefb_platform_data`. Declared or inline functions: none visible in
this header. Important struct details: struct simplefb_format fields include `const char *name`,
`u32 bits_per_pixel`, `struct fb_bitfield red`, `struct fb_bitfield green`, `struct fb_bitfield
blue`, `struct fb_bitfield transp`, `u32 fourcc`; struct simplefb_platform_data fields include `u32
width`, `u32 height`, `u32 stride`, `const char *format`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/n64/init.c`, `sources/distributed-fs/ceph-client/include/linux/sysfb.h`,
`sources/distributed-fs/ceph-client/drivers/mfd/ls2k-bmc-core.c`, `sources/distributed-fs/ceph-
client/drivers/firmware/google/framebuffer-coreboot.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `drm/drm_fourcc.h`, `linux/fb.h`, `linux/types.h`. Direct source-tree consumers found by
include search are `sources/distributed-fs/ceph-client/arch/mips/n64/init.c`, `sources/distributed-
fs/ceph-client/include/linux/sysfb.h`, `sources/distributed-fs/ceph-client/drivers/mfd/ls2k-bmc-
core.c`, `sources/distributed-fs/ceph-client/drivers/firmware/google/framebuffer-coreboot.c`,
`sources/distributed-fs/ceph-client/drivers/firmware/sysfb_simplefb.c`, `sources/distributed-
fs/ceph-client/drivers/firmware/sysfb.c`, `sources/distributed-fs/ceph-
client/drivers/video/fbdev/simplefb.c`, `sources/distributed-fs/ceph-
client/drivers/gpu/drm/sysfb/simpledrm.c`. It integrates through `struct platform_device` platform
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/simplefb.h` completely for this pass (62 lines, 2258 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/simplefb.h_research.md`.
