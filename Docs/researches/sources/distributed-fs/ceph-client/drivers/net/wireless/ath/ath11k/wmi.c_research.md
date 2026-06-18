# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wmi.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004738`: lines 1-9185, `Docs/researches/chunks/subset-b-004738_research.md`
- `subset-b-004739`: lines 9186-10050, `Docs/researches/chunks/subset-b-004739_research.md`

## Chunk Research

### subset-b-004738: lines 1-9185

# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wmi.c lines 1-9185

## Scope

This chunk covers the first 9,185 lines of `drivers/net/wireless/ath/ath11k/wmi.c` in the Ceph client distributed-fs source snapshot. It includes the ath11k WMI TLV parser, command send path, most command builders, service-ready capability parsing, regulatory event parsing, firmware event dispatch, stats/event handling, HTC WMI endpoint connection, unit-test radar simulation, and the beginning of firmware debug-log configuration. Later lines beyond this chunk continue with attach/detach, WoW/offload/SAR/keepalive helpers, and final support predicates.

## Purpose

`wmi.c` is the ath11k driver's main Wireless Module Interface bridge between Linux/mac80211 state machines and Qualcomm ath11k firmware. In this chunk it performs two complementary jobs:

- It serializes host requests into firmware WMI TLV sk_buffs and sends them over HTC endpoints.
- It parses firmware WMI TLV events and converts them into driver state changes, completions, regulatory updates, mac80211 callbacks, debugfs stats, testmode signals, and direct-buffer ring notifications.

The file is not a filesystem component directly; in this repository it is part of the distributed-fs kernel source tree and its behavior affects wireless device initialization, scanning, association, regulatory compliance, management frames, power-save accounting, firmware statistics, debug capture, and DFS handling.

## Main Types And Data Structures

- `struct wmi_tlv_policy` and `wmi_tlv_policies[]`: local minimum-length validation for known TLV tags. The iterator uses this table to reject undersized firmware payloads before handler-specific parsing.
- Parse scratch structs:
  - `wmi_tlv_svc_ready_parse` tracks whether the base service bitmap has been consumed.
  - `wmi_tlv_svc_rdy_ext_parse` accumulates service-ready-ext capability state: hardware modes, preferred mode, MAC/PHY caps, HAL regulatory caps, chainmask placeholder arrays, OEM DMA-cap placeholders, and direct-buffer ring caps.
  - `wmi_tlv_svc_rdy_ext2_parse` handles the later EXT2 DMA-ring-cap-only variant.
  - `wmi_tlv_dma_buf_release_parse` collects fixed, buffer-entry, and metadata arrays for direct buffer releases.
  - `wmi_tlv_fw_stats_parse` holds the current stats event, RSSI chain metadata, and output `ath11k_fw_stats`.
  - `wmi_tlv_mgmt_rx_parse` holds fixed management RX metadata plus frame bytes.
- Firmware-facing TLV structs are defined in headers, especially `wmi.h`. This file populates many of them directly: `wmi_vdev_create_cmd`, `wmi_vdev_start_request_cmd`, `wmi_peer_assoc_complete_cmd`, `wmi_start_scan_cmd`, `wmi_resource_config`, `wmi_init_cmd`, event structs for regulatory/scan/mgmt/stats/TWT/P2P/CFR, and others.
- Driver state targets include `struct ath11k_base`, `ath11k_wmi_base`, `ath11k_pdev_wmi`, `ath11k`, `ath11k_pdev`, `ath11k_vif`, `ath11k_sta`, `ath11k_fw_stats`, regulatory `cur_regulatory_info`, and survey/debug/CFR/direct-buffer structs.

## Core Parsing And Send APIs

- `ath11k_wmi_tlv_iter()` is the generic TLV walker. It validates TLV header availability, payload length, and policy minimum length, then calls a supplied callback. This is the foundational safety gate for almost every WMI event parser in the chunk.
- `ath11k_wmi_tlv_parse_alloc()` allocates a tag-indexed table of TLV pointers for simple events. Handlers must `kfree(tb)`.
- `ath11k_wmi_alloc_skb()` allocates an HTC skb with WMI headroom, rounds payload length to 4 bytes, reserves headroom, zeroes payload bytes, and warns on unaligned data.
- `ath11k_wmi_cmd_send_nowait()` prepends `struct wmi_cmd_hdr`, traces the command, clears the skb control block, and calls `ath11k_htc_send()`.
- `ath11k_wmi_cmd_send()` wraps the send path with wait queues. With firmware credit-flow enabled it retries while `ath11k_htc_send()` returns `-EAGAIN`; otherwise it waits for CE descriptors and retries on `-ENOBUFS`. Crash flushing maps pending failures to `-ESHUTDOWN`.

The command-builder pattern is repeated throughout the file: compute TLV length, allocate WMI skb, write fixed command TLV header, fill fields from caller parameters, append optional array TLVs, send by command ID, and free the skb only on send failure.

## Initialization And Capability Discovery

The WMI startup sequence in this chunk is event-driven:

1. Firmware emits service-ready events.
2. `ath11k_service_ready_event()` parses base target capabilities into `ab->target_caps` and copies the base service bitmap into `ab->wmi_ab.svc_map`.
3. `ath11k_service_available_event()` may extend `svc_map` with service segment bitmaps.
4. `ath11k_service_ready_ext_event()` parses hardware modes, preferred hardware mode, MAC/PHY capabilities, HAL regulatory capabilities, direct-buffer ring capabilities, and radio/pdev capability data. It completes `service_ready` immediately unless firmware advertises the EXT2 message.
5. `ath11k_service_ready_ext2_event()` parses additional DMA ring capabilities and completes `service_ready`.
6. `ath11k_wmi_cmd_init()` asks hardware ops for resource config, stores it in `wmi_ab->wlan_resource_config`, maps bands to MACs, and sends `WMI_INIT_CMDID`.
7. `ath11k_ready_event()` parses firmware MAC address/pktlog checksum/extra pdev MAC addresses and completes `unified_ready`.

