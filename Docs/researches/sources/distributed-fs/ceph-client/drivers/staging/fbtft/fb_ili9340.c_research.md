<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9340.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9340.c

Purpose: supports ILI9340 240x320 LCDs with an Adafruit 2.2-inch style initialization sequence.

Important APIs/types/functions: `init_display()` writes power, VCOM, pixel format, frame-rate, display function, gamma, sleep-out, and display-on commands. `set_var()` writes MADCTL rotation/BGR.

Control flow: reset is followed by vendor command unlock/configuration and MIPI DCS commands. Address-window and memory writes are left to FBTFT core defaults.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: no runtime gamma hook despite fixed gamma writes in init. Rotation mapping differs from ILI9341 and must be validated with panel orientation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9340.c -->
