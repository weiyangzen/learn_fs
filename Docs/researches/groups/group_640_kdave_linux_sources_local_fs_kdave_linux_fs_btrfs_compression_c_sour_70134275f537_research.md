# Group Research: group_640_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_compression_c_sour_70134275f537

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/kdave-linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/compression.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/compression.c

Btrfs compressed I/O implementation for zlib, lzo, and zstd, including compressed read/write bio handling, compression workspace management, cached compression folios, and compressibility heuristics.

Key responsibilities:
- Maps compression types to strings, validates type names, parses compression levels, and clamps levels to algorithm-supported ranges.
- Allocates `compressed_bio` instances from a dedicated bioset and routes reads/writes through algorithm-specific compression/decompression backends.
- Maintains a global cached folio pool for compression pages, with shrinker integration and fallback allocation for larger block-size cases.
- Submits compressed writes, completes ordered extents, clears writeback on original file-cache folios, and frees compressed folios after I/O.
- Submits compressed reads by allocating folios for on-disk compressed data, optionally adding readahead pages from the same compressed extent, then decompressing into the original bio.
- Manages per-filesystem compression workspace managers for heuristic, zlib, lzo, and zstd paths, with preallocation and wait queues for forward progress.
- Provides inline/small decompression helpers and `btrfs_decompress_buf2page()` to copy decompressed buffers into requested bio ranges.
- Implements the compression heuristic using systematic sampling, byte-set size, core-byte distribution, repeated-pattern detection, and Shannon entropy estimation.

Dependencies:
- Uses Btrfs bio, ordered extent, extent map, extent I/O, subpage, inode, filesystem, and message infrastructure.
- Calls algorithm-specific helpers declared in `compression.h` and implemented in zlib/lzo/zstd modules.
- Depends on kernel folio/page cache APIs, biosets, shrinkers, PSI memstall accounting, wait queues, and GFP allocation controls.

Notable risks:
- Workspace allocation intentionally waits instead of returning errors; failed initial preallocation can still lead to low-memory retry loops.
- Compressed read readahead has special cases for subpage and block-size-greater-than-page-size filesystems, so behavior differs across sector/page configurations.
- `btrfs_compress_is_valid_type()` treats a matching prefix as valid, so callers must separately handle suffix parsing and option boundaries.
- Heuristic sampling assumes source pages are present and maps pages directly; callers must only use it in contexts where the page-cache range is valid.
- Bio length, folio order, sector alignment, and original bio advancement are tightly coupled and corruption-prone if caller invariants change.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/compression.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/compression.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/compression.h

Public Btrfs compression interface shared by compressed I/O, algorithm implementations, and defrag/compression callers.

Key responsibilities:
- Defines compressed extent limits: 128 KiB maximum on-disk compressed size, 128 KiB maximum uncompressed size, and 512 KiB worker chunk size.
- Defines `struct compressed_bio`, which wraps a `btrfs_bio` with file offset, logical length, compression type, writeback mode, and original read bio pointer.
- Provides helpers for deriving filesystem info from a compressed bio and computing per-folio input lengths.
- Declares global compression lifecycle, per-filesystem workspace manager allocation/free, compressed read/write submission, and compressed bio allocation.
- Defines `struct workspace_manager` for idle workspace lists, spinlock protection, counters, and waiters.
- Declares compression level metadata and algorithm-specific zlib, lzo, and zstd workspace/compress/decompress hooks.
- Provides `cleanup_compressed_bio()` for releasing all compressed folios attached to a compressed bio.

Dependencies:
- Includes Linux mm, list, workqueue, wait, and page-cache interfaces.
- Includes Btrfs bio, fs, and inode headers.
- Relies on UAPI compression type constants and Btrfs folio free helpers.

Notable risks:
- `compressed_bio` requires `bbio` to stay last because allocation embeds it through bioset offset arithmetic.
- Maximum compressed page count is derived from `PAGE_SIZE`; folio/block-size variants require matching assumptions in implementation code.
- Cleanup assumes every folio in the bio was allocated with `btrfs_alloc_compr_folio()`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/compression.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ctree.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ctree.c

Core Btrfs copy-on-write B-tree implementation, covering path allocation, key search, node/leaf balancing, block COW, insertion, deletion, item mutation, and tree traversal.

