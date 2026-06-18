# subset-b-004836 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rxmq.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rxmq.c

### Purpose
`rxmq.c` is the Intel iwlwifi MVM multi-queue receive path. It turns firmware RX notifications into mac80211 `sk_buff` deliveries, while validating decryption state, packet numbers, duplicate sequence numbers, BlockAck reordering, checksum metadata, RSSI/rate status, monitor-mode radiotap data, scan/MEI filters, and beacon-filter energy updates.

### Important APIs, Types, And Functions
The public RX handlers are `iwl_mvm_rx_mpdu_mq()`, `iwl_mvm_rx_monitor_no_data()`, `iwl_mvm_rx_queue_notif()`, `iwl_mvm_rx_frame_release()`, `iwl_mvm_rx_bar_frame_release()`, and `iwl_mvm_rx_beacon_filter_notif()`. Core helpers include `iwl_mvm_create_skb()`, `iwl_mvm_pass_packet_to_mac80211()`, `iwl_mvm_rx_crypto()`, `iwl_mvm_check_pn()`, `iwl_mvm_is_dup()`, `iwl_mvm_reorder()`, `iwl_mvm_release_frames()`, `iwl_mvm_agg_rx_received()`, `iwl_mvm_rx_fill_status()`, `iwl_mvm_rx_he()`, `iwl_mvm_rx_eht()`, and the HE/EHT/LSIG radiotap decoders. The local `struct iwl_mvm_rx_phy_data` normalizes firmware v1/v3 descriptor fields before rate/status decoding.

### Control Flow
`iwl_mvm_rx_mpdu_mq()` rejects RX during hardware restart, validates descriptor size and firmware-reported MPDU length, extracts descriptor-version-specific PHY fields, allocates a small skb head, marks CRC/FIFO failures for monitor consumers, sets TSF and band, and tracks A-MPDU references on the default queue. Under RCU it resolves the source station from firmware status or MAC address, processes crypto and protected management beacon status, fills mac80211 RX status, updates TCM and CSA unblock state, updates RSSI and low-RSSI debug triggers, applies RX checksum offload, rejects duplicates, fixes hardware-deaggregated A-MSDU QoS/address quirks, updates BA timeout activity, records scheduled-scan pass-all observations, creates the skb payload/frags, and finally either buffers through reorder logic or passes to mac80211 after time-sync and MEI scan filters.

`iwl_mvm_reorder()` interprets firmware reorder metadata, validates BAID/TID/station mapping, handles invalid or old sequence numbers, buffers holes per RX queue in `iwl_mvm_baid_data` entries, and releases contiguous frames through `iwl_mvm_release_frames()`. Firmware release notifications and BAR release notifications call `iwl_mvm_release_frames_from_notif()` to advance NSSN-driven delivery. `iwl_mvm_rx_queue_notif()` handles internal RX queue sync notifications and DELBA cleanup.

`iwl_mvm_rx_monitor_no_data()` builds zero-length PSDU reports for monitor mode, including failed PLCP, no-PSDU type, PHY/rate status, and HE/EHT no-data NSS overrides, then delivers directly to mac80211. `iwl_mvm_rx_beacon_filter_notif()` stores firmware average beacon energy on the vif link, which `iwl_mvm_get_signal_strength()` can later use to override RSSI for filtered beacons.

### State, Persistence, And Dependencies
RX state is in-memory and spread across `struct iwl_mvm`, per-station `struct iwl_mvm_sta`, `ptk_pn` packet-number tables, duplicate tracking arrays, BAID maps, reorder buffers, firmware-id-to-station mappings, scan pass-all state, PTP/timing fields, and per-vif average beacon energy. Reorder buffers are protected by per-buffer spinlocks; station/vif lookups use RCU; queue sync uses `queue_sync_state`, `queue_sync_cookie`, and `rx_sync_waitq`. Persistent effects are packet delivery to mac80211, debug trigger collection, checksum/radiotap metadata, and state updates such as `last_rx`, `average_beacon_energy`, `ampdu_ref`, and `sched_scan_pass_all`.

The file depends on mac80211/cfg80211 RX APIs, Linux skb page-frag mechanics, firmware descriptor definitions from `fw-api.h`, transport family/version checks, MVM station/vif helpers, rate conversion helpers, PTP time-sync, MEI scan filtering, TCM work scheduling, and firmware capability/API gates.

