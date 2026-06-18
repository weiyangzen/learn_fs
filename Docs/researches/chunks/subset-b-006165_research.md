# sources/distributed-fs/ceph-client/net/bluetooth/mgmt.c lines 10240-10630

## Scope And Purpose

This chunk is the tail of the Bluetooth management control-plane implementation. It covers the last part of service-discovery result filtering, management event emission for found devices, advertising monitor notifications, mesh-specific scan reporting, discovery state events, suspend/resume events, management channel registration, and per-socket cleanup.

The code is not a command parser in this range. The management command handlers and `mgmt_handlers[]` table are defined earlier, and this chunk closes the file by publishing asynchronous events to management sockets and registering the `HCI_CHANNEL_CONTROL` management channel. The main consumers are HCI event/core paths that call into `mgmt_device_found()`, `mgmt_remote_name()`, `mgmt_discovering()`, `mgmt_suspending()`, and `mgmt_resuming()` as controller state changes.

## Important APIs, Types, And Functions

`is_filter_match()` finishes here. It evaluates `hdev->discovery.rssi`, `hdev->discovery.uuid_count`, and `hdev->discovery.uuids` against EIR/scan-response payloads, with special handling for `HCI_QUIRK_STRICT_DUPLICATE_FILTER`. It depends on earlier helpers `eir_has_uuids()` and `has_uuid()`.

`mgmt_adv_monitor_device_lost()` emits `MGMT_EV_ADV_MONITOR_DEVICE_LOST` with `struct mgmt_ev_adv_monitor_device_lost`, a monitor handle, and a Bluetooth address. It is called by Microsoft advertisement-monitor support when monitored devices are removed or lost.

`mgmt_send_adv_monitor_device_found()` allocates an `MGMT_EV_ADV_MONITOR_DEVICE_FOUND` skb. That event has the same payload shape as `MGMT_EV_DEVICE_FOUND` with a leading `monitor_handle`, so the function prepends the little-endian handle and copies the original `DEVICE_FOUND` skb bytes.

`mgmt_adv_monitor_device_found()` fans one built `DEVICE_FOUND` skb out to advertising-monitor-specific events. It walks `hdev->monitored_devices`, whose entries are `struct monitored_device { bdaddr, addr_type, handle, notified }`, updates `dev->notified`, and maintains `hdev->advmon_pend_notify`.

`mesh_device_found()` emits `MGMT_EV_MESH_DEVICE_FOUND` for LE mesh scanning. It optionally filters advertising data by `hdev->mesh_ad_types[16]`, then sends address, RSSI, flags, an `instant` timestamp, and concatenated advertising plus scan-response data in `struct mgmt_ev_mesh_device_found`.

`mgmt_device_found()` is the central asynchronous found-device event builder. It receives BR/EDR or LE discovery data from HCI event code, applies discovery activity and service-filter rules, allocates `MGMT_EV_DEVICE_FOUND`, normalizes address type through `link_to_bdaddr()`, handles invalid RSSI compatibility for old BR/EDR inquiry behavior, appends EIR data, optionally synthesizes Class of Device EIR data, appends scan-response data, and then delegates final delivery to `mgmt_adv_monitor_device_found()`.

`mgmt_remote_name()` emits a name-only `MGMT_EV_DEVICE_FOUND` result after remote-name resolution. When name lookup fails, it sends no EIR name and sets `MGMT_DEV_FOUND_NAME_REQUEST_FAILED`.

`mgmt_discovering()`, `mgmt_suspending()`, and `mgmt_resuming()` are simple event wrappers for `MGMT_EV_DISCOVERING`, `MGMT_EV_CONTROLLER_SUSPEND`, and `MGMT_EV_CONTROLLER_RESUME`.

`chan`, `mgmt_init()`, and `mgmt_exit()` register and unregister the management channel with `hci_mgmt_chan_register()` and `hci_mgmt_chan_unregister()`. The channel uses `HCI_CHANNEL_CONTROL`, the earlier `mgmt_handlers[]` command table, and `mgmt_init_hdev` for per-device initialization.

