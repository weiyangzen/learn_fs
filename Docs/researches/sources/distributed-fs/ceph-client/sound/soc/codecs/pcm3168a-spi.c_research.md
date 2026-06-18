# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a-spi.c

Purpose: SPI bus driver for the PCM3168A shared codec core. It initializes a SPI regmap and connects SPI matching/removal/runtime PM to the common implementation.

Important APIs and functions: `pcm3168a_spi_probe()` creates `devm_regmap_init_spi(spi, &pcm3168a_regmap)` and calls `pcm3168a_probe(&spi->dev, regmap)`. `pcm3168a_spi_remove()` delegates to `pcm3168a_remove()`. Matching uses SPI ID `pcm3168a` and OF compatible `ti,pcm3168a`; `.pm` uses `pcm3168a_pm_ops`.

Control flow: all codec behavior is in `pcm3168a.c`; this file is the SPI transport adapter. Probe failure returns directly from regmap/core calls.

State and persistence: only devres-managed regmap is created here. Core private data persists in the device drvdata.

Dependencies and integration points: Linux SPI, regmap, ALSA SoC, OF module tables, and the shared header.

Risks: no SPI-specific mode constraints are set here; board data and regmap defaults must match device requirements. Runtime PM correctness depends on shared core remove/resume/suspend.

Test signals: instantiate on SPI, validate register reads/writes, runtime suspend/resume, and parity with the I2C transport.
