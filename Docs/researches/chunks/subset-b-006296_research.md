# sources/distributed-fs/ceph-client/net/wireless/nl80211.c lines 9100-18680

## Scope

This chunk covers a large middle section of `nl80211.c`, the generic netlink front end for cfg80211 wireless control operations. The covered range starts in the tail of station-add validation and includes:

- Station deletion, mesh path/MPP commands, BSS parameter changes, mesh configuration parsing, and regulatory-domain get/set helpers.
- Scan, scheduled-scan, radar-detection, channel-switch, scan-result dump, and survey dump handlers.
- MLME authentication, association, deauthentication, disassociation, connect/disconnect, IBSS, OCB, mesh join/leave, TDLS, remain-on-channel, management TX/RX registration, and bitrate/power/CQM commands.
- WoWLAN, packet coalescing, GTK rekey offload, unexpected-frame registration, client probing, beacon registration, P2P device lifecycle, NAN configuration/function/schedule APIs, vendor/testmode event and command plumbing, QoS/TID policy, BSS color change, FILS/OWE/external-auth helpers, MLO link/station operations, hardware timestamping, and the beginning of TTLM support.

The path is under a Ceph client source snapshot, but the code is Linux wireless/cfg80211 infrastructure. It does not implement CephFS behavior directly.

## Purpose

This chunk is primarily a userspace-to-driver translation layer. It accepts nl80211 generic netlink requests, validates required attributes and feature support, builds cfg80211 request structures, updates cfg80211-visible state where necessary, and calls `rdev_*()` or `cfg80211_*()` helpers that ultimately reach wireless drivers or cfg80211 core logic.

The code is defensive because nl80211 is a public ABI. Most handlers follow the same pattern: reject missing or inconsistent attributes with `-EINVAL`, reject unsupported driver operations or feature bits with `-EOPNOTSUPP`, verify interface type and connection/running state, parse nested attributes into kernel structures, then call the relevant driver operation. Several paths also send immediate netlink replies carrying cookies, BSS records, survey data, regulatory domains, power-save state, WoWLAN/coalesce configuration, FTM stats, NAN match events, or vendor/testmode payloads.

The chunk is also a state boundary for long-lived wireless control-plane configuration. It stores scheduled scan requests, power-save state, CQM RSSI config, WoWLAN triggers, coalesce rules, connection owner port IDs, NAN running/function state, critical protocol owners, beacon-registration subscribers, MLO valid-link state, and cfg80211-managed BSS references.

## Important APIs, Types, And Functions

Station and mesh path handling:

- `nl80211_del_station()` validates AP, mesh, NAN, and supported IBSS deletion contexts, parses optional MAC, management subtype, reason code, and MLO link ID, then calls `rdev_del_station()`.
- `nl80211_send_mpath()`, `nl80211_dump_mpath()`, `nl80211_get_mpath()`, `nl80211_set_mpath()`, `nl80211_new_mpath()`, and `nl80211_del_mpath()` expose mesh path table entries through `struct mpath_info` and driver `get/dump/add/change/del_mpath` operations.
- `nl80211_get_mpp()` and `nl80211_dump_mpp()` expose mesh proxy path data using the same message format as mesh paths.
- `nl80211_set_bss()` parses `struct bss_parameters` for AP/P2P GO BSS settings such as CTS protection, short preamble/slot, basic rates, AP isolation, HT opmode, P2P CTWindow/OPPPS, and MLO link ID.
- `nl80211_get_mesh_config()`, `nl80211_parse_mesh_config()`, `nl80211_parse_mesh_setup()`, `nl80211_update_mesh_config()`, `nl80211_join_mesh()`, and `nl80211_leave_mesh()` parse, dump, update, and apply mesh configuration/setup state. Policies include `nl80211_meshconf_params_policy` and `nl80211_mesh_setup_params_policy`.

Regulatory handling:

- `nl80211_req_set_reg()` handles user, cell-base, and indoor regulatory hints.
- `nl80211_reload_regdb()` requests a regulatory database reload.
- `nl80211_put_regdom()`, `nl80211_get_reg_do()`, `nl80211_send_regdom()`, and `nl80211_get_reg_dump()` serialize global and per-wiphy regulatory domains, using RCU while reading `cfg80211_regdomain` and per-wiphy regdom pointers.
- Under `CONFIG_CFG80211_CRDA_SUPPORT`, `parse_reg_rule()` and `nl80211_set_reg()` parse CRDA-supplied nested regulatory rules, allocate a flexible `struct ieee80211_regdomain`, validate alpha2/DFS/rule counts, and hand ownership to `set_regdom()`.

Scanning and survey handling:

