# sources/distributed-fs/ceph/src/rgw/rgw_realm_watcher.h

## Purpose

Declares the realm notification enum and observer interface used by RGW components that react to realm control-object notifications.

## Important APIs, Types, and Functions

`RGWRealmNotify` has `Reload` and `ZonesNeedPeriod`, with raw encoder support. `RGWRealmWatcher::Watcher` declares `handle_notify(RGWRealmNotify, bufferlist::const_iterator&)`. `RGWRealmWatcher` stores a map from notification type to watcher reference and exposes `add_watcher()`.

## Control Flow and Data Flow

Notification payloads are expected to be decoded from a `bufferlist::const_iterator` by the registered watcher. The base class only holds registrations; subclasses establish actual RADOS watches and dispatch.

## State and Persistence Behavior

No durable state is present. The enum's raw encoder is a wire/persistence concern for notification payload compatibility.

## Dependencies and Integration Points

Depends on Ceph buffer and encoding support. Integrated with realm reloader, period update flows, and realm control object watch implementations.

## Risks and Edge Cases

Raw enum encoding depends on enum value stability. The map stores references, not owned pointers. Only one watcher per notification type is naturally supported by the current map shape.

## Test Signals

Test enum encode/decode compatibility, registering reload and zone-period watchers, duplicate registration behavior, and payload iterator consumption by concrete watcher implementations.
