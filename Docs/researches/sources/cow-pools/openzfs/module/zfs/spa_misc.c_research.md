# File Research: sources/cow-pools/openzfs/module/zfs/spa_misc.c

## Role

`spa_misc.c` is the central miscellaneous support file for the Storage Pool Allocator. It defines the SPA namespace, SPA config lock implementation, pool object allocation/destruction, reference management, global spare and L2ARC-device tracking, administrative vdev locking wrappers, pool accessors, space accounting helpers, import-progress reporting, initialization/finalization ordering, scan/stat helpers, exported symbols, and many module tunables.

It is not a single algorithmic unit. Its main value is coordinating cross-subsystem invariants and providing common state-management routines used by vdev, DMU, DSL, ZIO, scan, import/export, and pool administration paths.

## Locking Model

The opening block documents the SPA locking hierarchy. `spa_namespace_lock` protects pool namespace lookup/add/remove, zero-to-nonzero refcount transitions, rename, import/export boundaries, and vdev topology operations. `spa_refcount` tracks active users. `spa_config_lock[]` is an ordered set of handoff-capable rw-style locks: `SCL_CONFIG`, `SCL_STATE`, `SCL_ALLOC`, `SCL_ZIO`, `SCL_FREE`, and `SCL_VDEV`.

`spa_config_lock_init()` and `spa_config_lock_destroy()` initialize and tear down the per-SPA lock array. `spa_config_tryenter()` tries a subset of locks and unwinds partial acquisition on conflict. `spa_config_enter_impl()` handles reader/writer acquisition, writer preference, and priority reader acquisition for MMP. `spa_config_exit()` releases in reverse lock order and broadcasts waiters. `spa_config_held()` tests reader/writer holdings.

The namespace wrapper functions provide enter, tryenter, interruptible enter, exit, wait, broadcast, and held checks. `spa_lookup()` normalizes dataset-like names to pool names and waits out concurrent import/export activity not owned by the current thread.

## SPA Lifecycle

`spa_add()` allocates and initializes a new `spa_t`: mutexes, condition variables, per-TXG free bplists, identity fields, deadman settings, allocator selection, refcount, config locks, stats, namespace AVL insertion, altroot/cachefile configuration, label feature nvlists, feature refcount cache, allocation geometry defaults, flushed metaslab/log-space-map AVL trees, log summary list, config list, load info, and leaf list.

`spa_remove()` performs the matching teardown after the pool is closed and uninitialized. It removes the SPA from the namespace, frees root/load-name/config structures, destroys allocator state, AVL/list structures, nvlists, config, refcount, stats, config locks, bplists, checksum templates, CVs, mutexes, and finally the `spa_t` itself.

`spa_init()` initializes global SPA state and dependent subsystems in a specific order, including FMA, refcounts, unique IDs, btrees, metaslab stats, BRT, DDT, ZIO, DMU, ZIL, vdev stats/math/file support, properties, checksums, features, scan, QAT, import-progress procfs, and ZAP. `spa_fini()` evicts all pools and tears these down in reverse-compatible order.

## Vdev Administration

`spa_vdev_enter()` and `spa_vdev_detach_enter()` acquire `spa_vdev_top_lock`, the namespace lock, stop autotrim, optionally stop rebuild for detach, and enter all config locks as writer through `spa_vdev_config_enter()`. The returned TXG is one past the last synced TXG.

`spa_vdev_config_exit()` reassesses DTLs, notes config changes, validates metaslab classes, exits all config locks, optionally triggers panic injection, waits for the requested TXG to sync on success, cancels initialize/trim/autotrim for a removed vdev, frees detached vdev state under state locks, and writes the cachefile when configuration changed. `spa_vdev_exit()` restarts autotrim and rebuild, calls the config exit helper, releases namespace and top-lock, and returns the operation error.

