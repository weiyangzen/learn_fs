# sources/distributed-fs/ceph-client/net/wireless/nl80211.c lines 1-9099

## Scope

This chunk covers the first 9,099 lines of `net/wireless/nl80211.c`, the cfg80211 generic-netlink front end for Linux wireless configuration. The range starts at family setup, netlink attribute validation, policy tables, wiphy/interface/key helpers, capability dump builders, channel/wiphy mutation, interface lifecycle, key management, AP start/update/stop, station statistics serialization, and station-change parsing. It ends inside `nl80211_new_station()`, just after rejecting HT/VHT capabilities on 6 GHz HE stations; the remaining station-add type-specific validation and later mesh/regulatory/scan/connect operations continue in later chunks.

## Purpose

The covered code translates the public `nl80211` userspace ABI into cfg80211 driver operations and translates kernel/cfg80211 state back into netlink replies and multicast events. It is the main validation and marshalling layer between tools such as `iw`, `wpa_supplicant`, `hostapd`, NetworkManager, and per-driver `struct cfg80211_ops` callbacks.

The chunk has three broad jobs:

- Identify the target `wiphy` or `wireless_dev` from `NL80211_ATTR_WIPHY`, `NL80211_ATTR_IFINDEX`, or `NL80211_ATTR_WDEV`, while enforcing network namespace and lifetime locking rules.
- Define and apply netlink policies for the large nl80211 ABI surface, including beacon elements, keys, WoWLAN, peer measurements, tx rates, NAN, S1G, HE/EHT/UHR, MBSSID, station flags, and AP/station parameters.
- Implement early command handlers for querying and mutating wireless devices: `GET_WIPHY`, `SET_WIPHY`, interface dump/get/new/set/delete, key get/set/add/delete, AP start/change/stop, station dump/get/change, and the first part of station creation.

## Important APIs, Types, and Helpers

The generic-netlink family state is rooted in `nl80211_fam` and `nl80211_mcgrps`. The multicast groups advertise configuration, scan, regulatory, MLME, vendor, NAN, and optional testmode event channels.

Device lookup helpers are central:

- `__cfg80211_wdev_from_attrs()` resolves a `struct wireless_dev` by ifindex or wdev id, optionally constrained to a known `rdev`.
- `__cfg80211_rdev_from_attrs()` resolves a `struct cfg80211_registered_device` and rejects inconsistent wiphy/wdev/ifindex combinations.
- `cfg80211_get_dev_from_info()` is the command-side wrapper around rdev lookup.
- `nl80211_prepare_wdev_dump()` initializes and resumes dump operations for commands scoped to one wireless device, storing cursor state in `netlink_callback->args`.

The policy and validation layer includes the top-level `nl80211_policy`, key policies, monitor flag policy, station flag policy, tx queue policy, WoWLAN/coalesce/packet-pattern policies, peer-measurement policies, AP-related nested policies, NAN policies, SAR policy, MBSSID policy, and station WME policy. Validation functions include `validate_beacon_head()`, `validate_ie_attr()`, `validate_he_capa()`, `validate_uhr_capa()`, `validate_uhr_operation()`, `validate_supported_selectors()`, and NAN-specific checks for cluster ids, availability blobs, and ULW attributes.

Message builders serialize cfg80211 state to the nl80211 ABI:

- `nl80211hdr_put()` creates family headers.
- `nl80211_msg_put_channel()`, `nl80211_send_chandef()`, `nl80211_send_band_rateinfo()`, and `nl80211_send_iftype_data()` publish channel, band, HT/VHT/HE/EHT/UHR, S1G, EDMG, and rate capabilities.
- `nl80211_put_iftypes()`, `nl80211_put_ifcomb_data()`, `nl80211_put_iface_combinations()`, `nl80211_put_radio()`, and `nl80211_put_radios()` publish interface-type and multi-radio constraints.
- `nl80211_send_wiphy()` is the large split-dump builder for wiphy capabilities and feature flags.
- `nl80211_send_iface()` emits interface records, including MLO link attributes, channel, tx power, SSID, txq stats, and radio masks.
- `nl80211_put_sta_rate()`, `nl80211_fill_link_station()`, and `nl80211_send_station()` serialize per-station and per-link statistics, including rates, bytes, packets, signal, TID stats, mesh state, MLO association data, and optional link stats.

Command handlers in this chunk call through `rdev_*()` wrappers to driver callbacks, including `rdev_set_wiphy_params()`, `rdev_set_txq_params()`, `rdev_set_tx_power()`, `rdev_set_antenna()`, `rdev_set_ap_chanwidth()`, `rdev_add_virtual_intf()`, `rdev_del_virtual_intf()`, key callbacks, `rdev_start_ap()`, `rdev_change_beacon()`, `rdev_dump_station()`, `rdev_get_station()`, and `rdev_change_station()`.

## Control Flow

Lookup and dump flow is lock-sensitive. Global lookup paths use `rtnl_lock()` when walking registered devices or netdevices. Per-wiphy mutation and serialization occurs under `wiphy_lock()`/`guard(wiphy)` or explicit `rdev->wiphy.mtx` locking. Dump callbacks use `cb->args` as cursors so long replies can resume without re-parsing or re-walking from the beginning.

