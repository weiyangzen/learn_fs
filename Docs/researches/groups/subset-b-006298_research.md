# subset-b-006298 Wireless Regulatory and Measurement Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/nl80211.h -->
# sources/distributed-fs/ceph-client/net/wireless/nl80211.h

## Purpose

`nl80211.h` is an internal cfg80211 header that publishes the nl80211-facing helpers used by other wireless core files. It does not implement netlink policy itself; it declares initialization/teardown, message construction, channel/MAC parsers, notification emitters, and the peer-measurement start hook used by `pmsr.c`. It is the local bridge between cfg80211 state machines and the generic netlink command/event ABI.

## Important APIs, Types, and Functions

- `nl80211_init()` and `nl80211_exit()` register and unregister the nl80211 generic netlink family.
- `nl80211hdr_put()` starts an nl80211 message in an skb for a command, portid, sequence, and flags.
- `nl80211_put_sta_rate()` serializes `struct rate_info` into a netlink attribute.
- `wdev_id()` composes the stable nl80211 wireless-device id from `wireless_dev.identifier` and the registered wiphy index.
- `nl80211_parse_chandef()` and `nl80211_parse_random_mac()` are parser entry points used by command handlers such as peer measurement.
- Notification helpers cover wiphy/interface changes, scans, scheduled scans, regulatory changes, authentication/association/deauth/disassoc/connect/roam/disconnect events, MIC failures, beacon hints, management frames, radar events, AP stop, MLO reconfiguration, and port authorization.
- `nl80211_pmsr_start()` declares the peer-measurement command handler implemented in `pmsr.c`.

## Control Flow

Most declarations are called from cfg80211 operation code after it has validated state and taken the expected locks. Event helpers build an skb with `nl80211hdr_put()`, fill attributes, and send either unicast replies or multicast notifications. The inline regulatory helpers select between `NL80211_CMD_REG_CHANGE` and `NL80211_CMD_WIPHY_REG_CHANGE` while sharing `nl80211_common_reg_change_event()`.

## State and Persistence Behavior

The header itself stores no state. The only inline state derivation is `wdev_id()`, whose result depends on persistent `wireless_dev` and `cfg80211_registered_device` identifiers. All other state is owned by the implementations in nl80211, cfg80211 core, regulatory, scan, and connection code.

## Dependencies and Integration Points

The file includes `core.h` and relies on cfg80211/nl80211 types such as `cfg80211_registered_device`, `wireless_dev`, `regulatory_request`, `cfg80211_chan_def`, `cfg80211_rx_assoc_resp_data`, `cfg80211_connect_resp_params`, and `cfg80211_pmsr_request`. It is included by `ocb.c`, `pmsr.c`, `reg.c`, and many other wireless core files that need to emit user-visible events.

## Risks and Edge Cases

The main risk is ABI drift: declarations here must match nl80211 implementation signatures and the UAPI attribute semantics. `wdev_id()` depends on the high 32 bits holding `wiphy_idx`; changing identifier allocation or wiphy indexing would break userspace references. Parser helpers must remain consistent with nl80211 policies or callers can accept malformed requests.

## Test Signals

Useful signals include nl80211 command/event selftests, `iw` scan/connect/regulatory flows, peer-measurement requests, and build coverage for files that include this header. Runtime validation should watch for malformed netlink responses, missing multicast events, and stable `NL80211_ATTR_WDEV` ids across interface operations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/nl80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/ocb.c -->
# sources/distributed-fs/ceph-client/net/wireless/ocb.c

## Purpose

`ocb.c` implements cfg80211 support for Outside the Context of a BSS mode. It exposes join and leave helpers that validate interface type and driver capability, call the driver through `rdev-ops.h`, and persist the active OCB channel definition in `wireless_dev` state.

## Important APIs, Types, and Functions

