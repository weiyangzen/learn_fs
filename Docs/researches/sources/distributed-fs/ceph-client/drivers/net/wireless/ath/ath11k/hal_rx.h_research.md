# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_rx.h

## Purpose
`hal_rx.h` is the public RX HAL interface and monitor-status data contract for ath11k. It declares RX error/release info, monitor PPDU status structures, PHY SIG TLV layouts, RX MPDU layout variants, helper prototypes implemented in `hal_rx.c`, and magic patterns for REO queue descriptors.

## Important APIs, types, and data
`struct hal_rx_wbm_rel_info` carries parsed WBM error-release details. `enum hal_rx_mon_status` describes monitor parse progress. `struct hal_rx_user_status`, `struct hal_sw_mon_ring_entries`, and `struct hal_rx_mon_ppdu_info` are the main outputs used by monitor receive code to build rate/RSSI/radiotap information.

The header defines packed TLV payload structures for PPDU start, PPDU end user stats, HT SIG, L-SIG A/B, VHT SIG A, HE SIG A SU/MU, HE SIG B MU/OFDMA, legacy RSSI, per-chip RX MPDU info layouts, PPDU duration, and RXPCU classification overview. It declares REO status parsers, buffer-address helpers, REO entrance/monitor ring address extractors, and monitor parsing.

## Control flow
Control flow lives in `hal_rx.c`. This header defines the data shape for callers in `dp_rx.c`, `dbring.c`, and monitor-mode code.

## State and persistence behavior
The header owns no state. Its structures are transient per-packet/per-PPDU outputs or views over DMA descriptor data. Persistent effects happen in caller-owned objects, RX ring descriptors, DP RX peer/TID state, and REO queue DMA memory initialized through declared APIs.

## Dependencies and integration points
It depends on `hal.h`/`hal_desc.h`, Linux endian types, mac80211 radiotap constants used by implementation, and chip-specific hardware ops that choose the right MPDU info variant. DP RX and monitor code are the direct integration points.

## Risks
The biggest risk is mismatched TLV layout across chips or firmware revisions. Consumers must check validity flags in `hal_rx_mon_ppdu_info`. The duplicate prototype for `ath11k_hal_reo_flush_cache_status()` is harmless but indicates header drift. HE/OFDMA/radiotap bit definitions need validation against firmware output.

## Test signals
Monitor captures should show accurate PPDU ids, rates, MCS/NSS, HE flags, RSSI, TSFT, duration, RU allocation, and FCS counters. RX stress should show correct buffer cookie/RBM extraction and no invalid descriptor warnings. Compile tests catch signature drift.
