# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_znode_os.c

## Read Coverage
Read completely: 1,932 lines, 49,981 bytes.

## Purpose
`zfs_znode_os.c` implements FreeBSD-specific znode lifecycle, vnode construction, SA/DMU object binding, filesystem bootstrap, and file-size/block-range helpers for OpenZFS. It is the object-lifecycle counterpart to the vnode operation layer: it creates, finds, refreshes, deletes, and frees znodes while keeping FreeBSD vnode state consistent with ZFS on-disk metadata.

## Major Responsibilities
- Initializes and destroys the znode allocation cache, using SMR-aware UMA zones when available or a kmem cache under debug builds.
- Constructs and destructs per-znode locks, range locks, xattr locks, ACL cache state, cached symlink pointers, and vnode pointers.
- Allocates and initializes `znode_t` plus FreeBSD `vnode_t` pairs from DMU buffers and SA handles.
- Creates new ZFS objects and their SA metadata via `zfs_mknode()`.
- Looks up existing znodes by object number through `zfs_zget()` and refreshes stale znodes through `zfs_rezget()`.
- Tears down znodes and SA handles through `zfs_znode_dmu_fini()`, `zfs_zinactive()`, `zfs_znode_delete()`, and `zfs_znode_free()`.
- Implements atime/mtime/ctime update setup, block-size growth, file extension, truncation, hole punching/free-range, and `zfs_freesp()`.
- Bootstraps a new ZPL objset in `zfs_create_fs()`, including master node, root object, unlinked set, SA registration object, and shares directory.

## Key Data and Interfaces
- `znode_t` holds cached metadata such as object id, generation, size, links, mode, uid/gid, project ID, pflags, block size, SA handle, vnode pointer, and cached xattr/symlink state.
- `zfsvfs_t` provides object set, ZPL version, SA/FUID configuration, normalization/case settings, znode list, per-object hold locks, and root/share object IDs.
- `vnode_t` is created with FreeBSD VOP vectors: regular ZFS vnode ops, FIFO ops, or special share-file ops.
- SA attributes are read and written through `sa_bulk_lookup()`, `sa_replace_all_by_template()`, `sa_bulk_update()`, `sa_update()`, and SA handle setup/destruction.
- DMU object creation uses `zap_create_norm_dnsize()`, `zap_create_claim_norm_dnsize()`, `dmu_object_alloc_dnsize()`, and `dmu_object_claim_dnsize()`.
- Object hold locks (`ZFS_OBJ_HOLD_ENTER/EXIT`) serialize znode lookup, creation, refresh, and deletion for a given object number.

## Control Flow Highlights
- `zfs_rangelock_cb()` converts append locks into writer locks at the current EOF and expands locks to the whole file when a write may grow the file block size.
- `zfs_znode_alloc()` reserves and creates a FreeBSD vnode, initializes znode cached fields, attaches an SA handle, loads core metadata, sets vnode type and operation vector, inserts the znode into `z_all_znodes`, and returns the vnode locked.
- `zfs_mknode()` creates or claims a DMU object depending on replay mode, determines old-style znode versus SA layout, fills all required ZPL attributes in correct layout order, writes ACL data, creates an in-core znode for non-root objects, and enqueues the vnode on the mount.
- `zfs_zget()` first checks whether the SA buffer already has user data for a live znode. If found, it safely holds the vnode and retries if the vnode is doomed by concurrent reclaim. If not found, it allocates a new znode/vnode from the DMU object and inserts it into the mount queue.
- `zfs_rezget()` removes cached pages, clears cached ACL/xattr state, reloads SA metadata after rollback/receive, validates generation and vnode type, marks zero-link received files as unlinked, and updates vnode pager size if needed.
- `zfs_zinactive()` removes unlinked files through `zfs_rmnode()` unless the filesystem is read-only; otherwise it drops SA state and frees the znode.
- `zfs_extend()`, `zfs_trunc()`, and `zfs_free_range()` use range locks plus DMU operations to update file size, purge page ranges, grow block size when appropriate, and keep vnode pager size synchronized.
- `zfs_create_fs()` builds a minimal temporary `zfsvfs_t` and root znode so `zfs_mknode()` can be reused during initial filesystem creation.

