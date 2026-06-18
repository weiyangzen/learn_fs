# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060-spi.c

Purpose: SPI transport wrapper for the PCM3060 shared codec core. It mirrors the I2C wrapper with SPI regmap initialization and shared probe delegation.

Important APIs and functions: `pcm3060_spi_probe()` allocates `struct pcm3060_priv`, stores it with `spi_set_drvdata()`, initializes `devm_regmap_init_spi(spi, &pcm3060_regmap)`, and calls `pcm3060_probe(&spi->dev)`. Matching is through `pcm3060_spi_id[]` and optional `ti,pcm3060` OF entry.

Control flow: SPI core calls probe; probe creates the control-plane regmap; the shared core performs soft reset, optional single-ended output configuration, and component/DAI registration. No explicit remove callback is present.

State and persistence: persistent transport state is only SPI driver data and regmap. Cached registers and DAI clock state live in `pcm3060_priv` used by the core.

Dependencies and integration points: Linux SPI, regmap, ALSA SoC, and `pcm3060.h`. Machine drivers interact through the DAIs registered by the core.

Risks: the wrapper adds no validation beyond regmap creation. SPI mode/word-size assumptions are left to the SPI/regmap defaults and board setup.

Test signals: bind a SPI PCM3060, confirm regmap initialization, verify shared register defaults and both ADC/DAC DAIs, and compare behavior with the I2C wrapper for parity.
