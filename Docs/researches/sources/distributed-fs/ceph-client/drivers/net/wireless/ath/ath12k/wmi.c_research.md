# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wmi.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004752`: lines 1-8859, `Docs/researches/chunks/subset-b-004752_research.md`
- `subset-b-004753`: lines 8860-11314, `Docs/researches/chunks/subset-b-004753_research.md`

## Chunk Research

### subset-b-004752: lines 1-8859

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wmi.c lines 1-8859

## Scope

This chunk covers the main body of the ath12k WMI transport and firmware-control implementation from the top of `wmi.c` through the beginning of `ath12k_probe_resp_tx_status_event()`. The requested range includes TLV framing/parsing helpers, WMI command submission, service-ready capability parsing, most vdev/peer/pdev command builders, scan and regulatory command paths, firmware initialization, spectral/direct-buffer setup, extended capability and hardware-mode parsing, regulatory and management event handling, scan/state-machine events, firmware statistics parsing, CSA/DFS/thermal/FILS events, and the start of probe-response TX status handling.

The range ends at line 8859 inside `ath12k_probe_resp_tx_status_event()`. The remainder of that event handler, the WMI event dispatcher, attach/connect/detach code, WoW/offload/MLO commands, and other tail functions are outside this chunk and should be reconciled by `subset-b-004753`.

## Purpose

`wmi.c` is the host-side WMI protocol layer for ath12k. It translates mac80211/ath12k core operations into firmware TLV commands, parses asynchronous WMI events back into host state, and gates initialization on firmware service/capability events.

In this chunk, the file is responsible for:

- constructing WMI TLV messages in `sk_buff`s and sending them over HTC endpoints;
- parsing TLV events with per-tag minimum-length validation;
- learning firmware services, target capabilities, per-radio MAC/PHY capabilities, EHT/MLO features, regulatory ranges, direct-buffer ring capabilities, and preferred hardware mode;
- creating, starting, stopping, deleting, and bringing up/down vdevs, including MBSSID/EMA and MLO vdev parameters;
- creating/deleting peers, installing keys, associating peers, configuring reorder queues, BA sessions, WMM, power-save, OBSS/Spatial Reuse, TWT, FILS, probe-response and beacon templates;
- issuing scan, channel-list, country, 11d, statistics, spectral, DMA-ring, LRO, BIOS/SAR/GEO, DFS, temperature, and firmware-hang commands;
- consuming firmware events for vdev/peer completions, management RX/TX, scan progress, regulatory updates, station kickout, roam/beacon miss, channel survey, key install completion, service availability, firmware stats, CSA, DFS radar, testmode FTM segments, thermal readings, and FILS/probe-response notifications.

## Important APIs, Types, and Functions

### TLV and Command Transport

`ath12k_wmi_tlv_hdr()` and `ath12k_wmi_tlv_cmd_hdr()` encode WMI tags and payload lengths into little-endian TLV headers. `ath12k_wmi_tlv_iter()` is the central parser: it walks a byte buffer, validates TLV header and payload lengths, checks `ath12k_wmi_tlv_policies[]` minimum sizes for known event tags, and invokes a caller-supplied iterator. `ath12k_wmi_tlv_parse_alloc()` builds a tag-indexed lookup table for event handlers that expect one instance of a tag.

`ath12k_wmi_alloc_skb()` allocates HTC-backed WMI buffers with `WMI_SKB_HEADROOM`, 4-byte alignment, zeroed rounded length, and an alignment warning. `ath12k_wmi_cmd_send_nowait()` prepends `struct wmi_cmd_hdr` and sends via `ath12k_htc_send()`. `ath12k_wmi_cmd_send()` wraps this in a wait on `wmi_ab->tx_credits_wq`, converts crash flushes to `-ESHUTDOWN`, and warns on `WMI_SEND_TIMEOUT_HZ` timeout.

### Service Ready, Capabilities, and Initialization

`ath12k_service_ready_event()` parses `WMI_TAG_SERVICE_READY_EVENT` and the base service bitmap into `ab->target_caps` and `ab->wmi_ab.svc_map`. `ath12k_service_available_event()` extends the service map from later segmented service bitmaps.

`ath12k_service_ready_ext_event()` and helpers parse the first extended capability event. `ath12k_wmi_hw_mode_caps()` selects `wmi_ab.preferred_hw_mode` using `ath12k_hw_mode_pri_map`. `ath12k_pull_mac_phy_cap_svc_ready_ext()` populates `ab->pdevs[]`, `ab->fw_pdev[]`, `pdev->cap`, per-band HT/HE fields, chainmasks, NSS ratio data, pdev IDs, and hardware link IDs. `ath12k_wmi_ext_hal_reg_caps()` saves regulatory hardware ranges into `ab->hal_reg_cap[]`. `ath12k_wmi_dma_ring_caps()` allocates and fills `ab->db_caps`/`ab->num_db_cap`.

`ath12k_service_ready_ext2_event()` parses later EHT/DBS/SBS capability data. `ath12k_wmi_tlv_mac_phy_caps_ext()` and `ath12k_wmi_eht_caps_parse()` fill EHT MAC/PHY/MCS/PPE data and MLD/EML capabilities. The hardware-mode range helpers update `ab->wmi_ab.hw_mode_info.freq_range_caps`, derive DBS/SBS support, split shared 5 GHz ranges, and record `sbs_lower_band_end_freq`.

