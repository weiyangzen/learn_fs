# sources/distributed-fs/ceph/src/mon/MonSub.h

## Purpose

`MonSub.h` declares the `MonSub` class, a compact in-memory subscription tracker used by Ceph monitor clients. It records which monitor data subscriptions are newly requested, which have already been sent, what version each subscription should start from, and when renewals are due.

The class is part of the monitor client protocol machinery around `MMonSubscribe` and `MMonSubscribeAck`.

## Important APIs, types, and fields

Public APIs:

- `have_new()` reports whether unsent subscriptions exist.
- `get_subs()` returns a copy of `sub_new` for message construction.
- `get_start(what)` returns the requested start version, preferring pending new state over sent state and returning `0` if absent.
- `need_renew()` checks whether renewal time has passed.
- `renewed()` moves new requests into sent state.
- `acked(interval)` updates renewal scheduling after monitor acknowledgment.
- `got(what, version)` advances/removes subscription state after receiving data.
- `reload()` makes sent subscriptions pending again.
- `want(what, start, flags)` requests an exact subscription.
- `inc_want(what, start, flags)` requests a higher start version only.
- `unwant(what)` cancels a subscription.

Private state:

- `sub_sent`: map of subscription name to `ceph_mon_subscribe_item` that has been sent.
- `sub_new`: map of subscription name to unsent `ceph_mon_subscribe_item`.
- `renew_sent`: coarse monotonic time when renewal was sent.
- `renew_after`: coarse monotonic deadline for the next renewal.

## Control flow

Callers request subscriptions through `want()` or `inc_want()`. If either returns true, `have_new()` becomes true and `get_subs()` exposes the pending map for a subscribe message. After the message is sent, `renewed()` transitions pending entries to `sub_sent`. After acknowledgment, `acked()` schedules the next renewal. As updates arrive, `got()` advances the start version or removes one-time entries. Reconnect handling can call `reload()` to resend active subscriptions, and callers use `unwant()` to cancel.

`get_start()` is important for callers deciding the current requested version. It intentionally checks `sub_new` first so a pending update to subscription state overrides older sent state.

## State and persistence behavior

`MonSub` has no persistent storage and does not encode/decode itself. It is volatile protocol state inside `MonClient`. The only durable-ish data it tracks is the next requested `version_t` per subscription while the process is alive.

The class stores maps by subscription key string, and values are protocol structs containing `start` and `flags`. Renewal timing uses monotonic coarse time, avoiding wall-clock adjustments.

## Dependencies

The header depends on:

- `common/ceph_time.h` for coarse monotonic time types.
- `include/ceph_fs.h` for `ceph_mon_subscribe_item` and subscription flags.
- `include/types.h` for `version_t`.
- Standard `map` and `string`.

Integration points include `MonClient.h`, `MonClient.cc`, `MMonSubscribe`, and `MMonSubscribeAck`.

## Risks and edge cases

- `get_subs()` returns a copy by value. That is simple and safe but can be wasteful if many subscriptions are added.
- `renew_after` default initialization relies on default construction of coarse monotonic time; callers should expect initial `need_renew()` behavior to be defined by that zero/default value.
- There is no locking. Use from multiple threads would need external serialization.
- Subscription names are untyped strings, so misspellings create independent subscriptions rather than compile-time failures.
- `get_start()` returning `0` for absent keys means callers must distinguish "not subscribed" from a legitimate start-at-zero request by checking subscription existence through other state if needed.

## Test signals

Header-facing tests should verify:

- `get_start()` precedence for `sub_new` over `sub_sent`.
- `have_new()` and `get_subs()` after request, renewal, reload, and cancel operations.
- Initial renewal behavior before any ack.
- Correct use of `version_t` start values and subscription flags.
- Caller integration with `MonClient` message creation and ack handling.
