# sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a-i2c.c

Purpose: I2C wrapper for the ROHM/Kionix KX022A/KX132/KX134 accelerometer core. It requires an IRQ, selects chip-specific metadata from match data, creates the regmap, and delegates to `kx022a_probe_internal()`.

Important APIs and flow: `kx022a_i2c_probe()` rejects devices with no IRQ, obtains `const struct kx022a_chip_info *` from I2C/OF match data, initializes `devm_regmap_init_i2c()` with the chip-specific regmap config, then calls the shared probe. ID and OF tables map five chip names to exported chip-info structures. The driver uses asynchronous probe preference and imports namespace `IIO_KX022A`.

State, dependencies, risks, and tests: no local state persists beyond devm regmap registration. Dependencies are I2C, regmap, IRQ firmware description, I2C/OF match-data plumbing, and the shared KX022A core. Risks include hard failure on missing IRQ even for direct-read-only use cases, match data being mandatory, and regmap config differing by chip family. Test signals include module autoload, no-IRQ rejection, match-data selection for each compatible, regmap initialization, and shared probe success.
