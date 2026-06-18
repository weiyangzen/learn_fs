# sources/distributed-fs/ceph-client/include/uapi/linux/nl80211.h lines 5951-8803

## Scope

This chunk covers the tail of the Linux `nl80211.h` UAPI header embedded in the Ceph client source tree. It starts in the connected-quality-monitoring attribute section and runs through the final NAN peer schedule-map definitions and include guard close.

The code in this range is almost entirely public ABI metadata: enums, fixed-size UAPI structs, compatibility macros, and constants used by cfg80211/nl80211 netlink messages. It does not implement Ceph file-system behavior directly. In this repository it matters because the Ceph client source snapshot carries kernel UAPI headers that may be compiled, analyzed, or consumed by tooling expecting Linux-compatible wireless netlink definitions.

## Purpose

`nl80211.h` defines the numeric contract between userspace and the Linux kernel's cfg80211 wireless subsystem. This chunk supplies late-file definitions for monitoring, power/rate policy, wake-on-wireless, interface limits, mesh, security offload, feature advertisement, scan behavior, NAN, fine timing measurement, HE/6GHz AP features, SAR limits, MBSSID, multi-radio metadata, and final NAN capability objects.

The most important purpose is ABI stability. Many values here are serialized as generic-netlink attribute IDs or bit positions. Applications such as `wpa_supplicant`, `hostapd`, `iw`, NetworkManager, test tools, and vendor daemons build nested netlink messages with these constants and parse kernel replies that use the same numeric values. Kernel code and userspace must therefore agree on:

- Attribute IDs for nested netlink containers.
- Bit positions in capability and feature masks.
- Fixed binary layout of packed UAPI structures.
- Units and signedness for numeric fields such as dBm, mBm, TU, kHz, nanoseconds, picoseconds, and power units.
- Validation rules such as mutually exclusive flags, required attributes, and "keep last" maxima.

## Important APIs, Types, And Constants

There are no functions in this range. The externally relevant APIs are UAPI enum values and structs used in netlink messages.

Connected-quality and traffic configuration:

- `enum nl80211_attr_cqm` defines nested connection quality monitor attributes for RSSI thresholds, hysteresis, RSSI events, packet loss, TX error rate/window settings, beacon loss, and event RSSI level.
- `enum nl80211_cqm_rssi_threshold_event` defines low/high RSSI threshold event values; the beacon-loss value is reserved and never sent.
- `enum nl80211_tx_power_setting`, `enum nl80211_tid_config`, and `enum nl80211_tx_rate_setting` define automatic, limited, fixed, enable, and disable policy selectors.
- `enum nl80211_tid_config_attr` defines per-VIF and per-peer TID configuration attributes for TID masks, override behavior, no-ack policy, retry counts, AMPDU/AMSDU/RTS-CTS controls, and TX-rate masks.

Packet pattern, WoWLAN, and coalescing support:

- `enum nl80211_packet_pattern_attr` defines packet pattern `MASK`, `PATTERN`, and `OFFSET` attributes. The mask uses bit positions per byte and matching is performed on unpacked 802.3-style MSDUs.
- `struct nl80211_pattern_support` is a packed four-`__u32` capability structure for maximum pattern count, min/max pattern length, and max packet offset.
- Compatibility macros alias old `NL80211_WOWLAN_PKTPAT_*` names to the common packet-pattern enum and support struct.
- `enum nl80211_wowlan_triggers` defines wake triggers for any activity, disconnect, magic packet, packet pattern, GTK rekey failure/support advertisement, EAP identity, 4-way handshake, rfkill release, wake packet reporting, TCP-connection wake, net detect, net-detect results, and unprotected deauth/disassoc.
- `struct nl80211_wowlan_tcp_data_seq`, `struct nl80211_wowlan_tcp_data_token`, and `struct nl80211_wowlan_tcp_data_token_feature` describe TCP keepalive payload sequence and token insertion.
- `enum nl80211_wowlan_tcp_attrs` defines source/destination IP, MAC, ports, keepalive payload, sequence/token config, interval, wake payload, and wake mask.
- `struct nl80211_coalesce_rule_support`, `enum nl80211_attr_coalesce_rule`, and `enum nl80211_coalesce_condition` describe packet coalescing capability and match/no-match rule behavior.

