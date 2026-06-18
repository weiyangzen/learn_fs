<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9320.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9320.c

Purpose: supports ILI9320 240x320 16-bit-register LCDs and warns if the read device code is unexpected.

Important APIs/types/functions: `read_devicecode()` uses the FBTFT read op. `init_display()` programs the application-note power/display/GRAM sequence. `set_addr_win()`, `set_var()`, and `set_gamma()` handle cursor, rotation, BGR, and two 10-value gamma curves.

Control flow: after reset it reads register 0, initializes power and GRAM bounds, turns the display on, then later FBTFT updates set GRAM address and stream pixels through register `0x22`.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: requires a working read operation for meaningful ID warning; write-only configurations will likely read zero. Gamma masking protects bit width, but coordinate code assumes 240x320 geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9320.c -->
