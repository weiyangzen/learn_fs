# Group Research: group_769_linux_sources_os_linux_linux_fs_jffs2_xattr_c_sources_os_linux_linux_02a4e258c7e4

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

This group covers JFFS2 extended attribute storage and a slice of JFS VFS, inode, allocation-map, discard, ACL, debug, and build metadata. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/xattr.c -->
# File Research: sources/os/linux/linux/fs/jffs2/xattr.c

## Purpose
Implements the JFFS2 extended-attribute subsystem: xattr datum caching, xattr reference nodes, mount-time reconstruction, VFS get/set/list operations, and garbage-collection support for xattr flash nodes.

## Main Concepts
- `jffs2_xattr_datum` represents a unique xattr name/value payload stored in a raw `JFFS2_NODETYPE_XATTR` flash node.
- `jffs2_xattr_ref` links an inode cache to an xattr datum through raw `JFFS2_NODETYPE_XREF` nodes.
- Datums are hash-indexed by prefix/name/value so identical xattrs can be shared by multiple refs.
- Refs are sequence-numbered; the low bit is `XREF_DELETE_MARKER`, so newer ref/delete records win during mount reconstruction.
- `c->xattr_sem` protects logical xattr structures; `c->erase_completion_lock` protects raw-node chains and dead lists.

## Key Functions
- `xattr_datum_hashkey()` combines CRC32 of prefix/name and prefix/value for the datum cache key.
- `do_verify_xattr_datum()` reads a raw xattr node header from flash, validates node CRC, magic, nodetype, length, xid, and version, then converts unchecked raw refs to usable refs.
- `do_load_xattr_datum()` reads name/value bytes, validates `data_crc`, installs `xname`/`xvalue`, inserts the datum into `c->xattrindex`, and may trigger cache reclamation.
- `load_xattr_datum()` verifies unchecked datums before loading full value data.
- `save_xattr_datum()` writes a raw xattr node, increments `xd->version`, sets CRC fields, and registers a pristine physical node ref.
- `create_xattr_datum()` reuses an equivalent cached datum or creates/writes a new one with a fresh xid.
- `unrefer_xattr_datum()` decrements refcount, unloads cached data, marks dead datums, and places reclaimable nodes on `xattr_dead_list`.
- `verify_xattr_ref()` reads raw xref nodes during build, validates CRC/type/length, loads inode/xid/sequence data, and marks unchecked raw refs usable.
- `save_xattr_ref()` writes normal or delete-marker xref nodes and advances `highest_xseqno` by two.
- `create_xattr_ref()` writes a new xref and chains it onto `ic->xref`.
- `delete_xattr_ref()` marks a ref dead, records ino/xid for delete-node persistence, moves it to `xref_dead_list`, and unreferences the datum.
- `check_xattr_ref_inode()` lazily loads refs for an inode, removes corrupt datums, and resolves duplicate prefix/name refs by keeping the newest xseqno.
- `jffs2_build_xattr_subsystem()` reconstructs all xattr state after scanning in three phases: merge duplicate xrefs, bind live refs to inode caches and datums, and classify unchecked/orphan datums.
- `jffs2_setup_xattr_datum()` is the scanner-side insertion path for discovered xattr datums.
- `jffs2_listxattr()`, `do_jffs2_getxattr()`, and `do_jffs2_setxattr()` implement VFS-visible list/get/set semantics.
- `jffs2_garbage_collect_xattr_datum()` and `jffs2_garbage_collect_xattr_ref()` rewrite live xattr/xref nodes during GC.
- `jffs2_verify_xattr()` forces verification of unchecked datums before GC can safely reclaim related blocks.
- `jffs2_release_xattr_datum()` and `jffs2_release_xattr_ref()` free dead in-memory objects once their raw-node chains have been fully reclaimed.

## VFS Behavior
- `jffs2_xattr_handlers[]` exports user, optional security, and trusted handlers.
- `jffs2_xattr_prefix()` maps on-flash JFFS2 xattr prefixes to Linux handler prefixes and suppresses entries the caller is not allowed to list.
- `listxattr` and `getxattr` first call `check_xattr_ref_inode()` to normalize duplicate refs and purge corrupt refs.
- Read-side get/list can upgrade from `down_read()` to `down_write()` when a datum must be loaded or a corrupt ref must be removed.
- `setxattr` reserves flash space for the xattr datum first, writes/reuses a datum, then reserves/writes the xref. Replacing an existing xattr writes a new ref and deletes the old ref only after the new ref succeeds.
- Removing an xattr is encoded by writing a delete-marker xref before moving the old ref to the dead list.

