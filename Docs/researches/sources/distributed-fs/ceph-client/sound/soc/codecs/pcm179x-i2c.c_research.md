# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x-i2c.c

Purpose: provides the I2C transport wrapper for the shared TI PCM179x codec core.

Important APIs, types, and functions: `pcm179x_i2c_probe()` initializes an I2C regmap with `pcm179x_regmap_config` and delegates to `pcm179x_common_init()`. It binds OF compatible `ti,pcm1792a` and I2C ID `pcm179x`.

Control flow: probe does no codec logic beyond regmap creation and common-core registration. There is no remove callback because common state uses device-managed allocation and the PCM179x core has no deferred work cleanup hook.

State and persistence: no I2C-specific persistent state. The common core stores private state in device drvdata.

Dependencies and integration points: depends on I2C, OF, regmap, and `pcm179x.h`. It provides one of two bus front ends for `pcm179x.c`, with SPI handled by `pcm179x-spi.c`.

Risks: only `ti,pcm1792a` is listed in OF despite the generic driver name. Any transport-specific register formatting must be compatible with the shared 8-bit regmap config.

Test signals: I2C probe on compatible hardware, regmap allocation failure, component registration through common init, and playback smoke tests through the shared DAI.
