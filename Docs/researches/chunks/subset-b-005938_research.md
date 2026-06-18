# sources/distributed-fs/ceph-client/include/net/cfg80211.h lines 7165-10751

## Scope

This chunk covers the final public API section of `include/net/cfg80211.h`. It starts with IEEE 802.11 channel/frequency conversion helpers and ends at the closing include guard after newer NAN, MLO, S1G, and incumbent-signal notification helpers.

The covered range includes:

- Channel/frequency conversion, Preferred Scanning Channel checks, radio/channel validation, response/mandatory rate helpers.
- Radiotap iterator state and parser entry points.
- Data-path helpers for 802.11 header length, 802.11-to-802.3 conversion, A-MSDU validation/splitting, tunnel encapsulation, mesh header stripping, and QoS classification.
- Information-element search, vendor/extension element matching, RNR iteration, and element defragmentation.
- Regulatory entry points and beaconing checks.
- Scan result/BSS database update, lookup, iteration, reference, and unlink helpers.
- MLME, association, connection, roaming, management-frame, control-port, station, CQM, DFS/CAC/radar, channel-switch, TDLS, WoWLAN, and critical-protocol notification APIs.
- Vendor command and testmode netlink SKB allocation/sending helpers.
- RFkill, netdevice/wireless-dev registration, extended feature flags, interface combinations, radio lookup, interface stop/shutdown helpers.
- NAN, PMSR, external authentication, OWE, BSS color, MLO reconfiguration, EPCS, debugfs locking wrappers, S1G helpers, and 6 GHz incumbent-signal notification APIs.

This is a declaration-heavy public kernel header. Most functions are implemented in cfg80211/net/wireless sources, while this chunk provides prototypes, small inline adapters, lightweight parameter structs, and macros used by wireless drivers and mac80211.

## Purpose

The purpose of this header section is to define the driver-facing cfg80211 support API: conversions and parsers that drivers can call, and notification/reporting functions that drivers use to hand asynchronous wireless events back to cfg80211 and nl80211 userspace.

The chunk forms the contract between full-MAC or soft-MAC driver code and the wireless core. It tells drivers how to:

- Convert channel numbers, frequencies, chandefs, operating classes, and S1G channel ranges.
- Populate and maintain cfg80211's scan/BSS database.
- Report authentication, association, roaming, disconnection, station, management TX/RX, control-port, radar/CAC, CQM, WoWLAN, NAN, PMSR, MLO, and regulatory events.
- Allocate correctly shaped nl80211 reply/event SKBs for vendor commands and testmode.
- Use common data path helpers when hardware does not perform 802.11/802.3 conversion.

## Important APIs, Types, and Macros

### Channel, Frequency, Rate, and Radio Helpers

`ieee80211_channel_to_khz()`, `ieee80211_channel_to_freq_khz()`, `ieee80211_channel_to_frequency()`, `ieee80211_freq_khz_to_channel()`, `ieee80211_frequency_to_channel()`, `ieee80211_get_channel_khz()`, and `ieee80211_get_channel()` convert among channel numbers, MHz/kHz frequencies, and `struct ieee80211_channel` entries in a `struct wiphy`.

`cfg80211_channel_is_psc()` identifies 6 GHz Preferred Scanning Channels by checking the band and channel modulo. `ieee80211_radio_freq_range_valid()`, `cfg80211_radio_chandef_valid()`, and `cfg80211_wdev_channel_allowed()` validate frequency/chandef/channel suitability against radio and wireless-device capabilities.

`ieee80211_get_response_rate()` and `ieee80211_mandatory_rates()` expose basic-rate and mandatory-rate selection for supported bands. Later helpers translate operating classes and chandefs through `ieee80211_operating_class_to_band()`, `ieee80211_operating_class_to_chandef()`, `ieee80211_chandef_to_operating_class()`, and `ieee80211_chandef_to_khz()`.

S1G helpers `cfg80211_s1g_get_start_freq_khz()`, `cfg80211_s1g_get_end_freq_khz()`, and `cfg80211_s1g_get_primary_sibling()` derive operating-channel edge frequencies and the sibling 1 MHz channel for 2 MHz primary S1G operation.

