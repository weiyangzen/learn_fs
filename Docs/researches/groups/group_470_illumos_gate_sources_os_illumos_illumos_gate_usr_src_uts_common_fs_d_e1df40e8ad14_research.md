# Group Research: group_470_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_d_e1df40e8ad14

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vnops.c

This file implements the base vnode operations for the illumos `/dev` filesystem (`sdev`). It is the main behavioral layer for synthetic `/dev` nodes, persistent backing-store nodes, non-global-zone device profiles, and dynamic-directory dispatch.

Core responsibilities:
- Defines `sdev_vnodeops_tbl`, the primary VOP table for `/dev`.
- Handles VDIR, VCHR, VBLK, VLNK, VREG, and VDOOR-style `/dev` entries, with regular-file operations delegated to the backing vnode.
- Maintains the `sdev_node_t` lifecycle rules described in the large file header: `SDEV_INIT`, `SDEV_READY`, and `SDEV_ZOMBIE`.
- Coordinates in-memory `sdev_node_t` entries with optional persistent backing-store vnodes in `sdev_attrvp`.
- Routes non-global-zone operations through profile helpers such as `prof_lookup()` and `prof_filldir()`.
- Routes global-zone lookup and directory enumeration through `devname_lookup_func()` and `devname_readdir_func()`.

Important operations:
- `sdev_open`, `sdev_close`, `sdev_read`, `sdev_write`, and `sdev_ioctl` only support global-zone regular files, delegating to `sdev_attrvp`. Directories are special-cased, and links or unsupported types fail.
- `sdev_getattr` reads attributes from the persistent backing vnode if present, otherwise from the in-memory `sdev_attr`, then merges sdev-specific fields.
- `sdev_setattr` delegates to `devname_setattr_func()`.
- `sdev_getsecattr` and `sdev_setsecattr` support ACL/security attributes, fabricating ACLs for memory-only nodes when possible and creating a shadow node when persistence is required.
- `sdev_access` uses `sdev_self_access`; memory-only access is checked by `sdev_unlocked_access`, while persisted nodes defer to the backing vnode.
- `sdev_lookup` checks execute permission and dispatches either to the zone profile lookup path or global `devname_lookup_func`.
- `sdev_create`, `sdev_mkdir`, and `sdev_symlink` create new in-memory nodes, optionally backed by persistent storage, then unblock waiters on `SDEV_LOOKUP`.
- `sdev_remove`, `sdev_rmdir`, and `sdev_rename` remove nodes from the in-memory cache and perform best-effort cleanup of backing-store entries.
- `sdev_readdir` expects the caller to hold the node contents lock through `sdev_rwlock`; it fills profile directories for non-global zones and otherwise delegates to `devname_readdir_func`.
- `sdev_inactive` delegates final cleanup to `devname_inactive_func`.
- `sdev_fid` exposes `sdev_ino` through an NFS-style fid.
- `sdev_pathconf` reports the ACL flavor via `_PC_ACL_ENABLED`.

Locking and lifecycle model:
- Directory contents are protected by each node’s `sdev_contents` rwlock.
- The file header documents the core ordering: parent before child; vnode `v_lock` before `sdev_contents` when both are needed.
- Removal is two-phase: unlink from the directory cache and mark zombie without changing vnode references; final destruction is left to inactive handling.
- Several operations check parent zombie state by locking the parent’s parent before proceeding.

Research notes:
- This is the authoritative behavioral contract for `/dev` persistence and dynamic-node semantics.
- Dynamic-node directories are expected to override selected VOPs while sharing this common base table.
- Non-global-zone `/dev` is intentionally constrained; create/remove-like operations mostly redirect to profile lookup or return `ENOTSUP`.
- Backing-store operations are best effort in removal/rename paths, with some errors intentionally suppressed to preserve `/dev` semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vtops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vtops.c

This file implements dynamic vnode operations for the `/dev/vt` directory. It builds and validates virtual terminal device nodes and special symlinks.

Core responsibilities:
- Defines `devvt_vnodeops_tbl`, overriding lookup, readdir, create, and disallowing mutation operations for `/dev/vt`.
- Exposes `devvt_getvnodeops()` for installing these operations on the dynamic directory.
- Creates numeric VT character-device entries with default mode `0600`.
- Creates `active` and `console_user` symlink entries.
- Validates cached `/dev/vt` entries against the current VT subsystem state.

