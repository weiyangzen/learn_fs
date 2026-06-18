# subset-b-005679 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/xattr.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/xattr.c

## Purpose
`xattr.c` implements the JFFS2 extended-attribute core: persistent xattr datum nodes, inode-to-datum reference nodes, cache loading/reclaim, mount-time reconstruction, VFS list/get/set helpers, inode teardown, CRC verification, and garbage-collection relocation. It stores each unique name/value pair as a deduplicated `jffs2_xattr_datum` and links inodes to datums through `jffs2_xattr_ref`.

## Important APIs, types, and functions
- Datum helpers: `xattr_datum_hashkey()`, `load_xattr_datum()`, `save_xattr_datum()`, `create_xattr_datum()`, and `unrefer_xattr_datum()`.
- Xref helpers: `verify_xattr_ref()`, `save_xattr_ref()`, `create_xattr_ref()`, `delete_xattr_ref()`, `check_xattr_ref_inode()`.
- Subsystem entry points: `jffs2_init_xattr_subsystem()`, `jffs2_build_xattr_subsystem()`, `jffs2_setup_xattr_datum()`, `jffs2_clear_xattr_subsystem()`.
- VFS-facing helpers: `jffs2_listxattr()`, `do_jffs2_getxattr()`, `do_jffs2_setxattr()`, and `jffs2_xattr_handlers`.
- GC hooks: `jffs2_garbage_collect_xattr_datum()`, `jffs2_garbage_collect_xattr_ref()`, `jffs2_verify_xattr()`, release helpers.

## Control flow
Mount scanning first creates datum stubs with `jffs2_setup_xattr_datum()` and temporary refs. `jffs2_build_xattr_subsystem()` verifies unchecked refs, merges duplicate `(ino,xid)` refs by sequence number, binds live refs to inode caches and datums, moves dead/orphan refs to dead lists, and places unverified or orphan datums on `xattr_unchecked`.

Runtime reads call `check_xattr_ref_inode()` to remove duplicate names and load any required datums. `jffs2_listxattr()` walks `ic->xref`, loads uncached datums after upgrading from read to write semaphore, maps JFFS2 prefixes to Linux xattr handlers, and emits prefixed names. `do_jffs2_getxattr()` performs the same walk for one prefix/name and copies the value if the caller buffer is large enough. `do_jffs2_setxattr()` reserves space for a raw xattr, finds and optionally deletes/replaces an existing ref, creates or reuses a matching datum, then reserves and writes a raw xref. Replacing an attribute writes a new ref before deleting the old ref.

GC relocates only current pristine nodes. Datum GC loads and rewrites a live datum, then obsoletes the old raw node. Xref GC rewrites the latest ref unless it is a terminal delete marker.

## State and persistence behavior
Persistent state is journaled as `JFFS2_NODETYPE_XATTR` raw datum nodes and `JFFS2_NODETYPE_XREF` raw reference nodes, both protected by node CRCs. Datums carry xid/version/name/value CRC; xrefs carry ino/xid/xseqno, where the low bit is `XREF_DELETE_MARKER`. In memory, `c->xattrindex[]` caches loaded datums by hash, `xattr_unchecked` tracks datums that need verification, `xattr_dead_list` and `xref_dead_list` defer release until raw refs are reclaimed, and `ic->xref` links inode attributes. `xattr_sem` serializes xattr object mutation; `erase_completion_lock` protects raw-node chains and space accounting. Cache memory is capped by `xdatum_mem_threshold` with a hot/bind reclamation scheme.

## Dependencies and integration points
The file integrates with JFFS2 scan/build code, inode cache lifetime, raw node references, flash read/write/reservation APIs, GC, VFS xattr handlers, optional security and POSIX ACL handlers, MTD flash I/O, CRC32, and JFFS2 summary accounting.

## Risks and test signals
Risks include CRC/corruption classification, read-to-write lock upgrades during list/get, sequence-number handling for duplicate refs, replacing refs without leaking datum refs, cache reclamation while a datum is being compared, delete marker recovery, unchecked-size accounting, and GC behavior on dead or invalid objects. Tests should cover mount rebuild with duplicate refs, corrupt datum/ref CRCs, create/replace/delete flags, large xattrs near eraseblock limits, list visibility for trusted/security/user prefixes, GC relocation, inode deletion, memory-pressure cache reclaim, and EBS/unchecked-node verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/xattr.h -->
# sources/distributed-fs/ceph-client/fs/jffs2/xattr.h

## Purpose
`xattr.h` defines JFFS2 xattr in-memory objects, flags, dead-reference encoding, exported xattr subsystem APIs, and compile-time fallbacks when xattrs or security labels are disabled.

