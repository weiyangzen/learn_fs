<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_agm1264k-fl.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_agm1264k-fl.c

Purpose: drives an AGM1264K-FL 128x64 monochrome module made from two KS0108-compatible halves over GPIO parallel lines.

Important APIs/types/functions: `init_display()`, `verify_gpios()`, `request_gpios_match()`, custom `write_reg8_bus8()`, `set_addr_win()`, `write_vmem()`, and GPIO bit-banged `write()` override standard FBTFT paths. It defines gamma and Floyd-Steinberg style diffusion tables for RGB565-to-1bpp conversion.

Control flow: init resets both controller halves and enables display/page/start-line registers. GPIO matching maps `wr`, `cs0`, `cs1`, and `rw`; `write_vmem()` converts framebuffer RGB565 to grayscale, applies gamma and dithering, splits updates across left/right chips, selects command/data mode with RS, and bit-bangs bytes over db0-db7.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: requires many GPIOs and has no hardware read/status wait. A file-static `addr_win` is shared across instances. Per-update allocation and full conversion are costly; dithering/window calculations must avoid crossing the two chip halves incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_agm1264k-fl.c -->
