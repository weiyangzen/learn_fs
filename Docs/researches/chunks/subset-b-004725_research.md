# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi.c lines 1-7925

## Scope And Purpose

This chunk is the first 7,925 lines of the ath10k non-TLV WMI implementation. It covers the firmware-version abstraction layer for WMI command IDs, parameter IDs, peer capability flags, WMI receive dispatch, service-ready parsing, firmware initialization command construction, scan/vdev/peer command builders, management-frame event handling, survey/statistics parsing, AP beacon/SWBA handling, DFS/radar/spectral PHY error processing, TPC debug-table conversion, TDLS/STA power-save event handling, and host-memory allocation requested by firmware.

The file is the main host-side bridge between Linux/mac80211 driver state and ath10k firmware's Wireless Module Interface. Code above this layer generally calls function pointers in `struct wmi_ops` or wrappers from `wmi-ops.h`; this file fills those operations for main, 10.1, 10.2, 10.2.4, and 10.4 firmware families and translates common ath10k/mac80211 concepts into version-specific WMI binary messages.

This chunk ends immediately after `ath10k_wmi_set_wmm_param()`. Many later command builders, the final `struct wmi_ops` tables, attach/detach logic, and host-memory free path are in chunk `subset-b-004726`, so references to final ops registration and cleanup are cross-chunk dependencies.

## Version Maps And Protocol Surface

The opening section is mostly static protocol mapping data:

- `wmi_cmd_map`, `wmi_10x_cmd_map`, `wmi_10_2_cmd_map`, `wmi_10_2_4_cmd_map`, and `wmi_10_4_cmd_map` translate semantic ath10k command slots into firmware-specific command IDs, with unsupported slots set to `WMI_CMD_UNSUPPORTED`.
- `wmi_vdev_param_map`, `wmi_10x_vdev_param_map`, `wmi_10_2_4_vdev_param_map`, and `wmi_10_4_vdev_param_map` translate vdev parameters such as RTS threshold, beacon interval, protection, NSS, multicast rates, 4-address learning, proxy STA, RTT responder role, TSF increment/decrement, and 10.4-only controls.
- `wmi_pdev_param_map`, `wmi_10x_pdev_param_map`, `wmi_10_2_4_pdev_param_map`, and `wmi_10_4_pdev_param_map` translate physical-device parameters such as chain masks, tx power, ANI, LTR, scan/stat update periods, BT coexistence, multicast-to-unicast, RX filter, burst controls, TDLS/powersave controls, and 10.4-specific reset/TTL/CCA/PPDU settings.
- `wmi_peer_flags_map`, `wmi_10x_peer_flags_map`, and `wmi_10_2_peer_flags_map` normalize peer association flags for auth, QoS, PTK/GTK handshakes, APSD, HT/VHT, bandwidth, STBC, LDPC, MIMO power save, PMF, VHT-on-2GHz, and 160 MHz support.

These tables are a compatibility boundary. Most later builders do not hard-code numeric firmware IDs directly; they use the selected map through `ar->wmi.cmd`, `ar->wmi.vdev_param`, `ar->wmi.pdev_param`, and peer flag maps that are assigned later in the file. Incorrect entries silently route valid driver requests to wrong firmware commands or mark supported firmware features as unsupported.

## Channel And Buffer Helpers

`ath10k_wmi_put_wmi_channel()` converts a `struct wmi_channel_arg` into firmware channel layout. It encodes passive/IBSS/HT/VHT/HT40/DFS flags, primary and center frequencies, regulatory power values, and mode. It has special VHT80+80 and VHT160 handling: secondary center frequency and DFS-on-secondary-channel flag are inferred through `ieee80211_get_channel()`. This function feeds vdev start/restart and scan-channel-list builders.

`ath10k_wmi_alloc_skb()` is the common allocator for outbound WMI payloads. It allocates HTC skb headroom, rounds payload length to 4 bytes, reserves headroom, checks 4-byte data alignment, zeroes padding, and returns an skb with the payload area already present. Most command builders in this chunk depend on this zero-fill behavior to leave reserved fields clean.

