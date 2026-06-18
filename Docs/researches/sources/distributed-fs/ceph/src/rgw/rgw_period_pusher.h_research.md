# sources/distributed-fs/ceph/src/rgw/rgw_period_pusher.h

## Purpose
`rgw_period_pusher.h` declares `RGWPeriodPusher`, the realm watcher/reloader participant responsible for pushing period updates to other zones.

## Important APIs, Types, And Functions
It aliases `RGWZonesNeedPeriod` to `RGWPeriod`, declares `RGWPeriodPusher final` deriving from `RGWRealmWatcher::Watcher` and `RGWRealmReloader::Pauser`, and exposes constructor, destructor, `handle_notify()`, `pause()`, and `resume()`.

## Control Flow
The header documents the high-level flow: notifications trigger period pushes; pause prevents access to stale driver state during dynamic reconfiguration; resume processes queued notifications with a new driver.

## State And Persistence
Member state includes `CephContext`, mutable driver pointer, mutex, current realm/period epochs, pending period notifications, and an opaque `CRThread`. Persistence is remote side effect through the `.cc` implementation.

## Dependencies And Integration Points
It depends on `rgw_realm_reloader.h`, SAL forward declarations, async yield, and epoch types. It integrates directly with realm watch/notify and reload orchestration.

## Risks And Test Signals
Risks include lock ordering with reloader callbacks, driver lifetime, and pending notification growth during long pauses. Tests should cover pauser lifecycle and notification handling during reload.
