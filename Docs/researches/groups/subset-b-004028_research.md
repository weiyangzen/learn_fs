# subset-b-004028 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-thin-metadata.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-thin-metadata.c

## Purpose
`dm-thin-metadata.c` is the persistent metadata engine for the device-mapper thin provisioning target. It owns the on-disk superblock, metadata and data space maps, the two-level mapping btree `(thin device id, virtual block) -> packed(data block, time)`, and the device-details btree `thin id -> mapped block count / creation / snapshot times`. It is the transactional persistence layer used by `dm-thin.c`; it does not map bios itself.

## Important APIs, Types, And Functions
- `struct thin_disk_superblock` is the packed block-zero disk format. It contains checksum, feature flags, transaction id, held metadata snapshot root, space-map roots, mapping/detail roots, block sizes, and metadata device size.
- `struct dm_pool_metadata` is the in-memory pool metadata handle. Key fields are the block manager, transaction managers, metadata/data space maps, btree descriptors, `root_lock`, current transaction/time fields, in-service/fail flags, metadata reserve, and pre-commit callback.
- `struct dm_thin_device` tracks an opened virtual device, cached details, open count, changed flag, aborted-with-changes flag, and mapped block count.
- Superblock validation is handled by `sb_prepare_for_write()` and `sb_check()` using `dm_bm_checksum()` and `THIN_SUPERBLOCK_MAGIC`.
- `dm_pool_metadata_open()` creates block-manager and persistent-data objects, formats all-zero metadata when permitted, opens the current transaction, and calculates metadata reserve.
- `dm_pool_commit_metadata()` commits changed device details, data space-map roots, transaction-manager state, superblock roots, transaction id, flags, and then begins the next transaction.
- `dm_pool_abort_metadata()` destroys current persistent objects except the block manager, resets the block manager, reopens the last committed transaction, and sets `fail_io` if rollback fails.
- Device APIs include `dm_pool_create_thin()`, `dm_pool_create_snap()`, `dm_pool_delete_thin_device()`, `dm_pool_open_thin_device()`, and `dm_pool_close_thin_device()`.
- Mapping APIs include `dm_thin_find_block()`, `dm_thin_find_mapped_range()`, `dm_pool_alloc_data_block()`, `dm_thin_insert_block()`, and `dm_thin_remove_range()`.

## Control Flow
Opening first creates a `dm_block_manager`, then either formats or opens metadata. Formatting creates transaction manager and space maps, initializes mapping and details btrees, commits the space map, and writes an initial superblock. Opening validates the existing superblock, rejects unsupported feature flags, opens transaction manager and both space maps from roots, creates a non-blocking transaction-manager clone, loads mapping roots, and initializes btree descriptors.

Transactions flow through `__commit_transaction()`: optional pre-commit callback, flush changed `dm_thin_device` details into the details btree, commit data space map, pre-commit the transaction manager, copy both space-map roots into scratch buffers, lock the superblock for write, update time/root/detail-root/trans-id/flags/space-map roots, and commit through `dm_tm_commit()`. `dm_pool_commit_metadata()` wraps this under `root_lock` without marking the pool in-service and calls `__begin_transaction()` afterward.

Thin creation creates an empty bottom-level mapping tree, inserts its root into the top-level tree, then opens a new device details entry. Snapshot creation looks up and increments the origin mapping-root reference, inserts that root under the new device id, increments metadata time, opens the snapshot details, and updates origin/snapshot `snapshotted_time` so lookup can report shared blocks. Deletion removes the details entry and top-level mapping-tree entry after verifying the device is not open more than once.

Lookup uses `dm_btree_lookup()` on the two-level mapping tree and decodes the packed block/time. `shared` is inferred from `td->snapshotted_time > exception_time`, so sharing detection is timestamp based. Range lookup walks contiguous mapped blocks while physical block numbers and maybe-shared state remain adjacent. Insert packs current pool time with the allocated data block and increments mapped count only on new insertion. Range removal temporarily removes and pins the device mapping tree, removes leaves across mapped runs, updates mapped count, then reinserts the updated root.

