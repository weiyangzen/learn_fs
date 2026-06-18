# sources/distributed-fs/ceph-client/drivers/gpu/drm/sitronix/Kconfig

Purpose: declares build-time configuration for Sitronix DRM panel/controller drivers: ST7567/ST7571 core plus I2C/SPI transports, ST7586, ST7735R/ST7715R, and ST7920.

Important entries: `DRM_ST7571` is the common ST7567/ST7571 DRM core and selects shmem GEM, KMS helpers, client setup, and videomode helpers. `DRM_ST7571_I2C` and `DRM_ST7571_SPI` depend on the core and select appropriate regmap support. `DRM_ST7586` and `DRM_ST7735R` depend on SPI and select DMA GEM plus MIPI DBI. `DRM_ST7920` depends on DRM, SPI, and MMU and selects shmem GEM, KMS helpers, and REGMAP_SPI.

Control flow: Kconfig only controls symbol visibility and module selection. Bus wrappers are intentionally separate from the ST7571 core, so selecting the core alone does not bind hardware.

State and persistence: no runtime state. The selected symbols decide module objects and helper dependencies.

Dependencies and integration: integrates with the DRM menu, SPI/I2C stacks, regmap, MIPI DBI, backlight support for ST7735R, and DRM client setup for fbdev/emulation clients.

Risks: users must select the matching ST7571 bus driver or no transport will probe. Help text mentions ST7565 in transport descriptions while the compatible/core naming is ST7567/ST7571, which may confuse configuration audits.

Test signals: compile coverage with each symbol as built-in and module, especially the split ST7571 namespace import/export relationship.
