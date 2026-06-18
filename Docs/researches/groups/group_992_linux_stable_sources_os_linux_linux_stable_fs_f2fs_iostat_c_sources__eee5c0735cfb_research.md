# Group Research: group_992_linux_stable_sources_os_linux_linux_stable_fs_f2fs_iostat_c_sources__eee5c0735cfb

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/iostat.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/iostat.c

## Purpose

`iostat.c` implements F2FS runtime I/O accounting and latency tracing when `CONFIG_F2FS_IOSTAT` is enabled. It tracks per-superblock byte/count totals, periodic deltas for tracepoints, read folio order statistics, and bio-level latency classified by read/write and page type.

## Main Responsibilities

- Expose a proc-style sequence view through `iostat_info_seq_show()`.
- Maintain cumulative `sbi->iostat_bytes[]` and `sbi->iostat_count[]`.
- Emit periodic `trace_f2fs_iostat()` delta events.
- Track per-bio latency through a mempool-backed `bio_iostat_ctx`.
- Reset and initialize per-filesystem iostat state.
- Initialize and destroy the global bio context slab/mempool.

## Key Functions

- `iostat_info_seq_show()`
  - Returns no output if `sbi->iostat_enable` is false.
  - Prints current time and byte/count/average rows for write, read, and other I/O categories.
  - Includes application data I/O, compressed-data variants, filesystem data/node/meta I/O, GC/checkpoint I/O, discard, flush, zone reset, and read folio order counts.

- `iostat_get_avg_bytes()`
  - Computes average bytes per counted I/O type.
  - Avoids divide-by-zero by returning `0` when count is absent.

- `f2fs_record_iostat()`
  - Periodically snapshots deltas from cumulative counters.
  - Uses `sbi->iostat_next_period` and `sbi->iostat_period_ms`.
  - Double-checks the period under `sbi->iostat_lock`.
  - Updates previous byte/read-folio counters and emits `trace_f2fs_iostat()`.
  - Calls `__record_iostat_latency()` after byte/count tracing.

- `__record_iostat_latency()`
  - Copies `sbi->iostat_io_lat` into a local trace payload under `sbi->iostat_lat_lock`.
  - Converts jiffies to milliseconds for peak and average latency.
  - Resets accumulated latency state after copying.
  - Emits `trace_f2fs_iostat_latency()`.

- `f2fs_reset_iostat()`
  - Clears byte counters, count counters, previous counters, read folio order counters, and latency state.
  - Uses separate locks for byte/count state and latency state.

- `f2fs_update_read_folio_count()`
  - Counts read folio orders, clamping orders above `NR_PAGE_ORDERS - 1`.
  - Triggers periodic iostat tracing afterward.

- `f2fs_update_iostat()`
  - Updates one `enum iostat_type` byte/count pair.
  - Also aggregates buffered/direct app writes into `APP_WRITE_IO`.
  - Also aggregates buffered/direct app reads into `APP_READ_IO`.
  - Under compression, mirrors selected logical data I/O types into compressed-data counters when the inode is compressed.

- `iostat_alloc_and_bind_ctx()`
  - Allocates a `bio_iostat_ctx` from the global mempool.
  - Stores `sbi`, submit timestamp placeholder, page type placeholder, and optional post-read context.
  - Replaces `bio->bi_private` with the iostat context.

- `iostat_update_and_unbind_ctx()`
  - Classifies completed bios as `READ_IO`, `WRITE_SYNC_IO`, or `WRITE_ASYNC_IO`.
  - Restores `bio->bi_private` to the `f2fs_sb_info` for writes and post-read context for reads.
  - Records latency and frees the context.

- `f2fs_init_iostat_processing()` / `f2fs_destroy_iostat_processing()`
  - Manage the global `f2fs_bio_iostat_ctx` slab and mempool.

- `f2fs_init_iostat()` / `f2fs_destroy_iostat()`
  - Initialize per-superblock locks, defaults, disabled state, and latency storage.
  - Free per-superblock latency storage at teardown.

## Important State

- `sbi->iostat_lock`
  - Protects byte/count/read-folio counters and previous snapshots.

- `sbi->iostat_lat_lock`
  - Protects accumulated latency arrays.

- `sbi->iostat_enable`
  - Main runtime gate for accounting.

- `sbi->iostat_period_ms`
  - Periodic trace interval; initialized to `DEFAULT_IOSTAT_PERIOD_MS`.

- `bio_iostat_ctx_pool`
  - Guarantees bio context allocation for iostat instrumentation.

## Interactions

- Called from data, node, segment, checkpoint, GC, file, and compression paths to account I/O.
- `sysfs.c` controls `iostat_enable` and `iostat_period_ms`.
- `data.c` binds/unbinds bio contexts and updates submit timestamps.
- Tracepoints under `trace/events/f2fs.h` consume periodic byte/count and latency snapshots.

## Concurrency and Error Handling

- Counter updates use IRQ-safe spinlocks.
- Periodic tracing is intentionally best-effort and avoids tracing more frequently than configured.
- Latency accounting validates `page_type`; `META_FLUSH` is normalized to `META`, while out-of-range page types warn and are ignored.
- Global allocation setup returns `-ENOMEM` on slab or mempool creation failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/iostat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/iostat.h -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/iostat.h

## Purpose

`iostat.h` declares the F2FS iostat interface and provides no-op stubs when `CONFIG_F2FS_IOSTAT` is disabled. It defines latency classes, tunables, per-bio iostat context layout, and small inline helpers used by bio submission/completion paths.

## Main Contents

- `enum iostat_lat_type`
  - `READ_IO`
  - `WRITE_SYNC_IO`
  - `WRITE_ASYNC_IO`
  - `MAX_IO_TYPE`