## Mount and Corruption Handling
- Mount build deduplicates multiple refs for the same `(ino, xid)` by keeping the highest sequence and chaining older raw nodes behind it.
- Orphan xrefs, refs to missing/deleted inodes, refs to missing datums, and explicit delete markers are moved to `xref_dead_list`.
- Orphan datums with zero refs are marked `JFFS2_XFLAGS_DEAD` and left for verification/GC.
- CRC or structural validation failures mark datums invalid and cause callers to delete related refs when possible.
- The file uses a convention where negative return values are retryable/recoverable I/O or allocation errors, while positive `JFFS2_XATTR_IS_CORRUPTED` indicates unrecoverable corruption requiring logical deletion.

## Dependencies
- Uses JFFS2 raw-node APIs from `nodelist.h`: flash read/write, reservation, physical node refs, obsoletion, raw ref flags, and inode caches.
- Uses Linux xattr and POSIX ACL handler infrastructure.
- Relies on `jffs2_xattr_datum` and `jffs2_xattr_ref` definitions from `xattr.h`.

## Notable Details
- Cached xattr payload memory is capped by `xdatum_mem_threshold`, defaulting to 32 KiB.
- Reclamation uses a rotating hash-bucket index and a HOT bit: first pass cools hot datums, later passes unload non-bound cold datums.
- `JFFS2_XFLAGS_BIND` temporarily protects a datum from reclamation while another datum is being loaded for comparison.
- `save_xattr_ref()` assumes live refs have valid `ic` and `xd`; dead refs use stored `ino` and `xid`.
- Flash reservation is explicitly completed after each datum/xref write path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/xattr.h -->
# File Research: sources/os/linux/linux/fs/jffs2/xattr.h

## Purpose
Declares JFFS2 xattr in-memory structures, state flags, helper macros, subsystem entry points, VFS xattr handlers, and no-op stubs for builds without xattr/security support.

## Main Definitions
- `JFFS2_XFLAGS_HOT`, `JFFS2_XFLAGS_BIND`, `JFFS2_XFLAGS_DEAD`, and `JFFS2_XFLAGS_INVALID` define datum cache/reclaim/corruption state.
- `struct jffs2_xattr_datum` stores raw-node chain pointer, prefix, cache-list link, refcount, xid/version, CRC/hash, name, and value.
- `struct jffs2_xattr_ref` stores raw-node chain pointer, xref sequence, inode cache or scanned inode number, xattr datum or scanned xid, and inode-local next pointer.
- `XREF_DELETE_MARKER` is the low xseqno bit used to represent deletion records.
- `is_xattr_ref_dead()` tests whether an xref sequence carries the delete marker.

## Exported Interfaces
- Subsystem lifecycle: `jffs2_init_xattr_subsystem()`, `jffs2_build_xattr_subsystem()`, `jffs2_clear_xattr_subsystem()`.
- Scan/build support: `jffs2_setup_xattr_datum()`.
- Inode lifecycle: `jffs2_xattr_do_crccheck_inode()`, `jffs2_xattr_delete_inode()`, `jffs2_xattr_free_inode()`.
- GC support: `jffs2_garbage_collect_xattr_datum()`, `jffs2_garbage_collect_xattr_ref()`, `jffs2_verify_xattr()`, release helpers.
- VFS operations: `do_jffs2_getxattr()`, `do_jffs2_setxattr()`, `jffs2_listxattr()`.
- Handler exports: `jffs2_xattr_handlers`, `jffs2_user_xattr_handler`, `jffs2_trusted_xattr_handler`, and optional security handler/init.

## Compile-Time Behavior
- Under `CONFIG_JFFS2_FS_XATTR`, all xattr interfaces are real functions.
- Without `CONFIG_JFFS2_FS_XATTR`, the subsystem lifecycle and inode hooks become no-ops, `jffs2_verify_xattr()` returns success, and VFS handler/list hooks are `NULL`.
- Under `CONFIG_JFFS2_FS_SECURITY`, security xattr initialization and handler declarations are enabled; otherwise `jffs2_init_security()` is a no-op.

## Dependencies
- Includes Linux `xattr.h` and `list.h`.
- Expects `struct jffs2_sb_info`, `struct jffs2_inode_cache`, and raw node types from surrounding JFFS2 headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/xattr_trusted.c -->
# File Research: sources/os/linux/linux/fs/jffs2/xattr_trusted.c

## Purpose
Provides the JFFS2 trusted xattr handler for the Linux xattr framework.

## Key Functions
- `jffs2_trusted_getxattr()` delegates reads to `do_jffs2_getxattr()` with `JFFS2_XPREFIX_TRUSTED`.
- `jffs2_trusted_setxattr()` delegates writes/removals to `do_jffs2_setxattr()` with `JFFS2_XPREFIX_TRUSTED`.
- `jffs2_trusted_listxattr()` only allows listing trusted attributes for callers with `CAP_SYS_ADMIN`.