Important initialization helpers:

- `ath11k_pull_service_ready_tlv()` copies base target capability values such as PHY capability, RF chains, HT/VHT caps, power limits, max scan channels, supported MAC count, firmware subfeatures, chainmask, DBS mode index, and MSDU descriptors.
- `ath11k_pull_svc_ready_ext()` copies extended scan/firmware config bits, HE cap info, MPDU density, BSSID RX filter limit, and PPET data.
- `ath11k_wmi_tlv_hw_mode_caps()` chooses `ab->wmi_ab.preferred_hw_mode` using `ath11k_hw_mode_pri_map`.
- `ath11k_pull_mac_phy_cap_svc_ready_ext()` fills pdev/radio capabilities, supported bands, chain masks, HT/VHT/HE caps, NSS ratio, 2/5/6 GHz band caps, and target pdev IDs.
- `ath11k_pull_reg_cap_svc_rdy_ext()` fills `ab->hal_reg_cap[phy_id]`.
- `ath11k_wmi_tlv_dma_ring_caps()` allocates `ab->db_caps`, validates module IDs, and records pdev/module/min buffer constraints for direct-buffer integrations.
- `ath11k_wmi_copy_resource_config()` maps `target_resource_config` to WMI resource config, including vdev/peer counts, scan/roam/offload limits, TWT counts, service flags, EMA limits, and `WMI_RSRC_CFG_FLAG2_CALC_NEXT_DTIM_COUNT_SET`.
- `ath11k_init_cmd_send()` serializes resource config, host memory chunks, optional hardware mode, and band-to-MAC ranges into `WMI_INIT_CMDID`.

Persistent initialization state written by this chunk includes `svc_map`, `target_caps`, `num_radios`, `pdevs[].cap`, `pdevs[].pdev_id`, `target_pdev_ids`, `target_pdev_count`, `hal_reg_cap`, `reg_info_store`, `db_caps`, `num_db_cap`, `mac_addr`, `pktlog_defs_checksum`, `pdevs[].mac_addr`, and `pdevs_macaddr_valid`.

## Command Coverage

This chunk contains WMI command senders for most online driver operations:

- Management TX: `ath11k_wmi_mgmt_send()` sends a DMA-backed management frame, optionally with CFR capture params. `ath11k_wmi_mgmt_get_freq()` selects off-channel ROC frequency when supported.
- VDEV lifecycle: create/delete/start/restart/up/stop/down and generic set-param. `ath11k_wmi_put_wmi_channel()` maps channel mode, center frequencies, DFS/passive/HT/VHT/HE flags, and regulatory power fields into `wmi_channel`.
- Peer lifecycle and association: peer create/delete, peer set-param, peer flush TIDs, reorder queue setup/remove, peer association complete, addba/delba helpers, AP/STA power-save parameters.
- PDEV operations: set regdomain, set param, suspend/resume, BSS channel info request, DFS phyerr offload enable, pktlog enable/disable, peer pktlog filter, LRO config, spectral configure/enable, DMA ring config, hardware mode, firmware hang trigger, temperature request.
- Scanning and regulatory setup: default scan init, start scan, stop scan, scan channel-list upload with chunking by WMI max message length, initial/current country commands, 11d scan start/stop, vdev TPC power.
- Beacon/probe/FILS/P2P templates: beacon offload control, P2P GO beacon IE, beacon template, probe response template, FILS discovery template and interval command.
- Crypto/security: vdev install key and status completion.
- 802.11ax features: TWT enable/disable/add/delete/pause/resume, OBSS spatial reuse config and SRG/non-SRG bitmaps, OBSS color collision config and BSS color change enable.
- Diagnostics/test hooks: unit-test command, radar simulation, firmware debug-log config start.
- CFR: peer CFR capture configuration and CFR event parsing.

Most command APIs return `0`, `-ENOMEM`, `-EINVAL`, `-EOPNOTSUPP`, `-ESHUTDOWN`, or the transport return code. On send failure they generally warn and free the skb. Callers remain responsible for sequencing against completions such as vdev setup, key install, peer association, and stats completion.

## Event Dispatch And Control Flow

`ath11k_connect_pdev_htc_service()` connects each WMI HTC service endpoint and registers:

- `ep_tx_complete = ath11k_wmi_htc_tx_complete`
- `ep_rx_complete = ath11k_wmi_tlv_op_rx`
- `ep_tx_credits = ath11k_wmi_op_ep_tx_credits`

`ath11k_wmi_tlv_op_rx()` is the central firmware event dispatcher. It reads the WMI command header, traces the event, pulls the header, and switches on `WMI_*_EVENTID`. It frees the skb at the end except for `WMI_MGMT_RX_EVENTID`, where `ath11k_mgmt_rx_event()` takes ownership and passes or frees it.

Major dispatch targets in this chunk:

- Startup: service ready, service ready ext/ext2, ready, service available.
- Regulatory: standard and extended channel-list events, 11d new country event.
- VDEV/peer completions: peer delete, vdev delete, vdev start, vdev stopped, peer assoc, install key.
- Scan/survey: scan events, channel info, pdev BSS channel info.
- Management frame path: mgmt RX and mgmt TX completion.
- Station behavior: peer STA kickout, roam, peer PS state change.
- Stats/debug/diagnostics: update stats, ctl failsafe, diag, UTF/testmode.
- PHY/environment: DFS radar detected, pdev temperature, direct-buffer release.
- AP offload features: beacon TX status, CSA switch count, FILS discovery, probe response TX status, OBSS color collision, TWT add-dialog status, GTK offload status, P2P NoA, CFR capture.