Interface combinations, mesh, rekey, station, and auth/security policy:

- `enum nl80211_iface_limit_attrs` and `enum nl80211_if_combination_attrs` define advertised interface-combination limits, max interface counts, channel counts, beacon-interval requirements, radar-detection widths/regions, and beacon-interval GCD constraints.
- `enum nl80211_plink_state` and `enum nl80211_plink_action` define mesh peer link finite-state values and user actions.
- `NL80211_KCK_LEN`, `NL80211_KEK_LEN`, `NL80211_KCK_EXT_LEN`, `NL80211_KEK_EXT_LEN`, `NL80211_KCK_EXT_LEN_32`, and `NL80211_REPLAY_CTR_LEN` fix byte lengths for GTK rekey offload material.
- `enum nl80211_rekey_data` defines KEK, KCK, replay counter, and AKM attributes for GTK rekey offload.
- `enum nl80211_hidden_ssid`, `enum nl80211_sta_wme_attr`, `enum nl80211_pmksa_candidate_attr`, `enum nl80211_tdls_operation`, and `enum nl80211_ap_sme_features` define AP beacon SSID hiding modes, station WME attributes, PMKSA candidate reporting, TDLS operations, and AP SME offload feature flags.
- `enum nl80211_acl_policy`, `enum nl80211_external_auth_action`, `enum nl80211_sae_pwe_mechanism`, `enum nl80211_iftype_akm_attributes`, and `enum nl80211_ap_settings_flags` define AP access-control semantics, external auth start/abort, SAE PWE mechanisms, interface-type-specific AKM suite advertisement, and AP userspace support flags.

Feature and protocol capability advertisement:

- `enum nl80211_feature_flags` is a 32-bit feature mask for socket TX status, HT IBSS, inactivity timer, regulatory hints, SAE, scan variants, AP scan, per-VIF TX power, P2P features, full AP client state, userspace MPM, active monitor, channel width changes, probe-request IEs, quiet/TPC/dynack/SMPS, WMM admission, MAC-on-create, TDLS channel switching, and scan/scheduled-scan/net-detect random MAC support.
- `enum nl80211_ext_feature_index` is an index list for extended feature bitmaps, including VHT IBSS, RRM, MU-MIMO sniffer, scan timing, BSS parent TSF, beacon-rate controls, FILS, randomized management frame TA, scheduled-scan RSSI behavior, CQM RSSI lists, device/driver 4-way and SAE offload, DFS offload, control-port-over-nl80211, ACK signal reporting, TXQs, scan privacy flags, FTM responder, PTK0 replacement safety, Extended Key ID, airtime fairness/AQL, AP PMKSA caching, VLAN offload, beacon protection, multicast management registrations, kHz scan frequencies, OCV, FILS discovery, unsolicited broadcast probe response, HE/EHT beacon rates, secure ranging, BSS color, FILS crypto offload, background radar, powered address change, preamble puncturing, secure NAN, OWE offload, DFS concurrent operation, SPP A-MSDU, EPPKE, association-frame encryption, and IEEE 802.1X authentication with auth frames.
- `enum nl80211_probe_resp_offload_support_attr` defines protocol bits for WPS, WPS2, P2P, and 802.11u probe response offload.
- `enum nl80211_protocol_features` advertises split wiphy dump support.
- `enum nl80211_crit_proto_id` and `NL80211_CRIT_PROTO_MAX_DURATION` define identifiers and maximum duration for critical-protocol protection.
- `enum nl80211_rxmgmt_flags` identifies received management frames answered by device/driver or associated with external authentication.
- `NL80211_VENDOR_ID_IS_LINUX` and `struct nl80211_vendor_cmd_info` define vendor command identity layout.

