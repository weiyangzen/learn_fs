<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1331.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1331.c

Purpose: supports SSD1331 96x64 color OLEDs with a custom command/data register writer and 63-entry grayscale gamma table.

Important APIs/types/functions: `init_display()` configures remap/color depth, address offsets, precharge, contrast, and display-on. `write_reg8_bus8()` sends the first byte as command then remaining bytes as data. `set_gamma()` accumulates 63 relative gamma entries into SSD1331 lookup values. `blank()` toggles display.

Control flow: initialization sets orientation partly from `rotate == 180`, then FBTFT updates use column/row address commands. Gamma validation enforces monotonically increasing accumulated values <=180.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: rotation handling in init only distinguishes 180 from others; no `set_var()` hook for runtime rotation. Gamma write is very long and easy to break if `gamma_len` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1331.c -->
