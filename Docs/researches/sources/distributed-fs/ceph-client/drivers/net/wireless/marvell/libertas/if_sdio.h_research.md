# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_sdio.h

## Purpose
Defines SDIO register offsets, interrupt bit masks, status bits, firmware status values, RX length/unit registers, event register location, block size, and deep-sleep wake register bits used by `if_sdio.c`.

## Important Definitions
Key registers include `IF_SDIO_IOPORT`, host interrupt mask/status registers, `IF_SDIO_RD_BASE`, `IF_SDIO_STATUS`, scratch/status registers, `IF_SDIO_RX_LEN`, `IF_SDIO_RX_UNIT`, and `IF_SDIO_EVENT`. Important status bits are `IF_SDIO_IO_RDY`, `IF_SDIO_DL_RDY`, and `IF_SDIO_FIRMWARE_OK`. `IF_SDIO_BLOCK_SIZE` is the normal post-firmware transfer block size. `CONFIGURATION_REG` and `HOST_POWER_UP` support deep-sleep wake.

## Control Flow And State
No runtime code is present. The constants drive state polling in firmware download, packet-length discovery, interrupt masking/clearing, and deep-sleep transitions.

## Dependencies And Integration
Included only by the SDIO transport. It encodes hardware ABI values and must remain consistent with Marvell SDIO firmware expectations.

## Risks And Test Signals
Risks are incorrect register offsets or bit masks causing firmware load hangs, missed interrupts, or invalid packet lengths. Test signals include successful `IF_SDIO_FIRMWARE_OK` polling, upload/download interrupts, RX length decoding for old and newer models, and wake from deep sleep.