Important operations:
- `devvt_str2minor` parses numeric entry names into VT minor numbers.
- `devvt_validate` classifies cached entries as valid, invalid, stale, or skipped. It checks `vt_wc_attached()`, `vt_minor_valid()`, and compares symlink targets for `active` and `console_user`.
- `devvt_create_rvp` is the lookup callback used by `devname_lookup_func`; it returns either a device vattr or a symlink target buffer.
- `devvt_lookup` chooses `SDEV_VLINK` for special symlink names and `SDEV_VATTR` for numeric devices, then verifies the returned vnode type.
- `devvt_create_snode` creates missing cached entries during directory refresh.
- `devvt_rebuild_stale_link` updates stale symlink targets in-place while holding the directory write lock.
- `devvt_prunedir` removes invalid cached entries and refreshes stale links.
- `devvt_cleandir` refreshes the whole directory on first read: prune, add valid numeric terminal nodes, and ensure `active` and `console_user` links exist.
- `devvt_readdir` triggers `devvt_cleandir` when reading from offset zero, then delegates to `devname_readdir_func`.
- `devvt_create` implements read-only create semantics: opening existing entries can succeed, but new creation returns `EROFS`, exclusive create returns `EEXIST`, and writable directory create returns `EISDIR`.

Mutation policy:
- Remove, mkdir, rmdir, symlink, and setsecattr are all `fs_nosys`.
- This directory is dynamically generated from VT state, not user-modifiable.

Research notes:
- `/dev/vt` is a compact example of sdev dynamic-directory design: validator, lookup callback, prune/rebuild, and read-only create semantics.
- `devvt_create_snode` creates symlink nodes for both special link names, but its `SDEV_VLINK` path obtains the active VT target. Validation/rebuild later distinguishes `console_user`; this is worth checking if investigating `/dev/vt/console_user` freshness or initial target behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vtops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_zvolops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_zvolops.c

This file implements dynamic vnode operations for `/dev/zvol`, including `/dev/zvol/dsk` and `/dev/zvol/rdsk`. It bridges sdev with ZFS zvol discovery, zvol minor creation, global-zone symlink generation, and non-global-zone direct device-node creation.

Core responsibilities:
- Defines `devzvol_vnodeops_tbl`, overriding lookup, readdir, create, and rejecting namespace mutations.
- Dynamically opens `fs/zfs` and `/dev/zfs` instead of statically linking sdev to ZFS.
- Resolves `zvol_create_minor` and `zvol_name2minor` using `ddi_modsym`.
- Uses ZFS ioctls to test datasets, list pools/datasets/snapshots, and cache pool configuration data.
- Builds `/dev/zvol` hierarchy entries from ZFS object-set state.
- Handles the global-zone and non-global-zone zvol namespace differences.

Important operations:
- `sdev_zvol_create_minor` and `sdev_zvol_name2minor` wrap dynamically resolved ZFS symbols.
- `devzvol_open_zfs` opens `/dev/zfs`, modopens `fs/zfs`, resolves required zvol symbols, and records the zfs device major.
- `devzvol_close_zfs` releases the LDI handle, ident, module handle, and function pointers.
- `devzvol_handle_ioctl` serializes most ZFS ioctls through `devzvol_mtx`, grows nvlist destination buffers on `ENOMEM`, and lazily opens ZFS.
- `devzvol_objset_check` uses `ZFS_IOC_POOL_STATS` or `ZFS_IOC_OBJSET_STATS` and returns the object-set type. Snapshot visibility is controlled by `devzvol_snaps_allowed`.
- `devzvol_make_dsname` maps `/dev/zvol/{dsk,rdsk}/...` paths plus optional names to ZFS dataset names.
- `devzvol_validate` checks whether cached sdev nodes are still valid. It detects deleted datasets, stale type transitions, stale zvol-minor symlinks, and special non-global-zone profile pass-through cases.
- `devzvol_update_zclist` and `devzvol_update_zclist_cb` maintain a cached pool-config nvlist via taskq so pool listing runs in a safe global context.
- `devzvol_create_pool_dirs` creates pool directories under `/dev/zvol/dsk` and `/dev/zvol/rdsk`.
- `devzvol_create_dir` creates directory vattrs for pools or datasets.
- `devzvol_create_link` creates global-zone zvol symlinks pointing into `ZVOL_PSEUDO_DEV`, with raw-device suffix handling for `rdsk`.
- `devzvol_prunedir` validates and removes obsolete cached entries before directory enumeration.
- `devzvol_mk_ngz_node` creates non-global-zone zvol nodes directly as VBLK/VCHR devices because zones do not have a usable `/devices` target for global-style symlinks.
- `devzvol_lookup` enforces the global-zone versus non-global-zone lookup split. It prevents global-zone traversal into a zone’s `/dev/zvol`, avoids creating nonsensical profile shadows from NGZ context, and creates either directories or links based on object-set type.
- `sdev_iter_datasets` and `sdev_iter_snapshots` populate cached children through ZFS list ioctls.
- `devzvol_readdir` creates `dsk`/`rdsk`, pool directories, dataset directories, and optional snapshot entries as needed.