Key responsibilities:
- Allocates, releases, and frees `btrfs_path` objects through a slab cache, dropping locks and extent-buffer references consistently.
- Provides safe root-node reference acquisition with RCU and dirty-root tracking for cow-only roots.
- Copies roots for snapshots/relocation, decides when blocks can be shared, updates backrefs for COW, and performs forced or conditional block COW.
- Implements key comparison and binary search across leaf and node extent buffers, including fast little-endian key comparison.
- Reads child nodes with parent checks for level, transid, owner root, and first key.
- Implements `btrfs_search_slot()` and `btrfs_search_old_slot()`, including lock-level escalation, nowait reads, commit-root searches, tree-mod-log rewind, path restarts, readahead, and COW during modifying searches.
- Balances internal nodes during insertion and deletion, including promoting a single child to root, pushing pointers left/right, inserting new root levels, and splitting full nodes.
- Balances leaves by pushing items left/right, splitting leaves, avoiding double splits when possible, and maintaining parent low keys.
- Provides item mutation helpers for safe key update, item split, duplicate, truncate, extend, single/batch insertion, and deletion.
- Deletes empty leaves and tree pointers, frees tree blocks, and updates root used-byte accounting.
- Provides forward, backward, old-version, and next-item traversal helpers used by defrag, send, logging, and metadata walkers.
- Initializes and destroys the path slab cache.

Dependencies:
- Uses Btrfs transaction, locking, disk I/O, extent tree, qgroup, relocation, tree-mod-log, tree-checker, file-item, print-tree, and accessor infrastructure.
- Depends on extent buffers, Btrfs tree block allocation/freeing, delayed refs/backrefs, RCU root pointer replacement, lockdep nesting classes, and error injection hooks.

Notable risks:
- Search paths deliberately release and reacquire locks, returning `-EAGAIN` for restarts; callers must respect path invalidation rules.
- COW/backref logic distinguishes shareable roots, relocation roots, full backrefs, commit roots, and last-ref cases; mistakes can corrupt metadata ownership.
- Many helpers use `BUG_ON`, `WARN_ON`, and transaction aborts when invariants fail, so malformed metadata or incorrect caller state can take the filesystem read-only or crash debug paths.
- Leaf item layout is manually maintained with offset/size arrays growing opposite data storage; off-by-one or size accounting errors directly corrupt tree blocks.
- Parent low-key updates are required when slot 0 changes; callers using `btrfs_set_item_key_safe()` remain responsible for preserving key order.
- Old-root and commit-root searches rely on tree-mod-log and commit semaphore rules, with special cloning for callers that cannot block transaction commits.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ctree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ctree.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ctree.h

Primary in-memory Btrfs tree header defining path state, root state, root structure fields, tree sizing helpers, and the public ctree manipulation API.

Key responsibilities:
- Defines readahead modes for B-tree searches, including backward, forward, and full forward traversal modes.
- Defines `struct btrfs_path`, including nodes, slots, lock state, lowest level, readahead behavior, commit-root search flags, lock-retention flags, split/extension flags, and nowait mode.
- Provides cleanup macros for automatic path freeing or release.
- Enumerates `btrfs_root` state bits for transaction setup, shareability, dirty tracking, deletion, defrag, force-COW, log-tree state, qgroup flushing, orphan cleanup, unfinished drops, and relocation lockdep reset.
- Defines `struct btrfs_qgroup_swapped_blocks` and the large `struct btrfs_root`, covering tree roots, log roots, inode/delayed-node indexes, dirty lists, logging state, defrag progress, delalloc/ordered extents, relocation, send/dedupe/snapshot controls, qgroup reservations, swapfiles, and debug fields.
- Provides root flag and generation helpers using endian-aware fields and READ/WRITE_ONCE for concurrently read log transaction fields.
- Defines extent replacement and drop-extents argument structures used by file extent update paths.
- Defines leaf/node sizing helpers and maximum item/xattr calculations from filesystem node size.
- Declares core ctree APIs for search, COW, copy root, insert/delete, item mutation, traversal, path lifecycle, and old tree walks.
- Provides batch insertion structure and inline wrappers for single-item insertion/deletion and next-leaf/item traversal.
- Provides helpers identifying filesystem roots and data relocation roots.

Dependencies:
- Includes Linux cleanup, spinlock, rbtree, mutex, wait, list, atomic, xarray, and refcount APIs.
- Includes UAPI `linux/btrfs_tree.h`, plus Btrfs locking and accessors.
- Forward-declares major Btrfs structures to expose the ctree API without pulling full subsystem headers.

