# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_tx.h

## Purpose

`dp_tx.h` declares shared ath12k TX datapath helper APIs and a compact HTT WBM TX status structure. It is the interface used by TX descriptor-building code and cleanup code for encapsulation, TID selection, metadata alignment, descriptor pools, and TX buffer freeing.

## Important APIs, Types, and Functions

`struct ath12k_dp_htt_wbm_tx_status` carries completion acknowledgement state and ACK RSSI.

Declared APIs include `ath12k_dp_tx_put_bank_profile()`, `ath12k_dp_tx_get_encap_type()`, `ath12k_dp_tx_encap_nwifi()`, `ath12k_dp_tx_get_tid()`, `ath12k_dp_metadata_align_skb()`, `ath12k_dp_tx_align_payload()`, `ath12k_dp_tx_release_txbuf()`, `ath12k_dp_tx_assign_buffer()`, and `ath12k_dp_tx_free_txbuf()`.

## Control Flow and Integration

TX code uses these helpers around TCL descriptor construction: determine encapsulation, edit native Wi-Fi frames, select TID, allocate descriptor state, append metadata, align payload for device IOVA requirements, and free/unmap buffers on completion or failure.

## State and Persistence Behavior

The header has no storage, but its functions mutate skb contents/control blocks, TX descriptor lists, DMA mappings, and pdev pending counters.

## Dependencies and Integration Points

It includes `core.h` and depends on HAL TCL encap types, ath12k datapath rings, TX descriptor structures, and Linux skb/mac80211 APIs.

## Risks and Contract Notes

- Callers must treat `ath12k_dp_tx_align_payload()` as possibly replacing the skb pointer.
- Descriptor pool functions require a valid pool ID and initialized list/lock state.
- Header does not declare `ath12k_dp_tx_get_encrypt_type()` even though `dp_tx.c` exports it, so consumers may rely on another declaration; prototype drift should be checked.

## Test Signals

Compile checks for all TX users, symbol/prototype consistency, and TX-path tests covering encapsulation, descriptor exhaustion, and cleanup paths are useful.
