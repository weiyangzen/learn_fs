# sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a-spi.c

Purpose: SPI wrapper for the ROHM/Kionix KX022A/KX132/KX134 accelerometer core. It mirrors the I2C wrapper but initializes a SPI regmap.

Important APIs and flow: `kx022a_spi_probe()` rejects missing IRQ, obtains chip info with `spi_get_device_match_data()`, creates `devm_regmap_init_spi()` using the chip-specific config, and delegates to `kx022a_probe_internal()`. SPI ID and OF tables cover the same five supported chip-info structures as I2C, and the driver prefers asynchronous probe.

State, dependencies, risks, and tests: all device state is in the core. Dependencies are SPI, regmap, IRQ configuration, OF/SPI match data, and namespace `IIO_KX022A`. Risks include mandatory IRQ requirement, chip-info mismatch with SPI ID/compatible, and protocol support depending on generic regmap SPI behavior. Test signals include SPI/OF autoload, no-IRQ failure, regmap setup, chip-info-specific WHO_AM_I validation in the core, and trigger/FIFO operation over SPI.