- `validate_scan_freqs()` validates nested scan frequency lists and rejects duplicates.
- `nl80211_parse_random_mac()` parses scan/scheduled-scan random MAC and mask pairs, with a default locally administered randomization mask when no explicit attributes are present.
- `cfg80211_off_channel_oper_allowed()` checks regulatory/channel constraints for off-channel work, including radar-channel restrictions and multi-link/channel compatibility.
- `nl80211_check_scan_flags()` validates scan flags against `wiphy->features` and extended feature bits, and parses random MAC options.
- `nl80211_trigger_scan()` builds a single allocation containing `struct cfg80211_scan_request_int`, channel pointers, SSIDs, and IE data; filters disabled/disallowed channels; checks off-channel constraints; stores `rdev->scan_req`; calls `cfg80211_scan()`; and sends a scan-start event on success.
- `nl80211_abort_scan()` calls driver abort support when a scan is pending and not already completing.
- `nl80211_parse_sched_scan_plans()`, `nl80211_parse_sched_scan()`, `nl80211_start_sched_scan()`, and `nl80211_stop_sched_scan()` parse scheduled scan plans, SSIDs, match sets, RSSI thresholds, relative RSSI, randomization, delay, and request IDs, then add or remove requests from the cfg80211 scheduled-scan list.
- `nl80211_send_bss()` and `nl80211_dump_scan()` serialize BSS records, including IEs under RCU, signal fields, current association/IBSS status, MLO link metadata, use-for flags, and cannot-use reasons.
- `nl80211_send_survey()` and `nl80211_dump_survey()` serialize per-channel or radio survey data, optionally including radio-wide stats.

DFS and channel changes:

- `nl80211_start_radar_detection()` validates interface type, DFS region, chandef, CAC usability, background radar flag, beaconing state, DFS offload, and driver support; then starts CAC, records CAC state in the relevant AP/IBSS/mesh link state, and marks the chandef CAC-active.
- `nl80211_notify_radar_detection()` lets userspace report radar for a DFS chandef, updates DFS state to unavailable, schedules channel updates, and queues propagation to other radios.
- `nl80211_parse_counter_offsets()` validates CSA/color countdown offsets against IE buffers and count values.
- `nl80211_channel_switch()` parses AP/IBSS/mesh channel switch requests, including replacement beacons, nested CSA IEs, countdown offsets, DFS handling, optional unsolicited broadcast probe response, MLO link ID, and cleanup of parsed MBSSID/RNR buffers.
- `nl80211_color_change()` mirrors channel-switch-style validation for AP BSS color changes, including beacon/color-change beacon data, countdown offsets, optional probe-response offsets, unsolicited broadcast probe response, and driver `color_change`.

MLME, connection, and security:

- `nl80211_authenticate()` validates auth attributes, WEP key constraints, cipher support, auth type, SAE/FILS/EPPKE/802.1X auth data requirements, optional MLO link/MLO address, resolves a target BSS, calls `cfg80211_mlme_auth()`, and releases the BSS reference.
- `validate_pae_over_nl80211()` enforces socket ownership, driver support, and `NL80211_EXT_FEATURE_CONTROL_PORT_OVER_NL80211`.
- `nl80211_crypto_settings()` parses pairwise/group ciphers, WPA versions, AKM suites, control-port settings, PMK, SAE password, and SAE PWE settings into `struct cfg80211_crypto_settings`.
- `nl80211_assoc_bss()`, `nl80211_process_links()`, and `nl80211_associate()` handle legacy and MLO association. They resolve per-link BSS references, reject unsupported MLO combinations, validate capability overrides, parse crypto, call `cfg80211_mlme_assoc()`, report per-link errors, and release all BSS references.
- `nl80211_deauthenticate()`, `nl80211_disassociate()`, and `nl80211_disconnect()` validate ownership, reason codes, interface type, and driver support before calling cfg80211 MLME disconnect primitives.
- `nl80211_connect()` parses high-level connect requests, including auth type, privacy, crypto, BSSID/hints, frequency/hints, IEs, MFP, cached keys, HT/VHT/HE/EHT/UHR disable/capability controls, RRM, PBSS, BSS selection, FILS ERP offload, external-auth support, MLO support, and connection ownership.
- `nl80211_update_connect_params()` updates association IEs, FILS ERP info, and auth type for an existing connection.
- `nl80211_set_pmksa()`, `nl80211_del_pmksa()`, and `nl80211_flush_pmksa()` manage PMKSA caches for station/P2P client and supported AP/P2P GO caching cases.
- `nl80211_set_pmk()`, `nl80211_del_pmk()`, `nl80211_external_auth()`, `nl80211_tx_control_port()`, `nl80211_update_owe_info()`, and `nl80211_set_fils_aad()` implement PMK installation/removal, external auth result reporting, control-port frame TX, OWE update, and FILS AAD setup.

IBSS, OCB, TDLS, management, and QoS:

- `nl80211_join_ibss()` parses IBSS SSID, beacon interval, BSSID, IEs, chandef, regulatory beacon permission, channel-width feature support, basic rates, HT caps, multicast rate, cached keys, control-port-over-nl80211, DFS handling, and connection ownership.
- `nl80211_leave_ibss()`, `nl80211_join_ocb()`, and `nl80211_leave_ocb()` delegate IBSS/OCB lifecycle to cfg80211.
- `nl80211_parse_mcast_rate()` and `nl80211_set_mcast_rate()` translate a legacy bitrate value into per-band rate table indexes for IBSS, mesh, and OCB.
- `nl80211_tdls_mgmt()`, `nl80211_tdls_oper()`, `nl80211_tdls_channel_switch()`, and `nl80211_tdls_cancel_channel_switch()` validate TDLS feature bits and interface types, parse peers/action data/chandefs, reject DFS and invalid wide-channel cases, and call driver TDLS operations.
- `nl80211_remain_on_channel()` and `nl80211_cancel_remain_on_channel()` validate duration, off-channel constraints, create a cookie reply, and call driver remain/cancel operations.
- `nl80211_register_mgmt()`, `nl80211_tx_mgmt()`, and `nl80211_tx_mgmt_cancel_wait()` register management frame matches and transmit/cancel management frames, with special handling for P2P device and secure/userspace NAN cases.
- `nl80211_set_tx_bitrate_mask()`, `nl80211_set_qos_map()`, `nl80211_add_tx_ts()`, `nl80211_del_tx_ts()`, `parse_tid_conf()`, and `nl80211_set_tid_config()` parse rate/QoS/TID policy requests and enforce driver-advertised support masks.
- `nl80211_set_power_save()` and `nl80211_get_power_save()` store and report `wdev->ps`.
- `nl80211_set_cqm_txe()`, `cfg80211_cqm_rssi_update()`, `nl80211_set_cqm_rssi()`, and `nl80211_set_cqm()` implement connection quality monitor TX error and RSSI threshold configuration, including RCU replacement of `wdev->cqm_config`.

WoWLAN, coalesce, rekey, and P2P/NAN:

- `nl80211_send_wowlan_patterns()`, `nl80211_send_wowlan_tcp()`, `nl80211_send_wowlan_nd()`, and `nl80211_get_wowlan()` dump current wake-on-wireless triggers.
- `nl80211_parse_wowlan_tcp()`, `nl80211_parse_wowlan_nd()`, and `nl80211_set_wowlan()` parse and install wake triggers for any/disconnect/magic/GTK/EAP/4-way/rfkill/pattern/TCP/net-detect modes. TCP wake can allocate a kernel TCP socket and source port under `CONFIG_INET`.
- `nl80211_send_coalesce_rules()`, `nl80211_get_coalesce()`, `cfg80211_free_coalesce()`, `nl80211_parse_coalesce_rule()`, and `nl80211_set_coalesce()` dump, parse, install, and free packet coalescing rule state.
- `nl80211_set_rekey_data()` validates KEK/KCK/replay counter lengths, including extended KCK/KEK feature flags, and calls driver GTK rekey-data setup.
- `nl80211_register_unexpected_frame()`, `nl80211_probe_client()`, `nl80211_register_beacons()`, `nl80211_start_p2p_device()`, and `nl80211_stop_p2p_device()` manage AP/P2P/NAN unexpected-frame ownership, AP client probing, OBSS beacon subscribers, and P2P device running state.
- `nl80211_parse_nan_conf()`, `nl80211_start_nan()`, `nl80211_stop_nan()`, `nl80211_nan_add_func()`, `nl80211_nan_del_func()`, `nl80211_nan_change_config()`, `cfg80211_nan_match()`, `cfg80211_nan_func_terminated()`, `cfg80211_nan_sched_update_done()`, `nl80211_nan_set_peer_sched()`, and `nl80211_nan_set_local_sched()` implement NAN startup, function management, notifications, and schedule control.
- NAN helpers such as `nl80211_get_nan_channel()`, `nl80211_parse_nan_band_config()`, `validate_nan_filter()`, `handle_nan_filter()`, `nl80211_parse_nan_channel()`, `nl80211_parse_nan_schedule()`, `nl80211_parse_nan_peer_map()`, `nl80211_nan_validate_map_pair()`, and `nl80211_nan_is_sched_empty()` enforce regulatory, band, NSS, schedule, and peer-map constraints.

Vendor/testmode, MLO, and late chunk operations:

- `__cfg80211_alloc_vendor_skb()`, `__cfg80211_alloc_event_skb()`, `__cfg80211_send_event_skb()`, `__cfg80211_alloc_reply_skb()`, `cfg80211_vendor_cmd_reply()`, and `cfg80211_vendor_cmd_get_sender()` provide exported helpers for vendor/testmode replies and multicast/unicast events.
- `nl80211_testmode_do()` and `nl80211_testmode_dump()` exist under `CONFIG_NL80211_TESTMODE` and delegate opaque test data to driver testmode hooks.
- `nl80211_vendor_check_policy()`, `nl80211_vendor_cmd()`, `nl80211_prepare_vendor_dump()`, and `nl80211_vendor_cmd_dump()` find vendor commands by vendor/subcommand, enforce command flags and nested/raw policy expectations, and call vendor `doit`/`dumpit`.
- `nl80211_wiphy_netns()` moves a wiphy to another net namespace after checking `CAP_NET_ADMIN` in the target user namespace.
- `nl80211_get_protocol_features()`, `nl80211_update_ft_ies()`, `nl80211_crit_protocol_start()`, and `nl80211_crit_protocol_stop()` expose split-wiphy-dump support, FT IE updates, and critical-protocol protection ownership.
- `nl80211_get_ftm_responder_stats()` dumps AP FTM responder stats.
- `nl80211_probe_mesh_link()` validates an Ethernet probe frame and station presence before driver mesh-link probing.
- `nl80211_add_link()`, `nl80211_remove_link()`, `nl80211_add_mod_link_station()`, `nl80211_add_link_station()`, `nl80211_modify_link_station()`, and `nl80211_remove_link_station()` handle AP MLO link and per-link station operations.
- `nl80211_set_hw_timestamp()` configures per-peer or all-peer hardware timestamping when advertised.
- The chunk ends just after the start of `nl80211_set_ttlm()`, which validates station/P2P client connection state and parses MLO TTLM uplink/downlink bitmaps before calling `rdev_set_ttlm()`. Its closing return lies immediately after the requested line range.

## Control Flow

Most handlers are single netlink request paths. The generic nl80211 dispatch layer, defined later in the file, has already selected and locked the required `wiphy`, `wireless_dev`, or `net_device` according to internal flags. Inside each handler, control generally moves through validation, parsing, operation dispatch, and local state update.

Mesh path dumps use netlink dump cursors. `nl80211_dump_mpath()` and `nl80211_dump_mpp()` call `nl80211_prepare_wdev_dump()`, check that the target interface is mesh, then repeatedly call the driver dump operation with `path_idx`. They stop on `-ENOENT`, update `cb->args[2]`, and return the amount of data placed in the SKB. Message construction is centralized in `nl80211_send_mpath()`.

Regulatory get control flow uses RTNL plus RCU. Single get allocates a reply, optionally finds a wiphy, enters RCU, selects the private or global regdomain, serializes it with `nl80211_put_regdom()`, exits RCU/RTNL, and replies. Dump mode emits the global domain as index 0 and then per-wiphy domains while tracking the current index in `cb->args[2]`.

Scan start builds a variable-size request in one allocation. It chooses user-specified frequencies or all supported channels, counts SSIDs, validates IE length, places SSIDs and IEs behind the request structure, filters disabled/disallowed/no-primary channels, checks each selected channel for off-channel permission or current-subchannel compatibility, parses rates and measurement duration, checks scan flags and random MAC settings, sets the BSSID semantics, stores the request in `rdev->scan_req`, and calls `cfg80211_scan()`. On failure it clears `rdev->scan_req` and frees the allocation; on success cfg80211 owns the request and the netdev reference is held.

Scheduled scan parsing is similar but more complex. `nl80211_parse_sched_scan()` counts channels, SSIDs, match sets, and scan plans; handles backward compatibility for RSSI-only match sets; validates relative RSSI support; allocates one flexible request block; fills channel, SSID, IE, match-set, scan-plan, randomization, delay, and RSSI state; and returns either a request or `ERR_PTR`. `nl80211_start_sched_scan()` assigns a cookie-like request ID for multi-scheduled-scan support, calls the driver, records device/wiphy/owner state, links the request into cfg80211, and sends a start notification.

DFS CAC and channel-switch paths first validate that the interface mode can legally use the operation. Radar detection parses a chandef, checks that DFS is required and usable, rejects already-running CAC and DFS offload manual start, starts the driver CAC, then records CAC metadata and the chandef in AP/IBSS/mesh state. Channel switch for AP/P2P GO requires both replacement beacon data and CSA IE data, validates countdown offsets against the CSA buffers, parses the target chandef, checks beacon permission and DFS requirements, optionally enforces a userspace `HANDLE_DFS` flag for non-AP modes, and finally calls `rdev_channel_switch()`.

Authentication and association are reference-managed around BSS lookup. Auth resolves a single BSS with `cfg80211_get_bss()`, calls `cfg80211_mlme_auth()`, then always releases the BSS. Association supports either a legacy single BSS or nested MLO link data. The MLO path rejects top-level BSSID/frequency, requires an AP MLD address, resolves per-link BSS objects through `nl80211_process_links()`, requires the association link BSS, forbids per-link elements on the association link, calls `cfg80211_mlme_assoc()`, reports the first link-specific error by marking the nested link attribute, and releases every BSS reference.

Connect is the higher-level cfg80211 connection path. It parses all attributes into `struct cfg80211_connect_params`, optionally parses cached keys, validates feature-dependent options such as MFP optional, FILS ERP offload, external auth, PBSS, BSS selection, and MLO support, then calls `cfg80211_connect()`. On success with `SOCKET_OWNER`, it records `conn_owner_nlportid` and the disconnect BSSID. Disconnect/deauth/disassoc paths check the same owner field and reject other netlink senders with `-EPERM`.

