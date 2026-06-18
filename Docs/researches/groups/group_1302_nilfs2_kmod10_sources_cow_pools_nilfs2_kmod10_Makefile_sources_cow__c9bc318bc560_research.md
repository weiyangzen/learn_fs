# Group Research: group_1302_nilfs2_kmod10_sources_cow_pools_nilfs2_kmod10_Makefile_sources_cow__c9bc318bc560

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/Makefile -->
# File Research: sources/cow-pools/nilfs2-kmod10/Makefile

Top-level recursive Makefile for the out-of-tree NILFS2 kernel module source tree. It sets `SUBDIRS = fs` and forwards `all`, `clean`, `install`, and `uninstall` into `fs` via `$(MAKE) -C $@ $(RULE)`.

There is no direct build logic here; target-specific `RULE` assignments translate top-level lifecycle targets to child targets.

Risk/notes: depends on GNU make target-specific variables and on child Makefiles supporting the same target names.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/Makefile -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/Makefile

Second-level recursive Makefile. It sets `SUBDIRS = nilfs2` and forwards `all`, `clean`, `install`, and `uninstall` into `fs/nilfs2`.

This keeps actual kbuild/module logic isolated in `fs/nilfs2/Makefile`.

Risk/notes: no fallback or validation; failures are delegated to the NILFS2 child Makefile.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/Makefile -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/Makefile

Kbuild/external-module Makefile for `nilfs2.ko`. It defaults `CONFIG_NILFS2_FS=m` for external builds, lists the composite object members, adds local include paths, optionally enables debug flags, detects `RHEL_RELEASE_N`, and disables unsupported xattr/POSIX ACL options for external builds.

External targets build against `/lib/modules/$(uname -r)/build`, install into `/lib/modules/<kver>/kernel/fs/nilfs2/`, run `depmod`, and include guarded load/unload behavior that refuses unload while NILFS2 mounts exist.

Risk/notes: Linux distribution assumptions are hardcoded (`/lib/modules`, `/sbin/depmod`, `/sbin/rmmod`, `modprobe`). The file explicitly supports external builds, not in-kernel tree builds.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/alloc.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/alloc.c

Implements the shared persistent allocator used by NILFS metadata files such as DAT and ifile. It organizes persistent objects into groups with descriptor blocks, bitmap blocks, and entry blocks, and uses `struct nilfs_palloc_req` as the prepare/commit/abort transaction carrier.

Key behavior includes group/block offset calculation, descriptor initialization, cached descriptor/bitmap/entry block lookup, free-slot search with little-endian bitmap helpers, single allocation/free transactions, batch freeing, empty entry/bitmap block deletion, and maximum-entry counting.

Concurrency: bitmap and descriptor updates use metadata block-group locks from `nilfs_mdt_bgl_lock`; allocator cache access is protected by a spinlock.

Risk/notes: descriptor free counts and bitmap bits must remain synchronized. Double-free paths warn but continue cleanup. Descriptor block initialization notes lack support for block sizes larger than page size.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/alloc.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/alloc.h

Public interface for NILFS persistent allocation. It exposes allocator initialization, entry block lookup, entry offset calculation, max-entry counting, allocation/free prepare-commit-abort APIs, batch freeing, and allocator cache lifecycle.

Important types:
- `struct nilfs_palloc_req`: entry number plus descriptor, bitmap, and entry buffer heads.
- `struct nilfs_bh_assoc`: cached block offset and buffer head.
- `struct nilfs_palloc_cache`: cached descriptor, bitmap, and entry buffers under a spinlock.

Risk/notes: callers must pair prepare/commit/abort correctly to avoid leaked buffer references or inconsistent allocation state.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/bmap.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/bmap.c

Generic NILFS block mapping layer. It wraps direct-map and B-tree implementations behind `struct nilfs_bmap_operations`, provides locking, converts internal corruption errors to filesystem errors, and translates DAT-backed virtual block numbers.

Key behavior includes lookup, contiguous lookup, insert/delete with direct/B-tree conversion, truncate-by-last-key deletion, dirty propagation, assignment of physical block numbers, GC bmap initialization, and bmap save/restore.

Concurrency: public operations use `b_sem` read/write locking. DAT and metadata bmaps get separate lockdep classes.

Risk/notes: missing DAT entries after bmap lookup are treated as metadata corruption. Pointer-type selection is coupled to special NILFS inode numbers.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/bmap.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/bmap.h

Core block-map abstraction header. It defines the bmap operation table, bmap state, pointer request union, stats structure, pointer type constants, dirty-state helpers, and public bmap APIs.

Pointer modes distinguish physical pointers, single-version DAT virtual pointers, multi-version DAT virtual pointers, and no pointer operations. Inline helpers bridge allocation/end operations to DAT or local pointer counters.

