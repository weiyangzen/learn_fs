## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lg-lg4573.c

Purpose: This is a SPI-controlled DRM DPI panel driver for LG4573-based 480x800 LCD panels. It sends DCS-like 16-bit SPI command/data words for display, power, and gamma configuration, and exposes a fixed DPI mode through DRM.

Important APIs, types, and functions: `struct lg4573` stores the DRM panel, SPI device, and an unused `videomode` field. `lg4573_spi_write_u16()` writes a big-endian 16-bit word over SPI; command words use `0x70xx`, data words use `0x72xx`. `lg4573_display_mode_settings()`, `lg4573_power_settings()`, and `lg4573_gamma_settings()` send static u16 arrays. `lg4573_init()` runs those three blocks. `lg4573_enable()` initializes and then sends exit-sleep/display-on. `lg4573_disable()` sends display-off, waits 120 ms, and enters sleep. `lg4573_get_modes()` exposes the default 480x800 mode.

Control flow: Probe allocates a DPI panel, stores SPI drvdata, forces `bits_per_word = 8`, calls `spi_setup()`, and adds the panel. Enable is the full initialization path each time DRM enables the panel. Disable is the display-off/sleep path. Remove calls display-off and removes the panel.

State and persistence: Panel register configuration is resent on every enable. The driver does not manage regulators, reset GPIOs, or a backlight, so those states are external. There is no cached enabled state; SPI/DPI panel state persists until sleep or external power/reset.

Dependencies and integration points: The driver uses SPI core, DRM panel/mode APIs, MIPI DCS constants, and OF matching on `lg,lg4573`. It integrates as a DPI connector because pixel data is supplied outside the SPI control channel.

Risks: `lg4573_enable()` ignores the return value of `lg4573_init()` and proceeds to display-on even if configuration writes fail. No power/reset sequencing is present despite including regulator/GPIO headers. Fixed timings may not match all LG4573-attached panels. SPI word format depends on the panel's 9/16-bit command encoding and on SPI controller byte ordering.

Test signals: Tests should verify SPI setup, successful writes of init arrays, one preferred 480x800 mode with 61x103 mm metadata, clean display-off on disable/remove, and visible DPI scanout. Error injection should confirm the ignored init error does not mask real hardware bring-up failures.