`ath10k_wmi_cmd_send_nowait()` pushes a `struct wmi_cmd_hdr`, traces the command, and hands the skb to HTC. `ath10k_wmi_cmd_send()` is the blocking wrapper: it rejects `WMI_CMD_UNSUPPORTED`, waits on `ar->wmi.tx_credits_wq`, prioritizes queued beacons before sending, handles wedged/crash-flush state, frees failed skbs, and starts recovery on persistent `-EAGAIN`. Command send is therefore coupled to HTC credit accounting and beacon scheduling, not just skb formatting.

`ath10k_wmi_wait_for_service_ready()` and `ath10k_wmi_wait_for_unified_ready()` wait for firmware boot completions. Service-ready wait includes a PCI/CE workaround: on timeout it polls all copy-engine send completions once and waits again.

## Management TX And RX

`ath10k_wmi_op_gen_mgmt_tx()` builds a management TX command from a mac80211 skb. It validates the frame type, chooses the vdev from `ATH10K_SKB_CB(msdu)->vif` when available, computes extra MIC/MMIE room for protected deauth/disassoc/action frames, copies the 802.11 frame into the WMI payload, and fills peer DA, buffer length, tx rate, and tx power fields.

`wmi_process_mgmt_tx_comp()` completes management TX skbs tracked in `ar->wmi.mgmt_pending_tx` by descriptor ID. Under `ar->data_lock` it removes the IDR entry, unmaps DMA, sets or clears `IEEE80211_TX_STAT_ACK`, stores ACK RSSI if available, and reports status back through `ieee80211_tx_status_irqsafe()`.

`ath10k_wmi_event_mgmt_tx_compl()` handles one TLV management completion. `ath10k_wmi_event_mgmt_tx_bundle_compl()` loops bundled completions. A notable risk in this chunk is that the bundled path sets `param.status = __le32_to_cpu(arg.desc_ids[i])` even though `struct wmi_tlv_mgmt_tx_bundle_compl_ev_arg` has a separate `status` array. If this is not compensated elsewhere, bundled completions may report ACK status based on descriptor IDs rather than firmware completion status.

`ath10k_wmi_op_pull_mgmt_rx_ev()` and `ath10k_wmi_10_4_op_pull_mgmt_rx_ev()` parse management RX event envelopes, including extended info when `WMI_RX_STATUS_EXT_INFO` is set. They validate skb length, pull the event header, verify MSDU length, copy optional timestamp/RSSI extension data, and trim padding.

`ath10k_wmi_event_mgmt_rx()` converts a firmware management RX event into mac80211 RX status. It drops frames during CAC and frames with decrypt/key-cache/CRC errors, marks MIC errors, derives band/frequency from channel number rather than PHY mode, computes signal from SNR/noise floor, fills chain RSSI, maps rate to mac80211 rate index, skips monitor duplication, handles WEP reauth decryption marking, strips protected flags for firmware-decrypted PMF-style frames, updates beacon tracking, timestamps beacon/probe responses, and finally passes ownership to `ieee80211_rx_ni()`.

## Scan And Survey Control Flow

The scan event handlers maintain `ar->scan.state` under `ar->data_lock`:

- `ath10k_wmi_event_scan_started()` transitions `ATH10K_SCAN_STARTING` to `ATH10K_SCAN_RUNNING`, completes `ar->scan.started`, and notifies mac80211 ready-on-channel for ROC scans.
- `ath10k_wmi_event_scan_start_failed()` completes the start wait and finishes the scan when start fails.
- `ath10k_wmi_event_scan_completed()` finishes running or aborting scans, while warning on idle/starting states.
- `ath10k_wmi_event_scan_bss_chan()` clears `ar->scan_channel` for BSS channel events.
- `ath10k_wmi_event_scan_foreign_chan()` records the current off-channel `ieee80211_channel` and completes ROC `on_channel` when the reported frequency matches.