Wiphy queries flow through `nl80211_dump_wiphy_parse()`, `nl80211_dump_wiphy()`, and `nl80211_send_wiphy()`. `nl80211_send_wiphy()` uses `struct nl80211_dump_wiphy_state` to split large capability payloads into ordered stages. The stages publish base wiphy properties, cipher suites, supported interface types, bands/channels, supported commands, off-channel/WoWLAN/software-iftype/interface-combination data, feature flags, management frame stypes, address lists, coalesce support, vendor commands/events, extended features, SAR, MBSSID, PMSR, NAN, multi-radio, and related capability blocks. If unsplit userspace cannot fit the response, the dump path can increase minimum skb allocation or require split behavior for newer features.

Channel and wiphy mutation flows through `nl80211_set_wiphy()` and `__nl80211_set_channel()`. The code parses chandefs from legacy channel type or modern width/center-frequency attributes, validates disabled/monitor-only constraints, puncturing support, S1G, 5/10 MHz support, and regulatory beaconing. For AP/GO, it either stores a preset chandef before AP start or performs dynamic channel-width changes if the AP is already beaconing and the driver supports it. Other wiphy settings stage values, call the driver, and roll local `struct wiphy` fields back on callback failure.

Interface management flows through `nl80211_dump_interface()`, `nl80211_get_interface()`, `nl80211_set_interface()`, `_nl80211_new_interface()`, `nl80211_new_interface()`, and `nl80211_del_interface()`. The code validates iftype transitions, monitor options, 4-address support, radio masks, mesh ids, MAC-on-create behavior, owner socket tracking, netdev-less P2P/NAN registration, and notification on successful changes.

Key management uses `struct key_parse` and supports both nested modern key attributes and older top-level key attributes. `nl80211_parse_key()` normalizes key index, cipher, sequence, default flags, default unicast/multicast flags, and extended key-id mode. Command handlers validate if the current interface state allows keys, validate link id rules for MLO pairwise/group keys, enforce cipher/key-index ranges, then dispatch to add/delete/get/set-default driver callbacks. Connection-time WEP keys are cached by `nl80211_parse_connkeys()`.

AP flow is assembled in `nl80211_start_ap()`. It requires AP/GO iftype, a driver `start_ap` op, no CAC in progress, no existing beacon interval, and required beacon interval/DTIM/head attributes. It parses beacon bodies, SSID, hidden SSID, auth type, crypto, inactivity timeout, P2P GO power-save settings, channel definition or preset channel, regulatory beacon permission, optional beacon rate, PBSS, ACLs, TWT responder, HE OBSS PD, FILS discovery, unsolicited broadcast probe response, MBSSID/EMA/RNR, S1G short beacon, UHR operation, and AP settings flags. After `rdev_start_ap()` succeeds it persists AP beacon interval, chandef, SSID, optional owner port id, and multicasts `NL80211_CMD_START_AP`. `nl80211_set_beacon()` revalidates beacon content and 6 GHz power type before `rdev_change_beacon()`, while `nl80211_stop_ap()` delegates to `cfg80211_stop_ap()`.

Station query flow allocates per-link `link_station_info` storage, calls driver `dump_station`/`get_station`, optionally aggregates MLO statistics with `cfg80211_sta_set_mld_sinfo()`, serializes with `nl80211_send_station()`, and releases dynamic station-info content. Station mutation flow parses address, MLD/link MACs, rates, listen interval, AID, VLAN, capabilities, station flags, mesh plink state/action, mesh power, opmode, HE 6 GHz, EML, airtime, per-station tx power, TDLS capability updates, supported channels/oper classes, WME, and VLAN netdev binding. `cfg80211_check_station_change()` is exported so drivers can validate the parsed `station_parameters` against station type before applying them.

## State and Persistence Behavior

Most state in this chunk is either kernel object state protected by cfg80211 locks or temporary netlink parse/build state. Persistent software state includes:

- `struct wiphy` parameters such as retry limits, fragmentation/RTS thresholds, coverage class, txq settings, antenna settings, per-radio RTS thresholds, feature/capability data, radio configurations, and address lists.
- `struct wireless_dev` fields such as iftype, `use_4addr`, `radio_mask`, owner netlink port ids, AP preset chandef, AP beacon interval/chandef, AP SSID, MLO links, mesh id, and netdev-less P2P/NAN registration state.
- Driver-owned key, station, AP, channel, tx power, and interface state reached through `rdev_*()` operations.
- Dump cursors in `netlink_callback->args`, including wiphy indexes, interface indexes, station indexes, split-stage cursors, and wdev identifiers.

Sensitive temporary state includes key material and cached WEP connection keys. `nl80211_parse_connkeys()` allocates `cfg80211_cached_keys`, copies WEP key bytes into owned storage, and frees with `kfree_sensitive()` on parse error. Other key command paths usually pass pointers into netlink attribute memory to driver callbacks during the command lifetime.