## Important Functions
- `zfs_znode_init()` and `zfs_znode_fini()` manage allocator lifetime.
- `zfs_znode_alloc()` is the central in-core znode/vnode constructor for existing objects.
- `zfs_mknode()` is the central on-disk object constructor for new files, directories, devices, symlinks, root, and xattr objects.
- `zfs_zget()` is the primary object-number-to-znode resolver.
- `zfs_rezget()` handles znode refresh after object set changes.
- `zfs_zinactive()` and `zfs_znode_free()` implement final lifecycle cleanup.
- `zfs_freesp()` coordinates truncate, extend, hole punching, timestamp update, and ZIL truncate logging.
- `zfs_create_fs()` initializes the core ZPL objects for a new dataset.
- `zfs_znode_parent_and_name()` maps a znode back to its parent and name for `vptocnp`.

## Invariants and Assumptions
- A znode with a valid `z_zfsvfs` pointer is on the filesystem's znode list; invalidating that pointer is part of final removal.
- `zfs_znode_sa_init()` requires the per-object hold mutex and assumes `z_sa_hdl` is not already set.
- Existing SA user data must point back to a matching live znode for the same object.
- Root creation uses a temporary, partially initialized znode and `zfsvfs_t`, then tears them down after writing on-disk bootstrap metadata.
- Old `DMU_OT_ZNODE` layout has strict SA attribute ordering to preserve the historical `znode_phys_t` format.
- File block size growth is allowed only before the file has grown past the current block size and follows the same whole-file lock condition used by the range-lock callback.
- Zero-link znodes may remain in the unlinked set, especially across read-only transitions or receive/rollback refresh behavior.

## Risks and Edge Cases
- `zfs_zget()` has subtle interaction with doomed vnodes and concurrent reclaim; incorrect reference or lock handling can produce stale vnode use or lock-order reversals.
- `zfs_rezget()` handles rare object-number/generation collisions after receive/rollback by refusing to reassociate incompatible vnode types.
- Root/share directory bootstrap depends on temporary structures mimicking enough mounted filesystem state for `zfs_mknode()`.
- SA versus old znode layout, ACL version upgrades, project-ID slot insertion, and FUID handling are all format-sensitive.
- Truncate/free-range paths must coordinate DMU frees with vnode pager size and page invalidation.
- Cached ACLs, cached xattrs, and cached symlinks must be freed on all final znode paths without racing SMR readers.
- `zfs_rlimit_fsize()` sends `SIGXFSZ` on file-size limit violation; callers must use it before growth paths that expose user-visible limit behavior.

## Testing Signals
Useful coverage should include:
- Znode cache init/fini under SMR and non-SMR builds.
- `zfs_zget()` for existing cached znodes, newly allocated znodes, unlinked objects, invalid bonus types, doomed vnode retry, and mount-queue insertion failure.
- `zfs_mknode()` for files, directories, root objects, xattrs, devices, SA layout, old znode layout, replay-claimed objects, ACL spill objects, FUIDs, and project quotas.
- `zfs_rezget()` after rollback/receive, including changed size, changed type, zero links, missing project ID, and generation mismatch.
- Inactive/reclaim of linked files, unlinked files, read-only unlinked files, and force-unmount/teardown cases.
- Extend, truncate, hole-punch/free-range, block-size growth, sparse flag clearing at size zero, timestamp updates, and ZIL truncate logging.
- Fresh filesystem creation with version, normalization, case-sensitivity, SA, root object, unlinked set, and shares directory properties.

## Overall Assessment
This file is the FreeBSD znode lifecycle and ZPL object-construction foundation. It is less VOP-facing than `zfs_vnops_os.c`, but it carries critical correctness obligations around object identity, SA metadata layout, vnode lifetime, rollback/receive refresh, and file-size state. Regressions here would show up as stale vnode references, metadata corruption, broken new-filesystem initialization, or incorrect unlinked/truncation behavior.