Management TX creates a reply only when userspace wants an ACK/cookie. It validates the interface type, optional off-channel duration, off-channel capability, chandef, link ID, CSA TX countdown offsets, and frame buffer. It then calls `cfg80211_mlme_mgmt_tx()` and either replies with a cookie or returns success directly for `DONT_WAIT_FOR_ACK`.

CQM RSSI configuration replaces an RCU-protected config object. The parser rejects non-negative or unsorted thresholds, detects disable requests, checks whether the range API or scalar API is supported, allocates and publishes a new `struct cfg80211_cqm_config`, programs the driver, restores the old pointer on failure, and frees the superseded config with `kfree_rcu()` on success.

WoWLAN configuration is parsed into a stack `new_triggers` object and duplicated only after all validation succeeds. Pattern masks and patterns are packed into single allocations per pattern. TCP wake setup validates payload, mask, token, and sequence constraints, may create and bind an IPv4 TCP socket, and stores the socket in the trigger. On success `nl80211_set_wowlan()` frees the previous config, installs the duplicated config, and toggles hardware wakeup if the enabled state changed. On any parse failure it explicitly frees patterns, TCP socket/config, and net-detect scheduled-scan config.

Coalesce follows the same install-after-parse pattern. Each nested rule validates delay, condition, pattern count, pattern mask length, pattern length, and packet offset. The driver is programmed before replacing `rdev->coalesce`; failed parses or driver rejection free the new tree with `cfg80211_free_coalesce()`.

NAN startup parses a default-plus-overrides `struct cfg80211_nan_conf`, validates master preference, bands, default 2.4 GHz channel, optional 5 GHz channel, cluster ID, extra/vendor attributes, band configs, scan timing, discovery beacon interval, and DW notification. Function addition allocates a `struct cfg80211_nan_func`, parses publish/subscribe/follow-up-specific attributes, service response filter, TX/RX filters, creates a reply, calls `rdev_add_nan_func()`, and replies with the assigned cookie and instance ID. On error it uses `cfg80211_free_nan_func()`.

NAN scheduling has several independent validation layers. Peer schedule parsing requires MAC and committed DW, then requires either all of sequence ID/channels/maps or none. It parses each peer channel, checks regulatory permission and compatibility with at least one local channel, parses maps, rejects duplicate map IDs, rejects compatible channels across maps, rejects overlapping slots on single-radio hardware, and ensures every provided channel is scheduled. Local schedule parsing counts channel attributes, parses mutually incompatible local channels, validates every time-slot index, treats all-unavailable schedules specially, and requires an availability blob for non-empty schedules.

Vendor command flow finds the vendor command by vendor ID and subcommand, resolves optional `wdev`, enforces `NEED_WDEV`, `NEED_NETDEV`, and `NEED_RUNNING` flags, validates vendor data as raw or nested according to the vendor command policy, sets `rdev->cur_cmd_info` while the driver callback runs, and clears it afterward. Reply helpers require `cur_cmd_info` to be present so the reply can target the original sender/sequence.

MLO AP link operations directly mutate `wdev->valid_links` and per-link MAC address before calling the driver add-link operation, then roll back those local changes if the driver rejects the add. Removal delegates to `cfg80211_remove_link()`. Link-station add/modify validates MLD address, link ID, optional link MAC, supported rates for add, HT/VHT/HE/EHT/UHR capability dependencies and sizes, 6 GHz capability, opmode notification, and station TX power before calling the corresponding driver operation.

## State And Persistence Behavior

This chunk stores no filesystem data. All persistence is in kernel memory and is scoped to net namespaces, registered wiphys, wireless devices, net devices, and driver-owned state.

Important in-memory state includes:

- `rdev->scan_req` and `rdev->scan_msg`: regular scan request/completion state. `nl80211_trigger_scan()` sets `rdev->scan_req` before `cfg80211_scan()` and clears it on error.
- `rdev->sched_scan_req_list`: scheduled scan requests installed by `cfg80211_add_sched_scan_req()` and removed through stop paths.
- `rdev->bss_list`, `rdev->bss_generation`, and `struct cfg80211_internal_bss`: scan result cache dumped by `nl80211_dump_scan()`. The BSS IE pointers are RCU-protected.
- Per-link wireless state such as `wdev->links[link_id].ap.chandef`, `beacon_interval`, `cac_started`, `cac_start_time`, `cac_time_ms`, `client.current_bss`, and `wdev->valid_links`.
- `wdev->u.ibss`, `wdev->u.mesh`, and `wdev->u.nan` mode-specific state, including IBSS current BSS, mesh ID/chandef, NAN local channels, schedule-update pending state, and NAN running state.
- `wdev->connected`, `wdev->conn_owner_nlportid`, and `wdev->disconnect_bssid`: used to gate connection/disconnection ownership for socket-owned operations.
- `wdev->ps`: userspace-visible power-save state updated only after `rdev_set_power_mgmt()` succeeds.
- `wdev->cqm_config`: RCU-protected CQM RSSI threshold configuration, replaced atomically and freed with `kfree_rcu()`.
- `rdev->wiphy.wowlan_config`: current WoWLAN trigger configuration. It owns nested pattern buffers, optional TCP wake state, optional socket, and optional net-detect scheduled-scan request.
- `rdev->coalesce`: current packet coalescing rules; each rule owns pattern arrays and packed mask/pattern buffers.
- `rdev->beacon_registrations`: list of netlink port IDs subscribed for beacon reports, protected by `beacon_registrations_lock`.
- `wdev->unexpected_nlportid`: single owner for unexpected-frame notifications on AP/P2P GO/NAN data.
- `rdev->crit_proto_nlportid`: owner of a critical protocol protection interval until stopped.
- `rdev->cur_cmd_info`: transient pointer used only while vendor/testmode callbacks run so driver helpers can send replies to the active generic netlink request.
- `rdev->opencount` and `wdev->is_running`: incremented/set when P2P device or NAN starts and decremented elsewhere when stopped.
- `cfg80211_regdomain` and per-wiphy regulatory domains: read under RCU and updated through regulatory core functions, not persisted by this file.

