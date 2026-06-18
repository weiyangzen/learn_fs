# Group Research: group_1428_openzfs_sources_cow_pools_openzfs_module_os_linux_zfs_zfs_vfsops_c__f890a5375c78

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_vfsops.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_vfsops.c

## Read Coverage
Read completely: 2,064 lines, 54,500 bytes.

## Purpose
`zfs_vfsops.c` is the Linux superblock/VFS lifecycle layer for OpenZFS ZPL datasets. It owns the mount-time construction of `zfsvfs_t`, dataset ownership, property callback wiring, root inode setup, ZIL replay, unmount teardown, suspend/resume for rollback/receive, statfs reporting, export file-handle lookup, and module filesystem registration.

## Major Responsibilities
- Allocates and frees Linux-side `vfs_t` mount option containers and `zfsvfs_t` filesystem state.
- Loads ZPL properties and master-node object IDs into `zfsvfs_t`, including root, unlinked set, FUID tables, quota objects, shares directory, normalization, case behavior, SA usage, and xattr mode.
- Registers DSL property callbacks for mounted datasets and maps selected ZFS properties into Linux superblock state.
- Sets up mounted filesystems by creating dataset kstats, opening the ZIL, draining the unlinked set, replaying intent logs, and installing the objset user pointer.
- Implements `zfs_domount()`, `zfs_preumount()`, `zfs_umount()`, and `zfs_remount()` around Linux `struct super_block`.
- Handles ARC-driven dentry/inode pruning and manual alias pruning when kernel shrinkers cannot reclaim enough.
- Implements `statfs`, project quota-aware statfs overrides, root lookup, NFS/export `vget`, and snapshot control-directory file-handle handling.
- Implements mounted filesystem suspend/resume/end paths used by rollback and receive.
- Registers and unregisters the ZPL filesystem type and znode/control-directory subsystems.

## Key Data and Interfaces
- `zfsvfs_t` is the central mounted-dataset state, binding `objset_t`, Linux `super_block`, ZIL, property-derived policy, znode lists, per-object hold locks, kstats, and teardown locks.
- `vfs_t` stores temporary mount-option overrides that can differ from persistent dataset properties.
- `struct super_block` receives ZFS-specific operations: `zpl_super_operations`, `zpl_xattr_handlers`, `zpl_export_operations`, and `zpl_dentry_operations`.
- Uses DSL/DMU interfaces including `dmu_objset_own()`, `dmu_objset_disown()`, `dmu_objset_set_user()`, `zap_lookup()`, `zfs_get_zplprop()`, `sa_setup()`, and `dsl_prop_register()`.
- Uses ZIL interfaces `zil_open()`, `zil_replay()`, `zil_commit_flags()`, `zil_destroy()`, and `zil_close()`.
- Uses Linux shrinker, dentry, inode, backing-device, and mount flags through `super_setup_bdi_name()`, `shrink_dcache_sb()`, `d_prune_aliases()`, `igrab()`, and superblock flag updates.

## Control Flow Highlights
- `zfs_register_callbacks()` preserves temporary mount-option overrides, registers dataset property callbacks, then reapplies the temporary values so mounted behavior can differ from persistent properties.
- `zfsvfs_init()` loads all persistent ZPL metadata and validates dataset/pool compatibility before the filesystem is usable.
- `zfsvfs_create()` owns the dataset and delegates construction to `zfsvfs_create_impl()`, which initializes znode lists, teardown locks, FUID locks, and per-object znode hold AVL trees.
- `zfsvfs_setup()` opens the ZIL, optionally clears readonly during replay, drains the unlinked set before replay, replays the ZIL when enabled and writeable, restores readonly, and installs `os_user_ptr`.
- `zfs_domount()` enforces zone visibility/writeability, handles snapshots as read-only non-replayed mounts, wires superblock operations, creates the root dentry, creates `.zfs` control state for live datasets, and registers ARC prune callbacks.
- `zfsvfs_teardown()` stops unlinked draining, waits for async `zrele` work, blocks VFS operations, closes the ZIL, optionally detaches SA handles for suspended filesystems, marks unmounted state, unregisters properties, waits for dirty txgs, evicts dbufs, and cancels DSL directory waiters.
- `zfs_resume_fs()` rebuilds `zfsvfs_t` state against a refreshed objset, reopens callbacks/ZIL, revalidates every active znode with `zfs_rezget()`, unhashes stale inodes, clears suspended references asynchronously, restarts unlinked draining, and drops cached negative dentries.
- `zfs_vget()` decodes short and long ZFS file handles, handles `.zfs` control/snapshot synthetic IDs, rejects xattr objects, verifies generation numbers, and returns a held inode.

