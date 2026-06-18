# sources/distributed-fs/ceph-client/drivers/md/dm-thin.c

## Purpose
`dm-thin.c` implements the device-mapper `thin-pool` and `thin` targets. The pool target owns data/metadata devices, the workqueue, pool mode, provisioning resources, discard behavior, metadata commit policy, and control messages. Thin targets expose virtual block devices backed by the pool and optionally an external origin. The data path maps bios through metadata lookups, provisions missing blocks, handles copy-on-write for snapshots, processes discards, and enforces degraded modes.

## Important APIs, Types, And Functions
- `struct pool` is the live pool object shared by one control target and many thin targets. It contains data and metadata block devices, `dm_pool_metadata`, pool features/mode, bio prison, kcopyd client, ordered workqueue, deferred sets, prepared mapping/discard lists, active thin list, callback function pointers, and mapping mempool.
- `struct pool_c` is the `thin-pool` target context with devices, requested/adjusted features, low-water mark, and bound pool.
- `struct thin_c` is the `thin` target context with pool device, optional origin, device id, opened metadata handle, requeue state, deferred bios/cells, and refcounted RCU list membership.
- `struct dm_thin_new_mapping` tracks an asynchronous provisioning, copy, zero, overwrite, or discard operation until metadata can be updated.
- `pool_target` registers constructor/destructor/map/suspend/resume/message/status/iterate/io_hints for `thin-pool`.
- `thin_target` registers constructor/destructor/map/end_io/suspend/resume/status/iterate/io_hints for `thin`.
- Key data-path functions are `thin_bio_map()`, `process_bio()`, `process_cell()`, `process_shared_bio()`, `provision_block()`, `schedule_copy()`, `schedule_zero()`, `process_prepared_mapping()`, and discard variants.
- Mode/error functions include `set_pool_mode()`, `metadata_operation_failed()`, `abort_transaction()`, `commit()`, `alloc_data_block()`, and `do_no_space_timeout()`.

## Control Flow
Module init creates the global pool table, a slab cache for new mappings, and registers `thin` then `thin-pool`. A pool table load parses metadata device, data device, block size, low-water mark, and optional features (`skip_block_zeroing`, `ignore_discard`, `no_discard_passdown`, `read_only`, `error_if_no_space`). It opens devices, creates or finds a shared pool, registers the metadata low-water callback, and registers a pre-commit callback that flushes the data device before metadata commit. `pool_preresume()` binds the control target, resizes data/metadata space maps if backing devices grew, and commits resize metadata. `pool_resume()` requeues held I/O, resumes active thins, clears suspended state, and starts the periodic waker.

Thin table load opens the pool device, finds the live `struct pool`, opens the internal thin metadata device id, sets max I/O length to the pool block size, configures flush/discard support, and inserts the thin into `pool->active_thins` under RCU. `thin_map()` offsets the bio and calls `thin_bio_map()`.

`thin_bio_map()` is non-blocking. Flushes and discards are deferred to the worker. For normal I/O it locks the virtual block in the bio prison, tries a non-blocking metadata lookup, and fast-remaps unshared mapped blocks by also briefly locking the physical block. Shared mappings, misses, and lookup cases that would block are queued as deferred cells for the ordered worker.

The worker processes prepared mappings, prepared discards, second-stage discard passdown, and then deferred bios/cells. Missing write blocks allocate data via `alloc_data_block()` and either zero, copy from an external origin, or copy from an internal shared block. Full-block overwrites can be issued before metadata insertion by hooking endio. When preparation completes, `process_prepared_mapping()` inserts the mapping with `dm_thin_insert_block()`, releases detained bios, remaps them to the new data block, and completes overwrite bios after required commit handling.

Snapshot copy-on-write uses a virtual-cell lock and physical-data-cell lock. Writes to shared blocks allocate a new data block and schedule an internal copy unless the write overwrites the full pool block. Reads of shared blocks increment `shared_read_ds` so COW waits for in-flight shared reads to quiesce.

Discard processing locks virtual ranges and, if passdown is enabled, breaks mapped ranges into bio-prison-safe physical ranges. It removes mappings, temporarily increments data-block refcounts to prevent immediate reuse while passdown discard is in flight, optionally double-checks whether blocks remain shared, then decrements the temporary refs after passdown completes. Without passdown it simply removes mapping ranges after all I/O quiesces.

Commits occur for flush/FUA-triggered bios, after pool messages, after resize, periodically via `COMMIT_PERIOD`, and during postsuspend/close. The pre-commit callback flushes the data device before metadata roots are published.

## State And Persistence Behavior
`enum pool_mode` controls behavior through function pointers: write, out-of-data-space, out-of-metadata-space, read-only, and fail. Out-of-metadata-space and read-only make metadata read-only and fail prepared mapping updates. Out-of-data-space keeps metadata writable for deletes/discards but queues or errors allocating writes depending on `error_if_no_space`; a delayed timeout flips queued behavior to `ENOSPC`. Fail mode errors all I/O and never upgrades.

Persistent state is delegated to `dm-thin-metadata.c`: created thin ids, snapshots, mappings, transaction ids, needs-check, and space-map sizes. Runtime-only state includes deferred bio lists, prison cells, pending mapping structs, active thin RCU list, mode function pointers, low-water trigger flags, and workqueue timers. On metadata operation failure, the target aborts the current transaction, sets needs-check, and moves to read-only or fail.

## Dependencies And Integration Points
This file integrates with device-mapper target registration, table events/status/messages, `dm-bio-prison-v1` for range exclusion, `dm_deferred_set` for quiescing, `dm-kcopyd` and `dm-io` for copy/zero, block-layer flush/discard APIs, and the metadata API from `dm-thin-metadata.h`. Userspace controls thin creation, snapshot creation, deletion, transaction id changes, and metadata snapshot reserve/release through pool target messages. Status output reports transaction id, metadata/data usage, held root, mode, discard/no-space policy, needs-check, and metadata threshold.

## Risks
- Snapshot consistency depends on userspace quiescing origins; the code comments explicitly warn of races around `shared` lookup and snapshot creation.
- Metadata failure handling is intentionally conservative: abort failure forces fail mode, and needs-check prevents return to write mode.
- Out-of-space queuing can hold bios until resume or timeout; tests must cover both `queue_if_no_space` and `error_if_no_space`.
- Discard passdown is multi-stage and depends on temporary refcount increments to avoid reuse races.
- Bio prison range limits require splitting discard ranges; starvation is possible if applications continuously race I/O with discard on the same region.
- The single ordered pool workqueue simplifies serialization but can become a bottleneck under heavy provisioning/discard workloads.

## Test Signals
Exercise table parsing and feature flags, read-only loads, pool/thin constructor failure unwinds, pool resume resizing, low-water dm events, metadata threshold events, create/snapshot/delete/set_transaction_id/reserve/release messages, fast-path mapped reads/writes, provisioning reads and writes with/without origin, shared-block COW, full-block overwrite optimization, flush/FUA commit ordering, discard with passdown and without passdown, no-space queue and timeout, metadata I/O failure injection, needs-check preventing write mode, suspend/noflush requeue, and status output in info/table/IMA modes.
