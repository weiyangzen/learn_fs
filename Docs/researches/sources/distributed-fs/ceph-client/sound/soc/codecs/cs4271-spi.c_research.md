# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271-spi.c

Purpose: SPI transport wrapper for the shared CS4271 ASoC codec core. It adapts the generic CS4271 regmap configuration to the device’s SPI command format and delegates probing to the common codec implementation.

Important APIs and data: `cs4271_spi_probe` copies `cs4271_regmap_config`, sets `reg_bits = 16`, `read_flag_mask = 0x21`, and `write_flag_mask = 0x20`, then calls `cs4271_probe` with `devm_regmap_init_spi`. The `spi_driver` is named `cs4271` and uses `cs4271_dt_ids` for OF matching.

Control flow and state: the wrapper does no state management beyond constructing the SPI regmap and invoking the common probe. The core handles reset GPIO, regulators, MCLK, regcache, DAI controls, suspend/resume, and component registration. Probe errors return directly to SPI core.

Dependencies, risks, and tests: depends on Linux SPI/regmap and `cs4271.h`. The critical integration point is the SPI register protocol: wrong register width or flag masks would make all core register accesses fail or target wrong addresses. There is no local test suite; test signals are SPI bus transactions during common probe, OF modalias binding, and normal CS4271 playback/capture behavior through the common core.