## Exported Object
- `jffs2_trusted_xattr_handler` uses `XATTR_TRUSTED_PREFIX`, custom `.list`, and the trusted get/set delegates.

## Dependencies
- Includes Linux fs/xattr/JFFS2/MTD headers and JFFS2 `nodelist.h`.
- Depends on core xattr operations implemented in `xattr.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/xattr_trusted.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/xattr_user.c -->
# File Research: sources/os/linux/linux/fs/jffs2/xattr_user.c

## Purpose
Provides the JFFS2 user xattr handler for the Linux xattr framework.

## Key Functions
- `jffs2_user_getxattr()` calls `do_jffs2_getxattr()` with `JFFS2_XPREFIX_USER`.
- `jffs2_user_setxattr()` calls `do_jffs2_setxattr()` with `JFFS2_XPREFIX_USER`.

## Exported Object
- `jffs2_user_xattr_handler` uses `XATTR_USER_PREFIX` and the user get/set delegates.

## Dependencies
- Includes Linux fs/xattr/JFFS2/MTD headers and JFFS2 `nodelist.h`.
- Depends on core xattr operations implemented in `xattr.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/xattr_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/jfs/Kconfig

## Purpose
Defines Linux Kconfig options for building IBM JFS support and optional JFS features.

## Options
- `JFS_FS`: tristate main filesystem option. Selects `BUFFER_HEAD`, `NLS`, `NLS_UCS2_UTILS`, `CRC32`, and `LEGACY_DIRECT_IO`.
- `JFS_POSIX_ACL`: optional ACL support, depends on `JFS_FS`, selects `FS_POSIX_ACL`.
- `JFS_SECURITY`: optional security-label xattr support for LSMs such as SELinux.
- `JFS_DEBUG`: optional additional debugging messages.
- `JFS_STATISTICS`: optional `/proc/fs/jfs/` statistics reporting.

## User-Facing Notes
- Main help points to `Documentation/admin-guide/jfs.rst`.
- ACL help suggests disabling ACLs when unfamiliar.
- Security label help recommends disabling unless an LSM requires xattr labels.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/Makefile -->
# File Research: sources/os/linux/linux/fs/jfs/Makefile

## Purpose
Builds the Linux JFS filesystem object from its component source files.

## Build Rules
- `obj-$(CONFIG_JFS_FS) += jfs.o` builds JFS when enabled.
- `jfs-y` links core components: superblock, file/inode/namei, mount/unmount, xtree/imap/dmap/dtree, unicode, metapage, log/transaction managers, resize, xattr, ioctl, symlink, and extent code.
- `jfs-$(CONFIG_JFS_POSIX_ACL) += acl.o` includes ACL support only when configured.

## Dependencies Reflected
- `jfs_dmap.o`, `jfs_discard.o`, `inode.o`, `file.o`, `ioctl.o`, and `acl.o` in this group are part of the same `jfs.o` module.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/acl.c -->
# File Research: sources/os/linux/linux/fs/jfs/acl.c

## Purpose
Implements POSIX ACL get/set/initialization support for JFS using JFS extended attributes and the transaction manager.

## Key Functions
- `jfs_get_acl()` maps ACL type to the POSIX ACL xattr name, reads the xattr via `__jfs_getxattr()`, converts it with `posix_acl_from_xattr()`, and returns `-ECHILD` for RCU lookup.
- `__jfs_set_acl()` converts an ACL to xattr bytes with `posix_acl_to_xattr()`, writes through `__jfs_setxattr()` under an existing transaction id, and updates the VFS cached ACL on success.
- `jfs_set_acl()` starts a transaction, locks `JFS_IP(inode)->commit_mutex`, updates inode mode for access ACLs with `posix_acl_update_mode()`, writes the ACL, marks mode/ctime dirty if needed, commits, and unlocks.
- `jfs_init_acl()` creates inherited ACLs for a new inode via `posix_acl_create()`, writes default and access ACLs when present, clears inode ACL caches otherwise, and synchronizes `mode2` low bits with `i_mode`.

## Error Handling
- Unsupported ACL types return `-EINVAL`.
- Missing ACL xattrs map `-ENODATA` to `NULL`.
- Allocation/conversion failures return standard kernel errors.
- Transaction commit result is returned from `jfs_set_acl()`.