Mutation policy:
- `devzvol_create` only opens existing entries; absent names map to `EROFS`.
- Rename, mkdir, rmdir, remove, and symlink are `fs_nosys`.

Security and namespace notes:
- Global-zone zvol entries are symlinks to pseudo-device nodes.
- Non-global-zone zvol entries may be direct block/character device nodes when datasets are delegated or explicitly profile-matched.
- The code explicitly blocks global-zone lookup into a non-global-zone `/dev/zvol` to avoid materializing all zone zvol devices and crossing delegation boundaries.

Research notes:
- This is the key file for zvol `/dev` materialization and stale zvol cleanup.
- The ZFS coupling is intentionally late-bound through `ddi_modopen`, LDI, and ioctl calls.
- Important concurrency state is protected by `devzvol_mtx`, especially ZFS open state and cached pool configuration state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_zvolops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_subr.c

This file contains the main support routines for illumos `devfs`, the filesystem mounted at `/devices`. It manages `dv_node` allocation, device-tree-backed lookup, shadow permission storage, directory population, cleanup, stale-node handling, and tree walking.

Core responsibilities:
- Creates and destroys the `dv_node_cache`.
- Builds root, directory, and leaf device nodes.
- Maintains per-directory AVL trees of child `dv_node` entries.
- Derives stable inode numbers from devinfo nodes and device numbers.
- Creates and finds shadow attribute nodes in the underlying filesystem.
- Drives top-down device-tree configuration during lookup and readdir.
- Cleans cached devfs nodes during device removal or DR operations.
- Supports permission reset and stale shadow cleanup after driver removal.

Important operations:
- `dv_node_cache_init` and `dv_node_cache_fini` create/destroy the cache and `devfs_clean_key` TSD key.
- `dv_mkino` derives 32-bit-compatible inode numbers for directories and leaf nodes, including VCHR/VBLK differentiation.
- `dv_mkroot` constructs the root `dv_node`, sets VROOT, initializes `dv_entries`, and records `ddi_root_node()`.
- `dv_mkdir` creates directory nodes for attached devinfo nodes and holds the devinfo node.
- `dv_mknod` creates VCHR/VBLK leaf nodes from `ddi_minor_data`, records internal/no-fs-permission/default-mode flags, and holds private policy data where present.
- `dv_destroy` frees unreferenced nodes, releases shadow vnodes, attributes, names, devinfo holds, and private policy data. Referenced stale directories are left for `devfs_inactive`.
- `dv_findbyname`, `dv_insert`, and `dv_unlink` manage the directory AVL tree and link counts.
- `dv_vattr_merge` overwrites nodeid/link/fsid/rdev/type details so backing-store attributes look like devfs attributes.
- `devfs_get_defattr` computes default permissions from directory defaults, `DM_NO_FSPERM`, `minor_perm`, or private minor defaults.
- `dv_shadow_node` finds or creates the backing attribute vnode for a devfs node, handles read-only fallback to memory attributes, and tracks non-trivial ACLs.
- `dv_find_leafnode` locates a named minor under an attached devinfo node.
- `dv_clone_mknod` manufactures clone-device nodes for STREAMS drivers.
- `dv_find` is the central lookup engine: handles `.`, `..`, cached children, shadow-node construction, device-tree configuration through `ndi_devi_config_one`, alias handling, hidden-node filtering, clone/minor node creation, duplicate-race handling, internal-node filtering, and specfs vnode substitution for VCHR/VBLK leaves.
- `dv_filldir` populates a directory by configuring children, iterating attached child devinfo nodes and their minor data, and creating both leaf minor nodes and child directories.
- `dv_cleandir` recursively removes cached children, marks directories stale under force-clean rules, and sets `DV_BUILD` so future reads rebuild.
- `dv_reset_perm_dir` and `devfs_reset_perm` walk cached nodes and update memory permissions to match `minor_perm` defaults when no explicit shadow override exists.
- `devfs_remdrv_cleanup` and `devfs_remdrv_rmdir` remove stale shadow-permission files for removed drivers.
- `dv_walk` walks cached `dv_node` subtrees and invokes a callback.