Scanning, BSS selection, regulatory, DFS, and radio behavior:

- `enum nl80211_connect_failed_reason` and `enum nl80211_timeout_reason` define connection failure and timeout reasons.
- `enum nl80211_scan_flags` defines scan controls: low priority, flush, AP scan, random MAC, FILS/OCE behavior, low-span/low-power/high-accuracy modes, random sequence numbers, minimal probe request contents, kHz frequency reporting, and colocated 6GHz scan optimization.
- `enum nl80211_smps_mode`, `enum nl80211_radar_event`, and `enum nl80211_dfs_state` define spatial multiplexing powersave modes, DFS radar/CAC events, and DFS channel state.
- `enum nl80211_sched_scan_plan` defines scheduled scan interval/iteration plans, with the last plan running indefinitely.
- `struct nl80211_bss_select_rssi_adjust` and `enum nl80211_bss_select_attr` define driver-side BSS selection preferences by RSSI, band preference, and packed RSSI adjustment.
- `enum nl80211_wiphy_radio_attrs` and `enum nl80211_wiphy_radio_freq_range` define per-radio metadata, including radio index, supported frequency ranges, interface combinations, antenna mask, RTS threshold, and kHz frequency range edges.

NAN and proximity/ranging:

- `enum nl80211_nan_function_type`, `enum nl80211_nan_publish_type`, `enum nl80211_nan_func_term_reason`, constants `NL80211_NAN_FUNC_SERVICE_ID_LEN`, `NL80211_NAN_FUNC_SERVICE_SPEC_INFO_MAX_LEN`, and `NL80211_NAN_FUNC_SRF_MAX_LEN`, and `enum nl80211_nan_func_attributes` define NAN publish/subscribe/follow-up functions and their service IDs, filters, instance IDs, TTLs, service info, and termination reasons.
- `enum nl80211_nan_srf_attributes`, `enum nl80211_nan_match_attributes`, `enum nl80211_nan_band_conf_attributes`, and `enum nl80211_nan_conf_attributes` define service response filters, match events, band-specific NAN configuration, cluster IDs, vendor elements, scan periods, discovery beacon intervals, and discovery-window notifications.
- `enum nl80211_nan_capabilities`, `enum nl80211_nan_peer_map_attrs`, and `NL80211_NAN_SCHED_NOT_AVAIL_SLOT` define NAN capability reporting and peer schedule maps.
- `enum nl80211_ftm_responder_attributes`, `enum nl80211_ftm_responder_stats`, `enum nl80211_preamble`, and the `nl80211_peer_measurement_*` enums define FTM responder config/statistics and peer measurement capability, request, response, peer, failure, and result attributes. Result units include boottime nanoseconds, AP TSF microseconds, RTT picoseconds, distance millimeters, RSSI half-dBm, and optional LCI/Civic Location payloads.

HE, 6GHz, AP advertisement, SAR, and MBSSID:

- `enum nl80211_obss_pd_attributes` and `enum nl80211_bss_color_attributes` define HE spatial reuse/OBSS packet detection and BSS color parameters.
- `enum nl80211_fils_discovery_attributes`, `NL80211_FILS_DISCOVERY_TMPL_MIN_LEN`, and `enum nl80211_unsol_bcast_probe_resp_attributes` define FILS discovery and 6GHz unsolicited broadcast probe response templates and intervals.
- `enum nl80211_sar_type`, `enum nl80211_sar_attrs`, and `enum nl80211_sar_specs_attrs` define SAR power-limit configuration and capability reporting. Power is expressed in 0.25 dBm units; frequency ranges are kHz edge values, not channel centers.
- `enum nl80211_mbssid_config_attributes` defines MBSSID/EMA capability advertisement and AP configuration attributes: max interfaces, max EMA periodicity, BSS index, transmitted interface index, EMA enable flag, and transmitted profile link ID for MLO cases.
- `enum nl80211_s1g_short_beacon_attrs` defines short beacon head/tail binary template attributes.

