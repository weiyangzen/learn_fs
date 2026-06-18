# Group Research: group_1011_linux_stable_sources_os_linux_linux_stable_fs_jffs2_xattr_c_sources_011e20bbbd66

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/xattr.c

Complete JFFS2 extended-attribute engine for storing xattr name/value data (`xdatum`) and inode-to-xattr references (`xref`) as flash nodes. It handles lazy verification/loading after mount, deduplication of identical xattr data, VFS list/get/set operations, and GC relocation/release paths.

Key flows:
- `xattr_datum_hashkey()`, `load_xattr_datum()`, `save_xattr_datum()`, and `create_xattr_datum()` manage cached xattr data, CRC verification, hash indexing, flash writes, and memory pressure reclamation.
- `verify_xattr_ref()`, `save_xattr_ref()`, `create_xattr_ref()`, and `delete_xattr_ref()` manage xref nodes and sequence-number delete markers.
- `jffs2_build_xattr_subsystem()` merges duplicate refs, binds refs to inode caches and xdata, and classifies dead/orphan/unchecked records during mount build.
- `jffs2_listxattr()`, `do_jffs2_getxattr()`, and `do_jffs2_setxattr()` implement VFS xattr semantics, including create/replace/delete behavior and reserve-space/complete-reservation pairing.
- GC entry points `jffs2_garbage_collect_xattr_datum()` and `jffs2_garbage_collect_xattr_ref()` rewrite live xattr nodes and obsolete old raw refs.

Important state/locking:
- `c->xattr_sem` serializes most xattr subsystem mutations.
- `c->erase_completion_lock` protects raw-node chains and dead lists.
- Positive `JFFS2_XATTR_IS_CORRUPTED` return means unrecoverable corruption requiring node/ref deletion; negative errors are retryable/recoverable I/O or allocation failures.
- The cache uses `JFFS2_XFLAGS_HOT` and `JFFS2_XFLAGS_BIND` to avoid reclaiming active data while scanning/comparing duplicate names.

Integration points:
- Uses raw flash I/O (`jffs2_flash_read`, `jffs2_flash_write`, `jffs2_flash_writev`), reservation APIs, summary sizes, inode cache xref chains, CRC32, and xattr handler visibility checks.
- Exposes `jffs2_xattr_handlers[]` for user, trusted, optional security, and optional POSIX ACL prefixes.

Risk notes:
- Correctness depends on raw-node chain invariants where `next_in_ino` terminates at the owning object sentinel.
- Error handling around two-stage setxattr is delicate: xdatum write succeeds before xref reservation/write, so rollback must unreference the datum on xref failure.
- Duplicate-name cleanup chooses newest `xseqno`; any sequence-number ordering bug could expose stale attributes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/xattr.h

Defines the in-memory JFFS2 xattr model and public subsystem API.

Key structures:
- `struct jffs2_xattr_datum` represents one deduplicated xattr name/value payload, with raw node pointer, prefix, xid/version, CRC, hash key, cached name/value pointers, and refcount.
- `struct jffs2_xattr_ref` represents an inode-to-xdatum association, using unions so scan/build time stores raw inode/xid values and runtime stores `ic`/`xd` pointers.
- `XREF_DELETE_MARKER` marks deleted xrefs in the low bit of `xseqno`.

Feature gates:
- Under `CONFIG_JFFS2_FS_XATTR`, declares lifecycle, mount-build, inode cleanup, GC, get/set, listxattr, and handler symbols.
- Without xattr support, most APIs compile to no-op stubs and `jffs2_verify_xattr()` returns complete.
- Security xattrs are separately gated by `CONFIG_JFFS2_FS_SECURITY`.

Risk notes:
- The struct layout assumes first fields line up with raw-node ownership conventions used elsewhere in JFFS2.
- The scan/runtime union fields require callers to respect subsystem build phases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/xattr_trusted.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/xattr_trusted.c

Registers the `trusted.*` xattr handler for JFFS2.

