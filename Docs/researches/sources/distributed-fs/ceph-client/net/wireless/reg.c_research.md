# sources/distributed-fs/ceph-client/net/wireless/reg.c

## Purpose

`reg.c` implements cfg80211's wireless regulatory infrastructure. It owns the central regulatory domain, per-wiphy regulatory domains, regulatory request queueing and processing, regulatory database loading and validation, channel flag/power/DFS updates, user/driver/core/country-IE hint conflict handling, beacon hints, indoor state, active-interface enforcement after regulatory changes, and DFS state propagation across compatible wiphys.

## Important APIs, Types, and Functions

- Global regulatory state includes `cfg80211_regdomain`, `cfg80211_world_regdom`, `last_request`, `reg_requests_list`, beacon hint lists, `regdb`, user alpha2 cache, `cfg80211_user_regdom`, indoor state, and delayed/work items.
- Initialization/exit: `regulatory_init()`, `regulatory_init_db()`, and `regulatory_exit()`.
- Domain setting and lookup: `set_regdom()`, `get_wiphy_regdom()`, `reg_get_dfs_region()`, `freq_reg_info()`, `reg_get_max_bandwidth()`, and `reg_query_regdb_wmm()`.
- Request entry points: `regulatory_hint_user()`, `regulatory_hint()`, `regulatory_hint_country_ie()`, `regulatory_hint_found_beacon()`, `regulatory_hint_disconnect()`, `regulatory_hint_indoor()`, and `regulatory_netlink_notify()`.
- Per-wiphy APIs: `wiphy_regulatory_register()`, `wiphy_regulatory_deregister()`, `wiphy_apply_custom_regulatory()`, `regulatory_set_wiphy_regd()`, and `regulatory_set_wiphy_regd_sync()`.
- Channel enforcement: `handle_channel()`, `handle_band()`, `wiphy_update_regulatory()`, `update_all_wiphy_regulatory()`, `reg_process_ht_flags()`, `reg_check_channels()`, and `reg_leave_invalid_chans()`.
- DFS support: `reg_dfs_domain_same()`, `regulatory_pre_cac_allowed()`, `regulatory_propagate_dfs_state()`, `cfg80211_check_and_end_cac()`.
- Regulatory database support: `valid_regdb()`, `query_regdb_file()`, `regdb_fw_cb()`, `reg_reload_regdb()`, `regdb_query_country()`, WMM parsing, and optional PKCS#7 signature verification.

## Control Flow

Initialization creates a faux `regulatory` device, points `cfg80211_regdomain` at the static world domain, initializes user alpha2 as unset, and later loads built-in keys and requests `regulatory.db`. The initial core hint queues a request for the world alpha2, and a non-world module parameter queues a user hint.

All regulatory hints are converted into `struct regulatory_request`, uppercased, appended to `reg_requests_list`, and processed by `reg_work`. `reg_process_pending_hints()` serializes processing: if the previous `last_request` is not processed it waits; otherwise it pops one request, notifies self-managed wiphys for user hints, and dispatches by initiator. Core, user, driver, and country-IE requests each have treatment logic that can accept, ignore, intersect with the current domain, or report already-set state.

Accepted requests call `reg_query_database()`, which first attempts the firmware regulatory database and then CRDA when configured. When a matching regdomain arrives, `set_regdom()` verifies that it matches the outstanding unprocessed request, validates or intersects domains as required, updates central and/or per-wiphy regdomain pointers, updates every wiphy's channels, prints/debug-notifies the domain, sends nl80211 regulatory events, and marks the request processed. Errors restore regulatory settings and may reset user state.

Regdb loading validates magic, version, optional signature, country collection bounds, rule bounds, WMM rule sanity, and optional CAC/WMM fields. Firmware is loaded asynchronously for normal queries and synchronously for reload. Parsed rules are translated to `ieee80211_reg_rule`, including flags, max EIRP, DFS CAC time, and WMM AC parameters.

