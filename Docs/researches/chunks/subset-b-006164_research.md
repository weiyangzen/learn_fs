# sources/distributed-fs/ceph-client/net/bluetooth/mgmt.c lines 1-10239

## Scope

This chunk covers the first 10,239 lines of the Linux Bluetooth HCI management implementation. It starts at the file header, command/event tables, status conversion helpers, controller-index queries, settings computation, and management command handlers. It continues through power, discoverability, connectability, BR/EDR, LE, mesh, security, pairing, OOB data, discovery, device lists, privacy/key loading, connection info, advertising monitor, and legacy/extended advertising commands. The range also includes the management handler table and many HCI-to-management event emitters up through the start of discovery result filtering (`is_filter_match`). The remainder of discovery result processing and module/channel teardown is outside this chunk.

## Purpose

`mgmt.c` implements the kernel-side Bluetooth management socket control plane for HCI controllers. User space sends management opcodes over `HCI_CHANNEL_CONTROL`; this file validates each request, maps it to controller state mutations and HCI commands, tracks asynchronous completions with `struct mgmt_pending_cmd`, and emits management command-complete/status replies plus asynchronous events.

The code is the central integration point between BlueZ-style management protocol ABI structures from `<net/bluetooth/mgmt.h>` and kernel controller internals from `hci_core`, SMP, EIR helpers, Microsoft/AOSP vendor extensions, ISO sockets, and advertising monitor support. Most operations are per-controller and guarded by `hci_dev_lock(hdev)`, while HCI transactions are queued through command-sync helpers and completed later on callback paths.

## Command and Event Surface

- `MGMT_VERSION` and `MGMT_REVISION` identify management protocol version 1 revision 23.
- `mgmt_commands[]` and `mgmt_events[]` enumerate the trusted control-plane ABI visible to management clients. The chunk includes handlers for classic settings, discovery, pairing, key loading, privacy, controller configuration, advertising, advertising monitors, experimental features, mesh operations, and raw synchronous HCI command passthrough.
- `mgmt_untrusted_commands[]` and `mgmt_untrusted_events[]` restrict untrusted sockets to read-only discovery/introspection operations and selected passive events.
- `mgmt_status_table[]`, `mgmt_errno_status()`, and `mgmt_status()` translate HCI status codes and Linux errnos into management status values. This translation is used consistently by async completions, command-status replies, and event paths.
- `mgmt_handlers[]` is the command dispatch table. Each entry binds an opcode index to a handler, fixed minimum payload size, and flags such as `HCI_MGMT_VAR_LEN`, `HCI_MGMT_NO_HDEV`, `HCI_MGMT_UNTRUSTED`, `HCI_MGMT_UNCONFIGURED`, and `HCI_MGMT_HDEV_OPTIONAL`.

## Important Helpers and State Mapping

- Event wrappers `mgmt_index_event()`, `mgmt_limited_event()`, `mgmt_event()`, and `mgmt_event_skb()` centralize `mgmt_send_event*()` calls on `HCI_CHANNEL_CONTROL` and apply trusted/listener flags or a socket to skip.
- `le_addr_type()` maps management address types (`BDADDR_LE_PUBLIC`, `BDADDR_LE_RANDOM`) to internal HCI LE address encodings.
- `get_supported_settings()`, `get_current_settings()`, `get_supported_phys()`, `get_selected_phys()`, and `get_configurable_phys()` project `struct hci_dev` feature bits, quirks, packet-type masks, LE PHY defaults, and ISO/PAST/LL-privacy capabilities into management settings/PHY bitmasks.
- `is_configured()` and `get_missing_options()` define whether externally configured or invalid-address controllers should be exposed as configured or unconfigured indexes.
- `pending_find()`, `pending_eir_or_class()`, `settings_rsp()`, `cmd_status_rsp()`, `cmd_complete_rsp()`, `generic_cmd_complete()`, and `addr_cmd_complete()` implement common pending-command lookup, serialization, and reply behavior.
- Delayed work handlers `discov_off()`, `service_cache_off()`, `rpa_expired()`, and `mesh_send_done()` mutate timed state and enqueue HCI command-sync work after timeouts.

