<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1289.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1289.c

Purpose: supports SSD1289 240x320 16-bit-register LCD controllers.

Important APIs/types/functions: `reg11` module parameter seeds display-control register `0x11`. `init_display()`, `set_addr_win()`, `set_var()`, and `set_gamma()` configure controller registers, cursor, rotation, and two 10-value gamma curves.

Control flow: init writes the ITDB02-derived register sequence and enters RAM data write. `set_var()` avoids touching register `0x11` if the init hook has been replaced by platform data, preventing override of custom init.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: module parameter `reg11` can alter scan/color behavior. No device ID read. Rotation depends on register `0x11` bits matching the panel wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1289.c -->
