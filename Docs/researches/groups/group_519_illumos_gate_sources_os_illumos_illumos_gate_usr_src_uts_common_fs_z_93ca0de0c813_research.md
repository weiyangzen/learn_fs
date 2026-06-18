# Group Research: group_519_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_93ca0de0c813

Scope checked against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_pool.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_pool.c

## Role

Implements core ZFS DSL pool lifecycle and synchronization plumbing: opening/creating/closing `dsl_pool_t`, managing MOS/root/special directories, coordinating txg sync work, dirty-space accounting, pool config locking, clone upgrade helpers, and temporary user-hold pool ZAP support.

## Main Responsibilities

- Pool initialization/open/create/close:
  - `dsl_pool_open_impl()` allocates and initializes the in-core pool, txg state, MMP, txg lists, taskqs, mutexes, CVs, and async drain queues.
  - `dsl_pool_init()` opens the MOS from the root block pointer.
  - `dsl_pool_open()` resolves root, `$MOS`, `$ORIGIN`, `$FREE`, `$LEAKED`, free/obsolete bpobjs, scan state, feature objects, and temporary userrefs.
  - `dsl_pool_create()` creates the MOS, pool directory, scan state, root dir, `$MOS`, `$FREE`, free bpobj, origin snapshot, feature ZAPs, encryption feature enablement, root dataset, and root ZPL objset.
  - `dsl_pool_close()` unwinds all held dirs/datasets, bpobjs, objset, txg lists, taskqs, ARC buffers, MMP, scan state, locks, and memory.

## Synchronization Flow

`dsl_pool_sync()` is the central txg sync function. Its ordering is important:

1. Runs early sync tasks before dirty dataset blocks.
2. Writes dirty datasets, waits for their zios, then reconciles dirty-space accounting.
3. Updates user/group/project quota accounting and waits for `dp_sync_taskq`.
4. Re-syncs datasets dirtied by quota updates.
5. Finalizes dataset and dir sync state.
6. Applies accumulated MOS space deltas to `$MOS`.
7. Syncs MOS if dirty.
8. Runs normal sync tasks after data and pre-task MOS sync.
9. Commits the assigned tx.

`dsl_pool_sync_done()` then cleans dirty ZILs and confirms MOS cleanliness for the txg.

## Dirty Space and Throttling

The file defines write throttle tunables such as `zfs_dirty_data_max`, `zfs_dirty_data_sync_pct`, `zfs_delay_min_dirty_percent`, and `zfs_delay_scale`. Dirty bytes are tracked globally and per txg through `dsl_pool_dirty_space()`, `dsl_pool_undirty_space()`, and `dsl_pool_dirty_delta()`. `dsl_pool_need_dirty_delay()` kicks a txg when dirty bytes exceed the sync threshold and reports whether writers should delay.

## Space Availability

`dsl_pool_adjustedsize()` subtracts checkpoint space, deferred frees, and configurable slop reservation from pool allocatable space. `dsl_pool_unreserved_space()` further subtracts deferred metaslab allocation to produce a quota-like availability value used by sync tasks.

## Upgrade and Compatibility Helpers

- `dsl_pool_upgrade_clones()` and `upgrade_clones_cb()` repair old clone/origin metadata and populate next-clone ZAPs.
- `dsl_pool_upgrade_dir_clones()` creates `$FREE` and free bpobj during upgrade and populates `dd_clones`.
- `dsl_pool_create_origin()` creates the hidden `$ORIGIN` dataset/snapshot used by older clone accounting.

## Temporary User Holds

Pool-wide temporary hold state is maintained in `dp_tmp_userrefs_obj`.

- `dsl_pool_clean_tmp_userrefs()` reconstructs hold nvlists from `<dsobj>-<tag>` entries and releases them.
- `dsl_pool_user_hold_create_obj()` creates the pool ZAP lazily.
- `dsl_pool_user_hold()` and `dsl_pool_user_release()` add/remove temporary hold records.

## Locking Model

The long comment near the end documents the `dp_config_rwlock` contract. Holds on datasets/dirs require the config lock. User-visible mutations should generally use sync tasks, while read-only paths manually hold/release the pool and dataset. Long holds may outlive the config lock only when they intentionally prevent destruction.

## Key Dependencies

