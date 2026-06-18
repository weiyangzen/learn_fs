# sources/distributed-fs/lustre-release/lustre/mdt/mdt_restripe.c

## Purpose

`mdt_restripe.c` implements MDT-side directory restriping and auto-splitting. It owns the background `mdt_restriper_*` kernel thread, queue management for directories needing split/migrate/layout-update work, and helper preparation for invoking the normal reintegration paths internally. It converts manual or automatic layout changes into LMV state transitions, migrates directory entries between old and new stripes, and finalizes the master layout after all stripes clear migration state.

## Important APIs, Types, and Functions

- `mdt_auto_split_add()`, `mdt_restripe_migrate_add()`, and `mdt_restripe_update_add()` enqueue MDT objects on `mdr_auto_splitting`, `mdr_migrating`, and `mdr_updating` while setting `mot_restriping` and taking object references.
- `mdt_restripe_internal()` performs the split/merge layout transition for a directory under caller-held locks.
- `mdt_auto_split()` consumes auto-split work, resolves a stripe back to its master when needed, allocates a target FID, locks parent/child/stripes, prepares `md_op_spec`, and calls `mdt_restripe_internal()`.
- `mdt_restripe_migrate()` reads one directory page from a migrating stripe, selects the next real dirent after `mot_restripe_offset`, allocates a target FID, prepares a synthetic migrate reint record, and calls `mdt_reint_migrate()`.
- `mdt_restripe_migrate_finish()` clears `LMV_HASH_FLAG_MIGRATION` on a stripe and drops it from the migration queue.
- `mdt_restripe_layout_update()` checks all stripes of a master for migration completion and then calls `mdt_dir_layout_update()` to clear layout-change state or shrink.
- `mdt_restriper_start()` and `mdt_restriper_stop()` initialize/tear down the queue state, folio, LU environment/session, root-like ucred, and background task.

## Control Flow

Producers enqueue objects by setting `mot_restriping`, resetting offsets where needed, taking a ref, appending to a list under `mdr_lock`, and waking the restriper thread. The thread loops in idle state, prioritizing auto-split, then delayed layout update, then migration. Each item is removed or left queued depending on whether more work remains.

Manual split/merge runs through `mdt_restripe_internal()`. It fetches the child LMV, rejects changing layouts, rejects unchanged stripe count/hash, and distinguishes split from merge by comparing requested and existing stripe counts. Split may create a new master object for a plain directory and calls `mo_layout_change(MD_LAYOUT_SPLIT)`. Merge marks the LMV with `LMV_HASH_FLAG_MERGE | LMV_HASH_FLAG_MIGRATION`, records merge count/hash, bumps layout version, and stores the xattr.

Auto-split consumes a child or stripe object. If the queued object is a stripe, it resolves the master from PFID and avoids doing the split on a remote master. It calculates the next count from `mdr_dir_split_delta` capped by connected MDT count, fetches the parent name/FID, allocates a target FID, locks parent and child stripes, prepares a synthetic LMV user MD, and invokes the same internal restripe helper as manual restripe.

Migration consumes one dirent at a time from the current stripe page. It validates stripe LMV and stripe index, skips new split stripes and some CRUSH merge target stripes by finishing them immediately, reads `mo_readpage()` from `mot_restripe_offset`, skips empty and dot entries, copies the name into `mti_filename`, allocates a target FID from the master, prepares `mti_rr`/`mti_spec`, and calls `mdt_reint_migrate()`. On success it advances `mot_restripe_offset` to the next dirent hash or page end. End-of-directory finishes the stripe by clearing migration state.

Layout update waits until `mdr_update_time` has passed. It verifies every stripe no longer has restriping flags by fetching LMV directly and invalidating cache, then prepares a synthetic `REINT_SETXATTR` record and calls `mdt_dir_layout_update()`. If any stripe is still in progress it delays another five seconds; otherwise it clears `mot_restriping`, removes the master from the update list, and drops the ref.

## State and Persistence Behavior

Queue state lives in `struct mdt_dir_restriper`: three lists, one spinlock, an update timestamp, split thresholds, a folio used for `mo_readpage()`, reusable LMV buffers, and a thread LU environment/session. Per-object state is `mot_restriping`, `mot_restripe_linkage`, and `mot_restripe_offset`. Persistent layout state is in `trusted.lmv` xattrs: layout version, split/merge/migration flags, stripe FIDs, merge offset/hash, and cleared layout-change bits. Actual namespace movement is persisted by the regular `mdt_reint_migrate()` and MDD migration path.

## Dependencies and Integration Points

This file depends on Linux kthreads/folios, MDT object lifetime rules, LMV helpers, `mdt_reint_migrate()`, `mdt_dir_layout_update()`, `mdt_object_stripes_lock()`, MDD layout change and readpage methods, FID allocation through the child device, and capability/RBAC setup for an internal root-like thread. It is triggered by create/restripe paths in `mdt_reint.c` and finalizes through setxattr/layout code in `mdt_xattr.c`.

## Risks and Edge Cases

- Queue and `mot_restriping` invariants must match. Failing to clear the flag or delete linkage on every error can wedge future restripe attempts.
- `mdt_restripe_migrate()` reads one page and has a TODO to read one dirent; malformed or changing directory pages can return `-EBADF` and drop the queue item.
- The code parses stripe index from stripe name text after a rendered FID prefix, making name format changes risky.
- Internal synthetic requests have no ptlrpc request capsule in some paths, so called functions must tolerate `req == NULL` where expected.
- Auto-split is gated by connected MDT count; split attempts during no MDS-MDS connections fail and must be retried by higher-level triggers.
- Layout-update delay is time-based and may leave master objects queued while stripes are still migrating.

## Test Signals

Tests should cover enqueue idempotence, auto-split of plain and already-striped directories, remote-master skip, no-MDS-MDS connection behavior, split count capping, merge xattr flag/version updates, migration offset advancement across pages, skip of dot/dummy entries, end-of-directory finish, `-EBUSY` open-file handling, layout update while stripes are still in progress, layout update after all stripes finish, start/stop cleanup of non-empty queues, and fail injection through internal migrate/layout calls.