## State And Persistence Behavior
The file persists all authoritative thin-pool metadata under block-zero superblock roots and persistent-data btrees. `root_lock` serializes metadata mutation and protects readers. The `in_service` flag avoids committing a newly opened pool solely because open/close happened; interfaces that imply live service call `pmd_write_lock()` and set it. `fail_io` is a hard error state after abort rollback failure; most public APIs then return `-EINVAL`, leaving close as the only useful operation.

Metadata snapshots reserve a held superblock copy in `held_root`. Reservation commits first, shadows block zero, increments mapping/detail roots to keep them alive, wipes space-map roots from the copy, and stores the held root in the live superblock. Release clears `held_root`, deletes preserved mapping/detail trees, and decrements the metadata block. The held root is intended for userspace read-only inspection.

Metadata reserve hides up to 4096 blocks or 10 percent of metadata space from free-space reporting, protecting commit overhead. `THIN_METADATA_NEEDS_CHECK_FLAG` is written directly to the superblock by `dm_pool_metadata_set_needs_check()` when repair is required.

## Dependencies And Integration Points
This file depends heavily on `persistent-data/dm-btree`, `dm-space-map`, `dm-space-map-disk`, `dm-transaction-manager`, and block-manager validation. `dm-thin.c` is the primary consumer. It registers a pre-commit callback that flushes the data device before metadata commit, uses metadata thresholds for dm events, calls create/snapshot/delete APIs from target messages, allocates data blocks while provisioning, and switches pool modes based on metadata API errors.

## Risks
- Timestamp-based shared-block detection intentionally overestimates sharing; this can cause extra copy-on-write work.
- Any failure during abort/reopen sets `fail_io`, making the pool effectively unrecoverable in-kernel until external repair.
- Metadata snapshot reservation increases copy-on-write pressure and must be released promptly by userspace.
- `__remove_range()` has multiple intermediate btree operations; failures can leave the active transaction invalid enough that callers must abort and mark needs-check.
- Feature flag support is zero for compat and incompat masks in this file; future metadata features must update these checks carefully.
- Metadata resize refuses shrink and relies on superblock/device-size comparisons in the target frontend.

