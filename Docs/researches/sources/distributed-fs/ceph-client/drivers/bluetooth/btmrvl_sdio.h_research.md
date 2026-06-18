# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_sdio.h

## Purpose
Defines the Marvell SDIO transport contract used by `btmrvl_sdio.c`: packet framing constants, firmware-transfer limits, register bit masks, card register maps, per-card runtime state, device table metadata, and DMA alignment helpers.

## Important APIs, Types, And Functions
- `SDIO_HEADER_LEN`, `SDIO_BLOCK_SIZE`, `ALLOC_BUF_SIZE`, `MAX_POLL_TRIES`, and `MAX_WRITE_IOMEM_RETRY` define transport sizing, polling, and retry policy.
- Register bits such as `HOST_POWER_UP`, `HOST_CMD53_FIN`, `HIM_ENABLE`, `UP_LD_HOST_INT_STATUS`, `DN_LD_HOST_INT_STATUS`, `DN_LD_CARD_RDY`, `CARD_IO_READY`, and `FIRMWARE_READY` encode the SDIO/firmware handshake.
- `struct btmrvl_sdio_card_reg` describes chip-specific register offsets and interrupt/coredump capabilities.
- `struct btmrvl_sdio_card` stores live per-function state: SDIO function, I/O port, firmware names, register map, feature flags, RX unit, common Marvell private pointer, and wakeup config.
- `struct btmrvl_sdio_device` is the immutable SDIO ID table payload copied into a card at probe.
- `ALIGN_SZ` and `ALIGN_ADDR` support 8-byte DMA-safe SDIO buffers.

## Control Flow
This header has no executable flow, but it drives the flow in the C file. Probe selects a `btmrvl_sdio_device`, which points at a `btmrvl_sdio_card_reg`. Register offsets are then used for function enablement, firmware status checks, firmware block transfer, interrupt masking/clearing, data port I/O, and optional firmware dump reads. Buffer constants determine allocation size and block rounding for RX, TX, and firmware download.

## State And Persistence
The header separates immutable hardware descriptions from mutable runtime state. Register maps and device descriptors are static const data; `btmrvl_sdio_card` persists for the SDIO function lifetime and references common driver state through `priv`. Wake configuration persists only when device tree parsing supplies an IRQ.

## Dependencies And Integration Points
Requires Bluetooth HCI size definitions and kernel bit/alignment helpers through the including C file. It is tightly coupled to `btmrvl_sdio.c` and common Marvell structures from `btmrvl_drv.h`; no public cross-driver API is exposed.

## Risks And Edge Cases
Incorrect register offsets or feature flags can corrupt firmware download, interrupt clearing, or coredump behavior for a whole chip family. `ALLOC_BUF_SIZE` must remain large enough for maximum HCI frames plus SDIO headers and block rounding. Alignment helpers operate on integer-cast addresses, so callers must allocate enough slack before aligning.

## Test Signals
Build coverage should catch structure/member drift against `btmrvl_sdio.c`. Runtime signals are indirect: correct I/O port discovery, RX unit reads, interrupt clearing mode selection, firmware ready polling, and coredump register ranges across every SDIO device-table entry.
