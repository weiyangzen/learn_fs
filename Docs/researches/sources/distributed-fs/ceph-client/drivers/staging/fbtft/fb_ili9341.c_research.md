<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9341.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9341.c

Purpose: supports ILI9341 LCD panels over SPI, using FBTFT's SPI-specific registration macro and gamma sysfs support.

Important APIs/types/functions: `init_display()` sends MI0283QT-9A startup commands. `set_var()` writes MADCTL bits. `set_gamma()` writes positive/negative 15-value gamma tables. Display metadata sets `txbuflen` to 4 pages.

Control flow: probe registers an SPI/platform-compatible driver. Initialization soft-resets, powers/configures display, exits sleep, then display-on. Rotation and gamma are applied through FBTFT operations.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: the header comments mention 9-bit SPI emulation, but the file does not expose a local emulate parameter. Gamma values are not masked here, so invalid sysfs gamma may reach hardware registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9341.c -->