`ath12k_wmi_cmd_init()` obtains chip-specific resource settings through `ab->hw_params->wmi_init()`, persists `ab->wow.wmi_conf_rx_decap_mode`, passes memory chunks and preferred hardware mode to `ath12k_init_cmd_send()`, fills band-to-MAC mappings from regulatory caps, and copies `peer_metadata_ver` into datapath state. `ath12k_ready_event()` later marks `ab->wmi_ready`, stores primary and per-pdev MAC addresses, saves `pktlog_defs_checksum`, and completes `unified_ready`.

### Vdev, Peer, Key, and Association Commands

Vdev commands include `ath12k_wmi_vdev_create()`, `ath12k_wmi_vdev_delete()`, `ath12k_wmi_vdev_start()`, `ath12k_wmi_vdev_stop()`, `ath12k_wmi_vdev_down()`, and `ath12k_wmi_vdev_up()`. They map host vdev arguments into firmware TLVs, including per-band TX/RX stream counts, MBSSID fields, EMA beacon metadata, MLO vdev create/start TLVs, partner link information, channel definition via `ath12k_wmi_put_wmi_channel()`, CSA/PMF/hidden-SSID flags, puncturing bitmap, and BSSID/association IDs.

Peer commands include `ath12k_wmi_send_peer_create_cmd()`, `ath12k_wmi_send_peer_delete_cmd()`, `ath12k_wmi_set_peer_param()`, `ath12k_wmi_send_peer_flush_tids_cmd()`, `ath12k_wmi_peer_rx_reorder_queue_setup()`, and `ath12k_wmi_rx_reord_queue_remove()`. MLO peer creation and association TLVs carry MLO enable flags, logical-link indexes, MLD address, peer ID, associated/primary UMAC flags, partner links, and EMLSR timing values.

`ath12k_wmi_vdev_install_key()` sends cipher/key material and optional RSC to firmware; `ath12k_vdev_install_key_compl_event()` records `ar->install_key_status` and completes `ar->install_key_done`. `ath12k_wmi_copy_peer_flags()` translates peer association flags for QoS, APSD, HT/VHT/HE/EHT, bandwidth, STBC/LDPC, TWT, PMF, authorization, 4-way/2-way handshake needs, safe mode, and disabled HT rates. `ath12k_wmi_send_peer_assoc_cmd()` serializes legacy, HT, VHT, HE, EHT, and MLO association state into a large multi-TLV command.

### Management, Beacon, Scan, Regulatory, and Pdev Commands

`ath12k_wmi_mgmt_send()` sends management frames through WMI, DMA-addressed by `ATH12K_SKB_CB(frame)->paddr`, with optional link-agnostic MLO TX parameters when firmware/hw ops identify the frame as link agnostic. `ath12k_wmi_bcn_tmpl()`, `ath12k_wmi_p2p_go_bcn_ie()`, `ath12k_wmi_fils_discovery_tmpl()`, `ath12k_wmi_probe_resp_tmpl()`, and `ath12k_wmi_fils_discovery()` program firmware offload templates and intervals.

Scan setup is split across `ath12k_wmi_start_scan_init()`, `ath12k_wmi_send_scan_start_cmd()`, `ath12k_wmi_send_scan_stop_cmd()`, and `ath12k_wmi_send_scan_chan_list_cmd()`. The scan start command serializes channels, SSIDs, BSSIDs, extra IEs, short-SSID hints, BSSID hints, dwell/rest timings, event subscriptions, and control flags, while dropping overlarge extra IE payloads relative to `max_msg_len`. Channel-list programming chunks large lists by `ATH12K_WMI_MAX_NUM_CHAN_PER_CMD` and firmware message size.

Regulatory paths include `ath12k_wmi_send_pdev_set_regdomain()`, `ath12k_wmi_send_init_country_cmd()`, `ath12k_wmi_send_set_current_country_cmd()`, `ath12k_wmi_send_11d_scan_start_cmd()`, `ath12k_wmi_send_11d_scan_stop_cmd()`, `ath12k_reg_11d_new_cc_event()`, and `ath12k_reg_chan_list_event()`. `ath12k_pull_reg_chan_list_ext_update_ev()` validates 2/5/6 GHz rule counts, allocates `struct ath12k_reg_rule` arrays, filters firmware-supplied 6 GHz rules from the 5 GHz list, records AP/client 6 GHz regulatory domains and bandwidths, then hands the result to regulatory validation and channel-list handling.

Other command builders cover pdev/vdev parameters, AP/STA power-save parameters, forced firmware hang, pdev temperature request, beacon offload control, WMM, DFS phyerr offload, BIOS interface blobs, ACPI SAR and GEO tables, DELBA/ADDBA flows, TWT enable/disable, OBSS PD and BSS-color commands, LRO, spectral scan configuration/enablement, direct-buffer DMA ring configuration, pdev suspend/resume, BSS channel survey request, statistics request, and hardware mode setting.

### Event Handlers and State Completion

Most event handlers follow a common pattern: parse TLVs, validate required tags, map pdev/vdev IDs to `struct ath12k` or `struct ath12k_link_vif` under RCU, update host state, and complete a waiter or call a mac80211/cfg80211 callback.

Important completions and state updates include:

