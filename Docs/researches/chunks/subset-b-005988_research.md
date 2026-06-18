# sources/distributed-fs/ceph-client/include/uapi/linux/nl80211.h lines 1-5950

## Scope

This chunk covers the first 5,950 lines of `sources/distributed-fs/ceph-client/include/uapi/linux/nl80211.h`. The file is a Linux UAPI header for the generic-netlink `nl80211` wireless configuration interface. This chunk contains the public family name and multicast groups, high-level feature documentation, the append-only command and top-level attribute ABI, compatibility aliases, constants, and many early nested attribute enums/packed structs used by cfg80211/mac80211, wireless drivers, and userspace tools such as `iw`, `wpa_supplicant`, and `hostapd`.

## Purpose

The header defines the stable numeric contract between userspace and the Linux wireless stack. It does not implement behavior directly; instead, it names commands, attributes, flags, nested attribute layouts, fixed sizes, and compatibility aliases that both kernel-side nl80211 policy code and userspace netlink encoders/decoders must agree on.

The opening comments are explicit that command and attribute order is ABI and must not be rearranged. New commands and attributes are appended before the internal `__..._AFTER_LAST` sentinels, and many old names are preserved as macros to avoid breaking source compatibility.

## Important APIs, Types, and Constants

- `NL80211_GENL_NAME` is the generic-netlink family name, `"nl80211"`.
- Multicast group names include `config`, `scan`, `regulatory`, `mlme`, `vendor`, `nan`, and `testmode`. These are integration points for async userspace subscribers.
- EDMG bounds are defined with `NL80211_EDMG_BW_CONFIG_MIN/MAX` and `NL80211_EDMG_CHANNELS_MIN/MAX`.
- The largest ABI surfaces in this chunk are `enum nl80211_commands` and `enum nl80211_attrs`; both warn that order is ABI.
- `enum nl80211_commands` defines request/response/event command IDs for wiphy, interface, key, AP/beacon, station, mesh path, regulatory, scan, MLME, connection, remain-on-channel, management-frame TX/RX, power save, CQM, WoWLAN, scheduled scan, TDLS, NAN, MLO, hardware timestamping, EPCS, and incumbent-signal events.
- `enum nl80211_attrs` defines the top-level netlink attributes used across those commands. It covers identifiers, channel definitions, key material, station/BSS/mesh data, scan filters, regulatory data, security/offload parameters, vendor payloads, NAN schedule data, MLO link data, EHT/UHR capabilities, multi-radio masks, and many feature flags.
- Compatibility macros preserve older command and attribute spellings, such as `NL80211_CMD_GET_MESH_PARAMS`, `NL80211_ATTR_SCAN_GENERATION`, `NL80211_ATTR_MESH_PARAMS`, `NL80211_ATTR_SAE_DATA`, `NL80211_FREQUENCY_ATTR_PASSIVE_SCAN`, `NL80211_RRF_PASSIVE_SCAN`, and old survey names.
- Fixed limits and wire-format sizes include `NL80211_WIPHY_NAME_MAXLEN`, `NL80211_MAX_SUPP_RATES`, `NL80211_MAX_SUPP_SELECTORS`, `NL80211_MAX_SUPP_REG_RULES`, TKIP key offsets, HT/VHT/HE/EHT capability lengths, `NL80211_MAX_NR_CIPHER_SUITES`, legacy `NL80211_MAX_NR_AKM_SUITES`, `NL80211_MIN_REMAIN_ON_CHANNEL_TIME`, and `NL80211_CQM_TXE_MAX_INTVL`.
- `struct nl80211_sta_flag_update` is a packed UAPI struct with `mask` and `set` bitmaps for station flag updates.
- `struct nl80211_txrate_vht`, `struct nl80211_txrate_he`, and `struct nl80211_txrate_eht` are fixed arrays of MCS bitmaps indexed by NSS, using 8 VHT streams, 8 HE streams, and 16 EHT streams.

## Command Surface