## Regulatory Behavior

The chunk has two full regulatory parsers:

- `ath11k_pull_reg_chan_list_update_ev()` handles legacy 2.4/5 GHz channel-list events. It extracts alpha2, DFS region, phy/domain metadata, bandwidth bounds, and allocates 2 GHz and 5 GHz `cur_reg_rule` arrays.
- `ath11k_pull_reg_chan_list_ext_update_ev()` handles extended events with 6 GHz AP/client rule families. It validates rule counts against `MAX_REG_RULES` and `MAX_6GHZ_REG_RULES`, extracts 2/5/6 GHz bandwidth ranges, subdomain codes, client/AP usability flags, PSD data, and filters accidental 6 GHz rules from the 5 GHz rule array.

`ath11k_reg_chan_list_event()` allocates a `cur_regulatory_info`, calls the relevant parser, hands it to `ath11k_reg_handle_chan_list()`, then either frees just the shell on success or resets allocated rule arrays via `ath11k_reg_reset_info()` on failure. `ath11k_reg_11d_new_cc_event()` updates `ab->new_alpha2`, resets each radio's 11d state to idle, completes `completed_11d_scan`, and queues `update_11d_work`.

Risk-relevant detail: the standard parser logs `status_code` before assigning the converted firmware status, so that debug line can report stale zeroed status rather than the event status.

## Scan, Survey, And Channel State

`ath11k_wmi_start_scan_init()` provides default scan parameters and scan event subscriptions. Scan priority is raised to medium while 11d is preparing; otherwise it is low. Passive-scan enhancement is enabled when the service bit is present.

`ath11k_wmi_send_scan_start_cmd()` builds a compound TLV with channel array, SSID array, BSSID array, optional extra IEs, optional short-SSID hints, and optional BSSID hints. `ath11k_wmi_send_scan_stop_cmd()` maps driver cancel types to WMI stop request types. `ath11k_wmi_send_scan_chan_list_cmd()` sends channel-list chunks that fit the per-pdev WMI maximum message length and appends to existing firmware channel lists after the first chunk.

Firmware scan events drive `ar->scan.state` under `ar->data_lock`:

- `STARTED`: transitions `STARTING` to `RUNNING`, completes `scan.started`, and signals remain-on-channel readiness when applicable.
- `START_FAILED`: completes `scan.started` and calls `__ath11k_mac_scan_finish()`.
- `COMPLETED`: finishes scans from `RUNNING` or `ABORTING`; warns and ignores completion from `IDLE` or `STARTING`.
- `BSS_CHANNEL`: clears `ar->scan_channel`.
- `FOREIGN_CHAN`: records current scan channel and completes `scan.on_channel` for ROC frequency matches.
- `DEQUEUED`: finishes the scan.

`ath11k_chan_info_event()` updates per-channel survey noise/time/busy data during scans. `ath11k_pdev_bss_chan_info_event()` updates BSS survey data using 64-bit counter pairs and completes `ar->bss_survey_done`.

## Management Frame And Association Behavior

RX path:

- `ath11k_pull_mgmt_rx_params_tlv()` parses WMI RX header and frame bytes, checks `skb->len` against `buf_len`, reshapes the skb to the frame payload, and byte-swaps payload data.
- `ath11k_mgmt_rx_event()` maps pdev to `ath11k`, drops frames during CAC or with decrypt/key/CRC errors, sets MIC error flags, determines 2/5/6 GHz band, calculates signal and rate index, marks WMI-delivered frames with `RX_FLAG_SKIP_MONITOR`, handles PMF protected-bit behavior, feeds beacons to `ath11k_mac_handle_beacon()`, and calls `ieee80211_rx_ni()`.

TX completion path:

- `wmi_process_mgmt_tx_comp()` removes the pending skb from `ar->txmgmt_idr`, DMA-unmaps it, fills mac80211 TX status including ACK and optional ACK RSSI, calls `ieee80211_tx_status_irqsafe()`, decrements `num_pending_mgmt_tx`, and wakes `txmgmt_empty_waitq` when empty.
- `ath11k_mgmt_tx_compl_event()` parses WMI completion and locates the radio by pdev ID.

Association and peer state:

- `ath11k_wmi_copy_peer_flags()` derives WMI peer flags from QoS/HT/VHT/HE/TWT/STBC/LDPC/MIMO/auth/PTK/GTK/PMF settings. It suppresses authorization during 4-way handshake unless hardware crypto is disabled and clears HT if HT rate count is zero.
- `ath11k_wmi_send_peer_assoc_cmd()` serializes legacy rates, HT rates, VHT MCS, HE MCS sets, HE capability arrays, PPET, peer flags, NSS, bandwidth/NSS override, and min data rate.
- Peer/vdev completion events complete `peer_delete_done`, `vdev_delete_done`, `vdev_setup_done`, `install_key_done`, and `peer_assoc_done`.

## Stats And Debug Output

Firmware stats parsing is split by TLV type:

- `ath11k_wmi_pull_fw_stats()` drives `ath11k_wmi_tlv_fw_stats_parse()`.
- `ath11k_wmi_tlv_fw_stats_data_parse()` walks pdev, vdev, and beacon stats from a byte array based on counts in `wmi_stats_event`, allocates driver-side list nodes, and updates STA RSSI beacon SNR when matching vdev/station state exists.
- `ath11k_wmi_tlv_rssi_chain_parse()` updates per-chain signal values in `ath11k_sta`.
- `ath11k_update_stats_event()` splices stats into `ar->fw_stats`, handles completion semantics for pdev/vdev/RSSI stats, and delegates beacon/debugfs-only stats to `ath11k_debugfs_fw_stats_process()`.
- `ath11k_wmi_fw_stats_fill()` formats pdev/vdev/beacon stats into debug buffers under `ar->data_lock`.

