<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.h

Purpose: Main private header for the viafb fbdev front end. It aggregates key headers, declares driver version, shared/private framebuffer state structures, global output flags, LVDS I2C helpers, and PCI-facing fbdev entry points.

Important APIs/types/functions: `struct viafb_shared` holds IGA output masks, procfs entries, `viafb_dev`, probed aux I2C buses, shared TMDS/LVDS/chip info, hardware cursor/VQ offsets, and the acceleration `hw_bitblt` callback. `struct viafb_par` holds per-framebuffer depth, VRAM offset, physical framebuffer accounting, IGA path, pointer to shared state, and deprecated direct pointers into shared chip settings. Prototypes include `viafb_gpio_i2c_read_lvds()`, `viafb_gpio_i2c_write_mask_lvds()`, `via_fb_pci_probe()`, `via_fb_pci_remove()`, `viafb_init()`, and `viafb_exit()`.

Control flow and state: No executable flow in the header. The structures describe persistent per-driver and per-fb state allocated by `via_fb_pci_probe()` and later consumed by fb_ops, LCD/DVI setup, acceleration, procfs, and PM paths.

Dependencies and integration points: Includes Linux fb/proc/spinlock headers and viafb subsystem headers (`via_aux.h`, `ioctl.h`, `share.h`, `chip.h`, `hw.h`). It is the main contract between `via-core.c` and `viafbdev.c`. Risks include global singleton assumptions, duplicated state pointers marked deprecated, and storing physical framebuffer addresses in `unsigned int`. Test signals are structure layout compile coverage, dual-fb state separation, and correct shared pointer use after framebuffer allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viafbdev.h -->