- Iostat constants under `CONFIG_F2FS_IOSTAT`
  - `NUM_PREALLOC_IOSTAT_CTXS`: mempool size for bio contexts.
  - `DEFAULT_IOSTAT_PERIOD_MS`: default periodic trace interval.
  - `MIN_IOSTAT_PERIOD_MS`: minimum sysfs period.
  - `MAX_IOSTAT_PERIOD_MS`: maximum period, documented as one day.

- `struct iostat_lat_info`
  - `sum_lat[MAX_IO_TYPE][NR_PAGE_TYPE]`
  - `peak_lat[MAX_IO_TYPE][NR_PAGE_TYPE]`
  - `bio_cnt[MAX_IO_TYPE][NR_PAGE_TYPE]`

- `struct bio_iostat_ctx`
  - Stores the owning `f2fs_sb_info`.
  - Stores submit timestamp in jiffies.
  - Stores F2FS `enum page_type`.
  - Preserves `struct bio_post_read_ctx *` for read bios.

## Exported Interface

When enabled, the header declares:

- `iostat_info_seq_show()`
- `f2fs_reset_iostat()`
- `f2fs_update_iostat()`
- `f2fs_update_read_folio_count()`
- `iostat_update_and_unbind_ctx()`
- `iostat_alloc_and_bind_ctx()`
- `f2fs_init_iostat_processing()`
- `f2fs_destroy_iostat_processing()`
- `f2fs_init_iostat()`
- `f2fs_destroy_iostat()`

## Inline Helpers

- `iostat_update_submit_ctx()`
  - Assumes `bio->bi_private` points to `bio_iostat_ctx`.
  - Records `jiffies` and F2FS page type at submission.

- `get_post_read_ctx()`
  - Returns the saved post-read context from the wrapped bio private data.

## Disabled Build Behavior

When `CONFIG_F2FS_IOSTAT` is not set:

- Update and lifecycle routines compile to no-ops.
- Initialization returns success.
- `get_post_read_ctx()` returns `bio->bi_private` directly, preserving normal post-read behavior without iostat wrapping.

## Interactions

- Implemented by `iostat.c`.
- Used by data bio submission/completion paths.
- Depends on `NR_PAGE_TYPE`, `enum page_type`, `enum iostat_type`, and `struct f2fs_sb_info` definitions from core F2FS headers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/iostat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/namei.c

## Purpose

`namei.c` implements F2FS namespace operations for the Linux VFS: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, tmpfile, rename, whiteout, parent lookup, and inode operation tables. It also applies F2FS-specific inode creation policy such as extension-based hot/cold classification, compression inheritance, inline-data setup, project quota inheritance, encryption preparation, and inline xattr/dentry setup.

## Extension and Temperature Policy

- `is_extension_exist()`
  - Matches filename extensions case-insensitively.
  - Supports wildcard `"*"`.
  - Handles temporary-extension matching for patterns such as media files with an additional temp suffix.

- `is_temperature_extension()`
  - Uses relaxed temporary-extension matching for hot/cold data classification.

- `is_compress_extension()`
  - Uses stricter dot-aware matching for compression allow/deny extension lists.

- `f2fs_update_extension_list()`
  - Adds or removes hot/cold extension entries in `raw_super->extension_list`.
  - Maintains cold count in little-endian `extension_count` and hot count in `hot_ext_count`.
  - Preserves layout where cold extensions precede hot extensions.
  - Rejects duplicates, missing removals, and full extension lists.

- `set_file_temperature()`
  - Marks newly created files cold or hot based on superblock extension lists, unless extension identification is disabled.

## Compression Policy for New Inodes

- `set_compress_new_inode()`
  - Applies only when compression is supported.
  - Directories inherit compression/no-compression policy.
  - Regular files may be excluded if their filename matches a hot extension.
  - `nocompress` extensions override compression.
  - `compress` extensions enable compression context.
  - Otherwise compression flags may be inherited from the parent directory.

## Inode Creation

- `f2fs_new_inode()`
  - Allocates a VFS inode and an F2FS nid.
  - Initializes owner, timestamps, generation, directory depth, project quota, encryption, quota state, and F2FS inode flags.
  - Sets `FI_NEW_INODE`, optional `FI_EXTRA_ATTR`, `FI_INLINE_XATTR`, `FI_INLINE_DENTRY`, `FI_PROJ_INHERIT`, `FI_INLINE_DATA`, and encryption state.
  - Computes inline xattr size from flexible-inline-xattr support and mount options.
  - Inherits masked F2FS flags from parent and sets indexed directory flag for directories.
  - Initializes extent tree and emits `trace_f2fs_new_inode()`.
  - On failure, marks the inode bad and, if needed, marks `FI_FREE_NID` so later cleanup can return the nid.

## VFS Namespace Operations

- `f2fs_create()`
  - Checks checkpoint error and checkpoint readiness.
  - Initializes parent quota.
  - Creates a regular file inode, assigns file operations, and adds a directory entry under `f2fs_lock_op()`.
  - Completes nid allocation with `f2fs_alloc_nid_done()`.
  - Instantiates the dentry and performs dirsync if required.

- `f2fs_link()`
  - Prepares fscrypt link context.
  - Enforces project quota inheritance compatibility.
  - Increments link state through `FI_INC_LINK`.
  - Adds a new directory entry for an existing inode.
  - Rolls back link increment and inode reference on failure.

- `f2fs_get_parent()`
  - Resolves `..` by looking up `dotdot_name` and returning an alias for the parent inode.

- `f2fs_lookup()`
  - Validates name length.
  - Prepares encrypted/casefolded lookup name.
  - Finds the directory entry and loads the inode.
  - Rejects zero-link inodes as corruption.
  - Verifies encryption context compatibility for encrypted directory children.
  - Avoids negative dentry caching for Unicode casefolded directories.

- `f2fs_unlink()`
  - Finds the target entry, validates link count invariants, acquires orphan inode capacity, deletes the entry, and optionally invalidates casefolded dentries.
  - Marks serious link-count inconsistencies as `SBI_NEED_FSCK`.

