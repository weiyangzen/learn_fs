# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_object_expirer_core.h

## Purpose
Declares the object expiration hint store and background expirer. It gives callers a way to enqueue future delete hints and provides a worker that scans those hints, garbage-collects expired objects, and trims processed timeindex entries.

## Important APIs And Types
`RGWObjExpStore` exposes `objexp_hint_add()`, `objexp_hint_list()`, and `objexp_hint_trim()` over RADOS timeindex shards. `RGWObjectExpirer` wraps a SAL driver and store, exposes `hint_add()`, object garbage collection methods, shard processing methods, and worker lifecycle methods. Nested `OEWorker` is a Ceph `Thread` and `DoutPrefixProvider` used for periodic background processing.

## Control Flow And State
`start_processor()` allocates and starts the worker thread; `stop_processor()` sets `down_flag`, wakes the condition variable, joins, and deletes the worker. The worker calls `inspect_all_shards()` and sleeps based on `rgw_objexp_gc_interval`. `going_down()` exposes the atomic shutdown flag. `hint_add()` is a thin delegation into the store.

## Dependencies And Integration Points
The header depends on RADOS SAL types, Ceph thread/mutex/condition primitives, formatting/config utilities, crypto/global includes inherited from older RGW components, and `objexp_hint_entry` from RGW object expiry types. It integrates with bucket/object code that schedules delayed deletion and with RGW daemon startup/shutdown.

## Risks And Test Signals
The class stores the driver as a base pointer but downcasts to RadosStore in the store constructor and implementation, so it is RADOS-specific despite accepting `rgw::sal::Driver*`. Worker lifetime is manual and must not double-start. Tests should exercise start/stop idempotence, down-flag wakeup, hint add/list/trim delegation, and shard-processing behavior with mocked or test RADOS stores.
