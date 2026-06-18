# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp.h

Purpose: Defines ath11k datapath state, ring sizing, HTT host/target message formats, PPDU stats formats, RX filter masks, peer map events, ext-stats messages, and public DP function prototypes.

Important APIs and types: Core state structs include `dp_rx_tid`, `dp_reo_cmd`, `dp_srng`, `dp_rxdma_ring`, `dp_tx_ring`, `ath11k_mon_data`, `ath11k_pdev_dp`, `ath11k_hp_update_timer`, and `ath11k_dp`. Constants define TX/RX/REO/RXDMA ring sizes, buffer sizes, descriptor-bank limits, cookie masks, TCL metadata fields, PPDU stats tags, monitor filter masks, and shadow timer intervals. Packed HTT layouts include version, SRING setup, PPDU stats config/indication, RX ring selection, full monitor config, peer map/unmap, packet log, ext-stats request/response, and PPDU user/rate/completion structs. `ath11k_dp_get_mac_addr()` handles endian-aware MAC extraction.

Control flow: The header encodes control messages consumed by `dp_tx.c` and response/event formats consumed by `dp_rx.c`. It also declares the lifecycle and service functions implemented in `dp.c`, allowing core probe, bus interrupt handlers, mac80211 vdev/peer setup, RX monitor code, and ring users to share DP primitives.

State and persistence: Defines in-memory runtime state for SOC-level DP and per-pdev DP. Lists track REO commands and full monitor MPDUs; IDRs map software buffer IDs to skbs; DMA ring descriptors expose host memory to firmware/hardware; timers defer shadow head/tail pointer updates. The state is rebuilt on probe/reset and is not persistent beyond device lifetime.

Dependencies and integration points: Includes `hal_rx.h` and references `ath11k_base`, `ath11k_peer`, `ath11k_vif`, `hal_srng`, `hal_tcl_status_ring`, `ath11k_ext_irq_grp`, `sk_buff`, `timer_list`, IDR, locks, and mac80211 constants. It is a high-fanout header for `dp.c`, `dp_tx.c`, `dp_rx.c`, `peer.c`, `mac.c`, bus interrupt code, copy engines, and debugfs HTT stats.

Risks: This file is firmware/hardware ABI dense: bit masks, packed layouts, enum numeric values, and ring sizes must match target firmware and HAL expectations. A duplicate `HTT_TX_WBM_COMP_INFO0_REINJECT_REASON` define and typo-like `FLASG` names are harmless only because users already match them. Changing ring sizes affects memory use, interrupt load, and firmware capacity. Flexible array and payload-size users must validate lengths before reading. Endian-sensitive MAC unpacking is isolated in `ath11k_dp_get_mac_addr()` and should be reused.

Test signals: Compile all users after HTT/HAL schema changes; run HTT version, SRING setup, PPDU stats, RX ring selection, full monitor, peer map/unmap, pktlog, and ext-stats flows; verify RX monitor filters produce expected TLVs; stress TX IDR and RX refill cookie bounds; validate ring sizes on each supported hardware family; run big-endian build or static checks for MAC extraction.
