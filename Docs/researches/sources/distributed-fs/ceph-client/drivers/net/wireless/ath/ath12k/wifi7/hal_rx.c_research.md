# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx.c

## Purpose

`hal_rx.c` implements common Wi-Fi 7 RX and REO helper logic for ath12k. It encodes REO commands, decodes REO status descriptors, handles RX buffer/link descriptor address fields, parses REO/WBM error descriptors, sizes and initializes REO queue descriptors, initializes REO command rings, and programs basic REO hardware behavior.

## Important APIs and Functions

- REO command encoding: `ath12k_wifi7_hal_reo_cmd_send()`, `ath12k_wifi7_hal_reo_cmd_queue_stats()`, `ath12k_wifi7_hal_reo_cmd_flush_cache()`, and `ath12k_wifi7_hal_reo_cmd_update_rx_queue()`.
- Descriptor address helpers: `ath12k_wifi7_hal_rx_buf_addr_info_set()`, `ath12k_wifi7_hal_rx_buf_addr_info_get()`, `ath12k_wifi7_hal_rx_reo_ent_paddr_get()`, and `ath12k_wifi7_hal_rx_reo_ent_buf_paddr_get()`.
- RX list/link helpers: `ath12k_wifi7_hal_rx_msdu_link_info_get()`, `ath12k_wifi7_hal_rx_msdu_list_get()`, and `ath12k_wifi7_hal_rx_msdu_link_desc_set()`.
- Error parsing: `ath12k_wifi7_hal_desc_reo_parse_err()` and `ath12k_wifi7_hal_wbm_desc_parse_err()`.
- REO status decoding: queue stats, flush queue, flush cache, unblock cache, flush timeout list, descriptor threshold reached, and update RX queue status functions.
- REO queue setup: `ath12k_wifi7_hal_reo_qdesc_size()` and `ath12k_wifi7_hal_reo_qdesc_setup()`.
- Command ring initialization: `ath12k_wifi7_hal_reo_init_cmd_ring_tlv64()` and `ath12k_wifi7_hal_reo_init_cmd_ring_tlv32()`.
- Hardware setup: `ath12k_wifi7_hal_reo_hw_setup()` and `ath12k_wifi7_hal_reo_shared_qaddr_cache_clear()`.

## Control Flow

REO command submission locks the source ring, begins SRNG access, obtains the next entry, encodes the selected command, ends access, and unlocks. Queue stats encode queue address and optional clear/status flags. Flush cache optionally reserves a blocking resource using `ffz(hal->avail_blk_resource)` and `hal->current_blk_index`, then encodes cache address, forward/flush/block flags, and 1K descriptor handling. Update RX queue encodes a large set of update-enable bits and new values, normalizes PN size values of 24/48/128 into hardware enums, and clamps BA window size to hardware expectations.

RX descriptor parsing flows decode DMA addresses and software cookies from `ath12k_buffer_addr`. REO error parsing validates push reason, updates `dp->device_stats.reo_error[err_code]`, extracts the link descriptor bank from the cookie, and returns the physical address. WBM error parsing distinguishes normal and hardware-cookie-converted release formats, verifies descriptor type and return buffer manager, fills `hal_rx_wbm_rel_info`, and captures source-specific push reason/error code.

REO status handlers decode uniform command number/status first and then populate the matching `struct hal_reo_status` union payload. Flush/unblock cache status also updates `hal->avail_blk_resource` based on the current blocking resource index.

REO queue descriptor setup writes a REO-owned descriptor header, queue number, valid/link counter/access category, BA window size, PN policy, ignore-AMPDU flag, optional SSN, and extension descriptor headers for QoS TIDs. Command ring initialization pre-fills each entry's command number for TLV64 or TLV32 layouts.

`ath12k_wifi7_hal_reo_hw_setup()` enables REO aging/flush, routes fragment and BAR frames to REO2SW0, programs aging thresholds, and writes destination ring hash maps. `ath12k_wifi7_hal_reo_shared_qaddr_cache_clear()` toggles the clear bit in the queue descriptor address register under `dp->dp_lock`.

## State and Persistence

The file mutates `hal->avail_blk_resource`, `hal->current_blk_index`, REO command ring entries, REO queue descriptors, RX/WBM release info, DP error counters, SRNG producer/consumer state, and REO hardware registers. It reads/writes DMA-visible descriptor memory in little-endian form and uses spinlocks around command-ring access. Persistent hardware state includes REO aging enablement, destination ring routing, aging thresholds, hash maps, and queue descriptor cache clear toggling.

## Dependencies and Integration Points

It depends on common ath12k debug/HAL/HIF headers, Wi-Fi 7 `hal_tx.h`, `hal_rx.h`, `hal_desc.h`, and `hal.h`. It integrates with chip-specific `hal->ops->reo_cmd_enc_tlv_hdr()` implementations, SRNG access helpers, DP lock/state, device stats, and upper RX/TID management that allocates and updates REO queue descriptors.

## Risks

- Unsupported REO commands (`FLUSH_QUEUE`, `UNBLOCK_CACHE`, `FLUSH_TIMEOUT_LIST`) return `-EOPNOTSUPP` from the send path even though status decoders exist; callers must not assume full command support.
- Blocking resource accounting uses a single `current_blk_index`; overlapping flush/unblock operations may be fragile if multiple commands are outstanding.
- `ath12k_wifi7_hal_reo_flush_timeout_list_status()` reads `FWD_BUF_COUNT` from `desc->info0` while the mask is named for `INFO1`, suggesting a possible decode bug.
- `ath12k_wifi7_hal_rx_msdu_list_get()` modifies `rx_msdu_info.info0` in the link descriptor to force first/last flags while building software lists.
- WBM error parsing expects `HAL_RX_BUF_RBM_SW3_BM`; chips with different RX buffer RBM policy must ensure `hal_params` and hardware release descriptors agree.
- Queue descriptor setup always initializes three extension descriptors for QoS TIDs despite size calculation supporting more cases; allocation and initialization policy must remain consistent with callers.

## Test Signals

Key tests include REO command-ring exhaustion (`-ENOBUFS`), queue stats/flush cache/update queue command encoding, blocking resource exhaustion (`-ENOSPC`), REO/WBM error descriptor parsing with valid and invalid RBMs, RX MSDU list extraction for empty, single, multi-MSDU, and continuation cases, REO queue descriptor setup across BA window sizes and TIDs, TLV32/TLV64 command ring initialization, and REO hardware setup register readback. Lockdep should cover `ath12k_wifi7_hal_reo_shared_qaddr_cache_clear()` under `dp_lock`.
