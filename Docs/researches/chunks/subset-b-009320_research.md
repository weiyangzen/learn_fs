# sources/test-tools/strace/bundled/linux/include/uapi/linux/nl80211.h lines 1-5950

## Scope

This chunk covers the opening 5,950 lines of the bundled Linux UAPI header for the `nl80211` generic netlink family. It is a public ABI contract, not executable implementation code. The covered range defines the generic netlink family name, multicast group names, kernel-doc protocol semantics, the complete `enum nl80211_commands`, the complete `enum nl80211_attrs`, and many supporting attribute enums and packed structs through the beginning of `enum nl80211_attr_cqm`. Line 5,950 ends mid-documentation for CQM attributes, so the rest of CQM and later nl80211 sub-APIs must be reconciled from following chunks.

## Purpose

`nl80211.h` is the userspace API surface for Linux wireless stack operations via generic netlink. In this repository it is bundled under strace test tools, so its practical consumer is decoder/test code that needs exact numeric command and attribute values to trace nl80211 messages accurately. The file itself warns that enum ordering is ABI-sensitive: existing entries must not be moved, and new commands/attributes are appended before the internal `*_AFTER_LAST` sentinels.

The header models most cfg80211/mac80211 user-visible behavior as numbered commands and nested netlink attributes. This chunk documents station management, management frame registration and TX, virtual interface concurrency, packet coalescing, handshake/authentication offloads, VLAN and TID configuration, FILS crypto, Multi-Link Operation, OWE offload, NAN scheduling, regulatory state, scan results, mesh state, BSS descriptions, key material, rates, channel widths, bands, and power save.

## Important APIs, Types, and Constants

Top-level constants:

- `NL80211_GENL_NAME` is the generic netlink family string, `"nl80211"`.
- Multicast group string constants define event channels: `config`, `scan`, `regulatory`, `mlme`, `vendor`, `nan`, and `testmode`.
- EDMG min/max constants constrain channel and bandwidth configuration.
- Size and limit macros define ABI-visible maxima such as `NL80211_WIPHY_NAME_MAXLEN`, `NL80211_MAX_SUPP_RATES`, `NL80211_MAX_SUPP_SELECTORS`, HT/VHT/HE/EHT capability lengths, cipher/AKM suite limits, TKIP key offsets, minimum remain-on-channel duration, RSSI threshold defaults, and CQM TX error interval maximum.

Primary command API:

- `enum nl80211_commands` is the central operation/event namespace. It includes wiphy and interface lifecycle commands, key management, AP beacon/start/stop, station and mesh path management, regulatory get/set/change events, scans, MLME authentication/association/deauth/disassoc, IBSS/mesh/OCB/NAN lifecycle, testmode, connection/roam/disconnect, remain-on-channel, management frame register/TX/status, power save, CQM, channel switching, WoWLAN, TDLS, vendor commands, QoS map, TX traffic streams, PMK/PMKSA, external auth, peer measurements, SAR, color change, FILS AAD, MLO link operations, hardware timestamping, TID-to-link mapping, EPCS, incumbent signal detection, and newer NAN scheduling events.
- Many commands act as both requests and notifications. Examples include authentication, association, control-port frames, management frames, radar detection, WoWLAN wake reason, external authentication, NAN function deletion, and local/peer NAN schedule updates.
- Compatibility aliases preserve older names, e.g. `NL80211_CMD_NEW_BEACON = NL80211_CMD_START_AP`, `NL80211_CMD_DEL_BEACON = NL80211_CMD_STOP_AP`, `NL80211_CMD_REGISTER_ACTION = NL80211_CMD_REGISTER_FRAME`, and `NL80211_CMD_ACTION = NL80211_CMD_FRAME`.

Primary attribute API:

- `enum nl80211_attrs` is the top-level netlink attribute namespace. It maps commands to typed data such as wiphy ids/names, interface indexes/names/types, MAC addresses, keys, beacon templates, station metadata, band capabilities, regulatory rules, scan parameters/results, frames, SSIDs, auth/reason/status codes, WPA/AKM/cipher suites, generation counters, net namespace selectors, cookies, frame registration filters, TX rates, CQM, antenna masks, WoWLAN triggers, sched scan plans and matches, interface combinations, rekey data, TDLS parameters, DFS/radar attributes, vendor data/events, QoS maps, socket ownership, extended features, FILS/SAE/OWE inputs, FTM and peer measurements, SAR specs, MBSSID/EMA, EHT/UHR and MLO capabilities, hardware timestamps, TTLM bitmaps, multi-radio data, S1G and NAN schedule data.
- The attribute enum ends with `__NL80211_ATTR_AFTER_LAST`, `NUM_NL80211_ATTR`, and `NL80211_ATTR_MAX`. The comment immediately before the sentinels says new attributes also require updating policy in `nl80211.c`, which is an integration contract with kernel-side validation.
- Compatibility macros map old names to newer attributes: scan generation to generation, mesh params to mesh config, interface socket owner to socket owner, SAE data to auth data, CSA offsets to countdown offsets, passive scan/no IBSS to `NO_IR`, UHB names to 6 GHz names, and older survey time names to newer ones.

Supporting type families in this chunk:

- Interface and station: `enum nl80211_iftype`, `enum nl80211_sta_flags`, `enum nl80211_sta_p2p_ps_status`, and packed `struct nl80211_sta_flag_update`.
- Rate/capability encoding: HE/EHT guard interval, LTF, and RU allocation enums; `enum nl80211_rate_info`; `enum nl80211_tx_rate_attributes`; `struct nl80211_txrate_vht`; `struct nl80211_txrate_he`; `struct nl80211_txrate_eht`; `enum nl80211_txrate_gi`.
- Station and queue statistics: `enum nl80211_sta_bss_param`, `enum nl80211_sta_info`, `enum nl80211_tid_stats`, and `enum nl80211_txq_stats`.
- Mesh: `enum nl80211_mpath_flags`, `enum nl80211_mpath_info`, `enum nl80211_mesh_power_mode`, `enum nl80211_meshconf_params`, and `enum nl80211_mesh_setup_params`.
- Band/channel/regulatory: `enum nl80211_band_iftype_attr`, `enum nl80211_band_attr`, `enum nl80211_nan_phy_cap_attr`, `enum nl80211_wmm_rule`, `enum nl80211_frequency_attr`, `enum nl80211_bitrate_attr`, `enum nl80211_reg_initiator`, `enum nl80211_reg_type`, `enum nl80211_reg_rule_attr`, `enum nl80211_reg_rule_flags`, `enum nl80211_dfs_regions`, `enum nl80211_user_reg_hint_type`, `enum nl80211_survey_info`, `enum nl80211_mntr_flags`, `enum nl80211_channel_type`, `enum nl80211_chan_width`, and `enum nl80211_bss_scan_width`.
- BSS/auth/key/power domains: `enum nl80211_bss_use_for`, `enum nl80211_bss_cannot_use_reasons`, `enum nl80211_bss`, `enum nl80211_bss_status`, `enum nl80211_auth_type`, `enum nl80211_key_type`, `enum nl80211_mfp`, `enum nl80211_wpa_versions`, `enum nl80211_key_default_types`, `enum nl80211_key_attributes`, `enum nl80211_band`, `enum nl80211_ps_state`, and the start of `enum nl80211_attr_cqm`.

## Protocol and Control Flow

There is no local C control flow in this chunk. The control flow is protocol-level:

1. Userspace opens a generic netlink socket and resolves the `nl80211` family.
2. Userspace sends an `enum nl80211_commands` value with a command-specific set of top-level `NL80211_ATTR_*` attributes.
3. Kernel cfg80211/mac80211 and driver code validate attributes against policy, device capabilities, interface type, regulatory state, and feature flags.
4. The kernel replies synchronously, emits multicast/unicast events, or both. Dump commands use `NL80211_ATTR_GENERATION` so userspace can detect inconsistent snapshots and retry.
5. Many long-lived operations return or later emit `NL80211_ATTR_COOKIE`, allowing userspace to correlate asynchronous completion/status events such as remain-on-channel, management frame TX, station probe, NAN functions, and peer measurements.

