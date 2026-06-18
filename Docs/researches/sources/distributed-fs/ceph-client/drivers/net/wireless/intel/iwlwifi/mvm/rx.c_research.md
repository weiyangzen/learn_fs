# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rx.c

## Purpose
`rx.c` handles receive-side firmware notifications for the Intel MVM driver. It pairs PHY and MPDU notifications, builds mac80211 RX status and SKBs, updates RSSI/TCM/statistics state, translates firmware crypto and rate metadata, triggers debug collection, and reports BA-window filtering information.

## Important APIs, Types, and Functions
- `iwl_mvm_rx_rx_phy_cmd()` stores the latest PHY information in `mvm->last_phy_info`, increments `ampdu_ref`, and updates debug AMPDU counters.
- `iwl_mvm_rx_rx_mpdu()` is the main MPDU handler. It validates packet length, allocates an SKB, fills `ieee80211_rx_status`, resolves the station, handles decryption status, updates RSSI/TCM/checksum state, decodes rate flags, records debug frame stats, and passes the packet to mac80211.
- `iwl_mvm_pass_packet_to_mac80211()` constructs the SKB using head data plus an RX page fragment when the packet is larger than the small head allocation.
- `iwl_mvm_set_mac80211_rx_flag()` maps firmware security status to mac80211 `RX_FLAG_DECRYPTED` and crypto header lengths, or drops frames with failed MIC/ICV checks.
- `iwl_mvm_get_signal_strength()` decodes per-chain energy and updates `rx_status->signal`, `chains`, and `chain_signal`.
- `iwl_mvm_rx_handle_tcm()` updates traffic classification manager counters, RX airtime, and U-APSD non-aggregation detection.
- Statistics handlers include legacy `iwl_mvm_handle_rx_statistics()`, TLV versions 14/15, system operational notifications, part1 radio-time notifications, per-link MLO handling, per-phy channel load, per-station average energy, and firmware debug trigger checks.
- `iwl_mvm_window_status_notif()` forwards BA-window bitmaps to `ieee80211_mark_rx_ba_filtered_frames()`.

## Control Flow
For older RX API flows, firmware sends a PHY notification followed by one or more MPDU notifications. `iwl_mvm_rx_rx_phy_cmd()` snapshots the PHY metadata, and `iwl_mvm_rx_rx_mpdu()` uses that snapshot for timestamps, channel, RSSI, rate, AMPDU grouping, and frame time. The MPDU path validates lengths before accessing the header/status trailer, marks CRC/FIFO errors for monitor visibility, finds the station by firmware station ID or source address, rejects protected multicast before authorization, and asks `iwl_mvm_set_mac80211_rx_flag()` whether hardware decryption succeeded. Under RCU it updates station-local state, CSA unblock state, rate-scaling RSSI, low-RSSI debug triggers, TCM, and RX checksum offload.

After station handling, the MPDU path converts firmware rate bits into mac80211 RX encoding. HT, VHT, and legacy are decoded separately, including bandwidth, SGI, LDPC, STBC, NSS, and BF flags. It then handles scheduled-scan pass-all beacon/probe response state, timestamps beacons/probe responses with boottime, and finally passes the SKB to mac80211.

Statistics flow is version-gated. If the system statistics command exists, legacy `STATISTICS_NOTIFICATION` is ignored. TLV version 14/15 handlers verify payload/header size and notification version, update beacon stats, radio times, per-station energy, per-mac TCM airtime/RX bytes when stats were cleared, and per-phy channel load. Newer system operational stats use per-link data and aggregate airtime/RX bytes per vif ID only when `mvm->statistics_clear` is set to avoid double counting.

## State and Persistence
`mvm->last_phy_info` and `mvm->ampdu_ref` bridge PHY and MPDU notifications. `rx_status` is per-SKB and handed to mac80211. Persistent updates include `mvmsta->deflink.avg_energy`, `mvmvif->link[*].beacon_stats`, `mvmvif->deflink.beacon_stats`, `mvm->radio_stats`, `mvm->rx_stats`/`rx_stats_v3`, `mvm->phy_ctxts[*].channel_load_*`, TCM counters, and RS RSSI via `rs_update_last_rssi()`. CQM and BT-coex last-event thresholds are stored in link beacon-filter data to avoid duplicate notifications.

## Dependencies and Integration Points
This file depends on firmware RX/status structures, MVM station/vif maps, mac80211 RX APIs, checksum offload flags, debug trigger infrastructure, TCM work, BT coexistence RSSI events, rate-scaling RSSI state in `rs.c`, and BA reordering support. Its behavior is tied to firmware API version helpers such as `iwl_mvm_has_new_rx_api()`, `iwl_mvm_has_new_rx_stats_api()`, `iwl_fw_lookup_notif_ver()`, and command-version lookup.

## Risks
- The PHY/MPDU split assumes `mvm->last_phy_info` is the correct metadata for the following MPDU sequence; ordering bugs or API transitions can misattribute rates, RSSI, or AMPDU references.
- Length validation is critical because the handler computes header and trailer offsets inside firmware-provided buffers.
- Security status mapping must be conservative. Incorrect MIC/ICV handling can either drop valid frames or pass corrupted/decrypted frames incorrectly.
- Statistics format handling has many version branches; a firmware ABI mismatch can silently skip stats or double-count airtime if clear flags are misunderstood.
- RCU station/vif lookups must tolerate station removal and CSA transitions.
- The SKB fragment path steals the RX page, so offset/length errors could corrupt packet delivery or page ownership.

## Test Signals
- RX MPDU tests should cover bad length, bad CRC/FIFO, encrypted CCMP/TKIP/WEP/EXT cases, multicast before authorization, and missing station mapping.
- Rate decode coverage should include HT, VHT, legacy, SGI, LDPC, STBC, BF, and bandwidth cases.
- Monitor-mode paths should preserve CRC-failed frames with `RX_FLAG_FAILED_FCS_CRC`.
- Statistics tests should replay legacy, TLV v14/v15, and system operational notifications and verify beacon stats, radio stats, average energy, TCM updates, and per-phy channel load.
- BA-window notifications should mark filtered frames only for valid TID entries with nonzero MPDU counts and valid station IDs.
