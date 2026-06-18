# sources/distributed-fs/ceph-client/include/net/cfg80211.h lines 1-7164

## Scope

This chunk covers the first 7164 lines of Linux wireless `cfg80211.h`, the public kernel interface between cfg80211/nl80211 and wireless drivers. It includes the introductory documentation, hardware capability structures, channel/regulatory helpers, AP/STA/mesh/IBSS/OCB/NAN request structs, scan and BSS cache types, the large `struct cfg80211_ops` driver callback table, `struct wiphy` hardware registration state, wiphy work helpers, and the start of `struct wireless_dev`.

The file is primarily API contract and state layout. Executable logic in this range is limited to small inline helpers and macros; the behavioral contract is mostly encoded in struct fields, callback documentation, pointer ownership rules, locking notes, and lifecycle comments.

## Purpose

`cfg80211.h` defines how modern Linux 802.11 drivers advertise capabilities and receive configuration requests. A driver registers one or more physical wireless devices as `struct wiphy`, exposes supported bands/channels/interface modes/features, and implements callbacks in `struct cfg80211_ops`. cfg80211 then translates nl80211 requests and internal kernel flows into these callback parameters and expects drivers to report asynchronous completion through cfg80211 event APIs declared elsewhere.

The chunk also defines shared representation for:

- Channel and regulatory state, including DFS state, PSD power, 6 GHz/AP power restrictions, S1G/EDMG bandwidths, channel definitions, and channel usability checks.
- PHY capabilities for legacy, HT, VHT, HE, EHT, UHR, S1G, and EDMG operation.
- Interface creation, AP beacons, channel switches, BSS color changes, station and link-station management, mesh/OCB/IBSS setup, scans, BSS cache entries, authentication, association, connection, roaming, PMKSA, WoWLAN, packet coalescing, management TX, QoS maps, NAN, external authentication, OWE, peer measurement/FTM, SAR, hardware timestamping, and TID-to-link mapping.
- Driver capability advertisement through `struct wiphy`, interface combinations, WoWLAN/coalesce/vendor-command support, per-iftype AKM/extended capabilities, multi-radio descriptors, NAN capabilities, and PMSR capabilities.
- Driver-owned wireless interface state through `struct wireless_dev`.

## Important APIs, Types, and Data

Hardware and channel capabilities start with `enum ieee80211_channel_flags`, `struct ieee80211_channel`, `enum ieee80211_rate_flags`, `struct ieee80211_rate`, and per-STA capability structs for HT/VHT/HE/EHT/UHR/S1G plus `struct ieee80211_edmg`. `struct ieee80211_supported_band` groups the channels, bitrates, and per-interface-type capability data for one band. The `__iftd` annotation, `ieee80211_set_sband_iftype_data()`, `for_each_sband_iftype_data()`, and `ieee80211_get_*_iftype_cap()` helpers protect and retrieve interface-type-specific HE/EHT/UHR data.

`struct cfg80211_chan_def` is the central channel descriptor passed through most AP/mesh/scan/connect/radar paths. Helpers include `cfg80211_get_chandef_type()`, `cfg80211_chandef_create()`, `cfg80211_chandef_identical()`, `cfg80211_chandef_is_edmg()`, `cfg80211_chandef_is_s1g()`, `cfg80211_chandef_compatible()`, `nl80211_chan_width_to_mhz()`, `cfg80211_chandef_valid()`, `cfg80211_chandef_usable()`, DFS helpers, `cfg80211_chandef_primary()`, `nl80211_send_chandef()`, `ieee80211_chandef_max_power()`, and `cfg80211_any_usable_channels()`.

Configuration structs in this range mirror nl80211 commands: `vif_params`, `key_params`, `cfg80211_bitrate_mask`, `cfg80211_tid_config`, `cfg80211_fils_aad`, AP/beacon structs, CSA/color-change structs, station/link-station add/change/delete structs, `bss_parameters`, `mesh_config`, `mesh_setup`, `ocb_setup`, and `ieee80211_txq_params`. Many use explicit masks or sentinel values such as `-1` or `NULL` to mean "unchanged".

