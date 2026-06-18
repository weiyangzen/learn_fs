<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9163.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9163.c

Purpose: supports 128x128 ILI9163 LCD modules, including offsets for panel variants whose controller memory is 128x160.

Important APIs/types/functions: `init_display()`, `set_addr_win()`, `set_var()`, and optional `gamma_adj()` under `GAMMA_ADJ` configure the panel. Constants describe ILI9163C power/frame/gamma commands.

Control flow: initialization resets, exits sleep, sets RGB565, gamma curve, normal mode, power/VCOM/frame controls, column/page ranges, display on, and memory-write mode. Address windows add `__OFFSET` for selected rotations and issue memory-write start.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: compile-time `RED`/`GAMMA_ADJ` switches mean behavior changes at build time rather than runtime. Default branch mutates `var.rotate` if unsupported. The color-space comment and BGR bit use must be validated on real red/black modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9163.c -->