### Radiotap and Data-Path Helpers

`struct radiotap_align_size`, `struct ieee80211_radiotap_namespace`, `struct ieee80211_radiotap_vendor_namespaces`, and `struct ieee80211_radiotap_iterator` describe radiotap parser state. The iterator is initialized with `ieee80211_radiotap_iterator_init()` and advanced by `ieee80211_radiotap_iterator_next()`. Fields prefixed with underscores are parser-private state, while `this_arg`, `this_arg_index`, `this_arg_size`, `current_namespace`, and `is_radiotap_ns` are the caller-observable iteration result.

`rfc1042_header` and `bridge_tunnel_header` are shared encapsulation constants. `ieee80211_get_hdrlen_from_skb()`, `ieee80211_hdrlen()`, and `ieee80211_get_mesh_hdrlen()` compute 802.11 and mesh header lengths.

The conversion APIs `ieee80211_data_to_8023_exthdr()` and inline `ieee80211_data_to_8023()` convert 802.11 data frames to Ethernet framing. `ieee80211_is_valid_amsdu()` validates A-MSDU subframe lengths, including mesh-specific length variants. `ieee80211_amsdu_to_8023s()` converts a headerless A-MSDU into a list of 802.3 SKBs and consumes the input SKB. `ieee80211_get_8023_tunnel_proto()` detects RFC1042/bridge tunnel encapsulation, and `ieee80211_strip_8023_mesh_hdr()` removes mesh headers left in converted Ethernet frames.

`cfg80211_classify8021d()` maps data frames to 802.1p/1d tags, optionally using an interworking QoS map.

### Information Element Parsing

`cfg80211_find_elem_match()` is the common element search primitive. Inline wrappers adapt it to common caller expectations:

- `cfg80211_find_ie_match()`, `cfg80211_find_ie()`, and `cfg80211_find_elem()` for ordinary element IDs.
- `cfg80211_find_ext_elem()` and `cfg80211_find_ext_ie()` for `WLAN_EID_EXTENSION`.
- `cfg80211_find_vendor_elem()` and `cfg80211_find_vendor_ie()` for vendor-specific OUI/type matching.

`enum cfg80211_rnr_iter_ret` and `cfg80211_iter_rnr()` define callback-driven Reduced Neighbor Report iteration. `cfg80211_defragment_element()` copies fragmented element data into a contiguous buffer, optionally in-place. `cfg80211_merge_profile()` merges split multi-BSSID profiles, and `cfg80211_is_element_inherited()` applies non-inheritance rules. `ieee80211_ie_split_ric()`, `ieee80211_ie_split()`, and `ieee80211_fragment_element()` support IE ordering and fragmentation for generated management frames.

### Regulatory and Beaconing APIs

`regulatory_hint()`, `regulatory_set_wiphy_regd()`, `regulatory_set_wiphy_regd_sync()`, `wiphy_apply_custom_regulatory()`, `freq_reg_info()`, `reg_initiator_name()`, `regulatory_pre_cac_allowed()`, and `reg_query_regdb_wmm()` are the driver-facing regulatory APIs in this chunk.

`struct cfg80211_beaconing_check_config`, `cfg80211_reg_check_beaconing()`, `cfg80211_reg_can_beacon()`, and `cfg80211_reg_can_beacon_relax()` check whether beaconing is allowed on a chandef. The relaxed variant explicitly requires the wiphy mutex. `cfg80211_6ghz_power_type()` maps 6 GHz HE operation control/regulatory bits and station AFC-client restrictions into `enum ieee80211_ap_reg_power`.

DFS and radar integration is provided by `__cfg80211_radar_event()`, `cfg80211_radar_event()`, `cfg80211_background_radar_event()`, `cfg80211_cac_event()`, `cfg80211_background_cac_abort()`, and `cfg80211_incumbent_signal_notify()`.

### Scan and BSS Database APIs

