## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_mon.c

Purpose: implements Wi-Fi 7 monitor-mode datapath parsing and delivery for RX/TX monitor rings, including HE/EHT radiotap metadata, PPDU/user statistics, and synthetic protection/ACK frames for TX monitor.

Important APIs/functions: public entry points are `ath12k_wifi7_dp_mon_process_ring()` and `ath12k_wifi7_dp_mon_tx_parse_mon_status()`. Major internal paths include RX TLV parsing (`ath12k_wifi7_dp_mon_rx_parse_status_tlv()`), destination TLV handling, monitor skb delivery (`ath12k_wifi7_dp_mon_rx_deliver()`), TX monitor TLV parsing, status-ring reaping, RXDMA1 destination processing, and legacy monitor destination processing.

Control flow: monitor status buffers are reaped from RXDMA monitor rings, DMA-synced/unmapped, parsed TLV by TLV, and either used to update PPDU metadata or to build MPDU lists. RX monitor delivery merges MSDUs, updates radiotap headers, sets monitor-only flags, and passes frames to mac80211. TX monitor parsing allocates per-PPDU tracking objects, interprets FES/setup/PHY/status TLVs, may synthesize RTS/CTS/QoS-null/ACK frames, and delivers accumulated MPDUs. The top-level path chooses RXDMA1 `ath12k_wifi7_dp_mon_srng_process()` when supported, otherwise the older status/destination process.

State and persistence: `struct ath12k_mon_data` holds in-progress PPDU info, MPDU lists, TX PPDU info, duplicate/stuck counters, last cookies/link descriptors, buffer state, and monitor locks. IDR maps in monitor rings track DMA buffers by buffer ID. All state is runtime-only and reset as PPDUs complete or monitor mode restarts.

Dependencies/integration: depends on HAL TLV structures for Wi-Fi 7 chips, common `dp_mon` helpers, RX descriptor helpers, peer lookup/stats updates, NAPI, DMA APIs, radiotap definitions, and mac80211 monitor delivery. It is invoked by `dp.c` based on monitor ring masks.

Risks: TLV parsing is complex and heavily offset-based; malformed lengths or unsupported tags can desynchronize parsing. EHT RU index handling appears to encode `rtap_ru_size` into the RU index field in one branch, which merits review. TX MPDU allocation code assigns a local `mon_mpdu` but does not store it back before later use, a likely null/use-after-uninitialized risk. Monitor destination stuck handling skips progress after 16 status PPDUs and must be validated under high traffic. DMA buffer IDR and duplicate-cookie logic are critical to avoiding leaks/double frees.

Test signals: monitor mode capture for legacy/HT/VHT/HE/EHT SU, MU-MIMO, OFDMA, 160/320 MHz RU allocations, RXDMA1 and non-RXDMA1 hardware, malformed/truncated status buffers, FCS/error reporting, TX monitor protection/ACK synthesis, buffer replenishment failures, duplicate cookie/link descriptor counters, and peer stats updates.
