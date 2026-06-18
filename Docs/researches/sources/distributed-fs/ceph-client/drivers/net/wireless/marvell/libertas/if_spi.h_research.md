# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_spi.h

## Purpose
Defines SPI transport constants for Libertas cards: firmware load sizes and retry limits, SPU register offsets, read/write operation masks, interrupt cause/status bits, device id extraction, and bus mode fields.

## Important Definitions
`IF_SPI_CMD_BUF_SIZE` bounds command/upload buffers. `HELPER_FW_LOAD_CHUNK_SZ`, `FIRMWARE_DNLD_OK`, `MAX_MAIN_FW_LOAD_CRC_ERR`, and `SUCCESSFUL_FW_DOWNLOAD_MAGIC` drive firmware loading. Register constants cover command/data/io ports, scratch registers, interrupt control/status/mask registers, delay read, and bus mode. `IF_SPI_HIST_*`, `IF_SPI_HISM_*`, and `IF_SPI_CIC_*` map interrupt state between host and card.

## Control Flow And State
This header has no executable code. Its constants drive SPU reads/writes, readiness polling, interrupt-mode setup, packet movement, and firmware-success detection in `if_spi.c`.

## Dependencies And Integration
Included by `if_spi.c`; the values are hardware ABI and are also coupled to platform data choices such as dummy clock delay support.

## Risks And Test Signals
Risks are off-by-one buffer assumptions, wrong interrupt masks, or invalid bus mode bit composition. Test signals include stable SPU initialization, correct device id/revision extraction, successful command/data port transfers, and firmware success magic detection.