The command enum models nl80211 as a mixed command/event protocol:

- Object lifecycle commands operate on wiphys and virtual interfaces: get/set/new/delete wiphy, get/set/new/delete interface, and setting a wiphy netns.
- Key-management commands create, update, delete, and query keys, with MLO-specific interpretation of peer MLD addresses and per-link group keys.
- AP commands start/stop AP operation and update beacon/probe/association response templates. `NL80211_CMD_NEW_BEACON` and `NL80211_CMD_DEL_BEACON` are old aliases.
- Station commands get, add, modify, or delete station records, including VLAN movement, TDLS setup, MLD station handling, and optional deauth/disassoc indication parameters.
- Scan commands trigger, abort, dump, and report normal and scheduled scans. Scheduled scans support plans, delay, multi-request support, and driver stop notifications.
- Regulatory commands get/set/request domains and notify about regulatory changes, beacon hints, wiphy-specific regulatory changes, DFS radar events, and 6 GHz incumbent signal detection.
- MLME and connection commands cover authenticate, associate, deauthenticate, disassociate, connect, roam, disconnect, external auth, association comeback, MLO association reconfiguration, and port authorization.
- Management-frame registration and TX/RX commands allow userspace handling of selected frame classes. Registrations are socket-bound and may interact with multicast registration support.
- Off-channel commands return cookies for remain-on-channel and frame TX status matching.
- Mesh, OCB, P2P, TDLS, NAN, FTM/peer measurement, QoS map, TID config, SAR, BSS color change, MBSSID/RNR, link add/remove, hardware timestamping, and NAN schedule commands define feature-specific control planes.
- Vendor commands use `NL80211_ATTR_VENDOR_ID`, `NL80211_ATTR_VENDOR_SUBCMD`, and `NL80211_ATTR_VENDOR_DATA`, plus wiphy-advertised vendor command/event descriptions.

Several commands are intentionally dual-use: a userspace request and a kernel event share the same ID, with semantics distinguished by direction and attributes. Examples include authentication/association commands, `NL80211_CMD_FRAME`, `NL80211_CMD_SET_WOWLAN` wake reports, `NL80211_CMD_TDLS_OPER`, `NL80211_CMD_EXTERNAL_AUTH`, control-port frames, and NAN deletion/schedule update notifications.

## Attribute Surface

The top-level attribute enum is the central wire schema. Important groups in this chunk include:

- Device and interface selectors: `WIPHY`, `WIPHY_NAME`, `IFINDEX`, `IFNAME`, `IFTYPE`, `WDEV`, `WIPHY_RADIO_INDEX`, and `VIF_RADIO_MASK`.
- Channel and radio configuration: `WIPHY_FREQ`, `WIPHY_FREQ_OFFSET`, `CHANNEL_WIDTH`, `CENTER_FREQ1/2`, `CENTER_FREQ1_OFFSET`, `SCAN_FREQ_KHZ`, `PUNCT_BITMAP`, DFS/radar/background-radar fields, and radio combination attributes.
- Security and authentication: key attributes, cipher suites, WPA versions, AKM suites, PMK/PMKID/PMK lifetime and reauth threshold, SAE password/PWE, FILS ERP/AAD/KEK/nonces/cache ID, MFP, control-port options, transition-disable bitmap, and external-auth support/action.
- AP and BSS configuration: beacon head/tail, DTIM, hidden SSID, probe/assoc response IEs, ACL policy/MAC list, AP settings flags, MBSSID config/elements, EMA RNR elements, BSS parameters, S1G long/short beacon fields, and unsolicited/FILS discovery templates.
- Station and link state: station flags, station info, link IDs, MLD address, MLO links, removed links, TTLM uplink/downlink maps, EML/MLD capabilities, SPP A-MSDU, EPCS, EPP peer, and association MLD extended capabilities/operations.
- Scan and BSS selection: SSID, BSSID, scan SSIDs/frequencies, match sets, scan flags, BSS selection, relative RSSI and RSSI adjustment, scan TSF metadata, supported selectors, and BSS dump-use data.
- Capabilities: supported interface types, software iftypes, interface combinations, feature flags, extended features byte array, iftype extended capabilities, AKM suites per iftype, HE/EHT/UHR capability blobs, NAN capabilities, and per-band iftype capabilities.
- Lifecycle/persistence helpers: `SOCKET_OWNER` ties interfaces, scans, regulatory indoor setting, NAN notifications, associations, IBSS, mesh, and AP lifetime to the netlink socket.
- Timing/counters: cookies, timeouts, hardware RX/TX timestamps, survey radio stats, CQM thresholds, FTM responder stats, peer measurements, and station/TID/TXQ counters.