`ath10k_wmi_event_scan()` parses `wmi_scan_ev_arg`, logs event/reason/frequency/request IDs, and dispatches to the state helpers. It also accepts several events as informational or ignored: dequeued, preempted, restarted, and foreign-channel exit.

Survey data has two paths. Legacy channel-info events are parsed by `ath10k_wmi_op_pull_ch_info_ev()` and `ath10k_wmi_10_4_op_pull_ch_info_ev()`, then processed by `ath10k_wmi_event_chan_info()`. For firmware that emits a single report per channel, `ath10k_wmi_event_chan_info_unpaired()` writes noise, total time, and busy time into `ar->survey[idx]`. For paired start/stop reports, `ath10k_wmi_event_chan_info_paired()` uses saved cycle/rx-clear counters and `ath10k_hw_fill_survey_time()`. BSS channel survey events use 64-bit counters in `ath10k_wmi_event_pdev_bss_chan_info()` and complete `ar->bss_survey_done`.

## Statistics And Debug Events

The chunk provides a large set of little-endian conversion helpers for firmware statistics:

- `ath10k_wmi_pull_pdev_stats_base()`, `_tx()`, `_rx()`, and `_extra()` fill `struct ath10k_fw_stats_pdev`.
- 10.4-specific TX, peer, and vdev extended stats helpers fill additional counters such as HW pause, sequence state, MU sequence, ACK failures, RX duration, peer RX rate, and FTM counts.
- `ath10k_wmi_main_op_pull_fw_stats()`, `ath10k_wmi_10x_op_pull_fw_stats()`, `ath10k_wmi_10_2_op_pull_fw_stats()`, `ath10k_wmi_10_2_4_op_pull_fw_stats()`, and `ath10k_wmi_10_4_op_pull_fw_stats()` parse version-specific statistics event layouts into linked lists of pdev, peer, extended peer, and vdev stats.

Most parsing uses `skb_pull()` after checking enough payload remains. Allocation failures for individual stats records are tolerated by skipping that record, so a stats event can partially populate output under memory pressure.

`ath10k_wmi_event_update_stats()` delegates to `ath10k_debug_fw_stats_process()`. Debug message and print events feed trace/debug channels, sanitize printable firmware strings to a fixed 100-byte local buffer, and queue coverage-class work after several event types because firmware may reset coverage-related registers.

## AP Beacon And SWBA Flow

AP beacon handling is split across SWBA parsing, TIM/NoA mutation, DMA mapping, and deferred send:

- `ath10k_wmi_op_pull_swba_ev()`, `ath10k_wmi_10_2_4_op_pull_swba_ev()`, and `ath10k_wmi_10_4_op_pull_swba_ev()` decode firmware SWBA events and extract per-vdev TIM and optional P2P NoA data. All variants bound-check TIM bitmap lengths; 10.4 subtracts a 4-byte guard length and ignores NoA.
- `ath10k_wmi_update_tim()` persists firmware TIM bitmap data in `arvif->u.ap.tim_bitmap`, recalculates effective TIM length, expands the mac80211 beacon TIM IE when needed, sets DTIM/CAB skb flags, and updates the virtual bitmap.
- `ath10k_wmi_update_noa()` applies P2P NoA changes and appends NoA data to the beacon skb if available.
- `ath10k_wmi_event_host_swba()` iterates the vdev bitmap, resolves each `ath10k_vif`, handles CSA countdown completion, gets a fresh mac80211 beacon, fills sequence number/TIM/NoA, maps or copies the beacon into DMA-visible storage, updates `arvif->beacon` and `beacon_state`, and calls `ath10k_wmi_tx_beacons_nowait()`.

`ath10k_wmi_tx_beacon_nowait()` sends scheduled DMA beacon references via `ath10k_wmi_beacon_send_ref_nowait()` while holding `ar->data_lock` only around state transitions. Beacon state can be `SCHEDULED`, `SENDING`, or `SENT`; SWBA overrun warnings indicate that firmware requested a new beacon before the previous one was cleanly consumed.

