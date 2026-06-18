# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575-spi.h

`rt5575-spi.h` is the optional SPI firmware-loading interface for RT5575.

When `CONFIG_SND_SOC_RT5575_SPI` is enabled it declares `rt5575_spi_get_device()` and `rt5575_spi_fw_load()`. Otherwise it provides inline stubs returning `NULL` and `-EINVAL`, allowing the I2C codec driver to compile while rejecting SPI boot mode at runtime.

There is no runtime state in the header. The integration point is compile-time selection between real SPI helper and stubs. Risks include ambiguous ownership of the returned `spi_device` and dependence on explicit config checks in `rt5575.c`. Test signals are enabled/disabled config builds and SPI-boot probe behavior for both real and stubbed helper paths.