- `ath12k_peer_delete_resp_event()` completes `ar->peer_delete_done`;
- `ath12k_vdev_delete_resp_event()` completes `ar->vdev_delete_done`;
- `ath12k_vdev_start_resp_event()` stores `ar->last_wmi_vdev_start_status`, `ar->max_allowed_tx_power`, and completes `ar->vdev_setup_done`;
- `ath12k_vdev_stopped_event()` completes `ar->vdev_setup_done`;
- `ath12k_peer_assoc_conf_event()` completes `ar->peer_assoc_done`;
- `ath12k_reg_chan_list_event()` replaces `ab->reg_info[pdev_idx]`, calls regulatory handlers, and completes `ar->regd_update_completed`;
- `ath12k_update_stats_event()` splices parsed stats into `ar->fw_stats`, completes `fw_stats_done` and `fw_stats_complete`;
- `ath12k_wmi_pdev_temperature_event()` forwards temperatures to thermal code;
- `ath12k_wmi_pdev_dfs_radar_detected_event()` calls `ieee80211_radar_detected()` unless radar events are blocked;
- `ath12k_wmi_pdev_csa_switch_count_status_event()` updates CSA countdown or calls `ieee80211_csa_finish()`;
- `ath12k_wmi_obss_color_collision_event()` calls `ieee80211_obss_color_collision_notify()`.

Management RX/TX is handled by `ath12k_mgmt_rx_event()` and `ath12k_mgmt_tx_compl_event()`. RX events rewrite the skb to contain only the management frame, fill `ieee80211_rx_status`, drop frames during CAC or with fatal RX errors, set PMF/decryption flags, handle beacons, and pass frames to `ieee80211_rx_ni()`. TX completions remove the MSDU from `ar->txmgmt_idr`, unmap DMA, set ACK/NOACK status, report through `ieee80211_tx_status_irqsafe()`, decrement `num_pending_mgmt_tx`, and wake `txmgmt_empty_waitq` when empty.

Scan events are state-machine driven. `ath12k_scan_event()` maps firmware events to the correct radio, including cancelled-scan fallback lookup by scan state. Under `ar->data_lock`, it transitions STARTING to RUNNING, completes `ar->scan.started`, completes remain-on-channel on matching foreign-channel events, clears `scan_channel` on BSS-channel events, and finishes scans on COMPLETED, START_FAILED, or DEQUEUED.

## Control Flow

Initialization starts with base service-ready parsing, then extended service-ready parsing. Base service bits populate `svc_map`; extended events populate target capabilities, radio count, pdev capabilities, HAL regulatory caps, direct-buffer caps, EHT/MLO capabilities, and hardware mode frequency ranges. If `WMI_TLV_SERVICE_EXT2_MSG` is absent, EXT1 completes `service_ready`; otherwise EXT2 completes it. After the service-ready wait, `ath12k_wmi_cmd_init()` sends the firmware resource configuration and optional hardware-mode/band-to-MAC mappings. `ath12k_ready_event()` completes `unified_ready`.

Command flow is generally: compute TLV length, allocate a rounded WMI skb, write the fixed command TLV, append array/fixed-struct/nested TLVs, send via `ath12k_wmi_cmd_send()`, and free the skb on send failure. The code consistently uses little-endian conversions at the firmware boundary and leaves host-side arguments in CPU order.

Vdev flow is: create vdev with MAC, pdev, streams, optional MLD address; start/restart with channel and optional MLO partner links; firmware sends start response and `vdev_setup_done` completes; vdev up sends BSSID/AID; stop/down/delete use their own WMI commands and events. Peer flow is similar: create peer, send peer association with rate/security/MLO state, wait for peer assoc confirmation, and later delete peer with a completion event.

Scan flow is: host initializes scan defaults, emits channel list updates separately when needed, sends start scan with full channel/SSID/BSSID/IE payload, then the scan event handler drives `ar->scan.state` and mac80211 scan/ROC completion. Stop scan converts ath12k cancel request types to firmware stop types and returns `-EINVAL` for unknown request types.

Regulatory flow is: host can set initial/current country or start/stop 11d scan; firmware sends new-country or extended channel-list events; the handler builds host `ath12k_reg_info`, validates rule counts and content, replaces cached `ab->reg_info[phy]`, invokes `ath12k_reg_handle_chan_list()`, and completes waiters for post-country-change processing.

Statistics flow is: host requests stats, firmware sends a `WMI_TAG_STATS_EVENT` plus data arrays; parser allocates per-vdev, per-beacon, or per-pdev stat nodes and updates per-station beacon/chain RSSI when possible; event processing splices lists into `ar->fw_stats` and completes the relevant waiters.

## State and Persistence Behavior

The chunk persists firmware-discovered capabilities in `struct ath12k_base`: `target_caps`, `wmi_ab.svc_map`, `wmi_ab.svc_ext_info`, `wmi_ab.preferred_hw_mode`, `wmi_ab.hw_mode_info`, `wmi_ab.dp_peer_meta_data_ver`, `wmi_ab.sbs_lower_band_end_freq`, `hal_reg_cap[]`, `pdevs[]`, `fw_pdev[]`, `fw_pdev_count`, `num_radios`, `db_caps`, `num_db_cap`, primary/per-pdev MAC addresses, `wlan_init_status`, `pktlog_defs_checksum`, `wmi_ready`, `reg_info[]`, and `new_alpha2`.

Per-radio state in `struct ath12k` is updated through completions and event handlers: scan state, `scan_channel`, `last_wmi_vdev_start_status`, `max_allowed_tx_power`, `install_key_status`, `fw_stats`, `fw_stats_done`, `fw_stats_complete`, `num_pending_mgmt_tx`, survey data, BSS survey completion, 11d state, and regulatory update completions.

Per-vif/per-station state is touched through lookup helpers: OBSS color notifications use `arvif->link_id`; beacon template programming stores `arvif->current_cntdown_counter`; CSA events update `current_cntdown_counter` and finish CSA through mac80211; peer kickout and roam events call beacon-miss or low-ACK handlers; RSSI stats update `arsta->rssi_beacon` and `arsta->chain_signal`.

