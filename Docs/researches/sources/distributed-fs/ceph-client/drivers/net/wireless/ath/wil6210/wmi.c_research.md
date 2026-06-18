# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wmi.c

## Purpose
`wmi.c` implements the host-side Wireless Module Interface for the Qualcomm Atheros/Wilocity `wil6210` 60 GHz wireless driver. It translates driver operations into firmware mailbox commands, receives firmware events from the mailbox, routes those events to cfg80211/netdev/ring-management handlers, and owns the firmware address-remapping tables used when host code dereferences firmware-provided buffers.

The file is central to device bring-up, connection management, scan reporting, AP/PCP operation, P2P discovery, block-ack negotiation, suspend/resume, EDMA ring setup, management frame Tx/Rx, link statistics, temperature reads, LED control, and firmware capability-gated features.

## Important APIs, Types, and Functions
- Module parameters:
  - `max_assoc_sta` caps AP station count against firmware and driver limits.
  - `agg_wsize` controls automatic Tx Block Ack establishment.
  - `led_id` selects the device LED for firmware LED configuration.
- Firmware memory maps:
  - `sparrow_fw_mapping`, `talyn_fw_mapping`, `talyn_mb_fw_mapping`, and `sparrow_d0_mac_rgf_ext` define linker-to-host address mappings.
  - `fw_mapping[MAX_FW_MAPPING_TABLE_SIZE]` is the active mapping table used by WMI buffer validation.
  - `wil_find_fw_mapping()` returns a mapping by section name.
  - `wmi_addr_remap()`, `wmi_buffer_block()`, `wmi_buffer()`, and `wmi_addr()` validate alignment, BAR bounds, overflow, and host-visible offsets before returning `__iomem` pointers.
- Mailbox command APIs:
  - `wmi_send()` serializes asynchronous firmware commands through `wil->wmi_mutex`.
  - `wmi_call()` sends a command and waits for a matching event ID/MID completion through `wil->wmi_call`.
  - `__wmi_send()` builds `wil6210_mbox_hdr` plus `wmi_cmd_hdr`, writes command payloads to the Tx mailbox ring, advances the hardware head, traces the command, and interrupts firmware with `SW_INT_MBOX`.
  - `wmi_read_hdr()` reads a mailbox header through validated firmware buffer addressing.
- Event receive and dispatch:
  - `wmi_recv_cmd()` runs from the threaded IRQ path, drains Rx mailbox descriptors, copies events into `pending_wmi_event`, completes immediate `wmi_call()` replies, and queues `wil->wmi_event_worker`.
  - `wmi_event_worker()`, `next_wmi_ev()`, and `wmi_event_handle()` run deferred event handling in workqueue context.
  - `wmi_evt_handlers[]` maps selected event IDs to handlers.
  - `wmi_event_flush()` drops queued events during reset/teardown.
  - `wil_is_wmi_idle()` checks pending event queue, active synchronous call, and mailbox Rx head/tail for power-management idleness.
- Key event handlers:
  - `wmi_evt_ready()` records firmware readiness, max VIF/MID support, firmware version, calibration status, max AP association count, recovery state, and completes `wil->wmi_ready`.
  - `wmi_evt_rx_mgmt()` and `wmi_evt_sched_scan_result()` validate variable event lengths, derive 60 GHz channel/frequency, and report BSS or management frames to cfg80211.
  - `wmi_evt_scan_complete()` completes cfg80211 scans and schedules delayed P2P listen if needed.
  - `wmi_evt_connect()` validates connect payload lengths/CID, initializes Tx rings, notifies station or AP cfg80211 paths, updates STA status, and tracks connected VIFs.
  - `wmi_evt_disconnect()` calls `wil6210_disconnect_complete()` and may notify packet loss in host-AP-SME mode.
  - `wmi_evt_eapol_rx()` reconstructs Ethernet EAPOL frames from firmware events and injects them into the network stack.
  - `wmi_evt_ring_en()`, `wmi_evt_ba_status()`, `wmi_evt_addba_rx_req()`, and `wmi_evt_delba()` coordinate data-port opening and AMPDU state.
  - `wmi_evt_auth_status()` and `wmi_evt_reassoc_status()` handle FT roaming auth/reassoc events, key removal, ring modify, and cfg80211 FT/roam notifications.
  - `wmi_evt_link_stats()` parses variable link-stat records and stores basic/global firmware stats.
  - `wmi_evt_link_monitor()` maps firmware RSSI threshold notifications to cfg80211 CQM events.
