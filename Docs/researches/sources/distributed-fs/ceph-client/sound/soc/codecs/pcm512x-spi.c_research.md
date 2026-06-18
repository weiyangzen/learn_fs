# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x-spi.c

Purpose: SPI wrapper for the PCM512x/PCM514x/PCM5242 shared codec core. It initializes the SPI regmap, delegates probe/remove, and attaches shared runtime PM ops.

Important APIs and functions: `pcm512x_spi_probe()` calls `devm_regmap_init_spi(spi, &pcm512x_regmap)` and `pcm512x_probe(&spi->dev, regmap)`. `pcm512x_spi_remove()` calls `pcm512x_remove()`. Matching supports `pcm5121`, `pcm5122`, `pcm5141`, `pcm5142`, and `pcm5242`.

Control flow: SPI core calls probe; the shared core handles reset, supplies, optional SCLK, DAI/PLL/control registration, and PM. Remove unwinds through the core.

State and persistence: transport state is devres regmap plus core private data in drvdata. No bus-specific mutable state is kept here.

Dependencies and integration points: Linux SPI, regmap, ALSA SoC through `pcm512x.h`, and OF matching.

Risks: unlike the I2C wrapper, this wrapper does not include TAS5754/TAS5756 IDs. SPI mode and timing are not set here and depend on board/controller configuration.

Test signals: SPI bind/probe, regmap read/write, shared runtime PM, playback DAI setup, and ID/OF matching coverage.