## Important Functions
- `zfsvfs_init()` caches ZPL on-disk properties and master-node object IDs into `zfsvfs_t`.
- `zfsvfs_create()` and `zfsvfs_create_impl()` allocate and initialize mounted filesystem state after owning an objset.
- `zfsvfs_setup()` performs mount or resume setup, including unlinked draining and ZIL replay/opening.
- `zfs_domount()` is the main Linux mount entry point.
- `zfs_preumount()`, `zfs_umount()`, and `zfsvfs_teardown()` implement unmount ordering and final release.
- `zfs_remount()` swaps temporary mount options and refreshes callbacks.
- `zfs_statvfs()` and `zfs_statfs_project()` report filesystem and project-quota-limited capacity.
- `zfs_prune()` and `zfs_prune_aliases()` coordinate ARC pressure with Linux inode/dentry reclaim.
- `zfs_suspend_fs()`, `zfs_resume_fs()`, and `zfs_end_fs()` support rollback/receive transitions.
- `zfs_set_version()` and `zfs_set_default_quota()` mutate ZPL version/default quota properties transactionally.
- `zfs_init()` and `zfs_fini()` register/unregister the Linux ZPL filesystem type.

## Invariants and Assumptions
- Mounted VFS operations must be blocked through teardown locks before SA handles, dbufs, ZIL state, or objset ownership are invalidated.
- `zfsvfs->z_os` is owned by the `zfsvfs_t` while the filesystem is mounted or suspended.
- `os_user_ptr` is the active bridge from an objset back to its mounted `zfsvfs_t`; it must be set during setup and cleared during unmount.
- Snapshots are mounted read-only, skip normal ZIL setup/replay, and use deferred unmount timing through snapshot control-directory code.
- Unlinked-set draining must happen before ZIL replay for correctness under ziltest and object reuse scenarios.
- Active znodes must be pinned or processed asynchronously while suspend/resume walks `z_all_znodes`.
- Temporary mount options are represented in `vfs_t` and must survive property callback registration.

## Risks and Edge Cases
- Mount failure paths must avoid double-freeing `zfsvfs_t`, `vfs_t`, objset ownership, and `sb->s_fs_info`.
- Teardown ordering is subtle: async `iput()`, inactive processing, ZIL close, dbuf eviction, and VFS operation blocking can deadlock if reordered.
- Rollback/receive resume can encounter active inodes whose object number now refers to different contents; stale inodes must be unhashed safely.
- Export file handles must distinguish real objects from `.zfs` control-directory synthetic objects and verify generation masks.
- ARC pruning relies on kernel shrinker behavior but has a manual fallback for non-root memory cgroup references.
- Project-quota statfs reporting can observe async accounting races and falls back to estimated object/block usage.
- Readonly handling is layered: persistent readonly property, snapshot status, zone writeability, remount flags, and temporary mount options can all affect behavior.

## Testing Signals
Useful coverage should include:
- Mount and unmount of normal datasets, snapshots, readonly datasets, non-writeable pools, and datasets hidden from a zone.
- Mount failure injection around objset ownership, property lookup, BDI setup, root inode allocation, root dentry allocation, ZIL setup, and callback registration.
- ZIL replay enabled/disabled paths and unlinked-set draining before replay.
- Remount transitions between read-write and read-only, including txg sync on read-only transition.
- Rollback/receive suspend and resume with active files, deleted files, negative dentries, stale object generations, and in-flight async `zrele`.
- NFS/export file-handle lookup for root, normal files, stale generations, xattrs, `.zfs`, and snapshot directories.
- `statfs` with and without project quota, default project quota, project object quota, and async accounting gaps.
- ARC prune callback behavior under memory pressure and when kernel shrinkers reclaim nothing.

