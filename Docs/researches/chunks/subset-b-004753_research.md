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