`mgmt_cleanup()` is called from HCI socket destruction. It iterates all HCI devices under `hci_dev_list_lock`, finds mesh transmissions associated with the closing socket via `mgmt_mesh_next()`, and completes them with `mesh_send_complete(..., true)`.

Important event payload definitions live in `include/net/bluetooth/mgmt.h`: `struct mgmt_ev_device_found`, `struct mgmt_ev_discovering`, `struct mgmt_ev_controller_suspend`, `struct mgmt_ev_controller_resume`, `struct mgmt_ev_adv_monitor_device_found`, `struct mgmt_ev_adv_monitor_device_lost`, and `struct mgmt_ev_mesh_device_found`.

## Control Flow

Discovery filtering first rejects results below the RSSI threshold unless strict duplicate filtering requires a later restart/check path. If UUID filters are active, it requires at least one requested UUID in either the advertising/EIR payload or the scan response. For strict duplicate filtering controllers, the RSSI threshold is checked again before accepting the event.

Advertising monitor loss is direct: fill the event struct, copy the address, set the address type, and broadcast with `mgmt_event()`.

Advertising monitor found delivery is two-stage. `mgmt_device_found()` always builds the normal `MGMT_EV_DEVICE_FOUND` skb first. `mgmt_adv_monitor_device_found()` then either sends it directly when active discovery does not need pending monitor notifications, or iterates monitored devices to send one `MGMT_EV_ADV_MONITOR_DEVICE_FOUND` per newly matched monitor. If a report came only from advertisement monitoring, the normal device-found event is suppressed and the skb is freed after any monitor event is emitted.

The monitor fanout distinguishes three scan sources: active kernel discovery, passive scanning for pending LE reports, and advertisement-monitor-only scanning. Active discovery and pending-report scans may send both normal device-found and one monitor-found event per matched monitor. Advertisement-monitor-only scans send only monitor-found events; subsequent reports for an already notified monitored device use monitor handle `0` unless controller offload is unavailable.

Mesh discovery is checked before normal discovery gating in `mgmt_device_found()`. When `HCI_MESH` is set and the link type is LE, `mesh_device_found()` may emit a mesh event even if normal discovery reporting later returns. Mesh AD-type filtering scans both advertising data and scan response fields by walking length-prefixed EIR elements and comparing the AD type byte against `hdev->mesh_ad_types`.

Normal device-found reporting is gated by `hci_discovery_active(hdev)`. BR/EDR reports outside kernel discovery are dropped. LE reports outside active discovery are allowed only when `hdev->pend_le_reports` is non-empty, which represents passive scanning for pending LE actions, or when advertisement monitoring is active. Service-discovery result filtering and limited-discovery filtering run after those source checks.

Event skb construction writes the fixed header first, then variable data. The code appends advertising/EIR data, conditionally appends a 5-byte generated Class-of-Device EIR element when a `dev_class` pointer exists and the payload lacks `EIR_CLASS_OF_DEV`, then appends scan-response data. `ev->eir_len` covers all appended variable bytes.

Remote-name reporting is a smaller device-found event path. It allocates enough room for a complete-name EIR field only when a name is present, otherwise sets `MGMT_DEV_FOUND_NAME_REQUEST_FAILED`.

Discovery state transitions are driven elsewhere. `hci_discovery_set_state()` calls `mgmt_discovering(hdev, 1)` on `DISCOVERY_FINDING` and `mgmt_discovering(hdev, 0)` when moving to `DISCOVERY_STOPPED` from most states. Suspend and resume events are similarly called from `hci_suspend_dev()` and `hci_resume_dev()` after controller sync operations.

File-level initialization is straight-line: `mgmt_init()` registers the static channel, `mgmt_exit()` unregisters it, and `mgmt_cleanup()` drains mesh send work tied to a closing management socket.

## State And Persistence Behavior

This chunk mostly reports state held in `struct hci_dev`; it does not persist state to disk or stable storage.

Discovery filtering reads `hdev->discovery` fields such as `type`, `result_filtering`, `limited`, `rssi`, `uuid_count`, `uuids`, and `report_invalid_rssi`. It does not mutate those fields in this range, except that reporting code relies on the current discovery state managed by HCI core.