## Controller Discovery and Information APIs

The top-level read handlers provide management clients with global and per-controller metadata:

- `read_version()` and `read_commands()` return protocol revision plus command/event availability. Trusted sockets get the full tables; untrusted sockets receive restricted tables.
- `read_index_list()`, `read_unconf_index_list()`, and `read_ext_index_list()` walk `hci_dev_list` under `hci_dev_list_lock`, skip setup/config/user-channel/raw-only devices, and report configured, unconfigured, or extended typed indexes. Calling `read_ext_index_list()` changes per-socket event subscription flags so extended index events replace legacy configured/unconfigured index events.
- `read_config_info()` reports manufacturer, supported configuration options, and missing options for unconfigured controllers.
- `read_controller_info()` and `read_ext_controller_info()` return address, version, manufacturer, settings, class, name, and EIR-like extended info. Extended info subscription disables legacy class/name events in favor of `MGMT_EV_EXT_INFO_CHANGED`.
- `read_controller_cap()` exposes security capabilities, encryption key-size support, and LE TX power range where available.

## Power and Settings Control Flow

Most setting handlers follow the same pattern: validate mode values and capability gates, take `hci_dev_lock()`, reject conflicting pending commands, either update state directly when powered off/no HCI work is needed or allocate `mgmt_pending_cmd`, enqueue HCI command-sync work, and finish in a completion callback.

- `set_powered()` serializes `MGMT_OP_SET_POWERED`, rejects duplicate or busy power-down requests, uses `hci_cmd_sync_submit()` for power-on because the device may not be running, and cancels command-sync work before power-off. Completion restarts LE actions and passive scans on power-on and defers power-off settings events to lower close paths.
- `set_discoverable()` validates general/limited modes and timeout rules, requires connectable mode, rejects paused advertising, updates powered-off flags directly, or enqueues `hci_update_discoverable_sync()`. `discov_off()` clears discoverable flags after timeout and sends new-settings events.
- `set_connectable()` updates powered-off state directly or enqueues `hci_update_connectable_sync()`. Disabling connectable also clears discoverable and limited-discoverable state.
- `set_bondable()`, `set_link_security()`, `set_ssp()`, `set_le()`, `set_bredr()`, `set_secure_conn()`, `set_debug_keys()`, `set_privacy()`, `set_wideband_speech()`, `set_static_address()`, `set_scan_params()`, `set_fast_connectable()`, `set_external_config()`, and `set_public_address()` each manipulate specific `hdev` flags or stored fields, with powered-state restrictions where HCI or identity semantics require it.
- `mgmt_new_settings()` and internal `new_settings()` emit `MGMT_EV_NEW_SETTINGS` to listeners that requested setting events.

## Names, Class, UUIDs, and EIR State

- `add_uuid()`, `remove_uuid()`, and `set_dev_class()` serialize against other EIR/class-changing commands with `pending_eir_or_class()`, update `hdev->uuids`, class fields, or service-cache flags, then enqueue class/EIR refresh operations.
- `enable_service_cache()` delays EIR/class refresh by `CACHE_TIMEOUT` when removing all UUIDs on a powered controller.
- `set_local_name()` updates `hdev->short_name` and `hdev->dev_name`, emits legacy and extended info events when powered off, or enqueues HCI name/EIR/scan-response updates when powered. Completion may expire advertising instances that manage local name data.
- `set_appearance()` changes `hdev->appearance`, schedules advertising expiration when needed, and emits extended info changes.
- `set_device_id()` stores Device ID source/vendor/product/version and queues EIR refresh.

## Pairing, Keys, Privacy, and OOB Data

The chunk owns a large part of management security state transfer:

- `load_link_keys()`, `load_long_term_keys()`, and `load_irks()` clear existing key stores and load user-provided keys into HCI/SMP stores after strict length/count checks. Blocked keys are skipped, invalid address/key encodings are rejected or ignored depending on command semantics.
- `set_blocked_keys()` replaces `hdev->blocked_keys` with RCU-listed blocked key entries.
- `unpair_device()` removes BR/EDR link keys or cancels/removes LE SMP pairing, updates LE connection parameters, optionally aborts live connections, and emits `MGMT_EV_DEVICE_UNPAIRED`.
- `pair_device()` initiates BR/EDR ACL or LE scan connection, installs connection callbacks, stores the pending command in `conn->*cfm_cb` flow, and completes only when security/pairing reaches the right point. `cancel_pair_device()` unwinds that pending command and removes created pairing material.
- `pin_code_reply()`, `pin_code_neg_reply()`, `user_confirm_reply()`, `user_confirm_neg_reply()`, `user_passkey_reply()`, and `user_passkey_neg_reply()` bridge management pairing replies into HCI or SMP operations.
- `read_local_oob_data()`, `add_remote_oob_data()`, `remove_remote_oob_data()`, and `read_local_oob_ext_data()` handle BR/EDR SSP and LE Secure Connections OOB material. Extended OOB generation builds EIR payloads, rejects LE OOB reads under privacy because the active RPA is not readily available, and emits `MGMT_EV_LOCAL_OOB_DATA_UPDATED` for subscribed sockets.
- Event emitters `mgmt_new_link_key()`, `mgmt_new_ltk()`, `mgmt_new_irk()`, `mgmt_new_csrk()`, `mgmt_auth_failed()`, and pairing request/complete functions convert internal key/security events into management events and replies.

## Discovery and Filtering

- `start_discovery_internal()` validates discovery type, powered state, current discovery state, periodic inquiry, and pause state, clears old filters, records type/limited mode, enqueues `hci_start_discovery_sync()`, and marks state as `DISCOVERY_STARTING`.
- `start_service_discovery()` adds variable-length UUID filter validation, stores RSSI and UUID filter state in `hdev->discovery`, and starts discovery with result filtering enabled.
- `stop_discovery()` validates active discovery type, enqueues `hci_stop_discovery_sync()`, and marks state as `DISCOVERY_STOPPING`.
- `confirm_name()` updates inquiry-cache name resolution state while discovery is active.
- `has_uuid()`, `eir_has_uuids()`, and the beginning of `is_filter_match()` implement result-filter helpers. This chunk covers UUID parsing for 16-, 32-, and 128-bit EIR UUID fields and the RSSI-threshold check; later matching logic continues outside the requested range.

## Device Lists, Connection Parameters, and Connection Info

- `block_device()` and `unblock_device()` mutate `hdev->reject_list` and emit block/unblock events.
- `add_device()` and `remove_device()` manage BR/EDR accept-list entries and LE `hci_conn_params`, including auto-connect modes, passive-scan refresh, identity-address enforcement, and device added/removed events.
- `get_device_flags()` and `set_device_flags()` read and write per-device connection flags from BR/EDR accept-list entries or LE connection params, emitting `MGMT_EV_DEVICE_FLAGS_CHANGED`. A source comment notes `hci_dev_lock()` probably should be taken earlier around `conn_flags`, making this an explicit concurrency concern.
- `load_conn_param()` bulk-loads LE connection parameter preferences, clears disabled params when appropriate, validates interval/latency/timeout, and can queue a connection update for an already-connected central link.
- `get_connections()` reports management-connected ACL/LE/BIS links and filters out non-management or SCO/ESCO link entries.
- `disconnect()` and `unpair_device()` use command-sync abort flows rather than relying on immediate HCI command success.
- `get_conn_info()` caches RSSI/TX-power/max-TX-power in `struct hci_conn` and refreshes them after a randomized age interval. `get_clock_info()` reads local and piconet clock data for BR/EDR links.
- `mgmt_device_connected()`, `mgmt_device_disconnected()`, `mgmt_connect_failed()`, `mgmt_disconnect_failed()`, and `mgmt_powering_down()` translate connection lifecycle changes into management events and pending-command completions.

## Advertising, Mesh, and Monitor APIs

