# Group Research: group_1424_openzfs_sources_cow_pools_openzfs_module_os_freebsd_zfs_zfs_vnops_o_3f69272c391e

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_vnops_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_vnops_os.c

## Read Coverage
Read completely: 7,083 lines, 174,869 bytes.

## Purpose
`zfs_vnops_os.c` is the FreeBSD vnode-operation implementation for the OpenZFS ZPL. It adapts ZFS directory, file, metadata, ACL, extended-attribute, VM paging, ZIL logging, and block-cloning behavior to FreeBSD's VOP interface and vnode/page-cache rules.

## Major Responsibilities
- Implements core ZPL vnode operations: open, close, lookup, create, remove, mkdir, rmdir, readdir, getattr, setattr, rename, symlink, readlink, link, space/deallocate, inactive, fid, pathconf, fsync, access, and advise.
- Bridges FreeBSD VOP wrappers to common ZFS helpers such as `zfs_read()`, `zfs_write()`, `zfs_fsync()`, `zfs_access()`, `zfs_clone_range()`, `zfs_holey()`, `zfs_rewrite()`, and ACL/security helpers.
- Maintains mmap/page-cache coherence through `update_pages()`, `mappedread()`, `mappedread_sf()`, `zfs_getpages()`, and `zfs_putpages()`.
- Integrates ZFS transactions and ZIL logging for namespace and metadata changes using `dmu_tx_*()`, `zfs_log_create()`, `zfs_log_remove()`, `zfs_log_rename()`, `zfs_log_symlink()`, `zfs_log_link()`, `zfs_log_setattr()`, `zfs_log_write()`, and `zil_commit()`.
- Implements FreeBSD extended attributes over both ZFS SA xattrs and hidden xattr directories, including legacy compatibility naming via `zfs_xattr_compat`.
- Registers `zfs_vnodeops`, `zfs_fifoops`, and `zfs_shareops` VOP vectors.

## Key Data and Interfaces
- Uses `znode_t`, `zfsvfs_t`, and `vnode_t` as the main object, filesystem, and FreeBSD vnode state.
- Uses SA attributes (`SA_ZPL_*`) for file metadata and ZAP objects for directories and hidden xattr directories.
- Uses range locks (`z_rangelock`) around file data operations that interact with DMU writes, truncation, and page-cache I/O.
- Uses FreeBSD VM primitives: `vm_page_*`, `vm_object_*`, `vnode_pager_setsize()`, `vnode_pager_purge_range()`, and page busy/unbusy/wire handling.
- Uses FreeBSD namecache/VFS interfaces: `cache_enter()`, `vfs_cache_lookup()`, `cache_vop_rename()`, `vn_lock_pair()`, `insmntque`-compatible vnode lifecycle, and named-attribute flags on newer FreeBSD.
- Uses FreeBSD security and metadata APIs: `secpolicy_*`, `vaccess()`, `extattr_check_cred()`, `acl_from_aces()`, `aces_from_acl()`, MAC write checks, and `chflags` conversions.

## Control Flow Highlights
- The large opening comment defines the file's transaction discipline: enter ZFS, acquire needed locks and range locks before transaction assignment, use `DMU_TX_NOWAIT` when ZPL locks are held, log successful operations before dropping locks, commit all transactions, then do synchronous `zil_commit()` when required.
- `zfs_lookup()` handles ordinary lookup, xattr lookup, UTF-8 validation, `.zfs` control directory exposure, snapshot `..` behavior, dot-dot relocking, namecache positive/negative entries, and FreeBSD create/delete/rename lookup return conventions.
- `zfs_create()` and `zfs_mkdir()` validate name length, FUID/version support, ACLs, permissions, quotas, and UTF-8; reserve a vnode, create a DMU transaction, call `zfs_mknode()`, link the new object into the parent, log the create, and optionally commit synchronously.
- `zfs_remove_()` and `zfs_rmdir_()` validate delete permissions and object type, hold both directory and object state, destroy the directory link, add unlinked files to the unlinked set when needed, update namecache state, and log removal.
- `zfs_setattr()` is the central metadata mutation path. It handles size changes through `zfs_freesp()`, validates immutable/read-only/version/timestamp constraints, maps uid/gid/project IDs, updates xattr directories when ownership/project changes, updates ACLs and optional attributes, logs the setattr, and commits.
- Rename is split into relocking/revalidation and implementation. `zfs_rename_relock()` reacquires source dir, target dir, source vnode, and target vnode with deadlock avoidance. `zfs_do_rename_impl()` rechecks source/target validity, xattr-space boundaries, project inheritance, directory ancestry, target type compatibility, performs link-create/link-destroy ordering, updates AV flags, logs, and updates namecache.
- VM read/writeback paths align page operations to ZFS block sizes, avoid reading beyond object size, read only invalid pages, preserve dirty state on failed writeback, and use ZIL callbacks for synchronous page-clean completion.
- Extended attribute operations try SA-backed xattrs when available and fall back to hidden xattr directory files. User namespace lookup/list/delete also checks the alternate legacy/non-legacy name format.
- `zfs_freebsd_copy_file_range()` tries ZFS block cloning only when enabled and supported by the output pool, then falls back to `vn_generic_copy_file_range()` for unsupported, cross-dataset, unaligned, or otherwise unsuitable cases.

