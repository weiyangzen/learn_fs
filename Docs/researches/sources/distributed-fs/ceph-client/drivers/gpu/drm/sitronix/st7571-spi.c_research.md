# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/st7571-spi.c

Purpose: SPI transport wrapper for the shared ST7567/ST7571 DRM core.

Important APIs and types: `st7571_spi_regmap_config` configures an 8-bit register/value SPI regmap with multi-write support. `st7571_spi_probe()` initializes regmap with `devm_regmap_init_spi()`, calls `st7571_probe()`, and stores the core pointer as SPI driver data. OF and SPI IDs cover `st7567` and `st7571`.

Control flow: probe delegates all device parsing, DRM object creation, and display initialization to the core. remove retrieves the stored pointer and calls `st7571_remove()`.

State and persistence: no local persistent runtime state beyond SPI driver data and the regmap owned by devres.

Dependencies and integration: depends on SPI regmap and the ST7571 core export namespace. It binds to `sitronix,st7567` and `sitronix,st7571`.

Risks: as with the I2C wrapper, the error message after a failed core probe says regmap initialization failed. Multi-write support is enabled, but the core still uses many single-byte writes in update paths because of controller limitations noted in comments.

Test signals: SPI probe/remove, module autoload via SPI IDs, and core namespace import should be validated along with display updates through the shared core.