Allocated state has explicit cleanup paths in this chunk. Temporary TLV lookup tables are freed after parsing. Extended MAC/PHY caps are allocated during service-ready parsing and freed on exit. Direct-buffer caps are freed on service-ready parse errors or invalid module IDs. Regulatory rule arrays are owned by `ath12k_reg_info` and reset through `ath12k_reg_reset_reg_info()` on validation/drop/error paths. Firmware stats lists are either spliced into `ar->fw_stats` or freed on parse/lookup failure.

Locking is mixed: WMI send can sleep; event handlers often run in atomic context and use `GFP_ATOMIC`; RCU guards protect vdev/pdev/vif/station lookups; `ar->data_lock` protects scan and survey state; `ab->base_lock` protects station/base lookup updates; `txmgmt_idr_lock` protects management TX ID removal; completions and wait queues synchronize with sleeping lifecycle callers.

## Dependencies and Integration Points

The chunk depends on Linux networking and wireless core APIs: `sk_buff`, `idr`, DMA mapping, completions, wait queues, RCU, `ieee80211_rx_status`, `ieee80211_tx_status_irqsafe()`, `ieee80211_ready_on_channel()`, scan/channel helpers, cfg80211 regulatory structures, survey info, CSA finish/update, DFS radar notification, and OBSS color collision notification.

Internal ath12k dependencies include:

- HTC transport: `ath12k_htc_alloc_skb()` and `ath12k_htc_send()`;
- core/mac helpers: pdev/vdev/radio lookup, `ath12k_mac_get_ar_by_*()`, `ath12k_mac_get_arvif*()`, scan finish, beacon handling, beacon miss, station lookup, bitrate conversion, BSS link-conf lookup, and channel-context helpers;
- regulatory helpers: `ath12k_reg_validate_reg_info()`, `ath12k_reg_handle_chan_list()`, `ath12k_reg_reset_reg_info()`;
- datapath helpers: `ath12k_ab_to_dp()`, `DP_HW2SW_MACID()`, direct-buffer release via `ath12k_dbring_buffer_release_event()`;
- thermal/testmode/debug integrations: `ath12k_thermal_event_temperature()`, `ath12k_tm_process_event()`, `ath12k_dbg()`, `ath12k_warn()`;
- chip-specific `hw_params` callbacks and flags, including WMI init, single-pdev behavior, frame link-agnostic detection, REO queue-reference support, and message size limits.

Firmware ABI dependencies are pervasive: every command and event uses WMI tag IDs, command IDs, service bits, capability masks, firmware enum values, and little-endian struct layouts shared with `wmi.h`. The parser's minimum-length policy is a defensive ABI check for common event tags.

## Risks and Edge Cases

- TLV parsing is the trust boundary for firmware events. Incorrect minimum lengths or missed nested-array validation can lead to out-of-bounds reads; the code mitigates this with length checks but many handlers still rely on firmware-provided counts matching payload layout.
- The service-ready EXT parser depends on ordered `WMI_TAG_ARRAY_STRUCT` sections. If firmware reorders or omits arrays, boolean "done" sequencing can associate data with the wrong parser stage.
- `ath12k_pull_mac_phy_cap_svc_ready_ext()` increments `ab->fw_pdev_count` while deriving capabilities. Bad firmware phy maps or unsupported bands can return errors after partial state has been written.
- Single-pdev-only targets reuse `pdevs[0]` while tracking multiple firmware pdevs in `fw_pdev[]`; EHT-cap parsing must match pdev/phy IDs correctly to avoid advertising capabilities on the wrong band.
- Direct-buffer caps are allocated once and later duplicate caps are ignored. A parse failure frees caps, so later code must tolerate `ab->db_caps == NULL`.
- Many command builders manually compute nested TLV lengths. MLO peer/vdev association, scan, channel-list, beacon/probe templates, and regulatory rule parsing are particularly sensitive to count/length mismatch.
- `ath12k_wmi_set_bios_cmd()` returns `0` even if `ath12k_wmi_cmd_send()` fails, unlike the SAR/GEO variants; callers that expect hard failure may miss BIOS interface command errors.
- Scan start drops extra IEs that exceed firmware message size and continues with no extra IE. That avoids command failure but changes probe request content.
- Management RX rewrites the original skb buffer after validating frame length. Any future handler that assumes original TLV contents after `ath12k_pull_mgmt_rx_params_tlv()` would be wrong.
- Management TX completion must find the descriptor in `txmgmt_idr`; missing descriptors produce warnings and no mac80211 status, while incorrect pending counts trigger `WARN_ON_ONCE`.
- Regulatory event parsing allocates many rule arrays. Some allocation failures after earlier allocations return immediately after freeing only the TLV table; ownership/reset behavior relies on higher-level cleanup to avoid leaks.
- Scan, vdev, peer, key, regulatory, and stats completions are asynchronous. Missing firmware events can leave waiters blocked until timeout; duplicate or out-of-state events are generally warned and ignored.
- Channel survey conversion uses `ab->cc_freq_hz` or firmware `mac_clk_mhz`; incorrect units or zero frequencies would distort survey time accounting.
- DFS radar handling requires a valid channel context; if no context is found, radar is ignored with a warning.
- The chunk ends mid-function, so final behavior for probe-response TX status and the central WMI RX dispatcher cannot be concluded from this chunk alone.

## Test and Validation Signals

Useful validation for this chunk should emphasize firmware integration, error handling, and event sequencing:

- build coverage for ath12k with mac80211/cfg80211, regulatory, DFS, thermal, debugfs, testmode, and WoW-related config combinations;
- boot/firmware-start tests that verify service-ready, service-ready-ext, optional ext2, init command, and unified-ready completions on single-pdev and multi-pdev hardware;
- capability tests confirming advertised 2/5/6 GHz, HE/EHT, 320 MHz, chainmask, MLO/EML, DBS/SBS, regulatory range, and direct-buffer capabilities match firmware reports;
- vdev lifecycle tests for create/start/restart/up/down/stop/delete, MBSSID/EMA APs, MLO vdevs with partner links, CSA restart, and failure status propagation from vdev start response;
- peer lifecycle tests for peer create/delete, association confirmation, MLO peer association, EMLSR timing, key install completion, BA setup/teardown, reorder queue setup/removal, and peer flush;
- scan tests covering active/passive/6 GHz scans, hint BSSID/short-SSID payloads, overlarge extra IE handling, stop-scan request types, cancelled scans during teardown, ROC on-channel completion, and missing/duplicate scan events;
- regulatory tests for init/current country commands, 11d new-country events, extended 2/5/6 GHz channel-list parsing, invalid rule counts, 6 GHz rules embedded in the 5 GHz list, fallback/drop validation paths, and regd completion;
- management TX/RX tests for DMA mapping completion, ACK RSSI reporting, invalid descriptor handling, PMF decrypted management frames, CAC filtering, CRC/MIC/decrypt error handling, 6 GHz frequency handling, and beacon reporting;
- firmware stats tests for pdev/vdev/beacon/RSSI-chain requests, multi-radio vdev stat aggregation, empty stats warnings, per-station RSSI updates, and list cleanup on parse failure;
- event tests for peer kickout, roam/beacon miss, channel survey and BSS channel survey, OBSS color collision, CSA countdown, DFS radar, pdev temperature, direct-buffer release, FILS discovery, and FTM segmented testmode events;
- fault-injection tests for WMI send failures, TLV length truncation, missing required tags, invalid pdev/vdev IDs, allocation failures in regulatory/stats/direct-buffer parsing, service-ready array reordering, and firmware crash flush during command send.

## Cross-Chunk Notes

This chunk should be merged with `subset-b-004753` before producing the final per-file report for `sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wmi.c`. The next chunk starts at line 8860 and is expected to finish `ath12k_probe_resp_tx_status_event()`, cover the WMI receive dispatcher and WMI endpoint attach/connect/detach logic, and cover WoW/offload/MLO/tail command helpers that are not present in this range.

### subset-b-004753: lines 8860-11314

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wmi.c lines 8860-11314

## Scope

This chunk covers the late WMI event-handling and command-building region of `ath12k/wmi.c`. It starts in the probe-response TX status event tail, then handles P2P NoA, rfkill, diagnostic trace, TWT completion, WoW wakeup, GTK rekey status, MLO setup/teardown completion, debugfs TPC statistics, RSSI-to-dBm conversion events, the central WMI RX dispatcher, HTC WMI service connection, unit-test/radar simulation, WMI attach/connect/detach helpers, WoW command builders, ARP/NS and GTK rekey offload commands, STA keepalive, MLO setup/ready/teardown, 6 GHz TPC power programming, and MLO link-active commands.

This is not the whole WMI layer. It relies on earlier definitions in the same file for many event handlers and on `wmi.h` for TLV layouts, command IDs, service bits, and argument structures.

## Purpose

The covered code has three main responsibilities:

- Translate firmware WMI events into ath12k/mac80211 state changes or completions.
- Dispatch all inbound WMI events from the HTC endpoint to specific event parsers.
- Construct outbound firmware TLV commands for WoW, debug/test, lifecycle, regulatory/TPC, keepalive, and MLO control paths.

The common pattern is `ath12k_wmi_alloc_skb()` or TLV parse/iterate, fill or consume packed little-endian firmware structures, use `ath12k_wmi_cmd_send()` for outbound commands, and free the SKB only on send failure because successful sends transfer ownership.

## Important APIs, Types, and Functions

### Event Handlers

`ath12k_wmi_p2p_noa_event()` parses `WMI_TAG_P2P_NOA_EVENT` plus `WMI_TAG_P2P_NOA_INFO`, extracts `vdev_id`, looks up the radio with `ath12k_mac_get_ar_by_vdev_id()` under RCU, and passes the Notice of Absence data to `ath12k_p2p_noa_update_by_vdev_id()`. Invalid TLVs return protocol errors and invalid vdev IDs are logged.

`ath12k_rfkill_state_change_event()` parses `WMI_TAG_RFKILL_EVENT`, updates `ab->rfkill_radio_on` under `ab->base_lock`, and queues `ab->rfkill_work`. The event is base-wide rather than per-vdev.

`ath12k_wmi_diag_event()` is a trace-only path that emits the raw SKB payload with `trace_ath12k_wmi_diag()`.

`ath12k_wmi_twt_enable_event()` and `ath12k_wmi_twt_disable_event()` parse completion TLVs and log pdev/status. They do not update local state or complete waiters in this range.

`ath12k_wmi_event_wow_wakeup_host()` iterates the wakeup-host event with `ath12k_wmi_wow_wakeup_host_parse()`. The parser records the wake reason, dumps page-fault payloads for `WOW_REASON_PAGE_FAULT` after validating the supplied length, then the event completes `ab->wow.wakeup_completed`.

`ath12k_wmi_gtk_offload_status_event()` handles firmware GTK rekey status. It looks up `arvif` by vdev ID under RCU, stores the little-endian replay counter in `arvif->rekey_data.replay_ctr`, converts it to big-endian for supplicant expectations, and calls `ieee80211_gtk_rekey_notify()`.