Advertising monitor state is mutable. `hdev->monitored_devices` persists across reports and holds one entry per monitored address/handle. Each `struct monitored_device` has a `notified` bit so the management layer sends only one handle-specific found event per device/monitor until the lower monitor layer clears or removes the entry. `hdev->advmon_pend_notify` persists whether there are still monitored devices waiting for first notification.

`mgmt_adv_monitor_device_found()` owns the input skb after `mgmt_device_found()` hands it over. Depending on scan source, it may pass the skb to `mgmt_event_skb()`, copy it into monitor-specific skbs, or free it with `kfree_skb()`. That ownership boundary is important because monitor-found event construction copies from the original skb but does not replace ownership of it.

Mesh reporting reads persistent `hdev->mesh_ad_types`, which is configured by earlier mesh management commands. An all-zero first byte means accept all LE advertisements for mesh; otherwise the array is treated as a zero-terminated list of desired AD types.

`mgmt_cleanup()` mutates outstanding mesh transmission state by repeatedly completing socket-owned mesh TX objects. It walks all devices under the global HCI device list read lock but relies on `mgmt_mesh_next()` and `mesh_send_complete()` for the per-device mesh TX list mechanics.

## Dependencies And Integration Points

The event APIs depend on core management helpers in the same file: `mgmt_alloc_skb()`, `mgmt_event()`, `mgmt_event_skb()`, `mgmt_limited_event()` elsewhere, `mgmt_pending_*()` elsewhere, and the management command table used by `struct hci_mgmt_chan`.

HCI event integration is extensive. LE advertising reports in `hci_event.c` merge advertising and scan-response data, resolve identity addresses, consult pending LE actions, and call `mgmt_device_found()`. BR/EDR inquiry and inquiry-result paths also call `mgmt_device_found()`, while remote-name completion calls `mgmt_remote_name()`.

HCI core integration supplies discovery and power-state events. `hci_discovery_set_state()` calls `mgmt_discovering()`, suspend calls `mgmt_suspending()`, and resume calls `mgmt_resuming()` with wake reason/address state.

Advertisement monitor integration crosses into `msft.c`. Microsoft monitor code adds/removes entries from `hdev->monitored_devices`, initializes `hdev->advmon_pend_notify`, and calls `mgmt_adv_monitor_device_lost()` when a notified monitored device is removed or lost. The found path in this chunk also checks `msft_monitor_supported(hdev)` to choose handle `0` fallback behavior.

Mesh integration spans earlier management commands, HCI event scan reporting, and HCI socket cleanup. Earlier `set_mesh` command handling configures `HCI_MESH` and `hdev->mesh_ad_types`; this chunk emits mesh found events and cleans socket-owned mesh transmissions.

Protocol integration is through `include/net/bluetooth/mgmt.h` event IDs and packed payload ABI. All multi-byte fields sent here are explicitly little-endian via `cpu_to_le16()`, `cpu_to_le32()`, or `cpu_to_le64()`, preserving the management socket ABI.

Channel integration uses `struct hci_mgmt_chan` with `.channel = HCI_CHANNEL_CONTROL`, `.handlers = mgmt_handlers`, `.handler_count = ARRAY_SIZE(mgmt_handlers)`, and `.hdev_init = mgmt_init_hdev`. This binds the file's earlier command handlers to the kernel HCI management socket infrastructure.

## Risks And Edge Cases

EIR parsing in both UUID filtering and mesh AD-type filtering trusts length-prefixed fields enough to walk by `eir[i] + 1`. UUID filtering has an explicit remaining-length check; mesh filtering only checks `i + 1 < len` at loop entry. Malformed fields with an oversized length can skip past the end without reading a type byte beyond `i + 1`, but changes to the loop body would need care.

The generated Class-of-Device EIR field reserves a fixed 5 extra bytes in the skb allocation. That must stay consistent with `eir_append_data(..., EIR_CLASS_OF_DEV, ..., 3)` and with the updated `eir_len`.

`mgmt_send_adv_monitor_device_found()` computes the monitor skb size as the original device-found skb length plus the structural difference between monitor-found and device-found events. Any ABI layout change to either event struct must preserve that relationship or adjust this calculation.

