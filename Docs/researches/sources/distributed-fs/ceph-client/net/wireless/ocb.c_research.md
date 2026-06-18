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
