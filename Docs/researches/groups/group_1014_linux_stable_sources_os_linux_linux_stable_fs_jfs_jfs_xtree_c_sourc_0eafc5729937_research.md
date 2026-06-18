# Group Research: group_1014_linux_stable_sources_os_linux_linux_stable_fs_jfs_jfs_xtree_c_sourc_0eafc5729937

Scope: `Docs/research_subset_a.md`

This grouped report covers the requested Linux stable JFS extent/name/xattr/mount paths, the generic `kernel_read_file` helper, and the kernfs directory implementation. Each source file below was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_xtree.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_xtree.c

## Purpose

Implements the JFS extent allocation descriptor B+tree, called the xtree. It maps logical file block ranges to physical extents, mutates those mappings for file growth, recorded writes, appends, and truncation, and integrates those changes with JFS transaction logging, quotas, metapages, and allocation maps.

## Main Structures And Helpers

- `struct xtsplit` carries an insertion/split candidate while propagating page splits up the tree.
- `XT_CMP()` compares a logical block offset against an extent entry.
- `XT_PUTENTRY()` writes XAD flag, offset, length, and address fields.
- `xt_getpage()` wraps the JFS btree page fetch and performs structural sanity checks on `nextindex`, `maxentry`, and root/page capacity before returning an xtree page.

## Key Operations

- `xtLookup()` resolves a logical block range to a physical block range, returning holes with `*paddr = 0` and limiting `*plen` to the next extent or requested length.
- `xtSearch()` walks from the inline root down to a leaf, builds a `btstack`, and pins the found leaf. It has a sequential access fast path using `JFS_IP(ip)->btorder` and `btindex`, then falls back to binary search per xtree page.
- `xtInsert()` inserts a new extent, optionally allocating data blocks and charging quota. It rejects overlaps via `cmp` and `next`, marks new entries `XAD_NEW`, and either shifts a non-full leaf or delegates to `xtSplitUp()`.
- `xtSplitUp()`, `xtSplitPage()`, and `xtSplitRoot()` split full leaves/internal pages, allocate new index pages, update sibling pointers, create router entries, and propagate split keys upward. Root splits copy the inline root into a real child page and convert the inline root to an internal page.
- `xtExtend()` extends the previous extent in place when contiguous and splits into an additional XAD if the length exceeds `MAXXLEN`.
- `xtUpdate()` converts an allocated-but-not-recorded extent into a recorded one. It handles replacement, left/right coalescing, and two- or three-way splitting of an existing XAD.
- `xtAppend()` is optimized for append-mode growth, including bottom-up allocation for data and potential xtree index pages.
- `xtInitRoot()` initializes an inline xtree root in the inode, using fewer initial slots for non-directories to leave room for inline EA.
- `xtTruncate()` truncates xtree/data extents and index pages from the right side of the tree, with separate behavior for persistent/working map update modes. It limits a single transaction to `MAX_TRUNCATE_LEAVES` to avoid exhausting metapages and tlocks.
- `xtTruncate_pmap()` logs persistent-map freeing for zero-link files while leaving the working map and xtree available for open file handles.
- `jfs_xtstat_proc_show()` exposes search/split counters when `CONFIG_JFS_STATISTICS` is enabled.

## Locking, Transactions, And Lifetime

Metapages returned by xtree search/split paths are pinned until explicitly released with `XT_PUTPAGE()`. Mutations mark metapages dirty and generally acquire `txLock()` records unless the inode is marked `COMMIT_Nolink`. Quota charging happens before block allocation for new data/index extents and is rolled back on allocation/split failures where possible. Truncation uses transaction lock types such as `tlckTRUNCATE`, `tlckFREE`, and map locks to defer or perform block freeing according to commit mode.

## Error Handling And Integrity Notes