- `f2fs_get_link()`
  - Wraps `page_get_link()` and treats empty symlink content as broken, returning `-ENOENT`.

- `f2fs_symlink()`
  - Prepares encrypted symlink target if required.
  - Creates symlink inode and directory entry.
  - Encrypts and writes symlink data.
  - Flushes symlink data to reduce broken symlink risk after power loss.
  - Unlinks the dentry on data-write failure after instantiation.

- `f2fs_mkdir()`
  - Creates a directory inode with dir operations and nofs mapping GFP mask.
  - Uses `FI_INC_LINK` while adding the directory entry.
  - Instantiates and optionally dirsyncs.

- `f2fs_rmdir()`
  - Delegates to `f2fs_unlink()` only if `f2fs_empty_dir()` succeeds.

- `f2fs_mknod()`
  - Creates special inode, initializes device type, adds link, and instantiates.

- `__f2fs_tmpfile()`
  - Shared implementation for tmpfile and whiteout creation.
  - Creates unlinked regular or whiteout inode.
  - Acquires orphan inode slot and adds the inode to the orphan list.
  - For whiteouts, marks inode linkable for rename whiteout handling.
  - For real tmpfiles, calls `d_tmpfile()` when a file is available.

- `f2fs_tmpfile()`
  - Public VFS tmpfile hook.
  - Checks checkpoint state and calls `finish_open_simple()`.

- `f2fs_create_whiteout()`
  - Creates a whiteout inode for `RENAME_WHITEOUT`.

- `f2fs_get_tmpfile()`
  - Helper for creating an unlinked regular inode without a `struct file`.

## Rename Paths

- `f2fs_rename()`
  - Handles normal rename, replacement, and whiteout.
  - Checks checkpoint state, project quota inheritance compatibility, quotas, and inline-dir conversion where needed.
  - If replacing an existing inode:
    - Ensures replaced directory is empty.
    - Repoints the new entry to the old inode.
    - Decrements replaced inode link count and manages orphan entry.
  - If not replacing:
    - Adds a new link in the destination directory.
    - Updates destination directory link count for directory moves.
  - Updates old inode parent tracking or marks lost parent ino.
  - Deletes the old entry.
  - Adds whiteout at the old name if requested.
  - Updates `..` for moved directories.
  - Adds strict-fsync transition directory ino entries when configured.
  - Dirsyncs when either directory requires it.

- `f2fs_cross_rename()`
  - Implements `RENAME_EXCHANGE`.
  - Locates both entries and, for directory operands crossing parents, locates both `..` entries.
  - Checks project quota inheritance on both sides.
  - Computes parent link-count adjustments for file/directory exchanges across directories.
  - Swaps directory entries and updates parent ino metadata.
  - Updates directory link counts and strict-fsync tracking.

