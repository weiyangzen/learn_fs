# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_service.cc

## Purpose
This file constructs, initializes, starts, and shuts down the RGW RADOS service graph. It also initializes higher-level control objects and metadata handlers used by admin and metadata paths.

## Important APIs, Types, and Functions
- `RGWServices_Def::init()` allocates concrete services: bucket, bucket sync, bucket index, bilog, cls, config-key, datalog, mdlog, notify, zone, zone utils, quota, sync modules, sysobj/core/cache, user, and async RADOS processor.
- `RGWServices_Def::shutdown()` tears down services and stops the async processor.
- `RGWServices::do_init()` delegates initialization and publishes non-owning service pointers.
- `RGWServiceInstance::start()` implements idempotent service start and marks `StateStarting` before `do_start()` to tolerate circular service references.
- `RGWCtlDef::init()` creates metadata manager/handlers, topic cache, user control, and bucket control.
- `RGWCtl::init()` attaches metadata handlers to the metadata manager.

## Control Flow
Initialization allocates all service objects, starts the async RADOS processor, wires dependencies with each service's `init()`, then starts services in dependency-aware order. Notify starts first when cache exists. Non-raw mode starts zone, datalog, mdlog, sync modules, bucket, bucket-sync, and user services; raw mode skips high-level services. Core services such as cls, config key, zone utils, quota, sysobj core/cache/sysobj start in both modes. Control initialization allocates handlers and attaches each one, aborting on the first attach error.

## State and Persistence Behavior
The file manages in-memory service ownership through `unique_ptr`s in `RGWServices_Def` and public non-owning pointers in `RGWServices`. It starts background/stateful components including `RGWAsyncRadosProcessor`, datalog, mdlog, notify/cache, and sync modules. Metadata handlers persist and retrieve users, buckets, bucket instances, OTP, roles, OIDC providers, accounts, groups, and pubsub topics.

## Dependencies and Integration Points
It depends on the RADOS service headers, metadata modules for accounts/groups/OIDC/roles/topics, `RGWRados`, `RGWBucketCtl`, `RGWUserCtl`, and the sync module service. Sync modules can override bucket and bucket-instance metadata handlers during control setup.

## Risks
- Startup order is fragile because many services depend on initialized but not always started peers.
- `shutdown()` assumes pointers are valid once `can_shutdown` is set, so partial init failure paths must remain safe.
- If `do_start()` fails, `start_state` has already moved to `StateStarting`.
- Raw mode leaves some services unstarted; callers must not use skipped high-level services.

## Test Signals
Signals include RGW daemon startup/shutdown tests, raw initialization tests, cache/no-cache configurations, sync module configuration tests, metadata admin tests for every attached handler, and fault-injection tests for service start or handler attach failures.