The file treats corrupt tree shape as filesystem corruption via `jfs_error()` and returns `-EIO`. Stack overflow in tree descent is guarded with `BT_STACK_FULL()`. Split paths have several pinned-page transfer points; correct `XT_PUTPAGE()` pairing is central to safety. The `xtSplitUp()` return path maps some split failures to `-EIO`, so callers lose the original error in one branch. Truncation intentionally may return a nonzero new size to signal the caller to continue in another transaction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_xtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_xtree.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_xtree.h

## Purpose

Defines the on-disk/in-memory extent allocation descriptor types and public xtree APIs used by JFS file mapping, growth, update, append, and truncation code.

## Main Definitions

- `xad_t` is a 16-byte extent descriptor with flags, a 40-bit logical offset split across `off1/off2`, and a `pxd_t` physical location/length.
- `MAXXLEN` caps an XAD length at 24 bits.
- `XADoffset`, `XADaddress`, and `XADlength` construct descriptor fields; `offsetXAD`, `addressXAD`, and `lengthXAD` extract them.
- XAD flags include `XAD_NEW`, `XAD_EXTENDED`, `XAD_COMPRESSED`, `XAD_NOTRECORDED`, and `XAD_COW`.
- Root/page sizing constants define inline root capacities, page capacity, and `XTENTRYSTART == 2`.
- `struct xtheader`, `xtroot_t`, and `xtpage_t` define xtree page headers and arrays.

## Exported Surface

The header declares `xtLookup`, `xtInitRoot`, `xtInsert`, `xtExtend`, `xtUpdate`, `xtTruncate`, `xtTruncate_pmap`, and `xtAppend`. These are the primary xtree services used by JFS inode, write, symlink, resize, and removal paths.

## Notes

The field macros encode endian and bit-width assumptions directly. Callers must pass filesystem-block units, not bytes, for offsets, addresses, and lengths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_xtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/namei.c

## Purpose

Implements JFS directory inode operations: create, mkdir, rmdir, unlink, link, symlink, rename, mknod, lookup, NFS export helpers, and case-insensitive dentry operations for OS/2-style mounts.

## Main Operation Patterns

- Creation paths (`jfs_create`, `jfs_mkdir`, `jfs_mknod`, `jfs_symlink`) initialize quota, convert dentries to JFS Unicode names, allocate the inode before directory search to avoid blocking while holding pinned dtree pages, start a transaction, lock parent/child commit mutexes, initialize ACL/security state, insert a dtree entry, set inode ops, mark dirty inodes, and commit.
- `jfs_rmdir()` validates directory emptiness with `dtEmpty()`, deletes the parent dtree entry, adjusts parent link count, clears EA/ACL extents through `txEA()`, clears target nlink, and commits deletion.
- `jfs_unlink()` deletes a directory entry and decrements the target link count. If the link count reaches zero, `commitZeroLink()` frees persistent resources and may require repeated `xtTruncate_pmap()` transactions after commit.
- `jfs_link()` inserts another dtree reference and increments the target nlink, rejecting read-only inodes.
- `jfs_symlink()` stores small symlink targets inline as fast symlinks, while larger targets are stored in one xtree-backed extent written through metapages.
- `jfs_rename()` supports only `RENAME_NOREPLACE` among flags. It verifies both source and destination dtree state before transaction work, handles replacement victim deletion/truncation, updates directory parent `..` metadata when moving directories, and commits all changed inodes.
- `jfs_lookup()` searches the directory dtree and returns `d_splice_alias()` around `jfs_iget()`.

## Zero-Link Resource Handling

`commitZeroLink()` handles regular files and non-fast symlinks by marking the transaction `COMMIT_PMAP`, logging EA/ACL extent frees, and calling `xtTruncate_pmap()`. `jfs_free_zero_link()` later frees EA/ACL/data resources from the working map and cache once the unlinked open file is finally released.

## VFS Exports

`jfs_dir_inode_operations` wires standard directory methods plus xattrs, setattr, fileattr, and POSIX ACL hooks. `jfs_dir_operations` wires read, iterate, fsync, ioctl, llseek, and leases. Export helpers use generic file-handle decode with inode generation validation and directory parent lookup via `i_dtroot.header.idotdot`.