- `f2fs_rename2()`
  - Validates supported flags: `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, `RENAME_WHITEOUT`.
  - Runs `fscrypt_prepare_rename()`.
  - Dispatches to exchange or normal rename.
  - Emits rename tracepoints.

## Symlink and Inode Operation Tables

- `f2fs_encrypted_get_link()`
  - Reads symlink page and calls `fscrypt_get_symlink()`.

- `f2fs_encrypted_symlink_getattr()`
  - Combines F2FS getattr with fscrypt symlink size adjustment.

- Operation tables:
  - `f2fs_encrypted_symlink_inode_operations`
  - `f2fs_dir_inode_operations`
  - `f2fs_symlink_inode_operations`
  - `f2fs_special_inode_operations`

## Consistency and Recovery Hooks

- Namespace mutations are guarded by checkpoint error/readiness checks.
- Operations that alter metadata use `f2fs_lock_op()` where appropriate.
- Deletions/replacements acquire orphan inode capacity before removing links.
- Dirsync directories trigger `f2fs_sync_fs()`.
- Strict fsync mode records transitioned directories for recovery.
- Corruption signals set `SBI_NEED_FSCK` and return `-EFSCORRUPTED`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/node.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/node.c

## Purpose

`node.c` implements F2FS node and NAT management. It is responsible for node address translation, NAT cache state, free nid discovery/allocation, node-page lookup/allocation/truncation, node writeback/fsync ordering, roll-forward recovery helpers, NAT checkpoint flushing, node manager initialization, and cache teardown.

## Core Concepts

- NAT maps nid to node owner inode, physical block address, and version.
- Free nids are derived from NAT entries whose block address is `NULL_ADDR`.
- Node pages form the file block-index tree: inode node, direct nodes, indirect nodes, and double-indirect nodes.
- Dirty NAT entries are grouped by NAT block offset into `nat_entry_set` objects for checkpoint flushing.
- Dirty node pages are written copy-on-write style, then NAT entries are updated to the newly allocated node block.
- Fsync node pages are tracked in sequence order to support atomic/fsync recovery semantics.

## Memory Pressure

- `f2fs_available_free_memory()`
  - Provides type-specific memory admission decisions for free nids, NAT entries, dirty dentries, ino entries, extent caches, discard cache, and compressed pages.
  - Uses system low memory, F2FS thresholds, dirty-writeback pressure, and cache counts.
  - Prevents excessive NAT caching via `excess_cached_nats()`.

## NAT Cache Management

- `f2fs_check_nid_range()`
  - Rejects nids below root ino or beyond `max_nid`.
  - Marks filesystem for fsck and reports corruption.

- `get_current_nat_folio()` / `get_next_nat_folio()`
  - Read the current NAT block or copy it to the alternate NAT block.
  - `get_next_nat_folio()` flips the NAT bitmap to the next copy.

- `__alloc_nat_entry()` / `__free_nat_entry()`
  - Allocate/free cached NAT entries.
  - New entries receive nid and reset checkpoint/fsync flags.

- `__init_nat_entry()`
  - Inserts NAT entry into the radix tree.
  - Initializes from raw NAT when available.
  - Places clean entries on reclaimable LRU or initializes dirty entries for checkpoint state.

- `__lookup_nat_cache()`
  - Looks up cached NAT entry.
  - Moves clean, non-dirty lookup hits to the tail of the reclaimable list when not being dirtied.

- `__set_nat_cache_dirty()`
  - Marks a NAT entry dirty.
  - Groups non-preallocation updates under a `nat_entry_set`.
  - Tracks dirty NAT count and reclaimable count.
  - Treats `NEW_ADDR` entries as preallocated and not yet assigned to a NAT block set.

- `__clear_nat_cache_dirty()`
  - Moves flushed entries back to clean reclaimable NAT list.
  - Updates dirty/reclaimable counters and set entry counts.

- `set_node_addr()`
  - Central NAT state transition routine.
  - Allocates or reuses a NAT cache entry.
  - Handles reallocation to `NEW_ADDR`, deletion to `NULL_ADDR`, and valid block address updates.
  - Increments NAT version when a node is removed.
  - Marks entries dirty and updates fsync-related NAT flags.
  - Maintains inode NAT flags for last fsync and fsynced inode tracking.

- `f2fs_get_node_info()`
  - Resolves node info from NAT cache, current NAT journal, or NAT block.
  - Avoids lock-order issues around checkpoint and journal locks by retrying when needed.
  - Validates resolved block address and quota-file NAT consistency.
  - Caches NAT entries outside checkpoint-sensitive paths.

- `f2fs_try_to_free_nats()`
  - Shrinks reclaimable clean NAT cache entries from the LRU list.

## Fsync Node Tracking

- `f2fs_init_fsync_node_info()`
  - Initializes fsync node list, lock, sequence id, and count.

- `f2fs_add_fsync_node_entry()`
  - Records a folio in fsync write order and returns its sequence id.

- `f2fs_del_fsync_node_entry()`
  - Removes a completed fsync node entry and drops the folio reference.

- `f2fs_reset_fsync_node_info()`
  - Resets fsync segment sequence id.

- `f2fs_need_dentry_mark()`
  - Determines whether an inode node needs a dentry mark for roll-forward recovery.

- `f2fs_is_checkpointed_node()`
  - Reports whether a nid is known checkpointed.

- `f2fs_need_inode_block_update()`
  - Checks NAT fsync flags to decide whether inode block update is required.

## Node Tree Pathing and Lookup

- `get_node_path()`
  - Converts a logical data block index into offsets through the F2FS node tree.
  - Handles direct inode addresses, two direct nodes, two indirect-node regions, and one double-indirect region.
  - Returns path level or `-E2BIG`.

- `f2fs_get_next_page_offset()`
  - Computes next page offset after an absent node lookup, allowing callers to skip unmapped ranges.

- `f2fs_get_dnode_of_data()`
  - Walks inode/direct/indirect/double-indirect node path to locate the dnode for a logical page index.
  - Can allocate missing nodes in `ALLOC_NODE` mode.
  - Can perform sibling readahead in `LOOKUP_NODE_RA` mode.
  - Detects self-referential node mapping corruption.
  - Handles inline-data special case.
  - Updates compressed read extent cache on readonly compressed files when clusters are contiguous.
  - Returns enough level/offset context on `-ENOENT` for callers to skip forward.

## Node Truncation and Removal

- `truncate_node()`
  - Invalidates the node block, decrements valid node/inode counts, updates NAT to `NULL_ADDR`, clears dirty page state, and invalidates node mapping page.
  - Removes orphan inode and marks inode synced for inode nodes.

- `truncate_dnode()`
  - Loads a direct node, validates ownership, truncates all data blocks in it, and removes the node.

- `truncate_nodes()`
  - Recursively truncates indirect and double-indirect subtrees.
  - Clears nid pointers in parent nodes and tracks whether parent changed.

- `truncate_partial_nodes()`
  - Handles partial truncation along an indirect path before whole-subtree truncation.

- `f2fs_truncate_inode_blocks()`
  - Removes all node/data block references from a given logical offset onward.
  - Handles direct, indirect, and double-indirect regions.
  - Marks fsck-needed on invalid node references but may continue when possible.

- `f2fs_truncate_xattr_node()`
  - Removes the external xattr node and clears inode xattr nid.

- `f2fs_remove_inode_page()`
  - Removes an inode node after truncating xattr node and possible inline-data block.
  - Validates unexpected `i_blocks` values and respects checkpoint error state.

## Node Allocation and Reading

- `f2fs_new_inode_folio()`
  - Allocates the inode node page for a new inode.

- `f2fs_new_node_folio()`
  - Allocates a node cache folio and increments valid node count.
  - Initializes NAT state to `NEW_ADDR`.
  - Fills node footer and cold-node mark.
  - Marks page dirty and records xattr nid when allocating xattr node.
  - Increments valid inode count for inode node offset `0`.

- `read_node_folio()`
  - Reads a node page from the block address resolved through NAT.
  - Rejects `NULL_ADDR`/`NEW_ADDR`.
  - Verifies checksum for already uptodate pages.
  - Accounts node read I/O through iostat.

- `f2fs_ra_node_page()`
  - Readaheads a node page if it is not already cached.

- `f2fs_sanity_check_node_footer()`
  - Validates footer nid and expected node type.
  - Distinguishes regular, inode, xattr, and non-inode node expectations.
  - Marks fsck-needed and reports `ERROR_INCONSISTENT_FOOTER` on mismatch.

- `__get_node_folio()`
  - Shared locked node-folio acquisition path.
  - Reads from disk if needed, handles retry if folio identity changes, verifies uptodate state, checksum, and footer consistency.
  - Optional parent-based readahead.

- Public wrappers:
  - `f2fs_get_node_folio()`
  - `f2fs_get_inode_folio()`
  - `f2fs_get_xnode_folio()`

## Node Writeback

- `flush_inline_data()`
  - Flushes dirty inline data for an inode before inode eviction/writeback conflicts.

- `last_fsync_dnode()`
  - Finds the last dirty warm dnode for an inode, used to mark the final fsync node during atomic fsync.

- `__write_node_folio()`
  - Core node writeback routine.
  - Handles checkpoint error, POR in-progress, and asynchronous warm dnode deferral.
  - Validates node footer and NAT block address.
  - Applies preflush/FUA for atomic writes unless barriers are disabled.
  - Sets fsync and dentry marks.
  - Adds warm fsync nodes to global sequence list before clearing dirty state.
  - Calls `f2fs_do_write_node_page()`, updates NAT via `set_node_addr()`, decrements dirty node page count, and optionally balances filesystem state.

- `f2fs_write_single_node_folio()`
  - Writes one node folio for GC or synchronous callers.

- `f2fs_move_node_folio()`
  - Moves a node folio during GC using foreground/background sync mode.

- `f2fs_fsync_node_pages()`
  - Writes dirty warm dnodes for a specific inode.
  - Marks the final atomic fsync dnode.
  - Updates inode page if dirty inode metadata must be folded into the inode node.
  - Submits merged node writes for the inode.

- `f2fs_flush_inline_data()`
  - Scans dirty inode node pages and flushes inline data marked on node folios.

- `f2fs_sync_node_pages()`
  - General node writeback scanner.
  - Flush order:
    1. indirect nodes
    2. dentry dnodes
    3. file dnodes
  - Gives priority to synchronous writers.
  - Flushes inline data and dirty inode metadata before node writeback in balancing contexts.
  - Submits merged node writes at the end.

- `f2fs_wait_on_node_pages_writeback()`
  - Waits for fsync node writeback up to a sequence id.
  - Checks node mapping writeback errors.

- `f2fs_write_node_pages()`
  - Address-space writepages hook for node mapping.
  - Skips during POR.
  - Performs background balancing.
  - Avoids small async writeback batches and avoids deadlock with synchronous node writeback.
  - Calls `f2fs_sync_node_pages()` under a block plug.

- `f2fs_dirty_node_folio()`
  - Address-space dirty_folio hook.
  - Marks uptodate, updates checksum under checkfs, increments dirty node count, and sets F2FS reference bit.

- `f2fs_node_aops`
  - Node mapping address-space operations table.

## Free Nid Management

- `__lookup_free_nid_list()`
  - Looks up free/preallocated nid state in radix tree.

- `__insert_free_nid()`, `__remove_free_nid()`, `__move_free_nid()`
  - Maintain radix tree, free list, and `FREE_NID`/`PREALLOC_NID` counters.

- `update_free_nid_bitmap()`
  - Updates per-NAT-block free nid bitmap and free count, but only after that NAT block has been scanned/known.

- `add_free_nid()`
  - Adds a nid as free after validating range and checking NAT cache conflicts.
  - During free-nid building, avoids stale nids that are preallocated or dirtied concurrently.
  - Updates free nid bitmap and `available_nids` when requested.

- `remove_free_nid()`
  - Removes a nid from the free list when it is no longer free.

- `scan_nat_page()`
  - Scans a NAT block and adds free nids for `NULL_ADDR` entries.
  - Treats `NEW_ADDR` in NAT as corruption.

- `scan_curseg_cache()`
  - Reconciles free nid state against NAT entries in the current hot data journal.

- `scan_free_nid_bits()`
  - Builds free nid list from cached free-nid bitmaps and then reconciles current segment journal.

- `__f2fs_build_free_nids()` / `f2fs_build_free_nids()`
  - Populate free nid list from nat_bits/free-nid bitmap or by scanning NAT pages.
  - Uses `build_lock` to serialize builders.
  - Readaheads NAT pages and advances `next_scan_nid`.

- `f2fs_alloc_nid()`
  - Allocates a nid from free list by moving it to `PREALLOC_NID`.
  - Decrements available nid count and clears free nid bitmap.
  - Builds free nids synchronously if needed.
  - Refuses allocation when no available nids remain or fault injection triggers.

- `f2fs_alloc_nid_done()`
  - Completes a successful preallocated nid by removing and freeing its state entry.

- `f2fs_alloc_nid_failed()`
  - Returns a preallocated nid to free state or drops it under memory pressure.
  - Restores available nid count and bitmap state.

- `f2fs_try_to_free_nids()`
  - Shrinks excess free nid cache entries above `MAX_FREE_NIDS`.

## Recovery Helpers

- `f2fs_recover_inline_xattr()`
  - Replays inline xattr state from recovered node folio into the inode folio.
  - Adjusts inline xattr flags and statistics.

- `f2fs_recover_xattr_data()`
  - Invalidates previous xattr node, allocates a new xattr nid/node, updates inode page, and copies recovered xattr node content.

- `f2fs_recover_inode_page()`
  - Recreates a missing inode page during roll-forward recovery.
  - Removes the ino from free nid cache.
  - Copies safe inode metadata from recovered folio, resets size/blocks/links/xattr nid, preserves selected extra attributes, sets NAT to `NEW_ADDR`, increments valid node/inode counts, and marks inode folio dirty.

- `f2fs_restore_node_summary()`
  - Rebuilds node summary entries by scanning node segment blocks and reading footer nids.

## NAT Checkpoint Flushing

- `remove_nats_in_journal()`
  - Moves NAT journal entries into dirty NAT cache so checkpoint can write a coherent NAT state.
  - Adjusts available nid count for free NAT entries that will be re-added.

- `__adjust_nat_entry_set()`
  - Orders dirty NAT sets by entry count for journal/NAT block flushing efficiency.

- `__update_nat_bits()`
  - Maintains empty/full NAT block bitmaps when NAT bits are enabled.

- `__flush_nat_entry_set()`
  - Flushes a dirty NAT set either to the hot data summary journal or to the alternate NAT block.
  - Converts cached `node_info` into raw NAT entries.
  - Resets NAT flags, clears dirty state, and updates free nid tracking.
  - Updates nat_bits when writing NAT blocks directly.
  - Frees empty `nat_entry_set`.

- `f2fs_flush_nat_entries()`
  - Main checkpoint NAT flush routine.
  - Optionally removes NAT journal entries first when nat_bits are enabled or journal space is insufficient.
  - Sorts NAT sets, readaheads NAT pages for direct flushes, and flushes each set.

## Node Manager Initialization and Teardown

- `__get_nat_bitmaps()`
  - Loads nat_bits from checkpoint area when enabled.
  - Verifies checkpoint version/CRC before accepting nat_bits.
  - Disables nat_bits if validation fails.

- `load_free_nid_bitmap()`
  - Initializes free nid bitmap from empty NAT bits and marks full NAT blocks as scanned.

- `init_node_manager()`
  - Initializes NAT geometry, max nid, available nid count, thresholds, radix trees, lists, locks, NAT bitmap, nat_bits, and checkfs mirror bitmap.

- `init_free_nid_cache()`
  - Allocates per-NAT-block free nid bitmaps, NAT block scanned bitmap, and per-block free nid counts.

- `f2fs_build_node_manager()`
  - Allocates `sbi->nm_info`, initializes manager and free nid cache, loads nat_bits-derived state, then builds initial free nids.

- `f2fs_destroy_node_manager()`
  - Frees free nid list, NAT cache, NAT set cache, bitmaps, nat_bits, mirror bitmap, and manager structure.
  - Uses assertions to catch leaked free/preallocated nids and NAT entries.

- `f2fs_create_node_manager_caches()` / `f2fs_destroy_node_manager_caches()`
  - Manage slab caches for NAT entries, free nid entries, NAT entry sets, and fsync node entries.

## Concurrency and Consistency

- `nat_tree_lock` protects NAT radix trees and NAT entry sets.
- `nat_list_lock` protects NAT clean/dirty list movements.
- `nid_list_lock` protects free/preallocated nid radix tree, list, counters, and bitmaps.
- `build_lock` serializes free nid construction.
- `node_write` coordinates node writes with NAT state changes.
- `fsync_node_lock` protects fsync node sequence list.
- Checkpoint and journal lock ordering is carefully handled in `f2fs_get_node_info()` and NAT flush paths.
- Corruption detection sets `SBI_NEED_FSCK` and reports specific F2FS error categories for invalid nid ranges, NAT inconsistencies, footer mismatches, summaries, and node references.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/node.h -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/node.h

## Purpose

`node.h` defines F2FS node-manager constants, NAT/free-nid data structures, node footer helpers, NAT address helpers, node-tree offset rules, and inline utilities for manipulating node ids and node flags.

## NAT and Free Nid Constants

- `START_NID(nid)`
  - Aligns a nid to the first nid in its NAT block.

- `NAT_BLOCK_OFFSET(start_nid)`
  - Converts a start nid to NAT block offset.

- `FREE_NID_PAGES`
  - Number of NAT pages to scan synchronously when building free nids.

- `MAX_FREE_NIDS`
  - Maximum normal free nid cache target derived from NAT entries per block and scanned pages.

- `SHRINK_NID_BATCH_SIZE`
  - Batch size when shrinking free nid cache.

- `DEF_RA_NID_PAGES`
  - Default NAT readahead pages for nid scanning.

- `MAX_RA_NODE`
  - Maximum node readahead size during data block lookup.

- `DEF_RAM_THRESHOLD`
  - Default memory threshold factor.

- `DEF_DIRTY_NAT_RATIO_THRESHOLD`
  - Dirty NAT ratio threshold.

- `DEF_NAT_CACHE_THRESHOLD`
  - Hard threshold for total cached NAT entries.

- `DEF_RF_NODE_BLOCKS`
  - Default roll-forward node block limit.

- `NAT_VEC_SIZE`
  - Gang lookup vector size for NAT cache/set scans.

- `LOCKED_PAGE`
  - Special return value from node read path.

- `FILE_NOT_ALIGNED`
  - Pinned-file alignment status constant.

## NAT Entry State

- Node info flags:
  - `IS_CHECKPOINTED`
  - `HAS_FSYNCED_INODE`
  - `HAS_LAST_FSYNC`
  - `IS_DIRTY`
  - `IS_PREALLOC`

- `struct node_info`
  - `nid`: node id.
  - `ino`: owning inode number.
  - `blk_addr`: physical node block address.
  - `version`: NAT version.
  - `flag`: in-memory state bits.

- `struct nat_entry`
  - List linkage plus cached `node_info`.

- NAT accessor macros
  - Get/set nid, block address, inode number, and version.

- `copy_node_info()`
  - Copies persistent node info fields but intentionally does not copy flags.

- `set_nat_flag()`, `get_nat_flag()`, `nat_reset_flag()`
  - Manage NAT state bits.
  - Reset makes an entry checkpointed, clears fsynced-inode marker, and marks last-fsync true.

- `node_info_from_raw_nat()` / `raw_nat_from_node_info()`
  - Convert between on-disk little-endian NAT entries and in-memory `node_info`.

- `excess_dirty_nats()` / `excess_cached_nats()`
  - Test dirty NAT ratio and total NAT cache pressure.

## Memory Type Enum

`enum mem_type` defines memory accounting categories used by node and cache pressure logic:

- `FREE_NIDS`
- `NAT_ENTRIES`
- `DIRTY_DENTS`
- `INO_ENTRIES`
- `READ_EXTENT_CACHE`
- `AGE_EXTENT_CACHE`
- `DISCARD_CACHE`
- `COMPRESS_PAGE`
- `BASE_CHECK`

## NAT Set and Free Nid Structures

- `struct nat_entry_set`
  - Groups dirty NAT entries by NAT block.
  - Contains set list, entry list, set number, and entry count.

- `struct free_nid`
  - Tracks a free or preallocated nid.
  - Contains list linkage, nid, and state.

- `next_free_nid()`
  - Peeks at first free nid under `nid_list_lock`.

## NAT Bitmap and Address Helpers

- `get_nat_bitmap()`
  - Copies current NAT bitmap, with optional mirror check under `CONFIG_F2FS_CHECK_FS`.

- `current_nat_addr()`
  - Computes physical NAT block address for a start nid using NAT bitmap to select old/new NAT copy.

- `next_nat_addr()`
  - Computes alternate NAT block address by flipping segment-copy bit.

- `set_to_next_nat()`
  - Toggles NAT bitmap for a NAT block, and mirror bitmap under checkfs.

## Node Footer Helpers

- `ino_of_node()`
  - Reads footer owner inode number.

- `nid_of_node()`
  - Reads footer nid.

- `ofs_of_node()`
  - Extracts logical node offset from footer flag bits.

- `cpver_of_node()`
  - Reads checkpoint version stored in footer.

- `next_blkaddr_of_node()`
  - Reads footer next-block pointer used by roll-forward recovery chain.

- `fill_node_footer()`
  - Initializes nid, ino, and offset in a node footer.
  - Optionally clears the node body.
  - Preserves non-offset flag bits when not resetting.

- `copy_node_footer()`
  - Copies only node footer between folios.

- `fill_node_footer_blkaddr()`
  - Stores checkpoint version/CRC and next block address for recovery.

- `is_recoverable_dnode()`
  - Checks whether a node footer checkpoint version matches current checkpoint recovery expectations.
  - Handles no-CRC and CRC recovery modes.

## Node Offset Topology

The comment documents F2FS node offset layout:

- Inode block is offset `0`.
- Direct nodes occupy offsets `1` and `2`.
- First indirect node is offset `3`; its direct children begin at `4`.
- Second indirect node starts at `4 + NIDS_PER_BLOCK`.
- Double-indirect node starts at `5 + 2 * NIDS_PER_BLOCK`.
- Double-indirect children use a repeated indirect/direct-node offset pattern.

## Node Type and Nid Access

- `IS_DNODE()`
  - Determines whether a node folio is a direct node carrying data addresses.
  - Treats xattr blocks as dnodes.
  - Excludes known indirect and double-indirect node offsets.

- `set_nid()`
  - Writes a child nid into inode or indirect node nid array.
  - Waits for node folio writeback and marks folio dirty.

- `get_nid()`
  - Reads child nid from inode or indirect node nid array.

## Cold/Fsync/Dentry Marks

- `is_node()`
  - Tests a footer flag bit.

- Macros:
  - `is_cold_node()`
  - `is_fsync_dnode()`
  - `is_dent_dnode()`

- `__set_mark()`
  - Sets or clears a footer flag bit.

- `set_cold_node()`
  - Marks non-directory node blocks cold.

- `set_mark()`
  - Sets a footer mark and updates inode checksum under checkfs.

- Macros:
  - `set_dentry_mark()`
  - `set_fsync_mark()`

## Interactions

- Used heavily by `node.c` for NAT, node footer, dnode classification, and writeback/recovery state.
- Used by `recovery.c` to validate roll-forward node chains and interpret fsync/dentry marks.
- Used by namespace and data paths through exported node helpers in `f2fs.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/recovery.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/recovery.c