Memory ownership is explicit in many paths. BSS references acquired by `cfg80211_get_bss()` or `__cfg80211_get_bss()` are released with `cfg80211_put_bss()`. WoWLAN and coalesce nested allocations are freed on error and during replacement. NAN function allocations are transferred to the driver/cfg80211 on success and freed on failure. Netlink SKBs are either replied/multicast or freed on construction failure.

RCU protects several state views. Scan-result IE pointers are read under `rcu_read_lock()`. CQM config replacement uses `rcu_assign_pointer()` and `kfree_rcu()`. Scheduled scan stop reads the first request with `list_first_or_null_rcu()`. Regulatory-domain dumps traverse `cfg80211_rdev_list` under RCU.

## Dependencies And Integration Points

This code depends on the generic netlink/nl80211 framework:

- `struct genl_info`, `struct netlink_callback`, `nl80211hdr_put()`, `genlmsg_reply()`, `genlmsg_multicast_netns()`, `genlmsg_unicast()`, `nla_*()` parsers/putters, nested attribute policies, dump cursors, `NETLINK_CB()`, and extack helpers such as `NL_SET_ERR_MSG_ATTR()`.
- nl80211 UAPI attributes, commands, interface types, scan flags, CQM attributes, WoWLAN attributes, coalesce attributes, NAN attributes, TID configuration attributes, and MLO attributes defined in `include/uapi/linux/nl80211.h`.

It depends on cfg80211 core types and helpers:

- `struct cfg80211_registered_device`, `struct wireless_dev`, `struct wiphy`, `struct net_device`, `struct cfg80211_scan_request_int`, `struct cfg80211_sched_scan_request`, `struct cfg80211_bss`, `struct cfg80211_internal_bss`, `struct cfg80211_chan_def`, `struct ieee80211_channel`, and many operation-specific cfg80211 parameter structs.
- `cfg80211_scan()`, `cfg80211_add_sched_scan_req()`, `cfg80211_stop_sched_scan_req()`, `__cfg80211_stop_sched_scan()`, `cfg80211_bss_expire()`, `cfg80211_mlme_auth()`, `cfg80211_mlme_assoc()`, `cfg80211_mlme_deauth()`, `cfg80211_mlme_disassoc()`, `cfg80211_connect()`, `cfg80211_disconnect()`, `__cfg80211_join_ibss()`, `cfg80211_leave_ibss()`, `__cfg80211_join_mesh()`, `cfg80211_leave_mesh()`, `cfg80211_join_ocb()`, `cfg80211_leave_ocb()`, `cfg80211_stop_p2p_device()`, `cfg80211_stop_nan()`, `cfg80211_close_dependents()`, `cfg80211_nan_set_local_schedule()`, and related helpers.

It integrates with wireless drivers through `rdev->ops` and `rdev_*()` wrappers. Driver hooks covered here include station deletion, mesh path/proxy path operations, BSS changes, mesh config, scan/abort/scheduled scan, radar detection, channel switch, survey dump, MLME auth/assoc/deauth/disassoc, connect updates, PMKSA, TDLS, remain-on-channel, management TX, power management, CQM, WoWLAN wakeup, coalesce, rekey data, client probing, P2P/NAN lifecycle, NAN functions/schedules, vendor/testmode commands, QoS map, WMM admission, TDLS channel switch, multicast-to-unicast, PMK, external auth, control-port TX, FTM stats, OWE, mesh link probe, TID config, color change, MLO link/station management, hardware timestamping, and TTLM.

It integrates with regulatory and DFS subsystems through `regulatory_hint_user()`, `regulatory_hint_indoor()`, `reg_reload_regdb()`, `reg_get_dfs_region()`, `cfg80211_chandef_dfs_required()`, `cfg80211_chandef_dfs_usable()`, `cfg80211_set_cac_state()`, `cfg80211_set_dfs_state()`, `cfg80211_sched_dfs_chan_update()`, `regulatory_pre_cac_allowed()`, `cfg80211_reg_can_beacon()`, and `cfg80211_reg_can_beacon_relax()`.

