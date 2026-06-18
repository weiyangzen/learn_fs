<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8353d.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8353d.c

Purpose: supports 128x160 HX8353D LCD controllers using MIPI-style command registers and a single custom gamma curve.

Important APIs/types/functions: `init_display()` enables extended commands, power/VCOM/pixel format, sleep-out/display-on, and LUT programming. `set_var()` writes MADCTL rotation/BGR. `set_gamma()` writes register `0xE0` with 19 values.

Control flow: initialization resets, waits, configures panel power and RGB LUT, then enables normal display. Rotation updates only MADCTL; FBTFT core performs memory writes.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: gamma values are not masked before register writes, unlike many sibling drivers. Fixed 128x160 geometry may not cover panel variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8353d.c -->