- `cfg80211_join_ocb()` joins an OCB channel. It requires the wiphy lock, `NL80211_IFTYPE_OCB`, a driver `join_ocb` op, and a non-null channel in `struct ocb_setup`.
- `cfg80211_leave_ocb()` leaves OCB mode. It requires the same interface type and a driver `leave_ocb` op, and returns `-ENOTCONN` when no OCB channel is active.
- `rdev_join_ocb()` and `rdev_leave_ocb()` are the traced driver-dispatch wrappers used after local validation.
- `wdev->u.ocb.chandef` is the persistent cfg80211 copy of the active OCB channel state.

## Control Flow

Join first asserts the wiphy lock, rejects non-OCB interfaces and drivers without OCB support, checks that the requested chandef has a channel, then dispatches to the driver. Only after a zero driver return does it copy `setup->chandef` into `wdev->u.ocb.chandef`.

Leave similarly asserts locking and validates type/op support. It rejects leave when `wdev->u.ocb.chandef.chan` is unset. On successful driver leave it zeroes the stored chandef, making later regulatory checks and leave attempts see the interface as disconnected from OCB.

## State and Persistence Behavior

The only persistent state is `wdev->u.ocb.chandef`. It is updated only after driver success and cleared only after driver success, so cfg80211 state mirrors the driver's accepted transition. Failed joins/leaves do not mutate stored state.

## Dependencies and Integration Points

The file depends on Linux 802.11 definitions, `cfg80211.h`, `core.h`, `nl80211.h`, and `rdev-ops.h`. The regulatory code in `reg.c` later checks `wdev->u.ocb.chandef` in `reg_wdev_chan_valid()` and can force leave through `cfg80211_leave()` if an active OCB channel becomes invalid.

## Risks and Edge Cases

The lock assertion is important because cfg80211 and driver state must not race. A missing channel in the setup is treated as a warning and `-EINVAL`, since later code assumes a valid chandef. If a driver returns success without actually leaving or joining, cfg80211's stored OCB state will diverge from hardware behavior.

## Test Signals

OCB tests should cover join/leave success, unsupported interface type, missing driver ops, invalid chandef, duplicate leave returning `-ENOTCONN`, and regulatory changes that invalidate an OCB chandef. Tracepoints from `rdev_join_ocb` and `rdev_leave_ocb` confirm driver dispatch and return status.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/ocb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/of.c -->
# sources/distributed-fs/ceph-client/net/wireless/of.c

## Purpose

`of.c` applies device-tree frequency limits to a wiphy. It reads the optional `ieee80211-freq-limit` property, validates pairs of start/end kHz values, and disables any advertised channels whose 20 MHz operating bandwidth does not fit within one of the declared ranges.

## Important APIs, Types, and Functions

- `wiphy_read_of_freq_limits()` is exported for drivers/core code to call after wiphy bands are populated.
- `wiphy_freq_limits_apply()` iterates all `wiphy->bands[]` and marks out-of-range channels with `IEEE80211_CHAN_DISABLED`.
- `wiphy_freq_limits_valid_chan()` checks whether a channel center frequency with a fixed 20 MHz bandwidth fits a parsed `ieee80211_freq_range`.
- Device-tree helpers include `dev_of_node()`, `of_find_property()`, and `of_prop_next_u32()`.

## Control Flow

The exported function obtains the wiphy device, exits if no OF node/property exists, and validates that the property length is non-zero, u32-aligned, and composed of start/end pairs. It allocates an array of frequency ranges, parses each pair, rejects zero or inverted ranges, then applies the ranges. Cleanup always frees the temporary array and logs parse/allocation errors through the device.

## State and Persistence Behavior

The parsed range array is temporary. Persistent effects are direct mutations of `struct ieee80211_channel.flags`: channels outside the OF limits are permanently disabled for the registered wiphy unless later code explicitly rebuilds or restores channel flags. The code skips already disabled channels and never re-enables anything.

## Dependencies and Integration Points

The file depends on Linux OF/property APIs, cfg80211 frequency helpers, and `core.h`. It integrates with driver registration paths that call `wiphy_read_of_freq_limits()` and with later regulatory processing, which sees OF-disabled channels as part of each channel's flag baseline.

## Risks and Edge Cases

The property format is strict; malformed length or invalid ranges abort the whole application. The check uses a fixed 20 MHz bandwidth, so very narrow channels are not specially handled here. Because the function only disables channels, an overly restrictive device-tree property can remove channels even if regulatory data would otherwise allow them.

