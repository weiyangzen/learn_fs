<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tls8204.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tls8204.c

Purpose: drives TLS8204 monochrome 84x48 LCDs from an RGB565 framebuffer, similar to PCD8544 but with TLS8204 addressing.

Important APIs/types/functions: `init_display()` configures extended mode, bias `bs`, display line address, and normal display. `set_addr_win()`, `write_vmem()`, and `set_gamma()` manage addressing, page-row packing, and contrast.

Control flow: updates iterate six 8-pixel rows, set page/column before each row because controller memory is larger than visible LCD, pack pixels MSB-first, set DC high, and write one row at a time.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: only contrast/bias are tunable. Nonzero pixels become on. Full-row writes ignore partial update regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tls8204.c -->