## Important APIs, types, and functions
- `struct jffs2_xattr_datum` represents one deduplicated raw xattr name/value datum with xid, version, CRC, cache hash, name/value pointers, and refcount.
- `struct jffs2_xattr_ref` represents one inode-to-datum link and is reused during scanning as `(ino,xid)` before binding to `(ic,xd)`.
- `JFFS2_XFLAGS_HOT`, `BIND`, `DEAD`, and `INVALID` drive cache reclaim and lifecycle.
- `XREF_DELETE_MARKER` and `is_xattr_ref_dead()` encode deletion in `xseqno`.
- Exports include build/clear/setup, inode delete/free/CRC-check, GC relocate/release, get/set helpers, `jffs2_xattr_handlers`, and `jffs2_listxattr`.

## Control flow
Consumers include `nodelist.h` users during scan/build, VFS xattr handlers, inode eviction/free paths, and GC. With `CONFIG_JFFS2_FS_XATTR`, the header exposes real functions. Without it, initialization and cleanup become no-ops, verification returns success, handlers/listxattr are null, and no xattr storage path is compiled.

## State and persistence behavior
The structures are in-memory mirrors for on-flash xattr/xref nodes. The header itself persists nothing, but its fields define the lifecycle contract: datum refcounts determine when a name/value can die, raw node chains stay attached through `node`, and scanning temporarily interprets unions as raw ids until build binds them to inode and datum pointers.

## Dependencies and integration points
It depends on Linux xattr/list primitives and JFFS2 core types. Optional security support exports `jffs2_init_security()` and `jffs2_security_xattr_handler`; otherwise security initialization is a no-op.

## Risks and test signals
Risks are ABI-like: structure fields are assumed by raw-node ref code and GC, and the union fields must only be read in the correct scan/build or runtime phase. Build tests should cover all config combinations for `CONFIG_JFFS2_FS_XATTR`, security, and POSIX ACL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/xattr_trusted.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/xattr_trusted.c

## Purpose
`xattr_trusted.c` registers the JFFS2 `trusted.*` xattr namespace handler and delegates storage to the shared JFFS2 xattr core.

## Important APIs, types, and functions
- `jffs2_trusted_getxattr()` calls `do_jffs2_getxattr()` with `JFFS2_XPREFIX_TRUSTED`.
- `jffs2_trusted_setxattr()` calls `do_jffs2_setxattr()` with the same prefix.
- `jffs2_trusted_listxattr()` allows listing only for callers with `CAP_SYS_ADMIN`.
- `jffs2_trusted_xattr_handler` exposes `.prefix`, `.list`, `.set`, and `.get`.

## Control flow
The VFS xattr layer dispatches trusted namespace operations to this handler. Get/set are thin wrappers; list filtering is capability-based and is also consumed by `jffs2_xattr_prefix()` before `listxattr` emits names.

## State and persistence behavior
This file owns no state. Values are persisted as normal JFFS2 xattr datums with trusted prefix metadata in `xattr.c`.

## Dependencies and integration points
It depends on Linux xattr handler contracts, capability checks, JFFS2 prefix constants, and `nodelist.h` declarations of the common helper functions.

## Risks and test signals
Main risks are namespace permission regressions and mismatched prefix encoding. Tests should verify trusted attributes can be set/read by privileged callers, are hidden from unprivileged list output, and round-trip through remount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/xattr_trusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/xattr_user.c -->
# sources/distributed-fs/ceph-client/fs/jffs2/xattr_user.c

## Purpose
`xattr_user.c` registers the JFFS2 `user.*` xattr namespace handler and maps user namespace operations onto the common xattr engine.

## Important APIs, types, and functions
- `jffs2_user_getxattr()` delegates to `do_jffs2_getxattr()` with `JFFS2_XPREFIX_USER`.
- `jffs2_user_setxattr()` delegates to `do_jffs2_setxattr()` with `JFFS2_XPREFIX_USER`.
- `jffs2_user_xattr_handler` advertises `XATTR_USER_PREFIX` and get/set operations.

## Control flow
The VFS xattr layer invokes the handler for `user.*` names. There is no namespace-specific list predicate, so normal VFS/JFFS2 handler policy controls visibility.

## State and persistence behavior
No independent state is stored here. The prefix and suffix name/value are persisted by `xattr.c` raw xattr nodes and inode xrefs.

## Dependencies and integration points
The file depends on Linux xattr APIs, JFFS2 prefix constants, and the common JFFS2 xattr helper prototypes.