## Overall Assessment
This file is the Linux mounted-filesystem control plane for OpenZFS. It does not implement most file operations directly; instead it establishes the safe execution environment for them by owning dataset state, ZIL lifecycle, property policy, superblock wiring, teardown locks, znode hold tables, and rollback/receive transitions. Regressions here tend to be severe: failed mounts, unsafe unmounts, stale inodes after rollback, broken snapshot export behavior, or deadlocks between VFS reclaim, async inode release, and ZFS teardown.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_vnops_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_vnops_os.c

## Read Coverage
Read completely: 4,440 lines, 113,842 bytes.

## Purpose
`zfs_vnops_os.c` is the Linux-specific ZPL operation layer for OpenZFS. It implements exported inode/vnode-style helpers for open/close, lookup, create, tmpfile, remove, mkdir/rmdir, readdir, getattr/setattr, rename, symlink/readlink, link, page-cache writeback/fault reads, dirty inode handling, mmap permission checks, space freeing, and file-handle generation.

## Major Responsibilities
- Implements namespace operations over ZFS directories: lookup, create, tmpfile, remove, mkdir, rmdir, rename, symlink, hard link, and directory iteration.
- Bridges Linux inode/page-cache behavior with ZFS DMU/SA/ZIL state through page update, mapped-read, page fault read, dirty inode, and writeback helpers.
- Enforces ZFS security and metadata policy: ACL checks, FUID support, ephemeral ID validation, readonly/immutable/append-only/nounlink flags, project inheritance, project quota, xattr namespace boundaries, and Linux idmapped mount translation.
- Coordinates ZFS transactions and ZIL logging for namespace and metadata mutations.
- Supports Linux rename extensions: `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`.
- Handles O_TMPFILE creation and later linking from the unlinked set with txg durability semantics.
- Updates Linux inode state from znode/SA state after ZFS metadata mutations.
- Exports the Linux operation helpers consumed by ZPL wrapper files such as `zpl_inode.c`, `zpl_file.c`, and related Linux glue.

## Key Data and Interfaces
- Uses `znode_t` and embedded Linux `struct inode` as paired filesystem/inode state.
- Uses `zfsvfs_t` for mounted dataset state, including objset, ZIL, sync mode, xattr mode, UTF-8/case handling, quota objects, and teardown guards.
- Uses `zfs_dirlock_t` for directory-entry locking and `z_rangelock` for file data/page-cache ranges.
- Uses SA attributes (`SA_ZPL_*`) and bulk SA updates for inode metadata, timestamps, flags, project IDs, link counts, symlink data, and xattr pointers.
- Uses DMU transactions with explicit holds and follows the file header’s ordering rules: enter filesystem, take locks, create/hold tx, assign nonblocking when ZPL locks are held, log before unlocking, commit, then optionally `zil_commit()`.
- Uses Linux page-cache APIs such as `find_lock_page()`, `kmap()`, `flush_dcache_page()`, `clear_page_dirty_for_io()`, `set_page_writeback()`, `end_page_writeback()`, `truncate_inode_pages_range()`, and `truncate_setsize()`.
- Uses Linux VFS idmapping helpers through `zidmap_t`, `zfs_uid_to_vfsuid()`, `zfs_gid_to_vfsgid()`, and inode namespace helpers.