- Legacy `set_advertising()` toggles instance 0 advertising. It handles powered-off or busy scan/mesh/link cases by changing flags and replying without HCI commands; otherwise it updates advertising data and starts/stops advertising asynchronously.
- `read_adv_features()`, `get_supported_adv_flags()`, `get_adv_size_info()`, `tlv_data_max_len()`, `tlv_data_is_valid()`, and related helpers describe available advertising features and validate caller-provided advertising/scan-response TLV data. Managed flags, TX power, local name, and appearance cannot also appear in raw user data when requested as managed.
- `add_advertising()`, `add_ext_adv_params()`, `add_ext_adv_data()`, and `remove_advertising()` manage multi-instance advertising, including software rotation, extended advertising parameters, per-instance data, pending instance rollback, and advertising-added/removed events.
- Advertising monitors are implemented by `read_adv_mon_features()`, `add_adv_patterns_monitor()`, `add_adv_patterns_monitor_rssi()`, `remove_adv_monitor()`, and parse helpers for RSSI thresholds and pattern lists. Hardware/vendor integration goes through `msft_monitor_supported()`, `hci_add_adv_monitor()`, and `hci_remove_*_adv_monitor()`.
- Mesh support is behind `HCI_MESH_EXPERIMENTAL`. `set_mesh()` configures passive-scan mesh receiving; `mesh_features()`, `mesh_send()`, and `mesh_send_cancel()` manage limited mesh advertising-transmit handles, queue serialized sends via temporary advertising instances, and complete/cancel handles through delayed work.

## Experimental Features and Vendor Hooks

- `read_exp_features_info()` reports experimental feature UUIDs and enabled flags for debug, LE simultaneous roles, quality report, offload codecs, ISO sockets, and management mesh when compiled/supported.
- `set_exp_feature()` dispatches by UUID to feature-specific setters. Some features are global and require `MGMT_INDEX_NONE`; others require a valid controller index.
- Quality reports integrate with AOSP vendor helpers or a controller callback. Offload codec support depends on `hdev->get_data_path_id`. ISO sockets call `iso_init()`/`iso_exit()`. Mesh and LE simultaneous roles toggle `hdev` flags and emit experimental feature change events.

## Index, Power, and External Event Integration

- `mgmt_index_added()` and `mgmt_index_removed()` emit legacy configured/unconfigured and extended index events, reject raw devices, complete pending commands with `INVALID_INDEX` on removal, and cancel delayed management work.
- `mgmt_power_on()`, `__mgmt_power_off()`, and `mgmt_set_powered_failed()` reconcile pending power commands with actual HCI power transitions, emit settings events, and complete/cancel remaining pending commands with context-sensitive statuses.
- `mgmt_set_class_of_dev_complete()` and `mgmt_set_local_name_complete()` are HCI completion hooks that emit class/name and extended-info events while avoiding spurious events during power-on/power-down command flows.

## State and Persistence Behavior

The file does not write disk state. Persistence is represented as in-kernel state that management clients are expected to seed after startup and store externally when events request it:

- Stored on `struct hci_dev`: management flags, supported/current settings, UUID list, link keys, SMP LTK/IRK/CSRK lists, blocked keys, reject/accept lists, connection params, discovery filter fields, advertising instances, advertising monitor IDR/counters, mesh state, local names, appearance, static/public addresses, privacy IRK, scan intervals, Device ID, and experimental feature flags.
- Stored on `struct hci_conn`: management-connected bit, cached RSSI/TX power, connection info timestamp, pairing callbacks, security state, and pending connection-param removal flag.
- Stored on management sockets: per-socket subscription behavior, including extended index/info events, OOB data events, experimental feature events, and trusted/untrusted access flags.
- Managed through timers/workqueues: discoverable timeout, service-cache timeout, RPA expiry, advertising instance expiry, mesh send completion, and passive-scan/advertising refreshes.

## Dependencies and Integration Points