## Control Flow

This chunk contains no executable control flow, but it encodes the message flow of multiple nl80211 operations.

For capability discovery, userspace issues requests such as `NL80211_CMD_GET_WIPHY` and parses attributes keyed by these enums. Capability paths include feature masks, extended feature bitmaps, WoWLAN trigger support, packet-pattern support, coalescing support, interface combinations, SAR capabilities, MBSSID/EMA support, per-radio data, NAN capabilities, and peer-measurement capabilities.

For configuration, userspace builds nested netlink attributes using these constants and sends command-specific messages. Examples include `NL80211_CMD_SET_TID_CONFIG`, WoWLAN trigger setup, `NL80211_CMD_START_SCHED_SCAN`, `NL80211_CMD_CONNECT`, `NL80211_CMD_START_AP`, NAN start/change/add-function flows, FTM responder configuration, SAR spec updates, and MBSSID AP setup.

For asynchronous reporting, the kernel sends events using these same values. Examples include CQM RSSI threshold events, WoWLAN wake reasons, PMKSA candidates, connection failures, timeout reasons, DFS radar/CAC events, NAN match/termination notifications, FTM responder statistics, peer-measurement partial/final results, and BSS color or background radar events.

Several nested schemas in this chunk have type-dependent control flow:

- WoWLAN `NL80211_WOWLAN_TRIG_PKT_PATTERN` is a set of nested packet-pattern definitions for setup, a packed support struct for capability reporting, and a `u32` pattern index for wake reporting.
- WoWLAN TCP wake setup requires address/port attributes, payload, optional sequence/token insertion, interval, and wake payload/mask. Wake reporting uses separate TCP-match, connection-lost, and no-more-tokens trigger attributes.
- Scheduled scan plans form an ordered list. Every plan except the last provides an iteration count; the final plan omits iterations and runs indefinitely.
- BSS selection allows exactly one nested selector attribute in `NL80211_ATTR_BSS_SELECT`.
- Peer measurements nest by peer and by measurement type; top-level peer measurement data contains capability or peer arrays, each peer contains request/response data, and FTM-specific request or response attributes sit below the type-specific node.
- FTM response delivery may be partial. `NL80211_PMSR_RESP_ATTR_FINAL` distinguishes intermediate burst data from the last or only result.
- NAN can be either driver-offloaded discovery-engine mode or userspace discovery-engine mode, depending on `NL80211_NAN_CAPA_USERSPACE_DE`; this changes which commands should be used.

## State And Persistence Behavior

The header itself has no mutable state and no persistence. It defines compile-time constants and packed data layouts.

The state implied by the API is held elsewhere:

- cfg80211/wireless drivers persist configured WoWLAN triggers across suspend until cleared or replaced.
- TID configuration, TX power/rate policy, station WME settings, ACLs, AP SME offload flags, MBSSID settings, FILS discovery templates, unsolicited broadcast probe response templates, and SAR specs become driver or wiphy/interface state after successful netlink commands.
- Scheduled scan plans and NAN functions are long-lived kernel/driver operations that produce later events.
- DFS channel state persists in regulatory/channel state, including non-occupancy and CAC validity.
- Peer measurement and FTM responder statistics are transient or driver-maintained counters returned through netlink, not stored in this header.
- SAR `SET` semantics are explicitly replace-all: every SET operation overwrites the previous SAR configuration, skipped ranges have no userspace SAR limitation, and duplicate range indices are invalid.
- NAN cluster ID is selected at start time and ignored on later change requests because it cannot change after NAN starts.

