# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_mon.h

## Purpose

`dp_mon.h` declares ath12k monitor datapath interfaces and compact monitor-only data structures. It is the contract between generic RX setup/processing code, monitor status parsing, monitor MPDU reconstruction, radiotap generation, and peer statistic updates.

## Important APIs, Types, and Functions

Key constants include `ATH12K_MON_RX_DOT11_OFFSET`, `ATH12K_MON_RX_PKT_OFFSET`, and the `ATH12K_LE32_DEC_ENC`/`ATH12K_LE64_DEC_ENC` field-copy helpers used by monitor TLV handling.

Monitor mode and TX monitor parsing enumerations include `dp_monitor_mode`, `dp_mon_tx_ppdu_info_type`, `dp_mon_tx_tlv_status`, and `dp_mon_tx_medium_protection_type`.

Monitor frame and packet structures include `dp_mon_qosframe_addr4`, `dp_mon_frame_min_one`, `dp_mon_packet_info`, and `dp_mon_tx_ppdu_info`. `dp_mon_packet_info` carries cookie, DMA length, continuation, and truncation state for monitor buffer parsing. `dp_mon_tx_ppdu_info` stores PPDU ID, user count, an embedded `hal_rx_mon_ppdu_info`, and TX monitor MPDU list state.

Declared functions cover buffer replenishment, monitor status buffer allocation/parsing, PPDU ID comparison across wrap, radiotap update, monitor MSDU delivery, MPDU merge, UL OFDMA post-processing, and SU/MU peer stat updates.

## Control Flow and Integration

RX setup code uses `ath12k_dp_mon_buf_replenish()` and `ath12k_dp_mon_status_bufs_replenish()` when creating monitor rings. Monitor destination/status processing calls `ath12k_dp_mon_parse_status_buf()` to convert ring cookies into skb chains, then merge/deliver helpers to construct packets for mac80211. Peer statistics code calls the SU/MU update helpers after HAL monitor TLVs have populated `hal_rx_mon_ppdu_info`.

The header includes `core.h`, so declarations have access to `ath12k_base`, `ath12k_pdev_dp`, `dp_rxdma_mon_ring`, `ath12k_mon_data`, and mac80211-visible types indirectly.

## State and Persistence Behavior

The header owns no storage, but the declared functions mutate monitor ring IDRs, skb DMA metadata, monitor MPDU lists, peer statistics, and mac80211 RX status blocks. Callers should treat the APIs as stateful datapath operations with DMA and peer lifetime implications.

## Dependencies and Integration Points

This header depends on HAL monitor PPDU structures and core datapath structures. It is consumed by `dp_mon.c`, `dp_rx.c`, and other datapath files that need monitor buffer lifecycle and monitor delivery helpers.

## Risks and Contract Notes

- The declarations expose raw pointers to monitor ring and skb state; callers must hold the appropriate SRNG/IDR/peer locks required by implementation paths.
- `ath12k_dp_pkt_set_pktlen()` can reallocate skb head storage under `GFP_ATOMIC`; callers must handle `-ENOMEM`.
- `ath12k_dp_mon_comp_ppduid()` maintains caller-provided PPDU state and encodes wraparound behavior; incorrect state sharing can reorder monitor processing.
- The header declares TX monitor enums and structures even though this source subset primarily implements RX monitor helpers, so future TX monitor users should verify all states are consumed.

## Test Signals

Header-level validation is compile coverage with monitor support enabled, prototype consistency with `dp_mon.c`, and integration tests that include both `rxdma1_enable` and non-`rxdma1_enable` hardware parameter paths.