## Control Flow Highlights
- The opening programming-rules block is central: it documents mount verification, delayed `zrele()`, range-lock-before-transaction ordering, `DMU_TX_NOWAIT` with ZPL locks, ZIL logging before unlock, unconditional tx commit, and post-unlock synchronous commits.
- `zfs_open()` enforces append-only write opens and upgrades existing async ZIL records to sync when the first `O_SYNC` open appears.
- `zfs_lookup()` has a fast path for simple non-xattr lookups, handles `.` and empty names, enters xattr directories through `zfs_get_xattrdir()`, enforces directory execute permission, validates UTF-8, and returns held znodes.
- `zfs_create()` handles existing-file open/truncate separately from new object creation; new creation validates FUID/ACL/version state, quotas, xattrs, UTF-8, directory permissions, transaction holds, `zfs_mknode()`, link insertion, ZIL create logging, and sync mode.
- `zfs_tmpfile()` creates an unlinked regular object and inserts it into the unlinked set so it can later be linked or destroyed.
- `zfs_remove()` decides between immediate deletion and deferred unlinked-set removal based on link count, inode references, cached data, file size threshold, xattr state, and external ACL state.
- `zfs_setattr()` is the central metadata mutation path. It handles truncation/extension, uid/gid/project changes, xattr directory propagation, ACL chmod/chown behavior, optional attributes, timestamp updates, quota checks, SA layout upgrades for project IDs, FUID synchronization, and ZIL setattr logging.
- `zfs_rename()` establishes deterministic source/target dirent locking, checks project inheritance and access, prevents directory cycles via parent-lock tree walk, supports exchange and whiteout variants, logs the exact rename flavor, and includes recovery code for partially changed link state.
- `zfs_putpage()` deliberately drops the page lock before taking the range lock, then rechecks page state to avoid Linux page-lock/range-lock inversions. It redirties failed writeback pages and uses ZIL callbacks for synchronous page-clean completion.
- `zfs_getpage()` takes a range lock around page fault reads to avoid races with direct I/O or block cloning that may temporarily clear dbuf data.
- `zfs_fid()` encodes object number and nonzero generation in short ZFS file handles.

## Important Functions
- `zfs_open()` and `zfs_close()` maintain append-only and sync-open semantics.
- `update_pages()` and `mappedread()` keep mmap/page-cache contents coherent with DMU reads.
- `zfs_write_simple()` provides a small kernel-buffer write wrapper around common `zfs_write()`.
- `zfs_zrele_async()` avoids synchronous final `iput()` in unsafe transaction/lock contexts.
- `zfs_lookup()`, `zfs_get_name()`, and `zfs_readdir()` implement lookup, reverse-name lookup, and directory enumeration.
- `zfs_create()`, `zfs_tmpfile()`, `zfs_remove()`, `zfs_mkdir()`, `zfs_rmdir()`, `zfs_rename()`, `zfs_symlink()`, and `zfs_link()` implement namespace mutation.
- `zfs_getattr_fast()` and `zfs_setattr()` expose and mutate Linux inode metadata.
- `zfs_setattr_dir()` propagates ownership/project changes into hidden xattr directory entries.
- `zfs_putpage()`, `zfs_getpage()`, `zfs_dirty_inode()`, and `zfs_inactive()` integrate Linux page-cache and inode lifecycle events with ZFS SA/DMU/ZIL state.
- `zfs_map()` enforces mmap restrictions for immutable, readonly, append-only, and quarantined files.
- `zfs_space()` calls `zfs_freesp()` for file hole punching/truncation-like operations.
- `zfs_fid()` produces exportable ZFS file IDs.

## Invariants and Assumptions
- Every operation that touches live ZFS state must enter the filesystem and verify znodes before using SA handles.
- Final `zrele()`/`iput()` can trigger `zfs_zinactive()` and new transactions, so release timing is part of transaction correctness.
- Directory-entry locks, range locks, parent/name locks, ACL locks, and znode locks must follow the ordering implied by the header comment and operation-specific retry loops.
- ZIL records must be generated while the mutation ordering locks are still held.
- Xattr directory contents must not be linked or renamed into ordinary namespace entries or vice versa.
- Project-inheriting directories constrain hard links and renames to matching project IDs.
- `O_TMPFILE` objects remain in the unlinked set until linked and require txg sync semantics rather than ordinary ZIL link replay.
- Page writeback must preserve dirty data on errors and must not unlock a synchronously written page as clean until its ZIL/txg durability condition has been met.
- Linux inode fields are refreshed after ZFS metadata mutations through `zfs_znode_update_vfs()`.