Works tightly with `dsl_dataset`, `dsl_dir`, `dsl_synctask`, `dsl_scan`, `bpobj`, `bptree`, `spa`, `txg`, `zio`, `zil`, `arc`, feature flags, and ZAP objects.

## Notable Invariants

- Early sync tasks must not dirty metaslabs; `dsl_early_sync_task_verify()` checks relevant free/checkpointing trees.
- Non-MOS datasets must not be synced twice except for the quota-update pass.
- MOS space deltas are accumulated and applied outside MOS syncing.
- Config lock helpers assert against recursive reader entry.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_pool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_prop.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_prop.c

## Role

Implements ZFS DSL property lookup, inheritance, received-property handling, property callbacks, and sync-task based property setting.

## Property Sources

The file models property source state with ZAP names:

- Local property: `<propname>`
- Explicit inherit marker: `<propname>$inherit`
- Received property: `<propname>$recvd`

`dodefault()` provides built-in defaults for valid properties, including set-once read-only defaults.

## Property Lookup

- `dsl_prop_get_dd()` walks a `dsl_dir_t` and its parents, respecting inheritable status, local values, explicit inheritance markers, received values, snapshot lookup behavior, and defaults.
- `dsl_prop_get_ds()` first checks snapshot-specific `ds_props_obj` when present, then falls back to directory lookup.
- Convenience wrappers include `dsl_prop_get()`, `dsl_prop_get_integer()`, and `dsl_prop_get_int_ds()`.

## Prediction and Quota/Reservation Handling

`dsl_prop_predict()` computes the effective value for quota/reservation/refquota/refreservation under a proposed source/value mutation. It handles old pools without received-property support by mapping received source to local behavior.

## Callback Infrastructure

Each `dsl_dir_t` owns property records, each record owns callback records:

- `dsl_prop_init()` / `dsl_prop_fini()` manage the directory property list.
- `dsl_prop_register()` registers callbacks and immediately invokes them with the current integer value.
- `dsl_prop_unregister_all()` removes callbacks by callback argument.
- `dsl_prop_notify_all()` recursively refreshes descendants, mainly after rename.
- `dsl_prop_changed_notify()` recursively propagates inherited integer property changes until overridden locally.

Important lifetime handling: callback records do not hold datasets, so notification paths use `dsl_dataset_try_add_ref()` for snapshot callback datasets that may be under eviction.

## Property Setting

- `dsl_prop_set_sync_impl()` applies source-specific mutations to local, inherit, and received ZAP entries, creates snapshot property ZAPs when needed, emits callbacks for integer properties, and logs history.
- `dsl_props_set_check()` validates dataset existence, property name length, string value length, and snapshot property support.
- `dsl_props_set()` wraps property updates in `dsl_sync_task()` and estimates modified blocks unless only clearing entries.

The setting path is intended to be all-or-nothing: check happens before sync mutation.

## Enumerating Properties

- `dsl_prop_get_all_impl()` converts ZAP entries to nested nvlists with `ZPROP_VALUE` and `ZPROP_SOURCE`, filtering local/received/inherited/snapshot validity.
- `dsl_prop_get_all_ds()` walks snapshot props and parent dirs as needed.
- `dsl_prop_get_all()` returns effective properties for an objset.
- `dsl_prop_get_received()` returns received properties when distinguishable, otherwise local properties for compatibility.
- `dsl_prop_nvlist_add_uint64()` and `dsl_prop_nvlist_add_string()` add or update formatted property entries.

## Compatibility Notes

Pools older than `SPA_VERSION_RECVD_PROPS` collapse received-source semantics into local-source behavior. Snapshot properties require `SPA_VERSION_SNAP_PROPS`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_prop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_scan.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_scan.c

## Role

Implements ZFS scrub, resilver, DDT scanning, sorted scan I/O queues, prefetch, async destroy/free processing, scan persistence, scan pause/resume/cancel, and hooks that keep scan state correct as datasets and vdev topology change.

## Scan Model

The file’s opening comment describes the modern sorted scan design:

- Metadata is traversed logically.
- Data I/O is queued by top-level vdev and sorted by physical LBA/extents.
- Memory use is bounded by hard/soft scan queue limits.
- Metadata traversal and queued I/O issuing are mutually exclusive in a txg.
- Periodic checkpoints persist restartable scan state.

Tunables control strict memory checks, inflight I/O, queue extent gaps, checkpoint interval, memory limits, scrub/resilver minimum txg time, disabling scrub I/O or prefetch, DDT class max, async free limits, and deferred resilver behavior.