## Dependencies
- Uses `jfs_xattr.h` for raw xattr helpers.
- Uses `jfs_txnmgr.h` for transaction begin/commit/end.
- Declared by `jfs_acl.h` and compiled only with `CONFIG_JFS_POSIX_ACL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/file.c -->
# File Research: sources/os/linux/linux/fs/jfs/file.c

## Purpose
Defines JFS regular-file VFS operations, fsync, open/release allocation-group accounting, and setattr/truncate behavior.

## Key Functions
- `jfs_fsync()` writes the requested file range, locks the inode, flushes the journal if no relevant inode dirty state remains, otherwise commits the inode synchronously and maps commit failure to `-EIO`.
- `jfs_open()` rejects regular files with negative size, initializes quotas through `dquot_file_open()`, and for newly opened empty writable regular files marks an active allocation group to reduce append fragmentation.
- `jfs_release()` decrements the active allocation-group counter and clears `ji->active_ag`.
- `jfs_setattr()` validates attributes, initializes/transfers quotas for uid/gid changes, waits for direct I/O before size changes, truncates through `jfs_truncate()`, copies attributes, marks the inode dirty, and updates ACLs on chmod.

## Exported Operation Tables
- `jfs_file_inode_operations`: listxattr, setattr, fileattr get/set, and optional ACL get/set.
- `jfs_file_operations`: open, llseek, generic buffered read/write, mmap prepare, splice, fsync, release, ioctl, compat ioctl, and lease support.

## Dependencies
- Calls into JFS dmap active-AG state (`bmap->db_active`), transaction/journal code, quota code, xattr/ACL code, and ioctl helpers.
- `jfs_setattr()` uses `jfs_truncate()` from `inode.c`.

## Notable Behavior
- Empty writable files are associated with the AG containing their inode extent; the allocator uses `db_active` to avoid multiple actively growing files in one AG.
- The code uses `nop_mnt_idmap` for idmapped-mount interactions in current call sites.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/inode.c -->
# File Research: sources/os/linux/linux/fs/jfs/inode.c

## Purpose
Implements JFS inode instantiation, writeback/commit, eviction, dirty marking, block mapping, address-space operations, direct I/O cleanup, and truncation.

## Key Functions
- `jfs_iget()` obtains or reads an inode, calls `diRead()`, then installs inode/file/address-space operations based on file type. It handles regular files, directories, long and fast symlinks, special files, and invalid modes.
- `jfs_commit_inode()` is the fsync/writeback workhorse. It skips deleted or non-JFS-dirty inodes, avoids committing read-only non-special files, starts a transaction, locks `commit_mutex`, retests dirty state, and calls `txCommit()`.
- `jfs_write_inode()` flushes the journal when the inode is VFS-dirty but not JFS `COMMIT_Dirty`, otherwise commits the inode.
- `jfs_evict_inode()` handles zero-link file cleanup, page truncation, possible zero-link extent freeing, dinode freeing, quota release, inode clearing, and active-AG counter cleanup.
- `jfs_dirty_inode()` sets `COMMIT_Dirty` unless the volume is read-only.
- `jfs_get_block()` maps logical blocks through `xtLookup()`, records unrecorded allocated extents on write, or allocates new extents via `extHint()` and `extAlloc()`.
- `jfs_writepages()`, `jfs_read_folio()`, `jfs_readahead()`, `jfs_write_begin()`, `jfs_write_end()`, `jfs_bmap()`, and `jfs_direct_IO()` bridge generic block/page-cache helpers to `jfs_get_block()`.
- `jfs_write_failed()` truncates page cache and JFS extents after failed extending writes.
- `jfs_truncate_nolock()` repeatedly calls `xtTruncate()` inside transactions because JFS truncation may not complete atomically.
- `jfs_truncate()` truncates the partial page, takes the inode write lock, and delegates to `jfs_truncate_nolock()`.

## Address-Space Operations
- `jfs_aops` wires dirty/invalidate folio, read/readahead, writepages, write_begin/end, bmap, direct_IO, and buffer folio migration.

## Dependencies
- Uses dinode read/write paths, extent/xtree allocation, transaction manager, quota infrastructure, page-cache helpers, and JFS locks/macros from `jfs_incore.h`.
- Calls into the allocator through extent code rather than directly invoking `jfs_dmap.c`.

## Notable Behavior
- Fast symlinks are null-terminated defensively to avoid kernel crashes from corrupted on-disk data.
- `jfs_get_block()` treats unrecorded extents as holes for reads and records them for writes.
- Failed direct I/O extending writes trim instantiated blocks beyond `i_size`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/ioctl.c -->
# File Research: sources/os/linux/linux/fs/jfs/ioctl.c

## Purpose
Implements JFS ioctl handling and VFS file-attribute get/set integration.

## Key Data
- `jfs_map[]` maps JFS inode flags to generic/ext2-style `FS_*` flags for noatime, dirsync, sync, secure deletion, undelete, append, and immutable.

## Key Functions
- `jfs_map_ext2()` translates flags between JFS internal and generic fileattr namespaces.
- `jfs_fileattr_get()` rejects special dentries, extracts user-visible flags from `JFS_IP(inode)->mode2`, translates them, and fills `struct file_kattr`.
- `jfs_fileattr_set()` rejects special dentries and fsx-style attrs, strips dirsync for non-directories, rejects quota files, preserves non-user-modifiable mode2 bits, applies file flags, updates ctime, and marks the inode dirty.
- `jfs_ioctl()` currently handles `FITRIM`: checks `CAP_SYS_ADMIN`, validates block-device discard support, copies `fstrim_range` from user space, raises `minlen` to discard granularity, calls `jfs_ioc_trim()`, copies the updated range back, and returns `-ENOTTY` for unknown commands.

## Dependencies
- Uses `jfs_dinode.h` for JFS flag definitions.
- Uses `jfs_discard.h` for `jfs_ioc_trim()`.
- Uses block-device discard helpers and Linux fileattr APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_acl.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_acl.h

## Purpose
Declares JFS ACL functions and provides a no-op initializer when POSIX ACL support is disabled.

## API
- With `CONFIG_JFS_POSIX_ACL`: declares `jfs_get_acl()`, `jfs_set_acl()`, and `jfs_init_acl()`.
- Without `CONFIG_JFS_POSIX_ACL`: `jfs_init_acl()` inline returns 0 so inode creation code can call it unconditionally.

## Dependencies
- Expects transaction id type `tid_t`, `struct inode`, `struct dentry`, and `struct posix_acl` from included surrounding headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_btree.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_btree.h

## Purpose
Provides common B+tree constants, macros, and traversal-stack structures shared by JFS directory trees and extent trees.

## Main Definitions
- Page flags: `BT_ROOT`, `BT_LEAF`, `BT_INTERNAL`, `BT_RIGHTMOST`, `BT_LEFTMOST`, and fsck-only `BT_SWAPPED`.
- Operation/order flags: random/sequential plus lookup/insert/delete markers.
- `BT_IS_ROOT()` distinguishes inline inode-root tree pages from metapage-backed pages.
- `BT_PAGE()`, `BT_GETPAGE()`, `BT_MARK_DIRTY()`, and `BT_PUTPAGE()` abstract root-vs-metapage access and dirtying.
- `struct btframe` records block number, entry index, last index, and metapage.
- `struct btstack` stores traversal frames up to `MAXTREEHEIGHT`.
- Stack macros initialize, push/pop, test full, and retrieve search results.

## Debug Support
- `BT_STACK_DUMP()` prints stack frame block numbers and indexes.

## Dependencies
- Uses JFS inode private data (`JFS_IP()`), metapages, `read_metapage()`, `mark_inode_dirty()`, `mark_metapage_dirty()`, and `jfs_err()`.

## Notable Behavior
- Root pages are stored inline in inode private data, using a fake metapage pointer based on `JFS_IP(IP)->bxflag`.
- Non-root pages are normal metapage buffers and must be released.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_debug.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_debug.c

## Purpose
Creates and removes `/proc/fs/jfs` debug/statistics entries when procfs plus JFS debug or statistics support is enabled.

## Key Functions
- `jfs_loglevel_proc_show()` prints current `jfsloglevel`.
- `jfs_loglevel_proc_open()` wraps the show function with `single_open()`.
- `jfs_loglevel_proc_write()` reads one user byte, accepts ASCII digits only, and sets `jfsloglevel`.
- `jfs_proc_init()` creates `/proc/fs/jfs`, optional stats entries (`lmstats`, `txstats`, `xtstat`, `mpstat`), optional debug entries (`TxAnchor`, `loglevel`).
- `jfs_proc_clean()` removes the proc subtree.

## Compile-Time Behavior
- Entire body is under `PROC_FS_JFS`.
- Loglevel handling and `TxAnchor` are under `CONFIG_JFS_DEBUG`.
- Statistics entries are under `CONFIG_JFS_STATISTICS`.

## Dependencies
- Uses procfs and seq_file APIs.
- Function declarations and `PROC_FS_JFS` are controlled by `jfs_debug.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_debug.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_debug.h