`ath12k_wmi_event_mlo_setup_complete()` parses `WMI_TAG_MLO_SETUP_COMPLETE_EVENT`, maps the event pdev ID to a `struct ath12k`, stores `ar->mlo_setup_status`, and completes `ar->mlo_setup_done`. `ath12k_wmi_event_teardown_complete()` currently parses and validates teardown completion but has no local state update.

### Debugfs TPC Stats

When `CONFIG_ATH12K_DEBUGFS` is enabled, `ath12k_wmi_process_tpc_stats()` processes multipart HALPHY control-path TPC statistics events. The first TLV must be `WMI_TAG_HALPHY_CTRL_PATH_EVENT_FIXED_PARAM`; its pdev ID is translated with `ath12k_mac_get_ar_by_pdev_id(... + 1)`. The path holds RCU and `ar->data_lock`, ignores unsolicited or timed-out events when `ar->debug.tpc_request` is false, allocates `ar->debug.tpc_stats` on event count zero, requires monotonically increasing `event_count`, and completes `ar->debug.tpc_complete` when `end_of_event` is set.

`ath12k_wmi_tpc_stats_event_parser()` handles top-level TLVs: fixed params are already processed, struct arrays recurse into `ath12k_wmi_tpc_stats_subtlv_parser()`, and integer/byte arrays copy payload data into previously allocated arrays. `ath12k_tpc_get_reg_pwr()`, `ath12k_tpc_get_rate_array()`, and `ath12k_tpc_get_ctl_pwr_tbl()` validate type and dimension-derived lengths before allocating storage for regulatory power, rate arrays, and CTL power tables. `ath12k_wmi_free_tpc_stats_mem()` frees all nested buffers and clears `ar->debug.tpc_stats`; it requires `ar->data_lock`.

Without debugfs, `ath12k_wmi_process_tpc_stats()` is a no-op, so the dispatcher can still compile with the event ID present.

### RSSI dBm Conversion

`ath12k_wmi_rssi_dbm_conversion_params_info_event()` parses a fixed pdev ID, looks up the active pdev, iterates sub-TLVs, and updates `ar->rssi_info` under `ar->data_lock` through `ath12k_wmi_update_rssi_offsets()`. The resulting noise floor is `min_nf_dbm + temp_offset` and is visible through `ath12k_pdev_get_noise_floor()`.

`ath12k_wmi_rssi_dbm_conv_info_evt_subtlv_parser()` accepts parameter and temperature-offset sub-TLVs. For noise-floor data, it unpacks firmware-provided signed 32-bit words into an antenna-by-20-MHz-segment signed byte matrix, derives the number of 20 MHz segments from current bandwidth up to 320 MHz, and chooses the minimum noise floor among enabled receive chains and active subbands. Invalid bandwidth is logged but treated as one 20 MHz segment rather than dropping the event.

### Central RX Dispatcher

`ath12k_wmi_op_rx()` is the HTC endpoint RX callback. It extracts the WMI event ID from `struct wmi_cmd_hdr`, pulls the header, dispatches through a large switch, and frees the SKB at `out`. `WMI_MGMT_RX_EVENTID` is special: `ath12k_mgmt_rx_event()` takes ownership, so the dispatcher returns immediately without freeing. UTF/testmode events are routed to segmented or unsegmented testmode handlers depending on `ATH12K_FLAG_FTM_SEGMENTED`. Known unsupported frequent events are silently ignored; rare unsupported events log debug messages.

Events handled in this chunk include rfkill, TWT, P2P NoA, diagnostic, WoW wakeup, GTK status, MLO completion, HALPHY TPC stats, RSSI dBm conversion, plus many earlier handlers outside the mapped lines.

### WMI Service and Attach

`ath12k_connect_pdev_htc_service()` connects a pdev-indexed WMI control service (`WMI_CONTROL`, `WMI_CONTROL_MAC1`, or `WMI_CONTROL_MAC2`) to HTC and installs callbacks for TX completion, RX completion, and TX credits. It records endpoint ID and max message length in `ab->wmi_ab`.

`ath12k_wmi_connect()` iterates `ab->htc.wmi_ep_count` after checking it does not exceed `max_radios`. `ath12k_wmi_pdev_attach()` initializes per-pdev WMI handles, `ath12k_wmi_attach()` initializes base WMI state and completions, and `ath12k_wmi_detach()` detaches per-pdev placeholders and frees DBRING capabilities.

### Unit Test and TPC Request Commands

`ath12k_wmi_send_unit_test_cmd()` builds `WMI_UNIT_TEST_CMDID` with a fixed command plus `WMI_TAG_ARRAY_UINT32` arguments. `ath12k_wmi_simulate_radar()` finds a started AP vdev on `ar->arvifs`, fills DFS unit-test arguments, and sends the command to trigger radar simulation.

`ath12k_wmi_send_tpc_stats_request()` builds `WMI_REQUEST_HALPHY_CTRL_PATH_STATS_CMDID` for `WMI_REQ_CTRL_PATH_PDEV_TX_STAT`, includes one target pdev ID, and adds empty vdev and peer arrays. Debugfs readers consume the later multipart event through the TPC stats event path.

### WoW and Offload Commands