## Risks and Edge Cases
- `zfs_setattr()` has a large blast radius: ACLs, FUIDs, uid/gid, project IDs, hidden xattr directories, SA upgrades, immutable/read-only policy, timestamps, truncation, and quotas all interact.
- Rename is concurrency-sensitive because it combines dirent locks, directory name locks, parent locks, optional target removal, exchange/whiteout creation, and rollback-style repair paths.
- `zfs_remove()` immediate-delete decisions can be invalidated by concurrent references, xattr changes, ACL changes, or cached page state.
- Page writeback has explicit lock-inversion hazards with `zfs_read()`, `zfs_write()`, truncation, and page fault handling.
- Fault reads must hold range locks because direct I/O and block cloning can transiently clear dbuf data.
- Linux lazytime/dirty-inode behavior means atime may be deferred and later persisted through inactive or dirty-inode handling.
- Case-insensitive/case-preserving rename and lookup behavior depends on UTF-8 normalization flags and exact-match handling.
- Error cleanup for failed namespace changes must preserve link counts, unlinked-set state, inode hash state, and ZIL replay consistency.

## Testing Signals
Useful coverage should include:
- Lookup of ordinary names, empty names, `.`, missing entries, xattr directories, invalid UTF-8, case-insensitive names, and hidden `.zfs` interactions through callers.
- Create/open existing/truncate paths, exclusive create, xattr-directory create restrictions, ACL inheritance, FUID/ephemeral IDs, project quotas, and sync-always behavior.
- O_TMPFILE creation, later link, failed link restoration, and txg sync behavior under normal and failmode-continue pools.
- Remove of small files, large files, files with cached pages, files with xattrs, files with external ACLs, open-but-unlinked files, and directories passed to remove.
- Mkdir/rmdir with permissions, non-empty directories, current-working-directory removal, project inheritance, and case-insensitive flags.
- Rename same-name no-op, case-only rename, directory cycle prevention, cross-superblock rejection, project mismatch rejection, `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`.
- `setattr` for size changes, uid/gid changes, project ID and project-inherit toggles, chmod under restricted ACL mode, immutable/append/nounlink flags, birthtime, AV flags, xattr directory propagation, quota failures, and SA project-ID upgrade.
- Page fault reads, mmap writes, async writeback, sync writeback, writeback failure redirtying, EOF partial pages, concurrent truncate/free-range, and direct I/O/block clone races.
- Dirty inode and inactive processing with lazytime atime, unlinked files, readonly remounts, and rollback-held teardown locks.
- Export file-handle generation and lookup paired with `zfs_vget()`.

## Overall Assessment
This file is the Linux operational core of the OpenZFS ZPL. Its complexity is concentrated at boundaries: Linux VFS semantics, ZFS transactions, ZIL replay requirements, SA metadata layout, ACL/security policy, project quotas, namespace locking, and page-cache coherency. Changes here should be treated as high risk unless backed by tests that combine concurrency, mmap/page writeback, rename, xattr, quota, ACL, tmpfile, and sync-write workloads.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_vnops_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_znode_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_znode_os.c

## Read Coverage
Read completely: 1,982 lines, 53,107 bytes.

## Purpose
`zfs_znode_os.c` implements Linux-specific znode/inode lifecycle and ZPL object construction for OpenZFS. It creates, finds, refreshes, updates, deletes, and frees znodes while binding Linux inode state to ZFS DMU objects and SA metadata. It also implements timestamp setup, block-size growth, truncate/free-range helpers, and initial ZPL filesystem creation.

## Major Responsibilities
- Initializes and destroys znode and per-object hold caches.
- Constructs/destructs znode locks, range locks, ACL/xattr cache state, and embedded Linux inode state.
- Implements external per-object znode hold locks used before a znode or SA handle may exist.
- Allocates Linux inodes and initializes ZFS znodes from DMU buffers and SA handles.
- Sets Linux inode operation tables and special inode/device state based on ZFS mode.
- Creates new DMU objects and SA metadata through `zfs_mknode()`.
- Resolves object numbers to live znodes with `zfs_zget()`.
- Rebinds active znodes after rollback/receive with `zfs_rezget()`.
- Deletes DMU objects and external ACL objects and finalizes SA handles.
- Handles inactive znode cleanup and removal of unlinked files.
- Implements relatime checks, timestamp mutation setup, block-size growth, file extension, hole punching, truncation, and `zfs_freesp()`.
- Bootstraps a new ZPL objset in `zfs_create_fs()`.

