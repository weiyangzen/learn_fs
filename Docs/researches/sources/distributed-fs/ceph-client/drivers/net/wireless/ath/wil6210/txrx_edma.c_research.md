# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx_edma.c

## Purpose
This file implements the enhanced DMA data path for wil6210. Compared with legacy vrings, eDMA uses separate TX/RX descriptor rings and TX/RX status rings, buffer IDs for RX, optional compressed RX status, optional hardware RX reordering, and enhanced descriptors with 64-bit DMA address support. It supplies the eDMA implementation of `wil->txrx_ops` while reusing common netdev TX/RX delivery logic from `txrx.c`.

## Important APIs, Types, and Functions
- Status ring lifecycle: `wil_find_free_sring()`, `wil_sring_alloc()`, `wil_sring_free()`, `wil_tx_init_edma()`, and `wil_tx_fini_edma()` allocate coherent completion queues and configure them through WMI.
- Descriptor ring lifecycle: `wil_ring_alloc_desc_ring()`, `wil_ring_free_edma()`, `wil_init_rx_desc_ring()`, `wil_ring_init_tx_edma()`, `wil_ring_init_bcast_edma()`, and `wil_tx_ring_modify_edma()`.
- RX buffer ID management: `wil_init_rx_buff_arr()`, `wil_free_rx_buff_arr()`, `wil_move_all_rx_buff_to_free_list()`, `wil_ring_alloc_skb_edma()`, and `wil_rx_refill_edma()` move buffers between free and active lists and post descriptors.
- RX status processing: `wil_get_next_rx_status_msg()`, `wil_sring_advance_swhead()`, `wil_sring_reap_rx_edma()`, `wil_rx_handle_edma()`, `wil_check_bar()`, `wil_rx_error_check_edma()`, and `wil_rx_crypto_check_edma()`.
- TX status processing: `wil_get_next_tx_status_msg()` and `wil_tx_sring_handler()` reap status messages, unmap completed descriptors, account SKBs, and update queue state.
- eDMA TX descriptor programming: `wil_tx_desc_map_edma()`, `wil_tx_desc_unmap_edma()`, `wil_tx_desc_offload_setup_tso_edma()`, `wil_tx_tso_gen_desc()`, and `__wil_tx_ring_tso_edma()`.
- Dispatch registration: `wil_init_txrx_ops_edma()` installs eDMA callbacks in the common operation table.

## Control Flow
TX initialization allocates a TX status ring, sends `wil_wmi_tx_sring_cfg()`, sets descriptor-ready polarity, and records `tx_sring_idx`. TX descriptor rings are created on connect/broadcast setup with WMI add commands. Common `wil_start_xmit()` eventually calls common non-GSO TX or eDMA TSO through `txrx_ops`. TX completions arrive as status messages: `wil_tx_sring_handler()` reads messages while the descriptor-ready bit matches expected polarity, validates ring IDs and descriptor counts, walks the corresponding descriptor ring from `swtail`, unmaps each DMA segment, consumes the SKB on the context carrying it, advances tails, periodically updates hardware status-ring tail, and wakes queues.

RX initialization validates status compression versus software reorder, sizes the status ring larger than the descriptor ring, configures default RX offload, allocates one or more RX status rings, allocates the RX descriptor ring and a coherent SW-tail pointer, builds a buffer-ID array, and posts initial RX buffers. `wil_rx_handle_edma()` scans all RX status rings under NAPI quota. `wil_sring_reap_rx_edma()` reads a status message, validates/retries buffer ID visibility, extracts and unmaps the active SKB, returns the buffer ID to the free list, validates length/CID, coalesces chained buffers until EOP, handles BAR frames for software reorder, applies data offset compensation, stores status in `skb->cb`, and returns a full packet. Packets go straight to `wil_netif_rx_any()` when hardware reorder is used or to `wil_rx_reorder()` otherwise.

## State and Persistence Behavior
The file maintains only volatile driver/device state: `wil->srings[]`, `wil->ring_rx`, `wil->ring_tx[]`, `wil->rx_buff_mgmt`, status-ring ready polarity, RX chaining state in `sring->rx_data`, invalid-buffer counters, per-descriptor DMA mapping context, and TX/RX statistics. The buffer array uses ID 0 as invalid, so valid IDs run from 1 through configured count. DMA physical addresses for RX buffers are temporarily stored in `skb->cb` until completion, then `skb->cb` is reused for the RX status message.

## Dependencies and Integration Points
This file depends on enhanced descriptor/status definitions from `txrx_edma.h`, common ring/netdev helpers from `txrx.h`, WMI eDMA commands declared in `wil6210.h`, Linux DMA/SKB/list APIs, NAPI, and tracepoints. It integrates with firmware capability/configuration paths through `use_compressed_rx_status`, `use_rx_hw_reordering`, `num_rx_status_rings`, `rx_status_ring_order`, `tx_status_ring_order`, `rx_buff_id_count`, and aggregation settings.

## Risks
RX buffer-ID handling is delicate: missing IDs, stale IDs, or invalid IDs can leak buffers or drop frames, so the reset and free-list paths are important. `skb->cb` reuse across DMA address storage and status storage makes ordering constraints strict. Compressed RX status cannot support software reorder, and the code rejects that combination. Status-ring ready polarity must flip exactly on wraparound. TX completion trusts firmware-provided `num_descriptors`; invalid values can desynchronize descriptor tails. eDMA ring modify is unsupported, so roaming or peer retargeting must use a different lifecycle than legacy.

## Test Signals
Validate eDMA with station/AP/broadcast traffic, multiple RX status rings, hardware and software RX reordering, compressed and extended status modes, chained RX packets, invalid/corrupt buffer ID injection, checksum offload status, L2 MIC/KEY/REPLAY/A-MSDU errors, TSO over IPv4 and IPv6, TX status ring wrap and polarity flip, ring-full behavior, and cleanup under disconnect/reset. Counters to watch include `invalid_buff_id_cnt`, `free_list_empty_cnt`, per-station RX/TX/error stats, tracepoints, and status-ring hardware tail updates.