Diagnostics also include `ath11k_wmi_diag_event()` trace emission, `ath11k_pdev_ctl_failsafe_check_event()` warnings for BDF CTL misses, temperature forwarding to `ath11k_thermal_event_temperature()`, and the beginning of `ath11k_wmi_fw_dbglog_cfg()`.

## Feature-Specific Event Behavior

- Beacon TX status queues `arvif->bcn_tx_work`.
- OBSS color collision notifies mac80211 via `ieee80211_obss_color_collision_notify()`.
- CSA switch count status calls `ieee80211_csa_finish()` for active CSA vifs when switch count reaches zero.
- DFS radar detected maps pdev to radio and calls `ieee80211_radar_detected()` unless `ar->dfs_block_radar_events` is set.
- TWT add-dialog events log nonzero firmware statuses.
- GTK offload status updates `arvif->rekey_data.replay_ctr` and calls `ieee80211_gtk_rekey_notify()` with big-endian replay counter.
- P2P NoA events validate descriptor count and call `ath11k_p2p_noa_update_by_vdev_id()`.
- CFR capture events parse fixed and phase params and call `ath11k_process_cfr_capture_event()`.
- Direct-buffer release events parse fixed, entry, and metadata arrays and call `ath11k_dbring_buffer_release_event()`.
- WoW wakeup host events parse wake reason and optional page-fault data, then complete `ab->wow.wakeup_completed`.

## State And Persistence Behavior

State is held in memory only; this chunk does not persist data to disk. Significant mutable state includes:

- Global/base state: WMI service bitmap, completions, target caps, radio count, pdev IDs/MACs, regulatory info storage, direct-buffer ring caps, new 11d alpha2, pktlog checksum, preferred hardware mode, resource config, and wakeup completion.
- Per-radio state: scan state/channel/completions, started vdev count, firmware stats lists and counters, max allowed TX power, last vdev-start status, install key status, TWT enabled flag, management TX IDR/pending counter, survey data, BSS survey completion, peer/vdev completions, 11d state, and DFS-block flag.
- Per-vif/station state: beacon TX work, replay counter for GTK offload, P2P NoA data, STA chain signal, beacon RSSI, power-save state, PS duration accounting, and current PS validity.

Concurrency is handled with a mix of completions, wait queues, RCU, spinlocks, atomics, and workqueues:

- `ab->wmi_ab.service_ready` and `unified_ready` gate initialization progress.
- `ar->data_lock` protects scan, survey, stats, and several station/vdev state updates.
- `ab->base_lock` protects peer table lookups and base alpha2 update.
- RCU protects active pdev/vdev/sta lookups.
- `ar->txmgmt_idr_lock` protects management TX IDR.
- Workqueue integration is used for 11d country updates and beacon TX work.

## Dependencies And Integration Points

Internal ath11k dependencies:

- `core.h`, `debug.h`, `mac.h`, `hw.h`, `peer.h`, `testmode.h`, and `p2p.h`.
- HTC transport: `ath11k_htc_alloc_skb()`, `ath11k_htc_send()`, `ath11k_htc_connect_service()`.
- HAL/DP conventions: `DP_HW2SW_MACID()`, `ath11k_ce_byte_swap()`, direct-buffer ring release.
- MAC helpers: `ath11k_mac_get_ar_by_pdev_id()`, `ath11k_mac_get_ar_by_vdev_id()`, `ath11k_mac_get_arvif()`, scan finish, beacon handling, beacon miss handling, bitrate mapping.
- Regulatory helpers: `ath11k_reg_handle_chan_list()`, `ath11k_reg_reset_info()`, country/status string conversion helpers.
- Debug/test hooks: tracepoints, debugfs stats processing, testmode WMI event, CFR processing.

Linux/mac80211/cfg80211 dependencies:

- sk_buff allocation/manipulation and skb control blocks.
- mac80211 callbacks such as `ieee80211_rx_ni()`, `ieee80211_tx_status_irqsafe()`, `ieee80211_ready_on_channel()`, `ieee80211_report_low_ack()`, `ieee80211_radar_detected()`, `ieee80211_csa_finish()`, `ieee80211_obss_color_collision_notify()`, and `ieee80211_gtk_rekey_notify()`.
- cfg80211/nl80211 band/channel definitions, survey info flags, and regulatory concepts.
- Kernel primitives: completions, wait queues, spinlocks, RCU, workqueues, IDR, DMA unmap, atomics, random bytes, list operations, and tracepoints.

## Risks And Edge Cases