## Test Signals

Device-tree tests should cover missing property, bad length, zero/inverted ranges, multiple valid ranges, and mixed bands. Runtime signals include `pr_debug()` lines for disabled frequencies and observing `IEEE80211_CHAN_DISABLED` in wiphy channel dumps or `iw list`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/pmsr.c -->
# sources/distributed-fs/ceph-client/net/wireless/pmsr.c

## Purpose

`pmsr.c` implements nl80211 peer measurement request handling and result reporting for cfg80211. Its current measurement type is FTM ranging. The file parses nested nl80211 request attributes, validates them against `wiphy->pmsr_capa`, starts driver work through `start_pmsr`, tracks active requests on `wireless_dev`, emits result/complete netlink messages, and aborts outstanding work when a netlink port or wireless device disappears.

## Important APIs, Types, and Functions

- `nl80211_pmsr_start()` is the command entry point declared in `nl80211.h`.
- `pmsr_parse_peer()` parses one peer: MAC address, nested channel definition, request flags, AP TSF reporting, and measurement type data.
- `pmsr_parse_ftm()` validates and fills `cfg80211_pmsr_request_peer.ftm` fields, including bandwidth, preamble, ASAP/non-ASAP, burst counts, FTM-per-burst, retries, LCI/civic location, trigger/non-trigger based ranging, LMR feedback, BSS color, and RSTA support.
- `cfg80211_pmsr_report()` sends `NL80211_CMD_PEER_MEASUREMENT_RESULT` for one peer result.
- `cfg80211_pmsr_complete()` sends `NL80211_CMD_PEER_MEASUREMENT_COMPLETE`, removes the request from `wdev->pmsr_list`, and frees it if not already moved to abort cleanup.
- `cfg80211_pmsr_wdev_down()` and `cfg80211_release_pmsr()` mark requests for abort when an interface goes down or the originating netlink port is released.
- `cfg80211_pmsr_free_wk()` runs deferred abort processing under the wiphy guard.

## Control Flow

Request start first checks that the device advertises PMSR capabilities and that `NL80211_ATTR_PEER_MEASUREMENTS` contains peers. It counts peers and enforces `max_peers`, allocates a flexible `cfg80211_pmsr_request`, copies timeout and MAC randomization settings, then parses each peer. MAC randomization is rejected unless the device advertises it; otherwise the request uses the wdev address and a broadcast mask. A cookie and sender portid are assigned before dispatch to `rdev_start_pmsr()`. Only successful driver start links the request into `wdev->pmsr_list` and returns the cookie through extack.

FTM parsing starts with existing channel data and capability checks. Non-DMG bands require an explicit preamble. Capability flags gate ASAP, non-ASAP, LCI, civic location, trigger based, non-trigger based, LMR feedback, and RSTA. The parser rejects inconsistent combinations such as both trigger modes, non-EDCA modes without HE preamble, LMR feedback on EDCA ranging, BSS color on EDCA ranging, RSTA without LMR feedback, and too many FTMs per burst.

Reporting builds a nested peer-measurement response with wiphy, wdev id, cookie, peer address, status, host time, optional AP TSF, final flag, and type-specific FTM response attributes. Complete sends a simpler completion event and then carefully removes/frees the request unless abort processing has already moved it out of the active list.

Abort flow is port and device driven. `cfg80211_release_pmsr()` zeroes `nl_portid` for matching requests and schedules work. `cfg80211_pmsr_wdev_down()` zeroes all portids, synchronizes outstanding cleanup work, aborts immediately if needed, and warns if the list is not empty. `cfg80211_pmsr_process_abort()` moves zero-portid requests to a local free list under `pmsr_lock`, calls driver `abort_pmsr`, and frees them.

## State and Persistence Behavior

Active PMSR requests persist in `wdev->pmsr_list`, protected by `wdev->pmsr_lock` for list mutation and portid changes. Each request stores peers, parsed per-peer FTM settings, timeout, randomized/source MAC parameters, cookie, and originating netlink portid. Cookie assignment uses cfg80211's registered-device cookie allocator.