## Test Signals
Useful tests include format/open/reopen on all-zero and existing metadata, create/open/close/delete thin devices, snapshot creation after quiescing origin, lookup shared/unshared transitions, commit and crash-reopen consistency, abort after injected metadata I/O failures, metadata snapshot reserve/release/get, resize grow-only behavior, low metadata free-space reserve accounting, and `needs_check` preventing return to write mode in `dm-thin.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-thin-metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-thin-metadata.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-thin-metadata.h

## Purpose
This header defines the public metadata contract between the thin target frontend and the thin metadata engine. It exposes opaque pool/device handles, thin device identifiers, metadata limits, superblock flags, feature masks, transaction APIs, mapping APIs, free-space/stat APIs, resize APIs, read-only toggles, threshold callbacks, and the pre-commit callback hook.

## Important APIs, Types, And Functions
- `THIN_METADATA_BLOCK_SIZE`, `THIN_METADATA_MAX_SECTORS`, and `THIN_METADATA_MAX_SECTORS_WARNING` bind thin metadata sizing to persistent-data space-map metadata limits.
- `THIN_METADATA_NEEDS_CHECK_FLAG` marks metadata requiring userspace repair.
- `dm_thin_id` is a `uint64_t`; `dm-thin.c` narrows accepted ids to 24 bits.
- `struct dm_pool_metadata` and `struct dm_thin_device` are opaque outside the implementation.
- `struct dm_thin_lookup_result` returns a physical pool block and a `shared` hint.
- Creation/deletion APIs are `dm_pool_create_thin()`, `dm_pool_create_snap()`, and `dm_pool_delete_thin_device()`.
- Transaction APIs are `dm_pool_commit_metadata()`, `dm_pool_abort_metadata()`, transaction id get/set, and metadata snapshot reserve/release/get.
- Per-device APIs include open/close, lookup, mapped range lookup, insert, remove range, mapped-count, highest mapped block, and changed/aborted-change queries.
- Pool APIs include data allocation, free counts, device sizes, shared-block query, data refcount range inc/dec, data/metadata resize, read-only/read-write, metadata threshold registration, prefetch issue, and pre-commit callback registration.

## Control Flow And Contracts
The header documents the central operational sequencing: callers create/open pool metadata, create or open thin devices, perform lookup/allocation/insert/remove operations, then commit all metadata changes as one transaction. Snapshot creation requires a quiesced origin. `dm_pool_abort_metadata()` rolls back uncommitted changes while leaving thin devices open and reports per-device aborted changes through `dm_thin_aborted_changes()`.

`dm_thin_find_block()` documents `-ENODATA` for absent mapping and `-EWOULDBLOCK` when non-blocking lookup cannot issue I/O. The frontend uses this in `thin_bio_map()` to fast-path already cached mappings and defer misses or blocking cases to the worker.

## State And Persistence Behavior
The header’s API is stateful: all mapping, free-space, transaction-id, resize, held-root, and needs-check behavior ultimately persists in `dm-thin-metadata.c`. The read-only/read-write toggles act on the block manager, not just on callers. The pre-commit callback is explicitly part of metadata commit ordering and is used by the thin-pool target to flush data before publishing metadata roots.

## Dependencies And Integration Points
It includes persistent-data block-manager, space-map, and metadata-space-map headers because callers need `dm_block_t`, `dm_sm_threshold_fn`, and metadata size constants. `dm-thin.c` is the main in-tree consumer in this subset. Userspace integration is indirect through target messages and status output implemented in `dm-thin.c`.

## Risks
- The comment for `dm_pool_open_thin_device()` says opening the same device more than once returns `-EBUSY`, while the implementation increments open count for an already open non-create device; consumers must rely on implementation behavior or verify current upstream semantics.
- `dm_pool_resize_data_dev()` comment mentions `-ENOSPC` for too-small resize, while implementation reports shrink as `-EINVAL`; tests should lock down expected behavior.
- The shared bit is only a hint based on metadata timestamps and may over-report sharing.
- Callers must respect quiescing requirements for snapshots; the metadata layer does not enforce application-level consistency.

## Test Signals
Header-level contract tests should validate documented error codes against implementation, non-blocking lookup behavior, abort/change flags, metadata snapshot lifecycle, read-only/write-mode transitions, threshold callback registration, and commit pre-callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-thin-metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-thin.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-thin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-uevent.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-uevent.c

## Purpose
`dm-uevent.c` implements optional device-mapper uevent support for path-related target events. It builds environment payloads for failed/reinstated paths, queues them on a mapped device, and later sends them through the kernel kobject uevent mechanism.

## Important APIs, Types, And Functions
- `_dm_uevent_type_names[]` maps `DM_UEVENT_PATH_FAILED` and `DM_UEVENT_PATH_REINSTATED` to `KOBJ_CHANGE` and string actions.
- `struct dm_uevent` stores target mapped-device pointer, kobject action, uevent environment, list node, and copied DM name/UUID buffers.
- `dm_uevent_init()` creates a slab cache for events; `dm_uevent_exit()` destroys it.
- `dm_path_uevent()` validates event type, builds a path uevent, and queues it with `dm_uevent_add()`.
- `dm_send_uevents()` drains a list, appends current `DM_NAME` and `DM_UUID`, sends via `kobject_uevent_env()`, and frees each event.

## Control Flow
Targets call `dm_path_uevent()` with target pointer, path string, and valid path count. The code obtains the mapped device from the target table, allocates an event with `GFP_ATOMIC`, populates `DM_TARGET`, `DM_ACTION`, `DM_SEQNUM`, `DM_PATH`, and `DM_NR_VALID_PATHS`, then queues the list node on the mapped device. Later, mapped-device uevent dispatch calls `dm_send_uevents()`, which removes each event from the list, copies device name/UUID while the device still exists, appends those fields, invokes `kobject_uevent_env()`, logs send failures, and frees the slab object.

## State And Persistence Behavior
There is no persistent state. Runtime state is the slab cache and queued `struct dm_uevent` objects. Sequence numbers come from `dm_next_uevent_seq(md)`. Events are best-effort: if the mapped device name/UUID can no longer be copied during removal, the event is skipped and freed.

## Dependencies And Integration Points
The file depends on DM core helpers from `dm.h`, `dm-uevent.h`, `dm_table_get_md()`, `dm_uevent_add()`, `dm_copy_name_and_uuid()`, and `dm_next_uevent_seq()`. It uses kernel kobject uevents, slab cache allocation, and exported GPL symbols so targets such as multipath can report path state changes.

## Risks
- Allocation uses `GFP_ATOMIC`; pressure can drop events.
- Environment addition failure collapses to `-ENOMEM` and drops the event.
- Only path failed/reinstated events are supported by the local enum mapping.
- Events are skipped if the device is disappearing before dispatch.

## Test Signals
Test init/exit cache lifecycle, invalid event type rejection, allocation failure path, each `add_uevent_var()` failure path, queued event list draining, name/UUID copy failure during device removal, `DM_SEQNUM` monotonicity, and generated environment variables for both path event types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-uevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-uevent.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-uevent.h

## Purpose
This header declares the optional DM uevent interface and provides no-op inline stubs when `CONFIG_DM_UEVENT` is disabled. It lets DM core and targets call the same functions regardless of configuration.

## Important APIs, Types, And Functions
- `enum dm_uevent_type` defines `DM_UEVENT_PATH_FAILED` and `DM_UEVENT_PATH_REINSTATED`.
- Enabled builds export declarations for `dm_uevent_init()`, `dm_uevent_exit()`, `dm_send_uevents()`, and `dm_path_uevent()`.
- Disabled builds return success for init and make send/path/exit functions no-ops.

## Control Flow
Compile-time configuration selects either real definitions in `dm-uevent.c` or static inline stubs. Callers can unconditionally initialize uevent support, queue path events, and flush event lists without local `#ifdef` blocks.