It integrates with net namespace management through `nl80211_wiphy_netns()`, `get_net_ns_by_pid()`, `get_net_ns_by_fd()`, `ns_capable()`, and `cfg80211_switch_netns()`.

It integrates with optional subsystems through preprocessor guards:

- `CONFIG_CFG80211_CRDA_SUPPORT` gates CRDA regulatory rule ingestion.
- `CONFIG_NL80211_TESTMODE` gates testmode command/dump support.
- `CONFIG_PM` gates WoWLAN support.
- `CONFIG_INET` affects TCP wake source port/socket allocation.

## Risks And Edge Cases

The largest risk class is accepting malformed netlink attributes and passing inconsistent structures to drivers. The code mitigates this with required-attribute checks, nested policies, explicit length checks, feature-bit checks, interface-type checks, and operation-presence checks. Any new attribute path should follow the same pattern before touching driver callbacks.

Single-allocation request layouts for scan and scheduled scan are sensitive to size and offset calculations. The code uses `struct_size()`, `array_size()`, and `size_add()`, then assigns interior pointers for SSIDs, IEs, match sets, and scan plans. Any future field or layout change must preserve alignment and avoid integer overflow or overlapping regions.

Many paths pass pointers directly into netlink attribute storage to drivers or cfg80211 helpers. These pointers are valid only for the duration of the request unless the callee copies them. Long-lived state such as WoWLAN/coalesce/NAN filters explicitly duplicates data; new persistent state must do the same.

Connection ownership is security-sensitive. `conn_owner_nlportid` prevents one userspace socket from disconnecting or changing state owned by another. New connection-affecting commands should preserve this permission model, including AP MLD/MLO reconfiguration paths.

Regulatory and DFS validation is central to correctness and legal operation. Off-channel, CAC, radar notification, channel switch, IBSS/mesh join, NAN channel, and TDLS channel-switch paths all check regulatory permission and DFS constraints. Skipping these checks would let userspace or drivers operate on disallowed channels.

MLO link ID handling is easy to get wrong. Some paths require valid link IDs during MLO, reject link IDs when not operating MLO, or translate nested link-specific BSS data. The add-link path mutates `wdev->valid_links` before driver add and must roll back on driver failure. Station/link and association paths must not allow duplicate or missing link IDs.

RCU and lifetime rules matter for BSS and CQM state. BSS IE pointers are dereferenced under RCU, BSS objects must be reference-counted around MLME operations, and CQM config replacement must restore the old pointer if driver programming fails. Incorrect ordering can cause stale pointer reads or leaked BSS references.

WoWLAN TCP wake parsing allocates a socket and source port under `CONFIG_INET`. Error paths must release the socket and free nested allocations. Port binding failures return `-EADDRINUSE`; zero source ports are only acceptable when the kernel can allocate one.

WoWLAN and coalesce pattern validation depends on mask length matching `DIV_ROUND_UP(pattern_len, 8)` and on min/max pattern/pkt-offset capability checks. A mismatch can produce out-of-bounds driver reads or misprogrammed wake/coalesce filters.

NAN schedule validation is unusually strict. Peer schedules must have all-or-none sets of sequence/channels/maps, each peer channel must be compatible with local channels, every provided channel must be scheduled, and maps cannot duplicate IDs, use compatible channels across maps, or overlap time slots on single-radio devices. Changes here can break interoperability or allow impossible schedules into firmware.

Vendor command policy handling is a trust boundary. Commands declared raw must not receive nested data, and commands with policies must receive nested data that validates against `vcmd->policy`. `rdev->cur_cmd_info` is transient and must be cleared after callbacks so exported reply helpers cannot target stale requests.

Netlink SKB construction has many `nla_put_failure` paths. Each path must either cancel the generic netlink message or free the SKB and return `-ENOBUFS`/`-EMSGSIZE`. Partial nested attributes must not be sent.

Some commands intentionally return success for no-op state transitions, such as starting an already-running P2P device, setting unchanged power-save state, or reporting radar that is already marked unavailable. Tests should distinguish no-op success from unsupported or invalid requests.

The requested line range ends in the middle of the larger file and just after the opening of `nl80211_set_ttlm()`. The handler's full body continues a few lines past the chunk and validates connected station/P2P client state plus uplink/downlink bitmap attributes before calling `rdev_set_ttlm()`.

## Test Signals

Useful tests for this chunk are mostly nl80211 integration tests, cfg80211/mac80211 selftests, driver smoke tests, and focused negative netlink tests:

