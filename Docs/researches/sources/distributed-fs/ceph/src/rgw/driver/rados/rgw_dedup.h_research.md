# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup.h

## Purpose
`rgw_dedup.h` declares the main RGW deduplication background service. It ties together the dedup control plane, per-run shard coordination, bucket-index scanning, slab generation, duplicate estimation, and optional full dedup execution. The file is the facade for the RADOS driver dedup subsystem: it depends on the utility types, table, cluster coordinator, filter, and realm reloader interfaces.

## Important APIs, Types, And Functions
`rgw::dedup::control_t` is the run-control state carried locally and over watch/notify acknowledgements. It stores the requested dedup mode, start/execution state, local and remote pause or abort flags, restart requests, and two `Throttle` instances for bucket-index and metadata access. `local_urgent_req()`, `should_stop()`, and `should_pause()` are used by worker loops to react to shutdown, local pause, remote abort, and remote pause.

`rgw::dedup::Background` derives from `RGWRealmReloader::Pauser`. Its public API is `watch_reload()`, `unwatch_reload()`, `handle_notify()`, `start()`, `shutdown()`, `pause()`, and `resume()`. `DedupWatcher` is a nested `librados::WatchCtx2` wrapper that forwards RADOS notifications and errors to the background instance.

The private `dedup_step_t` enum names the main pipeline phases: bucket-index ingress, table build, attribute read, and duplicate removal. The declarations show two execution lanes: estimate support is always present, while strong hashing, manifest mutation, refcount changes, and actual dedup object rewrites are under `FULL_DEDUP_SUPPORT`.

## Control Flow
The service starts a runner thread with `start()` and coordinates an epoch through `setup()`. It reads bucket metadata, partitions bucket-index work across work shards, writes bucket entries as disk records grouped by MD5 shard, waits at shard barriers, builds a per-MD5 dedup table, optionally reads object attributes and BLAKE3 hashes, then optionally removes duplicates.

Shard processing is abstracted through `process_all_shards()` and member-function callbacks. Work-shard functions scan bucket-index shards and emit records. MD5-shard functions load slabs, build or update dedup table entries, and estimate or execute deduplication. Barrier methods wait for cluster shard-token completion between phases.

Urgent control runs alongside the pipeline. `handle_notify()` receives restart, abort, pause, resume, and throttle messages from the cluster control object. `handle_pause_req()` and the `control_t` predicates let long loops pause or stop without waiting for full phase completion.

## State And Persistence Behavior
The header itself stores only in-memory state, but its members point to persistent subsystems. `d_cluster` manages epoch and token objects in the RGW control pool. `d_dedup_cluster_ioctx` targets the dedup pool or control plane for slab access. The background object tracks global bucket counts, dedup thresholds, split-head settings, current control flags, filters, the RADOS watch handle, and the runner synchronization primitives.

The dedup pipeline persists intermediate `disk_record_t` records in slab objects via `rgw_dedup_store.*`. Full dedup mode persists object metadata changes, manifests, tail object refcount updates, and cleanup through functions declared behind `FULL_DEDUP_SUPPORT`.

## Dependencies And Integration Points
This file integrates with SAL (`rgw::sal::Driver`, `RadosStore`, `Bucket`), `RGWRados`, bucket-index APIs, object manifests, RADOS watch/notify, `RGWRealmReloader`, the cluster coordinator, the disk slab store, and the dedup hash table. The full dedup declarations depend on BLAKE3, RGW object manifest semantics, refcount operations, and object attribute reads and writes.

Admin-visible control flows are exposed indirectly by `rgw_dedup_cluster.cc` static control functions, which notify the watch object that this background service is watching.

## Risks And Edge Cases
The dedup service mutates live RGW object metadata in full mode, so pause, abort, rollback, refcount, and split-head paths are high risk. The header exposes rollback helpers for manifest refcounts and created tail objects, indicating partial failure is expected. Shard heartbeat and barrier correctness are also critical: a stuck worker, missed notify, or stale epoch can leave tokens incomplete and delay later phases.

`FULL_DEDUP_SUPPORT` changes the behavioral surface dramatically. Builds without it only allow estimate mode, while this source tree defines it in `rgw_dedup_utils.h`, enabling declarations for actual dedup work.

## Test Signals
Useful tests should exercise control flag encoding/decoding, remote pause/abort/restart notify handling, per-phase barriers, filtered bucket scans, dedup estimate counters, and full dedup rollback paths. Integration tests need multi-RGW participation because token acquisition, heartbeats, and epoch restarts are cluster-level behaviors.
