# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx_edma.h

## Purpose
This header defines enhanced DMA descriptor and status-ring formats, eDMA constants, status accessors, 64-bit DMA address helpers, and public eDMA TX/RX entry points for wil6210. It is the hardware ABI companion to `txrx_edma.c`.

## Important APIs, Types, and Functions
- Ring sizing and IDs: `WIL_SRING_SIZE_ORDER_*`, default RX/TX status-ring orders, default RX buffer ID count, `WIL_DEFAULT_RX_STATUS_RING_ID`, `WIL_RX_DESC_RING_ID`, and interrupt index constants.
- Descriptor types: `struct wil_ring_rx_enhanced_mac`, `struct wil_ring_rx_enhanced_dma`, `struct wil_rx_enhanced_desc`, `struct wil_ring_tx_enhanced_dma`, `struct wil_ring_tx_enhanced_mac`, and `struct wil_tx_enhanced_desc`.
- Status types: `struct wil_ring_tx_status`, `struct wil_rx_status_compressed`, `struct wil_rx_status_extension`, and `struct wil_rx_status_extended`.
- RX status accessors: helpers extract length, MCS, CB mode, flow ID, CID/TID, EOP, buffer ID, data offset, frame type, FC, sequence, MID, error bits, L2/L3/L4 status, checksum state, security, and key ID.
- TX status/address helpers: `wil_tx_status_get_mcs()`, `wil_desc_set_addr_edma()`, `wil_tx_desc_get_addr_edma()`, and `wil_rx_desc_get_addr_edma()`.
- Public prototypes: `wil_configure_interrupt_moderation_edma()`, `wil_tx_sring_handler()`, `wil_rx_handle_edma()`, and `wil_init_txrx_ops_edma()`.

## Control Flow
The header provides inline logic used while processing status messages. RX code first checks descriptor-ready polarity, then uses helpers to interpret compressed fields or extended fields depending on driver mode. CID/TID decoding handles DLPF lookup hit and miss layouts. Checksum helper maps hardware L3/L4 status into Linux `CHECKSUM_UNNECESSARY` or `CHECKSUM_NONE`. Address helpers split or reconstruct 64-bit DMA addresses across enhanced descriptor fields.

## State and Persistence Behavior
All structures represent transient coherent-memory records shared with hardware. The ready bit polarity and buffer ID fields are stateful protocol fields; `wil_rx_status_reset_buff_id()` writes back to the coherent status slot to clear a consumed ID. Packed structure layout and bit positions are persistent ABI contracts with firmware/hardware but not persisted to storage.

## Dependencies and Integration Points
The header includes `wil6210.h` for common state, bit extraction, statistics, and ring types. It integrates with `txrx.h` through the shared `union wil_tx_desc`/`union wil_rx_desc` model and with IRQ code through the exported status handlers. It depends on Linux SKB and checksum semantics indirectly via inline helpers.

## Risks
Bitfield extraction must match hardware status exactly. A wrong DLPF hit/miss interpretation can deliver traffic to the wrong station/TID. `wil_rx_status_get_retry()` returns a conservative constant because eDMA lacks a retry bit, which can affect reorder duplicate handling. Compressed status masks management/control frame details and is only safe with hardware reorder. `wil_rx_status_get_data_offset()` accepts only encoded offsets 0 and 3, treating other values as invalid. Address helpers must preserve bits 48-63 or high-memory DMA will fail.

## Test Signals
Build tests should catch packed layout size changes where users assert descriptor sizes. Runtime tests should verify status parsing for DLPF hit/miss, compressed versus extended status, checksum states, MID defaulting, buffer ID reset, 64-bit DMA addressing, TSO descriptor fields, and MCS/CB-mode accounting.