## State And Persistence Behavior
The header itself stores no state. In disabled builds, no queued event state exists and all event requests are intentionally ignored.

## Dependencies And Integration Points
The prototypes refer to `struct list_head`, `struct kobject`, and `struct dm_target` through included or prior kernel declarations in compile units. It is included by DM core code and targets that report path state.

## Risks
- Disabled builds silently drop path events; tests must account for configuration.
- Adding new event enum values requires updating `_dm_uevent_type_names[]` in the C file.

## Test Signals
Build both `CONFIG_DM_UEVENT=y/m` and disabled configurations, verify no unresolved symbols in disabled mode, and verify callers do not depend on side effects from no-op stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-uevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-unstripe.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-unstripe.c

## Purpose
`dm-unstripe.c` implements the `unstriped` device-mapper target. It exposes one selected stripe from an already-striped layout as a linear virtual device by translating virtual sectors to the corresponding sectors on a backing striped device.

## Important APIs, Types, And Functions
- `struct unstripe_c` stores the backing `dm_dev`, physical start offset, total stripes, selected stripe, computed unstripe width/offset, chunk size, and optional power-of-two chunk shift.
- `unstripe_ctr()` parses target arguments: `<number of stripes> <chunk size> <stripe #> <dev_path> <offset>`.
- `map_to_core()` computes the backing sector by finding the stripe row and adding skipped stripe widths plus selected-stripe offset.
- `unstripe_map()` sets the bio device and translated sector.
- `unstripe_status()`, `unstripe_iterate_devices()`, and `unstripe_io_hints()` provide table output, underlying-device reporting, and chunk hints.