## Risks and test signals
Risks are limited but include prefix mismatches and flag propagation errors. Tests should cover create, replace, remove, get-size query, short buffer `-ERANGE`, and remount persistence for `user.*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jffs2/xattr_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/jfs/Kconfig

## Purpose
`Kconfig` declares the Linux JFS filesystem feature switches and their kernel dependencies.

## Important APIs, types, and functions
- `JFS_FS` is the main tristate and selects buffer heads, NLS helpers, CRC32, and legacy direct I/O.
- `JFS_POSIX_ACL` enables POSIX ACL support and selects `FS_POSIX_ACL`.
- `JFS_SECURITY` enables security label xattrs.
- `JFS_DEBUG` enables debug logging/proc controls.
- `JFS_STATISTICS` enables procfs statistics under `/proc/fs/jfs/`.

## Control flow
Kernel configuration resolves these symbols before compilation. The JFS Makefile and many source files use the symbols to include objects, expose inode operations, compile procfs entries, and enable handlers.

## State and persistence behavior
The file has no runtime state. It controls whether filesystem code paths and optional on-disk metadata consumers are built.

## Dependencies and integration points
It integrates with Kbuild, documentation, ACL/security frameworks, procfs statistics/debug code, and generic block/page-cache helpers selected by the main filesystem option.

## Risks and test signals
Risks include missing selected dependencies and untested config combinations. Build matrix tests should compile JFS as built-in and module, with ACL/security/debug/statistics toggled independently where dependencies allow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/jfs/Makefile

## Purpose
`Makefile` defines the JFS object composition for Kbuild.

## Important APIs, types, and functions
- `obj-$(CONFIG_JFS_FS) += jfs.o` builds the aggregate module/object.
- `jfs-y` lists the required implementation units: superblock, VFS files, inode, mount/unmount, extent/dtree/imap/dmap, unicode, metapage, log/transaction, resize, xattr, ioctl, discard, and others.
- `jfs-$(CONFIG_JFS_POSIX_ACL) += acl.o` conditionally adds ACL support.

## Control flow
Kbuild expands this file after Kconfig resolution. Source-level dependencies assume all listed base objects are linked into `jfs.o`; ACL calls are guarded by config macros and only linked when enabled.

## State and persistence behavior
No runtime state is defined. The file determines which code can affect on-disk JFS metadata at runtime.

## Dependencies and integration points
It integrates with the Linux kernel build system and the JFS Kconfig symbols.

## Risks and test signals
Risks are build/link regressions when a source file adds or removes exported symbols. Test signals are allconfig/modconfig builds and ACL-enabled/disabled link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/acl.c -->
# sources/distributed-fs/ceph-client/fs/jfs/acl.c

## Purpose
`acl.c` implements JFS POSIX ACL retrieval, setting, and inheritance using JFS extended attributes and transaction commits.

## Important APIs, types, and functions
- `jfs_get_acl()` reads `system.posix_acl_access` or `system.posix_acl_default` via `__jfs_getxattr()` and converts the xattr blob with `posix_acl_from_xattr()`.
- `__jfs_set_acl()` serializes ACLs with `posix_acl_to_xattr()`, writes through `__jfs_setxattr()`, and updates the inode ACL cache.
- `jfs_set_acl()` wraps ACL updates in `txBegin()`/`txCommit()`, `commit_mutex`, and optional mode adjustment via `posix_acl_update_mode()`.
- `jfs_init_acl()` derives inherited ACLs with `posix_acl_create()` during inode creation.

## Control flow
Get rejects RCU lookup with `-ECHILD`, maps ACL type to xattr name, sizes then reads the EA, and returns null on `-ENODATA`. Set begins a transaction, locks the inode commit mutex, updates mode if an access ACL changes permissions, writes ACL xattr data, marks inode dirty if mode changed, commits, and ends the transaction.

## State and persistence behavior
ACLs persist as JFS xattrs. In-memory VFS ACL caches are refreshed on successful set and initialized to null when no inherited ACL exists. Mode changes are persisted by dirtying and committing the inode in the same transaction.

## Dependencies and integration points
It depends on Linux POSIX ACL helpers, JFS xattr internals, JFS transaction manager, and inode commit locking. It is compiled only with `CONFIG_JFS_POSIX_ACL`.

## Risks and test signals
Risks include transaction ordering, cache coherency after failed writes, mode updates without commit, and xattr conversion allocation failures. Tests should cover default ACL inheritance, chmod ACL recalculation, ACL removal, remount persistence, RCU lookup fallback, and transaction failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/file.c -->
# sources/distributed-fs/ceph-client/fs/jfs/file.c

## Purpose
`file.c` defines regular-file VFS operations for JFS: fsync, open/release allocation-group activity tracking, setattr/truncate handling, ioctl wiring, xattr listing, ACL hooks, and generic read/write/mmap operation tables.

## Important APIs, types, and functions
- `jfs_fsync()` waits dirty file data and commits dirty inode metadata or flushes the journal.
- `jfs_open()` validates regular inode size, initializes quotas, and marks an active allocation group for empty writable files.
- `jfs_release()` decrements the active allocation-group writer count.
- `jfs_setattr()` handles VFS attribute validation, quota transfer, truncation, dirtying, and ACL chmod updates.
- `jfs_file_inode_operations` and `jfs_file_operations` expose JFS hooks to VFS.

## Control flow
`fsync` first writes the requested page-cache range. If the inode has no relevant dirty state, it flushes the journal so prior commits reach disk; otherwise it calls `jfs_commit_inode()`. `open` uses quota open handling and, for new writable regular files, pins `ji->active_ag` to the inode extent's AG to reduce append fragmentation. `release` reverses that counter. `setattr` validates, initializes/transfers quota on uid/gid changes, waits for DIO before size changes, truncates via `jfs_truncate()`, copies attributes, marks dirty, and applies ACL chmod if mode changed.

## State and persistence behavior
Persistent effects are inode metadata updates, journal commits, quota updates, and extent truncation. Runtime-only state includes `active_ag` and `bmap->db_active[]` counters protected by `ag_lock`.

## Dependencies and integration points
The file integrates with Linux VFS file/inode operations, quota APIs, page cache writeback, JFS transaction/inode/truncate code, xattr, ACL, ioctl, and dmap allocation-group accounting.

## Risks and test signals
Risks include missed journal flushes for datasync, active AG counter leaks on open/release/evict, quota transfer ordering, DIO/truncate races, and ACL chmod failures after partial setattr. Tests should cover fsync/datasync durability, open/release under append workloads, truncate grow/shrink with DIO, quota ownership changes, fileattr ioctls, and ACL chmod integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/jfs/inode.c

## Purpose
`inode.c` bridges JFS on-disk inode/extents with Linux inode and address-space operations. It loads inodes, commits dirty metadata, evicts deleted inodes, maps file blocks, performs buffered/direct I/O callbacks, and truncates extents.

## Important APIs, types, and functions
- `jfs_iget()` reads a disk inode with `diRead()` and installs operation tables by file type.
- `jfs_commit_inode()`, `jfs_write_inode()`, and `jfs_dirty_inode()` manage dirty commit state and journal flushing.
- `jfs_evict_inode()` truncates pages, frees zero-link inodes, updates quotas, and clears allocation-group activity.
- `jfs_get_block()` maps or allocates logical blocks using xtree/extents (`xtLookup()`, `extRecord()`, `extHint()`, `extAlloc()`).
- Address-space callbacks: `jfs_writepages()`, `jfs_read_folio()`, `jfs_readahead()`, `jfs_write_begin()`, `jfs_write_end()`, `jfs_direct_IO()`, `jfs_bmap()`.
- `jfs_truncate_nolock()` and `jfs_truncate()` shrink extent trees transactionally.

## Control flow
Inode lookup locks a new VFS inode, calls `diRead()`, and selects regular, directory, symlink, or special operations. Fast symlinks are served from inline inode bytes; long symlinks use page-cache operations. Dirty writeback checks JFS commit flags: clean-but-listed inodes only flush the journal, while true dirty inodes commit through `txBegin()`/`txCommit()` under `commit_mutex`.

Block mapping takes read or write inode locks depending on creation. Existing recorded extents are mapped directly. Not-recorded allocated extents are treated as holes for reads; writes call `extRecord()` before mapping and mark buffers new. If no extent exists and create is true, `extHint()`/`extAlloc()` allocates an extent. Buffered and direct I/O use this mapper; failed extending writes trim page cache and truncate extra blocks.

Truncation first truncates partial page data, takes the write lock, and repeatedly calls `xtTruncate()` inside transactions because JFS truncation may not complete atomically.

## State and persistence behavior
State spans Linux inode fields, JFS inode-private flags (`COMMIT_Dirty`, `COMMIT_Freewmap`, `COMMIT_Nolink`), xtree extents, page cache buffers, quotas, and the journal. Persistence is mediated by tx manager commits, extent allocation/recording, `diFree()`, and journal flushes. Inline symlink safety is handled by forcing a null terminator within the inline buffer.

## Dependencies and integration points
It integrates with VFS inode/page-cache/writeback/direct-I/O APIs, JFS disk inode manager, extent tree, imap, transaction manager, dmap allocator, quotas, and operation tables from file/namei/symlink code.

## Risks and test signals
Risks include extent recording races, not-recorded extent semantics, failed direct I/O cleanup, read-only dirty-inode warnings, truncate loops, evict ordering with quotas and imap, and invalid file type handling. Tests should cover inode reload for all file types, sparse/preallocated files, buffered and direct extending writes with injected failures, fsync/writeback durability, unlink eviction, truncate partial pages, fast symlink bounds, and read-only remount races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/jfs/ioctl.c

## Purpose
`ioctl.c` implements JFS file attribute get/set support and the FITRIM ioctl.

## Important APIs, types, and functions
- `jfs_map_ext2()` translates between JFS internal mode2 flags and generic `FS_*_FL` flags.
- `jfs_fileattr_get()` exposes user-visible flags through `fileattr_fill_flags()`.
- `jfs_fileattr_set()` validates generic fileattr input, filters unsupported or immutable flags, updates `mode2`, refreshes inode flags, ctime, and dirty state.
- `jfs_ioctl()` currently handles `FITRIM` and returns `-ENOTTY` otherwise.

## Control flow
Fileattr operations reject special files. Set rejects fsx-style attributes, removes directory-sync for non-directories, denies quota files, masks to user-modifiable bits, preserves non-user bits, and marks the inode dirty. FITRIM requires `CAP_SYS_ADMIN`, device discard support, copies a `fstrim_range` from userspace, clamps `minlen` to device granularity, calls `jfs_ioc_trim()`, and copies the result back.

## State and persistence behavior
File attributes persist in `JFS_IP(inode)->mode2` once the dirty inode is committed. FITRIM does not change logical file data but temporarily allocates/free-ranges internally through dmap trimming code and reports discarded bytes in `range->len`.

## Dependencies and integration points
It integrates with Linux fileattr and ioctl APIs, capability checks, block-device discard limits, userspace copy helpers, JFS inode flags, dmap, and discard implementation.

## Risks and test signals
Risks include exposing wrong flag mappings, allowing quota-file mutation, ctime/dirty omissions, FITRIM range overflow/rounding, and discard on unsupported devices. Tests should cover `lsattr/chattr` mappings, special files, quota files, directory-only dirsync, unknown ioctls, FITRIM privilege/device checks, and minlen/range clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_acl.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_acl.h

## Purpose
`jfs_acl.h` declares JFS ACL entry points and provides no-op initialization when ACL support is disabled.

## Important APIs, types, and functions
- With `CONFIG_JFS_POSIX_ACL`, it declares `jfs_get_acl()`, `jfs_set_acl()`, and `jfs_init_acl()`.
- Without ACL support, `jfs_init_acl()` is an inline success no-op.

## Control flow
Creation paths can call `jfs_init_acl()` unconditionally; regular file inode operations include get/set ACL hooks only under the config guard.

## State and persistence behavior
The header stores no state. It gates whether ACL xattrs are initialized and maintained by `acl.c`.

## Dependencies and integration points
It depends on VFS inode/dentry/idmap and JFS transaction id types supplied by included JFS headers in consumers.

## Risks and test signals
Risks are build-only: missing prototypes under config variants or creation paths assuming ACL side effects when disabled. Build and create-file tests should cover ACL enabled and disabled kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_btree.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_btree.h

## Purpose
`jfs_btree.h` provides common B+tree constants, page access macros, dirty/release helpers, and traversal stack structures for JFS directory trees and extent trees.

## Important APIs, types, and functions
- Page flags: `BT_ROOT`, `BT_LEAF`, `BT_INTERNAL`, right/left-most flags, and endian-swapped marker.
- Operation-order bits: `BT_RANDOM`, `BT_SEQUENTIAL`, `BT_LOOKUP`, `BT_INSERT`, `BT_DELETE`.
- `BT_IS_ROOT()`, `BT_PAGE()`, `BT_GETPAGE()`, `BT_MARK_DIRTY()`, and `BT_PUTPAGE()` abstract inline-root versus metapage-backed tree pages.
- `struct btframe` and `struct btstack` record traversal paths up to `MAXTREEHEIGHT`.
- Stack macros push/pop/search-result extraction and release searched pages.

## Control flow
Tree algorithms in dtree/xtree use these macros to fetch root pages from inode-private inline storage or read child pages from metapages, track the path to a leaf, dirty the proper backing object, and release non-root metapages.

## State and persistence behavior
The header defines transient traversal stack state and the access contract for persistent tree pages. Root pages live inside the inode; non-root pages live in metapages and are persisted through metapage dirty/writeback.

## Dependencies and integration points
It integrates with JFS inode-private tree roots, metapage cache, printk/assert diagnostics, and dtree/xtree implementations.

## Risks and test signals
Risks include macro side effects, root/non-root confusion, stack overflow at maximum tree height, and missing metapage release after searches. Tests should stress deep directories/extents, root splits, deletes, insertions, dirtying of root versus child pages, and I/O failure from `read_metapage()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_debug.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_debug.c