Advertising monitor notification semantics are stateful. If `dev->notified` or `hdev->advmon_pend_notify` are not reset by monitor removal/reconfiguration paths, userspace can miss first-found events or receive redundant handle-specific events.

The monitor-found path uses handle `0` as a sentinel for subsequent advertisements or no offload support. Userspace consumers must not treat handle `0` as a real monitor handle.

`mgmt_device_found()` can emit a mesh event and then return later before emitting a normal device-found event, depending on discovery state and filters. This is intentional for mesh receivers, but tests should assert both channels separately.

RSSI compatibility behavior differs by mode. BR/EDR discovery reports with `HCI_RSSI_INVALID` are converted to `0` unless service discovery requested invalid RSSI reporting. Service-discovery clients can therefore observe `127` where legacy discovery clients see `0`.

Limited discovery filters use different data sources for BR/EDR and LE. With `dev_class`, the code checks the limited discoverable bit in the class bytes; without it, it searches EIR flags for `LE_AD_LIMITED`. Missing or malformed flags drop LE reports during limited discovery.

`mesh_device_found()` allocates `sizeof(*ev) + eir_len + scan_rsp_len`; callers must ensure lengths are bounded before reaching this path. HCI event code enforces advertising length limits for normal reports, but this function itself does not revalidate combined length against management ABI maxima.

`mgmt_cleanup()` holds `hci_dev_list_lock` while it repeatedly completes mesh transmissions. If `mesh_send_complete()` ever needed the same global lock for writing, this loop could become a lock-order hazard. The current design appears to rely on read-side iteration over devices and per-device cleanup underneath.

## Test Signals

Discovery result tests should cover RSSI thresholds, `HCI_RSSI_INVALID`, strict duplicate filtering, UUID filters across 16-bit/32-bit/128-bit UUID EIR fields, filters split between advertising data and scan response, and malformed EIR length fields.

Normal `MGMT_EV_DEVICE_FOUND` tests should exercise active discovery, non-active BR/EDR suppression, passive LE pending-report allowance, advertisement-monitor-only allowance, limited discovery for BR/EDR Class of Device and LE flags, generated Class-of-Device EIR insertion, scan-response concatenation, and invalid-RSSI compatibility.

Advertising monitor tests should add multiple monitored devices/handles, deliver first and subsequent advertisements, verify one handle-specific found event per monitor until reset, verify handle `0` fallback, verify normal device-found suppression in monitor-only scanning, and verify `MGMT_EV_ADV_MONITOR_DEVICE_LOST` only for previously notified devices.

Mesh tests should configure no AD type filter, one AD type, and several AD types; feed matching and nonmatching advertising/scan-response payloads; verify `instant` propagation; and ensure mesh events are emitted independently of normal discovery gating.

Remote-name tests should verify complete-name EIR construction, failed-name flagging, address type conversion for BR/EDR and LE callers, and event sizing when name is absent.

Discovery state tests should transition through `DISCOVERY_STARTING`, `DISCOVERY_FINDING`, `DISCOVERY_STOPPING`, and `DISCOVERY_STOPPED` and assert `MGMT_EV_DISCOVERING` values and `type` fields.

Suspend/resume tests should verify suspend state, wake reason, wake address/address type, and zeroed address behavior when `mgmt_resuming()` is called without an address.

Socket cleanup tests should close management sockets with no mesh sends, one mesh send, and multiple mesh sends across multiple HCI devices, then assert all socket-owned mesh transmissions receive completion without disturbing unrelated sockets.

Channel registration tests should load/unload the Bluetooth management module path and verify `mgmt_init()` registers `HCI_CHANNEL_CONTROL`, `mgmt_exit()` unregisters it, and command dispatch still uses the earlier `mgmt_handlers[]` table.

## Chunk Boundary Notes

The range begins inside the final return path of `is_filter_match()`, whose helper definitions and first RSSI checks start before line 10240. The range ends at the end of the file after `mgmt_cleanup()`. Earlier chunks contain the management command handlers, mesh command setup, advertisement monitor commands, and the `mgmt_handlers[]` table; this chunk should be merged with those for a complete per-file report.
