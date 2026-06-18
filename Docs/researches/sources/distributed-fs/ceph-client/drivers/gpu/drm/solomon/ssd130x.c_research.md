# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x.c

Purpose: shared DRM/KMS driver for Solomon SSD130x, SSD132x, SSD133x, and Sino Wealth SH110x OLED controllers. It provides variant data, property parsing, power sequencing, display initialization, framebuffer conversion, atomic helpers, backlight contrast control, and DRM object setup.

Important APIs and types: exported `ssd130x_variants[]`, `ssd130x_probe()`, `ssd130x_remove()`, and `ssd130x_shutdown()` are the transport ABI. `struct ssd130x_deviceinfo` describes default geometry, clocks, PWM/chargepump needs, page-mode limitations, and family. Family-specific helper arrays select plane, CRTC, and encoder behavior for SSD130X monochrome pages, SSD132X 4-bit grayscale segments, and SSD133X RGB332 color.

Control flow: probe allocates the DRM device, gets variant match data, sets page mode if required, parses `solomon,*` properties, obtains reset GPIO and VCC regulator, registers a backlight, initializes modeset objects, registers DRM, and starts client setup. Encoder enable powers on, initializes the family-specific controller, turns display on, and enables backlight. Plane atomic update begins CPU access, iterates damage, converts XRGB8888 to R1/R8/RGB332 as needed, and writes the family-specific memory layout. Disable clears the display; remove/shutdown call atomic shutdown.

State and persistence: device state includes parsed geometry, offsets, COM/segment remap flags, contrast, clock/precharge/vcom settings, lookup table, cached column/page ranges, reset/regulator/PWM/backlight handles, and DRM objects. Atomic CRTC/plane state owns transient conversion/data buffers.

Dependencies and integration: uses DRM shmem GEM, damage helpers, fixed connector modes, backlight API, PWM, regulator, GPIO, regmap, and firmware properties. Transports provide the regmap protocol.

Risks: family-specific update functions have coordinate range issues: SSD132x/SSD133x row/column end writes use `columns - 1`/`rows - 1` rather than adding x/y starts, which is correct only for zero-origin rectangles. `ssd130x_fb_blit_rect()` ignores `ssd130x_update_rect()` return. `ssd130x_power_off()` disables and puts `pwm` even when no PWM was acquired; API tolerance matters for variants without PWM. Many command writes during enable are serial and fail-fast, but later display-on/backlight calls ignore return values.

Test signals: per-family panel tests should cover page-mode SH1106, horizontal-mode SSD1306, SSD132x grayscale conversion, SSD1331 color conversion, offsets, property defaults/overrides, backlight contrast writes, regulator/PWM failure unwinding, and damage rectangles away from origin.