## Purpose
`jfs_debug.c` creates and removes optional `/proc/fs/jfs` entries for debug loglevel control and statistics/debug state dumps.

## Important APIs, types, and functions
- `jfs_loglevel_proc_show()`, open, and write handlers expose `jfsloglevel` when debug is enabled.
- `jfs_proc_init()` creates `/proc/fs/jfs` and optional `lmstats`, `txstats`, `xtstat`, `mpstat`, `TxAnchor`, and `loglevel` entries.
- `jfs_proc_clean()` removes the proc subtree.

## Control flow
When procfs plus JFS debug/statistics are configured, mount/module initialization can call `jfs_proc_init()`. A loglevel write accepts one ASCII digit and stores it in the global. Cleanup removes the entire subtree.

## State and persistence behavior
State is runtime-only procfs state and the global `jfsloglevel`; nothing is persisted on disk. Statistic entries are read-only views supplied by other JFS modules.

## Dependencies and integration points
It depends on procfs, seq_file, user copy helpers, JFS debug/statistic show functions, and config macros from `jfs_debug.h`.

## Risks and test signals
Risks include proc entry leaks, permissive loglevel values beyond documented range, and missing entries under config combinations. Tests should mount/unmount or load/unload with debug/statistics combinations, read all proc files, and validate invalid/valid loglevel writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_debug.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_debug.h