`ath12k_wmi_wow_host_wakeup_ind()`, `ath12k_wmi_wow_enable()`, and `ath12k_wmi_wow_add_wakeup_event()` build fixed TLV commands for host wakeup, WoW enable, and add/delete wake event bitmaps. `ath12k_wmi_wow_add_pattern()` builds a compound wake-pattern command containing one bitmap pattern plus empty IPv4 sync, IPv6 sync, magic, timeout, and rate-limit arrays. `ath12k_wmi_wow_del_pattern()` deletes one bitmap pattern.

`ath12k_wmi_op_gen_config_pno_start()` builds an NLO/PNO start command from `struct wmi_pno_scan_req_arg`, including dwell times, scan periods, optional passive scan, optional probe request MAC randomization, SSID entries, RSSI conditions, broadcast-network types, and the channel list. `ath12k_wmi_op_gen_config_pno_stop()` builds a stop command. `ath12k_wmi_wow_config_pno()` chooses start or stop and sends `WMI_NETWORK_LIST_OFFLOAD_CONFIG_CMDID`.

`ath12k_wmi_arp_ns_offload()` builds `WMI_SET_ARP_NS_OFFLOAD_CMDID` from `struct wmi_arp_ns_offload_arg`. `ath12k_wmi_fill_ns_offload()` emits the fixed NS tuple array and, when needed, an extension tuple array for IPv6 addresses beyond `WMI_MAX_NS_OFFLOADS`. `ath12k_wmi_fill_arp_offload()` emits ARP tuple entries up to `WMI_MAX_ARP_OFFLOADS`.

`ath12k_wmi_gtk_rekey_offload()` enables or disables GTK rekey offload by sending KCK, KEK, and replay counter when enabling. `ath12k_wmi_gtk_rekey_getinfo()` requests current offload status before disabling, which pairs with the GTK status event handler.

`ath12k_wmi_sta_keepalive()` builds `WMI_STA_KEEPALIVE_CMDID` with optional ARP response parameters for unsolicited ARP response or gratuitous ARP request methods.

### MLO and 6 GHz TPC Commands

`ath12k_wmi_mlo_setup()` sends `WMI_MLO_SETUP_CMDID` with group ID, local pdev ID, and an array of partner link IDs. `ath12k_wmi_mlo_ready()` sends `WMI_MLO_READY_CMDID`, and `ath12k_wmi_mlo_teardown()` sends `WMI_MLO_TEARDOWN_CMDID` with `WMI_MLO_TEARDOWN_SSR_REASON`.

`ath12k_wmi_supports_6ghz_cc_ext()` gates 6 GHz country-code extension support on both the WMI service bit and `ar->supports_6ghz`.

`ath12k_wmi_send_vdev_set_tpc_power()` sends `WMI_VDEV_SET_TPC_POWER_CMDID` with PSD/EIRP power flags, 6 GHz AP power type, and an array of per-channel center-frequency/TX-power entries. MAC vdev start code fills `arvif->reg_tpc_info` and calls this after vdev setup when TPC is supported.

`ath12k_wmi_send_mlo_link_set_active_cmd()` builds `WMI_MLO_LINK_SET_ACTIVE_CMDID` from `struct wmi_mlo_link_set_active_arg`. It validates that at least vdev bitmaps or link-number entries exist, derives the arrays required by `force_mode`, emits link-number params, active vdev bitmap, optional inactive vdev bitmap, empty IEEE link ID bitmap arrays, and disallowed mode bitmap combinations. `ath12k_wmi_fill_disallowed_bmap()` bounds-checks the disallow array and packs up to four IEEE link IDs into one firmware field.

## Control Flow

Inbound firmware flow enters through HTC into `ath12k_wmi_op_rx()`. The dispatcher removes the WMI header, calls the event-specific parser, and usually frees the SKB. Event parsers commonly allocate a temporary TLV table with `ath12k_wmi_tlv_parse_alloc()` or stream sub-TLVs with `ath12k_wmi_tlv_iter()`, validate required tags, look up `ar` or `arvif` by pdev/vdev under RCU where needed, update protected state, complete waiters, and free parse tables.

Outbound command flow starts from MAC, WoW, debugfs, core, or regulatory code. Helpers compute the exact TLV payload length, allocate an SKB, write fixed params followed by arrays in the firmware-required order, convert host values to little-endian, send via `ath12k_wmi_cmd_send()`, and free the SKB only if sending fails.

Longer asynchronous command flows cross both directions. WoW wakeup sends `WMI_WOW_HOSTWAKEUP_FROM_SLEEP_CMDID` and waits for `WMI_WOW_WAKEUP_HOST_EVENTID`. MLO setup sends `WMI_MLO_SETUP_CMDID` and waits on `ar->mlo_setup_done` completed by the setup-complete event. Debugfs TPC sends a stats request and waits for the multipart HALPHY stats event sequence to complete.

## State and Persistence Behavior

Persistent state updated in this chunk includes:

- `ab->rfkill_radio_on`, protected by `ab->base_lock`, and follow-up `ab->rfkill_work`.
- `ab->wow.wakeup_completed`, completed after WoW wakeup-host parsing.
- `arvif->rekey_data.replay_ctr`, updated from GTK status events and reported to mac80211/supplicant.
- `ar->mlo_setup_status` and `ar->mlo_setup_done`, used by MAC MLO setup waits.
- `ar->debug.tpc_stats`, a multipart debugfs-owned allocation with nested arrays, protected by `ar->data_lock`.
- `ar->rssi_info.temp_offset`, `min_nf_dbm`, and `noise_floor`, updated from RSSI dBm conversion events under `ar->data_lock`.
- `ab->wmi_ab.wmi_endpoint_id[]`, per-pdev WMI endpoint IDs, maximum message lengths, service completions, and preferred hardware mode during WMI attach/connect.

