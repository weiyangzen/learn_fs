# sources/distributed-fs/ceph/src/mon/Session.h

## Purpose
`Session.h` defines in-memory monitor client/session tracking, including subscriptions to monitor maps, authenticated entity information, capabilities, feature accounting, proxied request fields, and lookup structures for OSD sessions.

## Important APIs, Types, and Control Flow
`Subscription` records a session, subscription type, next version, and one-shot flags. `MonSession` is refcounted and stores the `ConnectionRef`, peer identity, addresses, caps, auth handler, global id state, subscriptions, OSD epoch, proxy metadata, and last config state. `_ident()` initializes peer metadata from a connection. `is_capable()`, `get_allowed_fs_names()`, and `fs_name_capable()` delegate capability checks to `MonCap`. `dump()` emits session diagnostics.

`MonSessionMap` owns all sessions, subscription lists by type, OSD-session multimap, and a `FeatureMap`. `add_session()` sets timeout, links the session into lists, indexes OSD sessions, and increments feature counts. `remove_session()` clears subscriptions, removes list nodes and OSD index entries, decrements feature counts, marks closed, and drops the reference. `get_random_osd_session()` picks a likely OSD session and can validate it against the current `OSDMap`. Subscription helpers add, update, and remove per-session subscriptions.

## State and Persistence Behavior
This file manages volatile runtime state only. Session timeout, auth handler ownership, feature counts, and subscription lists are memory-resident and rebuilt as clients reconnect. Correct list membership is enforced by destructor assertions.

## Dependencies and Integration Points
It depends on `Connection`, message types, `FeatureMap`, `AuthServiceHandler`, `OSDMap`, `MonCap`, clocks, and intrusive `xlist`. It integrates with monitor command/message handling, subscription update fanout, auth, capability enforcement, config sharing, and OSD session selection.

## Risks and Test Signals
Risks include iterator misuse in `remove_session()` for OSD multimap entries, stale subscription pointers, feature-count leaks, capability mismatch, and auth handler lifetime. Tests should cover add/remove lifecycle, multiple subscriptions per session, OSD lookup with matching/mismatching addresses, feature map accounting, destructor invariants, and cap checks for monitor and filesystem-scoped permissions.