## DFS, Radar, And Spectral PHY Errors

`ath10k_wmi_event_phyerr()` is the top-level PHY error dispatcher. It parses a common or 10.4 phyerr header, builds a 64-bit TSF, iterates each included phyerr record, checks buffer lengths, normalizes firmware-specific phy error codes, and dispatches radar, spectral-scan, or combined false-radar-extension events.

DFS processing includes:

- `ath10k_wmi_event_dfs()` iterates PHYERR TLVs and recognizes radar pulse summary and FFT report TLVs.
- `ath10k_dfs_fft_report()` filters likely false pulses based on RSSI and peak magnitude.
- `ath10k_dfs_radar_report()` decodes radar pulse fields, chooses `ar->rx_channel` or `ar->tgt_oper_chan`, passes pulses to the DFS pattern detector, and either reports radar to mac80211 or, for FCC firmware with `WMI_SERVICE_HOST_DFS_CHECK_SUPPORT`, stores `ar->last_radar_info` and queues firmware confirmation work.
- `ath10k_radar_confirmation_work()` sends radar-found information to firmware, waits for `ar->wmi.radar_confirm` for `ATH10K_WMI_DFS_CONF_TIMEOUT_HZ`, treats missing confirmation as real radar, and resets `ar->radar_conf_state` unless confirmation was stopped.
- `ath10k_wmi_event_dfs_status_check()` accepts firmware's radar-detection status and completes the confirmation wait.

Spectral processing in `ath10k_wmi_event_spectral_scan()` validates TLV boundaries and passes FFT reports to `ath10k_spectral_process_fft()`. DFS behavior is compile-time gated by `CONFIG_ATH10K_DFS_CERTIFIED`, but PHY error parsing still runs to classify events.

## TPC, TDLS, Power Save, And Miscellaneous Events

TPC configuration and final-table events are converted into debug stats objects:

- `ath10k_wmi_tpc_config_get_rate_code()` builds the rate-code and preamble-boundary tables for CCK, OFDM, HT20/40, VHT20/40/80, and extra legacy rates.
- `ath10k_tpc_config_get_rate()` and `ath10k_tpc_config_disp_tables()` compute min-limited power values for CDD, STBC, and TXBF tables.
- `ath10k_wmi_tpc_final_get_rate()` and `ath10k_wmi_tpc_stats_final_disp_tables()` add CTL power-table limits and 2GHz/5GHz preamble mapping.
- `ath10k_wmi_event_pdev_tpc_config()` and `ath10k_wmi_event_tpc_final_table()` allocate stats objects, cap firmware-provided rate counts, populate metadata, and hand results to debugfs processing.

`ath10k_wmi_handle_tdls_peer_event()` handles 10.4 TDLS teardown requests by validating the peer, mapping firmware teardown reasons to WLAN TDLS reason codes, resolving the vdev, and calling `ieee80211_tdls_oper_request()`.

`ath10k_wmi_event_peer_sta_ps_state_chg()` records firmware-reported STA power-save state in `ath10k_sta.peer_ps_state` under `ar->data_lock`. Several other event stubs only log receipt: FTM integration, GTK offload status/failure, DELBA/ADDBA completion, key install completion, instant RSSI stats, standby/resume requests, QVIT, profile match, RTT/TSF reports, DCS interference, and TBTT offset updates.

WoW wakeup completes `ar->wow.wakeup_completed`, parses wake reason, and logs a human-readable reason. Roam events currently act on beacon-miss by calling `ath10k_mac_handle_beacon_miss()` and warn that better-AP, low-RSSI, suitable-AP, and handoff-failed reasons are not implemented.

## Service Ready, Host Memory, And Initialization

Service-ready handling is asynchronous. `ath10k_wmi_event_service_ready()` stores the skb in `ar->svc_rdy_skb` and queues `ar->svc_rdy_work` on `ar->workqueue_aux`. `ath10k_wmi_event_service_ready_work()` then:

- Parses main or 10.x service-ready layouts through `ath10k_wmi_pull_svc_rdy()`.
- Maps firmware service bits into `ar->wmi.svc_map`.
- Stores TX power, HT/VHT capabilities, firmware version fields, PHY capability, RF chains, EEPROM/regulatory channel bounds, and system capability fields into `struct ath10k`.
- Clamps advertised RF chains to `ar->max_spatial_stream`.
- Initializes default chain masks if config masks are unset.
- Writes `wiphy->fw_version` if it was empty.
- Handles `WMI_SERVICE_PEER_CACHING` by changing active peer, max peer, TID, and station counts.
- Reuses existing coherent host-memory chunks only if the request IDs and computed sizes still match; otherwise it frees old chunks and allocates fresh chunks with `ath10k_wmi_alloc_host_mem()`.
- Frees the service-ready skb and completes `ar->wmi.service_ready`.

Host-memory requests can specify units as active peers, peers, or vdevs. The code adjusts requested unit counts from current `ar->num_active_peers`, `ar->max_num_peers`, and `ar->max_num_vdevs`, with one extra unit for target self-peer cases. Allocated chunks are later advertised in init commands by `ath10k_wmi_put_host_mem_chunks()`.

Init builders are version-specific:

- `ath10k_wmi_op_gen_init()` builds the main `wmi_init_cmd` with fixed `TARGET_*` resource constants.
- `ath10k_wmi_10_1_op_gen_init()` uses 10.x constants and 10.x resource layout.
- `ath10k_wmi_10_2_op_gen_init()` conditionally increases peer/TID counts when peer stats are enabled and sets feature bits for RX batch mode, COEX GPIO, peer stats, and 64-bit BSS channel info.
- `ath10k_wmi_10_4_op_gen_init()` uses dynamic limits from `ar->max_num_vdevs`, `ar->max_num_peers`, `ar->num_active_peers`, `ar->num_tids`, hardware chain masks, HTT pending TX count, and 10.4-specific ATF/QWRAP/thermal/IP header padding/minfree settings.

## RX Dispatch And HTC Integration

`ath10k_wmi_connect()` connects the WMI control service over HTC. It clears the service map, installs endpoint callbacks for TX completion, RX completion, and TX credits, requests `ATH10K_HTC_SVC_ID_WMI_CONTROL`, and stores the returned endpoint ID in `ar->wmi.eid`.

`ath10k_wmi_process_rx()` calls the selected `ath10k_wmi_rx()` operation and warns on parse/dispatch errors. Four dispatchers are present in this chunk:

- `ath10k_wmi_op_rx()` handles main firmware event IDs.
- `ath10k_wmi_10_1_op_rx()` handles 10.1/10.x IDs.
- `ath10k_wmi_10_2_op_rx()` handles 10.2/10.2.4 IDs, including temperature, BSS channel info, and peer STA PS state changes.
- `ath10k_wmi_10_4_op_rx()` handles 10.4 IDs, including TDLS peer events, TPC final table, DFS status confirmation, and peer STA PS state changes.

All dispatchers pull the WMI command header, trace the event, then switch on the version-specific event ID. Management RX and service-ready events transfer skb ownership and return without freeing; most other paths free the skb at the common `out` label. Testmode can consume many 10.x/10.2/10.4 events through `ath10k_tm_event_wmi()`, but ready events are still processed normally so UTF firmware boot can complete.

## Command Builders In This Chunk

Command generator functions in this chunk construct outbound skbs but generally do not send them. Sending is performed by wrappers/op users outside this chunk through selected WMI command IDs.

PDEV builders include:

- `ath10k_wmi_op_gen_pdev_set_base_macaddr()`
- `ath10k_wmi_op_gen_pdev_set_rd()` and `ath10k_wmi_10x_op_gen_pdev_set_rd()`
- `ath10k_wmi_op_gen_pdev_suspend()` and `_resume()`
- `ath10k_wmi_op_gen_pdev_set_param()`
- `ath10k_wmi_10_2_op_gen_pdev_get_temperature()`
- `ath10k_wmi_10_2_op_gen_pdev_bss_chan_info()`