Behavior:
- `jffs2_trusted_getxattr()` forwards reads to `do_jffs2_getxattr()` with `JFFS2_XPREFIX_TRUSTED`.
- `jffs2_trusted_setxattr()` forwards writes/deletes to `do_jffs2_setxattr()` with the trusted prefix.
- `jffs2_trusted_listxattr()` permits listing only for callers with `CAP_SYS_ADMIN`.
- Exports `jffs2_trusted_xattr_handler` using `XATTR_TRUSTED_PREFIX`.

Integration:
- Thin adapter over the shared implementation in `xattr.c`; policy is only list visibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/xattr_trusted.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/xattr_user.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/xattr_user.c

Registers the `user.*` xattr handler for JFFS2.

Behavior:
- `jffs2_user_getxattr()` forwards reads to `do_jffs2_getxattr()` with `JFFS2_XPREFIX_USER`.
- `jffs2_user_setxattr()` forwards writes/deletes to `do_jffs2_setxattr()` with the user prefix.
- Exports `jffs2_user_xattr_handler` using `XATTR_USER_PREFIX`.

Integration:
- No extra permission/list policy in this file; VFS/xattr core and shared JFFS2 xattr engine handle the work.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/xattr_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/jfs/Kconfig

Defines build-time JFS configuration.

Options:
- `JFS_FS`: tristate filesystem support, selecting buffer heads, NLS, UCS-2 helpers, CRC32, and legacy direct I/O.
- `JFS_POSIX_ACL`: optional POSIX ACL support, selecting `FS_POSIX_ACL`.
- `JFS_SECURITY`: optional security-label xattr support for LSMs such as SELinux.
- `JFS_DEBUG`: optional debug logging.
- `JFS_STATISTICS`: optional `/proc/fs/jfs/` statistics.

Integration:
- These symbols control conditional compilation in ACL, debug/proc, xattr/security, and Makefile object inclusion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/jfs/Makefile

Builds the JFS kernel module/object.

Composition:
- `obj-$(CONFIG_JFS_FS) += jfs.o`.
- Core `jfs-y` includes superblock, file/inode/namei, mount/unmount, xtree/dtree/imap/dmap, unicode, discard, extent, symlink, metapage, log/transaction manager, resize, xattr, and ioctl code.
- `acl.o` is included only when `CONFIG_JFS_POSIX_ACL` is enabled.

Integration:
- Confirms files in this group are part of the main JFS object, except ACL is feature-gated.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/acl.c

Implements POSIX ACL support on top of JFS extended attributes and transactions.

Key functions:
- `jfs_get_acl()` maps access/default ACL type to the corresponding xattr name, reads via `__jfs_getxattr()`, and decodes with `posix_acl_from_xattr()`.
- `__jfs_set_acl()` encodes ACLs with `posix_acl_to_xattr()` and stores/removes them via `__jfs_setxattr()`.
- `jfs_set_acl()` starts a transaction, locks `commit_mutex`, optionally updates inode mode through `posix_acl_update_mode()`, writes the ACL xattr, and commits.
- `jfs_init_acl()` derives default/access ACLs for newly created inodes and updates `mode2`.

Risk notes:
- RCU ACL lookup is unsupported and returns `-ECHILD`.
- ACL mode updates and xattr writes must remain in the same transaction to keep permissions consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/file.c

Defines regular-file inode/file operations and setattr/fsync behavior.

Key functions:
- `jfs_fsync()` writes dirty page-cache range, then either flushes journal or commits dirty inode synchronously.
- `jfs_open()` initializes quotas and tracks an active allocation group for newly opened empty writable regular files to reduce fragmentation.
- `jfs_release()` decrements active AG counters.
- `jfs_setattr()` validates attribute changes, handles quota initialization/transfer, truncates on size changes, marks inode dirty, and invokes ACL chmod updates.

Exports:
- `jfs_file_inode_operations`: listxattr, setattr, fileattr get/set, optional ACL get/set.
- `jfs_file_operations`: generic read/write/mmap/splice/llseek plus JFS fsync, release, ioctl, compat ioctl, and lease handling.