- Command helpers:
  - Basic firmware/device commands: `wmi_echo()`, `wmi_set_mac_address()`, `wmi_led_cfg()`, `wmi_rbufcap_cfg()`.
  - AP/PCP/P2P: `wmi_pcp_start()`, `wmi_pcp_stop()`, `wmi_set_ssid()`, `wmi_get_ssid()`, `wmi_set_channel()`, `wmi_get_channel()`, `wmi_p2p_cfg()`, `wmi_start_listen()`, `wmi_start_search()`, `wmi_stop_discovery()`, `wmi_port_allocate()`, `wmi_port_delete()`.
  - Security and IEs: `wmi_add_cipher_key()`, `wmi_del_cipher_key()`, `wmi_set_ie()`, `wmi_update_ft_ies()`.
  - Rx/Tx/rings: `wmi_rxon()`, `wmi_rx_chain_add()`, `wil_wmi_tx_sring_cfg()`, `wil_wmi_rx_sring_add()`, `wil_wmi_cfg_def_rx_offload()`, `wil_wmi_rx_desc_ring_add()`, `wil_wmi_tx_desc_ring_add()`, `wil_wmi_bcast_desc_ring_add()`.
  - Management frames and scans: `wmi_abort_scan()`, `wmi_start_sched_scan()`, `wmi_stop_sched_scan()`, `wmi_mgmt_tx()`, `wmi_mgmt_tx_ext()`.
  - Block Ack: `wmi_addba()`, `wmi_delba_tx()`, `wmi_delba_rx()`, `wmi_addba_rx_resp()`, `wmi_addba_rx_resp_edma()`.
  - Power and telemetry: `wmi_suspend()`, `wmi_resume()`, `wmi_ps_dev_profile_cfg()`, `wmi_get_temperature()`, `wmi_get_all_temperatures()`, `wmi_link_stats_cfg()`, `wmi_set_cqm_rssi_config()`, `wmi_set_mgmt_retry()`, `wmi_get_mgmt_retry()`.

## Control Flow
The outbound path begins with a driver subsystem constructing a WMI command payload from a `wmi.h` struct. `wmi_send()` or `wmi_call()` acquires `wil->wmi_mutex`, checks firmware readiness and suspend/resume restrictions, waits for a free Tx mailbox descriptor, copies the command header and payload into firmware-visible memory, marks the descriptor full, advances the mailbox head, traces the command, and raises a software interrupt to firmware. `wmi_call()` additionally installs `wil->reply_id`, `wil->reply_mid`, `wil->reply_buf`, and `wil->reply_size` under `wmi_ev_lock` and waits for `wil->wmi_call`.

The inbound path is intentionally split. `wmi_recv_cmd()` runs in the IRQ thread only long enough to copy firmware events out of the Rx mailbox, mark descriptors empty, advance the mailbox tail, and either complete a synchronous reply immediately or enqueue the event on `wil->pending_wmi_ev`. Deferred handlers then run in `wmi_event_worker()`, which avoids deadlocking the IRQ thread when event handling itself sends WMI commands.

Event dispatch validates the WMI mailbox type and header size, normalizes broadcast MID to MID 0, rejects events for invalid or absent VIFs, checks whether the event completes a pending `wmi_call()`, and otherwise dispatches through `wmi_evt_handlers[]`. Unknown WMI events are logged rather than fatal.

Higher-level flows sit on top of that transport. Connection events allocate/configure Tx rings before notifying cfg80211; disconnect events route to common disconnect completion; scan events feed cfg80211 BSS tables; scheduled scan result events report PNO results; EDMA setup commands synchronously wait for firmware tail pointers before enabling rings in driver state; suspend requires both the WMI suspend event and a later `suspend_resp_comp` wait condition.

## State and Persistence
Most state is in `struct wil6210_priv` and `struct wil6210_vif`, not persisted beyond driver runtime. Important mutable fields include `wil->status` bits, `wil->wmi_seq`, `wil->reply_*`, `wil->pending_wmi_ev`, mailbox ring head/tail shadows, `wil->sta[]`, Tx/Rx ring metadata, firmware capability bitmaps, suspend statistics, firmware stats caches, and per-VIF scan/connect state. Persistent storage is not used; firmware command state is reconstructed after reset and firmware readiness.

The active `fw_mapping[]` table is global driver state initialized elsewhere from the chip-specific constant maps in this file. LED blink timing and `led_polarity` are global runtime constants. Module parameters persist only as module configuration values.