## Control Flow
Constructor validation checks argument count, stripe count, chunk size, stripe number, backing device open, offset parse, target length divisibility by chunk size, and max I/O length setup. It precomputes `unstripe_offset = unstripe * chunk_size`, `unstripe_width = (stripes - 1) * chunk_size`, and `chunk_shift` for power-of-two chunk sizes. Mapping gets the target-relative sector, divides by chunk size to get the row, adds the width skipped for other stripes in prior rows, then adds selected stripe offset and physical start.

## State And Persistence Behavior
The target has only table/runtime state in `struct unstripe_c`; it persists no metadata. Status table output reconstructs constructor arguments.

## Dependencies And Integration Points
It integrates with DM target registration through `module_dm(unstripe)`, uses `dm_get_device()`/`dm_put_device()`, `dm_target_offset()`, `dm_set_target_max_io_len()`, and queue limits. It depends on block-layer bio remapping and DM table modes.

## Risks
- The stripe number validation allows `uc->unstripe == uc->stripes` when `stripes > 1` because it checks `>` rather than `>=`; valid stripe indexes appear to be zero-based from the offset formula.
- Arithmetic overflow should be considered for very large target lengths, chunk sizes, or stripe counts.
- The target requires length divisible by chunk size but does not require the selected stripe to be within a stricter zero-based range.

## Test Signals
Test constructor reject paths, non-power-of-two and power-of-two chunk mapping equivalence, boundary sectors at chunk transitions, table status roundtrip, iterate-devices range, queue chunk hints, and stripe index equal to stripe count behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-unstripe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/Kconfig

## Purpose
This Kconfig entry exposes the VDO device-mapper target, described as a deduplication, compression, and thin-provisioning target.

## Important APIs, Types, And Functions
- `config DM_VDO` is a tristate option named `VDO: deduplication and compression target`.
- It depends on `64BIT` and `BLK_DEV_DM`.
- It selects `DM_BUFIO`, `LZ4_COMPRESS`, `LZ4_DECOMPRESS`, and `MIN_HEAP`.

## Control Flow
The build system includes the VDO target only when this option is enabled as built-in or module. If built as a module, the help text states the module name is `dm-vdo`.

## State And Persistence Behavior
Kconfig stores build-time selection only. Runtime VDO state is implemented by the C files included by the Makefile.

## Dependencies And Integration Points
The entry integrates VDO into the kernel configuration graph and ensures required compression, decompression, buffer I/O, and heap helpers are selected with the target.

## Risks
- VDO is unavailable on non-64-bit builds.
- Missing or incorrect selected dependencies would surface as build or link failures in the VDO object set.

## Test Signals
Build `DM_VDO=n`, `m`, and `y` where supported; verify dependency selection, module name, and that VDO object compilation follows the selected state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/Makefile

## Purpose
This Makefile defines how the `dm-vdo` composite object is built and which source files form the VDO target, including its indexer implementation.

## Important APIs, Types, And Functions
- `ccflags-y := -I$(src) -I$(src)/indexer` makes both the VDO root and indexer headers visible.
- `obj-$(CONFIG_DM_VDO) += dm-vdo.o` ties the object to the Kconfig option.
- `dm-vdo-objs` lists core VDO components such as admin state, action manager, block map, completion, dedupe, target glue, journal, slab depot, VIO, queues, logging, and many indexer files.

## Control Flow
Kbuild compiles each listed object and links them into `dm-vdo.o` when `CONFIG_DM_VDO` is enabled. Header lookup relies on local include paths rather than global kernel include directories.

