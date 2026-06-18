<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tinylcd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tinylcd.c

Purpose: implements a custom 320x480 tinylcd.com panel initialization and rotation mapping.

Important APIs/types/functions: `init_display()` writes a vendor command sequence including power, frame, display function, gamma-like commands, RGB565 pixel format, sleep-out, and display-on. `set_var()` writes rotation-specific display function and address mode values.

Control flow: after reset the driver programs fixed panel registers, sleeps 250 ms after exit-sleep, and enables display. Runtime rotation rewrites registers `0xB6` and MADCTL.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: panel-specific magic values and no gamma hook. Module aliases are SPI-only beyond FBTFT registration compatible string; platform alias is absent compared with many siblings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tinylcd.c -->