## Core State and Data Structures

- `dsl_scan_phys_t` persists scan state in `DMU_POOL_SCAN`.
- `scan_ds_t` represents datasets queued for traversal.
- `scan_io_t` stores compact reconstructed block I/O metadata for sorted queues.
- `dsl_scan_io_queue_t` is per top-level vdev and owns:
  - address-sorted queued scan I/Os,
  - address and score-sorted extents,
  - memory usage,
  - inflight-byte limiting,
  - per-txg stats.
- `scan_prefetch_ctx_t` and `scan_prefetch_issue_ctx_t` support ordered metadata prefetch.

## Initialization and Persistence

- `scan_init()` creates `scan_io_t` slab caches and freezes the runtime fill-weight.
- `dsl_scan_init()` allocates scan state, loads old-style or current scan state, handles errata around historical overflow layout, reloads the dataset queue ZAP, detects restart conditions, and initializes scan stats.
- `dsl_scan_sync_state()` persists scan state only when sorted I/O queues are empty, unless writing a cached safe state after dataset mutation events.

## Starting, Canceling, Pausing

- `dsl_scan()` reopens vdevs, dispatches resilver restarts, resumes paused scrubs, or starts a new scrub via sync task.
- `dsl_scan_setup_sync()` initializes a scan, sets txg ranges, DDT class bounds, queue object, blkstats, scan events, labels, and history.
- `dsl_scan_cancel()` cancels a running scan.
- `dsl_scrub_set_pause_resume()` toggles paused scrub state and persists it with cached sync state.

## Traversal

Traversal proceeds through DDT, MOS, origin, datasets, snapshots, and clones:

- `dsl_scan_ddt()` walks dedup entries first to avoid repeated scrubbing of shared blocks.
- `dsl_scan_visit()` drives DDT, MOS, resume bookmark, and dataset queue traversal.
- `dsl_scan_visitds()` scans a dataset rootbp, handles ZIL for live heads, enqueues descendants and clones, and repeats a dataset if marked incomplete.
- `dsl_scan_recurse()`, `dsl_scan_visitdnode()`, and `dsl_scan_visitbp()` recursively read indirect blocks, dnodes, objsets, spill blocks, and accounting dnodes.
- Resume/suspend logic is bookmark-based and only resumes from safe level-0 points, while user/group/project accounting objects are never skipped.

## Prefetch

`dsl_scan_prefetch_thread()` consumes an AVL queue sorted in future traversal order. Prefetch reads metadata blocks with `ARC_FLAG_PRESCIENT_PREFETCH`, rate-limited by `spa_scrub_inflight`. Callback recursion schedules child metadata prefetches for indirect blocks, dnodes, and objsets.

## Sorted Scan I/O Queues

When not in legacy mode, `dsl_scan_enqueue()` creates per-top-level-vdev queues and inserts one `scan_io_t` per DVA unless the block is gang, in which case it is issued immediately.

Queue draining:

- `scan_io_queue_fetch_ext()` chooses the next extent: LBA order during checkpointing, largest/highest-score extent under memory pressure.
- `scan_io_queue_gather()` extracts up to 32 queued I/Os from an extent.
- `scan_io_queue_issue()` issues them and accounts pending bytes.
- `scan_io_queues_run()` dispatches one worker per top-level vdev.
- `ext_size_compare()` scores extents by fill bytes and fill ratio.

## Scrub and Resilver I/O

`dsl_scan_scrub_cb()` decides whether each block needs I/O:

- Scrub always needs I/O for in-range blocks.
- Resilver only issues I/O when DTL/vdev state says the DVA needs repair.
- ZIL blocks are speculative.
- Blocks outside the scan txg range are counted but not read.
- `scan_exec_io()` performs rate limiting, stats updates, ABD allocation, and async `zio_read()`.
- `dsl_scan_scrub_done()` frees ABD, reduces inflight counters, signals waiters, and increments scan errors except for speculative checksum failures.

## Async Destroy, Free, and Obsolete Processing

`dsl_scan_sync()` processes async destroys before scrub/resilver traversal so frees are handled before scanning. `dsl_process_async_destroys()` iterates `dp_free_bpobj`, async-destroy bptree, and obsolete bpobj, issuing frees or marking indirect mappings obsolete. It handles pause/restart by time, txg waiters, block count, shutdown, and recovery mode. It also transfers leaked free-dir accounting to `$LEAKED` when configured.

