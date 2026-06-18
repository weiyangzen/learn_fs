# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-common.c lines 1-8292

## Scope

This chunk covers the first 8,292 lines of GlusterFS DHT's `dht-common.c`. It includes the main distributed-hash lookup paths, directory layout discovery and self-heal orchestration, MDS xattr handling, linkto-file repair logic, get/set/remove xattr routing, statfs aggregation, opendir/readdir/readdirp/fsyncdir, mknod/symlink/unlink, parent-layout guarding for namespace creation, and the beginning of hard-link callback cleanup. The chunk stops inside `dht_link_cbk`; hard-link continuation, create/mkdir/rmdir/locking/notify helpers, and tail utility functions are outside this chunk.

## Purpose

The file implements the DHT translator's common filesystem operations. DHT maps each pathname to a hashed child subvolume for namespace placement while allowing file data to live on another cached subvolume through linkto stubs during migration, rebalance, and disk-space fallback. For directories, it presents a single merged namespace assembled from all child subvolumes and persists directory layout state as DHT xattrs.

The covered code is responsible for:

- resolving lookups through hashed subvolumes, cached subvolumes, linkto targets, or all children;
- discovering directory layouts and detecting layout/GFID/type inconsistencies;
- setting and healing directory MDS xattrs used as the source of custom/user xattr consistency;
- aggregating directory xattrs, quota xattrs, split-brain status, statfs data, and readdir results;
- routing file operations to the cached subvolume while tracking migration phase state;
- routing directory xattr mutations across all children or through the MDS refcount protocol;
- creating new namespace entries on hashed or alternate available subvolumes, with linkto creation when needed;
- protecting namespace creation from stale parent layouts.

## Important APIs, Types, and Functions

### Core state

- `dht_local_t` is the per-FOP state carrier. In this chunk it stores `loc`, `loc2`, `fd`, xattr request/result dictionaries, `layout`, `selfheal` state, `cached_subvol`, `hashed_subvol`, `mds_subvol`, call counters, parent stat buffers, rebalance metadata, linkto cleanup state, directory-read queue state, and lock wrappers.
- `dht_conf_t` is `this->private`. It provides the child subvolume array/status, DHT layout and MDS xattr key names, linkto xattr key, commit-hash state, defrag/rebalance context, lookup/search options, readdir optimization flags, decommissioned-brick state, and operation method hooks.
- `dht_layout_t` records directory hash ranges and child errors. It is created, merged, normalized, stored in inode context, compared to disk layout, and refreshed under parent-layout protection.
- Inode context stores cached layout, cached subvolume, MDS subvolume, migration information, and time metadata through helpers such as `dht_layout_set()`, `dht_layout_preset()`, `dht_inode_ctx_mdsvol_set()`, `dht_inode_ctx_mdsvol_get()`, and `dht_inode_ctx_time_update()`.

### Lookup and directory discovery

- `dht_lookup()` initializes `dht_local_t`, filters special subvolume-key locs, handles nameless GFID lookup through `dht_do_discover()`, requests root commit-hash when needed, computes the hashed subvolume, and dispatches to fresh lookup or revalidate.
- `dht_do_fresh_lookup()` requests file and directory xattrs, strips incoming FUSE `gfid-req`, then looks up the hashed child first or all children if the hash cannot be found.
- `dht_lookup_cbk()` handles the first hashed lookup. Directories are expanded into `dht_lookup_directory()`, normal files preset inode layout to the child, linkto files are followed through `dht_lookup_linkfile_cbk()`, and misses may trigger `dht_lookup_everywhere()`.
- `dht_lookup_directory()` and `dht_lookup_dir_cbk()` query all children for a directory, merge on-disk layouts and attrs, detect GFID/type mismatches, track attr/xattr/self-heal needs, remember the MDS subvolume, and either self-heal or unwind a merged directory lookup.
- `dht_do_discover()`, `dht_discover_cbk()`, and `dht_discover_complete()` implement nameless GFID discovery. They query all children because no name is available for hashing, merge the found layout/xattrs/stats, detect file-vs-directory conflicts, update volume commit hash, mark missing MDS xattr if possible, optionally spawn `dht_heal_full_path`, and unwind the original lookup frame.
- `dht_revalidate_cbk()` revalidates existing inode layouts. Directory revalidation fans out to all children; file revalidation follows the cached layout. It detects stale/mismatched layouts, ENOENT migration races, ENODATA GFID gaps, linkto redirects, attr divergence, MDS-xattr healing needs, and ESTALE propagation.

### Linkto and lookup-everywhere repair