Because this is UAPI, persistence also exists at the ABI level: once released, numeric enum values and bit positions must remain stable. The repeated `MAX`, `NUM`, `AFTER_LAST`, and "add before this" markers are part of that maintenance discipline.

## Dependencies And Integration Points

This chunk depends on standard Linux UAPI integer types from earlier included headers, including `__u8`, `__s8`, `__u16`, `__u32`, `__s32`, `__u64`, and `__s64`. It also references enums and attributes defined earlier in the same header, such as `enum nl80211_band`, `enum nl80211_chan_width`, `enum nl80211_rate_info`, `enum nl80211_if_combination_attrs`, top-level `NL80211_ATTR_*` values, and command IDs such as `NL80211_CMD_*`.

Kernel integration points are cfg80211/nl80211 policy tables, command handlers, event builders, and driver operation structs. Drivers advertise capabilities through `wiphy` fields and callbacks, then nl80211 serializes them using these constants. The comments explicitly reference driver-facing fields such as `wiphy->mbssid_max_interfaces` and `wiphy->ema_max_profile_periodicity`.

Userspace integration points include:

- `iw` and wireless diagnostics that dump wiphy capabilities, interface combinations, scan features, WoWLAN, SAR, FTM, and NAN state.
- `wpa_supplicant` and NetworkManager for scan, connect, external authentication, SAE, PMKSA, OWE/FILS/802.1X capabilities, BSS selection, and roaming behavior.
- `hostapd` for AP start, ACL policy, MBSSID/EMA, FILS discovery, unsolicited probe responses, beacon protection, SAE offload, AP PMKSA, AP-side 4-way/SAE/OWE offload, and AP SME flags.
- Vendor daemons that use `struct nl80211_vendor_cmd_info` and vendor IDs.
- Power-management tooling for WoWLAN, rekey offload, TCP wake, coalescing, and net-detect setup.
- Ranging/location tools for FTM responder statistics and peer measurement requests/results.

In this repository's Ceph-client context, these definitions are not on the primary CephFS data path. Their integration risk is mostly snapshot fidelity: code or tests that include this UAPI header need definitions consistent with the kernel/userspace ABI they target.

## Risks And Edge Cases

ABI drift is the highest risk. Reordering enum values, reusing reserved bits, changing bit positions, or modifying packed struct fields would break userspace/kernel interoperation even though C compilation might still succeed.

The packed structs must keep exact binary layout. `struct nl80211_pattern_support`, `struct nl80211_coalesce_rule_support`, and `struct nl80211_bss_select_rssi_adjust` are serialized as binary netlink payloads. Padding, alignment, signedness, or field-width mistakes can make different architectures parse different values.

Nested attribute semantics are easy to misuse. Many attributes change type depending on context: packet pattern trigger support versus configuration versus wake reporting, peer measurement capability versus request versus response, SAR SET versus capability dump, and MBSSID capability advertisement versus AP setup. Tests must validate command-specific policies, not just enum presence.

Feature gating is mandatory. Many flags in `nl80211_feature_flags` and `nl80211_ext_feature_index` are instructions to userspace about what it may request. Requesting unsupported scan flags, CQM RSSI lists, FTM options, offload modes, DFS offload assumptions, SAE/OWE offload, kHz scan reporting, or 6GHz advertisement features should be rejected cleanly.

Security-sensitive behavior is encoded here. `NL80211_EXT_FEATURE_CAN_REPLACE_PTK0` warns that rekeying PTK keys without support can leak cleartext or freeze the connection. SAE PWE mechanism selection, beacon protection, FILS crypto offload, OWE offload, association-frame encryption, IEEE 802.1X auth frames, external auth, and AP SA Query offload all require careful userspace/driver coordination.

Privacy features must be validated together. Scan random MAC, scheduled-scan random MAC, net-detect random MAC, random probe-request sequence numbers, minimal probe content, randomized management/auth/deauth TA, and powered address changes all affect trackability. Incorrect feature advertisement can cause userspace to assume privacy properties the device does not provide.

