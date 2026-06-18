# sources/distributed-fs/ceph-client/include/linux/platform_data/video-pxafb.h

## Purpose
`video-pxafb.h` is a Linux kernel display or framebuffer board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct pxafb_mode_info` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `LCD_CONN_TYPE`, `LCD_CONN_WIDTH`, `LCD_TYPE_MASK`, `LCD_TYPE_UNKNOWN`,
`LCD_TYPE_MONO_STN`, `LCD_TYPE_MONO_DSTN`, `LCD_TYPE_COLOR_STN`, `LCD_TYPE_COLOR_DSTN`,
`LCD_TYPE_COLOR_TFT`, `LCD_TYPE_SMART_PANEL`, `LCD_TYPE_MAX`, `LCD_MONO_STN_4BPP`,
`LCD_MONO_STN_8BPP`, `LCD_MONO_DSTN_8BPP`, and 27 more. Types: `struct pxafb_mode_info`, `struct
pxafb_mach_info`. Declared or inline functions: `void`, `pxa_set_fb_info`, `pxafb_smart_queue`,
`pxafb_smart_flush`. Important struct details: struct pxafb_mode_info fields include `u_long
pixclock`, `u_short xres`, `u_short yres`, `u_char bpp`, `unused:22`, `u_char hsync_len`, `u_char
left_margin`, `u_char right_margin`; struct pxafb_mach_info fields include `struct pxafb_mode_info
*modes`, `unsigned int num_modes`, `unsigned int lcd_conn`, `unsigned long video_mem_size`,
`unused:28`, `u_int lccr0`, `u_int lccr3`, `u_int lccr4`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/am300epd.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
pxa/devices.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/fb.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am300epd.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/devices.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c`, `sources/distributed-fs/ceph-
client/drivers/video/fbdev/pxafb.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/video-pxafb.h` completely for this pass (189 lines, 6141 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/video-pxafb.h_research.md`.