## Dependencies and Integration Points
- Includes `wil6210.h`, `txrx.h`, `wmi.h`, and `trace.h`; depends on many driver-owned helpers and status bits.
- Uses Linux networking/cfg80211 APIs: `cfg80211_inform_bss_frame_data()`, `cfg80211_scan_done()`, `cfg80211_connect_bss()`, `cfg80211_connect_result()`, `cfg80211_new_sta()`, `cfg80211_del_sta()`, `cfg80211_rx_mgmt()`, `cfg80211_sched_scan_results()`, `cfg80211_ft_event()`, `cfg80211_roamed()`, `cfg80211_cqm_rssi_notify()`, and netdev stats delivery.
- Integrates with Tx/Rx code through `wil_ring_init_tx()`, `wil_addba_tx_request()`, `wil_addba_rx_request()`, `wil_tid_ampdu_rx_free()`, `wil->txrx_ops.tx_ring_modify()`, EDMA status/descriptor ring setup, and queue updates.
- Integrates with power management through `wil_is_wmi_idle()`, `wmi_suspend()`, `wmi_resume()`, HALP vote/unvote, suspend status bits, and `wil->wq`.
- Integrates with firmware recovery through `wil_set_recovery_state()`, `wil_fw_error_recovery()`, reset status checks, and mailbox-ready gating.
- Exposes public prototypes indirectly through `wil6210.h`; `wmi.h` supplies all command/event wire structs and IDs.

## Risks and Edge Cases
- Mailbox pointer validation is security- and stability-critical. Firmware-provided addresses must remain DWORD-aligned, remappable, inside BAR bounds, and non-overflowing; bugs here can turn malformed firmware events into invalid MMIO access.
- `__wmi_send()` assumes Tx mailbox descriptors become free within fixed retry loops. Firmware stalls surface as `-EBUSY` or timeouts and may cascade into recovery.
- `wmi_call()` supports one synchronous waiter per device through shared `wil->reply_*` state, so serialization by `wmi_mutex` is essential.
- Late events after a timed-out `wmi_call()` are explicitly dropped when they match a new pending reply with a reply buffer, reducing misdelivery but making timeout diagnosis important.
- Many firmware event payloads are variable length. The code has explicit checks for management, connect, FT, scheduled scan, and link-stat events, but any protocol drift in `wmi.h` can cause false rejection or under-validation.
- Several helpers truncate user/cfg80211 inputs to firmware maxima for scheduled scan match sets, channels, and plans; this is logged at debug level rather than treated as an error.
- Capability checks are uneven by feature: PNO and management retry are gated, AP SME partial offload is checked in `wmi_pcp_start()`, while many protocol structs are assumed compatible with the running firmware.
- Suspend/resume permits only traffic suspend/resume commands during suspend status bits. Incorrect status-bit transitions can block legitimate WMI activity.
- Connection event handling mutates STA and ring state before all cfg80211 notifications complete; error paths must reset `wil->sta[cid]` and connecting bits accurately.
- In `wmi_evt_auth_status()`, the FT roaming state check uses `wil->status` with `wil_vif_ft_roam`; this looks suspicious because the same bit is otherwise used with `vif->status`.

## Test Signals
- Build coverage should include `CONFIG_WIL6210`, normal DMA, enhanced DMA, AP, station, P2P, and suspend/resume code paths.
- Runtime smoke tests: firmware ready completion, `wmi_echo()`, MAC set, LED config when `led_id` is valid, SSID/channel set/get, temperature reads, and CQM RSSI config.
- cfg80211 integration tests: active scan completion, scheduled scan start/stop/result, station connect/disconnect, AP station add/remove, management frame Tx/Rx, FT auth/reassoc roaming, and EAPOL delivery.
- Ring tests: legacy Rx chain add, EDMA Tx/Rx status ring add, Rx descriptor ring add, Tx descriptor ring add, broadcast descriptor ring add, and returned hardware tail pointer sanity.
- Block Ack tests: ADDBA request/response, DELBA for Tx and Rx, extended CID/TID path, A-MSDU capability path, and `agg_wsize` values.
- Fault injection signals: WMI call timeout, mailbox ring full/head busy, invalid firmware buffer address, short/corrupt event lengths, invalid MID/CID/ring IDs, unsupported firmware capability, and suspend rejection paths.
- Tracepoints `trace_wil6210_wmi_cmd` and `trace_wil6210_wmi_event`, plus `wil_dbg_wmi` logs, are the main observability hooks for command/event sequencing.