Units are varied and easy to confuse: TX power may be mBm elsewhere while SAR power uses 0.25 dBm units; scan/FILS intervals are in TU or seconds depending on attribute; frequency ranges use kHz but many scan and channel APIs use MHz; FTM RTT is picoseconds, distance is millimeters, host time is nanoseconds, AP TSF is microseconds, and RSSI can be dBm, half-dBm, or threshold-specific.

Several rules are mutually exclusive or conditional. Low-span/low-power/high-accuracy scan flags are exclusive. FTM trigger-based and non-trigger-based flags are exclusive. NAN SRF bloom filters and MAC address lists are exclusive. NAN RSSI close/middle thresholds should be configured together. Some 6GHz and NAN parameters are forbidden on specific bands. MBSSID non-transmitted profiles require transmitted-profile references and may require a link ID for MLD cases.

The chunk ends the include guard. Any later merge lane must preserve the final `#endif /* __LINUX_NL80211_H */`; duplicate or missing tail guards can affect every consumer of this UAPI header.

## Test Signals

Useful validation signals for this chunk include:

- Compile all source that includes `sources/distributed-fs/ceph-client/include/uapi/linux/nl80211.h` under the repository's supported configurations, with warnings enabled for enum redefinitions, packed struct layout issues, and missing types.
- Compare the numeric values and comments in this snapshot against the expected upstream Linux `nl80211.h` version used by the source tree. For UAPI headers, diff-based verification is often the strongest regression signal.
- Run wireless userspace netlink parser tests, if available, that decode wiphy dumps with `NL80211_ATTR_EXT_FEATURES`, interface combinations, WoWLAN support, coalescing, SAR, MBSSID, per-radio data, NAN capabilities, and peer measurement capabilities.
- Exercise netlink policy tests for nested attributes: invalid enum values, missing required fields, duplicate SAR range indices, unsupported scan flags, invalid BSS selection with multiple selectors, invalid scheduled scan plans with zero iterations or non-final missing iterations, and mutually exclusive FTM/NAN options.
- Validate packed structure sizes with build-time assertions in consumers: `nl80211_pattern_support` should be four `u32` values, `nl80211_coalesce_rule_support` should be `u32 + nl80211_pattern_support + u32`, and `nl80211_bss_select_rssi_adjust` should be two bytes.
- Test WoWLAN setup/reporting paths with magic packet, packet pattern, disconnect, GTK rekey failure, EAP identity, 4-way handshake, net detect, and TCP wake triggers. Include malformed masks, offsets beyond advertised capability, truncated wake packets, and wake packet length attributes.
- Test scan behavior for every scan flag combination that is supposed to be valid, and rejection for exclusive or unsupported combinations. Include random MAC/mask handling, kHz reporting, colocated 6GHz scan behavior, and low-span/low-power/high-accuracy mode selection.
- Test AP flows for hidden SSID modes, ACL policy, external auth support, SA Query offload support, MBSSID/EMA configuration, FILS discovery template length, unsolicited 6GHz broadcast probe response intervals, BSS color, OBSS PD, and S1G short beacon templates.
- Test peer measurement and FTM flows with capability advertisement, successful measurements, local refusal, timeout, generic failure, FTM-specific failure reasons, partial/final results, AP TSF reporting, host-time reporting, LCI/Civic Location payloads, and 64-bit padding attributes.
- Test SAR set/get behavior for at least one range, skipped ranges, zero power meaning no userspace SAR limit for a range, excessive power meaning effective removal, duplicate range rejection, and overwrite-on-each-SET semantics.
- Test NAN flows in both offloaded and userspace discovery-engine modes, including publish/subscribe/follow-up functions, SRF bloom-filter versus MAC-list exclusivity, band restrictions, immutable cluster ID after start, discovery-window notification, peer schedule maps, and `NL80211_NAN_SCHED_NOT_AVAIL_SLOT`.