## Purpose
`jfs_debug.h` centralizes JFS assert, logging, procfs, and statistics macros behind kernel config options.

## Important APIs, types, and functions
- `PROC_FS_JFS` is defined when procfs plus debug or statistics are enabled.
- `assert()` always prints and BUGs on false; `ASSERT()` maps to `assert()` only in debug builds.
- `jfs_info()`, `jfs_debug()`, `jfs_warn()`, and `jfs_err()` emit printk messages according to `jfsloglevel` only when debug is enabled.
- `INCREMENT`, `DECREMENT`, and `HIGHWATERMARK` compile to statistic updates only under `CONFIG_JFS_STATISTICS`.

## Control flow
Source files call logging/stat macros unconditionally. Preprocessor guards either compile real logging/statistic code or erase it, reducing overhead in normal builds.

## State and persistence behavior
The header itself has no state. When enabled, logging depends on runtime global `jfsloglevel`; statistics counters live in their owning modules and are exposed via procfs.

## Dependencies and integration points
It integrates with printk, BUG assertions, procfs initialization declarations, seq_file show functions, and JFS source-wide diagnostics.

## Risks and test signals
Risks include side effects in macro arguments being compiled out, BUG-triggering assertions in production paths, and mismatched proc declarations. Build tests should cover debug/statistics on/off; runtime tests should validate loglevel gating and statistic counters under workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dinode.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_dinode.h