### Integration Points
This is the data-path bridge between the transport firmware RX ring and mac80211. It integrates with security by reporting beacon-protection MIC/replay failures and setting `RX_FLAG_DECRYPTED`, `RX_FLAG_MIC_STRIPPED`, `RX_FLAG_PN_VALIDATED`, and related flags. It integrates with aggregation setup/teardown code through `mvm->baid_map`; with scan code through scheduled-scan pass-all state and MEI filtering; with monitor tools through HE/EHT/LSIG/vendor radiotap TLVs; with CSA handling through `csa_tx_blocked_vif`; and with network stack performance through checksum offload and skb frag stealing.

### Risks
The highest-risk areas are ordering and security invariants. PN validation is skipped for queue 0 and delegated to mac80211, but non-default queues rely on correct per-key/per-TID tables and duplicate handling to allow same PN only for valid A-MSDU subframes. Reorder buffering must not release A-MSDU subframes too early when NSSN advances on the first subframe. BAID/TID/station mismatches are guarded but firmware or driver state races can bypass reordering. Descriptor-version checks, device-family conditionals, and TSF-overload PHY decoding are subtle and can produce wrong radiotap/rate metadata. `iwl_mvm_create_skb()` mixes copied head data and stolen RX pages, so length, pad, crypto header, MIC/FCS stripping, and checksum adjustment errors can corrupt delivered frames.

### Test Signals
Useful signals include RX under CCMP/GCMP/TKIP/WEP and open networks; replay, same-PN A-MSDU, duplicate sequence, old NSSN, BAR release, DELBA, and reorder-hole scenarios; monitor capture of HE/EHT MU/TB and no-data frames; checksum offload validation on pre-Bz and Bz+ hardware families; beacon-protection MIC/replay failure reporting; scheduled-scan pass-all result notifications; CSA unblock on channel switch; hardware restart suppression; and fuzz or fault injection around short descriptors, invalid BAIDs, invalid station IDs, and inconsistent MPDU lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rxmq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/scan.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/scan.c

### Purpose
`scan.c` implements Intel iwlwifi MVM scan orchestration. It translates cfg80211/mac80211 regular scan, scheduled scan, net-detect, 6 GHz, P2P-aware, OCE, adaptive-dwell, and MEI-limited scan requests into firmware LMAC or UMAC scan commands, tracks concurrent scan state, handles scan completion/iteration notifications, aborts scans, and records ACS channel survey data.

### Important APIs, Types, And Functions
`struct iwl_mvm_scan_params` is the central request model used after mac80211 input is normalized. Public entry points include `iwl_mvm_max_scan_ie_len()`, `iwl_mvm_config_scan()`, `iwl_mvm_reg_scan_start()`, `iwl_mvm_sched_scan_start()`, `iwl_mvm_scan_stop()`, `iwl_mvm_scan_size()`, `iwl_mvm_report_scan_aborted()`, `iwl_mvm_mei_scan_filter_init()`, and notification handlers for LMAC/UMAC scan completion, iteration completion, match found, and channel survey.

Important helpers include scan-type selection (`iwl_mvm_get_scan_type*()`), scan fitting and IE/probe construction (`iwl_mvm_scan_fits()`, `iwl_mvm_build_scan_probe()`), scheduled-scan profile programming (`iwl_mvm_config_sched_scan_profiles()`), LMAC command construction (`iwl_mvm_scan_lmac()`), reduced/legacy scan configuration (`iwl_mvm_config_scan()`, `iwl_mvm_legacy_config_scan()`), UMAC command construction across versions (`iwl_mvm_scan_umac()`, `iwl_mvm_scan_umac_v12()`, `iwl_mvm_scan_umac_v14_and_above()` and v14-v17 wrappers), 6 GHz channel/probe helpers, concurrent scan arbitration (`iwl_mvm_check_running_scans()`), and stop/abort helpers (`iwl_mvm_scan_stop_wait()`, `iwl_mvm_umac_scan_abort()`, `iwl_mvm_lmac_scan_abort()`).

### Control Flow
Regular scans enter `iwl_mvm_reg_scan_start()` and scheduled/net-detect scans enter `iwl_mvm_sched_scan_start()`. Both paths assert `mvm->mutex`, reject scans before LAR regulatory setup, arbitrate against existing scan state, populate `iwl_mvm_scan_params`, derive low-band/high-band scan types from TCM load and low-latency state, calculate whether P2P GO operation must be respected, build a probe request with optional random MAC, per-band IEs, DS parameter placeholder, and WFA TPC IE handling, then call `iwl_mvm_build_scan_cmd()`.

