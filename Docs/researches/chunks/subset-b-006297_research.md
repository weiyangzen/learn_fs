# sources/distributed-fs/ceph-client/net/wireless/nl80211.c lines 18681-23040

Chunk research for `subset-b-006297`. This is a partial oversized-file report for the tail of `nl80211.c`; the merge lane should combine it with earlier chunks before producing the final source-tree-aligned per-file research document.

## Purpose

This chunk covers the end of nl80211 command handlers and the registration/notification tail of the cfg80211 netlink interface. It does three broad jobs:

- validates and dispatches recent station-side MLO controls such as TID-to-link mapping, association MLO reconfiguration, and EPCS toggling;
- defines the generic-netlink operation metadata, pre/post command locking and object lookup behavior, and SAR command parsing;
- exposes cfg80211-to-userspace event emitters for wiphy/interface lifecycle, scans, regulatory updates, MLME/connect/roam/disconnect, MLO link changes, mesh/IBSS peer events, management/control-port frames, CQM, rekey/PMKSA, channel/radar/color changes, WoWLAN, TDLS, FT, external auth, OWE, EPCS, NAN, and nl80211 module init/exit.

The code is mostly glue between cfg80211 internal state and generic netlink messages. It converts driver/cfg80211 callbacks into `NL80211_CMD_*` events and converts privileged userspace commands into `rdev_*` cfg80211 operation calls.

## Important APIs, Types, and Functions

- `nl80211_assoc_ml_reconf()` builds a `struct cfg80211_ml_reconf_req` from `NL80211_ATTR_MLO_LINKS`, `NL80211_ATTR_MLO_RECONF_REM_LINKS`, and optional `NL80211_ATTR_ASSOC_MLD_EXT_CAPA_OPS`, validates that added/removed link sets are coherent with `wdev->valid_links`, calls `cfg80211_assoc_ml_reconf()`, and drops BSS references with `cfg80211_put_bss()`.
- `nl80211_epcs_cfg()` accepts `NL80211_ATTR_EPCS` for connected station/P2P-client interfaces and dispatches to `rdev_set_epcs()`.
- `NL80211_FLAG_*`, `INTERNAL_FLAG_SELECTORS`, `nl80211_internal_flags[]`, and `IFLAGS()` form a compile-time selector layer for `genl_split_ops.internal_flags`. The selector table encodes common command prerequisites: wiphy/netdev/wdev lookup, RTNL retention, netdev-up checks, MLO link-id validation, MLO rejection, wiphy mutex suppression, and sensitive SKB clearing.
- `nl80211_pre_doit()` is the central generic-netlink pre-handler. It grabs RTNL, resolves the requested wiphy/wdev/netdev into `info->user_ptr[]`, holds netdev references, enforces running-state and MLO link-id policy, optionally locks `rdev->wiphy.mtx`, and releases RTNL unless the command requested it.
- `nl80211_post_doit()` releases references and locks established by `nl80211_pre_doit()`. It also zeros the netlink payload for commands marked `NL80211_FLAG_CLEAR_SKB`, which covers key/PMK/vendor-sensitive messages.
- `nl80211_set_sar_sub_specs()` and `nl80211_set_sar_specs()` parse nested `NL80211_ATTR_SAR_SPEC` data into `struct cfg80211_sar_specs`, validate SAR type/range count/range-index uniqueness, call `rdev_set_sar_specs()`, and free the temporary flex allocation.
- `nl80211_ops[]`, `nl80211_small_ops[]`, and `nl80211_fam` register the nl80211 generic-netlink family. The large `nl80211_small_ops[]` table maps commands to handlers, privilege flags (`GENL_ADMIN_PERM` or `GENL_UNS_ADMIN_PERM`), validation mode, dump handlers, and internal flag selectors.
- Notification helpers such as `nl80211_notify_wiphy()`, `nl80211_notify_iface()`, `nl80211_send_scan_start()`, `nl80211_send_scan_msg()`, `nl80211_common_reg_change_event()`, and `nl80211_send_mlme_event()` build `sk_buff` messages with `nl80211hdr_put()`, fill netlink attributes with `nla_put*()`, close with `genlmsg_end()`, and multicast or unicast through `nl80211_fam`.
- Exported cfg80211 callback APIs in this chunk include `cfg80211_rx_unprot_mlme_mgmt()`, `cfg80211_links_removed()`, `nl80211_mlo_reconf_add_done()`, `cfg80211_notify_new_peer_candidate()`, `cfg80211_assoc_comeback()`, `cfg80211_ready_on_channel()`, `cfg80211_remain_on_channel_expired()`, `cfg80211_tx_mgmt_expired()`, `cfg80211_new_sta()`, `cfg80211_del_sta_sinfo()`, `cfg80211_conn_failed()`, `cfg80211_rx_spurious_frame()`, `cfg80211_rx_unexpected_4addr_frame()`, `cfg80211_rx_control_port()`, CQM notification exports, rekey/PMKSA/channel/radar/color/station-opmode/probe/WoWLAN/TDLS/FT/external-auth/OWE/NAN exports, and `nl80211_init()`/`nl80211_exit()`.