## Dataset Mutation Hooks

While a scan runs, dataset lifecycle changes rewrite cached/persistent scan state:

- `dsl_scan_ds_destroyed()` replaces or removes current/queued datasets.
- `dsl_scan_ds_snapshotted()` points traversal/queue state at the new snapshot.
- `dsl_scan_ds_clone_swapped()` swaps queued/current objset references during clone promotion.

These paths use `SYNC_CACHED` because sorted queues may contain pending I/O and the current live scan state may not be safe to persist.

## Freed-Block Queue Safety

`dsl_scan_freed()` is invoked during frees to remove corresponding cold queued scan I/Os from sorted queues. `dsl_scan_freed_dva()` finds the per-vdev queued DVA, removes it from `q_sios_by_addr`, adjusts extent fill, decrements pending bytes, and counts the block as examined. This prevents freed space from being reallocated while a stale scrub I/O remains queued.

## Vdev Interaction

- `dsl_scan_assess_vdev()` starts or restarts resilver based on DTL ranges.
- `dsl_scan_need_resilver()` checks indirect vdevs, gang blocks, partial DTL, offset need, and deferred resilver state.
- `dsl_scan_io_queue_vdev_xfer()` transfers a scan queue when top-level vdev structure changes during attach/detach.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_scan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_synctask.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_synctask.c

## Role

Provides the DSL sync task framework: a way for open-context callers to schedule checked mutations to run later in txg syncing context under the DSL pool config lock.

## Main Flow

`dsl_sync_task_common()`:

1. Opens the pool.
2. Creates and assigns a DMU tx.
3. Builds a stack `dsl_sync_task_t`.
4. Runs the check function in open context under config read lock.
5. Queues the task on either `dp_sync_tasks` or `dp_early_sync_tasks`.
6. Commits the tx.
7. Waits for the txg to sync.
8. Retries on `EAGAIN` after waiting past deferred txgs.
9. Returns the sync-context task error.

`dsl_sync_task()`, `dsl_early_sync_task()`, and `dsl_sync_task_sig()` are public wrappers.

## Early Sync Tasks

Early sync tasks run before dirty dataset blocks are written in `dsl_pool_sync()`. The file documents that they can affect the current txg’s dirty data writeout and must not dirty metaslabs.

## No-Wait Tasks

`dsl_sync_task_nowait()` and `dsl_early_sync_task_nowait()` allocate a heap task, mark `dst_nowaiter`, and enqueue without a waiter. `dsl_sync_task_sync()` frees these after execution or space-check failure.

## Sync-Context Execution

`dsl_sync_task_sync()` performs:

- optional space check against `dsl_pool_unreserved_space()`,
- MOS triple-ditto estimate by multiplying requested task space by 3,
- config writer lock acquisition,
- check function rerun in sync context,
- sync function invocation only on check success.

## Important Contract

Check functions must be valid in both open and syncing context, or detect syncing context with `dmu_tx_is_syncing(tx)`. The framework guarantees config lock read mode for preliminary checks and writer mode for sync checks/mutations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_synctask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_userhold.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_userhold.c

## Role

Implements snapshot user holds and releases, including temporary holds tied to process exit cleanup.

## Hold Creation

- `dsl_dataset_user_hold_check_one()` validates hold tag length, temporary-hold length restrictions, and duplicate tags on existing snapshots.
- `dsl_dataset_user_hold_check()` validates pool feature support, rejects duplicate snapshot/tag pairs, verifies targets are snapshots, records successful checks in `dduha_chkholds`, and records `ENOENT` entries in the error list without failing the entire operation.
- `dsl_dataset_user_hold_sync_one_impl()` creates `ds_userrefs_obj` when needed, increments `ds_userrefs`, adds the tag timestamp, optionally records pool-wide temporary hold state, and logs history.
- `dsl_dataset_user_hold()` runs the all-or-nothing hold operation as a sync task.

## Temporary Holds

Temporary holds use the pool-wide temporary userref ZAP managed by `dsl_pool_user_hold()` and are also registered with `zfs_onexit_add_cb()`. On process exit, `dsl_dataset_user_release_onexit()` reopens the same loaded pool by name and load GUID, then releases temporary holds by dataset object id.

## Release