## Purpose
Defines JFS assertion, logging, procfs, and statistics macros.

## Main Definitions
- `PROC_FS_JFS` is enabled only when `CONFIG_PROC_FS` and either `CONFIG_JFS_DEBUG` or `CONFIG_JFS_STATISTICS` are set.
- `assert(p)` prints a critical BUG message and calls `BUG()` on failure.
- With `CONFIG_JFS_DEBUG`, `ASSERT()` maps to `assert()`, `jfsloglevel` is extern, and `jfs_info/debug/warn/err()` emit printk messages according to runtime loglevel.
- Without `CONFIG_JFS_DEBUG`, `ASSERT()` and logging macros compile to no-ops.
- With `CONFIG_JFS_STATISTICS`, proc show functions are declared and `INCREMENT`, `DECREMENT`, `HIGHWATERMARK` mutate counters.
- Without statistics, those counter macros are no-ops.

## Dependencies
- Debug proc show declarations use `struct seq_file`.
- Used broadly by JFS files for diagnostics and optional assertions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dinode.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_dinode.h

## Purpose
Defines the 512-byte on-disk JFS inode layout and extended inode mode/attribute flags.

## Main Structures
- `struct dinode` contains the base 128-byte POSIX/generic area: inode stamp, fileset, number, generation, inode extent descriptor, size, block count, nlink, uid/gid, mode, timestamps, ACL/EA descriptors, directory index state, and ACL type.
- The trailing 384 bytes are a union:
  - Directory form stores a 12-entry inline directory index table and a dtree root.
  - File/special form stores imap generator data, xtree root or special-file data, device id, fast symlink storage, inline EA storage, and combined inline storage.
