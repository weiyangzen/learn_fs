<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7735r.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7735r.c

Purpose: supports ST7735R 128x160 LCDs with an FBTFT init sequence and gamma sysfs hook.

Important APIs/types/functions: `default_init_sequence` covers reset, sleep-out, frame-rate, inversion, power, pixel format, display-on, and normal mode. `set_var()` writes MADCTL rotation/BGR. `set_gamma()` writes positive/negative 16-value gamma curves masked to 6 bits.

Control flow: FBTFT executes the sequence and delays. Runtime rotation/gamma are applied by hooks; memory writes use common MIPI/FBD address paths.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: default init sequence is for one ST7735R panel class; offsets for common tab-color modules are not represented here. Gamma values are masked rather than rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7735r.c -->