Request lifetime is split between normal driver completion and abort cleanup. Normal completion may race with abort processing, so `cfg80211_pmsr_complete()` only frees if the request is still present in `wdev->pmsr_list`. Aborted requests are identified by `nl_portid == 0`.

## Dependencies and Integration Points

The file depends on nl80211 nested attributes and policies, `nl80211_parse_chandef()`, `nl80211_parse_random_mac()`, `nl80211hdr_put()`, `nl80211_put_sta_rate()`, `wdev_id()`, cfg80211 cookie assignment, tracepoints, and `rdev_start_pmsr()`/`rdev_abort_pmsr()`. Drivers implement the actual ranging operation and call `cfg80211_pmsr_report()` and `cfg80211_pmsr_complete()`.

## Risks and Edge Cases

The parser reuses `info->attrs` while parsing peer channel definitions; callers must not rely on original attrs after that point. Missing `return -EINVAL` after unsupported LCI/civicloc extack messages means those flags are noted but not rejected in this code path, which may be intentional compatibility or a risk if drivers assume unsupported requests were filtered. Result messages allocate only `NLMSG_DEFAULT_SIZE`, so oversized LCI/civic location blobs can fail with rate-limited errors. Lifetime races between completion and abort are subtle and depend on list membership under spinlock.

## Test Signals

Tests should exercise unsupported PMSR, missing peer data, max peer overflow, invalid chandefs, MAC randomization support, every FTM capability gate, trigger/non-trigger combinations, result serialization for success and failure, complete events, netlink-port release abort, and wdev-down abort. Tracepoints for PMSR start/report/complete plus nl80211 event captures provide runtime confirmation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/pmsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/radiotap.c -->
# sources/distributed-fs/ceph-client/net/wireless/radiotap.c

## Purpose

`radiotap.c` implements the exported radiotap iterator used to parse variable-length IEEE 802.11 radiotap headers. It validates header length/version, walks normal and extended present bitmaps, handles per-field alignment relative to the radiotap header, supports vendor namespaces, and returns one present argument at a time to callers.

## Important APIs, Types, and Functions

- `rtap_namespace_sizes[]` defines alignment and size for known standard radiotap fields such as TSFT, FLAGS, RATE, CHANNEL, MCS, AMPDU status, and VHT.
- `radiotap_ns` describes the standard namespace.
- `ieee80211_radiotap_iterator_init()` initializes `struct ieee80211_radiotap_iterator` and validates header bounds.
- `ieee80211_radiotap_iterator_next()` advances to the next present argument and returns `0`, `-ENOENT`, or `-EINVAL`.
- `find_ns()` selects a registered vendor namespace by OUI and subnamespace.

## Control Flow

Initialization rejects packets shorter than a radiotap header, non-zero radiotap versions, and `it_len` values larger than the available packet length. It seeds bitmap and argument pointers from `it_present` and skips any extended present words, with bounds checks before each dereference. The iterator starts in the standard namespace.

`iterator_next()` loops over bits in the current present bitmap. For absent bits it advances. For present bits it obtains the field alignment and size, applies padding relative to the radiotap header start, checks that the field fits in `it_len`, records `this_arg_index`, `this_arg`, and `this_arg_size`, then advances internal state. Standard namespace, vendor namespace, and extension bits receive special handling: vendor namespaces parse OUI/subns/length and either switch to a known vendor namespace or return raw vendor data; radiotap namespace switches back to standard fields; extension bits load the next bitmap word.

## State and Persistence Behavior

All state is held in the caller-provided iterator. It tracks the radiotap header pointer, maximum radiotap length, current argument pointer, current bitmap shifter, next bitmap pointer, namespace metadata, reset-on-extension behavior, and the last returned argument. The file has only static constant namespace tables and no persistent runtime allocations.

## Dependencies and Integration Points

The implementation depends on cfg80211/public radiotap iterator types, `net/ieee80211_radiotap.h`, `linux/unaligned.h`, and exported symbols used by wireless drivers, monitor injection paths, sniffers, and tests that need robust radiotap parsing.