Risk notes:
- `jfs_setattr()` has a latent return-value sharp edge: if no earlier operation initializes `rc` after `setattr_prepare()`, the final return relies on the earlier zero path unless chmod runs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/inode.c

Handles inode instantiation, commit/writeback, eviction, block mapping, page-cache operations, direct I/O, and truncate.

Key functions:
- `jfs_iget()` loads an inode with `diRead()` and assigns operation tables based on file type, including fast symlink handling and special inode setup.
- `jfs_commit_inode()` and `jfs_write_inode()` coordinate transaction commits for dirty inodes and journal flushing.
- `jfs_evict_inode()` truncates pages, frees zero-link filesystem inodes, drops quota state, and releases active AG accounting.
- `jfs_get_block()` maps logical blocks through `xtLookup()`, records not-yet-recorded extents on write, or allocates via `extHint()`/`extAlloc()`.
- `jfs_aops` wires mpage read/write, block write begin/end, bmap, direct I/O, and buffer folio migration.
- `jfs_truncate()` and `jfs_truncate_nolock()` truncate extents transactionally, looping because `xtTruncate()` may not complete atomically.

Integration:
- Central bridge between VFS address-space operations, JFS extent tree (`xtree`), transaction manager, quota, and disk allocation map.

Risk notes:
- Fast symlink null termination guards against corrupt inline data.
- Direct-I/O write failures above `i_size` trigger cleanup via `jfs_write_failed()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/ioctl.c

Implements JFS file attribute operations and the FITRIM ioctl.

Key pieces:
- `jfs_map_ext2()` maps between internal JFS inode flags and generic `FS_*` fileattr flags.
- `jfs_fileattr_get()` rejects special dentries and returns visible user flags from `mode2`.
- `jfs_fileattr_set()` rejects fsx attrs/special files/quota files, masks unsupported bits, updates `mode2`, propagates inode flags, ctime, and dirty state.
- `jfs_ioctl()` handles `FITRIM`: requires `CAP_SYS_ADMIN`, checks discard support, copies `fstrim_range`, normalizes `minlen`, calls `jfs_ioc_trim()`, and copies results back.

Integration:
- Fileattr hooks are referenced by `jfs_file_inode_operations`.
- FITRIM path delegates actual block selection/discard to `jfs_discard.c` and `jfs_dmap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_acl.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_acl.h

Small ACL interface header.

Behavior:
- With `CONFIG_JFS_POSIX_ACL`, declares `jfs_get_acl()`, `jfs_set_acl()`, and `jfs_init_acl()`.
- Without ACL support, provides an inline `jfs_init_acl()` stub returning success.

Integration:
- Lets inode/name creation code call ACL initialization unconditionally while making ACL support optional.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_btree.h

Shared B+-tree definitions for JFS directory trees and extent trees.

Key content:
- Defines B-tree page flags: root, leaf, internal, rightmost, leftmost, swapped.
- Defines operation/order hints such as random/sequential lookup/insert/delete.
- Provides macros for root-vs-metapage access: `BT_IS_ROOT`, `BT_PAGE`, `BT_GETPAGE`, `BT_MARK_DIRTY`, and `BT_PUTPAGE`.
- Defines traversal stack structures `btframe` and `btstack`, plus push/pop/access macros.
- `BT_GETSEARCH` and `BT_PUTSEARCH` retrieve/release search-result pages.