Scan completion and scheduled scan notifications are reported by `cfg80211_scan_done()`, `cfg80211_sched_scan_results()`, `cfg80211_sched_scan_stopped()`, and `cfg80211_sched_scan_stopped_locked()`.

Drivers update the cfg80211 BSS database with `cfg80211_inform_bss_frame_data()`, inline `cfg80211_inform_bss_frame()`, `cfg80211_inform_bss_data()`, and inline `cfg80211_inform_bss()`. `enum cfg80211_bss_frame_type` records whether data came from a beacon, probe response, S1G beacon, or unknown source. Multi-BSSID helpers include `cfg80211_gen_new_bssid()`, `cfg80211_merge_profile()`, and inheritance checks.

Lookup and lifetime management are handled by `__cfg80211_get_bss()`, `cfg80211_get_bss()`, `cfg80211_get_ibss()`, `cfg80211_ref_bss()`, `cfg80211_put_bss()`, `cfg80211_unlink_bss()`, `cfg80211_bss_iter()`, `cfg80211_bss_flush()`, and `cfg80211_get_ies_channel_number()`. BSS objects returned from inform/get functions are reference-counted and must be released with `cfg80211_put_bss()` unless ownership is transferred as documented.

### MLME, Association, Connection, and Roaming

Station MLME notifications include `cfg80211_rx_mlme_mgmt()`, `cfg80211_auth_timeout()`, `cfg80211_rx_assoc_resp()`, `cfg80211_assoc_failure()`, `cfg80211_tx_mlme_mgmt()`, `cfg80211_rx_unprot_mlme_mgmt()`, `cfg80211_michael_mic_failure()`, `cfg80211_ibss_joined()`, and `cfg80211_notify_new_peer_candidate()`.

`struct cfg80211_rx_assoc_resp_data` carries association response data including MLO per-link BSS/status entries. `struct cfg80211_assoc_failure` reports association failure, optional AP MLD address, per-link BSS references, and timeout state.

Connection reporting is structured around `struct cfg80211_fils_resp_params` and `struct cfg80211_connect_resp_params`. `cfg80211_connect_done()` is the generic result path; inline `cfg80211_connect_bss()`, `cfg80211_connect_result()`, and `cfg80211_connect_timeout()` build older/simple result shapes on top of it. `struct cfg80211_roam_info` and `cfg80211_roamed()` report driver/firmware roaming, including FILS and MLO per-link data. `cfg80211_port_authorized()` reports completion of security association after connection/roam, and `cfg80211_disconnected()` reports dropped connections.

Many of these APIs document that they may sleep and require the corresponding `wdev` mutex. MLO-aware structures transfer some BSS pointer ownership to cfg80211 when passed to completion APIs.

### Management, Station, Control Port, and CQM Events

Remain-on-channel and management TX/RX notifications include `cfg80211_ready_on_channel()`, `cfg80211_remain_on_channel_expired()`, `cfg80211_tx_mgmt_expired()`, `struct cfg80211_rx_info`, `cfg80211_rx_mgmt_ext()`, inline `cfg80211_rx_mgmt_khz()`, inline `cfg80211_rx_mgmt()`, `struct cfg80211_tx_status`, `cfg80211_mgmt_tx_status_ext()`, inline `cfg80211_mgmt_tx_status()`, and `cfg80211_probe_status()`.

Station notification and statistics helpers include `cfg80211_sinfo_alloc_tid_stats()`, `cfg80211_link_sinfo_alloc_tid_stats()`, inline `cfg80211_sinfo_release_content()`, `cfg80211_new_sta()`, `cfg80211_del_sta_sinfo()`, inline `cfg80211_del_sta()`, `cfg80211_conn_failed()`, and `cfg80211_sta_opmode_change_notify()`.

Control-port and AP/P2P/NAN_DATA frame events include `cfg80211_control_port_tx_status()`, `cfg80211_rx_control_port()`, `cfg80211_rx_spurious_frame()`, and `cfg80211_rx_unexpected_4addr_frame()`.