Risk/notes: several inline helpers assume the bmap semaphore is already held; misuse can race dirty-state and pointer updates.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/bmap.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btnode.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btnode.c

Implements the page-cache-backed cache for NILFS B-tree node blocks. It initializes node-cache inodes, creates node buffers, submits reads with optional DAT translation and readahead, deletes node buffers, and supports changing node cache keys.

The key-change path either moves an entire folio when block size equals page size or falls back to copying into a newly created buffer. Commit marks relocated buffers dirty; abort removes inserted folios or clears newly allocated buffers.

Risk/notes: duplicate node block address detection is treated as severe metadata inconsistency. Folio sizes larger than page size are explicitly unsupported in the key-change path.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btnode.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btnode.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btnode.h

Header for B-tree node cache operations. It declares cache initialization/clear, node block create/read/delete, and transactional prepare/commit/abort APIs for changing a node block key.

Central type: `struct nilfs_btnode_chkey_ctxt`, carrying old key, new key, old buffer, and optional new buffer.

Risk/notes: commit and abort have different cleanup semantics depending on whether full-folio move or copy-mode move was prepared.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btnode.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btree.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btree.c

Full B-tree implementation for large NILFS block mappings. It supplies bmap operations for lookup, contiguous lookup, insert, delete, dirty propagation, dirty-buffer collection, physical assignment, conversion from direct maps, and GC-specific assignment.

Key behavior:
- Manages traversal/mutation paths from `nilfs_btree_path_cache`.
- Defines node/root layout helpers, binary search, validation, and node readahead.
- Inserts using direct insert, carry-left/right, split, and grow operations.
- Deletes using borrow-left/right, concat-left/right, and shrink-root operations.
- Converts direct mappings into B-tree form.
- Propagates dirty state upward, updates DAT entries, and rekeys node-cache buffers when virtual block numbers change.
- Collects dirty node buffers by B-tree level for segment construction.
- Provides GC ops that mark/move DAT entries rather than normal lookup/insert/delete behavior.

Risk/notes: high-risk metadata code. Many paths require strict prepare/commit/abort ordering. Internal `-EINVAL` signals corrupted bmap state to the generic bmap layer.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btree.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btree.h

B-tree public header. It defines path state, node/root capacity macros, key bounds, exported B-tree initialization/conversion/GC functions, and node-block corruption checking.

Important type: `struct nilfs_btree_path`, which carries current and sibling buffers, child index, old/new pointer requests, node rekey context, and rebalance callback.

Risk/notes: capacity macros derive from on-disk structure layout and filesystem block size, so on-disk format changes must preserve these calculations.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/cpfile.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/cpfile.c

Implements the NILFS checkpoint metadata file. It maps checkpoint numbers to blocks and offsets, initializes checkpoint entries, reads and finalizes checkpoints, deletes ranges, enumerates checkpoints/snapshots, changes checkpoint mode, and reports checkpoint statistics.

Key behavior:
- Reads checkpoint state into a `nilfs_root`, including ifile inode state.
- Creates checkpoint entries idempotently and updates checkpoint/header counts.
- Finalizes checkpoint contents with root counters, block increment, creation time, flags, cno, and serialized ifile bmap.
- Deletes checkpoint ranges while preserving snapshots and deleting empty checkpoint blocks.
- Maintains a doubly linked snapshot list rooted in the cpfile header.
- Converts checkpoints to/from snapshots, refusing to clear mounted snapshots.
- Loads the cpfile inode after validating checkpoint entry size.

Concurrency: operations take `NILFS_MDT(cpfile)->mi_sem` in read or write mode and mutate mapped checkpoint/header buffers.

Risk/notes: snapshot list mutation spans multiple blocks plus the header. Deletion returns `-EBUSY` if snapshots are encountered. Missing or invalid checkpoint blocks are treated as metadata corruption in critical paths.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/cpfile.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/cpfile.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/cpfile.h

Public checkpoint-file interface. It declares checkpoint read/create/finalize/delete APIs, checkpoint mode changes, snapshot checks, checkpoint stats, checkpoint info enumeration, and cpfile inode loading.

Integration: consumed by mount/recovery/root management and ifile initialization.

Risk/notes: callers must distinguish valid checkpoint numbers from cno 0 and current/future checkpoint boundaries.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/cpfile.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dat.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dat.c

Implements the Disk Address Translation metadata file, mapping virtual block numbers to physical block numbers and lifetime ranges. It wraps the persistent allocator and owns DAT entry lifecycle.

Key behavior includes DAT entry allocation, start/end/update transactions, dirty marking, batch virtual block freeing, GC block moves through frozen redirected buffers, virtual-to-physical translation, vinfo export, and DAT inode initialization.

Risk/notes: DAT is central to NILFS copy-on-write semantics. `de_blocknr == 0` means no valid translation and returns `-ENOENT`. Several corruption paths return internal `-EINVAL` to upper bmap code.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dat.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dat.h