`spa_vdev_state_enter()` and `spa_vdev_state_exit()` cover state-only changes such as online/offline/fault/degrade/clear. Root pools split lock acquisition around `SCL_ZIO` so opening vdevs does not deadlock on root filesystem I/O. State exit reassesses DTLs, dirties top vdev state when needed, waits for sync for user-visible synchrony, and updates the cachefile on config change.

## Namespace, Refcounts, And Aux Devices

`spa_open_ref()`, `spa_close()`, `spa_async_close()`, and `spa_refcount_zero()` wrap SPA refcount operations with assertions appropriate to namespace locking, pool import/export, or async dataset eviction.

Hot spares and L2ARC cache devices use the shared `spa_aux_t` AVL helper functions. Spares maintain a reference count and active pool GUID because a spare can be listed in multiple pools and active in one. L2ARC devices use the same infrastructure, though cache devices currently only support one active pool. Public routines add, remove, test, and activate spare/L2ARC entries under their own global locks.

## Space And Allocation Helpers

The file defines important pool-space tunables and calculations. `spa_get_worst_case_asize()` inflates logical size by `spa_asize_inflation`, accounting for worst-case RAID-Z parity, multiple DVAs, and dittoed DDT blocks. `spa_get_slop_space()` computes reserved slop space from total pool space, `spa_slop_shift`, `spa_min_slop`, `spa_max_slop`, and embedded log classes. `spa_update_dspace()` updates raw/usable device space while reserving non-allocating vdev space and adding special/dedup/BRT accounting.

`spa_preferred_class()` chooses a metaslab class for allocation. DDT objects may use the dedup class, then special class, then normal class. Metadata and configured user indirects prefer the special class. Small blocks can use the special class only while preserving `zfs_special_class_metadata_reserve_pct` of special-class capacity for metadata.

Other helpers expose metaslab classes, DDT/special/slog presence, deflated DVA sizes, block pointer data size, and dirty data totals.

## Import Progress And Status

The import-progress section maintains a global procfs list of active imports. Entries track pool GUID, pool name, load state, notes, MMP seconds remaining, and rewind max TXG. Routines initialize/destroy the procfs list, add/remove import entries, and update state, notes, MMP check countdown, and max TXG.

`spa_load_failed()` and `spa_load_note()` format debug messages for import/load paths, with `spa_load_note()` also updating import-progress notes.

`spa_state_to_name()` returns user-facing pool state strings such as `ONLINE`, `DEGRADED`, `SUSPENDED`, `FAULTED`, `UNAVAIL`, or `TRANSITIONING`. `spa_scan_stat_init()` and `spa_scan_get_stats()` collect persistent and pass-local scrub/error-scrub stats for status reporting.

## Miscellaneous Interfaces

The file includes GUID generation and lookup, load GUID generation, `snprintf_blkptr()`, `spa_freeze()`, `zfs_panic_recover()`, a limited lowercase-hex `zfs_strtonum()`, MOS feature activation/deactivation, allocation-class feature activation, object-set eviction wait lists, pool property accessors, checkpoint helpers, multihost/hostid accessors, max block/dnode size checks, missing top-vdev tracking, and async-destroy suspension when a checkpoint plus low space could suspend the pool.

The end of the file exports many SPA symbols and defines module parameters for debug flags, recovery behavior, free-leak-on-EIO behavior, deadman settings, asize inflation, DDT/special allocation policy, slop shift, and allocator count/CPU grouping.

## Risks And Invariants

This file is heavy on cross-subsystem lock ordering. Changes to config-lock acquisition order, namespace/refcount rules, or vdev enter/exit sequencing can create deadlocks or break administrative synchrony guarantees.

Space accounting helpers feed ENOSPC decisions and allocator class routing. Errors in slop-space, non-allocating-vdev reservation, or special-class reserve calculations can expose pools to out-of-space suspension or misplace metadata. Lifecycle functions must remain aligned with `spa_t` field ownership; missing teardown or reordered subsystem finalization can leak resources or leave callbacks/kstats/procfs entries dangling.