The kernel-doc comments describe several stateful command flows:

- TDLS external setup creates a temporary station entry, updates it once after setup, enables the link, and later tears it down.
- Management frame registration is per interface and persists until the registering netlink socket closes. Interface type changes make registrations dormant until the type changes again.
- `NL80211_ATTR_SOCKET_OWNER` binds lifetimes of created interfaces, scheduled scans, indoor regulatory state, associations, IBSS, mesh, AP, and NAN notifications to the owning socket.
- Connect/roam/external-auth paths exchange SSID, BSSID/frequency hints, auth data, PMK/PMKSA material, control-port behavior, MLO support/link IDs, and status/timed-out events.
- AP/channel operations require beacon/probe/assoc response templates, CSA/countdown offsets, DFS/radar handling, color changes, MBSSID/EMA/RNR data, and optionally FILS discovery or unsolicited broadcast probe response templates.
- NAN has explicit start/stop, function add/delete, configuration changes, match notifications, cluster events, local schedule update, peer schedule configuration, ULW update, and channel evacuation events. Some NAN events are unicast to the socket owner.

## State and Persistence Behavior

This header does not store state, but it defines which state is exposed or controlled:

- Persistent-until-socket-close state includes frame registrations and socket-owned interfaces/scans/AP/mesh/IBSS/association/NAN resources.
- Per-connection state includes PMK/PMKSA, FILS ERP-derived material, QoS maps, TID configuration, control-port settings, MLO link setup, hardware timestamp configuration, and BSS association status. Many of these are explicitly cleared on disassociation, AP restart, interface down, roaming, or socket close.
- Regulatory state is global or per-wiphy depending on initiator/type and self-managed-reg flags. Frequency attributes and regulatory rule flags expose derived channel availability, DFS state/timers, indoor/no-IR/6 GHz/VLP/AFC/UHR restrictions, CAC start time, and power limits.
- Scan and BSS state is snapshot-like. `NL80211_ATTR_GENERATION` protects list dumps, BSS entries carry age and `CLOCK_BOOTTIME` timestamps, and BSS usability flags/reasons report device-specific restrictions.
- Statistics enums expose accumulated counters for station bytes/packets/retries/failures, per-TID counters, TXQ backlog/drops/ECN/overlimit/overmemory/collisions, survey channel time/noise/busy/RX/TX/scan, and mesh path changes.
- Security material handling is ABI-defined but opaque to the header: key data, PMK, PMKID, SAE password, FILS KEK/nonces, ERP keys, and PMKR0 names are transported as attributes and must be treated as sensitive by userspace and decoders.

## Dependencies and Integration Points

The only direct include in this chunk is `<linux/types.h>`, providing fixed-width UAPI types such as `__u16` and `__u32`. Several structs are wire-layout data and must retain exact size and packing; `struct nl80211_sta_flag_update` is explicitly `__attribute__((packed))`, and TX rate structs use fixed arrays indexed by NSS.

Kernel integration points:

- Kernel-side `net/wireless/nl80211.c` owns validation policy, command handlers, dump support, and event emission. New top-level attributes must be reflected in its policy.
- cfg80211/mac80211 and individual wireless drivers provide device capabilities, interface combinations, feature flags, channel/regulatory information, scan results, station stats, key offload support, MLO/NAN/FTM/SAR support, and command-specific behavior.
- Wireless-regdb/CRDA-style regulatory data and country IE processing inform the regulatory enums and frequency attributes.

Userspace integration points:

- `wpa_supplicant`, `hostapd`, `iw`, NetworkManager/iwd, and vendor tools consume these command/attribute numbers for wireless control and event handling.
- strace can include this header so nl80211 netlink traces decode numeric command and attribute IDs into symbolic names. ABI aliases in this chunk matter for older userspace and older kernel trace compatibility.
- Security/authentication consumers rely on documented command combinations for PMKSA caching, 4-way handshake offload, FILS, SAE, OWE, external authentication, control-port-over-nl80211, and port authorization events.