## Purpose
`jfs_dinode.h` defines the 512-byte on-disk JFS inode layout and extended mode/attribute bits used by inode, xattr, directory, symlink, and ioctl code.

## Important APIs, types, and functions
- `struct dinode` contains base POSIX fields, inode extent descriptor, size/block counts, link/uid/gid/mode, timestamps, ACL/EA descriptors, directory index state, and a large union for directory roots or file/special data.
- Directory overlays include inline directory table slots and `dtroot_t`.
- File overlays include `xtroot_t`, device descriptor, fast symlink bytes, and inline EA area.
- Mode bits include `IFJOURNAL`, `ISPARSE`, `INLINEEA`, OS/2 attributes, and Linux-visible flags such as `JFS_NOATIME_FL`, `JFS_SYNC_FL`, `JFS_APPEND_FL`, and `JFS_IMMUTABLE_FL`.

## Control flow
Disk inode read/write code maps these fields into `struct inode` and `struct jfs_inode_info`. Directory, extent, symlink, xattr, and ioctl code rely on the union aliases to interpret the final 384 bytes according to file type and mode bits.

## State and persistence behavior
This is persistent on-disk metadata. The layout must remain compatible with existing JFS/OS2 format expectations and endian annotations. Inline data and EA areas share storage, so transitions must update mode bits consistently.

## Dependencies and integration points
It depends on JFS descriptor types such as `pxd_t`, `dxd_t`, `dtroot_t`, `xtroot_t`, and `dir_table_slot`. It is consumed by inode manager, extent tree, directory tree, xattr, symlink, and ioctl flag mapping code.

