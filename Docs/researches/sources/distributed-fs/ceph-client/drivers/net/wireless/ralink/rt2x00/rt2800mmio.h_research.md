# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800mmio.h

## Purpose
Declares the RT2800 MMIO transport interface and the DMA descriptor bitfield layout used by PCI and SoC variants. It maps queue indexes to register offsets and defines TXD/RXD word fields consumed by `rt2800mmio.c`.

## Important APIs, Types, And Functions
The header defines queue register macros `TX_BASE_PTR()`, `TX_MAX_CNT()`, `TX_CTX_IDX()`, and `TX_DTX_IDX()`, descriptor sizes `TXD_DESC_SIZE` and `RXD_DESC_SIZE`, TX descriptor fields `TXD_W0_SD_PTR0`, `TXD_W1_SD_LEN*`, `TXD_W1_DMA_DONE`, `TXD_W3_WIV`, `TXD_W3_QSEL`, and checksum offload bits, plus RX descriptor fields for DMA ownership, CRC/cipher status, frame type, L2 padding, AMPDU, and PLCP/RSSI metadata. It declares all exported MMIO queue, interrupt, descriptor, probe, and radio helpers.

## Control Flow
Bus drivers include this header and wire its declared functions into `struct rt2x00lib_ops` and `struct rt2800_ops`. The descriptor macros are used to initialize outbound DMA rings, clear inbound descriptors for reuse, and translate RX descriptor state into `rxdone_entry_desc` flags before shared rt2x00 RX handling.

## State And Persistence
This header itself stores no runtime state. Its field definitions define the persistent ABI between driver memory descriptors and RT2800 MMIO hardware rings; those descriptors persist across queue lifetime and are reset by queue initialization and clear-entry paths.

## Dependencies And Integration Points
Depends on rt2x00 field macros (`FIELD32`), queue descriptors, `struct rt2x00_dev`, `data_queue`, and interrupt/tasklet types. It is tightly coupled with RT2800 register definitions such as `TX_BASE_PTR0` and `RX_CRX_IDX`, and with `rt2x00mmio` allocation of `queue_entry_priv_mmio`.

## Risks
Descriptor field masks are hardware ABI. A wrong mask or word index corrupts DMA ownership, buffer addresses, or RX status interpretation. `TX_QUEUE_REG_OFFSET` assumes contiguous queue registers; any chip exception must be handled elsewhere. Changes to descriptor sizes must be mirrored in queue initialization and skb descriptor accounting.

## Test Signals
Compile coverage for PCI and SoC builds, TX/RX descriptor dumps through debugfs, DMA API debugging, RX cipher/CRC flag tests, ring wraparound, and hardware queue register inspection after `rt2800mmio_init_queues()`.