- TLV ordering dependence: several parsers distinguish repeated `WMI_TAG_ARRAY_STRUCT` instances by "first array, second array, ..." booleans. Firmware schema changes or reordered TLVs can route data to the wrong parser.
- Pointer lifetime: many event pull helpers store pointers into skb/TLV memory. Consumers must not retain them beyond event handling. Peer kickout and peer assoc conf expose MAC pointer values from temporary TLV storage.
- Allocation cleanup: extended regulatory parsing allocates many rule arrays; all error paths must reset/free correctly. Some 6 GHz arrays are allocated even for zero rule count depending on `kzalloc_objs()` semantics, which should be checked when changing allocation helpers.
- Length arithmetic: command builders manually compute TLV sizes. Mismatches between length fields and actual writes would corrupt WMI payloads. Scan start and init commands are especially large and conditional.
- Potential copy direction bug: in scan start hint BSSID handling, `ether_addr_copy(&params->hint_bssid[i].bssid.addr[0], &hint_bssid->bssid.addr[0])` appears to copy from the just-allocated WMI buffer into caller params rather than from params into the WMI buffer.
- Firmware event count trust: stats and regulatory parsers depend on firmware-provided counts but include many bounds checks. Any new stats/regulatory arrays should preserve explicit remaining-length checks before advancing pointers.
- Locking and RCU assumptions: event handlers often find `ar`, `arvif`, `sta`, or `peer` under RCU and then update nested state under spinlocks. New code must preserve the same lock order and avoid sleeping in atomic/GFP_ATOMIC event context.
- Management RX skb ownership is special: `ath11k_mgmt_rx_event()` consumes the skb and the dispatcher returns immediately. Adding code after that case risks use-after-free/double-free if ownership is misunderstood.
- Credit wait semantics differ between credit-flow and CE descriptor modes. New command paths should return transport errors and free only on failed send, consistent with existing helpers.
- Debug formatting uses fixed `ATH11K_FW_STATS_BUF_SIZE`; newly added stat text should respect the tracked length and final NUL behavior.
- Channel index mapping `freq_to_idx()` returns the cumulative index where it stops, even if no channel matched; callers only bounds-check against `ARRAY_SIZE(ar->survey)`, so unknown frequencies inside the array-size range could map to a misleading survey slot.

## Test Signals

Useful validation signals for this chunk:

- Probe/init: driver reaches `ath11k_wmi_wait_for_service_ready()` and `ath11k_wmi_wait_for_unified_ready()` without timeout; logs show service-ready, service-ready-ext/ext2, and ready events.
- WMI transport: no recurring `wmi command timeout`, `ce desc not available`, TLV parse failures, unsupported event floods, or crash-flush send failures.
- Radio capability: expected number of radios, pdev IDs, supported bands, chain masks, 6 GHz capability, and regulatory caps appear in debug output and cfg80211 wiphy state.
- Scan: scan start/completion events transition through valid states; remain-on-channel completes; survey data populates; no warnings about scan events in invalid states during normal scans.
- Association: peer create/assoc/key install completions arrive; management TX completions drain `num_pending_mgmt_tx`; mgmt RX frames reach mac80211 with correct band/frequency/signal.
- Regulatory: country change and 11d events update alpha2 and channel lists; extended 6 GHz rules do not duplicate 6 GHz entries in the 5 GHz list.
- DFS: radar simulation through `ath11k_wmi_simulate_radar()` requires a started AP vdev and should result in DFS radar handling unless blocked.
- Stats/debugfs: firmware pdev/vdev/beacon stats requests complete and render sane output; RSSI per-chain stats update station chain signal.
- Power/offload features: TWT enable toggles `ar->twt_enabled`; OBSS color collision reaches mac80211; GTK offload status updates replay counter; P2P NoA updates P2P state; direct-buffer release reaches the dbring handler.

## Chunk Boundary Notes

The chunk ends in the middle of the broader WMI implementation, just after `ath11k_wmi_simulate_radar()` and at the beginning of `ath11k_wmi_fw_dbglog_cfg()`. Functions after line 9,185 continue the debug-log command and include attach/detach and wake/offload/SAR/keepalive routines. Those are outside this chunk and should be merged later with adjacent chunk research for a complete per-file report.

### subset-b-004739: lines 9186-10050

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wmi.c lines 9186-10050

## Scope And Purpose

This chunk is a late section of the ath11k WMI command encoder. It covers the tail of firmware debug-log configuration, WMI endpoint attach/detach helpers, hardware data filtering, WoWLAN command construction, preferred network offload (PNO/NLO) configuration, ARP/IPv6 neighbor-solicitation offload, GTK rekey offload, BIOS SAR/GEO table commands, station keepalive, and a small helper that gates 6 GHz country-code extension handling.

The code is almost entirely host-to-firmware command serialization. Each public helper allocates an `sk_buff` with `ath11k_wmi_alloc_skb()`, writes one or more WMI TLV records with `FIELD_PREP(WMI_TLV_TAG, ...)` and `FIELD_PREP(WMI_TLV_LEN, ...)`, fills command-specific fields from `struct ath11k`, `struct ath11k_vif`, cfg80211/mac80211-derived arguments, or debugfs input, and sends the buffer with `ath11k_wmi_cmd_send()`. The functions do not process received packets and do not persist configuration to disk; they transfer current driver state into firmware-owned suspend, offload, regulatory, and diagnostic state.

## Important APIs, Types, And Constants

