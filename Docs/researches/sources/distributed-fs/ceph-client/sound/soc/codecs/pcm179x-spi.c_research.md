# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x-spi.c

Purpose: provides the SPI transport wrapper for the shared TI PCM179x codec core.

Important APIs, types, and functions: `pcm179x_spi_probe()` initializes an SPI regmap using `pcm179x_regmap_config` and calls `pcm179x_common_init()`. It binds OF compatible `ti,pcm1792a` and SPI IDs `pcm1792a` and `pcm179x`.

Control flow: probe allocates only the regmap and delegates all codec registration and behavior to the common core. Module registration uses `module_spi_driver()`.

State and persistence: no SPI-specific private state. The shared core owns state and component registration through device-managed resources.

Dependencies and integration points: depends on SPI, OF, regmap, and `pcm179x.h`. It allows the same codec programming path as I2C while using `devm_regmap_init_spi()`.

Risks: shared regmap configuration must be valid for SPI framing on all supported PCM179x variants. There is no remove hook, matching the common core's lack of deferred resources. OF compatible is narrow.

Test signals: SPI probe by ID and OF compatible, regmap allocation failure path, shared component registration, and playback format/mute/volume testing over SPI.