Firmware-visible persistent state is programmed through WoW wake patterns/events, PNO/NLO, ARP/NS offload tuples, GTK offload keys and replay counter, STA keepalive, MLO setup/ready/teardown and link-active forcing, and per-vdev 6 GHz TPC power tables.

## Dependencies and Integration Points

External kernel integrations include HTC transport (`ath12k_htc_connect_service()`), SKB ownership rules, RCU lookups, spinlocks, completions, workqueues, tracepoints, mac80211 GTK rekey notification, and endian/bitfield helpers.

Internal ath12k integration points include:

- MAC/vdev lookup helpers: `ath12k_mac_get_ar_by_vdev_id()`, `ath12k_mac_get_arvif_by_vdev_id()`, and `ath12k_mac_get_ar_by_pdev_id()`.
- WoW core paths in `wow.c`, which call the WoW, PNO, ARP/NS, and GTK offload command builders during suspend/resume setup and cleanup.
- MAC MLO paths, which call MLO setup/teardown and MLO link-active commands and wait for setup completion.
- Regulatory and vdev-start paths, which call 6 GHz TPC support and power programming.
- Debugfs TPC readers, which issue `ath12k_wmi_send_tpc_stats_request()` and consume `ar->debug.tpc_stats`.
- WMI type definitions and constants in `wmi.h`, especially `struct wmi_tpc_stats_arg`, `struct wmi_mlo_link_set_active_arg`, RSSI conversion structs, TLV tags, service bits, and command/event IDs.

## Risks

- TLV length calculations are security- and stability-sensitive. Several command builders copy caller-provided pattern, SSID, channel, offload, and link arrays into fixed firmware payloads; callers must enforce maximum counts and lengths before these helpers run.
- `ath12k_wmi_wow_add_wakeup_event()` uses `(1 << event)`, so event values must remain within the host integer bitmap width.
- The PNO builder uses `pno->a_networks[0].channel_count` for the global channel array. Empty network lists or inconsistent per-network channel counts would produce malformed commands unless validated by the caller.
- `ath12k_wmi_fill_ns_offload()` derives `ns_ext_tuples = ipv6_count - WMI_MAX_NS_OFFLOADS` only on the extension path. Callers must cap `ipv6_count` to the firmware/argument array capacity.
- TPC stats parsing allocates nested arrays across multipart events. Invalid event ordering, duplicate event zero, parse errors, or timeout races can leak or discard stats if `ar->debug.tpc_request` and `ar->debug.tpc_stats` are not coordinated correctly.
- TPC dimension multiplication is done in `u32`; very large firmware-provided dimensions could overflow before comparison with the advertised array length.
- RSSI conversion unpacks firmware noise-floor data into fixed antenna/subband dimensions. The bandwidth-to-segment mapping must stay aligned with `ATH12K_MAX_20MHZ_SEGMENTS`, and chainmask interpretation must match firmware.
- `ath12k_wmi_event_mlo_setup_complete()` compares pdev ID against `ab->num_radios` and then searches by `pdev_id`; pdev ID/index mismatches can cause missed completions and setup timeouts.
- `ath12k_wmi_mlo_setup()` writes `partner_links[i]` without endian conversion, unlike most WMI scalar arrays. This is correct only if the source array is already in firmware endianness; call sites currently pass pdev hardware link IDs as plain host integers.
- `ath12k_wmi_send_mlo_link_set_active_cmd()` supports only a subset of fields present in `struct wmi_mlo_link_set_active_arg`; `use_ieee_link_id`, force command MAC/link bitmaps, and several control flags are not serialized in this implementation.
- WMI RX SKB ownership is exceptional for management RX. Adding new events with ownership transfer must mirror the early-return pattern to avoid double free.

## Test and Validation Signals

Useful validation for this chunk should include:

- Build coverage with `CONFIG_ATH12K_DEBUGFS`, WoW/PM, testmode/FTM, 6 GHz, and MLO-enabled configurations.
- WMI RX smoke tests should show expected dispatch for rfkill, TWT, P2P NoA, WoW wakeup, GTK status, MLO setup completion, HALPHY stats, and RSSI conversion events, with unknown events logged or ignored as intended.
- WoW suspend/resume testing should cover wake event programming, wake pattern add/delete, host wakeup completion, PNO start/stop, ARP/NS offload, GTK rekey offload enable/disable, and GTK rekey notification replay-counter endianness.
- Debugfs TPC tests should request stats, receive all multipart events in order, verify end-of-event completion, validate displayed regulatory/rate/CTL arrays, and exercise timeout/unsolicited-event cleanup.
- RSSI/noise-floor tests should inject or observe conversion events across 20/40/80/160/320 MHz bandwidths and multiple chainmasks, then verify `ath12k_pdev_get_noise_floor()` changes as expected.
- MLO tests should cover setup success, setup timeout/status failure, teardown, active/inactive vdev bitmap modes, link-number force modes, and invalid force-mode or oversized disallowed-bitmap arguments.
- 6 GHz AP/STA vdev start should verify `WMI_VDEV_SET_TPC_POWER_CMDID` contents for PSD and non-PSD power tables and confirm channel/power-type values match regulatory input.
- Fault injection on SKB allocation and `ath12k_wmi_cmd_send()` failures should verify every command helper returns `-ENOMEM` or the send error and frees the SKB only on failure.
- Lockdep/KASAN/KCSAN are useful around RCU vdev/pdev lookups, `ab->base_lock`, `ar->data_lock`, completion lifetimes, debugfs stats memory, and event handling during device teardown or firmware recovery.