- `dht_lookup_everywhere()` fans lookup to every child when the hashed path is inconclusive, GFID repair is needed, a linkto target fails, or migration may have moved the file.
- `dht_lookup_everywhere_cbk()` classifies each response as directory, real file, or linkto file. It tracks cached data file, hashed linkto file, open-fd counts, GFID mismatch, and stale-link cleanup candidates.
- `dht_lookup_everywhere_done()` encodes the migration race matrix for cached-vs-hashed states. It handles file/directory conflicts, GFID-missing directory repair, valid hashed linkto files, stale linkto unlink, false-linkto unlink, direct layout preset for migrated files, and namespace-protected linkto creation.
- `dht_fill_dict_to_avoid_unlink_of_migrating_file()` sets `DHT_SKIP_NON_LINKTO_UNLINK` and `DHT_SKIP_OPEN_FD_UNLINK` so lower layers only unlink safe linkto files.
- `dht_linkfile_create_lookup_cbk()`, `dht_call_lookup_linkfile_create()`, and `dht_lookup_linkfile_create_cbk()` protect namespace and create linkto files on the hashed subvolume pointing to cached data when a file is found off-hash.

### Directory MDS and xattr helpers

- `dht_common_mark_mdsxattr()` chooses the hashed subvolume as MDS for a directory with no internal MDS xattr, writes `conf->mds_xattr_key`, and stores the MDS in inode context. Fresh lookup uses a copied frame to avoid races with foreground revalidation.
- `dht_dir_xattr_heal()` starts a synctask to copy custom xattrs from MDS to non-MDS subvolumes when the MDS refcount xattr indicates missed propagation.
- `dht_dict_get_array()` and `dht_dict_set_array()` convert integer array xattrs between host and big-endian wire order.
- `dht_match_xattr()` uses `get_xattrs_to_heal()` to identify xattrs that must be read from or healed through the MDS path.

### Xattr read/write paths

- `dht_getxattr()` handles DHT virtual/debug xattrs, pathinfo/node-uuid aggregation, rebalance local-subvolume discovery, marker xattrs, linkinfo, real-filename fanout, MDS-routed custom xattrs on directories, and default aggregation over layout children.
- `dht_fgetxattr()` mirrors getxattr for file descriptors, routing directory custom xattrs through the MDS when possible.
- `dht_getxattr_cbk()` strips internal DHT/MDS/commit-hash xattrs from user-visible responses, removes internal quota/pgfid keys for normal clients, aggregates directory xattrs, and retries on remote-fd EBADF/EBADFD via `dht_check_and_open_fd_on_subvol()`.
- `dht_vgetxattr_dir_cbk()`, `dht_vgetxattr_cbk()`, and helpers build synthetic pathinfo/node-uuid strings, optionally appending DHT layout ranges.
- `dht_dir_common_set_remove_xattr()` is the central directory `(f)setxattr`/`(f)removexattr` dispatcher. Non-healed keys, root, or single-child volumes are sent to all children. User/custom keys are protected by subtracting one from the MDS refcount xattr, applying the operation to MDS and non-MDS children, then adding one back on MDS after non-MDS completion.
- `dht_setxattr()`, `dht_fsetxattr()`, `dht_removexattr()`, and `dht_fremovexattr()` initialize local state, reject native/internal DHT xattrs from normal clients, split file vs directory behavior, and request `DHT_IATT_IN_XDATA_KEY` for migration-phase checks on files.
- `dht_file_setxattr_cbk()` and `dht_file_removexattr_cbk()` inspect returned `DHT_IATT_IN_XDATA_KEY` iatts. During migration phase 1 or 2 they re-target through `dht_rebalance_in_progress_check()` or `dht_rebalance_complete_check()` and then retry via `dht_setxattr2()` / `dht_removexattr2()`.
- Special setxattr keys in this chunk include `GF_XATTR_FILE_MIGRATE_KEY`, `decommission-brick`, `GF_XATTR_FIX_LAYOUT_KEY`, `new-commit-hash`, `distribute.directory-spread-count`, and `glusterfs.dht.nuke`.

### Statfs and directory iteration

- `dht_statfs()` fans out to all children, substituting root loc for non-directory input.
- `dht_statfs_cbk()` normalizes block sizes/frsizes, sums capacity/inode counts, handles quota-deem-statfs selection, supports simple-quota aggregation, and compensates for failed children.
- `dht_opendir()` opens the fd on every child and injects linkto xattr requests. With `readdir_optimize`, non-first-up children are told to skip directories for readdir-ahead compatibility.
- `dht_readdir()` chooses `READDIRP` if any child is down or `conf->use_readdirp` is set; `dht_readdirp()` always uses readdirp.
- `dht_do_readdir()`, `dht_queue_readdir()`, and `dht_queue_readdirp()` serialize potentially recursive directory-read winds with an atomic queue counter to avoid stack blowups when callbacks synchronously request another read.
- `dht_readdir_cbk()` filters plain entries by layout owner for files and by first-up child when optimized directory reads are enabled.
- `dht_readdirp_cbk()` additionally strips linkto files, fixes directory stat size/block values, presets inode layout for file entries, updates directory inode times, may populate single-child directory layouts, and advances across child subvolumes until useful entries are returned or all children are exhausted.
- `dht_fsyncdir()` sends fsyncdir to every child and unwinds after all responses.