## Purpose

`recovery.c` implements F2FS roll-forward recovery for fsynced data after an unclean shutdown. It scans the warm node chain after the last checkpoint, identifies fsynced dnodes, reconstructs missing inode/dentry state when needed, replays inode and data block updates, and writes a checkpoint after successful recovery.

## Recovery Model

The opening comment documents recovery scenarios involving:

- `F`: fsync mark.
- `D`: dentry mark.
- inode nodes before/after checkpoint.
- dnodes after checkpoint.

The recovery logic handles cases where inode updates and fsynced dnodes appear in different orders around checkpoint, including missing dentry/inode node recovery and dropping unrecoverable dnodes.

## Roll-Forward Capacity

- `f2fs_space_for_roll_forward()`
  - Checks that current valid blocks plus newly allocated blocks do not exceed user block count.
  - Enforces optional `max_rf_node_blocks` limit through `rf_node_block_count`.

## Fsync Inode List Management

- `get_fsync_inode()`
  - Finds an inode entry in a recovery list by inode number.

- `add_fsync_inode()`
  - Loads inode with retry.
  - Initializes quota.
  - Optionally allocates quota inode usage for recovered newly-created inode pages.
  - Allocates and appends an `fsync_inode_entry`.

- `del_fsync_inode()` / `destroy_fsync_dnodes()`
  - Drop inode references and free recovery list entries.
  - Optionally call `f2fs_inode_synced()` to drop unrecovered inode state.