- Kernel Bluetooth core: `hci_dev`, `hci_conn`, HCI command-sync APIs, device flags, connection hash/list helpers, accept/reject lists, advertising instance helpers, discovery state helpers, and passive-scan update functions.
- Management protocol ABI: structures, opcodes, events, status values, and size constants from `<net/bluetooth/mgmt.h>`.
- SMP/security: `smp_cancel_and_remove_pairing()`, `smp_user_confirm_reply()`, `smp_generate_oob()`, LTK/IRK/CSRK stores, and security level/auth type handling.
- EIR helpers: `eir_append_*()`, local name/class/appearance encoding, UUID parsing, and advertising data validation.
- Vendor/optional features: Microsoft advertising monitor support, AOSP quality reports, ISO socket initialization, compile-time debug feature support, controller callback hooks such as `set_quality_report`, `get_data_path_id`, and `set_bdaddr`.
- Socket/event infrastructure: `mgmt_cmd_complete()`, `mgmt_cmd_status()`, `mgmt_send_event()`, `mgmt_send_event_skb()`, `hci_sock_*` flags, and `sock_hold()`/`sock_put()` around sockets captured from pending commands.

## Risks and Edge Cases

- Async state rollback is subtle. Several handlers update `hdev` flags or instance data before queued HCI work completes; failures must restore or remove state in completion paths. Advertising, BR/EDR, SSP, secure connections, and mesh send flows are especially sensitive.
- Pending-command lifetime is a recurring risk. Completion callbacks generally check `mgmt_pending_valid()` or `mgmt_pending_listed()` before dereferencing command data, but some direct HCI completion paths depend on opcode lookup rather than address matching.
- Variable-length command validation is critical. The code uses `struct_size()`, max-count checks against `U16_MAX`, and explicit expected-length comparisons for keys, IRKs, LTKs, UUID filters, advertising monitors, advertising data, and HCI command passthrough. Any missed length check would expose kernel memory risks.
- Locking is mixed between `hci_dev_lock()`, `hdev->mgmt_pending_lock`, `hci_req_sync_lock()`, RCU list updates, delayed work, and command-sync callbacks. The inline comment in `set_device_flags()` flags a possible ordering concern around reading `hdev->conn_flags` before taking `hci_dev_lock()`.
- Address-type conversion must remain exact. BR/EDR, LE public/random, identity-address checks, static-random high-bit checks, and internal HCI address type mappings are security relevant for pairing, privacy, device lists, OOB data, and key loading.
- Privacy and OOB support has explicit limitations: LE OOB extended data is rejected while privacy is enabled because the active RPA cannot be reliably returned.
- Some commands intentionally ignore invalid individual entries during bulk loads while succeeding overall, such as blocked or invalid keys. User space must rely on logs or subsequent state/events to infer skipped entries.
- Management event subscription flags alter which legacy versus extended events a socket receives, so client compatibility depends on maintaining the documented switch behavior.

## Test Signals

Useful validation signals for this chunk include:

- Management socket ABI tests that exercise trusted/untrusted command tables, handler length checks, invalid indexes, unconfigured indexes, and optional-HDEV experimental feature calls.
- Power/settings tests covering powered-off direct state changes versus powered-on HCI command-sync paths, duplicate pending command rejection, new-settings event emission, and rollback on injected HCI errors.
- Pairing/security tests for BR/EDR and LE pairing, cancellation, user confirmation/passkey responses, unpair-with-disconnect, blocked keys, key reloads, privacy modes, and OOB data generation/rejection.
- Discovery tests for regular, limited, service-filtered, and paused discovery, including RSSI/UUID filtering behavior once combined with the following chunk.
- Advertising tests for managed TLV validation, legacy instance 0 advertising, multi-instance add/remove, extended parameter/data split flow, timeout/duration handling, TX power reporting, and failure rollback.
- Advertising monitor tests for pattern count/offset/length validation, RSSI threshold parsing, add/remove events, passive scan refresh, and Microsoft monitor capability gating.
- Mesh tests under `HCI_MESH_EXPERIMENTAL` for scan parameter validation, handle exhaustion, queued sends, send completion/cancel behavior, and interaction with advertising instances.
- Race/fault-injection tests around controller unregister, power-off while commands are pending, delayed work cancellation, command-sync cancellation, and socket skip/hold semantics.
