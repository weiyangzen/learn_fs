<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_pcd8544.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_pcd8544.c

Purpose: drives PCD8544/Nokia 5110-style 84x48 monochrome LCDs from an RGB565 framebuffer.

Important APIs/types/functions: `init_display()` configures extended/basic instruction modes, temperature coefficient `tc`, bias `bs`, and display mode. `set_addr_win()`, `write_vmem()`, and `set_gamma()` implement addressing, RGB565-to-1bpp packing, and contrast.

Control flow: full updates reset X/Y RAM address, pack each vertical 8-pixel bank from framebuffer into bytes, set DC high, and write 504 bytes. Gamma writes Vop contrast in extended mode.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: any nonzero RGB565 pixel becomes on, so grayscale/color information is discarded. `set_addr_win()` ignores requested region and full-frame write_vmem is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_pcd8544.c -->
