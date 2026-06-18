<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1351.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1351.c

Purpose: supports SSD1351 128x128 color OLEDs with optional onboard backlight controlled through controller GPIO.

Important APIs/types/functions: `init_display()` conditionally installs `register_onboard_backlight()`, unlocks commands, initializes OLED power/timing/contrast, and displays on. `set_addr_win()`, `set_var()`, `set_gamma()`, `blank()`, and backlight ops handle runtime behavior.

Control flow: if platform data requests `FBTFT_ONBOARD_BACKLIGHT`, the driver registers a raw backlight whose update writes SSD1351 GPIO register `0xB5`. Rotation writes remap register `0xA0`; gamma accumulates 63 values and writes lookup table `0xB8`.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: backlight registration uses the framebuffer device string and must unregister through FBTFT. Gamma validation rejects small increments and accumulated >180. `set_var()` skips when custom init replaces this file's init hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1351.c -->
