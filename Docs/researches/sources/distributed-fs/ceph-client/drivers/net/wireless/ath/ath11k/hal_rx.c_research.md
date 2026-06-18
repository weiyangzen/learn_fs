# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_rx.c

## Purpose
`hal_rx.c` implements RX-side HAL helpers for REO command construction, REO status parsing, RX/WBM error descriptor parsing, RX buffer address extraction, REO queue descriptor setup, REO command ring initialization, and monitor-status TLV parsing into `hal_rx_mon_ppdu_info`.

## Important APIs, types, and functions
Important exported functions include `ath11k_hal_reo_cmd_send()`, buffer address set/get helpers, MSDU link extraction, REO/WBM error parsers, REO entrance address extractors, WBM release descriptor setup, REO status parsers, `ath11k_hal_reo_process_status()`, `ath11k_hal_reo_qdesc_size()`, `ath11k_hal_reo_qdesc_setup()`, `ath11k_hal_reo_init_cmd_ring()`, `ath11k_hal_rx_parse_mon_status()`, and monitor ring address extraction.

Internal builders create TLV entries for get queue stats, flush cache, and update RX REO queue commands. The monitor parser handles PPDU start/end, HT/VHT/HE SIG fields, RSSI, MPDU start peer id, RX duration/TSFT, dummy/status-done TLVs, and radiotap HE/HE-MU fields.

## Control flow
`ath11k_hal_reo_cmd_send()` locks the SRNG, begins access, obtains the next source entry, dispatches on command type, starts the DP REO command timer, ends access, and unlocks. Unsupported REO command sends return `-EOPNOTSUPP`; no ring space returns `-ENOBUFS`.

REO status parsing functions cast TLV payloads and populate `struct hal_reo_status`. Flush-cache and unblock-cache parsing update `ab->hal.avail_blk_resource`. Monitor parsing walks TLVs in an SKB until PPDU done, buffer done, or `DP_RX_BUFFER_SIZE` is reached, aligning each TLV to `HAL_TLV_ALIGN`.

## State and persistence behavior
State mutation includes REO cache blocking resource bookkeeping, SRNG head/tail movement through HAL access helpers, `ab->soc_stats.reo_error[]`, `invalid_rbm`, and caller-owned output structures. REO queue descriptors are initialized in DMA memory with owner/type/magic fields, BA window size, PN policy, AC, retry, SSN, and extension descriptors. No filesystem persistence exists.

## Dependencies and integration points
This file depends on `debug.h`, `hal.h`, `hal_tx.h`, `hal_rx.h`, `hal_desc.h`, `hif.h`, hardware ops, DP timers, Linux SKB/endian helpers, and mac80211 radiotap constants. DP RX consumes most helpers; DP TX uses the REO command send API.

## Risks
REO command send support is partial. The flush-cache blocking resource model uses a single `current_blk_index`, so callers must serialize blocked operations. Monitor parsing trusts firmware TLV lengths within buffer bounds. BA window coercion for QoS TIDs is subtle. Error parsers intentionally reject unexpected buffer types/RBMs, which protects recycling but can expose ABI drift as dropped descriptors.

## Test signals
Expected signals include successful REO command completions, RX reorder setup, stable RX traffic, sane monitor radiotap fields, valid peer ids, and no invalid RBM or unexpected REO push reason warnings. Hardware traffic tests are more meaningful than isolated unit tests.