Scanning and BSS cache types include `cfg80211_scan_request`, `cfg80211_sched_scan_request`, `cfg80211_inform_bss`, `cfg80211_bss_ies`, and `cfg80211_bss`. The BSS structs carry RCU-protected IE pointers, timestamps, signal/chain signal data, hidden-SSID/multi-BSSID relations, usage restrictions, and driver-private storage. `ieee80211_bss_get_elem()` and `ieee80211_bss_get_ie()` require RCU read-side protection.

SME/authentication data is represented by `cfg80211_auth_request`, `cfg80211_assoc_request`, `cfg80211_ml_reconf_req`, `cfg80211_deauth_request`, `cfg80211_disassoc_request`, `cfg80211_ibss_params`, and `cfg80211_connect_params`. MLO support appears throughout via link IDs, AP MLD addresses, per-link BSS entries, valid-link bitmaps, MLD station addresses, link station operations, TID-to-link mapping, and association multi-link reconfiguration.

Power, wake, and offload structures include `cfg80211_pmksa`, `cfg80211_wowlan_tcp`, `cfg80211_wowlan`, `cfg80211_wowlan_wakeup`, `cfg80211_gtk_rekey_data`, coalesce rules, `cfg80211_set_hw_timestamp`, `cfg80211_sar_specs`, `cfg80211_sar_capa`, and PMK/offloaded handshake structs.

NAN has a dedicated section defining the dependency model between NMI interface, NDI interface, NMI station, local/peer schedules, and NDI stations. Its concrete structs are `cfg80211_nan_conf`, `cfg80211_nan_local_sched`, `cfg80211_nan_peer_sched`, `cfg80211_nan_func`, associated filters/maps/channels, and `enum cfg80211_nan_conf_changes`.

`struct cfg80211_ops` is the main driver API. It includes callbacks for suspend/resume, virtual interface lifecycle, MLO interface links, keys, AP start/change/stop, station and link-station operations, mesh paths, mesh/OCB/IBSS join/leave, BSS parameter changes, scan/abort, auth/assoc/deauth/disassoc/connect/roam parameter updates/disconnect, tx power, rfkill, survey, remain-on-channel, management TX, testmode, bitrate masks, PMKSA, power management, CQM, scheduled scan, management frame registrations, antennas, TDLS, P2P device start/stop, ACLs, radar/CAC, FT IEs, critical protocol, coalescing, channel switch, QoS map, TX TS, NAN, multicast-to-unicast, TXQ stats, PMK/external auth/control port, FTM/PMSR, OWE, mesh probing, TID config, SAR, color change, FILS AAD, background radar, hardware timestamping, TTL mapping, radio masks, ML reconfiguration, and EPCS.

`struct wiphy` is the hardware registration object. Drivers fill capability fields before `wiphy_register()`, including permanent/alternate addresses, management subtype masks, interface modes/combinations, flags/features/ext_features, signal type, scan limits, cipher/AKM suites, thresholds, WoWLAN/coalesce/vendor capabilities, bands, regulatory notifier, extended capabilities, NAN/PMSR/SAR support, MBSSID/EMA limits, HW timestamp peer limit, and optional multi-radio descriptors. cfg80211 owns read-only fields such as the device object, debugfs directory, `wdev_list`, registered state, and regulatory domain pointer.

Registration and object helpers include `wiphy_new_nm()`, `wiphy_new()`, `wiphy_register()`, `wiphy_unregister()`, `wiphy_free()`, `wiphy_priv()`, `priv_to_wiphy()`, `set_wiphy_dev()`, `wiphy_dev()`, `wiphy_name()`, `wiphy_net()`, `wiphy_net_set()`, `get_wiphy_regdom()`, `lockdep_assert_wiphy`, `rcu_dereference_wiphy()`, and `wiphy_dereference()`.