- Macros alias union fields such as `di_dtroot`, `di_parent`, `di_xtroot`, `di_rdev`, `di_fastsymlink`, and `di_inlineea`.

## Constants and Flags
- `INODESLOTSIZE`, `L2INODESLOTSIZE`, and `log2INODESIZE` describe inode sizing.
- Extended mode bits include journaled file, sparse, inline-EA-free, swapfile, OS/2-style readonly/hidden/system/archive/name flags, and directory shadow bit.
- Linux-visible JFS flags include noatime, dirsync, sync, secure deletion, undelete, append, immutable.
- `JFS_FL_USER_VISIBLE`, `JFS_FL_USER_MODIFIABLE`, and `JFS_FL_INHERIT` define fileattr masks.

## Dependencies
- Uses on-disk descriptor types (`pxd_t`, `dxd_t`, `dtroot_t`, `xtroot_t`, `timestruc_t`) from other JFS headers.

## Notable Details
- Comments preserve OS/2 JFS layout compatibility and explain why the inode was not redesigned despite awkward union overlays.
- Fast symlink storage is expected to overflow into inline EA space when needed, clearing the `INLINEEA` flag.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_discard.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_discard.c

## Purpose
Implements JFS discard/TRIM support for online discard and the `FITRIM` ioctl path.

## Key Functions
- `jfs_issue_discard()` calls `sb_issue_discard()` for a filesystem block range using `GFP_NOFS`, logs failures with `jfs_err()`, and logs calls at info level.
- `jfs_ioc_trim()` converts user byte range fields to filesystem blocks, validates map state and range bounds, clamps end to map size, identifies allocation groups touched by the range, calls `dbDiscardAG()` for each AG, and updates `range->len` to the number of bytes actually trimmed.

## Error Handling
- Returns `-EINVAL` if the bmap is absent, `minlen` exceeds AG size, start is beyond map size, or range length is smaller than a filesystem block.
- `jfs_issue_discard()` does not propagate discard errors; it only logs them.

## Dependencies
- Uses `JFS_SBI(ip->i_sb)->bmap`, `ipbmap`, `BLKTOAG()`, and `dbDiscardAG()` from `jfs_dmap`.
- Called by `ioctl.c` for FITRIM and by `jfs_dmap.c` for mounted online discard.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_discard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_discard.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_discard.h

## Purpose
Declares the JFS discard/TRIM entry points.

## API
- Forward declares `struct fstrim_range`.
- Declares `jfs_issue_discard(struct inode *ip, u64 blkno, u64 nblocks)`.
- Declares `jfs_ioc_trim(struct inode *ip, struct fstrim_range *range)`.