## State And Persistence Behavior
The Makefile has no runtime state. It is the build manifest that determines which source modules participate in the VDO target binary.

## Dependencies And Integration Points
It integrates the VDO target into `drivers/md` Kbuild and explicitly pulls indexer subdirectory sources into the same module. The files researched here, `action-manager.o` and `admin-state.o`, are early entries in this object list.

## Risks
- Missing a source file from `dm-vdo-objs` can produce unresolved symbols or silently omit functionality.
- Include path changes can break local quoted includes across the root/indexer boundary.
- Object ordering usually should not matter for linking, but duplicate symbols or init ordering assumptions should be watched.

## Test Signals
Run kernel builds for `CONFIG_DM_VDO=m/y`, check that all listed objects compile, verify local header includes resolve, and run link/modpost checks for unresolved or duplicate symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/action-manager.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/action-manager.c

## Purpose
`action-manager.c` implements a VDO helper that serializes administrative actions across a multi-zone object. Each action can run an initiator-thread preamble, an asynchronous per-zone callback on each zone thread, an initiator-thread conclusion, and then notify a parent completion. It allows one active action and one pending action.

## Important APIs, Types, And Functions
- `struct action` stores in-use state, associated admin operation, preamble, zone action, conclusion, parent completion, action context, and circular next pointer.
- `struct action_manager` stores the completion used to requeue work, `struct admin_state`, two action slots, current action pointer, zone count, default scheduler, zone-thread getter, initiator thread id, manager context, and current zone index.
- `vdo_make_action_manager()` allocates the manager, initializes the two-slot ring, sets normal admin state, and initializes a `VDO_ACTION_COMPLETION`.
- `vdo_schedule_operation_with_context()` is the main scheduler, filling the current or next slot or completing the parent with `VDO_COMPONENT_BUSY`.
- `launch_current_action()` starts the admin operation and invokes the preamble, arranging requeue to the first zone or conclusion.
- `apply_to_zone()` runs zone actions one zone at a time on zone-specific threads.
- `finish_action_callback()` clears the completed slot, optionally schedules default or pending work, runs conclusion, finishes admin state, and continues parent completion.

## Control Flow
Scheduling must happen on the configured initiator thread. If no action is active, the new action launches immediately; otherwise it fills the one pending slot. Launch calls `vdo_start_operation()` against the manager admin state. If the operation cannot start, the parent gets the error, conclusion is suppressed, and the action finishes. Otherwise the preamble is called. On successful preamble, the manager completion is requeued across zone threads through `apply_to_zone()`. After the last zone, the completion requeues back to the initiator thread and runs `finish_action_callback()`.

Errors are preserved through `preserve_error()`, which propagates completion result to the parent, resets the manager completion, and reruns it. Preamble errors skip zone actions and go directly to finish.

## State And Persistence Behavior
There is no disk persistence. Runtime state is the two-slot action queue and embedded admin state. `vdo_start_operation()`/`vdo_finish_operation()` prevent overlapping admin operations. The copied `struct action` in `finish_action_callback()` avoids use-after-free if the conclusion or parent continuation frees the manager.

## Dependencies And Integration Points
The manager depends on `admin-state`, `completion`, `status-codes`, `memory-alloc`, `permassert`, thread ids from `types.h`, and VDO completion scheduling. VDO subsystems such as block maps or slab depots can use it to apply operations to all zones while preserving per-zone thread affinity.

## Risks
- Only one pending action is supported; additional schedules fail with `VDO_COMPONENT_BUSY`.
- Scheduling from the wrong thread is asserted log-only, so production behavior depends on callers obeying the contract.
- Parent completions may run during error or finish paths; ownership/lifetime must account for callbacks freeing the manager or context.
- Default action scheduling is attempted only when current operation is normal and no pending action is in use.

