# sources/distributed-fs/ceph/src/mon/MonSub.cc

## Purpose

`MonSub.cc` implements `MonSub`, the monitor-client subscription state machine used to request, renew, acknowledge, advance, reload, and cancel subscriptions to monitor-maintained data streams. It is used by `MonClient` to track wanted maps or service updates and to decide when a new `MMonSubscribe` request should be sent.

The implementation separates unsent/new subscriptions from sent subscriptions and advances each subscription start epoch as updates arrive.

## Important APIs and functions

- `have_new()` returns whether there are pending unsent subscriptions in `sub_new`.
- `need_renew()` compares `ceph::coarse_mono_clock::now()` with `renew_after`.
- `renewed()` marks a subscription request as sent by merging old sent subscriptions with new ones, swapping into `sub_sent`, clearing `sub_new`, and setting `renew_sent` if no renewal is already in flight.
- `acked(interval)` handles `MMonSubscribeAck` intervals, primarily for legacy monitors, by setting the next renewal point to half the ack interval after `renew_sent`.
- `reload()` copies all sent subscriptions not already pending back into `sub_new`, typically after reconnect or monitor session reset.
- `got(what, have)` advances or removes a subscription when a map/update version is received.
- `want(what, start, flags)` requests a subscription if no identical pending or sent subscription already exists.
- `inc_want(what, start, flags)` requests only if the desired start is greater than the existing start.
- `unwant(what)` cancels pending and sent state for a subscription key.

## Control flow

The normal flow starts with `want()` or `inc_want()`, which creates/updates an entry in `sub_new` and returns `true` when a send is needed. `MonClient` can then call `get_subs()` from the header and send an `MMonSubscribe`. After sending, `renewed()` moves all active subscription state to `sub_sent`. When the monitor replies with an ack interval, `acked()` schedules the next renewal at half the interval.

When the client receives an update, `got()` looks first in `sub_new`, then in `sub_sent`. If the current requested `start` is less than or equal to the received `have` version, one-time subscriptions are erased; persistent subscriptions advance to `have + 1` so future requests ask only for newer data.

On reconnect or resubscribe events, `reload()` repopulates `sub_new` from `sub_sent` for any subscription not already pending. Cancellation through `unwant()` erases both maps.

## State and persistence behavior

`MonSub` state is in-memory client-side subscription bookkeeping:

- `sub_new`: requested but unsent subscriptions.
- `sub_sent`: subscriptions already sent to a monitor.
- `renew_sent`: time the current renewal request was sent.
- `renew_after`: next time a renewal should be sent.

No state is persisted to disk or Paxos. The `start` values inside `ceph_mon_subscribe_item` are durable only for the lifetime of the client object and are reconstructed by callers after reconnect or process restart.

## Dependencies

The implementation depends on:

- `MonSub.h` for class declaration.
- `ceph::coarse_mono_clock`, `ceph::coarse_mono_time`, and `ceph::make_timespan`.
- `ceph_mon_subscribe_item` and `CEPH_SUBSCRIBE_ONETIME` from Ceph protocol headers.
- `MonClient`, which owns a `MonSub`, sends `MMonSubscribe`, handles `MMonSubscribeAck`, and calls `got()` when map versions arrive.

## Risks and edge cases

- `renewed()` only sets `renew_sent` if it is currently zero. Multiple sends before an ack keep the original send time, which is intentional for one in-flight renewal but can skew renewal timing if send/ack handling is changed.
- `acked(interval)` schedules renewal at `interval / 2.0`; very small or zero intervals can make `need_renew()` true immediately.
- `got()` checks `sub_new` before `sub_sent`, so a pending changed subscription takes precedence over an older sent subscription.
- `want()` considers an identical sent subscription sufficient and returns false. If the connection was lost but `reload()` was not called, callers may incorrectly believe no send is needed.
- `inc_want()` never lowers a start epoch. That avoids duplicate older updates but can prevent callers from re-requesting history through this API.
- Map ordering by string key is deterministic but there is no explicit concurrency protection; callers should use it from the owning client thread/context.

## Test signals

Useful tests include:

- `want()` idempotency for identical pending and sent subscriptions, and update behavior for changed start/flags.
- `renewed()` merge behavior when both `sub_new` and `sub_sent` contain entries.
- `acked()` scheduling with normal, small, and zero intervals.
- `got()` advancement for persistent subscriptions and erasure for one-time subscriptions in both new and sent maps.
- `reload()` repopulation without overwriting already pending entries.
- `inc_want()` behavior for higher, equal, and lower start versions.
- `unwant()` removing both pending and sent entries.
