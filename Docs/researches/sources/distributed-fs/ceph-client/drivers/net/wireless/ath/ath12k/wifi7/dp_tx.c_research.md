## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_tx.c

Purpose: implements Wi-Fi 7 TX datapath enqueue, descriptor construction, DMA mapping, completion handling, rate/status reporting, and vdev bank configuration.

Important APIs/functions: `ath12k_wifi7_dp_tx()` enqueues an skb to TCL; `ath12k_wifi7_dp_tx_completion_handler()` drains WBM/TCL completion status; `ath12k_wifi7_dp_tx_get_vdev_bank_config()` builds vdev bank config. Helpers prepare MSDU extension descriptors and HTT metadata, parse TX status, handle HTT/FW completions, update per-peer rates, and report completion to mac80211.

Control flow: TX rejects crash-flush and unsupported non-data frames, selects a TCL ring, assigns a TX descriptor, builds `hal_tx_info` from vif/link metadata, handles raw/native/ethernet encap, aligns payloads for IOVA constraints, DMA maps skb and optional extension descriptor, writes a TCL descriptor under ring lock, updates stats, and increments pending TX. Completion handling first copies hardware status descriptors into a software FIFO, resolves descriptors by hardware cookie conversion or software cookie, releases the TX buffer early, accounts release/status reasons, unmaps DMA, frees extension descriptors, updates pending counters, and either frees failed skbs or calls `ieee80211_tx_status_ext()`.

State and persistence: runtime state includes TX descriptor pools, TCL/WBM ring head/tail indices, per-pdev pending counts and wait queues, skb control-block DMA addresses, link/vif stats, device stats, and peer `txrate`/`last_txrate`. There is no persistent storage.

Dependencies/integration: depends on HAL TX descriptor layout, common DP TX helpers, peer lookup, mac80211 TX status APIs, DMA APIs, WMI service flags for RSSI conversion, and `dp.c` SRNG service dispatch.

Risks: descriptor and DMA cleanup paths are complex, especially when TCL ring retry happens after extension descriptor mapping. `ts` is declared once in the completion handler and should be fully overwritten per descriptor; stale fields after FW completions should be considered. TX MPDU status with missing peer frees skb without status. All-ring-full currently drops without throttling, noted by TODO. MLO multicast GSN rewrites vdev IDs and metadata, so off-by-base errors would be hard to diagnose.

Test signals: TX under crash flush, raw/native/ethernet encap, SW and HW crypto, EAPOL/null frames with metadata, IOVA alignment path, TCL ring full retry, DMA mapping failure, FW and TQM completion reasons, ACK/no-ACK reporting, peer missing during completion, EHT/HE/VHT/HT/legacy rate parsing, and bank config for STA/mesh/non-STA vdevs.