Locking and cleanup model:
- Per-node contents are protected by `dv_contents`.
- `devfs_clean_key` marks cleanup paths that must avoid blocking in places that could deadlock against device-tree configuration.
- `dv_find` uses `dv_busy` while dropping locks for device-tree operations so forced cleanup can identify active construction.
- `dv_cleandir` returns `EBUSY` internally for lock or reference conflicts, but higher-level `devfs_clean` treats cleanup as best effort.

Research notes:
- `dv_find` is the highest-value function for understanding `/devices` lookup side effects.
- `dv_shadow_node` is the key bridge between synthetic devfs nodes and persistent filesystem permissions.
- `dv_cleandir` is central to hotplug, detach, and dynamic reconfiguration behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_vfsops.c

This file implements VFS-level operations and module linkage for the illumos `/devices` filesystem (`devfs`). It initializes the filesystem type, creates the single devfs mount instance, exposes root/stat operations, and provides external cleanup and lookup helpers.

Core responsibilities:
- Defines module linkage for the `"devices filesystem"`.
- Registers devfs VFS operations and devfs vnode operations.
- Creates the fictitious devfs device number.
- Mounts devfs over the existing `/devices` vnode used as the attribute backing root.
- Keeps a global single mount instance in `devfs_mntinfo`.
- Exposes cleanup, lookup, walk, and device-policy helper APIs.

Important operations:
- `_init` initializes `devfs_lock`, creates the `dv_node` cache, and installs the filesystem module.
- `_fini` always returns `EBUSY`, reflecting that devfs is not unloaded in normal operation.
- `devfsinit` registers VFS ops, creates `dv_vnodeops`, and assigns `devfsdev`.
- `devfs_mount` enforces mount privilege and directory mountpoint type, creates the root `dv_node`, records the mountpoint as the root shadow attribute vnode, initializes `vfs_data`, fsid, block size, and timestamps.
- `devfs_unmount` always returns `EBUSY`.
- `devfs_root` returns a held root vnode.
- `devfs_statvfs` reports synthetic filesystem stats, using `kmem_cache_stat` for file count and zero block availability.
- `devfs_mountroot` rejects root mounting with `EINVAL`.
- `devfs_dip_to_dvnode` maps a `dev_info_t` to a cached devfs directory node using `ddi_pathname` and `devfs_lookupname`.
- `devfs_clean_vhci` cleans vHCI branches under `DV_CLEAN_FORCE`.
- `devfs_clean` performs best-effort cache cleanup for a devinfo subtree, sets `devfs_clean_key` to avoid configuration deadlocks, and optionally cleans vHCI branches relevant to DR.
- `devfs_lookupname` resolves a path relative to `/devices` with `kcred` and controlled root/directory arguments rather than using process credentials.
- `devfs_walk` resolves a `/devices`-relative path and walks cached `dv_node` entries via `dv_walk`.
- `devfs_devpolicy` extracts held device policy data from a devfs real vnode behind a specfs vnode.

