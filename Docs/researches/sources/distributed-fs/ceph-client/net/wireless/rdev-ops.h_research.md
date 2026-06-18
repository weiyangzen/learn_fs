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