- `ath11k_wmi_fw_dbglog_cfg()` finishes in this range. It sends `WMI_DBGLOG_CFG_CMDID` for debugfs-selected firmware logging parameters and optionally copies `MAX_MODULE_ID_BITMAP_WORDS` from `ar->debug.module_id_bitmap`.
- `ath11k_wmi_connect()`, `ath11k_wmi_pdev_attach()`, `ath11k_wmi_attach()`, and `ath11k_wmi_detach()` wire `struct ath11k_base::wmi_ab` and per-PDEV `struct ath11k_pdev_wmi` handles to HTC WMI services and completions.
- WoWLAN helpers include `ath11k_wmi_hw_data_filter_cmd()`, `ath11k_wmi_wow_host_wakeup_ind()`, `ath11k_wmi_wow_enable()`, `ath11k_wmi_scan_prob_req_oui()`, `ath11k_wmi_wow_add_wakeup_event()`, `ath11k_wmi_wow_add_pattern()`, and `ath11k_wmi_wow_del_pattern()`.
- PNO/NLO command generation uses `struct wmi_pno_scan_req`, `struct wmi_network_type`, `struct wmi_wow_nlo_config_cmd`, and `struct nlo_configured_parameters`. The public entry point is `ath11k_wmi_wow_config_pno()`, which selects start or stop command generation and sends `WMI_NETWORK_LIST_OFFLOAD_CONFIG_CMDID`.
- Protocol offload uses `struct ath11k_arp_ns_offload` stored in `struct ath11k_vif`, plus firmware tuple types `struct wmi_ns_offload_tuple`, `struct wmi_arp_offload_tuple`, and `struct wmi_set_arp_ns_offload_cmd`. Host-side maximums are `ATH11K_IPV6_MAX_COUNT` and `ATH11K_IPV4_MAX_COUNT`; the base WMI command has `WMI_MAX_NS_OFFLOADS` and `WMI_MAX_ARP_OFFLOADS` slots, with an extension array for additional IPv6 NS entries.
- GTK offload uses `struct ath11k_rekey_data` from `arvif->rekey_data`, `struct wmi_gtk_rekey_offload_cmd`, and opcodes `GTK_OFFLOAD_ENABLE_OPCODE`, `GTK_OFFLOAD_DISABLE_OPCODE`, and `GTK_OFFLOAD_REQUEST_STATUS_OPCODE`.
- BIOS power-limit commands use `struct wmi_pdev_set_sar_table_cmd`, `struct wmi_pdev_set_geo_table_cmd`, `BIOS_SAR_TABLE_LEN`, `BIOS_SAR_RSVD1_LEN`, and `BIOS_SAR_RSVD2_LEN`.
- Keepalive uses `struct wmi_sta_keepalive_arg`, `struct wmi_sta_keepalive_cmd`, `struct wmi_sta_keepalive_arp_resp`, and `enum wmi_sta_keepalive_method`.
- `ath11k_wmi_supports_6ghz_cc_ext()` checks `WMI_TLV_SERVICE_REG_CC_EXT_EVENT_SUPPORT` in `ar->ab->wmi_ab.svc_map` and `ar->supports_6ghz`.

## Control Flow

The debug-log tail writes the fixed TLV array header for module bitmaps, switches on `dbglog->param`, and either sets only `cmd->value` or copies the caller-provided module bitmap into the TLV payload. For module-bitmap parameters it clears the input bitmap after copying so debugfs can accumulate multi-write bitmap state only until the final `is_end` write. Unsupported parameters free the newly allocated skb and return `-EINVAL`. Send failures are logged and also free the skb.

The WMI attach path is deliberately small. `ath11k_wmi_connect()` reads `ab->htc.wmi_ep_count`, rejects endpoint counts above `ab->hw_params.max_radios`, and connects each PDEV service with `ath11k_connect_pdev_htc_service()`. `ath11k_wmi_pdev_attach()` bounds-checks the PDEV ID, stores `&ab->wmi_ab` into the per-PDEV WMI handle, and refreshes `ab->wmi_ab.ab`. `ath11k_wmi_attach()` initializes PDEV 0, sets `preferred_hw_mode` to `WMI_HOST_HW_MODE_MAX` or single-PDEV mode for single-PDEV multi-RXDMA hardware, and initializes the `service_ready` and `unified_ready` completions. `ath11k_wmi_detach()` iterates all HTC WMI endpoints, calls the currently placeholder PDEV detach helper, and releases DBR ring capabilities through `ath11k_wmi_free_dbring_caps()`.

The WoWLAN control helpers follow a common one-command pattern. Hardware data filtering fills `WMI_TAG_HW_DATA_FILTER_CMD` and uses the caller bitmap when enabling; when disabling it sends all bits set so firmware clears all filter modes. Host wakeup and global WoW enable send fixed commands. Probe-request OUI extracts the first three bytes from a MAC address into a 24-bit OUI. Wakeup-event enable/disable encodes `1 << event` into the firmware event bitmap.

Pattern add is more complex because firmware expects several TLV arrays after `WMI_TAG_WOW_ADD_PATTERN_CMD`. The function allocates space for one bitmap pattern, empty IPv4 sync, empty IPv6 sync, empty magic-pattern, empty timeout array, and a one-word rate-limit interval array. It copies the pattern and mask into `struct wmi_wow_bitmap_pattern`, byte-swaps both rounded to a 4-byte boundary, then appends the required empty placeholders before sending `WMI_WOW_ADD_WAKE_PATTERN_CMDID`. Pattern delete sends only the fixed delete command with `WOW_BITMAP_PATTERN`.

PNO start builds `WMI_TAG_NLO_CONFIG_CMD` followed by an array of `nlo_configured_parameters` and an array of channel frequencies. It sets start and hidden-SSID flags, maps active/passive dwell to the max dwell values because the firmware path does not support min/max ranges, optionally enables passive scanning, and copies fast/slow scan periods, fast cycles, delay, and randomized probe-request MAC/mask. It then serializes each match SSID, optional RSSI threshold, and broadcast network type. Channel serialization uses `pno->a_networks[0].channel_count` and `pno->a_networks[0].channels[]` for the single firmware channel list. PNO stop emits only a fixed `WMI_NLO_CONFIG_STOP` command. The public wrapper returns `-ENOMEM` for NULL/error skb generation and otherwise sends the chosen command.

ARP/NS offload first calculates a command length containing the fixed command, a base NS tuple array of `WMI_MAX_NS_OFFLOADS`, an ARP tuple array of `WMI_MAX_ARP_OFFLOADS`, and, when needed, an extension NS tuple array for IPv6 addresses beyond the base firmware slots. `ath11k_wmi_fill_ns_offload()` emits either the base or extension array. When enabled, it marks entries below `offload->ipv6_count` valid, copies target IPv6 and solicited-node multicast IPv6 addresses, flags anycast addresses, copies the target MAC, and marks the MAC valid when nonzero. `ath11k_wmi_fill_arp_offload()` emits two ARP tuple slots and marks entries below `offload->ipv4_count` valid when enabled. Disable commands still send tuple TLVs but leave validity flags clear.