## Case-Insensitive Dentries

`jfs_ci_hash()` and `jfs_ci_compare()` fold ASCII bytes with `tolower()`. `jfs_ci_revalidate()` keeps positive dentries valid but drops negative dentries for create/rename-target intents so the user-supplied case is used.

## Locking And Error Notes

The code relies on VFS inode locking plus JFS `commit_mutex` nesting classes. Paths that modify file data on zero-link deletion also take `IWRITE_LOCK`. Directory index truncation may be incomplete and is retried when `COMMIT_Stale` is observed. Several paths abort transactions differently for `-EIO` versus expected allocation/full errors, with `-EIO` marking the filesystem dirty.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/resize.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/resize.c

## Purpose

Implements online JFS filesystem growth through `jfs_extendfs()`. It recalculates filesystem, fsck workspace, and inline log layout for a larger logical volume, extends allocation maps, optionally moves the inline log, and finalizes the new geometry in the superblocks.

## Main Flow

- Determines the old logical-volume end from inline log or fsck workspace descriptors and returns early if the volume did not grow.
- Validates the requested size against the block device or by probing the last requested block.
- Rejects growth on a read-only filesystem.
- Computes a new inline log size/address when applicable, computes fsck workspace size/address, and derives the new filesystem size. Shrinking is rejected.
- Formats a non-overlapping new inline log early when possible.
- Calls `txQuiesce()` before moving active log structures or updating allocation maps.
- If using inline log, shuts down the old log, marks `FM_EXTENDFS` in the on-disk superblock, stores transitional descriptors, formats and initializes the new log.
- Extends the block map with `dbExtendFS()`, grows the bmap file with `xtAppend()` if more dmap pages are needed, and finalizes via `dbFinalizeBmap()`.
- Extends/syncs the inode allocation map with `diExtendFS()` and `diSync()` when allocation-group sizing changed.
- Writes bmap state, copies the primary bmap inode to the secondary, updates primary and secondary superblocks, clears `FM_EXTENDFS`, and resumes transactions.

## Crash Recovery Model

The code uses `FM_EXTENDFS` and staged superblock descriptor updates so recovery/fsck can distinguish pre-extension, in-progress extension, and post-extension states. Comments state that logredo can reconstruct pre-extension bmap file state by ignoring bmap growth outside the prior `s_size` boundary.

## Important Dependencies

This path depends on bmap/dmap functions, imap growth, log manager operations, special inode read/write helpers, synchronous buffer writes, and xtree append support for bmap file growth.

## Notes

The function is growth-only and assumes no shrink. It updates the direct inode size after quiescing to match the block device. Error paths call `jfs_error()` after quiesce and always resume transactions before returning.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/resize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/super.c

## Purpose

Provides the JFS filesystem type integration: module setup/teardown, superblock operations, mount option parsing via `fs_context`, remount/reconfigure handling, freeze/unfreeze, quota file I/O, statfs, export ops, and inode-cache lifecycle.

## Mount And Context Handling

- `jfs_param_spec` accepts integrity/nointegrity, `iocharset`, remount-only `resize`, error behavior, quota options, uid/gid/umask, and discard settings.
- `jfs_parse_param()` updates a private `jfs_context`, loading/unloading NLS tables as needed.
- `jfs_init_options()` seeds defaults, with `errors=remount-ro` as the default behavior for new mounts.
- `jfs_fill_super()` allocates `jfs_sb_info`, sets VFS operations and xattr handlers, creates the direct-mapping inode for metadata I/O, mounts the aggregate, optionally mounts read-write/log state, obtains the root inode, and sets maxbytes/time granularity.
- `jfs_reconfigure()` applies parsed options, handles online resize, transitions read-only/read-write state, and remounts the log path if integrity mode changes.

## Super Operations