## Risks and test signals
Risks include layout/packing drift, endian mistakes, inline symlink/EA overlap, and flag mapping mismatches. Tests should cover fsck compatibility, fast/long symlinks, inline and external EAs, device inodes, directory indexes, and user-visible file flags after remount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dinode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_discard.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_discard.c

## Purpose
`jfs_discard.c` implements online discard issuing and FITRIM range handling for JFS.

## Important APIs, types, and functions
- `jfs_issue_discard()` calls `sb_issue_discard()` for a filesystem block range and logs success/failure.
- `jfs_ioc_trim()` converts user byte ranges to filesystem blocks, validates them against the block map, iterates allocation groups, and calls `dbDiscardAG()`.

## Control flow
FITRIM reaches `jfs_ioc_trim()` from `jfs_ioctl()`. The range is shifted to block units, `minlen` is rounded up to at least one block, `s_umount` is held read-side, invalid ranges are rejected, the end is clamped to the map size, and each AG overlapping the range is trimmed. The result length is the number of trimmed blocks converted back to bytes.

## State and persistence behavior
Discard commands inform the block device that free blocks may be unmapped. Logical filesystem allocation state is preserved; `dbDiscardAG()` may temporarily allocate free ranges before issuing discard and freeing them again.

## Dependencies and integration points
The file integrates with block discard support, JFS superblock/bmap state, dmap trimming, logging macros, and ioctl FITRIM handling.

## Risks and test signals
Risks include range conversion overflow, mount/unmount races, minlen mismatch with device granularity, and discard failures being logged but not changing allocation state. Tests should cover FITRIM on devices with/without discard, partial and full filesystem ranges, minlen filtering, concurrent allocation/free workloads, and online discard mount option interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_discard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_discard.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_discard.h

## Purpose
`jfs_discard.h` declares the JFS discard/FITRIM interfaces.

## Important APIs, types, and functions
- Forward declares `struct fstrim_range`.
- Exports `jfs_issue_discard()` and `jfs_ioc_trim()`.

## Control flow
`ioctl.c` calls `jfs_ioc_trim()` for FITRIM, while dmap freeing code calls `jfs_issue_discard()` for online discard when mount options request it.

## State and persistence behavior
The header has no state; it exposes functions that issue block-device discard while preserving filesystem allocation semantics.

## Dependencies and integration points
It integrates JFS ioctl and dmap code without exposing implementation details.

## Risks and test signals
Risks are declaration drift and missing includes for callers. Build tests should cover discard-enabled code paths and ioctl compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_discard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dmap.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_dmap.c

## Purpose
`jfs_dmap.c` implements the JFS aggregate block allocation map. It mounts and syncs the bmap descriptor, allocates/frees working-map blocks, updates persistent maps for transactions, manages allocation groups, supports filesystem extension, and implements trimming of free AG ranges.

## Important APIs, types, and functions
- Lifecycle: `dbMount()`, `dbUnmount()`, `dbSync()`, `dbFinalizeBmap()`, `dbMapFileSizeToMapSize()`.
- Allocation/free: `dbAlloc()`, `dbReAlloc()`, `dbFree()`, `dbAllocBottomUp()`, `dbExtendFS()`.
- Persistent transaction map update: `dbUpdatePMap()`.
- AG selection and trim: `dbNextAG()`, `dbDiscardAG()`.
- Core internals: `dbAllocAG()`, `dbAllocAny()`, `dbFindCtl()`, `dbAllocCtl()`, `dbAllocDmapLev()`, `dbAllocDmap()`, `dbFreeDmap()`, `dbAllocBits()`, `dbFreeBits()`.
- Buddy-tree mutation/search: `dbAdjCtl()`, `dbSplit()`, `dbBackSplit()`, `dbJoin()`, `dbAdjTree()`, `dbFindLeaf()`, `dbFindBits()`, `dbMaxBud()`.
- Initialization/validation: `check_dmapctl()`, `dbInitDmap()`, `dbInitDmapTree()`, `dbInitTree()`, `dbInitDmapCtl()`, `dbGetL2AGSize()`.

## Control flow
`dbMount()` reads logical block 0 of the bmap file, endian-converts descriptor fields, validates map and AG geometry, initializes active AG counters and the bmap mutex, and attaches the descriptor to the superblock. `dbSync()` writes the in-memory descriptor back, flushes bmap pages, and writes the special inode.