## Test Signals
Test immediate action, queued pending action, third-action busy result, NULL preamble/action/conclusion defaults, preamble failure, operation-start failure, per-zone thread routing, zero/one/many zones if allowed by callers, parent completion result propagation, default scheduler launch, and manager-freeing conclusion callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/action-manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/action-manager.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/action-manager.h

## Purpose
This header declares the VDO action-manager interface for applying serialized administrative actions to multi-zone VDO components with initiator-thread preambles/conclusions and zone-thread callbacks.

## Important APIs, Types, And Functions
- `vdo_zone_action_fn` runs asynchronously for a zone and reports through a parent completion.
- `vdo_action_preamble_fn` runs on the action manager initiator thread before zone work.
- `vdo_action_conclusion_fn` runs on the initiator thread after zone work and returns a VDO status.
- `vdo_action_scheduler_fn` optionally schedules default work.
- `vdo_zone_thread_getter_fn` maps a zone number to a VDO thread id.
- Public functions allocate a manager, inspect current operation/action context, schedule default actions, schedule generic actions, schedule explicit admin operations, and schedule operations with an action-specific context.

## Control Flow
Callers construct an action manager with zone count, zone-thread resolver, initiator thread id, context, optional scheduler, and owning `struct vdo`. They then schedule actions or operations; implementation serializes them and invokes callbacks in the documented order. At least one of preamble, zone action, or conclusion must be supplied by contract, though the implementation substitutes no-op functions for NULL preamble/conclusion.

## State And Persistence Behavior
The header exposes an opaque `struct action_manager`. Runtime state is internal to the implementation and includes current admin operation and optional current action context. No persistent state is represented here.

## Dependencies And Integration Points
It depends on `admin-state.h` and `types.h`, plus `struct vdo_completion` and `struct vdo`. It is used by VDO components that need coordinated per-zone administrative operations.

## Risks
- The API does not expose queue depth beyond success/failure; callers must handle `false` scheduling and parent `VDO_COMPONENT_BUSY`.
- Callback threading is part of the contract; misuse can create race conditions in zone-owned structures.
- Context lifetime must outlive asynchronous callbacks.

## Test Signals
Compile all callback typedef users, test scheduling return values, operation-code reporting, current action context retrieval, default scheduler behavior, and callbacks running on expected thread ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/action-manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/admin-state.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/admin-state.c

## Purpose
`admin-state.c` implements VDO administrative state transitions. It defines the canonical state-code objects, validates whether operations can begin from the current state, tracks waiters, supports loading/draining/resuming operation families, and completes transitions to next states.

## Important APIs, Types, And Functions
- Static `VDO_CODE_*` objects define state names and flags such as `normal`, `draining`, `loading`, `quiescing`, `quiescent`, and `operating`.
- Exported pointers such as `VDO_ADMIN_STATE_NORMAL_OPERATION`, `VDO_ADMIN_STATE_SAVING`, `VDO_ADMIN_STATE_SUSPENDING`, and `VDO_ADMIN_STATE_RESUMING` identify states by pointer identity.
- `get_next_state()` encodes allowed transitions and final states for operations.
- `begin_operation()` validates state, waiter absence, sets `waiter`, `next_state`, current operation, and optionally calls an initiator.
- `vdo_finish_operation()` completes an operating state, updates final state when initiation has unwound, sets waiter result, and launches waiter completion.
- Specialized wrappers include `vdo_start_loading()`, `vdo_finish_loading_with_result()`, `vdo_start_draining()`, `vdo_finish_draining_with_result()`, `vdo_start_resuming()`, and `vdo_finish_resuming_with_result()`.
- `vdo_resume_if_quiescent()` moves quiescent states back to normal operation.

## Control Flow
Start functions first validate the requested operation class. Generic operations require `operation->operating`; loading requires `operation->loading`; draining requires `operation->draining`; resuming requires the exact resume state. `begin_operation()` rejects starts if the current code is already operating, the operation is invalid from the current state, or another waiter exists. If accepted, it installs the waiter and next state, switches current state to the operation, and invokes an optional initiator with `starting=true`.