`iwl_mvm_build_scan_cmd()` clears `mvm->scan_cmd`, applies MEI-limited scan rewriting when CSME link protection requires scanning only the connected AP/channel, then chooses LMAC `SCAN_OFFLOAD_REQUEST_CMD` or UMAC `SCAN_REQ_UMAC` by firmware capability. UMAC scans allocate a UID from `mvm->scan_uid_status` and dispatch to the exact firmware command version handler when available, falling back to older adaptive-dwell/CDB layouts.

LMAC setup fills dwell timing, scan flags, TX command rates, direct SSIDs, schedule lines, EBS channel options, channel configs, and a legacy probe request. UMAC setup fills general flags, dwell/adaptive dwell budgets, OOC priority, fragmented scan counts, schedule delay/iterations, probe parameters, and channel parameters. Version 14+ uses separate general/probe/channel structs; version 15 adds `flags2`; version 16 uses link IDs for TSF reporting; version 17 packs band in channel flags and stores 6 GHz PSD data.

6 GHz scans use short-SSID and BSSID arrays, PSC/non-PSC logic, unsolicited probe response hints, hidden SSID support, forced passive fallback, and optional passive PSC scan insertion after reset/resume or timeout. Scheduled scans program match profiles first and may filter 6 GHz scheduled channels to PSC-only. Successful regular scans pause TCM and arm a 30 second timeout work item; completion resumes TCM and reports mac80211 completion.

### State, Persistence, And Dependencies
Scan state persists in `mvm->scan_status`, `mvm->scan_uid_status[]`, `mvm->max_scans`, `mvm->scan_cmd`, `mvm->scan_cmd_size`, `mvm->scan_type`, `mvm->hb_scan_type`, `mvm->scan_vif`, `mvm->scan_link_id`, `mvm->scan_start`, `mvm->sched_scan_pass_all`, `mvm->last_ebs_successful`, passive-6GHz timestamps, MEI scan filter queues, and optional ACS survey storage. Regular scan timeout uses `scan_timeout_dwork` and forces an NMI on expiry. UMAC abort marks UID status as a shifted stopping state while waiting for completion. Scheduled-scan pass-all state is toggled by RX path detection of beacons/probe responses and by iteration notifications.

The file depends on mac80211/cfg80211 scan request structures and completion APIs, firmware scan command definitions in `fw/api/scan.h`, firmware capability/version lookup helpers, NVM band/channel data, MVM TCM and low-latency state, LAR regulatory state, MEI/CSME connection information, debugfs knobs, OCE and 6 GHz cfg80211 flags, and notification waiting infrastructure.

### Integration Points
This file is the scan control plane for MVM. It interacts with the RX path through scheduled-scan pass-all and MEI scan filtering, with mac80211 through `ieee80211_scan_completed()`, `ieee80211_sched_scan_results()`, and `ieee80211_sched_scan_stopped()`, with firmware through LMAC/UMAC scan request/config/abort commands, with regulatory handling through LAR readiness, with P2P by preserving GO operation under low latency, with net-detect through scan type arbitration, and with AP ACS through channel survey notifications.

### Risks
The main risks are version-specific command layout drift, scan UID/status races, and edge cases in channel/IE sizing. `iwl_mvm_max_scan_ie_len()` intentionally overreports for LMAC because the API shares a fixed probe buffer across bands, so large IEs can still fail later with `-ENOBUFS`. Concurrent scan arbitration stops opposite scan types for compatibility and must keep mac80211 notifications consistent. 6 GHz active/passive selection has many limits around PSC, hidden SSIDs, unsolicited probe responses, RNR-derived BSSID/short-SSID lists, PSD, and passive-scan timers. MEI-limited scans mutate caller-derived params and depend on valid CSME connection state. Timeout handling deliberately forces an NMI, so false timeouts are severe.

### Test Signals
High-value tests include regular and scheduled scans across LMAC and UMAC firmware versions 12, 14, 15, 16, and 17; scans with random MACs, large per-band IEs, wildcard and directed SSIDs, OCE flags, pass-all scheduled scans, multiple scan plans, delayed scheduled scans, and net-detect. Exercise concurrent regular/scheduled arbitration, abort paths including UMAC `NOT_FOUND`, hardware restart reporting, regular scan timeout, LAR-not-ready rejection, P2P GO low-latency respect flags, MEI-limited scan filtering, 6 GHz PSC/non-PSC and hidden SSID cases, passive 6 GHz insertion conditions, EBS success/failure state, and ACS survey notification allocation/population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sf.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sf.c