Connection quality and security notifications include `cfg80211_cqm_rssi_notify()`, `cfg80211_cqm_pktloss_notify()`, `cfg80211_cqm_txe_notify()`, `cfg80211_cqm_beacon_loss_notify()`, `cfg80211_gtk_rekey_notify()`, and `cfg80211_pmksa_candidate_notify()`.

### Vendor Commands, Testmode, RFkill, and Netdevice Integration

Vendor command support is built around internal SKB allocators/senders `__cfg80211_alloc_reply_skb()`, `__cfg80211_alloc_event_skb()`, and `__cfg80211_send_event_skb()`. Public inline helpers `cfg80211_vendor_cmd_alloc_reply_skb()`, `cfg80211_vendor_event_alloc()`, `cfg80211_vendor_event_alloc_ucast()`, and `cfg80211_vendor_event()` wrap the netlink command/attribute choices, while `cfg80211_vendor_cmd_reply()` and `cfg80211_vendor_cmd_get_sender()` complete replies and expose the current sender port ID.

When `CONFIG_NL80211_TESTMODE` is enabled, `cfg80211_testmode_alloc_reply_skb()`, `cfg80211_testmode_reply()`, `cfg80211_testmode_alloc_event_skb()`, `cfg80211_testmode_event()`, `CFG80211_TESTMODE_CMD()`, and `CFG80211_TESTMODE_DUMP()` expose analogous testmode support. When disabled, the testmode callback macros compile away.

RFkill integration is exposed through `wiphy_rfkill_set_hw_state_reason()`, inline `wiphy_rfkill_set_hw_state()`, `wiphy_rfkill_start_polling()`, and inline `wiphy_rfkill_stop_polling()`. Netdevice/wdev registration helpers include `cfg80211_unregister_wdev()`, `cfg80211_register_netdevice()`, and inline `cfg80211_unregister_netdevice()`.

### Interface, Feature, MLO, NAN, and Miscellaneous Helpers

Interface and topology helpers include `cfg80211_check_combinations()`, `cfg80211_iter_combinations()`, `cfg80211_get_radio_idx_by_chan()`, `cfg80211_stop_link()`, inline `cfg80211_stop_iface()`, `cfg80211_shutdown_all_interfaces()`, `cfg80211_iftype_allowed()`, `wiphy_ext_feature_set()`, and `wiphy_ext_feature_isset()`.

MLO and channel-change notifications include `cfg80211_ch_switch_notify()`, `cfg80211_ch_switch_started_notify()`, `cfg80211_links_removed()`, `struct cfg80211_mlo_reconf_done_data`, `cfg80211_mlo_reconf_add_done()`, and `cfg80211_schedule_channels_check()`. BSS color events are routed through `cfg80211_bss_color_notify()` and inline wrappers for OBSS collision, color change start, abort, and completion.

NAN support includes `cfg80211_free_nan_func()`, `struct cfg80211_nan_match_params`, `cfg80211_nan_match()`, `cfg80211_nan_func_terminated()`, `cfg80211_nan_sched_update_done()`, `cfg80211_next_nan_dw_notif()`, `cfg80211_nan_cluster_joined()`, `cfg80211_nan_ulw_update()`, and `cfg80211_nan_channel_evac()`.

Other integration points include `cfg80211_send_layer2_update()`, `cfg80211_tdls_oper_request()`, `cfg80211_calculate_bitrate()`, `cfg80211_ft_event()`, `cfg80211_get_p2p_attr()`, `cfg80211_report_wowlan_wakeup()`, `cfg80211_crit_proto_stopped()`, `ieee80211_get_num_supported_channels()`, `cfg80211_get_drvinfo()`, `cfg80211_external_auth_request()`, `cfg80211_pmsr_report()`, `cfg80211_pmsr_complete()`, `cfg80211_assoc_comeback()`, `cfg80211_update_owe_info_event()`, `cfg80211_epcs_changed()`, and the optional debugfs helpers `wiphy_locked_debugfs_read()` and `wiphy_locked_debugfs_write()`.

The logging macros `wiphy_printk()`, `wiphy_err()`, `wiphy_warn()`, `wiphy_info()`, rate-limited variants, `wiphy_dbg()`, `wiphy_vdbg()`, and `wiphy_WARN()` standardize diagnostics on `wiphy->dev`.