If an initiator completes synchronously, `vdo_finish_operation()` may be deferred until `starting` is false by using the `complete` flag. Normal finish sets waiter result, changes to `next_state`, forgets and launches the waiter completion. Draining short-circuits if already quiescent by launching the waiter without starting a new operation.

## State And Persistence Behavior
State is in-memory only in `struct admin_state`. The code uses pointer-valued state codes and `READ_ONCE`/`WRITE_ONCE` accessors from the header. A single `waiter` serializes administrative operations. `next_state`, `starting`, and `complete` handle synchronous and asynchronous operation completion without double finishing.

## Dependencies And Integration Points
The file depends on VDO logging, memory helpers, assertions, completions, status codes, and type definitions. `action-manager.c` uses `vdo_start_operation()` and `vdo_finish_operation()` to serialize zone actions. Broader VDO lifecycle code uses the loading, draining, saving, stopping, suspending, and resuming wrappers.

## Risks
- State identity relies on exported pointer constants; callers must not fabricate equivalent structs.
- `get_next_state()` is the central policy table; missing a transition produces `VDO_INVALID_ADMIN_STATE`.
- A stale waiter blocks all new operations with `VDO_COMPONENT_BUSY`.
- Quiescent drain calls launch the waiter and return false, which callers must not misinterpret as an error path requiring another completion.
- Incorrect initiator behavior can stress the `starting`/`complete` handshake.

## Test Signals
Test allowed and rejected transitions from every state, concurrent waiter rejection, synchronous initiator finish, asynchronous finish, invalid operation-class checks, quiescent drain shortcut, resume from quiescent states, result propagation to waiters, and pointer identity assumptions for state comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/admin-state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/admin-state.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/admin-state.h

## Purpose
This header defines VDO administrative state data structures, exported state-code pointers, inline state predicates, and operation transition APIs.

## Important APIs, Types, And Functions
- `struct admin_state_code` names a state and classifies it with booleans: normal, draining, loading, quiescing, quiescent, and operating.
- Exported state pointers cover normal operation, generic operation, formatting, pre-loading, loading variants, recovery/rebuild, saving/saved, scrubbing, stopping/stopped, suspending/suspended, suspended operation, and resuming.
- `struct admin_state` stores current state, next state, waiter completion, and synchronous-start flags.
- `vdo_admin_initiator_fn` is an optional callback invoked when an operation starts.
- Inline helpers read/write current state and test state classes or exact states.
- Public transition functions start/finish loading, draining, resuming, generic operations, resume if quiescent, and finish operations.

## Control Flow
Users initialize an `admin_state` by setting its code, usually to one of the exported pointers. They call a start function with an operation code and optional waiter/initiator. Later they call the matching finish function to transition to the computed next state and notify the waiter. Inline predicates let other subsystems gate I/O, drains, and lifecycle work.

## State And Persistence Behavior
The header describes in-memory administrative state only. The current code is accessed with `READ_ONCE` and `WRITE_ONCE`, giving simple visibility guarantees for lockless readers but not replacing higher-level serialization around state transitions.

## Dependencies And Integration Points
It includes VDO completion and type headers. The interface is used by the action manager and VDO lifecycle components to reject overlapping operations, identify quiescent states, and coordinate waiters.

## Risks
- Because state codes are pointers to exported constants, direct pointer comparisons are expected and must remain stable.
- Inline predicates expose flags directly; changes to state flag definitions affect many callers.
- `vdo_set_admin_state_code()` is public but documented primarily for initialization/internal use; arbitrary external use could bypass transition validation.

## Test Signals
Compile users of all predicates and transition prototypes, verify initialization to each exported state, test lockless predicate reads under transition stress, and validate that direct state-code pointer comparisons match expected lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/admin-state.h -->
