# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731-spi.c

Purpose: SPI bus wrapper for the shared WM8731 codec core. It mirrors the I2C wrapper but initializes regmap over SPI and registers through `module_spi_driver()`.

Important APIs/types/functions: `wm8731_spi_probe()` allocates `struct wm8731_priv`, stores it with `spi_set_drvdata()`, creates a regmap using `devm_regmap_init_spi(spi, &wm8731_regmap)`, logs allocation errors, and delegates to `wm8731_init()`. The OF match table uses compatible `wlf,wm8731`; the SPI driver name is `wm8731`.

Control flow: SPI probe handles only transport setup. All codec reset, regulator, clock, control, DAPM, and DAI registration is in the core file. Remove/unload is devm and module framework driven.

State and persistence: no wrapper-local runtime state beyond clientdata and the core private struct. Dependencies include SPI, module infrastructure, shared regmap config, and exported `wm8731_init()`.

Risks: as with I2C, no explicit ID validation is possible here. SPI mode/word settings are not customized in this file, so board descriptions must supply suitable SPI wiring/configuration. Test signals include SPI probe, regmap allocation failure, OF matching, shared init propagation, and basic register writes after reset.