Risk notes:
- Heavy macro use means callers must supply correct root field names and metapage variables.
- Root pages are embedded in inode memory, while non-root pages are metapages; dirty/release behavior differs by `BT_IS_ROOT()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_debug.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_debug.c

Creates optional JFS procfs debug/statistics entries.

Behavior:
- Compiled only when `PROC_FS_JFS` is defined by debug/statistics config plus procfs.
- Under `CONFIG_JFS_DEBUG`, exposes `/proc/fs/jfs/loglevel` with seq read and single-character write to update `jfsloglevel`.
- `jfs_proc_init()` creates `/proc/fs/jfs` and optional statistics/debug files: `lmstats`, `txstats`, `xtstat`, `mpstat`, `TxAnchor`, and `loglevel`.
- `jfs_proc_clean()` removes the proc subtree.

Risk notes:
- Loglevel write accepts only one ASCII digit and does not parse multi-digit input.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_debug.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_debug.h

Defines JFS debug, assert, and statistics macros.

Key behavior:
- `assert()` always prints a critical BUG message and calls `BUG()` on failure.
- With `CONFIG_JFS_DEBUG`, `ASSERT()` is active and `jfs_info/debug/warn/err` emit printk messages according to `jfsloglevel`.
- Without debug, `ASSERT()` and logging macros compile to no-ops.
- With `CONFIG_JFS_STATISTICS`, declares proc show functions and enables increment/decrement/high-watermark macros; otherwise those are no-ops.
- Defines `PROC_FS_JFS` when procfs and either debug/statistics are enabled.

Risk notes:
- Lowercase `assert()` remains fatal even outside `CONFIG_JFS_DEBUG`, while uppercase `ASSERT()` is gated.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dinode.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dinode.h

Defines the 512-byte on-disk JFS inode format and persistent mode/flag bits.

Structure:
- Base inode area stores identity, extent descriptor, size/block counts, link count, uid/gid/mode, timestamps, ACL/EA descriptors, directory index state, and ACL type.
- Extension union overlays directory inline index plus dtree root, regular-file xtree root, imap generator, device descriptor, fast symlink storage, and inline EA space.
- Macros provide named access to union overlays such as `di_dtroot`, `di_xtroot`, `di_fastsymlink`, and `di_inlineea`.

Flags:
- Defines JFS extended mode bits for journaling, sparse files, inline EA availability, swapfile, OS/2 attributes, archive/name flags, and Linux-visible file flags.
- `JFS_FL_USER_VISIBLE`, `JFS_FL_USER_MODIFIABLE`, and `JFS_FL_INHERIT` are used by ioctl/fileattr logic.

Risk notes:
- Layout compatibility with OS/2 JFS is explicit; changing union layout would be on-disk format breaking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_discard.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_discard.c

Implements discard/TRIM helpers for JFS.

Key functions:
- `jfs_issue_discard()` calls `sb_issue_discard()` for a block range and logs failures/info through JFS debug macros.
- `jfs_ioc_trim()` converts user byte range/minlen to filesystem blocks, validates against bmap state, clamps end to map size, computes allocation group range, and calls `dbDiscardAG()` for each AG.

Integration:
- Called from `FITRIM` ioctl and from allocation-map free paths when online discard is enabled.
- Uses `s_umount` read lock while consulting the bmap and trimming.

Risk notes:
- Trims entire allocation groups intersecting the requested range; fine-grained range filtering is effectively at AG selection granularity.
- Returns `-EINVAL` for missing bmap, too-large minlen, out-of-range start, or sub-block range length.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_discard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_discard.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_discard.h

Small discard interface header.

Exports:
- Forward declaration for `struct fstrim_range`.
- `jfs_issue_discard()` for issuing device discards.
- `jfs_ioc_trim()` for FITRIM handling.

Integration:
- Used by ioctl, dmap free/discard paths, and related JFS block management code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_discard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dmap.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dmap.c

Large JFS aggregate block allocation map implementation. It maintains working/persistent bitmaps, dmap summary trees, dmap control pages, allocation-group free counts, preferred AG selection, filesystem resize map extension, and discard enumeration.

Major areas:
- Mount/sync: `dbMount()` reads and validates the on-disk bmap descriptor, initializes locks/active AG counters; `dbSync()` writes it back; `dbUnmount()` syncs and frees state.
- Free/persistent update: `dbFree()` frees working-map blocks dmap by dmap and optionally issues online discard; `dbUpdatePMap()` updates persistent map bits and logsync metadata.
- Allocation policy: `dbAlloc()` tries next-to-hint, near-hint, same dmap, same AG, preferred AG, then anywhere; `dbNextAG()` avoids active writers and chooses an AG with average free space.
- Reallocation: `dbReAlloc()` first attempts in-place extension via `dbExtend()`, then falls back to allocating a larger new extent.
- Top-down search: `dbAllocAG()`, `dbAllocAny()`, `dbFindCtl()`, and `dbAllocCtl()` traverse dmapctl trees to find sufficient contiguous free space.
- Dmap mutation: `dbAllocDmap()`, `dbFreeDmap()`, `dbAllocBits()`, and `dbFreeBits()` update working bitmaps, leaf summaries, global/per-AG free counters, and parent control pages.
- Buddy tree maintenance: `dbSplit()`, `dbBackSplit()`, `dbJoin()`, `dbAdjTree()`, `dbFindLeaf()`, `dbFindBits()`, and `dbMaxBud()` maintain binary-buddy summaries over bitmap words/control pages.
- Discard: `dbDiscardAG()` temporarily allocates free extents within an AG, issues discard, then frees them again.
- Resize/init: `dbAllocBottomUp()`, `dbExtendFS()`, `dbFinalizeBmap()`, `dbInitDmap()`, `dbInitDmapTree()`, `dbInitTree()`, `dbInitDmapCtl()`, `dbGetL2AGSize()`, and `dbMapFileSizeToMapSize()` build or extend map coverage.

Serialization:
- Bottom-up dmap operations use `IREAD_LOCK`; top-down allocation/search uses `IWRITE_LOCK`.
- `BMAP_LOCK` protects aggregate counters such as `db_nfree`, `db_agfree`, `db_maxag`, and `db_agpref`.
- Busy metapages serialize persistent bitmap/control-page contents.

Integrity checks:
- `check_dmapctl()` validates dmapctl field ranges, tree shape, leaf index, height, budmin, leaf bounds, and leaf values before use.
- Allocation/free paths treat summary inconsistency as `-EIO` and call `jfs_error()` in several impossible-state branches.
- Multi-dmap allocation has a backout loop to avoid leaked blocks; failures during backout mark block leakage.

Risk notes:
- The allocator depends on precise buddy-tree invariants; incorrect split/join/backsplit handling can corrupt free-space summaries.
- Some bounds checks use assertions in paths where corrupt disk state may still be possible; newer explicit checks exist for dmapctl but not every dmap tree access.
- `dbDiscardAG()` intentionally mutates allocation state to find trim ranges, then restores it, so interruption/error paths are sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dmap.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dmap.h

Defines JFS block allocation map constants, on-disk structures, conversion macros, and exported allocator APIs.

Core model:
- A `dmap` covers 8192 blocks using 256 32-bit bitmap words plus a summary tree.
- `dmapctl` pages summarize lower-level dmaps/control pages through larger trees.
- `dbmap_disk` is the on-disk aggregate descriptor with map size, free counts, allocation-group geometry, per-AG free counts, and max free buddy.
- `struct bmap` wraps the descriptor in memory with the bmap inode, mutex, active AG counters, and optional map pointer.

Important macros:
- Tree sizes/indices: `TREESIZE`, `LEAFIND`, `CTLTREESIZE`, `CTLLEAFIND`, `ROOT`, `NOFREE`.
- Geometry: `BPERDMAP`, `L2BPERDMAP`, `MAXAG`, `MAXL0SIZE`, `MAXL1SIZE`, `MAXL2SIZE`, `MAXMAPSIZE`.
- Address conversion: `BLKTODMAP`, `BLKTOL0`, `BLKTOL1`, `BLKTOCTL`, `BMAPSZTOLEV`, `BLKTOAG`, `AGTOBLK`, `BLKTOCTLLEAF`.
- Buddy helpers: `TREEMAX`, `BLKSTOL2`, `NLSTOL2BSZ`, `LITOL2BSZ`, `BUDSIZE`.

Exports:
- Mount/sync/unmount, allocate/free/reallocate, persistent-map update, AG selection, bottom-up allocation, filesystem extension/finalization, map-size calculation, and AG discard.

Risk notes:
- Header encodes on-disk layout and page geometry; changes must preserve exact structure sizes and endian fields.
- Conversion macros are dense and assume the fixed three-level dmapctl layout.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dmap.h -->