Design notes:
- devfs is intended to be mounted by the kernel during boot, not by arbitrary userland.
- The mountpoint itself becomes the root attribute backing vnode.
- Cleanup is deliberately best effort and returns success even if some cached nodes remain busy, because device contracts or later releases may resolve references during offline processing.

Research notes:
- This file gives the public entry points used by device removal, driver unload cleanup, policy lookup, and path-based devfs introspection.
- The single-mount assumption is explicit through `ASSERT(devfs_mntinfo == NULL)` in `devfs_mount`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_vnops.c

This file implements vnode operations for devfs. Directories are handled by devfs itself, while leaf VCHR/VBLK devices are normally substituted with specfs vnodes by `dv_find`; devfs then mainly sees forwarded operations for special-file metadata.

Core responsibilities:
- Defines `dv_vnodeops_template`, the vnode operation table used by devfs.
- Implements directory open/close/read/write/ioctl behavior.
- Implements attribute, permission, ACL, lookup, create, readdir, inactive, fid, locking, seek, and pathconf operations.
- Manages the distinction between memory attributes and persistent shadow attributes.
- Restricts real-console device permissions/access.

Important operations:
- `devfs_open` and `devfs_close` are directory-only; close clears locks and shares.
- `devfs_read`, `devfs_write`, and `devfs_ioctl` reject directory data I/O.
- `devfs_getattr` reads from `dv_attr` if present or from `dv_attrvp` otherwise, then merges devfs identity fields. It also forces the real console device to root-owned `0600`-style access.
- `devfs_setattr_dir` updates directory attributes either in memory or in the backing attribute store, with read-only fallback to memory attributes.
- `devfs_setattr` handles VDIR/VCHR/VBLK attribute changes, rejects unsupported `AT_NOSET`, ignores non-persistent fields, honors `DV_NO_FSPERM`, compares requested leaf permissions against default `minor_perm` or private defaults, removes shadow nodes when attributes return to defaults, and creates shadow nodes when non-default permissions need persistence.
- `devfs_pathconf` forwards `_PC_ACL_ENABLED` to the root attribute vnode.
- `devfs_getsecattr` fabricates ACLs if no attribute vnode exists; otherwise it forwards to the backing attribute vnode.
- `devfs_setsecattr` creates a backing attribute vnode if needed, forwards ACL changes under the backing vnode RW lock, and records `DV_ACL` for non-trivial ACLs.
- `devfs_unlocked_access` supports secpolicy checks while `dv_contents` is already held.
- `devfs_access` restricts console access via `secpolicy_console`, then checks either memory attributes or backing vnode access.
- `devfs_lookup` delegates to `dv_find`.
- `devfs_create` supports open-existing semantics only: absent entries become `EROFS`, exclusive create becomes `EEXIST`, writable directory create becomes `EISDIR`.
- `devfs_readdir` rebuilds directory contents when `DV_BUILD` is set, emits `.`, `..`, and cached children, skips hidden nodes and internal nodes for non-kernel credentials, updates access time, and tracks directory offsets.
- `devfs_fsync` is a no-op.
- `devfs_inactive` leaves normal unreferenced nodes cached, but immediately destroys stale unlinked nodes when the vnode count reaches zero.
- `devfs_fid` exposes `dv_ino`.
- `devfs_rwlock` and `devfs_rwunlock` bracket read/write/readdir and locking operations with `dv_contents`.
- `devfs_seek` rejects negative offsets.

Research notes:
- Attribute persistence logic is the main complexity in this file.
- `devfs_readdir` is side-effecting: it may configure devices by calling `dv_filldir`.
- The file documents the devfs/shadow namespace mapping for directories, minor nodes, and driver attributes, which is useful context for `/devices` path interpretation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dnlc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dnlc.c

This file implements the illumos Directory Name Lookup Cache (DNLC) and a separate directory-entry cache. It caches name-to-vnode lookups, negative lookups, and directory entry/free-space metadata for filesystems that use the directory cache API.

