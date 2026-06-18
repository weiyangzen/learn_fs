# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_rx.h

## Purpose

`hal_rx.h` is the Wi-Fi 7 receive-side HAL interface header. It defines RX monitor TLV structures, PPDU/user statistics layouts, PHY signal bitfields for HT/VHT/HE/EHT/USIG parsing, REO status APIs, RX buffer address helpers, and queue-descriptor setup entry points used by the Wi-Fi 7 DP RX path. The file is mostly hardware ABI: packed structures and bit masks must match firmware and descriptor ring formats.

## Important APIs, Types, And Constants

Key exported types include `struct hal_rx_wbm_rel_info`, monitor TLV status headers, `struct hal_rx_ppdu_start`, `struct hal_rx_ppdu_end_user_stats`, HE/EHT/USIG signal structures, `struct hal_receive_user_info`, and `struct hal_rx_msdu_list`. The REO/RX helper prototypes include `ath12k_wifi7_hal_reo_status_queue_stats`, `ath12k_wifi7_hal_reo_flush_queue_status`, `ath12k_wifi7_hal_reo_flush_cache_status`, `ath12k_wifi7_hal_reo_unblk_cache_status`, `ath12k_wifi7_hal_reo_update_rx_reo_queue_status`, `ath12k_wifi7_hal_rx_msdu_link_info_get`, `ath12k_wifi7_hal_wbm_desc_parse_err`, `ath12k_wifi7_hal_desc_reo_parse_err`, `ath12k_wifi7_hal_rx_msdu_list_get`, `ath12k_wifi7_hal_reo_hw_setup`, and `ath12k_wifi7_hal_reo_qdesc_setup`.

The header also defines radiotap-related HE fields, RX MPDU error bits, EHT RU encodings, MRU composition macros for 80/160/320 MHz layouts, and status values such as `HAL_TLV_STATUS_PPDU_DONE` and `HAL_RX_MON_STATUS_*`.

## Control Flow And Integration

This header does not implement control flow directly, but it describes the contracts consumed by `wifi7/hal_rx.c`, `wifi7/dp_rx.c`, and `wifi7/dp_mon.c`. Monitor parsing code reads the PPDU, HE, EHT, USIG, and per-user structures to populate radiotap and RX status. DP RX uses the WBM/REO helper prototypes to recover buffer addresses, parse error release descriptors, return link descriptors, and build REO queue descriptors for per-peer/TID reorder state. HAL ops in chip files, such as WCN7850, point back to functions declared here.

## State And Persistence Behavior

The file defines transient on-ring and on-buffer state rather than persistent software state. REO queue descriptors and RX link descriptors represent durable hardware-owned DMA state while packets are in flight; fields such as PN, peer metadata, TID, PPDU ID, RSSI, RU allocation, and descriptor cookies are carried across ring transitions. Software persistence is indirect: queue descriptor setup and REO status parsing update DP peer/TID state elsewhere.

## Dependencies

It includes `hal_desc.h` and depends on common ath12k HAL types such as `struct ath12k_base`, `struct ath12k_dp`, `struct ath12k`, `struct hal_srng`, `struct hal_reo_status`, `struct hal_wbm_release_ring`, `struct ath12k_buffer_addr`, `enum hal_reo_cmd_type`, and Linux bitfield helpers (`GENMASK`, `BIT`, `le32_get_bits`). It is tightly coupled to `hal_rx_desc.h` for descriptor field masks and to monitor parsing in `dp_mon.c`.

## Risks And Edge Cases

Descriptor ABI drift is the primary risk: any field mask, packing, or TLV length mismatch can corrupt RX parsing, buffer recycling, monitor status, or REO commands. EHT and 320 MHz RU macros are dense and easy to mis-index. One visible risk is `HAL_RX_EHT_SIG_OFDMA_EB2_MCS` using `GNEMASK_ULL` instead of `GENMASK_ULL`, which would break compilation if that macro is compiled or referenced. Another risk is duplicate naming (`HE_TXBF_SHIFT`) in separate radiotap contexts; consumers must use the intended field context.

## Test Signals

Build coverage should compile all monitor and DP RX users with `W=1` to catch bad masks and missing symbols. Runtime signals include successful RX data traffic, monitor-mode radiotap correctness for HE/EHT frames, REO status processing under BA session setup/teardown, RX error path handling for FCS/decrypt/TKIP/fragment errors, and no DMA leak warnings when WBM/REO descriptors are recycled.