## Risks and Edge Cases

Radiotap fields are little-endian and may be unaligned; callers must use unaligned access helpers. Bounds checks are security-sensitive because radiotap headers can originate from packets or userspace injection. Unknown standard fields terminate standard parsing with `-ENOENT`; unknown vendor namespaces are returned as raw vendor data and skipped as a block. Namespace reset across extended bitmaps is subtle and easy to break.

## Test Signals

Parser tests should include minimal headers, invalid version, truncated `it_len`, extended bitmaps, every known field alignment, unknown standard bits, known and unknown vendor namespaces, and malformed vendor lengths. KASAN/UBSAN and packet-injection tests can catch out-of-bounds or unaligned misuse.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/radiotap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/rdev-ops.h -->
# sources/distributed-fs/ceph-client/net/wireless/rdev-ops.h

## Purpose

`rdev-ops.h` is cfg80211's internal trace-and-dispatch wrapper layer around `struct cfg80211_ops`. Each inline helper emits a tracepoint, calls the corresponding driver operation with `&rdev->wiphy` and cfg80211 objects, emits a return tracepoint, and normalizes optional operation behavior where needed. It centralizes driver-call instrumentation for interface, key, AP, station, mesh, OCB, scan, connect, management, NAN, DFS, MLO, PMSR, and other wireless operations.

## Important APIs, Types, and Functions

- Power and lifecycle wrappers: `rdev_suspend()`, `rdev_resume()`, `rdev_set_wakeup()`, `rdev_rfkill_poll()`.
- Interface wrappers: `rdev_add_virtual_intf()`, `rdev_del_virtual_intf()`, `rdev_change_virtual_intf()`, `rdev_add_intf_link()`, `rdev_del_intf_link()`, `rdev_get_radio_mask()`.
- Security/key wrappers: `rdev_add_key()`, `rdev_get_key()`, `rdev_del_key()`, default key setters, PMKSA setters, PMK add/delete, rekey data, FILS AAD, external auth, OWE update.
- AP/station/mesh/OCB wrappers: AP start/change/stop, station add/delete/change/get/dump, link station add/mod/delete, mesh path operations, mesh config, join/leave mesh, `rdev_join_ocb()`, `rdev_leave_ocb()`, BSS changes.
- Scan/connect/channel wrappers: scan/abort scan, auth/assoc/deauth/disassoc/connect/update/disconnect, IBSS join/leave, monitor channel, set/get channel, remain-on-channel, management TX/cancel, channel switch, radar detection/end CAC/background radar.
- Feature wrappers: testmode, bitrate mask, survey dump, TDLS, P2P, NAN, MAC ACL, QoS map, TX TS, multicast rate, coalesce, FTM responder stats, PMSR start/abort, TID config, SAR, color change, hardware timestamp, TTLM, MLO reconfiguration, EPCS.

## Control Flow

The common pattern is: declare `ret` when needed, emit `trace_rdev_<op>()`, call `rdev->ops-><op>()`, emit `trace_rdev_return_*()`, and return. Void operations emit return-void traces. Some wrappers check optional ops and return `-EOPNOTSUPP` when absent; a few optional void ops simply do nothing when absent. Dump/stat wrappers choose richer return tracepoints when the operation succeeds and plain integer traces on failure.

## State and Persistence Behavior

This header owns no state. It can indirectly mutate any driver, wiphy, wireless_dev, net_device, station, scan, connection, or regulatory state touched by the underlying driver operation. Tracepoints expose call inputs and returns but do not persist cfg80211 state. Optional fallbacks determine whether upper layers see unsupported operations as no-op, zero, or `-EOPNOTSUPP`.

## Dependencies and Integration Points

The header includes RTNL, cfg80211, `core.h`, and `trace.h`. It is included throughout cfg80211 code so upper layers call `rdev_*` rather than direct `rdev->ops` methods. It integrates strongly with ftrace/perf diagnostics and with all cfg80211 drivers implementing `struct cfg80211_ops`.

## Risks and Edge Cases

