# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/rx.h

## Purpose
Defines Intel iwlwifi firmware receive-side ABI structures and bit fields. It covers legacy pre-9000 RX PHY notifications, 9000+ MPDU descriptors, checksum/security status, reorder metadata, no-data RX reports, RSS/RFH queue configuration, station power-save and BA-window notifications, beacon-filter notifications, and air-sniffer PHY vector reports through HE, EHT, and UHR formats.

## Important APIs, Types, And Functions
Key ABI records include `iwl_rx_phy_info`, `iwl_rx_mpdu_res_start`, `iwl_rx_mpdu_desc`, `iwl_rx_no_data`, `iwl_rx_no_data_ver_3`, `iwl_rss_config_cmd`, `iwl_rxq_sync_cmd`, `iwl_rfh_queue_config`, `iwl_ba_window_status_notif`, and `iwl_rx_phy_air_sniffer_ntfy`. Important enums define RX PHY flags, checksum assist, MPDU status/security bits, reorder fields, HE/EHT/UHR PHY metadata masks, no-data error types, RSS hash functions, PM events, and sniffer status/flags.

## Control Flow
This header has no executable flow; it defines packets exchanged in firmware notifications and host commands. Runtime RX handling first interprets PHY/no-data/sniffer notifications, then parses MPDU descriptor fields for length, MAC header flags, checksum offload, decryption status, station ID, reorder BAID/SN/NSSN, rate, channel, RSSI, GP2, TSF, and optional PHY metadata. Setup flows use RFH and RSS commands before RX queues are active, and multi-queue sync commands can inject notifications into selected RX queues.

## State And Persistence
The file stores no driver state, but its packed little-endian records describe persistent firmware-visible state snapshots: RX queue DMA addresses, RSS key and indirection table, BA-window bitmaps, beacon-filter average energy, and per-frame descriptor metadata. Flexible-array payloads in RXQ sync commands and variable descriptor versions require command-size discipline at call sites.

## Dependencies And Integration Points
Depends on Linux integer/endian annotations, bit helpers, and iwlwifi shared rate/MAC constants from surrounding headers. It integrates with the MVM RX path, reorder buffer management, checksum offload, mac80211 RX status construction, monitor/sniffer paths, queue allocation, beacon filtering, and power-save station handling.

## Risks
This is a binary firmware contract: packed layout, endian conversion, descriptor version selection, and union interpretation must match the loaded firmware. Several fields are overloaded depending on API version, RPA enablement, TSF-overload flags, and PHY info type. Incorrect length or status parsing can corrupt skb boundaries, misreport crypto/checksum validity, break BA reordering, or expose invalid PHY metadata to mac80211.

## Test Signals
Useful signals include successful association traffic across legacy/HT/VHT/HE/EHT rates, checksum-offload correctness, encrypted RX with replay/MIC/ICV failures, A-MPDU reordering and BAR release behavior, RSS multi-queue distribution, monitor-mode PHY reporting, no-data notifications on malformed frames, and beacon-filter notifications during powersave. KASAN, sparse endian checks, and firmware API-version matrix boot tests are especially relevant.
