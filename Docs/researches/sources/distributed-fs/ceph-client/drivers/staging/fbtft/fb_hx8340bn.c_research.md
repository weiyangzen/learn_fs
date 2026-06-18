<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8340bn.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8340bn.c

Purpose: supports HX8340BN 176x220 16-bit color LCDs, including 9-bit SPI or emulated 9-bit transfer via FBTFT.

Important APIs/types/functions: `init_display()` sends extended-command, sleep-out, oscillator, power, drive, pixel-format, and display-on commands. `set_var()` writes MIPI MADCTL rotation/BGR. `set_gamma()` masks and writes GC0 gamma tables. Module parameter `emulate` exists to force emulation.

Control flow: after reset, initialization enables the extended command set, wakes the panel, configures power/drive/pixel format, then turns display on. FBTFT handles address windows while this driver handles rotation and gamma.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: the `emulate` parameter is declared here but actual 9-bit emulation depends on FBTFT core behavior. Gamma curve selection only customizes GC0; nonzero GC selection exits early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8340bn.c -->