Public DAT interface. It declares translation, allocation/start/end/update prepare-commit-abort routines, dirty marking, batch free, GC move, vinfo export, and DAT inode read/init.

Integration: used by direct/B-tree bmaps, B-tree node cache reads, GC inode logic, and segment construction.

Risk/notes: the API is transactional; every prepare path has matching commit/abort expectations.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dir.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dir.c

Directory entry implementation derived from ext2-style directory handling and adapted for NILFS folio/page-cache and transaction helpers.

Key behavior includes record length conversion, directory folio validation, readdir, name lookup with cached start folio, `".."` lookup, link updates, link insertion, entry deletion by record merging, empty directory creation, empty-dir checks, and exported directory file operations.

Integration: writes route through `nilfs_prepare_chunk`, `nilfs_commit_chunk`, `nilfs_get_block`, `nilfs_set_file_dirty`, and inode time/dirty updates.

Risk/notes: directory corruption is reported with `nilfs_error` and `-EIO`. Several paths use local kmap pointers as release anchors, so pointer lifetime correctness is important.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/direct.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/direct.c

Direct block pointer implementation for small NILFS bmaps. It stores direct pointers inside the inode bmap area and provides the direct-map `nilfs_bmap_operations`.

Key behavior includes single/contiguous lookup, insert with physical or DAT-backed pointer allocation, delete with pointer ending, seek/last-key lookup, direct data gathering for conversion, B-tree-to-direct conversion after deletion, dirty propagation, and physical block assignment.

Risk/notes: direct insert receives a buffer-head pointer encoded in an integer-like `ptr` argument. Dirty propagation reports corruption if a dirty buffer maps to an invalid direct slot.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/direct.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/direct.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/direct.h

Header for direct bmap implementation. It defines direct block count and key bounds based on inode bmap storage size, and declares direct initialization plus delete-and-convert support.

Risk/notes: direct capacity is tied to `NILFS_BMAP_SIZE` and the on-disk inode bmap layout.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/direct.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/export.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/export.h

NFS/export support header for NILFS. It declares `nilfs_export_ops` and defines packed `struct nilfs_fid`.

The file identifier stores checkpoint number, inode number, inode generation, parent generation, and parent inode number. Including checkpoint number matters because NILFS can expose historical checkpoint/snapshot roots.

Risk/notes: packed field layout is externally significant for file-handle compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/export.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/file.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/file.c

Regular-file operations for NILFS. It defines fsync behavior, mmap write-fault handling, file operations, and inode operations.

Key behavior:
- `nilfs_sync_file` constructs a datasync or normal segment when the inode is dirty, then flushes the device.
- `nilfs_page_mkwrite` handles mmap write faults, rejects near-disk-full writes, fills holes inside a NILFS transaction, marks file blocks dirty, commits, and waits for writeback.
- Exports generic read/write/splice/ioctl/mmap/open/fsync hooks.
- Exports setattr, permission, fiemap, and file attribute inode hooks.

Risk/notes: mmap write faults wait for writeback because NILFS recovery validates log checksums including data blocks. Disk-full maps to `VM_FAULT_SIGBUS`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/gcinode.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/gcinode.c

Implements dummy GC inodes used to cache blocks being moved by garbage collection. These inodes hold data and B-tree node buffers outside normal dirty data paths.

Key behavior includes submitting GC reads for data blocks, submitting B-tree node reads through the btnode cache, waiting for read completion, validating node blocks, marking buffers dirty for relocation, initializing GC inodes, and removing all pending GC inodes.

Risk/notes: GC buffers use `b_blocknr` to preserve virtual block number identity after physical reads. Read errors and broken B-tree nodes abort relocation with `-EIO`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/gcinode.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ifile.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ifile.c

Implements the inode file, a metadata file storing on-disk NILFS inode records. It uses the shared persistent allocator.

Key behavior includes inode number allocation from `NILFS_FIRST_INO`, raw inode buffer lookup, inode deletion by clearing raw inode flags and freeing allocator state, inode block retrieval with validation, free inode counting, and ifile initialization for a checkpoint/root by reading cpfile state.

Risk/notes: inode allocation is non-wrapping here. Delete clears only `i_flags` before allocator free, relying on allocation state to control reuse.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ifile.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ifile.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ifile.h

Public inode-file interface. It provides inline helpers to map/unmap raw `struct nilfs_inode` records inside ifile entry buffers, plus declarations for inode create/delete/get, free inode counting, and ifile read/init.

The map helper uses `nilfs_palloc_entry_offset` and `kmap_local_folio`; callers must unmap with `nilfs_ifile_unmap_inode`.

Risk/notes: mapped raw inode pointers are local kmap addresses and must not outlive the calling context.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ifile.h -->