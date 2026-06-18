# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-rename.c

## Purpose
Implements DHT rename for distributed GlusterFS volumes. It handles directory rename fan-out across all bricks, regular-file rename across hashed/cached subvolumes, linkto-file creation/removal, changelog rename tracking, quota-accounting suppression, and namespace/inode locking needed to make rename race-tolerant during lookup self-heal and rebalance.

## Important APIs and Functions
- `dht_rename`: public FOP entry. Resolves source/destination hashed and cached subvolumes, initializes `dht_local_t`, logs the operation, and dispatches to directory or file logic.
- `dht_rename_dir`, `dht_rename_dir_do`, `dht_rename_dir_cbk`: protect source/destination namespaces, verify destination emptiness when needed, perform the hashed-subvolume rename, fan out to remaining subvolumes, and reverse successful subvolume renames when a later subvolume fails.
- `dht_rename_lock`, `dht_rename_lock_cbk`, `dht_rename_file_protect_namespace`: acquire backward-compatible migration inodelks plus ordered namespace locks, then re-lookup source and destination before mutating.
- `dht_rename_create_links`, `dht_do_rename`, `dht_rename_unlink`, `dht_rename_cleanup`: create linkto/hardlink prerequisites, perform the actual backend rename, remove old data/linkto files, or roll back partial link creation.
- `dht_pt_rename`: pass-through rename for single-subvolume/pass-through mode while still marking changelog rename metadata for non-directories.

## Control Flow
The entry path first validates locations and derives `src_hashed`, `src_cached`, `dst_hashed`, and optionally `dst_cached`. Directory renames are all-brick namespace operations: DHT checks every subvolume is up, orders locks by hashed subvolume name and parent/name identity, optionally reads the destination directory to enforce non-empty semantics, renames on `dst_hashed`, and then renames on every other subvolume. Failure after partial success triggers reverse renames on subvolumes that already succeeded.

Regular-file rename is a linkfile-aware state machine. It takes inodelks on the source cached file and possibly destination cached file, then entry/namespace locks. After locks, it revalidates source and destination because rebalance or another rename may have changed cached placement or GFID. If source became a linkfile or GFID changed, the operation fails with an ENOENT-style path. Otherwise DHT creates a destination linkto file and/or hardlink when the cached and hashed subvolumes differ, performs the backend rename on either `src_cached` or `dst_hashed`, and cleans obsolete source data, source linkto, and overwritten destination data.

## State and Persistence
Persistent effects are backend `rename`, `link`, `unlink`, and linkto xattr operations on child xlators. The file adds request xdata such as `GLUSTERFS_MARKER_DONT_ACCOUNT_KEY`, `GF_FORCE_REPLACE_KEY`, `GLUSTERFS_INTERNAL_FOP_KEY`, and `DHT_CHANGELOG_RENAME_OP_KEY`. Runtime state lives in `dht_local_t`: cached/hashed subvol pointers, lock wrappers, `ret_cache`, `linked`, `added_link`, merged iatts, xattr request/response dictionaries, and copied destination loc.

## Dependencies and Integration Points
Depends on DHT common layout/cache helpers, `dht-lock` namespace/inodelk wrappers, linkfile creation/heal helpers, dict/xdata APIs, inode/link loc handling, and child xlator FOP vectors. It integrates with lookup self-heal, rebalance migration locks (`DHT_FILE_MIGRATE_DOMAIN`), changelog marker handling, quota/marker accounting, and the main DHT `fops.rename` registration in `dht.c`.

## Risks
- Rename correctness depends on lock ordering and complete unlock cleanup; failure to wind unlocks logs stale-lock warnings and then unwinds anyway.
- Directory fan-out rollback is best effort; reverse rename can also fail and leave divergent directories.
- Linkfile failures are intentionally sometimes non-critical, so stale linkto files may remain until lookup/rebalance heals them.
- `DHT_MARKER_DONT_ACCOUNT` can allocate a dict through a macro argument and changes ownership expectations; callers must unref carefully.
- Destination cached changes are handled by re-lookup, but races with concurrent rename/unlink still depend on downstream errno behavior.

## Test Signals
No direct unit test appears in this subset. Indirect signals come from DHT rename, rebalance, linkto, quota/changelog, and directory self-heal regressions. High-value tests would cover cross-subvolume rename with existing destination, directory partial failure rollback, source migration between lock and lookup, stale linkto replacement via `GF_FORCE_REPLACE_KEY`, and pass-through changelog tracking.