Because this is a header of static inlines, any signature mismatch with `struct cfg80211_ops` causes broad build failures. Optional-op semantics are not uniform: some wrappers require callers to precheck operation presence, some return `-EOPNOTSUPP`, some no-op, and `rdev_get_radio_mask()` returns `0` when unsupported. A notable detail is `rdev_set_antenna()` traces `radio_idx` but passes `-1` to the driver in this source, which may be intentional legacy behavior or a bug-prone mismatch. Callers must hold the locks required by each operation; this layer does not enforce locking beyond occasional `might_sleep()`.

## Test Signals

Build coverage across many wireless configs is the first signal. Runtime validation uses `trace_rdev_*` tracepoints to confirm arguments, return values, and optional-op handling. Targeted tests should cover unsupported optional operations, scan request validation, PMSR dispatch, OCB dispatch, DFS CAC end, MLO link station ops, and get/dump wrappers whose return tracepoints include output structures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/rdev-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/reg.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/reg.h -->
# sources/distributed-fs/ceph-client/net/wireless/reg.h

## Purpose

`reg.h` is the internal cfg80211 regulatory header. It declares the regulatory core's public-in-subsystem state and helper APIs used by wireless core files and drivers, including request validation, user/driver/country/beacon hints, wiphy register/deregister handling, DFS helpers, regdb reload, and channel enforcement scheduling.

## Important APIs, Types, and Functions

- `enum ieee80211_regd_source` distinguishes regdomains sourced from the internal database, CRDA, or cached data.
- `cfg80211_regdomain` is the RCU-protected global regulatory domain pointer.
- Request/domain helpers include `reg_is_valid_request()`, `is_world_regdom()`, `reg_supported_dfs_region()`, `reg_get_dfs_region()`, `set_regdom()`, `reg_get_max_bandwidth()`, and `reg_last_request_cell_base()`.
- Hint APIs include `regulatory_hint_user()`, `regulatory_hint_indoor()`, `regulatory_netlink_notify()`, `regulatory_hint_found_beacon()`, `regulatory_hint_country_ie()`, and `regulatory_hint_disconnect()`.
- Wiphy lifecycle APIs include `wiphy_regulatory_register()` and `wiphy_regulatory_deregister()`.
- DFS and channel APIs include `cfg80211_get_unii()`, `regulatory_indoor_allowed()`, `regulatory_propagate_dfs_state()`, `reg_dfs_domain_same()`, `reg_reload_regdb()`, and `reg_check_channels()`.
- Certificate arrays for shipped and extra regdb keys are declared for signed regulatory database support.

## Control Flow

The header defines no flow itself, but it sets the call graph contracts for `reg.c`. Init code calls `regulatory_init()` and `regulatory_exit()`. Drivers and cfg80211 code submit hints through the declared functions. Firmware/CRDA loaders call `set_regdom()` with a source enum. Wiphy lifecycle code calls register/deregister hooks so current regulatory settings are applied to newly registered devices and cleaned on removal.

## State and Persistence Behavior

Persistent state is declared, not owned, here. `cfg80211_regdomain` is externally visible under RCU. The APIs declared here mutate long-lived global regulatory state, per-wiphy regdomains, channel flags, DFS state, beacon-hint lists, cached user domains, indoor state, and pending work in `reg.c`.

## Dependencies and Integration Points

The header includes `net/cfg80211.h` and is included by cfg80211 core files needing regulatory decisions. It connects nl80211 user commands, driver hints, scan/beacon processing, DFS code, and wiphy lifecycle management to the implementation in `reg.c`.

## Risks and Edge Cases

Callers must respect locking and context requirements documented in comments, especially RTNL for DFS propagation and process context for disconnect restore. Misusing `set_regdom()` without a matching outstanding request fails by design. `cfg80211_regdomain` readers need RCU, RTNL, or the relevant wiphy lock depending on the access path.

## Test Signals

Build coverage catches signature drift between `reg.h` and `reg.c`. Runtime tests should validate user hints, indoor netlink ownership cleanup, beacon and country IE hints, DFS propagation, regdb reload, and delayed channel enforcement through the declared APIs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/wireless/reg.h -->
