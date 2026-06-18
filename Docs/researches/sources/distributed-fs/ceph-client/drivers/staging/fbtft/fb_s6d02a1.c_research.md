<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d02a1.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d02a1.c

Purpose: supports S6D02A1 128x160 LCDs through a long fixed vendor initialization sequence.

Important APIs/types/functions: `default_init_sequence` contains unlock, gamma/power, staged sleep-out power-up, address mode, tear, pixel format, gamma curve, display-on, and memory-write commands. `set_var()` writes MIPI address mode.

Control flow: FBTFT core executes the sequence with embedded delays; runtime rotation writes MADCTL bits and common FBTFT paths handle pixel transfer.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: large magic init table is hard to audit and panel-specific. No gamma hook exists despite gamma-like table values in the sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d02a1.c -->