Work helpers include `wiphy_lock()`, `wiphy_unlock()`, `struct wiphy_work`, `wiphy_work_queue/cancel/flush()`, delayed work wrappers, and hrtimer-backed work wrappers. Their key contract is that queued functions run with the wiphy mutex held and are synchronized with explicit `wiphy_lock()` sections.

`struct wireless_dev` begins near the end of the chunk and stores per-interface cfg80211 state: wiphy pointer, iftype, netdev association, management registrations, address/running/registration flags, connection and cached-key state, event queues, WEXT compatibility data, CQM/PMSR state, per-iftype union state for client/mesh/AP/IBSS/OCB/NAN, MLO link state including per-link address/chandef/current BSS/CAC timing, `valid_links`, and `radio_mask`. Helpers include `wdev_address()`, `wdev_running()`, `wdev_priv()`, `wdev_chandef()`, `WARN_INVALID_LINK_ID()`, and `for_each_valid_link()`.

## Control Flow

The normal driver lifecycle is allocate a `wiphy` with `wiphy_new()`/`wiphy_new_nm()`, fill capability fields, set the parent device with `set_wiphy_dev()`, optionally apply device-tree frequency limits with `wiphy_read_of_freq_limits()`, register with `wiphy_register()`, attach `wireless_dev` instances to netdevs or return them from cfg80211 callbacks, then later call `wiphy_unregister()` and `wiphy_free()`. cfg80211 serializes most `cfg80211_ops` calls with `wiphy->mtx`.

User-space nl80211 requests become structured callback invocations. For example, AP startup passes `cfg80211_ap_settings` to `start_ap()`, updates pass `cfg80211_ap_update` to `change_beacon()`, and CSA/color changes use the corresponding settings structs. Station management passes `station_parameters` or link-specific station structs and expects the driver to validate existing state, with `cfg80211_check_station_change()` called by drivers before applying station modifications.

Scan flow is explicitly asynchronous. `scan()` receives a `cfg80211_scan_request`; if it returns success, the request remains valid until the driver completes it with cfg80211 scan completion APIs outside this chunk. BSS discoveries are reported to cfg80211 rather than stored in a driver-local scan list. Scheduled scans follow a similar start/stop request model and can be owned by a netlink port.

Connection flow can be split between low-level MLME callbacks (`auth()`, `assoc()`, `deauth()`, `disassoc()`) and higher-level `connect()`/`disconnect()` callbacks. Successful connects, failures, timeouts, roam events, IBSS joins, and mesh events are asynchronous and documented as requiring cfg80211 notification calls declared elsewhere. Association requests contain refcounting rules for `cfg80211_bss` pointers: successful drivers receive BSS references that must later be returned through cfg80211 result/timeout paths.

Radar/DFS control flows through channel validation helpers, `start_radar_detection()`, `end_cac()`, per-channel DFS state in `struct ieee80211_channel`, and per-link CAC state in `struct wireless_dev`. Channel switching and background CAC have separate callbacks and parameters.

NAN control has strict dependency ordering: start/configure the NMI interface, configure local schedule, add peer/NMI stations and peer schedules, start NDI interfaces, then add NDI stations. Teardown occurs in reverse. The header documents these dependencies because cfg80211 and drivers must reject out-of-order operations.

Wiphy work flow queues `struct wiphy_work` items onto cfg80211-managed work. The timer-backed delayed and hrtimer helpers enqueue regular wiphy work when timers expire; `*_pending()` only reports timer state and cannot prove the function is not queued or running after timer expiry.

## State and Persistence Behavior

Most state in this chunk is in-memory kernel state tied to a wiphy, wireless device, BSS cache entry, or active request. `struct wiphy` persists from allocation to unregister/free and is the canonical advertised capability record. `struct wireless_dev` persists with a netdev or non-netdev wireless object and stores connection, management-registration, per-mode, MLO, CAC, CQM, PMSR, owner-port, and WEXT compatibility state.