## Key Data and Interfaces
- `znode_t` embeds or maps to Linux `struct inode` and stores cached ZFS state: object ID, size, block size, mode, pflags, project ID, sync count, SA handle, ACL cache, xattr cache, and range/name/parent locks.
- `znode_hold_t` serializes access to an object number before or while its znode/SA handle is being created, found, refreshed, or destroyed.
- `zfsvfs_t` provides object set, superblock, ZPL feature flags, SA attribute table, znode list, and hold-lock arrays.
- Uses `new_inode()`, `insert_inode_locked()`, `unlock_new_inode()`, `iput()`, `mark_inode_dirty()`, inode operation tables, and page-cache truncation APIs.
- Uses SA operations `sa_handle_get_from_db()`, `sa_replace_all_by_template()`, `sa_bulk_lookup()`, `sa_bulk_update()`, `sa_update()`, `sa_add_projid()`, and `sa_handle_destroy()`.
- Uses DMU/ZAP object creation and deletion APIs, including `zap_create_norm_dnsize()`, `zap_create_claim_norm_dnsize()`, `dmu_object_alloc_dnsize()`, `dmu_object_claim_dnsize()`, `dmu_object_free()`, `dmu_free_long_range()`, and `dmu_object_set_blocksize()`.

## Control Flow Highlights
- `zfs_rangelock_cb()` converts append locks into writer locks at EOF and expands locks to the whole file when a write may trigger block-size growth.
- `zfs_znode_hold_enter()` allocates outside the global hold lock, inserts/fetches a per-object hold in an AVL bucket, increments the refcount, then locks the per-object mutex. `zfs_znode_hold_exit()` reverses that and frees the hold when no waiters remain.
- `zfs_znode_alloc()` creates a Linux inode, initializes znode defaults, attaches an SA handle, bulk-loads metadata, validates generation/project attributes, sets inode mode/owner/timestamps/link count/flags, installs Linux inode ops, hashes linked inodes, and inserts the znode in `z_all_znodes`.
- `zfs_mknode()` creates or claims a DMU object, handles directory versus file object types, chooses old znode layout versus SA layout, writes all base attributes in layout-sensitive order, writes ACL data, allocates an in-core znode for non-root objects, and initializes project inheritance.
- `zfs_zget()` serializes by object number, validates bonus type, reuses an existing SA user znode when possible, retries if Linux eviction is in progress, rejects unlinked objects, or allocates a new znode from the DMU buffer.
- `zfs_rezget()` skips control-directory znodes, clears cached ACL/xattr state, rebuilds the SA handle, reloads metadata, validates generation, updates Linux inode state, and detaches SA state for zero-link received/unlinked files.
- `zfs_zinactive()` serializes against object lookup and either removes an unlinked object through `zfs_rmnode()` or destroys the SA handle while leaving read-only unlinked objects in the unlinked set.
- `zfs_freesp()` dispatches to extend, truncate, or free-range logic, then logs a truncate record and updates timestamps when requested.
- `zfs_create_fs()` creates the master node, ZPL properties, SA registration object, unlinked set, and root object using a minimal temporary `zfsvfs_t`, `super_block`, and root znode.

## Important Functions
- `zfs_znode_init()` and `zfs_znode_fini()` manage znode allocation caches.
- `zfs_znode_hold_enter()` and `zfs_znode_hold_exit()` provide per-object serialization outside the znode itself.
- `zfs_inode_alloc()`, `zfs_inode_free()`, and `zfs_inode_destroy()` bind Linux inode allocation/destruction to the znode cache and cleanup state.
- `zfs_inode_set_ops()` installs Linux inode/file/address-space operations for regular files, directories, symlinks, devices, FIFOs, and sockets.
- `zfs_znode_update_vfs()` refreshes Linux inode mode, block count, and size from ZFS state.
- `zfs_znode_alloc()` constructs an in-core znode/inode from an existing DMU object.
- `zfs_mknode()` constructs a new on-disk ZPL object and its in-core znode.
- `zfs_xvattr_set()` applies optional ZFS attributes and updates Linux immutable/append flags when needed.
- `zfs_zget()` resolves object IDs to held znodes.
- `zfs_rezget()` refreshes znodes after objset changes.
- `zfs_znode_delete()` and `zfs_zinactive()` implement object deletion and final inactive behavior.
- `zfs_tstamp_update_setup()`, `zfs_grow_blocksize()`, `zfs_extend()`, `zfs_free_range()`, `zfs_trunc()`, and `zfs_freesp()` manage file size, block ranges, timestamps, and page-cache truncation.
- `zfs_create_fs()` initializes a new ZPL filesystem.