### Namespace creation and unlink

- `dht_mknod()` hashes the new loc, handles decommissioned-brick layouts by refreshing the parent under an inodelk, and otherwise calls `dht_mknod_wind_to_avail_subvol()`.
- `dht_mknod_wind_to_avail_subvol()` creates directly on the hashed child unless it is filled. If another child has space, it creates a linkto file on the hashed child and then creates the actual object on the available cached child.
- `dht_newfile_cbk()` updates parent inode times, presets layout on the new inode, optionally heals linkfile attributes, fixes parent dir stat fields, and completes pending parent-layout unlock flow for guarded mknod.
- `dht_guard_parent_layout_and_namespace()` prepares `GF_PREOP_PARENT_KEY` and parent disk layout xdata for namespace creation, verifies the current hashed subvolume against the in-memory parent layout, and calls `dht_protect_namespace()`. `dht_handle_parent_layout_change()` refreshes the parent layout before resuming a saved FOP stub.
- `dht_symlink()` creates directly on the hashed child and reuses `dht_newfile_cbk()`.
- `dht_unlink()` sends unlink to the cached data subvolume. `dht_unlink_cbk()` then removes the hashed linkto file when hashed and cached differ.
- `dht_remove_stale_linkto()` is a syncop helper used by the beginning of `dht_link_cbk()` to clean up a linkto created before a failed hard-link operation. The chunk ends before `dht_link_cbk()` completes.

## Control Flow

Lookup starts in `dht_lookup()`. Named fresh lookups compute the hashed child and probe it first. A directory response expands into all-child directory lookup so DHT can merge layout xattrs and directory attrs. A regular file response presets a one-child layout on the inode. A linkto response follows the linkto target, and target failure falls back to all-child lookup to handle migration races.

Revalidate starts from an existing inode context. If the layout generation is stale, it discards the layout and restarts fresh lookup. Directory revalidate queries all children, compares on-disk layouts, and may self-heal. File revalidate queries the cached layout child or follows linkto state. ENOENT on a regular file triggers lookup-everywhere because a rebalance may have migrated it.

Lookup-everywhere is the repair path. Each child response is classified under frame lock, then the final callback resolves one of several states: no cached data, data on hashed, stale hashed linkto, false linkto pointing elsewhere, directory discovered, GFID missing, or off-hash data requiring a linkto. Some outcomes perform unlink or linkfile creation before unwinding.

Directory xattr mutation uses a two-stage refcount protocol for user/custom xattrs. DHT decrements an integer array on the MDS, mutates MDS, fans out to non-MDS children, then increments the MDS value after the fanout. A nonzero MDS value later marks that non-MDS xattr healing is needed.

Directory reads begin on the subvolume encoded in the transformed offset. Callbacks filter entries not owned by that child's layout range, skip linkto files, and move to the same or next child when no entries survive filtering. The queue helpers prevent deep recursive winding when lower layers respond synchronously.

Creation flows prefer the hashed child. If the hashed child is full, DHT creates a linkto file on the hashed child and the real object on an available child. If the hashed child is decommissioned, DHT locks/refreshes the parent layout before choosing the target.

## State and Persistence Behavior

Persistent DHT state is stored mainly in trusted xattrs on brick directories and linkto files:

- directory layout xattr `conf->xattr_name`, containing hash ranges and commit hash;
- directory MDS xattr `conf->mds_xattr_key`, used to identify the MDS child and track missed xattr propagation;
- linkto xattr `conf->link_xattr_name`, identifying the cached subvolume for an off-hash file;
- commit-hash xattr `conf->commithash_xattr_name` on the root;
- migration phase bits in `struct iatt`, stripped before returning stats to callers;
- preop parent-layout xdata for namespace operations.

Runtime state is stored in inode context and `dht_local_t`. Inode context caches layouts, MDS subvolume, cached file subvolume, migration information, and time metadata. `dht_local_t` state exists only for the in-flight FOP but carries references to dicts, inodes, fds, locks, copied frames, and synctask state; callbacks must unwind or destroy frames carefully.

Directory stats returned to upper layers are normalized with fixed size/block values by `dht_set_fixed_dir_stat()` because individual child directory sizes are not meaningful for the merged DHT namespace.

## Dependencies and Integration Points