Channel update flow obtains the applicable regdomain, finds a rule for each channel's center frequency and bandwidth, maps regulatory flags to `IEEE80211_CHAN_*`, sets max power/antenna/PSD/DFS CAC, handles adjacent rules for 20 MHz channels spanning two rules, applies beacon hints, recomputes HT40 plus/minus flags, calls driver notifiers, and schedules delayed active-interface enforcement. Strict driver domains can update `orig_*` channel fields so the driver's regulatory baseline is preserved.

Beacon hints are separate from country IEs. Found beacons on eligible world-roaming channels are queued, processed by work, remembered for future wiphys/reg changes, and can clear `IEEE80211_CHAN_NO_IR` while sending nl80211 beacon hint events.

Disconnect restore clears stale country-IE/beacon information unless all devices ignore country IEs, resets to world/cached/user/module domains, preserves pending requests, and requeues work. Indoor state can be controlled by a netlink portid; if the controlling port disappears or clears indoor mode, channel enforcement is scheduled.

DFS propagation requires RTNL and a valid chandef. It applies DFS state to other wiphys in the same DFS domain, schedules DFS channel updates, ends conflicting CAC where needed, and sends radar notifications.

## State and Persistence Behavior

Central regulatory state is RCU-protected and mostly mutated under RTNL. `cfg80211_regdomain` points to the active global domain, while each wiphy may have `wiphy->regd` for strict, custom, driver, or self-managed domains. Old domains are freed with RCU. `last_request` persists the most recent request and gates database responses through `reg_is_valid_request()`.

User preference persists in `user_alpha2` and a copied `cfg80211_user_regdom`, allowing restore from cached data after disconnect. The static world domain remains as a fallback, while loaded `regdb` persists until reload or exit. Beacon hints persist in `reg_beacon_list` and are replayed to new wiphys until regulatory restore/disconnect clears them.

Channel state persists in each `ieee80211_channel`: flags, original flags, max power, max regulatory power, max antenna gain, DFS state/entry time, CAC time, beacon-found state, and PSD. Regulatory changes may also force active interfaces to leave invalid channels after a grace period.

Self-managed wiphy requests persist temporarily in `rdev->requested_regd` until processed, then become `wiphy->regd`. Indoor state persists globally with a controlling netlink portid when userspace owns it.

## Dependencies and Integration Points

The file depends on Linux firmware loading, optional CRDA userspace uevents, optional PKCS#7 verification and built-in certificates, RCU, RTNL, workqueues, cfg80211 channel/regdomain helpers, nl80211 notifications, `rdev-ops.h`, and wiphy/wireless_dev lists. It integrates with drivers through regulatory hints, custom/self-managed regdomain APIs, reg notifiers, DFS callbacks, and channel validity enforcement. Userspace sees behavior through nl80211 regulatory events, `iw reg` flows, and firmware database reloads.

## Risks and Edge Cases

This is concurrency-sensitive code. Request processing spans spinlocks, RTNL, RCU, workqueues, delayed work, firmware callbacks, and optional CRDA timeout work. A bad `last_request` transition can make valid database responses fail or stale responses apply. Regdomain memory ownership is delicate because some domains are static, some are copied, and some are consumed by `set_regdom()`.

Regulatory correctness is safety-sensitive. Incorrect rule intersection, flag mapping, AUTO_BW handling, country-IE conflict logic, or power selection can allow illegal transmissions or unnecessarily disable channels. Active-interface enforcement is delayed by design; tests must account for the grace period. Beacon hints intentionally relax `NO_IR` only under world roaming and non-radar constraints.

Firmware parsing and signature verification are security-sensitive because malformed regulatory databases must not cause out-of-bounds reads or invalid rules. The code uses many bounds checks, but new optional fields must preserve alignment and length validation.

## Test Signals

Useful signals include cfg80211 regulatory selftests, `iw reg set/get`, regulatory.db reload, module parameter boot tests, driver regulatory hints, country IE association flows, beacon-hint scans on channels 12-14 and non-radar 5 GHz, self-managed wiphy tests, and DFS CAC/radar propagation tests. Build configs should cover CRDA on/off, signed regdb on/off, cellular hints on/off, module and built-in cfg80211, and multiple registered wiphys with strict/custom/self-managed flags.