## Filename and Dentry Recovery

- `init_recovered_filename()`
  - Builds an `f2fs_filename` from raw inode name and name length.
  - Handles unencrypted names directly.
  - For encrypted+casefolded directories, reads the saved hash from the raw name area.
  - For casefolded directories with keys, computes casefolded hash.
  - Rejects excessive name length and invalid encrypted hash layout.

- `recover_dentry()`
  - Ensures the parent directory inode is available in `dir_list`.
  - Looks for the recovered filename in the parent.
  - If an entry exists for another inode, loads that inode, initializes quota, acquires orphan capacity, deletes the stale entry, and retries.
  - If absent, adds a recovered dentry for the inode.
  - Retries on `-ENOMEM`.
  - Logs recovered name as `"<encrypted>"` when appropriate.

## Inode Metadata Recovery

- `recover_quota_data()`
  - Compares raw recovered uid/gid with current inode ownership.
  - Uses `dquot_transfer()` to update quota accounting when ownership changed.
  - Marks `SBI_QUOTA_NEED_REPAIR` on transfer error.

- `recover_inline_flags()`
  - Restores `FI_PIN_FILE` and `FI_DATA_EXIST` from raw inline flags.

- `recover_inode()`
  - Restores mode, uid/gid, project quota, size, atime/ctime/mtime, advise, flags, inode flags, GC failures, and inline state.
  - Transfers project quota if needed.
  - Calls `f2fs_set_inode_flags()` and marks inode dirty sync.
  - Logs recovered inode details.

