# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514-spi.h

`rt5514-spi.h` defines the RT5514 SPI transport ABI used by `rt5514-spi.c` and `rt5514.c`.

It defines `RT5514_SPI_BUF_LEN` as 240 bytes, DSP voice buffer addresses (`BASE`, `LIMIT`, `WP`), `RT5514_IRQ_CTRL`, `RT5514_IRQ_STATUS_BIT`, SPI command IDs, and prototypes for `rt5514_spi_burst_read()` and `rt5514_spi_burst_write()`.

There is no control flow or storage in this header. The constants are integration points for firmware writes, PLL calibration reads, IRQ-status reads, and DSP capture ring-buffer reads. Risks are caller-side enforcement of 8-byte transfer alignment, firmware ABI coupling of DSP addresses, and build/link dependency on `CONFIG_SND_SOC_RT5514_SPI`. Test signals include SPI-enabled/disabled builds, firmware load, calibration reads, and DSP capture buffer address validation.