`jfs_super_operations` includes inode allocation/free, dirty/write/evict inode hooks, `put_super`, `sync_fs`, freeze/unfreeze, `statfs`, option display, and quota hooks when configured. `jfs_statfs()` reports block counts from the bmap and estimates inode capacity from current inode map plus available blocks.

## Error And Freeze Behavior

`jfs_error()` logs the caller and message, marks the superblock dirty through `updateSuper(FM_DIRTY)`, and then either panics, remounts read-only, or continues according to mount flags. Freeze quiesces transactions, shuts down the log, and marks the superblock clean; unfreeze marks mounted, reinitializes the log, and resumes transactions.

## Quota Support

Quota reads and writes bypass pagecache-level regular write paths by mapping quota-file logical blocks through `jfs_get_block()` and reading/writing buffers directly. `jfs_quota_on()` marks quota files noatime/immutable in JFS and VFS flags; `jfs_quota_off()` clears them after quota shutdown.

## Module Lifecycle

`init_jfs_fs()` creates the inode cache with usercopy bounds for inline inode data, initializes metapages and the transaction manager, starts the JFS I/O, commit, and sync kernel threads, initializes proc entries when enabled, and registers the filesystem. Exit reverses this sequence and runs `rcu_barrier()` before destroying the inode cache.

## Notes

