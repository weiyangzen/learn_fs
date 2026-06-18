<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8347d.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8347d.c

Purpose: supports HX8347D 320x240 LCD controllers with custom power, address-window, rotation, and gamma programming.

Important APIs/types/functions: `init_display()`, `set_addr_win()`, `set_var()`, and `set_gamma()` are the key hooks. Gamma uses two 14-value curves and masks per register width.

Control flow: reset is followed by drive-strength, power, oscillator, pixel-format, and display-on commands. Address windows program x/y start/end registers then issue GRAM write register `0x22`; rotation uses register `0x16`.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: gamma all-zero input is treated as skip, so a user cannot intentionally write all-zero gamma. Window setup assumes controller coordinates match the configured 320x240 geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8347d.c -->