- `dsl_dataset_user_release_check_one()` validates snapshot targets, identifies existing hold tags, adds missing hold tags to `errlist`, and marks deferred-destroy snapshots for deletion when the released holds are the last user refs and no long hold exists.
- `dsl_dataset_user_release_check()` validates all requested releases in syncing context.
- `dsl_dataset_user_release_sync_one()` removes temporary pool records if present, removes per-snapshot userref ZAP entries, decrements `ds_userrefs`, and logs history.
- `dsl_dataset_user_release_sync()` also destroys deferred snapshots that become unheld.
- `dsl_dataset_user_release()` handles normal name-keyed releases.
- `dsl_dataset_user_release_tmp()` handles temporary dsobj-keyed releases.

## Snapshot Unmounting

Before release, kernel builds call `zfs_unmount_snap()` because releasing the last hold may destroy deferred snapshots.

## Querying Holds

`dsl_dataset_get_holds()` returns hold tags and timestamps from a snapshot’s `ds_userrefs_obj`.

## Error Semantics

Missing snapshots and missing hold tags are reported in the errlist but do not necessarily fail the entire grouped request. At least one actual release is required for release success, per the documented semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_userhold.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/edonr_zfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/edonr_zfs.c

## Role

Adapts the Edon-R hash implementation to the ZFS ABD/zio checksum interface.

## Native Checksum

`abd_checksum_edonr_native()` copies a preinitialized `EdonRState` template, iterates ABD data with `abd_iterate_func()`, feeds bit lengths to `EdonRUpdate()`, finalizes a 512-bit digest, and copies the first four 64-bit words into `zio_cksum_t`.

## Salted Template

`abd_checksum_edonr_tmpl_init()` expands the checksum salt to one Edon-R block by computing `H(salt) || H(H(salt))`, initializes an Edon-R context, feeds the expanded salt block as a MAC-like key, and returns that context as the checksum template. `abd_checksum_edonr_tmpl_free()` zeros and frees it.

## Byteswap Path

`abd_checksum_edonr_byteswap()` calls the native routine into a local `tmp`, then intends to byteswap the words for alternate endian use. As written, it byteswaps `zcp->zc_word[]` rather than `tmp.zc_word[]`, leaving the local native checksum unused. This is a notable implementation issue in this file.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/edonr_zfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/gzip.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/gzip.c

## Role

Small wrapper around ZFS zmod compression APIs for gzip compression and decompression.

## Compression

`gzip_compress()` calls `z_compress_level()` with the requested compression level. It asserts destination length is no larger than source length, matching ZFS’s “compression must save space” calling convention.

If compression fails:

- When destination is smaller than source, it returns `s_len` to signal no useful compression.
- When destination equals source, it copies input to output and returns `s_len`.

On success it returns compressed byte count.

## Decompression

`gzip_decompress()` calls `z_uncompress()` and returns `0` on success or `-1` on failure. It asserts the destination length can hold at least the source length.

## Dependencies

Uses `sys/zmod.h`; includes kernel or userland string/system headers depending on `_KERNEL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/gzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/hkdf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/hkdf.c

## Role

Implements HKDF-SHA512 for ZFS encryption key derivation using the illumos kernel crypto API.

## Extract

`hkdf_sha512_extract()` computes HMAC-SHA512 with the salt as the raw crypto key and input key material as data. It writes the pseudorandom key to a SHA-512 digest-sized output buffer and maps crypto failures to `EIO`.

## Expand

`hkdf_sha512_expand()` uses the extracted key as the HMAC key and iteratively computes HKDF blocks over `T(previous) || info || counter`. It copies each block into the output buffer, with the final block truncated to remaining output length. It rejects more than 255 blocks.

A detail to preserve: the block count is computed as `(out_len + SHA512_DIGEST_LENGTH) / SHA512_DIGEST_LENGTH`, which is one higher than the usual ceiling formula for exact digest-size multiples. That causes an extra zero-byte-copy HMAC round for exact multiples and rejects the theoretical maximum exact length one block early.

## Public API

`hkdf_sha512()` runs extract then expand and returns the first error, or `0` on success.

## Usage Context

The file comment states this is used to derive fresh encryption keys from a master key and salt to avoid cryptographic limits of underlying encryption modes. It notes that elsewhere in the code the HKDF `info` parameter is commonly referred to as “salt”.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/hkdf.c -->