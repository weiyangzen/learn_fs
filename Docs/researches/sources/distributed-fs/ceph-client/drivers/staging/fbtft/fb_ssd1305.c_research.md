<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1305.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1305.c

Purpose: supports SSD1305 OLED controllers with monochrome packing and contrast-as-gamma.

Important APIs/types/functions: `init_display()` configures display clock, multiplex, charge pump, addressing, COM pins, precharge, normal display, and display on. `set_addr_win()`, `write_vmem()`, `blank()`, and `set_gamma()` implement page addressing, RGB565-to-1bpp conversion, display on/off, and contrast.

Control flow: init sets a default contrast in `par->gamma.curves[0]` under lock when unset. Updates pack the whole framebuffer in vertical byte order and write it with DC high.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: write_reg caveat requires command/value pairs as separate calls because DC must stay low. Rotation only affects segment/COM choices in init/addressing. Any nonzero pixel is on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1305.c -->