## Invariants and Assumptions
- Object-number hold locks must protect znode/SA creation, lookup, refresh, and deletion when the znode itself may not yet be reliable.
- A znode with a live SA handle must not be freed or rediscovered concurrently outside the hold-lock protocol.
- Existing SA user data must point to a znode for the same object number; Linux `igrab()` decides whether it can be safely reused.
- Linked znodes are inserted into the Linux inode hash; unlinked znodes are deliberately not hashed to avoid rollback/unlinked-drain collisions.
- Old `DMU_OT_ZNODE` layout has strict SA attribute ordering to preserve historical `znode_phys_t` format.
- Root filesystem creation uses a temporary minimal mount/inode environment so `zfs_mknode()` can be reused.
- File block-size growth is allowed only under whole-file range locking and only while file layout constraints permit it.
- Truncate and free-range operations must keep DMU data, znode size, Linux inode size, and page cache coherent.

## Risks and Edge Cases
- `zfs_zget()` must handle Linux inode eviction races; incorrect handling can return a dying inode or block eviction completion.
- `zfs_rezget()` after rollback/receive must reject generation mismatches and stale object identities without corrupting active dentries.
- Project quota support depends on presence and layout of `SA_ZPL_PROJID`; old objects may need SA layout upgrades elsewhere.
- `zfs_mknode()` is format-sensitive across SA and old znode layouts, replay-claimed objects, ACL spill data, device files, tmpfiles, xattrs, and root creation.
- Inactive cleanup can leave unlinked files in the unlinked set on read-only filesystems or when debug suspension is enabled.
- Hole punching and truncation must coordinate full-page invalidation with partial-page zeroing under range locks.
- Temporary root creation in `zfs_create_fs()` manually initializes enough `zfsvfs_t`, hold locks, list state, and superblock state to satisfy shared constructors; missing one field can break bootstrap.
- Cache cleanup must release ACL and xattr caches on inode destruction and rollback refresh without racing users.

## Testing Signals
Useful coverage should include:
- Znode cache init/fini and inode allocation/free under reclaim.
- `zfs_zget()` for cached znodes, newly loaded znodes, invalid bonus types, unlinked objects, eviction-in-progress retry, and low-memory allocation retry through `zfs_mknode()`.
- `zfs_znode_alloc()` metadata loading for regular files, directories, symlinks, devices, FIFOs/sockets, xattr znodes, old znode layout, SA layout, and project-ID attributes.
- `zfs_mknode()` for root, normal files, directories, symlinks, devices, xattrs, tmpfiles, replay object claims, ACL spill objects, FUIDs, and project inheritance.
- `zfs_rezget()` after rollback/receive with changed size, changed timestamps, generation mismatch, zero links, missing project ID, and control-directory znodes.
- Inactive/delete behavior for linked files, unlinked open files, read-only unlinked files, files with external ACLs, and debug-suspended unlink progress.
- File extension, truncation to zero, truncation to nonzero, hole punching within one page, hole punching across pages, sparse flag clearing, page-cache truncation, and ZIL truncate logging via `zfs_freesp()`.
- New filesystem creation with different ZPL versions, SA enabled/disabled, case/normalization properties, root object creation, and unlinked set creation.

## Overall Assessment
This file is the Linux znode lifecycle and object-construction foundation for OpenZFS. It sits below the operation layer and determines whether Linux inodes, ZFS object numbers, SA handles, page-cache size, and on-disk metadata remain consistent across creation, lookup, deletion, rollback, receive, and truncation. Bugs here are likely to surface as stale inode reuse, incorrect metadata layout, leaked or prematurely freed objects, page-cache incoherency, or broken freshly created datasets.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_znode_os.c -->