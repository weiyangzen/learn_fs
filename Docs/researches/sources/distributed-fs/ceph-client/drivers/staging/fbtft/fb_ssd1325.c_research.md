<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1325.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1325.c

Purpose: supports SSD1325 128x64 4-bit grayscale OLEDs by converting RGB565 framebuffer data into packed grayscale nibbles.

Important APIs/types/functions: `rgb565_to_g16()`, `init_display()`, `set_addr_win()`, `write_vmem()`, `blank()`, and `set_gamma()` are key. Gamma represents a 15-entry grayscale lookup table.

Control flow: init writes clock/display/addressing/window commands and display-on. Updates iterate columns in pairs, convert two RGB565 pixels to 4-bit grayscale, pack them into one byte, set DC high, and write the whole buffer.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: Kconfig/Makefile selection appears tied to SSD1305 in this snapshot. `set_gamma()` validates all 15 entries but writes only the first 8 values to register `0xB8`, which may be incomplete or controller-specific.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1325.c -->
