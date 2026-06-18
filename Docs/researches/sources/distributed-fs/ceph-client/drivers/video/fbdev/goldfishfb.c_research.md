<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/goldfishfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/goldfishfb.c

Purpose: implements a platform fbdev driver for the Goldfish virtual framebuffer used by Android/emulator-style virtual platforms.

Important APIs, types, and functions: MMIO offsets cover width/height discovery, interrupt status/enable, framebuffer base update, rotation, blanking, and physical size. `struct goldfish_fb` embeds `struct fb_info`, register base, IRQ, spinlock, wait queue, base-update counter, rotation, and pseudo-palette. `goldfish_fb_interrupt()` handles `FB_INT_BASE_UPDATE_DONE` and wakes waiters. `goldfish_fb_check_var()` restricts modes to the host-reported dimensions, rotation parity, fixed xoffset, bpp, and grayscale. `goldfish_fb_set_par()` updates line length and writes rotation. `goldfish_fb_pan_display()` writes a new base and waits briefly for interrupt completion. `goldfish_fb_probe()` maps MMIO, reads geometry, allocates coherent DMA memory for two screens, requests IRQ, enables base-update interrupts, pans once, and registers fbdev.

Control flow: platform probe initializes state from device registers and coherent DMA memory. Runtime fbdev pan writes `FB_SET_BASE` and waits on `base_update_count`. Interrupts serialize with pan via a spinlock. Remove unregisters fbdev, frees IRQ, frees coherent memory, and releases the container.

State and persistence: persistent state is in the allocated `goldfish_fb` object, including embedded `fb_info`, 16-entry pseudo-palette, current rotation, and completion counter. The framebuffer is coherent DMA memory whose physical address is handed to the device.

Dependencies and integration points: depends on platform device resources, OF compatible `google,goldfish-fb`, ACPI ID `GFSH0004`, DMA coherent allocation, fbdev core, and interrupt delivery from the virtual device.

Risks: `goldfish_fb_pan_display()` waits only `HZ/15` and logs timeout but still returns success. Blank only handles normal and unblank modes. Rotation changes force line length to `xres * 2`, which is tailored to fixed 16 bpp. Probe embeds `fb_info` in a manually allocated object rather than using `framebuffer_alloc()`, so lifetime must remain carefully paired.

Test signals: probe/remove on OF and ACPI devices, DMA allocation failure, IRQ timeout during pan, rotate parity validation, ypan over two virtual screens, blank/unblank register writes, and interrupt handler behavior for zero/nonzero status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/goldfishfb.c -->