GTK rekey offload sends the same WMI command for enable, disable, and status request. Enable copies KCK, KEK, and a little-endian replay counter from `arvif->rekey_data`, then applies `ath11k_ce_byte_swap()` to the byte arrays before sending. Disable only sets the disable opcode. Status request sets the request-status opcode and is used before disabling so the resume path can retrieve updated replay counters from firmware events.

The BIOS SAR and GEO functions encode per-PDEV power-limit table commands. SAR allocates fixed command space plus two byte arrays: the 22-byte SAR table rounded to a 32-bit boundary and a 6-byte reserved array rounded to a 32-bit boundary. It copies only the SAR bytes from the caller and leaves the reserved array payload untouched apart from allocator initialization. GEO sends the fixed command plus an 18-byte reserved byte array rounded to 32-bit alignment. Both commands use `ar->pdev->pdev_id`.

Station keepalive allocates a fixed keepalive command followed immediately by an ARP-response TLV. It fills vdev, enable flag, interval, and method for all methods, and fills IPv4 source/destination plus destination MAC only for unsolicited ARP response or gratuitous ARP request methods. `ath11k_wmi_supports_6ghz_cc_ext()` has no send path; it is a pure predicate used by mac80211/regulatory code to decide whether 6 GHz country-code extension behavior is available.

## State And Persistence Behavior

The main persistent host state touched in this chunk is in `struct ath11k_base::wmi_ab`, per-PDEV WMI handles, `struct ath11k_vif`, and debugfs state. Attach initializes `wmi_ab.ab`, per-PDEV `wmi_handle->wmi_ab`, `preferred_hw_mode`, and WMI readiness completions. Detach releases DBR ring capability storage but leaves most PDEV/SOC WMI cleanup as TODO placeholders.

Firmware debug-log configuration consumes `ar->debug.module_id_bitmap` by copying it into the command and clearing it for bitmap-style parameters. This is observable by debugfs users because multiple debugfs writes can populate bitmap words before the final send, but the buffer is reset after the WMI command is generated.

WoWLAN, PNO, ARP/NS offload, GTK offload, hardware filters, and keepalive all persist primarily inside firmware after `ath11k_wmi_cmd_send()` succeeds. Host-side source state remains in existing structures: `arvif->arp_ns_offload` is populated by mac80211 IPv6 address callbacks, `arvif->rekey_data` is populated by key/offload setup, and PNO requests are built transiently from cfg80211 scheduled-scan/WoWLAN requests in `wow.c`. The WMI helpers themselves do not cache success state, so callers track higher-level state such as `ar->nlo_enabled` and `arvif->rekey_data.enable_offload`.

The skb payloads are temporary command buffers. On success, ownership transfers to `ath11k_wmi_cmd_send()`; on explicit pre-send validation failures or send failures where this function sees an error, the local helper frees the skb only in paths that are written to do so. Most one-line wrappers return the send result directly and rely on the common WMI send path's ownership behavior.

## Dependencies And Integration Points

This code depends on the ath11k WMI TLV ABI defined in `wmi.h`: tags, command IDs, fixed command structs, tuple structs, and service bits must match firmware expectations exactly. It also depends on the common command allocator/sender, CE byte-swapping helper, Linux skb allocation semantics, and bitfield helpers.

The debug-log helper is called from `debugfs.c` under `ar->conf_mutex` after parsing user input from the firmware debug-log debugfs file. The bitmap clearing behavior is paired with that parser's `is_end` protocol.

The WoWLAN helpers are called from `wow.c` during suspend/resume preparation. `ath11k_vif_wow_set_wakeups()` uses wakeup-event and pattern helpers, configures NLO through `ath11k_wmi_wow_config_pno()`, and sets hardware filters through `ath11k_wmi_hw_data_filter_cmd()`. Resume cleanup disables NLO, clears hardware filters, may request GTK rekey status, disables GTK offload, and notifies firmware that the host is awake.

ARP/NS offload input is populated by mac80211 operations in `mac.c`, notably IPv6 address change handling for solicited-node multicast addresses and ARP/IPv4 state tracking. `wow.c` applies the offload only to STA vdevs during protocol-offload setup.

GTK offload is part of the WoWLAN suspend/resume path. Firmware status events are handled elsewhere in WMI event parsing, but this chunk provides the commands that enable, disable, and request state.

Station keepalive is called from `ath11k_mac_vif_set_keepalive()` for STA vdevs only when firmware advertises `WMI_TLV_SERVICE_STA_KEEP_ALIVE`. That mac80211-side wrapper supplies null-frame keepalive by default, while this WMI helper also supports ARP-style payload fields for methods that need them.

The 6 GHz predicate is used from several mac80211/regulatory paths: station TPC support checks, interface-add regulatory rule handling, and STA authorization/regulatory power-type handling. It combines firmware service discovery with per-radio 6 GHz support so callers do not enable country-code extension behavior on non-6 GHz radios or firmware lacking the event service.

The source path is under `sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/`, a copied Linux wireless driver subtree inside this repository. There is no direct Ceph filesystem logic in this chunk; its integration surface is Linux wireless firmware control.

## Risks And Edge Cases

The most important local risk is TLV size and pointer arithmetic drift. Pattern add, PNO start, and ARP/NS offload manually compute lengths and then advance raw pointers through packed firmware records. Any future change to the serialized structures, tuple counts, or placeholder arrays must update both the length expression and write sequence together, or the command can be truncated, overrun, or rejected by firmware.

