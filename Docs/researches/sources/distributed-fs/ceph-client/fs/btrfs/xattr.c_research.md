# sources/distributed-fs/ceph-client/fs/btrfs/xattr.c

## Purpose

`xattr.c` implements Btrfs extended attribute operations and VFS xattr handlers. It stores xattrs as `BTRFS_XATTR_ITEM_KEY` dir-item payloads in the inode root, supports get/set/remove/list operations, wires security/trusted/user/Btrfs-property namespaces into the VFS, and initializes security xattrs during inode creation.

## Important APIs, Types, And Functions

`btrfs_getxattr()` allocates a path, looks up the named xattr with `btrfs_lookup_xattr()`, returns the size for zero-length probes, validates the caller buffer, and reads the packed dir-item data from the leaf.

`btrfs_setxattr()` is the low-level transaction-aware mutation helper. It enforces `BTRFS_MAX_XATTR_SIZE()`, handles remove when `value == NULL`, respects `XATTR_REPLACE` and `XATTR_CREATE`, inserts with `btrfs_insert_xattr_item()`, and performs atomic replacement for existing packed dir-items by extending, truncating, or deleting/re-extending the item as needed. On success it sets `BTRFS_INODE_COPY_EVERYTHING` and clears `BTRFS_INODE_NO_XATTRS`.

`btrfs_setxattr_trans()` wraps `btrfs_setxattr()` in a transaction unless the caller already has `current->journal_info`. The existing-transaction path exists for security hooks such as Smack during directory creation. After a successful mutation it increments inode version, updates ctime, writes the inode item, and aborts the transaction on update failure.

`btrfs_listxattr()` walks all xattr items for the inode with `btrfs_for_each_slot()`, iterates packed `struct btrfs_dir_item` records inside each leaf item, accounts names plus NUL terminators, and copies names to the VFS buffer or returns the required size.

Handler functions translate VFS namespace-relative names through `xattr_full_name()`. Security handlers maintain a negative cache bit for `security.capability` (`BTRFS_INODE_NO_CAP_XATTR`). Property handlers validate and route `btrfs.*` xattrs through `btrfs_validate_prop()`, `btrfs_ignore_prop()`, and `btrfs_set_prop()`. `btrfs_initxattrs()` receives LSM-provided security xattrs, prepends `security.`, and sets each under `memalloc_nofs_save()`. `btrfs_xattr_security_init()` exposes this to inode creation through `security_inode_init_security()`.

## Control Flow And Integration

Reads are path lookup plus leaf-buffer copy. Mutations start from VFS handlers, reject readonly roots, assemble full names, and enter `btrfs_setxattr_trans()` or property-specific transaction code. The low-level set path first resolves remove/replace/create semantics, then either inserts a new dir item or atomically updates an existing record in-place or by replacing only that packed name. Successful mutations update inode metadata and transaction state.

The xattr list path scans from `(ino, BTRFS_XATTR_ITEM_KEY, 0)` forward and stops when objectid or item type leaves the inode's xattr range. Security initialization integrates with LSM inode hooks and uses an existing transaction from create/mkdir code.

## State And Persistence Behavior

Xattrs persist in the Btrfs tree as dir-item records under the inode number and `BTRFS_XATTR_ITEM_KEY`. Multiple xattrs may be packed into a single leaf item, so replacement must preserve visibility of either old or new values and avoid transient missing ACL/security values. Inode ctime and i_version are updated for set/remove operations. Runtime flags cache absence of xattrs or capabilities but are corrected on successful mutations.

## Dependencies

The file depends on Linux VFS xattr, LSM security, POSIX ACL xattr constants, inode versioning, and memory allocation contexts. Btrfs dependencies include tree paths, dir-item helpers, transactions, inode update, root readonly checks, property validation, locking assertions, extent-buffer accessors, and disk IO.

## Risks And Edge Cases

Packed dir-item updates are high risk: item size, name length, data length, and slot position must stay coherent after truncate/extend/delete. `XATTR_REPLACE` relies on inode locking to avoid races with concurrent delete. `value == NULL` means remove, while a zero-length non-NULL value means an empty xattr. Buffer sizing must return `-ERANGE` without partial semantic corruption. Security capability negative caching must be cleared when setting capabilities. Property xattrs have separate validation and may be ignored without persistence.

## Test Signals

Test with `getfattr`/`setfattr` for user, trusted, security, ACL, and `btrfs.*` properties; create-only, replace-only, remove, empty-value, and oversized xattrs; list buffer size probes and small-buffer `-ERANGE`; concurrent set/remove under inode locking; readonly subvolume rejection; LSM security initialization during file and directory creation; capability xattr negative-cache behavior; and fsync/send behavior that depends on `BTRFS_INODE_COPY_EVERYTHING`.