`struct cfg80211_bss` entries are maintained by cfg80211, not by individual drivers. IE buffers are RCU-protected and can represent beacon data, probe-response data, hidden beacon relationships, transmitted/non-transmitted multi-BSSID membership, and private driver data sized by `wiphy->bss_priv_size`.

Driver- or firmware-resident state is created and mutated by callbacks: virtual interfaces, MLO links, keys, AP beacons, stations, mesh paths, scan state, connection/roam state, PMKSA/PMK entries, WoWLAN triggers, coalesce rules, NAN functions/schedules, SAR limits, TID configurations, hardware timestamping peers, radar/CAC state, and interface radio masks. cfg80211 passes structured data and expects drivers to keep only what the callback contract allows.

Persistent or suspend-spanning behavior appears in PMKSA caching, PMK offload, WoWLAN/GTK rekey/net-detect, rfkill state, firmware roaming state, WEXT compatibility settings, and regulatory domain state. Most structs do not themselves persist to disk; they describe state held in kernel memory, device firmware, or hardware until explicitly changed, disconnected, stopped, or unregistered.

## Dependencies and Integration Points

This header depends on Linux networking and wireless UAPI definitions: `net_device`, `sk_buff`, `socket`, `rfkill`, `debugfs`, `nl80211.h`, `ieee80211.h`, `if_ether.h`, `netlink`, `regulatory.h`, RCU/list/work/timer primitives, endian/fixed-width integer types, and optional `CONFIG_OF`, `CONFIG_CFG80211`, `CONFIG_PM`, `CONFIG_CFG80211_WEXT`, and `CONFIG_NL80211_TESTMODE` blocks.

The main integration path is nl80211/cfg80211 to driver. Userspace tools such as wpa_supplicant, hostapd, iw, NetworkManager, and regulatory agents communicate through nl80211; cfg80211 validates and transforms requests into these structs and callbacks. Drivers either implement callbacks directly for fullmac devices or receive them through mac80211 for softmac devices.

The kernel networking stack integrates through `struct net_device`, network namespaces, rtnetlink constraints, ethtool firmware/hardware version fields, TX queue length controls, control-port frames, 802.1X authorization flags, QoS maps, multicast-to-unicast conversion, and power-management hooks. Regulatory integration uses channel flags, DFS state, custom regulatory domains, `reg_notifier`, beacon hints, and device-tree frequency limits.

Multi-link operation is woven through AP, station, key, channel, association, station-info, connection, radar, and wireless-device state. Integration code must consistently interpret `link_id == -1`, `valid_links == 0`, MLD addresses, link addresses, per-link BSS pointers, and bitmaps.

## Risks

Locking and lifetime are the dominant risks. Most `cfg80211_ops` callbacks run with the wiphy mutex held; some also have RTNL, and some per-wireless-dev operations are documented as holding the wireless_dev mutex. Drivers must not acquire RTNL from callbacks where the header forbids relying on it. RCU-protected BSS IE pointers require RCU read-side protection, and BSS references from association requests must be released through the documented cfg80211 result/timeout paths.

Callback completion contracts are easy to violate. A driver that returns success from `scan()`, `connect()`, `join_ibss()`, `remain_on_channel()`, `mgmt_tx()`, `sched_scan_start()`, `start_pmsr()`, or similar asynchronous callbacks must later report completion/status through cfg80211. Failing to do so can leak requests, hang userspace operations, or leave cfg80211 state inconsistent with firmware.

Many structs use masks, counts, flexible arrays, and sentinel values. Incorrect `n_*` counts, overlapping iftype masks, unset change masks, missing `filled` bits, misuse of `-1`/`NULL` as "unchanged", or bad flexible-array sizing can lead to silent misconfiguration or memory bugs.

Regulatory and DFS errors have high operational risk. Incorrect channel flags, PSD/max power handling, CAC timing, radar-required checks, 6 GHz VLP/AFC/client/AP restrictions, or S1G/EDMG width validation can allow illegal transmission or reject legal operation.

