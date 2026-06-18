# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsInode.c

## Purpose
`FhgfsOpsInode.c` implements BeeGFS inode operations for the Linux VFS: lookup, getattr/setattr, xattrs, ACLs, mkdir/create/mknod/symlink/link/unlink/rmdir/rename, symlink following, truncate, inode allocation/destruction, inode instantiation, and remote-stat based cache revalidation. It is the primary bridge between kernel inode/dentry semantics and BeeGFS metadata-server RPCs.

## Important APIs, Types, And Functions
- `maybeRefreshInode()` refreshes inode attributes when the root is not initialized, the BeeGFS inode cache is invalid, or a forced stat is requested.
- `FhgfsOps_lookupIntent()`, `FhgfsOps_createIntent()`, and `FhgfsOps_atomicOpen()` use BeeGFS lookup-intent RPCs to combine lookup/create/stat/open.
- `FhgfsOps_getattr()` fills `kstat` after optional refresh and handles root inode numbering and 32-bit inode overflow mitigation.
- `FhgfsOps_setattr()` handles chmod/chown/utime/truncate, flushes dirty data for regular files, remotes attribute changes, updates ACLs, and performs remote truncation.
- Xattr and ACL APIs include `FhgfsOps_listxattr()`, `FhgfsOps_getxattr()`, `FhgfsOps_setxattr()`, `FhgfsOps_removexattrInode()`, `Fhgfs_get_acl()`, and `FhgfsOps_set_acl()`.
- Namespace mutation APIs include `FhgfsOps_mkdir()`, `FhgfsOps_rmdir()`, `FhgfsOps_mknod()`, `FhgfsOps_symlink()`, `FhgfsOps_link()`, `FhgfsOps_hardlinkAsSymlink()`, `FhgfsOps_unlink()`, and `FhgfsOps_rename()`.
- Inode lifecycle APIs include `FhgfsOps_initInodeCache()`, `FhgfsOps_alloc_inode()`, `FhgfsOps_destroy_inode()`, `__FhgfsOps_newInodeWithParentID()`, and `__FhgfsOps_instantiateInode()`.
- Refresh/cache APIs include `__FhgfsOps_flushInodeFileCache()`, `__FhgfsOps_doRefreshInode()`, and `__FhgfsOps_revalidateMapping()`.

## Control Flow
Lookup initializes dentry validation time, refreshes the parent/root if required, then either handles root specially or performs `FhgfsOpsRemoting_lookupIntent()` under the parent entry-info read lock. Successful lookup converts BeeGFS stat data into a `kstat`, generates a stable inode number from the entry ID, creates or reuses an inode through `iget5_locked()`, and attaches it with directory-specific `d_materialise_unique()` or `d_splice_alias()`.

Create/open paths build `LookupIntentInfoIn` with optional `CreateInfo` and `OpenInfo`. They check name length and type, lock parent entry info during the combined RPC, validate create/stat/open results, instantiate the inode, and when an open handle was returned attach it to the file via `FhgfsOps_openReferenceHandle()`. Error paths close server-side handles that were opened before local setup completed.

Setattr first performs kernel permission checks (`setattr_prepare()` or `inode_change_ok()`), ignores redundant open-time truncation, flushes page cache and buffered file cache for regular files, converts `iattr` into BeeGFS attributes, sends remote setattr with optional event logging, applies local attributes, updates ACLs for chmod, and issues remote truncate plus local `FhgfsOps_vmtruncate()` when size changes.

Namespace operations follow a repeated pattern: build `CreateInfo` or event metadata, lock the relevant parent/file entry infos in a stable order, call the remoting operation, update local dentry/inode timestamps/link counts/entry info on success, drop negative dentries on selected errors, and invalidate BeeGFS inode caches where needed. Rename takes a write lock on the renamed file's entry info to protect concurrent reference/release and then updates entry info after a successful remote rename.

Refresh flushes dirty local content unless `noFlush` is set, stats the metadata server, validates object type, applies stat fields under `i_lock`, and invalidates remote inode page state when mtime/size changed or the page-cache validity timeout expired.

## State And Persistence Behavior
Server-persistent operations include metadata creates, removes, hardlinks, symlink file creation, renames, xattr/ACL changes, setattr, truncation, and lookup/stat state. Local persistent-in-memory state includes inode cache slab objects, `EntryInfo`, `metaVersion`, parent node IDs for export reconnect, idmapped mount/user namespace pointers, generated inode numbers, link counts, timestamps, page-cache mappings, ACL caches, `dataCacheTime`, dirty-page/writeback counters, and `S_NOSEC` xattr/capability cache flags.

The code intentionally prevents some local `i_size` decreases while page writeback may still be racing, using `FhgfsIsizeHints`, writeback counters, and `lastWriteBackOrIsizeWriteTime`. Server timestamps are authoritative for normal inode timestamp state; local timestamps are updated for VFS-visible directory mutations after successful remoting.

## Dependencies And Integration Points
This file integrates with `FhgfsOpsRemoting`, `FhgfsInode`, `FhgfsOpsFile`, `FhgfsOpsFileNative`, `FhgfsOpsDir`, `FhgfsOpsSuper`, `FhgfsXAttrHandlers`, `OsTypeConv`, `CreateInfo`, `LookupIntentInfo`, `OpenInfo`, `FileEvent`, POSIX ACL helpers, Linux dentry/inode/page-cache APIs, idmapped/user namespace APIs, and configuration options controlling cache mode, ACL/xattr revalidation, hardlink-as-symlink behavior, event logging, and EBUSY-to-EXDEV rename mapping.

## Risks
- `FhgfsOps_createIntent()` has an early `return -EINVAL` inside a parent entry-info lock when `createMode` is not regular; that path is worth auditing for lock release in the active build configuration.
- Lock ordering is critical for link and rename paths because multiple directory and file entry-info locks are taken.
- `FhgfsOps_hardlinkAsSymlink()` has error handling around path resolution; wrong `IS_ERR`/`PTR_ERR` handling could report incorrect errors.
- Inode refresh and page-cache invalidation race with writeback; the no-decrease logic is complex and requires regression coverage.
- ACL/xattr caching with `inode_has_no_xattr()` and `forget_all_cached_acls()` depends on configuration and kernel security semantics.
- Atomic-open is conditionally enabled and has non-trivial cleanup paths for successful lookup but failed open/reference setup.

## Test Signals
High-value coverage includes lookup/create/open races, NFS/disconnected dentry aliasing, chmod with ACL updates, truncation while writeback is active, xattr/capability cache modes, SELinux xattr initialization, hardlink and hardlink-as-symlink modes, rename across directories, stale cache invalidation after remote modification, 32-bit stat inode behavior, and fault injection for remoting success with local open-handle setup failure.
