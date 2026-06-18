# sources/distributed-fs/ceph/src/rgw/rgw_realm_reloader.h

## Purpose

Declares `RGWRealmReloader`, a realm notification watcher that coordinates frontend pause/resume and storage driver replacement after multisite period changes.

## Important APIs, Types, and Functions

`RGWRealmReloader::Pauser` abstracts frontend `pause()` and `resume(rgw::sal::Driver*)`. The constructor receives `RGWProcessEnv`, implicit-tenant config, service-map metadata, pauser, and an Asio context. `handle_notify()` overrides the watcher interface. Private `reload()` performs replacement, and `C_Reload` is the timer callback type.

## Control Flow and Data Flow

The header documents the design: notifications should schedule a timer callback rather than doing slow reload work in the notify thread, and the timer can cancel/requeue reload events while a reload is already running. The pauser boundary prevents direct dependency on frontend classes.

## State and Persistence Behavior

Persistent state is not declared here. Runtime state includes references to process environment and auth/metadata inputs, the frontend pauser, io context, a `SafeTimer`, mutex/condition variable, and a raw pointer to the scheduled reload context.

## Dependencies and Integration Points

Depends on `RGWRealmWatcher`, `SafeTimer`, Ceph condition/mutex primitives, SAL forward declarations, and Boost.Asio. Integrated with RGW process setup and realm watch registration.

## Risks and Edge Cases

The class stores many references, so their lifetimes must outlive the reloader. `reload_scheduled` is a raw pointer managed by `SafeTimer`; cancellation/destruction paths need coverage. Frontend pause/resume correctness is outside the class but critical.

## Test Signals

Use fake pausers and fake environment/driver managers to exercise notify scheduling, timer cancellation, destruction with pending reload, reference lifetime expectations, and no direct frontend dependency.
