# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5575-spi.c

`rt5575-spi.c` is a small SPI firmware-loader helper for Realtek ALC5575/RT5575. It creates or obtains an SPI device described by the I2C codec node and writes four firmware blobs to fixed DSP addresses with a packed burst-write protocol.

`rt5575_spi_get_device()` parses the `spi-parent` phandle and optional chip-select index, finds the SPI controller, validates the chip select, and creates a new SPI device with modalias `rt5575`. `rt5575_spi_fw_load()` requests four firmware files under `realtek/rt5575/` and writes them to addresses `0x5f400000`, `0x5f600000`, `0x5f7fe000`, and `0x5f7ff000`. The internal `rt5575_spi_burst_write()` chunks transfers into 240-byte frames containing command, little-endian address, payload, and dummy byte.

The file has no long-lived driver state; firmware execution is started by `rt5575.c` after loading. Dependencies are firmware loader, OF APIs, SPI core, and `rt5575-spi.h`. Risks include ignored `spi_write()` return values, full-size writes for short final chunks, no obvious cleanup for a newly created SPI device on later failures, and an unusual `spi-parent` phandle/chip-select encoding. Test signals include DT parsing, invalid chip-select handling, missing firmware failures, all four address writes, SPI failure injection, and integration with RT5575 SPI boot probe.