### Purpose
`sf.c` manages iwlwifi MVM Smart FIFO configuration. Smart FIFO changes firmware buffering/watermark and timeout behavior based on active interface count and whether the single active station interface is associated with an AP.

### Important APIs, Types, And Functions
The public entry point is `iwl_mvm_sf_update()`. `struct iwl_mvm_active_iface_iterator_data` carries state while iterating active interfaces. `iwl_mvm_bound_iface_iterator()` counts active non-P2P-device MACs with bound PHY contexts and captures station AP state. `iwl_mvm_fill_sf_command()` builds `struct iwl_sf_cfg_cmd` watermarks and timeout tables. `iwl_mvm_sf_config()` validates and sends `REPLY_SF_CFG_CMD` and updates `mvm->sf_state`.

### Control Flow
`iwl_mvm_sf_update()` exits early when firmware exposes the newer Smart FIFO offload API, during hardware restart, or for P2P-device vifs. It iterates active interfaces excluding the changed vif, optionally adds the changed vif if it is not being removed, and chooses the target state. With no active MACs it selects `SF_INIT_OFF`; with one active MAC it selects `SF_FULL_ON` only for an associated station vif with a DTIM period, `SF_INIT_OFF` for unassociated station state, or `SF_UNINIT` for a single non-station interface; with multiple active MACs it selects `SF_UNINIT`. It then delegates to `iwl_mvm_sf_config()`.

`iwl_mvm_sf_config()` avoids redundant commands except when remaining in `SF_FULL_ON`, because station antenna/NSS capabilities may have changed and the watermarks need recalculation. For `SF_FULL_ON`, it requires a station pointer. `iwl_mvm_fill_sf_command()` derives the full-on watermark from the AP station link capabilities: legacy uses `SF_W_MARK_LEGACY`; HT/VHT/HE/EHT links choose SISO, MIMO2, or MIMO3 by maximum RX NSS across links. Unassociated/default configuration uses MIMO2 and the default timeout table. All long-delay timeouts use `SF_LONG_DELAY_AGING_TIMER`; full-on timeouts are copied from station or default static tables.

### State, Persistence, And Dependencies
Persistent driver state is `mvm->sf_state`; firmware state is updated asynchronously by `REPLY_SF_CFG_CMD`. The command contains state, two watermark slots, long-delay timeout matrix, and full-on timeout matrix. The file depends on mac80211 active-interface iteration, MVM vif wrappers, station link capabilities under RCU, firmware API capability checks, Smart FIFO constants/macros from MVM headers, and `iwl_mvm_send_cmd_pdu()`.

### Integration Points
Smart FIFO updates are expected around vif add/remove and association state transitions. The logic integrates with interface binding (`deflink.phy_ctxt`), station association (`vif->cfg.assoc`, `bss_conf.dtim_period`, `mvmvif->ap_sta`), MLO link station capabilities, hardware restart state, and firmware capability negotiation. It deliberately ignores P2P devices and turns Smart FIFO off/uninitialized when multiple active MACs make single-BSS assumptions invalid.

### Risks
The state choice depends on active-interface iteration plus a separate changed-vif adjustment, so callers must pass `changed_vif` and `remove_vif` accurately. `SF_FULL_ON` requires `mvmvif->ap_sta`; missing AP station data returns `-EINVAL`. NSS selection scans all station links under RCU and treats any HT/VHT/HE/EHT support as non-legacy; incorrect link capability data can produce wrong watermarks. The command is sent asynchronously, so `mvm->sf_state` records successful submission rather than firmware completion. Firmware supporting `IWL_UCODE_TLV_API_SMART_FIFO_OFFLOAD` bypasses this path entirely.

### Test Signals
Exercise transitions for zero interfaces, one unassociated station, one associated station with DTIM, one AP/non-station interface, multiple active MACs, changed-vif removal, P2P-device ignore, hardware restart ignore, and firmware offload-capability ignore. Validate watermark selection for legacy, 1x1, 2x2, and 3+ NSS AP links, including MLO stations with multiple links. Check that repeated non-`SF_FULL_ON` states suppress duplicate commands and repeated `SF_FULL_ON` recalculates after antenna capability changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sf.c -->
