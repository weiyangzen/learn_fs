## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_rx.c

Purpose: implements Wi-Fi 7 RX datapath processing: REO queue programming, normal RX delivery, error-ring recovery, defragmentation/reinjection, WBM error handling, PN check setup, and chip-specific RXDMA filter configuration.

Important APIs/functions: exported architecture ops include `ath12k_wifi7_dp_rx_process()`, `ath12k_wifi7_dp_rx_process_err()`, `ath12k_wifi7_dp_rx_process_wbm_err()`, `ath12k_wifi7_dp_rx_process_reo_status()`, `ath12k_wifi7_dp_reo_cmd_send()`, `ath12k_wifi7_dp_rx_assign_reoq()`, `ath12k_wifi7_peer_rx_tid_reo_update()`, `ath12k_wifi7_dp_reo_cache_flush()`, `ath12k_wifi7_dp_setup_pn_check_reo_cmd()`, and RXDMA ring setup functions for QCN9274/WCN7850/QCC2072.

Control flow: normal RX drains a REO destination ring, resolves hardware link/device IDs, converts cookies or hardware VA back to RX descriptors, unmaps DMA, queues skb fragments, replenishes buffers per device, extracts RX descriptor data, performs undecap/decryption flag handling, and delivers to mac80211. Error paths drain REO exception and WBM release rings, decide whether to drop, process fragments, report TKIP MIC/null queue descriptor cases, and replenish buffers. Fragment handling stores per-TID skb queues until all fragments arrive, validates incremental PN for CCMP/GCMP, defragments, and reinjects through the REO entrance ring.

State and persistence: runtime state includes REO queue buffers in `dp_peer->reoq_bufs`, REO queue LUT entries, `dp->reo_cmd_list`, RX descriptor free/used lists, per-TID fragment queues/timers/bitmaps, device stats, and DMA mappings. No durable persistence exists; state is rebuilt on peer/device setup.

Dependencies/integration: depends on common DP RX/TX helpers, peer tables, HAL RX descriptor parsers, chip-specific HAL offset providers, DMA APIs, NAPI, mac80211 RX status, HTT RX filter setup, and the `dp.c` ops table.

Risks: descriptor ownership is delicate: every path must clear `desc_info->skb`, unmap DMA once, add descriptors to used/free lists, and replenish the correct partner device. Fragment reinjection manually edits link descriptors and allocates RX descriptors under lock, making leak/error paths high risk. Multi-device MLO routing uses `hw_link_id` and partner DP lookup; invalid IDs can drop traffic. Some TODOs indicate incomplete handling for PN failures and other RXDMA/REO error codes.

Test signals: high-rate RX with A-MSDU/continuation buffers, invalid cookies, MLO partner-device routing, CAC drop path, descriptor exhaustion, REO command status callbacks, BA window updates, PN setup for supported ciphers, TKIP MIC failures, null queue descriptor handling, fragmented protected frames with timeout cleanup, and RXDMA filter setup on QCN9274/WCN7850/QCC2072.