Notable risks:
- `struct btrfs_root` is a central cross-subsystem structure; field semantics and locking comments are part of many implicit contracts.
- Path flags strongly affect locking, COW, restart, and commit-root behavior; invalid flag combinations can deadlock or expose stale tree blocks.
- Several inline helpers depend on little-endian disk-key layout optimizations and must stay synchronized with on-disk structures.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ctree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/defrag.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/defrag.c

Btrfs metadata and file defragmentation implementation, including autodefrag inode queuing, B-tree leaf reallocation, and file extent rewrite selection.

Key responsibilities:
- Maintains an rb-tree of autodefrag inode records keyed by root objectid and inode number, recording transid and extent-size threshold.
- Queues inodes for autodefrag when the mount option is enabled and the filesystem is not closing, merging duplicate records by lowering transid and threshold.
- Picks, removes, and cleans pending autodefrag records under `defrag_inodes_lock`.
- Runs autodefrag in batches by resolving roots/inodes, clearing the in-memory defrag flag, and invoking `btrfs_defrag_file()` with a sector limit.
- Reallocates metadata tree leaves by walking shareable roots and forcing COW of non-nearby child blocks so disk order better matches key order.
- Tracks root defrag progress and maximum key across repeated transactions, returning `-EAGAIN` to continue incremental metadata defrag.
- Provides `btrfs_defrag_root()` loop with transaction boundaries, dirty btree balancing, closing/cancel checks, and `BTRFS_ROOT_DEFRAG_RUNNING` serialization.
- Looks up file extents for defrag without inserting extent maps into the inode cache, optionally using `btrfs_search_forward()` to skip older metadata.
- Filters file defrag targets by holes, inline extents, prealloc extents, generation, writeback marker, delalloc state, size threshold, max extent capacity, compression mode, and adjacency/merge potential.
- Prepares folios for defrag by locking, rejecting untested large folios in non-experimental builds, waiting on ordered extents, reading missing data, and ensuring uptodate state.
- Converts selected ranges to delalloc plus `EXTENT_DEFRAG`, reserves/release delalloc space, dirties relevant folio ranges, and handles compressed/no-compress defrag options.
- Processes files in 256 KiB clusters with readahead, max-sector limits, cancellation checks, inode locking, swapfile rejection, and optional immediate writeback.
- Initializes and destroys the autodefrag inode-record slab cache.

Dependencies:
- Uses Btrfs ctree, disk I/O, transaction, locking, accessors, delalloc space, subpage, file-item, super, compression, extent map, and extent I/O infrastructure.
- Depends on page cache, file readahead, writeback throttling, superblock write guards, rbtrees, slab caches, and signal cancellation via `btrfs_defrag_cancelled()`.

Notable risks:
- Autodefrag records can outlive in-memory inode instances, so runtime inode flags are advisory and duplicate rb-tree detection is required.
- File defrag locks folios and extent ranges, waits for ordered extents, and reserves delalloc space; lock ordering is carefully arranged to avoid deadlocks.
- Target collection intentionally skips delalloc ranges and writeback-marked extents; changing these rules can create deadlocks or unnecessary I/O.
- Metadata defrag only operates on shareable roots and uses forced COW, which changes tree block placement while preserving transactional invariants.
- Compression defrag changes inode `defrag_compress` state while the inode is locked and must clear it at the end.
- Non-experimental builds reject large folios with `-ETXTBSY`, so behavior depends on kernel config and page-cache folio state.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/defrag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/defrag.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/defrag.h

Small Btrfs defragmentation interface header for file defrag, autodefrag lifecycle, queued inode processing, root defrag, and cancellation checks.

Key responsibilities:
- Declares `btrfs_defrag_file()` for ioctl/autodefrag file extent rewriting over a range with generation and sector-count limits.
- Declares autodefrag slab-cache init/exit functions.
- Declares queue, run, and cleanup helpers for autodefrag inode records.
- Declares `btrfs_defrag_root()` for metadata tree defragmentation.
- Provides `btrfs_defrag_cancelled()`, currently implemented as a signal-pending check on the current task.

Dependencies:
- Includes Linux integer and compiler-type definitions.
- Forward-declares Btrfs inode, filesystem info, root, transaction, ioctl range args, and `file_ra_state`.

Notable risks:
- Cancellation is signal-based only; callers needing filesystem-wide cancellation must combine it with closing/remount checks.
- The header exposes both file and metadata defrag entry points, which have different locking and transaction expectations.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/defrag.h -->