## Control Flow

Incoming userspace commands flow through the generic-netlink family:

1. Generic netlink chooses an entry from `nl80211_ops[]` or `nl80211_small_ops[]`.
2. `nl80211_pre_doit()` interprets the entry's internal selector, resolves the required kernel object from netlink attributes, sets `info->user_ptr[0]` to the `cfg80211_registered_device`, sets `info->user_ptr[1]` to the requested `net_device` or `wireless_dev`, validates up/MLO constraints, and establishes RTNL and/or wiphy locking.
3. The command-specific `doit` handler reads validated `info->attrs[]`, performs command-specific checks, and calls cfg80211/rdev helpers such as `rdev_set_ttlm()`, `cfg80211_assoc_ml_reconf()`, `rdev_set_epcs()`, or `rdev_set_sar_specs()`.
4. `nl80211_post_doit()` unwinds netdev references, wiphy locks, RTNL locks, and optionally scrubs sensitive request payloads.

Outgoing kernel-to-userspace events follow a repeated pattern:

1. A driver/cfg80211 event callback obtains `rdev` from `wiphy_to_rdev()` and allocates an `sk_buff` sized for the expected attributes.
2. The helper starts a generic-netlink message with `nl80211hdr_put()`, adds identifying attributes (`NL80211_ATTR_WIPHY`, `NL80211_ATTR_IFINDEX`, `NL80211_ATTR_WDEV`, MAC/BSSID/link IDs), then adds event-specific attributes.
3. Most events multicast to a group (`NL80211_MCGRP_CONFIG`, `SCAN`, `REGULATORY`, `MLME`, or `NAN`) within `wiphy_net(&rdev->wiphy)`. A smaller set unicasts to owner ports such as `wdev->conn_owner_nlportid`, `wdev->owner_nlportid`, registered beacon listeners, or unexpected-frame subscribers.
4. Attribute failures cancel/free the message and generally drop the notification rather than propagating an error to drivers, except for APIs declared to return status such as `nl80211_send_mgmt()`, `cfg80211_bss_color_notify()`, and `cfg80211_external_auth_request()`.

Notable flows include:

- MLO association reconfiguration adds links by parsing BSS references from nested link attributes, computes `add_links`, merges it with optional `rem_links`, rejects duplicate/no-op/invalid combinations, then hands the request to cfg80211 and releases temporary BSS refs.
- Connect and roam result builders support non-MLO and MLO reporting. For MLO, they precompute nested link attribute size, add top-level MLD/BSSID identity, and emit per-link nested entries with link ID, BSSID, link MAC, and status where applicable.
- `cfg80211_links_removed()` is stateful: under wiphy lock it validates station/client MLO state, releases link BSSes, clears bits from `wdev->valid_links`, and then emits `NL80211_CMD_LINKS_REMOVED`.
- CQM RSSI notification is split: `cfg80211_cqm_rssi_notify()` records the latest RSSI event under RCU and queues `wdev->cqm_rssi_work`; `cfg80211_cqm_rssi_notify_work()` runs later under wiphy context, optionally updates range thresholds, then emits a CQM event.
- `nl80211_netlink_notify()` handles userspace socket death. On `NETLINK_URELEASE`, it marks owned scheduled scans and wireless devices as dead, queues cleanup/disconnect work, releases peer-measurement state, removes beacon registrations, and notifies regulatory code.

## State and Persistence Behavior

This code does not persist state outside kernel memory, but it mutates several long-lived cfg80211 structures:

- `info->user_ptr[]` is used as transient per-command context between `pre_doit`, command handlers, and `post_doit`.
- Netdev references acquired with `dev_hold()` are released in `post_doit()` or the `pre_doit()` error path.
- `rdev->cur_cmd_info` is temporarily set around `rdev_set_sar_specs()` so lower layers can inspect the active netlink command.
- `wdev->valid_links` is read by MLO validation and updated by `cfg80211_links_removed()`. Link BSS references are released before clearing removed link bits.
- `wdev->unprot_beacon_reported` rate-limits unprotected beacon reports to roughly one every ten seconds.
- `wdev->cqm_config` fields store the latest RSSI event value/type before deferred work sends notification and possibly updates threshold ranges.
- `wdev->owner_nlportid`, `wdev->conn_owner_nlportid`, `wdev->unexpected_nlportid`, `rdev->crit_proto_nlportid`, scheduled-scan owner port IDs, beacon registration port IDs, and NAN owner ports control whether events are unicast, multicast, or ignored.
- `wdev->u.nan.cluster_id` is updated when a NAN cluster is joined.
- Interface/channel state is updated for channel switch notifications: station/P2P-client BSS entries, mesh chandefs, AP link chandefs, and IBSS chandef are synchronized before the event is emitted.

## Dependencies and Integration Points

- Generic netlink: `struct genl_family`, `genl_ops`, `genl_small_ops`, `genl_register_family()`, `genlmsg_multicast_netns()`, `genlmsg_multicast_allns()`, `genlmsg_unicast()`, and netlink notifier registration.
- Netlink attributes: `nla_parse_nested()`, `nla_for_each_nested()`, `nla_put*()`, `nla_nest_start*()`, `nla_nest_end()`, `nla_reserve()`, `nla_memcpy()`, and 64-bit padding conventions.
- cfg80211 core: `cfg80211_registered_device`, `wireless_dev`, `wiphy`, rdev operation wrappers, regulatory helpers, scheduled-scan lists, peer measurement cleanup, BSS/link management, channel checks, DFS updates, and tracepoints.
- Wireless protocol models: nl80211 commands/attributes, MLO link IDs and valid-link bitmasks, SAR capability structures, FILS/PMK/PMKID material, MLME frames, control-port frames, CQM events, DFS/radar/color/channel switch events, WoWLAN triggers, TDLS operations, FT/OWE/external auth, and NAN events.
- Kernel synchronization/lifetime: RTNL, wiphy mutex, RCU list traversal, spin locks for beacon registrations, work queues for deferred destroy/disconnect/scheduled-scan/CQM handling, `GFP_KERNEL` versus `GFP_ATOMIC` allocation contexts, and exported symbols for driver/cfg80211 callers.

## Risks and Edge Cases