## Control Flow and State Behavior

Most control flow in this chunk is in small inline adapters. The common pattern is to normalize older or simpler call shapes into newer structured APIs:

- MHz wrappers convert to kHz and call the kHz API.
- `cfg80211_find_ie*()` wrappers adjust IE offsets before delegating to `cfg80211_find_elem_match()`.
- `cfg80211_inform_bss_frame()` and `cfg80211_inform_bss()` build a `struct cfg80211_inform_bss` with channel/signal and call the data variants.
- `cfg80211_connect_bss()`, `cfg80211_connect_result()`, and `cfg80211_connect_timeout()` populate `struct cfg80211_connect_resp_params` and call `cfg80211_connect_done()`.
- Management RX/TX inline wrappers populate `struct cfg80211_rx_info` or `struct cfg80211_tx_status` and call extended variants.
- Radar, OBSS color, color-change, stop-interface, RFkill, vendor, and testmode wrappers call a common lower-level implementation with fixed command/event parameters.

The durable state managed by these APIs lives outside the header: cfg80211's registered wiphys/wdevs, BSS database, scan requests, connection state, scheduled scan state, regulatory state, interface combination state, station state, netlink subscribers, and driver-owned firmware/hardware state. This header records ownership and sequencing expectations rather than storing state itself.

State-sensitive behavior called out by the declarations includes:

- BSS references must be released, except where ownership explicitly moves to cfg80211 in MLO association/reconfiguration paths.
- Several MLME and channel-switch functions may sleep and require the corresponding `wdev` mutex or wiphy mutex.
- Some functions are asynchronous notifications to userspace through nl80211 and consume SKBs regardless of send success.
- `cfg80211_sched_scan_stopped_locked()` is the locked variant of scheduled scan stop notification.
- `cfg80211_stop_iface()` is explicitly asynchronous and lock-free, while netdevice registration/unregistration helpers require RTNL and wiphy mutex in cfg80211 callback contexts.
- `cfg80211_sinfo_release_content()` frees dynamically allocated per-TID and per-link station-info substructures but not the outer stack-owned `station_info`.

## Dependencies and Integration Points

This chunk depends heavily on surrounding kernel networking and wireless types:

- Core device types: `struct wiphy`, `struct wireless_dev`, `struct net_device`, `struct sk_buff`, `struct sk_buff_head`, `struct ethtool_drvinfo`, and `struct file`.
- Wireless protocol types and enums from cfg80211/nl80211/802.11 headers: `enum nl80211_band`, `enum nl80211_iftype`, `enum nl80211_commands`, `enum nl80211_attrs`, `enum nl80211_radar_event`, `enum nl80211_timeout_reason`, `enum nl80211_nan_function_type`, `struct cfg80211_chan_def`, `struct ieee80211_channel`, `struct ieee80211_supported_band`, `struct ieee80211_regdomain`, `struct ieee80211_reg_rule`, `struct element`, `struct ieee80211_mgmt`, `struct station_info`, and `struct rate_info`.
- Kernel subsystems: netlink/nl80211, regulatory database, rfkill, debugfs, rtnetlink, SKB memory management, device logging, and optional `CONFIG_NL80211_TESTMODE`/`CONFIG_CFG80211_DEBUGFS`.

Primary source-tree integration points are wireless drivers and mac80211. Drivers call these APIs after cfg80211 operations such as scan, sched_scan, auth, assoc, connect, mgmt_tx, remain_on_channel, start_ap, channel switch, TDLS, NAN, PMSR, and WoWLAN. cfg80211 then updates kernel-side wireless state and emits nl80211 events to userspace tools such as supplicants, connection managers, regulatory agents, vendor tools, and diagnostic utilities.

The data-path helpers integrate with drivers whose hardware exposes raw 802.11 frames instead of Ethernet frames, especially for monitor/injection, mesh, A-MSDU, and QoS-sensitive paths. Regulatory and beaconing helpers integrate with channel setup, AP/GO start, CSA, DFS CAC, and 6 GHz power-mode decisions.