Scan builders include `ath10k_wmi_start_scan_verify()`, `ath10k_wmi_start_scan_tlvs_len()`, `ath10k_wmi_put_start_scan_common()`, `ath10k_wmi_put_start_scan_tlvs()`, `ath10k_wmi_op_gen_start_scan()`, `ath10k_wmi_10x_op_gen_start_scan()`, `ath10k_wmi_start_scan_init()`, `ath10k_wmi_op_gen_stop_scan()`, and `ath10k_wmi_op_gen_scan_chan_list()`. They validate IE/channel/SSID/BSSID counts, add host scan/request prefixes, serialize optional TLV blocks, set conservative default scan timing, and request scan-channel-stat events.

VDEV builders include create/delete/start/stop/up/down/set-param/install-key and spectral configure/enable. The start builder validates hidden SSID input, sets hidden-SSID and PMF flags, embeds beacon/DTIM/tx settings, and serializes channel information with `ath10k_wmi_put_wmi_channel()`. Install-key validates cipher/key-data consistency before copying key bytes into the variable payload.

Peer builders include create/delete/flush/set-param and versioned peer association builders. `ath10k_wmi_peer_assoc_fill()` writes common association state, legacy/HT/VHT rates, caps, NSS, MPDU parameters, and peer address. 10.2 adds `info0` max-MCS/max-NSS fields; 10.4 adds bandwidth/RX-NSS override. `ath10k_wmi_peer_assoc_check_arg()` guards MPDU density and rate-array counts.

Other builders in this chunk cover beacon DMA reference send, GPIO config/output, STA power-save mode/params, AP peer power-save params, and WMM parameter serialization.

## State And Persistence Behavior

Key persistent or semi-persistent state touched in this chunk includes:

- `ar->wmi.svc_map`, WMI endpoint ID, barrier/radar/service/unified completions, coherent host-memory chunk list, and pending management TX IDR.
- Firmware-advertised capabilities and version fields stored in `struct ath10k`, including RF chain count, HT/VHT caps, regulatory channel bounds, firmware version string, and service-derived peer-cache sizing.
- Scan state, ROC completions, `ar->scan_channel`, and survey data in `ar->survey[]`.
- AP beacon state per `ath10k_vif`: current beacon skb, DMA address or shared beacon buffer, TIM bitmap/length, DTIM/CAB flags, NoA data, and beacon scheduling state.
- DFS/radar state: DFS counters, detector pulses, `ar->last_radar_info`, `ar->radar_conf_state`, and firmware confirmation completion.
- STA/peer state for low-ACK reporting, TDLS teardown requests, and `ath10k_sta.peer_ps_state`.
- Debug/statistics state passed to ath10k debugfs processors for firmware stats and TPC tables.

Most state changes are protected by `ar->data_lock`, RCU read-side critical sections, completions, or workqueue context. Persistent device/firmware behavior is changed by init resource settings, pdev/vdev/peer command builders, key installation, scan requests, regulatory domain commands, power-save commands, and beacon DMA references once callers send the generated skbs.

## Dependencies And Integration Points

This chunk depends on Linux kernel networking and ath10k infrastructure:

- `sk_buff`, DMA mapping, coherent DMA allocation, IDR, workqueues, completions, spinlocks, RCU, and endian conversion helpers.
- mac80211/cfg80211 APIs for RX/TX status, vifs/stations, channel lookup, scan/ROC notifications, beacon generation, CSA, TDLS requests, radar detection, and survey reporting.
- HTC transport for WMI endpoint connection, TX crediting, skb allocation, and command/event delivery.
- ath10k modules: `core.h`, `htc.h`, `debug.h`, `wmi.h`, `wmi-tlv.h`, `mac.h`, `testmode.h`, `wmi-ops.h`, `p2p.h`, `hw.h`, `hif.h`, and `txrx.h`.
- Debug/trace hooks such as `trace_ath10k_wmi_cmd()`, `trace_ath10k_wmi_event()`, `ath10k_debug_fw_stats_process()`, TPC debug processors, spectral processing, and testmode event interception.
- Firmware-feature and service-bit contracts from WMI headers, including main/10.x/10.2/10.2.4/10.4 command/event IDs and service bitmap semantics.