- `nl80211_pre_doit()` is central and easy to misuse from the operation table. A wrong selector can omit required locking, fail to clear sensitive request data, require or reject MLO link IDs incorrectly, or pass a `wireless_dev` where a `net_device` is expected.
- MLO validation is intentionally strict. Commands marked `NL80211_FLAG_MLO_VALID_LINK_ID` reject link IDs for non-MLO devices and require valid link IDs for MLO devices; commands marked `NL80211_FLAG_MLO_UNSUPPORTED` reject both an explicit link ID and any MLO-capable `wdev`. Command-specific exceptions in the op table should be checked carefully.
- `NL80211_FLAG_CLEAR_SKB` scrubs the netlink payload after handling, but only for commands whose op-table entry includes the flag. Key, PMK, rekey, auth/assoc/connect, vendor, and similar sensitive command entries need continued audit coverage.
- Many notification functions silently drop events on allocation or `nla_put` failure. This is normal for asynchronous kernel notifications, but userspace may miss important state transitions under memory pressure.
- Several helpers assume caller-side locking or valid state and use `WARN_ON()`/`lockdep_assert_wiphy()`, especially MLO link removal and channel switch paths. Calling them from the wrong context can leave state/event ordering inconsistent.
- `cfg80211_del_sta_sinfo()` releases `sinfo` content only on allocation failure; if `nl80211_send_station()` fails after allocation, the function frees the skb and returns without calling `cfg80211_sinfo_release_content(sinfo)`, so callers and adjacent code should be checked in other chunks for ownership expectations.
- `cfg80211_report_obss_beacon_khz()` holds `beacon_registrations_lock` while allocating and unicasting messages to registered port IDs. This uses `GFP_ATOMIC`, but extended work under the spin lock can still be sensitive to listener count and message size.
- `nl80211_netlink_notify()` traverses cfg80211 device lists under RCU while scheduling asynchronous cleanup. Correctness depends on referenced objects remaining valid under the cfg80211 lifetime rules in surrounding code.
- Historical external-auth compatibility intentionally sends SAE AKM suites as big-endian in one case. Tests must preserve that quirk because old and new userspace may both rely on it.
- Some events multicast without a full identifier set. For example EPCS changed emits only the enabled flag and command header in this chunk; the merge lane should inspect adjacent context or upstream expectations before judging whether this is intentional or incomplete.

## Test Signals

Useful validation signals for this chunk include:

- Generic-netlink command tests that exercise each internal selector class: wiphy-only, netdev, wdev, netdev-up, RTNL-retained, no-wiphy-mutex, MLO-valid-link, MLO-unsupported, and clear-SKB commands.
- MLO station tests for `NL80211_CMD_SET_TID_TO_LINK_MAPPING`, `NL80211_CMD_ASSOC_MLO_RECONF`, `NL80211_CMD_LINKS_REMOVED`, connect result, roam result, OWE update, channel/color events, and AP stopped events with and without `NL80211_ATTR_MLO_LINK_ID`.
- Netlink-policy/fuzz tests for nested SAR specs, including duplicate range indexes, out-of-range indexes, mismatched SAR type, empty specs, and more specs than capability ranges.
- Event-shape tests using nlmon/libnl to verify emitted attributes for scan start/done/abort, scheduled scan, regulatory changes, MLME auth/assoc/deauth/disassoc, connect/roam/disconnect, management RX/TX status, control-port frames, CQM, rekey/PMKSA, DFS/radar, WoWLAN, TDLS, FT, external auth, OWE, EPCS, and NAN.
- Socket-lifetime tests where the controlling netlink port exits while owning scheduled scans, interfaces, connections, beacon registrations, peer measurements, critical protocol ownership, or NAN ownership.
- Concurrency tests with RTNL/wiphy lockdep enabled, especially command paths that set `NL80211_FLAG_NO_WIPHY_MTX`, notification callbacks requiring wiphy lock, RCU CQM access, and beacon registration spin-lock paths.
- Fault-injection tests for `nlmsg_new()` and `nla_put*()` failures to confirm messages are freed/cancelled and state mutations either happen before intentional notification loss or are avoided on error.
- Security regression tests that verify sensitive request payloads are cleared for flagged commands and that unprivileged/admin permission flags in `nl80211_small_ops[]` match the intended user-space privilege boundary.