## Risks

- Unit mismatches are a recurring hazard. This chunk has both MHz and kHz APIs; using an MHz value with a kHz API can select the wrong channel or fail regulatory/channel validation.
- BSS lifetime errors can cause leaks, stale pointers, or warnings. Returned BSS references must be released, while documented ownership-transfer fields must not be reused after completion calls.
- Locking requirements are API-specific. Calling sleepable MLME/channel APIs without the wdev mutex, or calling RTNL/wiphy-mutex helpers from the wrong context, can race cfg80211 state or deadlock.
- Notification functions often accept caller-owned frame/IE buffers. Implementations may copy data, but callers must respect each API's lifetime expectations and allocation context (`GFP_ATOMIC` versus `GFP_KERNEL`).
- IE parsing helpers intentionally only validate element bounds and minimum match lengths. Callers remain responsible for semantic validation of element contents, ordering, and required lengths.
- Vendor command/testmode SKBs must only be filled inside the intended vendor/test data attribute and are consumed by reply/event functions. Modifying their structure or reusing them after send can corrupt nl80211 messages.
- MLO per-link arrays require correct link IDs, valid link masks, and non-MLO fallback through link 0. Incorrect masks or missing per-link BSS/status data can misreport association/reconfiguration state.
- Security-sensitive event ordering matters. `cfg80211_port_authorized()` must follow connection/roam reporting; unprotected management frames should use `cfg80211_rx_unprot_mlme_mgmt()` instead of normal MLME RX; control-port frames must have protocol fields set appropriately.
- Regulatory helpers can alter or enforce channel availability. Misusing custom or self-managed regulatory APIs can enable illegal channels, disable valid channels, or make beaconing checks inconsistent with concurrent-operation relaxations.
- Interface stop/shutdown APIs can trigger callbacks into drivers. Fatal-error paths using `cfg80211_shutdown_all_interfaces()` must be prepared for reentrancy under RTNL.

## Test and Validation Signals

Useful validation is driver integration and wireless behavior coverage:

- Build coverage for cfg80211, mac80211, and drivers including `include/net/cfg80211.h`; this catches prototype, type, and inline-wrapper regressions.
- Channel conversion tests should cover 2.4/5/6 GHz, S1G, PSC detection, operating-class conversion, MHz/kHz wrappers, and radio/chandef validation.
- Radiotap and data-path tests should exercise valid and malformed radiotap headers, 802.11 header-length variants, mesh headers, RFC1042/bridge tunnel payloads, A-MSDU split/validation, and QoS classification.
- IE parser tests should include malformed/truncated IEs, extension IEs, vendor IEs, fragmented elements, RNR iteration, multi-BSSID profile merge/inheritance, and split/fragment generation.
- Scan/BSS tests should verify inform/get/put/unlink/flush/iterate behavior, reference lifetimes, multi-BSSID BSSID generation, S1G beacon handling, and scheduled scan stop/result notifications.
- Connection tests should cover auth timeout, association response/failure, connect success/failure/timeout, FILS fields, roaming, port authorization, disconnection, unprotected management frames, and MLO per-link association/reconfiguration.
- Management-frame tests should cover remain-on-channel notifications, RX subscription return values, TX status cookies/ack flags/timestamps, probe status, control-port RX/TX status, spurious frame and unexpected 4-address frame notifications.
- Regulatory/DFS tests should cover regulatory hints, self-managed regdom setting, WMM rule lookup, beaconing with and without relaxation, CAC completion/abort, radar/background radar, 6 GHz power-type fallback, and incumbent-signal bitmaps.
- Vendor/testmode tests should verify reply/event SKB allocation, sender port IDs, multicast versus unicast events, disabled `CONFIG_NL80211_TESTMODE` macro behavior, and message attribute layout.
- NAN/PMSR/MLO/6 GHz feature tests should cover NAN match/termination/schedule/DW/cluster/ULW/channel-evacuation events, PMSR report/complete lifetime, link removal/add-done events, BSS color events, EPCS changes, OWE info, and channel resource conflict handling.
