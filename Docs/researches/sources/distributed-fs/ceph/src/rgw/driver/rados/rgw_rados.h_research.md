# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rados.h

## Purpose
This header is the central RADOS-backed RGW storage surface. It declares `RGWRados`, the object and bucket helper classes nested under it, serialized helper structs, raw object state caches, bucket index accessors, background service ownership, and integration hooks used by the RADOS SAL driver. Most implementation lives in companion `.cc` files; this file defines the API contract that object I/O, bucket index mutation, lifecycle, GC, sync, quota, restore, and reshard code depend on.

## Important APIs, Types, And Functions
- `RGWOLHInfo`, `RGWOLHPendingInfo`, and `objexp_hint_entry` are encoded metadata records for object-logical-head tracking and object expiration hints. They expose `encode()`, `decode()`, `dump()`, and `generate_test_instances()`, which signals Ceph's usual encode/decode compatibility tests.
- `RGWUsageBatch` aggregates `rgw_usage_log_entry` values by `ceph::real_time` and reports whether a timestamp was newly accounted.
- `RGWFetchObjFilter` and `RGWFetchObjFilter_Default` allow copy/fetch paths to adjust destination owner and placement rule based on source object attributes.
- `RGWObjectCtx` is a non-copyable, non-movable per-request object-state cache keyed by `rgw_obj`. It stores `RGWObjStateManifest`, exposes atomic/compressed/prefetch flags, and has explicit invalidation.
- `RGWRawObjState`, `RGWPoolIterCtx`, and `RGWListRawObjsCtx` hold raw RADOS state and pool iteration cursors.
- `RGWRados` owns pool IoCtxs, core services (`RGWServices`, `RGWCtl`), background workers, caches, sync managers, and the RADOS object API. It exposes initialization/finalization, service map updates, raw pool listing, log usage, bucket creation/deletion, object stat/read/write/delete/copy/transition/restore, bucket index operations, OLH repair/update, GC/lifecycle/quota/reshard helpers, and async object removal.
- Nested `RGWRados::Object::{Read,Write,Delete,Stat}` packages per-object I/O parameters and result state. Nested `RGWRados::Bucket::{UpdateIndex,List}` packages bucket index mutation and listing behavior.
- `get_obj_data` coordinates asynchronous object read completions, client callbacks, optional D3N cache write bypass, cancellation, and drain/flush sequencing.

## Control Flow
Callers initialize the store through `init_begin()`, `init_svc()`, `init_rados()`, and `init_complete()`, then use the exposed helpers through the RADOS SAL driver. Object flow typically starts with `RGWObjectCtx` and `RGWRados::Object`, resolves bucket shard and manifest state, applies preconditions, then drives `Read`, `Write`, `Delete`, or `Stat`. Bucket mutation flows through `Bucket::UpdateIndex::prepare()`, `complete()`, `complete_del()`, or `cancel()`, with `guard_reshard()` and `block_while_resharding()` protecting index operations while resharding is active. Listing flow chooses ordered or unordered listing based on `List::Params::allow_unordered`, then uses cls bucket list APIs and stores the next marker.

## State And Persistence Behavior
The class persists almost all RGW metadata through RADOS pools and cls helpers. It owns IoCtxs for root, GC, lifecycle, restore, object expiration, reshard, notification, and logging pools. Object state is cached in `RGWObjectCtx`, bucket metadata may be cached through chained caches, tombstones use an LRU map, and bucket topics have a separate cache. Persistent bucket instance state is read/written by `get_bucket_instance_info()`, `put_bucket_instance_info()`, `put_linked_bucket_info()`, and bucket entry name helpers. Bucket index entries and bilog records are maintained with `cls_obj_prepare_op()`, `cls_obj_complete_*()`, `bi_*()` functions, and OLH helpers. The API also exposes data/log sync wakeups and reshard queue integration, so bucket layout and log-generation metadata are part of the persistent contract.

## Dependencies And Integration Points
This header depends on librados, cls rgw/version/log/timeindex/otp types, RGW metadata, quota, log, sync, restore, cache, pubsub, SAL, and service headers. It friends GC, notifiers, expirer, sync processors, resharding, bucket index locking, serializers, and `rgw::sal::RadosStore`, showing that it is a low-level integration hub rather than an isolated abstraction. It also integrates with D3N data cache, neorados restore context, Ceph timers, async context pools, and trace contexts.

## Risks And Edge Cases
The API surface is large and has many cross-module invariants: object manifest state must match bucket index accounting, OLH updates must be idempotent across versioning modes, reshard guards must prevent writes to the wrong shard generation, and async read/delete paths must drain completions without leaking or double-accounting. The raw-state copy constructor intentionally omits `attrset` copying, so code assuming full state copies could be wrong. The file also contains many optional-yield paths; callers must preserve coroutine/blocking semantics. Misuse of `force`, `skip_olh_obj_update`, or `log_op` can leave index, bilog, or sync state inconsistent.

## Test Signals
The encoded helper structs provide `generate_test_instances()`, which supports Ceph encode/decode compatibility tests. High-value tests should cover bucket index prepare/complete/cancel, versioned delete and OLH repair, reshard guard behavior, ordered and unordered listing markers, quota accounting, raw object stat/listing, GC deferral, object copy attribute modes, and async read drain/cancel with and without D3N data cache.