Caller-side validation is assumed for several inputs. `ath11k_wmi_wow_add_pattern()` copies `pattern_len` bytes into fixed firmware buffers and byte-swaps `roundup(pattern_len, 4)` bytes; `wow.c` bounds-checks patterns against `WOW_MAX_PATTERN_SIZE` before calling, so direct new callers would need equivalent validation. PNO start trusts `uc_networks_count`, SSID lengths, and channel counts; current conversion in `wow.c` bounds these against WMI maximums. ARP/NS offload trusts `offload->ipv6_count` and `offload->ipv4_count`; host structures have fixed array sizes, so producers must cap counts.

The PNO channel-list model uses only `a_networks[0].channel_count` and `a_networks[0].channels[]` even though each network entry has its own channel array. This matches the conversion helper, which copies the same cfg80211 channel list into every network, but it is a coupling worth preserving if PNO conversion changes.

There are several byte-order and byte-swap subtleties. PNO randomized MAC/mask, SSID bytes, WoW patterns/masks, NS IPv6 addresses, target MACs, ARP IPv4 addresses, GTK keys, and replay counters are run through `ath11k_ce_byte_swap()` because firmware/CE expects 32-bit word-swapped payloads. Incorrectly adding or removing byte swaps can produce failures that look like firmware ignoring otherwise well-formed commands.

`ath11k_wmi_wow_add_wakeup_event()` uses `1 << event`; this assumes the enum value is within the width of the integer bitmap. Current callers iterate `WOW_EVENT_MAX`, but new events above bit 31 would require a wider bitmap or different command layout.

The debug-log module bitmap is cleared immediately after command serialization, before command success is known. If `ath11k_wmi_cmd_send()` fails, the accumulated bitmap is lost and must be supplied again through debugfs.

`ath11k_wmi_connect()` returns `-1` rather than a conventional errno for too many WMI endpoints. Callers that expect Linux errno values may log or handle this less clearly than `-EINVAL`.

The attach/detach helpers still contain TODOs for PDEV- and SOC-specific resource initialization/cleanup. At present that is safe only because this chunk initializes very little per-PDEV WMI state. Any future allocation added to attach must have a matching detach/unwind path.

The SAR/GEO reserved byte-array payloads are not explicitly filled. This is probably acceptable if `ath11k_wmi_alloc_skb()` zeroes command buffers, but it is an implicit dependency. A different allocator behavior would leak stack/heap contents to firmware or create nondeterministic command contents.

Most direct-send helpers do not free the skb on send failure in the local function. This is consistent with the common ath11k WMI send ownership model in much of the file, but functions with custom failure handling, such as the debug-log tail, make ownership easy to get wrong when copying patterns into new helpers.

## Test Signals

Useful test and review signals for this chunk include:

- Debugfs firmware logging tests for each accepted `WMI_DEBUG_LOG_PARAM_*` value, including multi-word module bitmap writes where non-final writes do not send WMI and final writes send the bitmap then clear `ar->debug.module_id_bitmap`.
- WMI attach/connect tests or boot logs on single-radio and multi-radio hardware verifying endpoint count bounds, PDEV WMI handle setup, `service_ready`/`unified_ready` completions, and `preferred_hw_mode` for single-PDEV multi-RXDMA targets.
- WoWLAN suspend tests covering magic packet, disconnect wake, AP/IBSS wake events, pattern wake, host wakeup indication on resume, and hardware data filter enable/disable. Firmware traces should show the expected command IDs and event bitmaps.
- Pattern offload tests for zero, maximum, and rejected-over-maximum pattern lengths, plus native Wi-Fi decap conversion paths in `wow.c`, checking that pattern and mask matching still works after CE byte-swapping.
- PNO/NLO tests using one and two scan plans, hidden SSIDs, passive scans, randomized MAC requests, RSSI thresholds, maximum SSID count, and maximum channel count. Resume cleanup should send `WMI_NLO_CONFIG_STOP` only when `ar->nlo_enabled` was set.
- ARP/NS protocol-offload tests with zero, one, two, and more-than-two IPv6 addresses to exercise both base and extension NS tuple arrays, plus up to two IPv4 ARP targets. Disable should send tuples with validity flags cleared.
- GTK rekey offload tests around suspend/resume should verify enable command payloads, request-status-before-disable ordering, replay counter update from firmware status events, and correct behavior when `arvif->rekey_data.enable_offload` is false.
- BIOS SAR/GEO tests on platforms with ACPI/BIOS SAR inputs should verify pdev ID, table lengths, alignment, and firmware acceptance of `WMI_PDEV_SET_BIOS_SAR_TABLE_CMDID` and `WMI_PDEV_SET_BIOS_GEO_TABLE_CMDID`.
- STA keepalive tests should verify service-bit gating in `mac.c`, null-frame keepalive command generation, and ARP/gratuitous-ARP payload fields if those methods are enabled by a caller.
- 6 GHz regulatory tests should compare behavior with and without `WMI_TLV_SERVICE_REG_CC_EXT_EVENT_SUPPORT` and with radios that do or do not set `ar->supports_6ghz`, especially station TPC, interface-add regulatory updates, and STA authorization on 6 GHz channels.

For the research pipeline, the artifact signal is that this source-tree-aligned chunk document exists at `Docs/researches/chunks/subset-b-004739_research.md` and covers only `wmi.c` lines 9186-10050. The final per-file synthesis should merge this with adjacent `ath11k/wmi.c` chunks that cover earlier command definitions, shared allocation/send helpers, and later WMI event parsing.