Core responsibilities:
- Maintains the global DNLC hash table of `ncache_t` entries.
- Tracks vnode references held by DNLC separately through `v_count_dnlc`.
- Supports negative-cache hits through `negative_cache_vnode` / `DNLC_NO_VNODE`.
- Provides purge APIs by vnode, VFS, filesystem vnodeops, and whole-cache.
- Shrinks the cache asynchronously under pressure through `system_taskq`.
- Provides a second directory cache for name-to-handle and free-space-handle metadata.
- Exposes kstats through legacy `ncstats` and named `dnlcstats`.

Name-cache operations:
- `dnlc_init` sizes the cache, creates hash buckets and locks, initializes rotors, creates the directory-space kmem cache, initializes directory-cache global state, prepares the negative vnode, and installs kstats.
- `dnlc_enter` inserts a new `(directory vnode, name) -> vnode` mapping unless it already exists.
- `dnlc_update` inserts or updates a mapping, and removes stale negative entries if allocation fails.
- `dnlc_lookup` searches the hash bucket, moves deep hits toward the front, returns a caller-held vnode, and counts negative hits separately.
- `dnlc_remove` deletes one named entry.
- `dnlc_purge` purges all entries.
- `dnlc_purge_vp` removes entries referring to a vnode and stops once `v_count_dnlc` reaches zero.
- `dnlc_purge_vfsp` removes entries for a VFS, optionally bounded by count.
- `dnlc_fs_purge1` frees one candidate entry for a filesystem vnodeops table, preferring vnodes with no cached data and only DNLC reference.
- `dnlc_reduce_cache` schedules cache reduction.
- `dnlc_get` allocates variable-sized name-cache entries, enforces `dnlc_max_nentries`, and triggers reduction.
- `do_dnlc_reduce_cache` reclaims entries down to the low-water target or a requested percentage target.

Reference and deadlock model:
- `VN_HOLD_DNLC` increments `v_count_dnlc` and only takes a real vnode hold for the first DNLC reference.
- `VN_RELE_DNLC` releases via `vn_rele_dnlc`.
- Purge routines collect vnode releases into stack arrays and release after dropping hash locks to avoid inactive-path recursion and DNLC deadlocks.
- Hash buckets each have their own mutex; global scans process bounded batches and retry chains when necessary.

Directory-cache operations:
- `dnlc_dir_lookup` looks up names in partial or complete directory caches and can return `DFOUND`, `DNOENT`, or `DNOCACHE`.
- `dnlc_dir_start` creates a directory cache if enabled and within size thresholds.
- `dnlc_dir_add_entry` adds name-to-handle entries, dynamically resizing the name hash table and aborting/purging on memory pressure or excessive size.
- `dnlc_dir_add_space` adds free-space records, dynamically resizing the free-space hash table.
- `dnlc_dir_complete` marks a cache complete so misses can become definite `DNOENT`.
- `dnlc_dir_abort` frees all entries, free-space records, hash tables, and the directory-cache object.
- `dnlc_dir_purge` removes a directory cache from the global list and aborts it.
- `dnlc_dir_rem_entry`, `dnlc_dir_rem_space_by_len`, and `dnlc_dir_rem_space_by_handle` remove cached records and may purge undersized caches.
- `dnlc_dir_update` changes an entry handle in-place.
- `dnlc_dir_fini` tears down a directory cache anchor.
- `dnlc_dir_reclaim` is the kmem reclaim callback; it purges least-recently-used directory caches until enough entries have been freed.
- `dnlc_dir_adjust_nhash` and `dnlc_dir_adjust_fhash` resize directory-cache hash tables.

Tuning and observability:
- Name-cache sizing is controlled by `ncsize`, `nc_hashavelen`, `dnlc_low_water_divisor`, and related low/high-water values.
- Directory caching is controlled by `dnlc_dir_enable`, min/max size tunables, hash sizing shifts, and reclaim thresholds.
- Named kstats track hits, misses, negative hits, enter/double-enter counts, purge counts, eviction heuristics, and directory-cache outcomes.

Research notes:
- DNLC is central VFS infrastructure, not tied to devfs or sdev specifically.
- The separate directory cache is handle-oriented and supports both name lookup acceleration and directory free-space reuse.
- Memory-pressure behavior is intentionally conservative: cache creation/addition can return `DNOCACHE`, purge existing directory caches, or mark an anchor with `DC_RET_LOW_MEM`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dnlc.c -->