`dbAlloc()` rounds the request to a buddy size and follows a tiered policy: try immediately after the hint, then near the hint, then within the same dmap, then the same AG, then a preferred AG from `dbNextAG()`, and finally anywhere. Small bottom-up attempts hold a read dmap lock; top-down control-page searches hold a write lock. `dbReAlloc()` first tries in-place extension through `dbExtend()` and falls back to allocating a larger replacement extent.

`dbFree()` validates range bounds, optionally issues online discard, then frees one dmap at a time. `dbUpdatePMap()` updates persistent `pmap` bits under transaction logging and maintains metapage logsync LSN/CLSN state. `dbDiscardAG()` locks an AG, temporarily allocates large free ranges into a bounded array, unlocks, issues discard for those ranges, and frees them.

Actual allocation/free updates `wmap` bits and dmap buddy-tree leaves. If a dmap root changes, `dbAdjCtl()` recursively bubbles the new maximum-free-buddy value up L0/L1/L2 dmapctl pages and updates `db_maxfreebud` at the top. Initialization code reconstructs dmap and control trees during extend.

## State and persistence behavior
Persistent state includes `struct dbmap_disk`, dmap pages with `wmap`/`pmap`, and L0/L1/L2 dmapctl summary trees. Runtime state lives in `struct bmap`: map size, free counts, AG geometry, AG free arrays, max free buddy, active AG counters, and lock. `wmap` is working allocation state; `pmap` is transaction-persistent state updated by `dbUpdatePMap()`. Metapages carry dirty and logsync state until writeback.

## Dependencies and integration points
The allocator depends on JFS metapage I/O, inode locks, superblock geometry, transaction/log manager, imap/extent users, discard helpers, debug/error handling, and Linux memory allocation. File open/release tracks `db_active[]` to reduce fragmentation; extent allocation uses `dbAlloc()`/`dbReAlloc()`; free/truncate uses `dbFree()`.

## Risks and test signals
Risks are high: bitmap/tree inconsistency, incorrect AG free counts, lock-order violations (`IREAD/IWRITE_LOCK` with `BMAP_LOCK`), endian mistakes, multi-dmap allocation backout leaks, dmapctl corruption handling, `dbBackSplit()` edge cases, persistent-map logsync ordering, filesystem extension geometry changes, and FITRIM temporary allocation behavior. Tests should cover random allocate/free with invariant checking, ENOSPC paths, large multi-dmap extents, AG-boundary hints, concurrent writers, online discard/FITRIM, crash recovery of `pmap`, resize/extend, corrupted dmapctl pages, metapage I/O failures, and active AG preference under append workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dmap.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_dmap.h

## Purpose
`jfs_dmap.h` defines JFS block-map geometry, dmap/dmapctl/dbmap structures, conversion macros, buddy-tree helpers, and exported allocator APIs.

## Important APIs, types, and functions
- Geometry constants define dmap coverage (`BPERDMAP`), bitmap word sizes, tree sizes, control levels, maximum AGs, and maximum map sizes.
- Conversion macros map block numbers to dmap/control-page logical blocks (`BLKTODMAP`, `BLKTOL0`, `BLKTOL1`, `BLKTOCTL`) and AG numbers (`BLKTOAG`, `AGTOBLK`).
- Structures: `dmaptree`, `dmap`, `dmapctl`, `dbmap_disk`, `dbmap`, and in-memory `bmap`.
- Buddy helpers include `TREEMAX`, `BLKSTOL2`, `NLSTOL2BSZ`, `LITOL2BSZ`, `BUDSIZE`, and `BLKTOCTLLEAF`.
- Exports include mount/unmount, alloc/free/realloc, persistent-map update, sync, bottom-up allocation, extend, finalize, map-size calculation, and AG discard.

## Control flow
Allocator code uses the macros to locate the dmap page and control tree leaf for any aggregate block. Public callers operate on `ipbmap` and ranges; internal code in `jfs_dmap.c` interprets the structures and updates counts/trees.

## State and persistence behavior
`struct dbmap_disk`, `dmap`, and `dmapctl` are on-disk state with little-endian fields. `struct bmap` is the runtime descriptor attached to the superblock and includes a mutex, active AG counters, and converted free counts. `wmap` tracks working allocation; `pmap` tracks persistent allocation.

## Dependencies and integration points
It depends on JFS transaction types and is consumed by inode/extent/free-space/discard/resize code. Because it exposes geometry macros, changes affect every caller's block-to-map translation.

## Risks and test signals
Risks include arithmetic overflow, off-by-one control-page addresses, layout drift from on-disk format, and mismatch between macros and implementation assumptions. Tests should validate conversion macros over boundary blocks, all AG sizes, max map sizes, endian conversion, and allocation/free invariants after remount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dmap.h -->
