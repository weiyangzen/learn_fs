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