MLO adds compatibility hazards. Non-MLO paths often use `link_id == -1` or `valid_links == 0`, while MLO paths use per-link arrays and bitmaps. Confusing MLD addresses with link addresses, applying group keys to the wrong link, or skipping valid-link checks can break association, security, or per-link CAC/channel state.

Security-sensitive material is passed through this API: keys, PMKs, SAE passwords, FILS KEK/nonces, GTK rekey data, PMKSA caches, OWE data, control-port frames, management frames, and WoWLAN patterns. Drivers must respect pointer lifetimes, avoid logging secrets, and reject invalid cipher/AKM/control-port combinations.

Feature advertisement must match implementation. If `wiphy` flags, ext_features, interface combinations, scan limits, AKM/cipher suites, WoWLAN/coalesce/PMSR/NAN/SAR capabilities, MBSSID/EMA limits, or callback presence overstate hardware support, nl80211 userspace can request unsupported combinations and expose hard-to-debug failures.

## Test and Validation Signals

Compile coverage should include wireless drivers that consume this header with `CONFIG_CFG80211`, `CONFIG_MAC80211`, `CONFIG_PM`, `CONFIG_OF`, WEXT compatibility, and testmode permutations. Sparse/lockdep/RCU builds are valuable because the header intentionally annotates iftype-data misuse, lock assertions, RCU dereferences, and work serialization.

Registration tests should allocate/register/unregister wiphys, verify namespace handling, parent device binding, permanent and alternate MAC address validation, band/channel/rate advertisement, regulatory notifier behavior, debugfs creation, and safe teardown with active or recently queued wiphy work.

Channel/regulatory tests should cover every `cfg80211_chan_def` width used in the chunk, including 5/10/20/40/80/160/80+80/320, S1G, EDMG, puncturing, PSD power adjustment, DFS usable/required/CAC-time calculations, and `cfg80211_chandef_primary()` puncturing updates.

Callback lifecycle tests should exercise virtual interface add/change/delete, AP start/change/stop, station add/change/delete with `cfg80211_check_station_change()`, mesh path and mesh setup changes, IBSS/OCB join/leave, connect/disconnect/roam, key add/get/delete/default key paths, remain-on-channel and management TX cookies, and scheduled scan start/stop.

Scan/BSS tests should verify active/passive scans, random MAC masking via `get_random_mask_addr()`, split 6 GHz scan parameters, scheduled scan plans/matchsets/relative RSSI, BSS inform paths, hidden SSID and multi-BSSID relationships, RCU-safe IE access, generation counters, and aborted scan reporting.

MLO tests should cover non-MLO and MLO variants for auth/assoc/connect, per-link station add/mod/delete, group vs pairwise key link IDs, AP/STA link channel definitions, `for_each_valid_link()`, `WARN_INVALID_LINK_ID()`, valid-link updates during ML reconfiguration, and TID-to-link mapping.

Power/offload tests should cover WoWLAN triggers and wake reports, GTK rekey data, net-detect matches, packet coalescing, PMKSA/PMK lifetime handling, SAR updates, hardware timestamp peer limits including `CFG80211_HW_TIMESTAMP_ALL_PEERS`, and rfkill polling.

NAN tests should validate start/stop dependency ordering, local and peer schedule replacement rules, NAN function ownership transfer and deletion, NMI/NDI station dependencies, and band/channel constraints.

Userspace compatibility tests should drive nl80211 through hostapd/wpa_supplicant/iw flows for AP, STA, P2P, mesh, IBSS, monitor, TDLS, CQM, QoS map, vendor commands, external auth, OWE, PMSR/FTM, and MBSSID/EMA advertisement where supported.

## Cross-Chunk Notes

This chunk starts at the header guard and ends just after the beginning of the utility-functions section. Later chunks of the same file will contain many cfg80211 event/reporting functions referenced by the callback documentation here, plus additional wireless utility declarations. The merge lane should preserve that split: this chunk defines the main driver-facing data model and callback table, while later chunks complete the notification and helper API surface.
