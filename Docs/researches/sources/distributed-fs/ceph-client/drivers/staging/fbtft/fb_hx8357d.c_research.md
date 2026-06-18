<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.c

Purpose: supports HX8357D 320x480 LCDs with an Adafruit-derived initialization sequence.

Important APIs/types/functions: `init_display()` uses command constants from `fb_hx8357d.h`; `set_var()` computes HX8357D MADCTL bits. Display metadata exposes two 14-value gamma curves but this file has no runtime `set_gamma()` hook.

Control flow: reset and soft reset are followed by extended command unlock, RGB/COM/oscillator/panel/power/timing/gamma constants, pixel format, TE configuration, sleep-out, and display-on. Rotation writes MIPI address mode.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: BGR logic is inverted-looking: `par->bgr ? RGB : BGR`, so panel color validation is important. Static gamma in init cannot be changed through FBTFT gamma hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.c -->
