# sources/distributed-fs/ceph/src/rgw/rgw_realm_watcher.cc

## Purpose

Implements the small base watcher registry for realm notifications. The concrete watch mechanism is elsewhere; this file stores observer registrations by notification type.

## Important APIs, Types, and Functions

`RGWRealmWatcher::~RGWRealmWatcher()` is an empty virtual destructor. `add_watcher(RGWRealmNotify type, Watcher& watcher)` inserts the watcher reference into the `watchers` map.

## Control Flow and Data Flow

Callers register an observer for a given `RGWRealmNotify` enum value. Later concrete watcher implementations can look up that type and invoke `Watcher::handle_notify()`.

## State and Persistence Behavior

Only in-memory references are stored. No watch handle or persisted realm state is managed in this file.

## Dependencies and Integration Points

Depends on `rgw_realm_watcher.h`. Integrated with realm reloader and other components interested in `Reload` or `ZonesNeedPeriod` notifications.

## Risks and Edge Cases

`std::map<RGWRealmNotify, Watcher&>::emplace()` ignores later registrations for the same type, so duplicate registration silently keeps the first watcher. Stored references must remain valid until watcher destruction. No locking is provided.

## Test Signals

Cover registering each enum type, duplicate registration semantics, callback dispatch in concrete subclasses, and lifetime ordering between registered watchers and the watcher container.
