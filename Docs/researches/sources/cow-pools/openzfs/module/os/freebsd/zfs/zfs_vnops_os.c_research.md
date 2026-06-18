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
