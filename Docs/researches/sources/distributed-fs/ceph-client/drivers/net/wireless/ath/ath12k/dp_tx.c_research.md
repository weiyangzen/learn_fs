# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_tx.c

## Purpose

`dp_tx.c` provides shared ath12k TX datapath helpers for encapsulation selection, native Wi-Fi header adjustment, TID selection, encryption type mapping, TX descriptor allocation/release, metadata tail allocation, payload alignment, and TX skb cleanup after failed or completed descriptor ownership.

## Important APIs, Types, and Functions

`ath12k_dp_tx_get_encap_type()` maps device raw mode and mac80211 `IEEE80211_TX_CTL_HW_80211_ENCAP` into HAL TCL encapsulation types.

`ath12k_dp_tx_encap_nwifi()` strips QoS control from QoS data frames when converting to native Wi-Fi encapsulation and clears the QoS subtype bit.

`ath12k_dp_tx_get_tid()` derives the TCL/REO TID from skb priority, returning `HAL_DESC_REO_NON_QOS_TID` for non-QoS 802.11 frames.

`ath12k_dp_tx_get_encrypt_type()` maps Linux cipher suite constants to HAL encryption types.

`ath12k_dp_tx_assign_buffer()` and `ath12k_dp_tx_release_txbuf()` move `ath12k_tx_desc_info` objects between per-pool free and used lists under `tx_desc_lock`.

`ath12k_dp_metadata_align_skb()` makes skb data writable and appends zeroed metadata at the tail. `ath12k_dp_tx_align_payload()` shifts or reallocates skb payload so the data pointer satisfies `dp->hw_params->iova_mask`.

`ath12k_dp_tx_free_txbuf()` unmaps TX DMA, frees optional extension descriptors, frees the mac80211 TX skb, decrements `num_tx_pending`, and wakes `tx_empty_waitq` when the pdev drains.

## Control Flow

TX submission code calls the small helpers while constructing TCL descriptors: choose encap, possibly rewrite native Wi-Fi header, choose TID, allocate a descriptor, align payload or append metadata if hardware requires it, and map/send elsewhere. On rollback or completion, `ath12k_dp_tx_free_txbuf()` reverses DMA ownership and skb ownership and descriptor release is handled separately by `ath12k_dp_tx_release_txbuf()`.

## State and Persistence Behavior

Persistent state touched here includes per-pool TX descriptor free/used lists, `tx_desc->skb_ext_desc`, skb DMA addresses in `ATH12K_SKB_CB`, optional extension descriptor DMA addresses, and `dp_pdev->num_tx_pending`. The list operations are protected by per-pool spinlocks; TX skb free uses RCU to map MAC ID to pdev datapath.

## Dependencies and Integration Points

The file depends on mac80211 TX metadata, skb helpers, HAL TCL and encryption enums, ath12k hardware params, peer/mac headers for shared datapath context, and `ieee80211_free_txskb()` for final skb release. Other TX implementation files are expected to use these helpers while programming TCL rings.

## Risks and Edge Cases

- `ath12k_dp_tx_align_payload()` may replace `*pskb` with a reallocated skb and free the original. Callers must use the updated pointer after success.
- Payload movement uses memmove with skb push/pull/trim; off-by-one errors would corrupt TX frames, so hardware IOVA alignment changes need direct packet tests.
- Descriptor allocation warns and returns `NULL` on exhaustion; callers need backpressure/drop handling.
- `ath12k_dp_tx_free_txbuf()` assumes `desc_params->skb_ext_desc` is valid when `paddr_ext_desc` is set.
- Encryption mapping defaults unknown ciphers to open, which is safe only if unsupported ciphers are filtered earlier.

## Test Signals

Useful tests include raw/native/Ethernet encapsulation selection, QoS/non-QoS TID mapping, cipher mapping coverage, TX descriptor exhaustion, IOVA alignment with tight headroom/tailroom and realloc paths, DMA mapping fault cleanup, and TX drain waitqueue behavior.
