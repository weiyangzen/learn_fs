# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x-spi.c

Purpose: 4-wire SPI transport for the shared SSD13xx DRM core, translating regmap command/data control bytes into D/C GPIO state and raw SPI writes.

Important APIs and types: `struct ssd130x_spi_transport` holds `spi_device` and D/C GPIO. `ssd130x_spi_write()` inspects the first byte for `SSD13XX_COMMAND` or `SSD13XX_DATA`, toggles D/C, strips that byte, and writes the remaining payload. `ssd130x_spi_read()` is unsupported. Probe obtains `dc`, allocates transport state, creates a custom regmap, then calls `ssd130x_probe()`.

Control flow: core write helpers call regmap with command/data pseudo-registers. The SPI write handler converts that protocol to hardware D/C signaling. remove and shutdown delegate to the core.

State and persistence: transport state is devm-managed and immutable after probe.

Dependencies and integration: depends on SPI, GPIO, custom regmap callbacks, OF/SPI ID tables, and `DRM_SSD130X` namespace. OF supports SSD1331 in addition to families available over I2C.

Risks: if a write begins with an unexpected control byte, D/C retains its previous state and `spi_write()` still sends data, which could misclassify traffic. The SPI ID table stores numeric variant IDs, but probe relies on OF `device_get_match_data()` through the core; non-OF SPI matching may not provide core match data unless handled elsewhere.

Test signals: command/data toggling on a logic analyzer, SPI ID autoload, SSD1331 binding, unsupported read behavior, and shutdown sequencing.
