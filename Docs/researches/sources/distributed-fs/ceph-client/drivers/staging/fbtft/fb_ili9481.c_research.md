<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9481.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9481.c

Purpose: supports ILI9481 320x480 LCDs using an FBTFT `init_sequence` array instead of a custom init function.

Important APIs/types/functions: `default_init_sequence` encodes sleep-out, power, VCOM, panel, frame/inversion, pixel format, gamma, and display-on commands. `set_var()` writes MIPI address mode with H/V flip and row/column exchange bits.

Control flow: the FBTFT core interprets the init sequence markers, delays, and commands. Runtime rotation only updates MADCTL.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: init sequence is fixed for one panel family. The HFLIP/VFLIP constants are low-bit values that differ from many MADCTL definitions, so orientation must be verified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9481.c -->