## Node Chain Discovery

- `adjust_por_ra_blocks()`
  - Dynamically adjusts recovery readahead window.
  - Doubles readahead on sequential next-block chains, halves toward minimum on non-segment-boundary discontinuity.

- `sanity_check_node_chain()`
  - Uses Floyd cycle detection against the roll-forward node chain.
  - Reads fast-pointer nodes, validates recoverability, advances by two links, and readaheads.
  - Returns `-EINVAL` if a loop is detected.

- `find_fsync_dnodes()`
  - Starts from `NEXT_FREE_BLKADDR()` of `CURSEG_WARM_NODE`.
  - Walks node chain while block addresses are valid and nodes are recoverable.
  - Tracks fsync-marked dnodes.
  - If a fsynced inode+dentry node is found and recovery is not check-only, calls `f2fs_recover_inode_page()` for missing new inode pages.
  - Adds fsynced inode entries.
  - Records latest fsync block and latest dentry block per inode entry.
  - In check-only mode, reports existence of recoverable new inode state through `new_inode`.

## Previous Ownership Checks

- `check_index_in_prev_nodes()`
  - Determines whether the destination data block being replayed is still referenced by a previous node.
  - Reads segment summary from current curseg summary or summary page.
  - Validates summary offset against max addresses in node.
  - If the previous reference belongs to the same inode or node, truncates that data block reference directly.
  - Otherwise loads the referenced inode and dnode, and truncates the previous data block if it still points at the replay destination.
  - Temporarily unlocks/relocks inode folio when needed to avoid lock conflicts.
  - Reports inconsistent summaries as corruption.

