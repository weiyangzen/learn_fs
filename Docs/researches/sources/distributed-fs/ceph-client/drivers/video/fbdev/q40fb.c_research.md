# sources/distributed-fs/ceph-client/drivers/video/fbdev/q40fb.c

Purpose: implements a minimal fbdev driver for the Q40 m68k machine framebuffer. It exposes a fixed 1024x512 16-bpp truecolor framebuffer at the Q40 physical screen address.

Important APIs/types/functions: `q40fb_fix` describes fixed framebuffer properties: id `Q40`, 1 MiB memory, packed pixels, truecolor, 2048-byte lines, and no acceleration. `q40fb_var` describes the fixed mode and RGB bitfields. `q40fb_setcolreg` fills the 16-entry pseudo palette for truecolor console use. `q40fb_probe` allocates/registers fbdev and enables display hardware. `q40fb_init` registers both a platform driver and synthetic platform device.

Control flow: module init exits if fb options disable `q40fb`, then registers the platform driver and platform device. Probe rejects non-Q40 machines with `MACH_IS_Q40`, sets `smem_start` to `0xFE800000`, allocates `fb_info` with space for a 16-entry pseudo palette, copies fixed/variable mode data, points `screen_base` at the already mapped physical screen address, allocates a 256-entry cmap, writes display control via `master_outb(3, DISPLAY_CONTROL_REG)`, and registers the framebuffer.

State and persistence: state is limited to static fixed/variable descriptors, one allocated `fb_info`, the pseudo palette stored in `info->par`, the cmap, and the Q40 display control register. There is no remove path or dynamic mode state. Framebuffer contents persist in physical screen memory while the machine is running.

Dependencies and integration: depends on m68k Q40 platform macros/register access (`MACH_IS_Q40`, `master_outb`, `DISPLAY_CONTROL_REG`), fbdev default I/O-memory ops, platform-device registration, and fixed early mapping from Q40 setup code.

Risks: no remove/unregister path is present because this is effectively a built-in style platform driver. `screen_base` is assigned from the physical address cast to a pointer, relying on Q40 setup mapping. Color bitfields are unusual (`red` offset 6, `green` 11, `blue` 0 with 6 blue bits), so palette conversion must match hardware. The driver accepts color register numbers up to 255 but only uses pseudo palette entries below 16.

Test signals: build for Q40/m68k, boot on Q40 or emulator with `MACH_IS_Q40`, verify fbdev registration, visible 1024x512 output, correct fbcon colors through pseudo palette, cmap allocation, and display enable register side effect. Negative signal is probe returning `-ENXIO` on non-Q40 systems.