## Important Functions
- `zfs_lookup()` defines lookup semantics, control-directory exposure, xattr lookup, namecache behavior, and dot-dot handling.
- `zfs_create()`, `zfs_remove_()`, `zfs_mkdir()`, `zfs_rmdir_()`, `zfs_do_rename_impl()`, `zfs_symlink()`, and `zfs_link()` implement namespace mutation.
- `zfs_getattr()` and `zfs_setattr()` implement metadata exposure and mutation, including ZFS optional attributes, FreeBSD `chflags`, ACLs, quotas, and project IDs.
- `zfs_getpages()` and `zfs_putpages()` are the main VM pager integration points.
- `zfs_getextattr()`, `zfs_setextattr()`, `zfs_deleteextattr()`, and `zfs_listextattr()` implement FreeBSD extattr compatibility.
- `zfs_freebsd_*()` wrappers bind FreeBSD VOP argument structs to ZFS internal helpers.
- `zfs_vnodeops`, `zfs_fifoops`, and `zfs_shareops` define the exported FreeBSD operation tables.

## Invariants and Assumptions
- Every normal vnode operation must guard against unmount/teardown using `zfs_enter*()` and must verify znodes before dereferencing SA state.
- `VN_RELE()` is intentionally delayed until after transactions and locks are done, because the final reference can trigger `zfs_zinactive()` and new transaction work.
- Range locks must be acquired before transaction assignment when the operation spans file data.
- ZIL logging must happen while operation ordering locks are still held.
- Xattr directory entries and regular namespace entries must not be linked or renamed across each other.
- Project inheritance forbids hard links or renames into a project-inheriting tree when project IDs differ.
- Page-cache operations assume careful coordination between VM page busy state, ZFS range locks, DMU reads/writes, and vnode object size.

## Risks and Edge Cases
- Rename has high concurrency risk because it must reorder and revalidate four vnode locks while supporting concurrent namespace changes.
- Dot-dot lookup has known race caveats around parent-child relationship changes during unlock/relock windows.
- `zfs_setattr()` combines size, ACL, ownership, project quota, xattr directory, optional attribute, and timestamp behavior; small ordering changes can affect security or accounting.
- SA xattrs and directory xattrs can both exist; compatibility fallback and cleanup paths must avoid stale duplicates.
- Page dirty-range handling depends on FreeBSD VM semantics, including DEV_BSIZE alignment and partial-page EOF behavior.
- FreeBSD-version conditionals affect named attributes, page invalidation, copy range locking, pathconf features, and namei/VOP ABI details.
- Block cloning deliberately falls back for many errors; callers must not assume clone happened just because `copy_file_range` succeeded.

## Testing Signals
Useful coverage should include:
- Lookup of ordinary names, `.`/`..`, root of snapshots, `.zfs`, missing names with negative cache, UTF-8 invalid names, and case/normalization-sensitive filesystems.
- Create/remove/mkdir/rmdir/symlink/link/rename across files, directories, existing targets, mounted directories, xattr directories, project inheritance, and quota failures.
- `setattr` for truncation/extension, uid/gid/projid changes, immutable/append/nounlink flags, birthtime, chflags, AV flags, ACL mode changes, and xattr directory propagation.
- mmap read/writeback, sendfile `UIO_NOCOPY`, partial EOF pages, synchronous putpages, writeback errors, and dirty-page preservation.
- Extattr get/set/delete/list across SA xattrs, directory xattrs, user/system namespaces, legacy compatibility names, oversized SA entries, and disabled xattr property.
- `copy_file_range` clone success, unsupported-feature fallback, cross-filesystem behavior, same-vnode range copies, and MAC/write-permission failures.

## Overall Assessment
This file is the FreeBSD-facing operational core of OpenZFS's ZPL. Its complexity is mostly in boundary management: VFS locking, VM page state, ZFS transactions, ZIL ordering, ACL/security checks, namecache semantics, and compatibility with multiple FreeBSD kernel versions. Changes here have broad user-visible filesystem semantics and should be tested with concurrent namespace, mmap, xattr, ACL, quota, and sync-write workloads.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_vnops_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_znode_os.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_znode_os.c -->