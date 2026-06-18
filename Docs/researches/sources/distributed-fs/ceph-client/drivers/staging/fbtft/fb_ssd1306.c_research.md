<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1306.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1306.c

Purpose: supports SSD1306 OLED controllers, including 128x64/128x48/other-height variants and a special 64x48 address window.

Important APIs/types/functions: `init_display()`, `set_addr_win_64x48()`, `set_addr_win()`, `write_vmem()`, `blank()`, and `set_gamma()` configure OLED mode and pack framebuffer data.

Control flow: init sets contrast default, clock, multiplex based on yres, charge pump, vertical addressing, remap/COM, precharge/VCOM, normal mode, and display-on. Updates pack RGB565 nonzero pixels into page bytes and write xres*yres/8 bytes.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: does not reject unsupported rotations; remap is fixed. 64x48 panels need special column/page commands. Contrast values are accepted after masking only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1306.c -->