The enum comment notes that when adding attributes the kernel policy in `nl80211.c` must be updated. That is a key integration requirement for any ABI extension.

## Nested Enums and Structs in This Chunk

- `enum nl80211_iftype` enumerates interface modes: unspecified, adhoc, station, AP, AP VLAN, WDS, monitor, mesh point, P2P client/GO/device, OCB, NAN, and NAN data.
- `enum nl80211_sta_flags` and `struct nl80211_sta_flag_update` model station authorization, QoS, MFP, authentication, TDLS, association, and SPP A-MSDU state.
- HE/EHT guard interval, LTF, and RU allocation enums support rate-info decoding for modern PHYs.
- `enum nl80211_rate_info` carries bitrate details across legacy, HT, VHT, HE, EHT, S1G, and UHR. It preserves both 16-bit and 32-bit bitrate attributes, recommending 32-bit use for high rates.
- `enum nl80211_sta_bss_param`, `enum nl80211_sta_info`, `enum nl80211_tid_stats`, and `enum nl80211_txq_stats` define station state and counters, including 64-bit byte counters, per-chain signals, beacon counters, airtime metrics, TXQ backlog/drop/flow stats, and boottime association timestamps.
- `enum nl80211_mpath_flags` and `enum nl80211_mpath_info` describe mesh path state, metrics, expiration, discovery retry/timeout, hop count, and path changes.
- Band and capability enums include `nl80211_band_iftype_attr`, `nl80211_band_attr`, `nl80211_nan_phy_cap_attr`, and `nl80211_band`.
- Regulatory enums include `nl80211_wmm_rule`, `nl80211_frequency_attr`, `nl80211_reg_initiator`, `nl80211_reg_type`, `nl80211_reg_rule_attr`, `nl80211_reg_rule_flags`, `nl80211_dfs_regions`, and `nl80211_user_reg_hint_type`.
- Scan and survey helpers include `nl80211_sched_scan_match_attr`, `nl80211_survey_info`, and RSSI/CQM documentation at the end of the chunk.
- Monitor, mesh, TX queue, channel, key, and rate-control helpers include `nl80211_mntr_flags`, `nl80211_mesh_power_mode`, `nl80211_meshconf_params`, `nl80211_mesh_setup_params`, `nl80211_txq_attr`, `nl80211_ac`, `nl80211_channel_type`, `nl80211_chan_width`, `nl80211_bss_scan_width`, `nl80211_bss_use_for`, `nl80211_bss_cannot_use_reasons`, `nl80211_bss`, `nl80211_bss_status`, `nl80211_auth_type`, `nl80211_key_type`, `nl80211_mfp`, `nl80211_wpa_versions`, `nl80211_key_default_types`, `nl80211_key_attributes`, `nl80211_tx_rate_attributes`, `nl80211_txrate_gi`, `nl80211_ps_state`, and the beginning of `nl80211_attr_cqm`.

## Control Flow and Protocol Behavior

There are no executable functions in this chunk, but the comments define important protocol flows:

- Station handling is per-interface. VLAN interfaces are special: a station bound to an AP may be moved to a VLAN via `NL80211_ATTR_STA_VLAN` while still logically belonging to the AP interface. TDLS external setup has a strict lifetime: add setup station, update once with capability/rate and authorization, enable link, then only tear down.
- Frame registration is per-interface and cannot be removed except by closing the socket. Interface type changes make registrations dormant until the type changes again. Frame TX reports status back to the requesting socket.
- Virtual interface concurrency is discovered from supported iftypes, software iftypes, and interface-combination attributes; active interfaces must match an advertised combination.
- Packet coalescing buffers matching multicast/broadcast packets until timer expiry, buffer exhaustion, or non-match.
- 4-way handshake, FILS, SAE, OWE, VLAN, TID configuration, and FILS crypto sections specify which attributes must be supplied to connect/start-AP/set-PMKSA/set-FILS-AAD operations and what state the driver returns.
- MLO changes command semantics by requiring `NL80211_ATTR_MLO_LINKS` in multi-link responses and `NL80211_ATTR_MLO_LINK_ID` for link-specific operations.
- Scheduled scans execute plan sequences, with the last plan infinite. Driver abort cancels all plans. Multi scheduled scans require explicit userspace support.
- NAN commands have socket ownership and cookie/instance-ID race-avoidance semantics; the cookie is authoritative because instance IDs may be reused.
- NAN schedule commands require full local or peer schedule information for updates, enforce compatible channel/map constraints, and use deferred update events for device-announced schedule changes.

## State and Persistence Behavior

Most values here describe transient kernel, driver, or firmware state exposed over netlink:

- `NL80211_ATTR_GENERATION` gives dump consistency and requires userspace to retry a dump if generation changes across multipart messages.
- `NL80211_ATTR_SOCKET_OWNER` makes resources auto-clean when the netlink socket closes. This affects created interfaces, scheduled scans, indoor regulatory configuration, NAN notifications, station associations, IBSS/mesh memberships, and AP operation.
- PMKSA and FILS PMKSA material may be cached in userspace persistently; the header documents PMKSA use after reboot or Wi-Fi off/on, but the header itself only defines the exchange.
- TID configuration is valid only for the current STA connection and is reset after disconnection, roaming, or interface down.
- QoS mapping is valid only during an association and is cleared on disassociation or AP restart.
- MAC ACL lists replace prior lists and must be cleared by the driver on AP stop.
- FILS AAD data is per-STA and cleaned by the driver once association completes.
- Scan/BSS metadata includes aging and boottime timestamps; hardware timestamps are device-clock values and may reset when the device or firmware resets.
- Mesh setup parameters are immutable once a mesh is active, while mesh configuration parameters can be changed during active mesh operation.

## Dependencies and Integration Points

- The header includes only `<linux/types.h>` in this chunk and uses fixed-width UAPI types such as `__u16`, `__u32`, and `__u64`.
- The constants are consumed by kernel nl80211 implementation code, especially `nl80211.c` policies, cfg80211/mac80211 internals, and wireless drivers advertising capabilities.
- Userspace integrations include generic-netlink clients, scan/connection managers, AP daemons, regulatory agents/databases, vendor tools, and diagnostic utilities. They must encode nested attributes exactly as documented.
- Many comments refer to IEEE 802.11 sections, Wi-Fi Aware NAN 4.0 tables, FCC guidance, DFS regions, and IETF RFC 6696 for FILS ERP key derivation.
- Wiphy capability responses advertise which commands, iftypes, features, AKMs, channel widths, bands, NAN capabilities, and vendor commands/events are supported; userspace must gate feature use on these advertised values.
- Driver feature bits outside this chunk are referenced throughout, e.g. `NL80211_EXT_FEATURE_*`, `NL80211_FEATURE_*`, and capability flags such as `WIPHY_FLAG_SUPPORTS_TDLS`; later chunks define more of these related enums.

## Risks and Edge Cases