## Data Recovery

- `f2fs_reserve_new_block_retry()`
  - Retries `f2fs_reserve_new_block()` up to `DEFAULT_FAILURE_RETRY_COUNT`.

- `do_recover_data()`
  - Replays one recoverable node folio for an inode.
  - Step 1: recover inline xattr or external xattr node.
  - Step 2: recover inline data.
  - Step 3: replay data block address indices.
  - Locates/allocates corresponding current dnode with `f2fs_get_dnode_of_data(..., ALLOC_NODE)`.
  - Validates current and recovered block addresses under `META_POR`.
  - Handles cases:
    - same source/destination: skip
    - recovered destination `NULL_ADDR`: truncate current source
    - recovered destination `NEW_ADDR`: truncate current source and reserve a new block
    - recovered destination valid: reserve if current source is null, remove stale previous references, validate destination is not currently valid data, and replace block mapping
  - Grows inode size unless `file_keep_isize()` is set.
  - Copies recovered node footer into current node folio and marks it dirty.
  - Logs recovered range and count.

- `recover_data()`
  - Walks the same warm node chain and replays only nodes belonging to discovered fsynced inodes.
  - Recovers inode metadata when the folio is an inode node.
  - Recovers dentry when the entry’s last dentry block matches the current block.
  - Calls `do_recover_data()` for each relevant dnode.
  - Moves completed inode entries to a temporary list once their last fsync block is replayed.
  - Allocates new segments after successful replay.
  - Logs recoverable/fsynced/total dnode counts and recovered inode/dentry/dnode counts.

## Top-Level Recovery

- `f2fs_recover_fsync_data()`
  - Logs check-only or real recovery mode.
  - Takes `cp_global_sem` write lock to prevent checkpoint during recovery.
  - Step 1: calls `find_fsync_dnodes()`.
  - In check-only mode, returns `1` when fsync data or new inode recovery is needed.
  - Step 2: calls `recover_data()` for real recovery.
  - Destroys inode recovery lists, truncates recovery meta pages, and on error truncates node/meta mappings fully.
  - Checks and fixes zoned-device write pointer consistency after successful recovery.
  - Clears `SBI_POR_DOING` on success.
  - Drops directory inode list after releasing checkpoint lock.
  - If recovery ran, sets `SBI_IS_RECOVERED` and writes a checkpoint with reason `CP_RECOVERY`.
  - Restores original superblock flags, including readonly status.

## Cache Lifecycle

- `f2fs_create_recovery_cache()`
  - Creates `f2fs_fsync_inode_entry` slab cache.

- `f2fs_destroy_recovery_cache()`
  - Destroys the recovery entry slab cache.

## Interactions

- Uses `node.h` helpers for fsync/dentry marks, node footer checkpoint version, and next block chain.
- Calls `node.c` recovery helpers:
  - `f2fs_recover_inode_page()`
  - `f2fs_recover_inline_xattr()`
  - `f2fs_recover_xattr_data()`
  - `f2fs_get_dnode_of_data()`
- Uses directory helpers to find/delete/add entries.
- Uses segment summaries and block replacement to avoid duplicate data block ownership.
- Invoked from mount/superblock recovery flow in `super.c`.

## Consistency and Error Handling

- Detects looped node chains and aborts with a notice.
- Validates recovered block addresses before use.
- Converts inconsistent summaries and invalid metadata into `-EFSCORRUPTED` or error flags.
- Uses retry loops for memory allocation pressure and block reservation.
- On recovery failure, keeps filesystem from silently proceeding with stale recovery pages by truncating node/meta mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/recovery.c -->