- Station deletion should reject missing unsupported operations, invalid management subtype, zero reason code, bad non-MLO link IDs, invalid MLO link IDs, unsupported interface types, and unsupported IBSS deletion unless `NL80211_EXT_FEATURE_DEL_IBSS_STA` is set.
- Mesh path and MPP dumps should verify cursor progression, `-ENOENT` end-of-dump handling, mesh-only interface enforcement, and correct `MPATH_INFO_*` attributes when `pinfo->filled` bits are set.
- BSS and mesh config tests should cover strict BSS parameter support masks, P2P-only CTWindow/OPPPS handling, mesh config policy ranges, HT opmode bit masking, userspace MPM feature gating, and connected-versus-default mesh config get behavior.
- Regulatory tests should cover global versus per-wiphy get, self-managed wiphy regdom expectations, alpha2 validation, DFS region handling, maximum rule count, missing nested regulatory rule attributes, PSD rule dumps, and RCU-safe dump consistency.
- Scan tests should cover duplicate frequencies, kHz frequency feature gating, disabled/no-primary/disallowed channels, all-channel scans, max SSID/IE/rate limits, random MAC mask parsing, BSSID backward compatibility with `NL80211_ATTR_MAC`, off-channel radar restrictions, busy scan state, abort with no scan, and scan-start notification.
- Scheduled scan tests should cover legacy interval fallback, scan plan interval/iteration limits, last-plan infinite rule, RSSI-only match-set compatibility, SSID/BSSID mutual exclusion in match sets, relative RSSI feature gating, multi-scheduled-scan request IDs, owner port restrictions, and stop-by-cookie versus legacy stop.
- DFS/channel-switch tests should cover missing DFS region, non-DFS chandef rejection, unusable DFS channels, DFS offload manual CAC rejection, already-beaconing CAC rejection, CAC state recording, radar notification idempotence, AP CSA beacon requirements, countdown offset validation, and `HANDLE_DFS` requirements in non-AP modes.
- Scan-result and survey dump tests should exercise split dumps, BSS generation consistency, RCU IE serialization, associated/IBSS status, MLO link metadata, hidden/disabled channels, radio-stat inclusion, and message-size short writes.
- Auth/assoc/connect tests should cover missing core attributes, invalid WEP key length/index/cipher, unsupported auth type, required auth data for SAE/FILS/EPPKE/802.1X, MLO link/address validation, missing BSS handling, BSS reference release, capability mask dependencies, MFP/RRM/FILS/SAE/PMK feature gates, connection ownership, and per-link MLO error reporting.
- Disconnect/deauth/disassoc tests should verify `conn_owner_nlportid` enforcement, reason code zero rejection, local-state-change behavior, and station/P2P-client interface restrictions.
- IBSS/OCB/mesh tests should cover beacon interval validation, chandef and regulatory beacon checks, HT/VHT IBSS feature gates, 320 MHz IBSS rejection, basic/mcast rate parsing, cached key cleanup on failure, control-port-over-nl80211 gating, mesh user MPM interactions, and mesh leave/join ownership.
- Management and remain-on-channel tests should cover interface-type allowlists, P2P-device frequency requirements, off-channel duration min/max, off-channel feature gating, NAN secure/userspace exceptions, link ID validation, CSA TX offset validation, cookie reply behavior, and cancel-by-cookie.
- CQM tests should cover unsorted or non-negative RSSI threshold rejection, single-threshold versus range API selection, disable semantics, driver failure pointer restoration, RCU freeing, TX error rate/window limits, and station/P2P-client restrictions.
- WoWLAN and coalesce tests should cover unsupported trigger/rule capabilities, incompatible `ANY` plus regular triggers, pattern min/max/mask/offset validation, TCP token/sequence/payload bounds, source port conflicts, net-detect scheduled scan parsing, wakeup toggling, replacing old config, disabling config, and all error-path frees.
- NAN tests should cover supported-band masks, mandatory master preference, default and explicit NAN channels, 5 GHz fallback/rejection, cluster ID generation, filter duplication, publish/subscribe/follow-up required attributes, SRF bloom filter versus MAC list exclusivity, function cookie/instance replies, match/termination event unicast versus multicast, local schedule empty/deferred/blob rules, peer schedule all-or-none requirements, duplicate map IDs, channel compatibility, single-radio slot conflicts, and scheduling every channel.
- Vendor/testmode tests should cover raw versus nested vendor data policy, missing vendor identifiers, unsupported subcommands, WDEV/NETDEV/RUNNING flag enforcement, dump cursor reuse, `cur_cmd_info` scoping, reply helper warnings without active command, and multicast versus unicast event delivery.
- MLO link/station tests should cover add-link rollback on driver failure, AP-only link commands, missing/invalid link MAC, link removal with missing link ID, add/modify link-station capability dependencies including EHT/UHR, TX power parsing, and delete with required MLD address/link ID.
- Late feature tests should cover QoS map length and UP bounds, WMM admission TSID bounds and connected-state checks, TDLS channel-switch DFS/wide-channel rejection, PMK length and authenticator-address matching, control-port frame connected-state checks, FTM responder AP/beaconing requirements, mesh probe frame address validation, BSS color countdown offsets, hardware timestamp max-peer semantics, and TTLM connected station/P2P-client plus uplink/downlink attribute validation.
