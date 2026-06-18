<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9486.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9486.c

Purpose: supports ILI9486 320x480 LCDs with a PiScreen-matching init sequence.

Important APIs/types/functions: `default_init_sequence` configures interface mode, sleep, RGB565 pixel format, power/VCOM, positive/negative/digital gamma, and display-on. `set_var()` writes rotation-specific address mode values.

Control flow: FBTFT core runs the sequence; this driver then handles rotation updates and relies on common memory-window writes.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: the sequence contains two sleep-out commands and fixed gamma values. No gamma hook exists for calibration. Unsupported rotation default silently does nothing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9486.c -->
