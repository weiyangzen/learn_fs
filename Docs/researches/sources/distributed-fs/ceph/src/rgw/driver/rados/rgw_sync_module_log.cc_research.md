# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.cc` implements a diagnostic RGW sync module that logs data-sync operations instead of exporting or indexing data. It is useful for observing multisite sync callbacks and remote object stats.

## Important APIs, Types, and Functions

`RGWLogStatRemoteObjCBCR` logs the result of a remote object stat, including source zone, bucket, key, size, mtime, and attributes. `RGWLogStatRemoteObjCR` wraps the callback in the standard remote-stat coroutine. `RGWLogDataSyncModule` implements `sync_object()`, `remove_object()`, and `create_delete_marker()` by logging operation details. `RGWLogSyncModuleInstance` exposes the data handler, and `RGWLogSyncModule::create_instance()` reads a `prefix` config value.

## Control Flow

On object sync, the module logs the requested bucket/key/versioned epoch and returns a remote stat coroutine whose callback logs full stat details. Remove and delete-marker callbacks only log and return null, so no downstream export action is performed. Instance creation is a simple prefix read plus object allocation.

## State and Persistence Behavior

The only state is the configured log prefix stored in the data handler. No RADOS or external state is written by this module.

## Dependencies and Integration Points

It depends on RGW data sync abstractions, coroutine support, remote stat helpers, and Ceph logging. It plugs into the same `RGWSyncModule`/`RGWDataSyncModule` path as production sync modules, making it a low-impact observer.

## Risks and Edge Cases

Logging at level 0 can be noisy under high object churn. Because delete and delete-marker operations return null, using this module as anything other than a diagnostic sink will not replicate state changes.

## Test Signals

Tests can instantiate the module with a prefix, trigger sync/remove/delete-marker callbacks, and assert that the expected coroutine is returned only for sync_object. Integration smoke tests should verify remote stat logging does not alter sync state.
