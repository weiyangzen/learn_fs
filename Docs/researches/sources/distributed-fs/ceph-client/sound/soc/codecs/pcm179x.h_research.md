# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x.h

Purpose: declares the shared PCM179x codec interface and supported PCM formats for I2C/SPI wrappers.

Important APIs, types, and functions: defines `PCM1792A_FORMATS` as S32, S24, and S16 little-endian PCM. Declares exported `pcm179x_regmap_config` and `pcm179x_common_init()`.

Control flow support: bus drivers include this header, construct a regmap with the exported config, and call common init to register the ASoC component and DAI.

State and persistence: no state is declared in the header. Common state is private to `pcm179x.c` and is attached to the device.

Dependencies and integration points: included by `pcm179x.c`, `pcm179x-i2c.c`, and `pcm179x-spi.c`. The header assumes including files provide `struct device` and `struct regmap` declarations.

Risks: there is no common exit hook because the core has no deferred work, so future additions that need cleanup must extend the interface. The format macro name is variant-specific and should stay aligned with the DAI in the common core.

Test signals: build both bus wrappers, verify exported symbols resolve in module configurations, and ensure future wrappers use the same regmap/init contract.