## Risks and Edge Cases

- ABI ordering is the largest risk. Reordering existing enum values, inserting in the middle, or changing aliases would break existing binaries and strace decoders.
- Numeric sentinel use must be careful. `*_MAX` values are for validation and iteration bounds, while `NUM_*` values are not always stable for userspace assumptions.
- Some attributes are deprecated, obsolete, or compatibility-only but still ABI-visible. Decoders and tests should preserve old symbolic names where expected.
- Attribute typing is implicit in comments and kernel policy, not encoded in C types. Incorrect parser assumptions about `u8`, `u16`, `u32`, `u64`, signed values, binary blobs, nested attributes, or flag attributes can misdecode traffic.
- Nested attributes are common and sometimes deeply structured: station info contains rate info/TID stats/TXQ stats; BSS data contains raw IEs and timestamps; regulatory data contains rules and frequency attributes; NAN schedule data uses channels, maps, slots, and raw availability blobs.
- 64-bit values require padding/alignment attributes in several families (`NL80211_ATTR_PAD`, BSS pad, survey pad, station info pad, TID stats pad). Netlink decoders must tolerate padding and preserve alignment.
- Several protocol flows depend on socket lifetime and asynchronous events. Tests that only inspect the request path can miss cleanup behavior or event-only command use.
- MLO and NAN additions introduce multiple identifiers for a peer/interface: MLD address, link ID, NMI/NDI addresses, peer schedule sequence IDs, and channel entries. Confusing link address with MLD address can produce incorrect traces or user-facing diagnostics.
- Regulatory names evolved from UHB to 6 GHz and from passive/no-IBSS to no-IR. Compatibility macros hide this in C but string decoders may need expected old/new names.
- The chunk ends before `enum nl80211_attr_cqm` is complete, so any final per-file synthesis must merge subsequent CQM definitions before making whole-file claims.

## Test Signals

Useful test signals for this chunk are ABI and decoder oriented:

- Build-time checks that this bundled header parses with C code that includes `<linux/types.h>` and uses the packed structs.
- strace decoder tests that numeric `nl80211_commands` values resolve to the expected symbolic names, including aliases such as `NEW_BEACON`/`START_AP`, `ACTION`/`FRAME`, and `ACTION_TX_STATUS`/`FRAME_TX_STATUS`.
- Attribute decoder tests for common requests and events: `GET_WIPHY` dumps, interface creation/deletion, connect/roam/disconnect, scan trigger/results, management frame TX/status, station dump, regulatory change, channel switch, vendor command, external auth, control-port frame, MLO link commands, and NAN schedule events.
- Nested attribute tests for `NL80211_ATTR_STA_INFO`, `NL80211_ATTR_BSS`, `NL80211_ATTR_WIPHY_BANDS`, `NL80211_ATTR_REG_RULES`, `NL80211_ATTR_TX_RATES`, `NL80211_ATTR_TID_CONFIG`, `NL80211_ATTR_MLO_LINKS`, and NAN schedule attributes.
- Boundary tests for enum sentinels and maximums: `NL80211_CMD_MAX`, `NL80211_ATTR_MAX`, `NL80211_IFTYPE_MAX`, `NL80211_RATE_INFO_MAX`, `NL80211_BSS_MAX`, and similar sub-enum max values.
- Compatibility-name tests for old macros: mesh params, scan generation, CSA offset aliases, frequency passive/no-IBSS aliases, regulatory no-IR/HT40 aliases, UHB-to-6GHz aliases, and survey channel-time aliases.
- Security-sensitive decode tests should avoid printing raw secrets by default, especially key data, PMK/PMKID/PMKR0, SAE passwords, FILS KEK/nonces, and ERP key material.

## Open Items for Merge Lane

- Merge with later chunks to complete `enum nl80211_attr_cqm` and all following sub-APIs.
- Confirm whether strace in this repository uses generated xlat tables from this header; if so, final research should connect these enum families to the exact generated decoder tables/tests.
- Verify final whole-file report preserves the UAPI ABI warning prominently because it governs nearly every enum in the file.
