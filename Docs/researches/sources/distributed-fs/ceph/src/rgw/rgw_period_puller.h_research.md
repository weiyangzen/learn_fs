# sources/distributed-fs/ceph/src/rgw/rgw_period_puller.h

## Purpose
`rgw_period_puller.h` declares the concrete period-history puller backed by RGW zone services and config-store storage.

## Important APIs, Types, And Functions
`RGWPeriodPuller` derives from `RGWPeriodHistory::Puller`. It stores `CephContext*` and service pointers for `RGWSI_Zone` and `RGWSI_SysObj`. It exposes a constructor and overrides `pull()`.

## Control Flow
The header defines only the interface. Runtime behavior is in `rgw_period_puller.cc`.

## State And Persistence
The class retains service pointers but owns no durable state. Persistence occurs through `pull()` writing to the config store.

## Dependencies And Integration Points
It includes `rgw_period_history.h`, common forward declarations, and sysobj service headers. It is the bridge between in-memory period history and multisite services.

## Risks And Test Signals
Risks include service lifetime assumptions and null service pointers. Tests should instantiate with mock or fixture services and verify `RGWPeriodHistory` integration through the `Puller` interface.
