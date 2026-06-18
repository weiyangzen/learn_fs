<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.h

Purpose: Defines the ath9k MAC descriptor/status ABI, TX/RX bitfields, queue/filter/key enums, 802.11n rate-series helper macros, and prototypes for MAC helper functions. It is the shared contract between descriptor construction/parsing code, TX/RX paths, and hardware-specific MAC implementations.

Important APIs and types: Major types are `struct ath_tx_status`, `struct ath_rx_status`, `struct ath_htc_rx_status`, packed `struct ath_desc`, packed `struct ar5416_desc`, `enum ath9k_phyerr`, `enum ath9k_tx_queue`, `enum ath9k_tx_queue_flags`, `struct ath9k_tx_queue_info`, `enum ath9k_rx_filter`, `struct ath9k_11n_rate_series`, `enum aggr_type`, `enum ath9k_key_type`, and `struct ath_tx_info`. It declares all exported MAC helpers implemented in `mac.c` plus `ath9k_hw_setuprxdesc()` and `ar9002_hw_attach_mac_ops()`.

Control flow: The header has no runtime flow, but its macros drive how callers populate multi-rate TX descriptors (`set11nTries`, `set11nRate`, `set11nPktDurRTSCTS`, `set11nRateFlags`, `set11nChainSel`) and decode AR5416 descriptor status words. Queue flags and RX filter bits are consumed by queue setup, RX filter calculation, interrupt selection, and mac80211 callback handling.

State and persistence: Owns no state. Its packed descriptor layout and constants define hardware-visible DMA memory format and driver-visible status memory format. Any ABI drift affects descriptors already allocated and status parsing across the driver.

Dependencies and integration points: Includes cfg80211 rate/bandwidth definitions and depends on AR register bit macros from lower ath9k headers. It is included by MAC, TX, RX, hardware ops, and chipset attachment code. `ath_rx_status` maps directly into mac80211 `ieee80211_rx_status`; `ath_tx_info` maps software TX metadata into hardware descriptor programming.

Risks: Incorrect bit masks, shifts, packing, or alignment cause hardware DMA corruption or bad status interpretation. `ATH9K_TXQ_USEDEFAULT` as `(u32)-1` requires careful comparisons. Descriptor comments document interrupt moderation tradeoffs; over-deferred TX interrupts can stale rate control and backup senders. `struct_group(ba, ...)` exposes block-ack bitmap fields as a unit and must stay layout-compatible.

Test signals: Compile coverage across AR9002/AR9003, descriptor size/alignment assertions, TX descriptor setup/parse tests, RX status parse tests, queue flag programming, RX filter combinations, key type use with crypto setup, and sparse/endian checks for HTC big-endian RX status fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.h -->