- ABI order is the highest risk. Reordering or inserting commands/attributes anywhere other than the documented append points changes numeric IDs and breaks existing userspace.
- Top-level attributes are heavily reused across commands. Parsers must validate command-specific required/optional attributes and types, not only enum membership.
- Several operations are both commands and events; code that assumes one direction per command ID can mishandle async notifications.
- Socket-owned lifetimes can surprise clients if the creating netlink socket closes, especially for AP, mesh, IBSS, NAN, scheduled scan, and association flows.
- Management frame registrations cannot be explicitly removed and may become dormant after interface type changes; long-lived daemons must account for socket lifetime and interface reconfiguration.
- Nested arrays use enum values as netlink attribute type/index in several places; off-by-one handling is visible in station TID stats where TID values are shifted by one and special TID 16 maps to value 17.
- Many values have units that differ by field: MHz, KHz offsets, mBm, dBm, mBi, milliseconds, seconds, TUs, 32-microsecond units, nanoseconds, and 100 kbps. Unit mistakes are likely integration bugs.
- Some attributes have legacy aliases or deprecated forms, such as channel type vs. channel width, old scan generation, old mesh names, old UHB/6 GHz naming, passive-scan/no-IR aliases, and old survey counter names.
- 64-bit attributes often need explicit padding/alignment attributes such as `PAD`, and userspace should handle alignment consistently.
- MLO introduces ambiguity between MLD addresses and link addresses; comments document cases where `NL80211_ATTR_MAC`, `NL80211_ATTR_MLO_LINK_ID`, and `NL80211_ATTR_MLD_ADDR` change meaning.
- Regulatory flags and frequency attributes are compliance-sensitive. Incorrect interpretation of NO_IR, DFS, indoor, VLP/AFC, PSD, and UHR/EHT/HE restrictions can create illegal transmit behavior.
- Security attributes carry raw key material and authentication state. Implementations must avoid logging secrets and must handle PMK/PMKSA lifetime/reauth thresholds carefully.

## Test Signals

- UAPI ABI tests should verify numeric stability of `enum nl80211_commands`, `enum nl80211_attrs`, and nested enums against expected generated headers.
- Netlink policy tests in kernel/user tooling should exercise required attributes for representative commands: connect, start AP, new key, station add/set/delete, trigger scan, scheduled scan, register frame, frame TX, remain-on-channel, NAN start/function/schedule, MLO link operations, and set SAR/TID config.
- Dump consistency tests should simulate generation changes and verify userspace retries.
- Parser tests should cover unknown future attributes, missing optional attributes, nested array ordering, 64-bit padding, and command/event direction for shared command IDs.
- Compatibility tests should compile userspace using old aliases such as mesh params, SAE data, passive scan/no-IR, UHB/6 GHz names, and survey channel-time names.
- Regulatory tests should verify rule flags and frequency attributes map consistently, including DFS CAC time/start time, NO_IR aliases, PSD, 6 GHz VLP/AFC restrictions, and UHR/EHT/HE restrictions.
- Security/offload tests should validate FILS, SAE, OWE, PMKSA, 4-way handshake offload, control-port-over-nl80211, and key-mode flows using advertised feature flags.
- MLO tests should include per-link group keys, MLD pairwise keys, external auth with AP MLD address, link add/remove, TTLM mapping length, BSS use/cannot-use reasons, and link-removal events.
- NAN tests should cover socket-owned notifications, cookie-vs-instance ID handling, local/peer schedule full replacement, deferred schedule update completion, channel evacuation, and ULW update notifications.
- Station/statistics tests should cover 32-bit/64-bit counters, rate-info fallback from 32-bit to legacy 16-bit bitrate, HE/EHT/UHR rate fields, per-chain signals, TID stats indexing, and mesh path metrics.

## Chunk Boundary Notes

This chunk ends in the documentation for `enum nl80211_attr_cqm` at line 5,950, before that enum is completed. Later chunks are needed to cover the remainder of CQM attributes and all subsequent UAPI definitions. The final per-file research document should reconcile this chunk with later chunks to avoid treating the incomplete CQM section as a full-file endpoint.
