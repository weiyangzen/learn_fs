# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp_rx.h

## Purpose

`dp_rx.h` is the public header for ath11k receive datapath services. It exposes RX decapsulation constants, RX MPDU error bits, small wire-format helper structs, and the RX/REO/HTT/monitor function prototypes used by core datapath, MAC, peer, and interrupt code.

## Important APIs, Types, and Functions

- `DP_MAX_NWIFI_HDR_LEN` bounds the temporary native-wifi header buffer used while rebuilding 802.11 headers.
- `DP_RX_MPDU_ERR_*` bits define the internal normalized MPDU error map for FCS, decrypt, TKIP MIC, A-MSDU, overflow, MSDU length, MPDU length, and unencrypted-frame problems.
- `enum dp_rx_decap_type` mirrors hardware decapsulation modes: raw, native wifi, Ethernet II/DIX, and 802.3.
- `struct ath11k_dp_amsdu_subframe_hdr` and `struct ath11k_dp_rfc1042_hdr` describe packed on-wire headers used by undecapsulation logic in `dp_rx.c`.
- AMPDU/reorder APIs: `ath11k_dp_rx_ampdu_start()`, `ath11k_dp_rx_ampdu_stop()`, `ath11k_peer_rx_tid_setup()`, `ath11k_peer_rx_tid_delete()`, `ath11k_peer_rx_tid_cleanup()`, and `ath11k_peer_frags_flush()`.
- Key/security API: `ath11k_dp_peer_rx_pn_replay_config()` updates REO PN replay behavior for pairwise keys.
- HTT and REO APIs: `ath11k_dp_htt_htc_t2h_msg_handler()`, `ath11k_dp_htt_tlv_iter()`, `ath11k_dp_pdev_reo_setup()`, `ath11k_dp_pdev_reo_cleanup()`, `ath11k_dp_reo_cmd_list_cleanup()`, and `ath11k_dp_process_reo_status()`.
- Ring processing APIs: normal RX, REO error, WBM error, RXDMA error, monitor status, and monitor rings are exported for NAPI/IRQ handlers.
- Allocation/lifecycle APIs: `ath11k_dp_rx_pdev_alloc()`, `ath11k_dp_rx_pdev_free()`, monitor attach/detach, pktlog start/stop, and buffer replenish helpers.

## Control Flow

This header does not implement control flow, but it defines the receive datapath surface used by the rest of the driver. Setup code calls pdev REO/RX allocation and monitor attach functions. Runtime NAPI code calls the process functions for normal REO destination rings, REO exceptions, WBM release errors, RXDMA errors, and monitor rings. MAC/peer code calls AMPDU, PN replay, and fragment setup/cleanup functions as stations and keys change. Firmware HTT messages enter through `ath11k_dp_htt_htc_t2h_msg_handler()`.

## State and Persistence Behavior

No state is stored in the header. The prototypes operate on runtime objects such as `ath11k_base`, `ath11k`, `ath11k_vif`, `ath11k_peer`, `dp_rxdma_ring`, `dp_rx_tid`, `sk_buff`, and `napi_struct`. All state is volatile driver memory maintained by implementation files.

## Dependencies and Integration Points

The header includes `core.h`, `rx_desc.h`, and `debug.h`, so users see core ath11k object definitions, RX descriptor definitions, and debug helpers. It depends on mac80211 types for AMPDU/key arguments and Linux networking types for skbs/NAPI through included headers. Its prototypes are consumed by datapath initialization, MAC callbacks, peer lifecycle code, interrupt/NAPI polling, HTT receive dispatch, and monitor/pktlog control paths.

## Risks and Edge Cases

- The decap enum and MPDU error bit definitions must stay aligned with `dp_rx.c` and hardware/HAL interpretation; mismatches would corrupt header reconstruction or error reporting.
- Exported buffer-replenish/process APIs assume callers pass the correct ring and mac id. Mixing pdev ids, LMAC ids, or ring types can break DMA ownership.
- The header exposes broad cross-module coupling between RX and TX because REO commands are submitted through TX code while RX owns reorder state.

## Test Signals

Compile coverage is the primary signal for this header. Runtime validation should exercise all declared entry points through RX pdev setup/free, AMPDU start/stop, key install/remove PN replay updates, normal/error RX NAPI polling, monitor start/stop, and pktlog start/stop.