## Dependencies
- Implemented by `jfs_discard.c`.
- Used by `ioctl.c` and `jfs_dmap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_discard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dmap.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_dmap.c

## Purpose
Implements the JFS aggregate block allocation map: mount/unmount synchronization, working and persistent bitmap updates, allocation/free policies, allocation-group selection, discard scanning, filesystem extension, and dmap/dmapctl buddy-summary tree maintenance.

## Architecture
- The allocator uses dmap pages for 8192-block bitmap chunks and dmapctl pages for multi-level summary trees.
- Working allocation state uses `dmap.wmap`; committed persistent allocation state uses `dmap.pmap`.
- Summary trees store log2 maximum free-buddy sizes, with `NOFREE` meaning no free blocks in a subtree.
- Allocation groups (`AG`s) track per-group free counts and active-writer counts to reduce fragmentation.
- Bottom-up operations hold `IREAD_LOCK(ipbmap, RDWRLOCK_DMAP)` and serialize through busy metapages plus `BMAP_LOCK` for global counters.
- Top-down searches hold `IWRITE_LOCK(ipbmap, RDWRLOCK_DMAP)` to exclude other map traversals.

## Mount, Unmount, and Sync
- `dbMount()` allocates `struct bmap`, reads the on-disk global map descriptor, converts little-endian fields, validates descriptor ranges, initializes active counters and the bmap mutex, and attaches it to `JFS_SBI(sb)->bmap`.
- `dbUnmount()` syncs the bmap unless read-only or mount-error, truncates bmap inode pages, frees the descriptor, and clears the superblock pointer.
- `dbSync()` writes in-memory global bmap fields back to the on-disk descriptor, writes dirty bmap pages, and calls `diWriteSpecial()`.

## Integrity Checks
- `check_dmapctl()` validates dmapctl metadata before tree descent/update: leaf count bounds, power-of-two leaf count, expected leaf index, height, `budmin`, leaf range bounds, and leaf value range.
- This check is used in `dbAllocAG()`, `dbFindCtl()`, `dbAdjCtl()`, and `dbExtendFS()` before relying on dmapctl tree fields.
- Additional checks reject corrupt dmap pages with unexpected `leafidx`, negative dmap `budmin`, inconsistent control pages, and invalid buddy tree states.

## Allocation and Freeing
- `dbFree()` validates range bounds, optionally issues online discard when mounted with `JFS_DISCARD`, then frees blocks dmap-by-dmap through `dbFreeDmap()`.
- `dbUpdatePMap()` updates the persistent bitmap for a transaction, dmap-by-dmap, and attaches metapages to log sync lists with appropriate `lsn`/`clsn`.
- `dbNextAG()` chooses a preferred inactive AG with at least average free space, falling back to the best inactive AG below average.
- `dbAlloc()` is the main allocation policy:
  - Large requests above AG size go directly to `dbAllocAny()`.
  - Hintless requests use `dbNextAG()`.
  - Hinted small requests try immediate next blocks, nearby leaves, the same dmap, the same AG, preferred AG, then anywhere.
  - Active-writer AG counters can push allocation away from busy AGs.
- `dbReAlloc()` first tries in-place extension through `dbExtend()`, then allocates a larger new range if extension fails with `-ENOSPC`.
- `dbExtend()` attempts to allocate blocks immediately after an existing range, with page-boundary and AG-boundary constraints.
- `dbAllocAG()` searches a specified AG through dmapctl subtrees or direct dmap allocation for minimum-size/free AG cases.
- `dbAllocAny()` searches from the top dmapctl level, then allocates through `dbAllocCtl()`.
- `dbAllocCtl()` allocates from a dmap or across multiple all-free dmaps; on multi-dmap failure it attempts to back out partial allocations.
- `dbAllocDmapLev()` searches one dmap tree for a suitable leaf and allocates from it.
- `dbAllocDmap()` and `dbFreeDmap()` update one dmap and propagate changed root values upward through `dbAdjCtl()`.
- `dbAllocBottomUp()` and `dbAllocDmapBU()` allocate a specified range during resize/setup-style paths and reconstruct the dmap tree afterward.

## Bitmap and Buddy Tree Maintenance
- `dbAllocBits()` sets working-map bits, splits buddy leaves through `dbSplit()`, updates dmap free count, AG free count, global free count, and `db_maxag`.
- `dbFreeBits()` clears working-map bits, joins buddies through `dbJoin()`, updates counts, and may move `db_maxag`/`db_agpref` left when rightmost AGs become fully free.
- `dbAdjCtl()` updates the dmapctl leaf corresponding to a lower-level root change, recursively bubbles root changes upward, and updates `db_maxfreebud` at the top.
- `dbSplit()` splits a larger buddy system down to the requested size before applying a new leaf value.
- `dbBackSplit()` handles rare allocations or rollbacks that start in the middle of a larger buddy system.
- `dbJoin()` coalesces equal-sized buddy leaves into larger free systems and rejects inconsistent buddy values with `-EIO`.
- `dbAdjTree()` updates a leaf and bubbles max values up a 4-way summary tree with bounds checking.
- `dbFindLeaf()` finds the leftmost leaf with sufficient free space in dmap or dmapctl trees.
- `dbFindBits()` scans a 32-bit bitmap word for aligned free bits.
- `dbMaxBud()` uses `budtab` plus word/halfword checks to compute the largest free buddy in one map word.
- `cnttz()`, `cntlz()`, and `blkstol2()` provide bit-count/log2 helpers used by macros and allocation sizing.

## Discard and Trim
- `dbDiscardAG()` trims free space in one AG by temporarily allocating large free ranges while holding the bmap write lock, storing up to 32K ranges, releasing the lock, issuing discard for each saved range unless online discard will do it through `dbFree()`, freeing the ranges, and returning blocks trimmed.
- This is called by `jfs_ioc_trim()` in `jfs_discard.c`.

## Filesystem Extension
- `dbExtendFS()` expands the bmap for new blocks, recomputes map size, max level, AG size/count, coalesces old AG free counts if AG size changes, reads or initializes L2/L1/L0/dmap pages, initializes new dmaps with `dbInitDmap()`, updates parent control leaves, and updates free counters.
- `dbFinalizeBmap()` recomputes preferred AG, AG tree level/height/width/start after extension.
- `dbInitDmap()` initializes a dmap's working/persistent maps for existing and non-existing blocks and builds its summary tree.
- `dbInitDmapTree()` initializes dmap tree fixed fields and leaf values from `wmap`.
- `dbInitTree()` coalesces leaf-level buddies and bubbles summary values upward.
- `dbInitDmapCtl()` initializes a dmapctl page and marks leaves outside the covered range as `NOFREE`.
- `dbGetL2AGSize()` derives allocation group size from aggregate size.
- `dbMapFileSizeToMapSize()` computes the aggregate block coverage possible from the bmap file size.

## Dependencies
- Uses `jfs_dmap.h` for constants, structures, and conversion macros.
- Uses metapage I/O, transaction/log sync structures, inode/superblock state, JFS locks, discard support, and debug/error helpers.
- Called indirectly from extent allocation/truncation code and directly from discard and mount/resize paths.

## Notable Risks and Invariants
- Bitmap, dmap tree, dmapctl tree, global free counts, and AG free counts must remain synchronized; many paths back out on propagation failure.
- Multi-dmap allocation expects complete dmaps to be all free; otherwise it treats the map as inconsistent.
- Persistent map updates are transaction/log-sensitive and distinct from working-map updates.
- Discard temporarily allocates free blocks as a scanning mechanism, so errors during later free would affect allocation-map consistency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dmap.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_dmap.h

## Purpose
Defines JFS block allocation-map constants, dmap/dmapctl/global descriptor structures, conversion macros, and exported allocator interfaces.

## Constants
- Dmap geometry: `TREESIZE`, `LEAFIND`, `LPERDMAP`, `DBWORD`, `BUDMIN`, `BPERDMAP`, `L2BPERDMAP`.
- Dmapctl geometry: `CTLTREESIZE`, `CTLLEAFIND`, `LPERCTL`, `L2LPERCTL`.
- Map limits: `MAXAG`, `L2MAXAG`, `L2MAXL0SIZE`, `L2MAXL1SIZE`, `L2MAXL2SIZE`, `MAXMAPSIZE`.
- `ROOT` identifies the root summary-tree index.
- `NOFREE` is `-1`, used when a subtree has no free blocks.

## Conversion Helpers
- `TREEMAX()` returns the max value of four sibling tree entries.
- `BLKTODMAP()`, `BLKTOL0()`, `BLKTOL1()`, and `BLKTOCTL()` translate aggregate block numbers to bmap file logical blocks.
- `BMAPSZTOLEV()` maps aggregate size to top dmapctl level.
- `BLKTOAG()` and `AGTOBLK()` convert between block numbers and allocation groups.
- `BLKSTOL2`, `NLSTOL2BSZ`, `LITOL2BSZ`, `BLKTOCTLLEAF`, and `BUDSIZE` support buddy sizing and tree indexing.

## Structures
- `struct dmaptree`: fixed metadata plus 341-entry dmap summary tree.
- `struct dmap`: one 4096-byte dmap page covering 8192 blocks, with free counts, start block, summary tree, working bitmap, and persistent bitmap.
- `struct dmapctl`: 4096-byte control-page summary tree for higher-level dmap coverage.
- `union dmtree`: overlays dmap and dmapctl tree metadata for generic tree routines.
- `struct dbmap_disk`: on-disk global allocation-map descriptor with aggregate counts, AG configuration/free counts, and max free buddy.
- `struct dbmap`: endian-native in-memory counterpart.
- `struct bmap`: runtime descriptor containing `dbmap`, bmap inode pointer, global bmap mutex, per-AG active-writer counters, and `db_DBmap`.

## Exported API
- Lifecycle/sync: `dbMount()`, `dbUnmount()`, `dbSync()`, `dbFinalizeBmap()`.
- Allocation/free: `dbAlloc()`, `dbReAlloc()`, `dbFree()`, `dbAllocBottomUp()`.
- Persistent bitmap and resize: `dbUpdatePMap()`, `dbExtendFS()`, `dbMapFileSizeToMapSize()`.
- Policy and discard: `dbNextAG()`, `dbDiscardAG()`.

## Dependencies
- Includes `jfs_txnmgr.h` because persistent-map updates need transaction blocks.
- Implemented primarily by `jfs_dmap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dmap.h -->