The direct inode is fake-hashed and uses `jfs_metapage_aops` for aggregate metadata access. Discard is disabled at mount if the block device reports no discard support. JFS export operations use generic 32-bit inode file handles plus JFS parent lookup from `namei.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/symlink.c

## Purpose

Defines inode operation tables for JFS symbolic links.

## Operations

- `jfs_fast_symlink_inode_operations` uses `simple_get_link` for inline symlink targets stored in the inode.
- `jfs_symlink_inode_operations` uses `page_get_link` for symlink targets stored in file data pages.
- Both variants share `jfs_setattr` and `jfs_listxattr`.

## Notes

Creation and storage selection are implemented in `namei.c`; this file only exposes the VFS operation vectors consumed by that code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/xattr.c

## Purpose

Implements JFS extended attributes: FEALIST parsing, inline/extent storage, namespace mapping, get/set/list operations, VFS xattr handlers, and security xattr initialization.

## Data Format And Storage

JFS stores a `struct jfs_ea_list` containing a 32-bit total size and a packed sequence of `struct jfs_ea` entries. Each entry contains flags, name length, 16-bit value length, a NUL-terminated name, and value bytes. Attribute lists may live inline in the inode (`DXD_INLINE`) or in allocated extents (`DXD_EXTENT`) accessed through metapages.

## Namespace Mapping

Unknown on-disk prefixes are presented to userspace with the `os2.` prefix. Known namespaces are `system.`, `user.`, `security.`, and `trusted.`. The OS/2 xattr handler rejects known namespace names so it only covers legacy/unknown names.

## Core Helpers

- `ea_write_inline()` writes a small or empty list into inode inline EA space when available and updates the DXD descriptor.
- `ea_write()` chooses inline storage or allocates blocks with quota charging and `dbAlloc()`, writes metapages synchronously, and fills the new DXD.
- `ea_read_inline()` and `ea_read()` load an EA list from inode inline data or extent metapages.
- `ea_get()` returns a mutable buffer for current EAs, allocating a larger inline/extent/kmalloc buffer when the caller needs room for updates. It validates the list size and dumps bad EA contents before returning `-EIO`.
- `ea_release()` releases or rolls back buffers, including freeing newly allocated extent blocks if the update is abandoned.
- `ea_put()` commits a new EA descriptor through `txEA()`, invalidates old extent metapages, frees old quota blocks, updates inode ctime, and frees inline space when appropriate.

## Public Operations

- `__jfs_setxattr()` serializes with `xattr_sem`, reads current EAs, enforces create/replace semantics, removes an existing matching entry, validates that values fit in the on-disk 16-bit field, appends the new entry, and calls `ea_put()`.
- `__jfs_getxattr()` serializes with `xattr_sem`, walks the FEALIST with corruption bounds checks, and returns the value size or bytes.
- `jfs_listxattr()` lists names, hiding `trusted.*` without `CAP_SYS_ADMIN` and applying the OS/2 prefix mapping.
- `__jfs_xattr_set()` wraps setxattr in a JFS transaction and inode `commit_mutex`.
- Handler tables wire `user`, `os2`, `security`, and `trusted` namespaces into VFS xattr dispatch.
- With `CONFIG_JFS_SECURITY`, `jfs_init_security()` stores LSM-provided security xattrs during inode creation using the existing transaction.

## Notes

The implementation carefully separates allocated-but-uncommitted EA buffers from existing committed EA storage. Value length is rejected at `>= USHRT_MAX` to avoid overflowing the on-disk 16-bit length. Extent allocation failure paths roll back quota and block allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernel_read_file.c -->
# File Research: sources/os/linux/linux-stable/fs/kernel_read_file.c

## Purpose

Provides generic helpers for reading a regular file into a kernel buffer, with Linux Security Module hooks before and after reading. Used by kernel subsystems that need to load firmware, policies, certificates, or other file-backed blobs.

## Main Function

`kernel_read_file()` validates partial-read rules, requires a regular file, denies concurrent write access with `deny_write_access()`, checks file size bounds, asks LSMs through `security_kernel_read_file()`, allocates a `vmalloc()` buffer if needed, reads with `kernel_read()` until the requested buffer is filled or EOF, and calls `security_kernel_post_read_file()` for whole-file reads.

## Wrapper APIs

- `kernel_read_file_from_path()` opens a path from the caller's namespace and reads it.
- `kernel_read_file_from_path_initns()` opens relative to the init task root.
- `kernel_read_file_from_fd()` validates an fd has `FMODE_READ` and reads from it.

## Error And Lifetime Notes

The function rejects empty/nonpositive files, files larger than `SSIZE_MAX`, whole-file reads whose buffer is too small, and invalid offset/buffer combinations. On error after internal allocation, it frees the buffer and nulls the caller pointer. `allow_write_access()` is always called before return after a successful deny.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernel_read_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/kernfs/Kconfig

## Purpose

Defines the internal `KERNFS` configuration symbol.

## Behavior

`KERNFS` is a boolean symbol with default `n`. The comment states it should be selected by users rather than enabled directly, matching kernfs being infrastructure for pseudo-filesystems such as sysfs/cgroupfs rather than a standalone user option.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/kernfs/Makefile

## Purpose

Builds kernfs core objects into the kernel when the directory is included.

## Objects

`obj-y` includes `mount.o`, `inode.o`, `dir.o`, `file.o`, and `symlink.o`. The researched `dir.c` is one component of the kernfs pseudo-filesystem implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/kernfs/dir.c

## Purpose

Implements kernfs directory hierarchy management: node naming/path generation, sibling indexing, active reference draining, node allocation/freeing, lookup, directory creation/removal/rename, activation/show-hide, recursive removal, self-removal, and readdir.

## Naming And Paths

- `kernfs_name()` returns a node name or `/` for root.
- `kernfs_path_from_node_locked()` constructs a path from one kernfs node to another, including relative `..` components when needed.
- `kernfs_path_from_node()` uses RCU and, unless the root has invariant parents, `kernfs_rename_lock` to stabilize parent traversal.
- `pr_cont_kernfs_name()` and `pr_cont_kernfs_path()` use a private spinlock and buffer to avoid using the global rename lock in `pr_cont()` paths.

## Tree Indexing And Lookup

Siblings are stored in an rbtree ordered by a 31-bit hash, namespace id, and name. Namespace ids use `ns_common->ns_id` instead of raw namespace pointers to avoid leaking kernel addresses. `kernfs_link_sibling()` inserts nodes, updates subdirectory counts and parent revision; `kernfs_unlink_sibling()` reverses this. Lookup helpers include `kernfs_find_ns()`, `kernfs_find_and_get_ns()`, `kernfs_walk_ns()`, and `kernfs_walk_and_get_ns()`.

## References, Activity, And Draining

- `kernfs_get()` and `kernfs_put()` manage lifetime references. Final put frees symlink target refs, xattrs, idr entries, node memory via RCU, and eventually the root.
- `kernfs_get_active()` increments the active count only if the node is not deactivated; `kernfs_put_active()` decrements and wakes waiters when deactivation completes.
- `kernfs_drain()` temporarily drops `kernfs_rwsem`, waits for active users to leave, optionally drains open files/mmaps, and reacquires locks. It is central to safe removal and hiding.

## Node Creation And Root Lifecycle

- `__kernfs_new_node()` allocates the name and node, assigns a cyclic id from the root idr, initializes ref/active state, optionally applies uid/gid iattrs, and invokes `security_kernfs_init_security()`.
- `kernfs_new_node()` handles setgid inheritance and parent reference setup.
- `kernfs_create_root()` creates a kernfs root, initializes locks/lists/idr/waitqueue, allocates the root node, and activates it unless create-deactivated mode is requested.
- `kernfs_destroy_root()` removes the root subtree and drops the root reference.
- `kernfs_create_dir_ns()` and `kernfs_create_empty_dir()` create normal and permanently empty directories.
- `kernfs_add_one()` validates namespace expectations, parent type, and removing/empty state, links the node, updates timestamps, and activates it unless the root requires explicit activation.

## VFS Directory Operations

- `kernfs_dop_revalidate()` validates positive and negative dentries against parent revision, node active state, parent identity, name, and namespace.
- `kernfs_iop_lookup()` performs namespace-aware lookup, hides inactive nodes from VFS, gets an inode for active nodes, and records parent revision on dentries.
- `kernfs_iop_mkdir()`, `kernfs_iop_rmdir()`, and `kernfs_iop_rename()` delegate to optional `kernfs_syscall_ops` callbacks while holding active references on involved nodes.
- `kernfs_dir_iops` exposes lookup, permission, setattr, getattr, listxattr, mkdir, rmdir, and rename.
- `kernfs_fop_readdir()` emits dot entries, then iterates active children in namespace/hash order using the directory position as the child hash. `file->private_data` pins the current position across calls, released by `kernfs_dir_fop_release()`.

## Activation, Hiding, And Removal

- `kernfs_activate()` walks a subtree post-order and activates nodes that were created deactivated.
- `kernfs_show()` hides or shows non-directory nodes by toggling `KERNFS_HIDDEN`; hiding deactivates and drains the node.
- `__kernfs_remove()` marks a subtree `KERNFS_REMOVING`, deactivates descendants, drains and unlinks each leftmost descendant, clears inode link counts across mounted supers, updates parent timestamps, and drops references.
- `kernfs_remove()` wraps recursive removal with `kernfs_supers_rwsem` and `kernfs_rwsem`.
- `kernfs_remove_by_name_ns()` resolves a child by name/namespace and removes it if present.
- `kernfs_remove_self()` lets a kernfs operation remove its own node by temporarily breaking active protection, arbitrating with `KERNFS_SUICIDAL/KERNFS_SUICIDED`, and making concurrent callers wait for full completion.

## Rename Semantics

`kernfs_rename_ns()` rejects root moves, inactive targets, inactive destination parents, and moves into empty directories. It optionally enforces invariant-parent roots, checks destination collisions, RCU-replaces the name if changed, updates parent under `kernfs_rename_lock` when moving across parents, recomputes the hash, relinks into the destination sibling tree, and RCU-frees the old dynamic name.

## Locking Notes

The file uses `kernfs_rwsem` for structural tree changes, `kernfs_iattr_rwsem` for iattrs/revisions/subdir counts, `kernfs_supers_rwsem` when touching mounted superblocks/inodes, `kernfs_rename_lock` for parent pointer stability, RCU for names and parent reads, and active references to keep callbacks/removal from racing. Many helpers assert the expected lock state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/dir.c -->