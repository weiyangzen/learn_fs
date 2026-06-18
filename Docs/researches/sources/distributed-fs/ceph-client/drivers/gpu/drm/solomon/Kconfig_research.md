# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/Kconfig

Purpose: declares configuration symbols for the Solomon/Sino Wealth SSD13xx/SH110x DRM OLED driver core and bus transports.

Important entries: `DRM_SSD130X` is the common core and selects backlight, DRM client setup, shmem GEM, and KMS helpers. `DRM_SSD130X_I2C` depends on the core and I2C and selects REGMAP_I2C. `DRM_SSD130X_SPI` depends on the core and SPI and selects generic REGMAP.

Control flow: selecting only the core builds shared logic but requires a bus transport for hardware binding.

State and persistence: no runtime state.

Dependencies and integration: integrates with DRM, MMU, backlight, I2C/SPI, and regmap Kconfig dependency closure.

Risks: SPI transport uses custom regmap callbacks rather than REGMAP_SPI, so the generic REGMAP select is intentional. Users can misconfigure by enabling the core without a transport.

Test signals: compile combinations for core-only, I2C, SPI, and both transports.
