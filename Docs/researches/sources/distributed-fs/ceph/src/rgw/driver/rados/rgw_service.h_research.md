# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_service.h

## Purpose
This header defines the service container and control facade for the RGW RADOS driver. It separates owning service definitions from public non-owning service pointers and declares metadata control structures used by RGW admin and metadata operations.

## Important APIs, Types, and Functions
- `RGWServiceInstance` is the base service class with `start()`, `do_start()`, `shutdown()`, and a start-state enum.
- `RGWServices_Def` owns concrete service objects and declares `init()`/`shutdown()`.
- `RGWServices` exposes initialized service pointers and has `init()` for normal mode plus `init_raw()` for raw storage mode.
- `RGWCtlDef` owns metadata manager, metadata handlers, topic cache, user control, and bucket control.
- `RGWCtl` exposes initialized control pointers and attaches handlers to the metadata manager.

## Control Flow
`RGWServices` delegates to `RGWServices_Def`, then publishes service pointers. `RGWCtlDef` allocates metadata handlers and controls; `RGWCtl` maps selected pointers and performs handler attach. `RGWServiceInstance::start()` is a common idempotent wrapper around service-specific startup.

## State and Persistence Behavior
The header stores in-memory ownership and lifecycle state. Persistent behavior is delegated to service implementations and metadata handlers, but the layout determines available persistent subsystems: bucket index, bilog, datalog, mdlog, config keys, sys objects, user records, quotas, sync modules, and topic metadata. `can_shutdown` and `has_shutdown` prevent premature or repeated shutdown.

## Dependencies and Integration Points
The header forward-declares service classes and integrates with `CephContext`, `optional_yield`, `DoutPrefixProvider`, `rgw::SiteConfig`, `rgw::sal::RadosStore`, `rgw::sal::ConfigStore`, librados, metadata handlers, and chained caches.

## Risks
- Public raw pointers are valid only while owning `_svc` or `_ctl` objects live.
- Raw and normal initialization expose different usable surfaces.
- The circular-reference startup behavior can hide reentrant startup failures if callers assume `StateStarting` means fully ready.

## Test Signals
Runtime tests should cover service lifecycle idempotency, raw initialization, normal initialization with and without cache, and metadata handler availability after `RGWCtl::init()`.