This chunk depends on Gluster's translator/FOP framework: `STACK_WIND`, `DHT_STACK_UNWIND`, call frames, cookies, dicts, inode/fd/loc helpers, gf logging, GFID utilities, syncops, and synctasks. It integrates with lower child xlators through their `lookup`, `setxattr`, `xattrop`, `getxattr`, `unlink`, `mknod`, `symlink`, `statfs`, `opendir`, `readdir`, `readdirp`, and `fsyncdir` fops.

Important local DHT integrations include layout management (`dht-layout` helpers), self-heal (`dht_selfheal_directory`, `dht_heal_full_path`, `dht_dir_heal_xattrs`), namespace locking (`dht_protect_namespace`, `dht_blocking_inodelk`, `dht_unlock_inodelk`), rebalance/migration helpers (`dht_start_rebalance_task`, `dht_rebalance_*_check`, `methods->migration_get_dst_subvol`), subvolume selection (`dht_subvol_get_hashed`, `dht_subvol_get_cached`, `dht_free_disk_available_subvol`), and marker/quota/upcall support through included Gluster utilities.

External behavior is visible to FUSE/NFS/SMB clients through normal file operations and virtual xattrs such as pathinfo, node-uuid, linkinfo, subvol status, and debug hashed-subvol queries.

## Risks and Edge Cases

- The lookup code intentionally tolerates many rebalance races, but the state matrix around hashed linkto, cached data, open fd counts, and GFID mismatches is fragile. Incorrect stale-link unlink decisions can cause data loss; the skip-unlink xdata keys are central safety guards.
- Directory MDS xattr consistency is availability-biased in some reads: if MDS cannot be determined or is down, code may fetch xattrs from a random subvolume. That can return stale custom xattrs until heal completes.
- MDS refcount handling depends on all branches unwinding correctly after decrementing and incrementing the MDS xattr. Failures in dict creation, xattrop, non-MDS fanout, or frame lifetime can leave a nonzero marker that requires future healing.
- Many callbacks aggregate state under `frame->lock` but perform follow-up winds after unlock. Races with synchronous callbacks, especially in readdir and lookup-everywhere cleanup, require strict call-count handling.
- `dht_getxattr()` rejects direct MDS xattr access by comparing `strncmp(key, conf->mds_xattr_key, strlen(key))`; short prefixes could behave unexpectedly if callers request partial internal key names.
- `dht_symlink()` unwinds with `link` on the error path in the covered code, even though the FOP is symlink. This should be checked in the wider file and tests because it looks suspicious in isolation.
- `dht_readdir_cbk()` sets `skip_hashed_check` only for single-child volumes and returns original entries in that path; linkto filtering is not done for plain readdir in the same way as readdirp.
- Parent-layout guarding assumes the in-memory parent layout is valid enough to extract the disk layout for the hashed subvolume. If the inode context is already stale, the guard falls back to refresh paths but creation can still race with remove-brick/fix-layout work.
- The chunk ends mid-`dht_link_cbk`, so hard-link migration retries, layout preset, and final unwind behavior must be reconciled with the next chunk before making file-level conclusions.

## Test Signals

Useful validation for this chunk should include:

- Fresh lookup of normal files, directories, linkto files, missing hashed entries, nameless GFID lookup, and root lookup with commit-hash xattr.
- Revalidate of regular files and directories with stale layout generation, layout mismatch, ENOENT during migration, ENODATA GFID gaps, ESTALE, and child-down cases.
- Lookup-everywhere race matrix coverage for cached/hashed states: no file, linkto, non-linkto, open linkto fd count, false linkto target, GFID mismatch, and safe stale-link deletion.
- Directory self-heal triggers for missing layout, layout holes/overlaps, missing MDS xattr, nonzero MDS xattr, attr divergence, and file-vs-directory conflicts.
- Getxattr/fgetxattr for pathinfo, node-uuid list, linkinfo, real-filename, subvol status, marker keys, MDS-routed custom xattrs, user xattr aggregation, internal xattr filtering, and remote-fd EBADF retry.
- Setxattr/fsetxattr/removexattr/fremovexattr for directories with and without user/custom keys, single-child volumes, root directory bypass, MDS down, and MDS refcount failure recovery.
- File xattr mutation during migration phase 1 and phase 2, including retry to the new subvolume and `we_are_not_migrating()` behavior.
- Special setxattr operations: file migrate, forced migrate, decommission-brick discovery, fix-layout, new commit hash update, directory spread count, and `glusterfs.dht.nuke`.
- Statfs aggregation with mixed block sizes, child failures, quota-deem-statfs, and simple-quota xdata.
- Opendir/readdir/readdirp over multi-child directories, single-child directories with stale linkto files, child-down readdirp fallback, readdir optimization, offset continuation across children, and synchronous callback queue behavior.
- Mknod/symlink/unlink paths for direct hashed creation, filled hashed subvolume with linkto creation, decommissioned hashed subvolume parent refresh, parent-layout lock failure, and hashed linkto cleanup after unlink.