The source path under `sources/distributed-fs/ceph-client/` indicates this is a vendored kernel driver source within the larger tree. It does not integrate with Ceph filesystem logic directly; its integration surface is Linux wireless hardware support when this driver is built.

## Risks And Edge Cases

Protocol map drift is the largest risk. Every command/event/parameter table must match the firmware family selected at attach time. A wrong map entry can produce plausible but incorrect WMI packets, and unsupported fields are often represented by sentinel values that only fail later when a builder or command send rejects them.

Length validation is extensive but not uniform. Event pull helpers generally check minimum structure sizes and use `skb_pull()`, but some event handlers cast `skb->data` directly after a single size check, and several debug/TPC paths trust firmware array contents after clamping only the top-level rate or chain counts.

Management RX decryption handling is subtle. Firmware may deliver PMF-style protected management frames already decrypted, WEP shared-auth frames encrypted, and some multicast management frames still encrypted depending on hardware parameters. Incorrect flagging can cause duplicate monitor frames, wrong IV/MMIC stripping, or mac80211 accepting encrypted data as decrypted.

Beacon/SWBA timing is race-prone by nature. The code warns on SWBA overruns and juggles DMA mapping, shared beacon buffers, CSA countdowns, and state transitions under partial locking. Failures here can miss beacons, send stale TIM data, or leak/free beacon skbs incorrectly if ownership assumptions change.

DFS/radar handling has regulatory impact. Missing channel context falls back to treating a pulse as radar; lack of firmware confirmation is also treated as radar. Conversely, false-pulse filtering and host/firmware confirmation state must avoid suppressing real radar indications.

Host-memory allocation is based on firmware requests plus mutable driver peer/vdev limits. If peer-cache services, peer-flow-control features, or max peer/vdev values are inconsistent between service-ready and init, firmware and host can disagree about memory sizing.

The bundled management TX completion status issue at lines 2515-2516 is a concrete audit signal: `param.status` appears to be filled from `arg.desc_ids[i]` instead of `arg.status[i]`.

## Test Signals

Useful test and validation signals for this chunk include:

- Boot/init logs showing service-ready completion, correct firmware version string, service bitmap mapping, WMI host-memory chunk allocation/reuse, and successful unified-ready completion.
- WMI command timeout/recovery logs from `ath10k_wmi_cmd_send()` and HTC credit behavior under heavy beaconing.
- Scan tests covering normal completion, start failure, abort, ROC ready/on-channel completions, foreign-channel events, channel-info survey updates, and coverage-class reapplication.
- Management TX/RX tests with protected action/deauth/disassoc frames, PMF, WEP shared-auth reauth, multicast mesh management frames, ACK RSSI reporting, and bundled TX completions.
- AP mode tests for beacon TIM expansion, multicast CAB delivery, P2P NoA append, CSA countdown completion, and SWBA overrun warnings.
- DFS/spectral tests with radar pulse TLVs, FFT TLVs, false-pulse filtering, firmware DFS confirmation timeout/status paths, and `CONFIG_ATH10K_DFS_CERTIFIED` enabled/disabled builds.
- Firmware stats/debugfs tests across main, 10.x, 10.2, 10.2.4, and 10.4 layouts, including peer-stats-enabled and extended 10.4 stats.
- Temperature and BSS channel survey events on 10.2/10.4 firmware.
- TDLS teardown, peer kickout/low-ACK reporting, peer STA PS state changes, WoW wakeup completion, and vdev start/stop completion paths.
- Sparse/static analysis around direct skb casts, DMA map/unmap ownership, IDR removal, endian conversions, and array bounds in TPC/stat/SWBA parsing.
