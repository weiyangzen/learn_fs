# sources/distributed-fs/ceph/src/rgw/rgw_restore.h

## Purpose
`rgw_restore.h` declares the RGW restore coordinator and the serializable restore queue entry used for cloud-tier object restoration. It is the public interface between request handling, background restore processing, the SAL restore backend, and GET waiters blocked on restore completion.

## Important APIs, Types, and Functions
`RestoreEntry` stores the durable unit of restore work: `rgw_bucket bucket`, `rgw_obj_key obj_key`, optional temporary-restore `days`, source `zone_id`, and `rgw::sal::RGWRestoreStatus status`. It provides Ceph encoding, JSON dump/decode, and test-instance generation.

`Restore` derives from `DoutPrefixProvider` and owns `CephContext`, a SAL `Driver`, a SAL `Restore` backend, shard object names, shutdown state, a waiter registry, and one `RestoreWorker`. `initialize()` and `finalize()` manage backend setup/teardown. `start_processor()`, `stop_processor()`, and `wake_worker()` manage the background thread. `process()` variants implement the shard loop and per-entry processing. Public operation helpers include `set_cloud_restore_status()`, `get_expiration_date()`, `update_cloud_restore_exp_date()`, `restore_obj_from_cloud()`, `send_notification()`, `list()`, and `status()`.

`RestoreWorker` is a nested `Thread` with a mutex/condition variable. It calls back into the owning `Restore`, sleeps according to `rgw_restore_processor_period`, and can be woken by restore enqueue operations.

## Control Flow
The interface supports two paths. The foreground request path calls `restore_obj_from_cloud()` to set object state and enqueue work. The background path is started via `start_processor()`, then repeatedly calls `process(RestoreWorker*, optional_yield)`, which fans into shard-level and entry-level processors. The same class exposes admin-style `list()` and `status()` queries over restore state.

## State and Persistence Behavior
The header shows that queue persistence is abstracted behind `rgw::sal::Restore`, while object restore state is persisted through object attributes. `restore_oid_prefix` and `restore_index_lock_name` define the shard naming and locking conventions. `down_flag` is atomic and controls thread exit. `waiter_registry` is in-memory and intentionally not durable; it bridges active GET requests to background completion.

## Dependencies and Integration Points
The declarations include Ceph threading, conditions, librados types, RGW common types, notifications, SAL interfaces, and `rgw_restore_waiter.h`. Restore is instantiated and controlled by the RADOS-backed driver but uses SAL-level abstractions so the queue and object restore implementation can live in the selected backend.

## Risks
`Restore` has a destructor with side effects (`stop_processor()` and `finalize()`), so ownership/lifetime mistakes can block waiting for the worker. The class stores raw pointers to `CephContext` and `Driver`; callers must ensure those outlive restore processing. `max_objs` is bounded by `HASH_PRIME`, and a zero or invalid configuration would make shard choice unsafe unless initialization rejects it downstream.

## Test Signals
Interface tests should verify serialization compatibility for `RestoreEntry`, start/stop idempotence, worker wake behavior, waiter registry lifetime, status attr helpers, expiry-date calculation with normal and debug intervals, and that frontend restore requests can enqueue while background processing is already active.