AP parsing allocates `cfg80211_ap_settings`, ACL data, MBSSID elements, and RNR elements; all are freed on exit, and referenced transmit BSSID netdevices are released with `dev_put()` when needed. Station dumps allocate per-link statistic structs and rely on `cfg80211_sinfo_release_content()` to free dynamic content after serialization or errors.

## Dependencies and Integration Points

This code depends on Linux netlink/generic-netlink helpers, cfg80211 core types, IEEE 802.11 element parsers, network namespace and netdevice APIs, RTNL, regulatory helpers, and driver callback wrappers from `rdev-ops.h`.

Important integration points include:

- Userspace ABI definitions in `<linux/nl80211.h>` and cfg80211 driver-facing structures in `<net/cfg80211.h>`.
- cfg80211 core registration, wiphy/device lists, wdev lists, namespace movement, and interface destruction in `core.c`/`core.h`.
- Regulatory channel and beaconing checks in `reg.c`/`reg.h`.
- Driver implementations of `struct cfg80211_ops`, which receive validated `cfg80211_chan_def`, `cfg80211_ap_settings`, `station_parameters`, `key_params`, `vif_params`, and wiphy parameter updates.
- MLME consumers of multicast events, especially AP-start notifications on the MLME multicast group.
- MLO support through link ids, valid-link masks, MLD addresses, per-link AP state, per-link station stats, and link-specific key/channel/txq/tx-power attributes.
- Wireless extension compatibility blocks under `CONFIG_CFG80211_WEXT`, which mirror default key indexes.

## Risks

- The nl80211 ABI is security-sensitive because unprivileged or privileged userspace supplies nested binary attributes. Length policies and custom validators must stay aligned with every parser that later dereferences element data.
- Locking order is fragile. Lookup paths mix RTNL, wiphy mutexes, netdevice references, and dump resumption; missing namespace rechecks or reference releases can cause stale object access across netns moves or device removal.
- Split wiphy dumps are compatibility-sensitive. Adding data to the unsplit region can break older userspace buffers, while cursor mistakes can duplicate or omit capability sections.
- Local wiphy state is updated before driver callbacks in some set paths and then rolled back on error. Any new mutable field must follow the same rollback pattern or the kernel can report state the driver did not apply.
- Channel parsing spans old and new ABIs, S1G, 6 GHz, 60 GHz, puncturing, DFS, monitor-only channels, and AP dynamic width changes. Incomplete validation can permit illegal beaconing or reject valid combinations.
- MLO link-id handling is easy to get wrong. Pairwise keys, per-link AP state, station MLD/link addresses, txq parameters, and station stats have different rules for missing, invalid, and non-MLO link ids.
- Beacon/AP parsing stores many pointers into netlink attributes for the duration of the driver call. Drivers must copy anything needed after the callback returns.
- Station validation is split between nl80211 parsing and exported `cfg80211_check_station_change()`. Drivers that do not call the checker risk accepting illegal flag combinations, TDLS/AP/mesh/NAN state, or capabilities.
- The chunk ends mid-`nl80211_new_station()`, so a complete station-add analysis requires the next chunk for interface-type-specific acceptance and the final driver call.

## Test and Validation Signals

Useful validation signals include:

- `iw phy`, `iw dev`, and split wiphy dumps should show stable capabilities, bands, channels, interface combinations, extended features, SAR, MBSSID, NAN, and multi-radio data without truncated or duplicated sections.
- Wiphy mutation tests should cover retry/RTS/fragmentation/coverage/txq changes, per-radio RTS threshold changes, tx power, antenna masks, rollback on driver failure, and invalid radio indexes.
- Channel tests should cover legacy channel type, modern chandef, S1G, 5/10 MHz, 6 GHz power-type beaconing, puncturing support, monitor-only channels, disabled channels, and AP channel-width changes.
- Interface lifecycle tests should create/set/delete AP, station, monitor, P2P device, NAN, mesh, AP VLAN, and radio-masked interfaces; verify owner socket behavior and netdev-less registration paths.
- Key tests should cover old and nested key formats, WEP connection keys, pairwise/group keys, default/default-mgmt/default-beacon keys, extended key-id TX selection, MLO link ids, and invalid index/cipher/iftype cases.
- AP tests should start/change/stop AP and P2P GO with beacon IEs, crypto, ACLs, custom beacon rates, HE/EHT/UHR constraints, FILS discovery, unsolicited probe response, MBSSID/EMA/RNR, S1G short beacons, owner-port conflicts, and regulatory rejection.
- Station tests should exercise dump/get serialization, MLO aggregate stats, per-link stats, rate-info encoding for legacy/HT/VHT/HE/EHT/UHR/S1G, station flag masks, TDLS setup, mesh plink changes, NAN station restrictions, VLAN binding, airtime fairness, and per-station tx power.
- Memory/debug configurations such as KASAN, KMSAN, lockdep, and netlink attribute fuzzing are valuable here because most bugs would surface as bad nested-attribute parsing, missed cleanup, lock-order problems, or stale object use.
