# subset-b-005660 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/iostat.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/iostat.c

## Purpose

`iostat.c` implements optional F2FS I/O accounting and latency tracing for a mounted filesystem. It maintains per-superblock counters in `struct f2fs_sb_info`, exposes the current aggregate view through a seq-file show function, periodically emits tracepoints with deltas, and wraps bios with a small private context so completion paths can attribute latency to read, synchronous write, or asynchronous write traffic.

The file is compiled only when `CONFIG_F2FS_IOSTAT` is enabled through declarations in `iostat.h`; without that option, callers get static inline no-ops.

## Important APIs and functions

- `iostat_info_seq_show()` prints current cumulative byte/count/average counters for write, read, folio-order read, discard, flush, and zone reset classes. It relies on `sbi->iostat_enable` and is suitable for debugfs/proc style reporting.
- `f2fs_update_iostat()` is the main accounting entry point for byte-count updates. It records the explicit `enum iostat_type`, derives aggregate app read/write counters, and conditionally mirrors compressed file traffic into compressed data categories.
- `f2fs_update_read_folio_count()` records folio-order read distribution and clamps oversize folio orders into the last bucket.
- `f2fs_reset_iostat()` clears byte, count, previous-delta, read-folio, and latency accumulators under the appropriate spinlocks.
- `iostat_alloc_and_bind_ctx()`, `iostat_update_submit_ctx()` from the header, and `iostat_update_and_unbind_ctx()` form the bio lifecycle. Allocation stores the original post-read context, submit stores jiffies/type, completion records latency and restores `bio->bi_private`.
- `f2fs_init_iostat_processing()` and `f2fs_destroy_iostat_processing()` create and destroy the global slab-backed mempool for `struct bio_iostat_ctx`.
- `f2fs_init_iostat()` and `f2fs_destroy_iostat()` initialize/destroy per-mount locks, defaults, and `sbi->iostat_io_lat`.

## Control flow and state

Counter updates first test `sbi->iostat_enable`, then mutate `sbi->iostat_bytes`, `sbi->iostat_count`, or `sbi->iostat_read_folio_count` under `sbi->iostat_lock`. After each update, `f2fs_record_iostat()` checks whether `sbi->iostat_next_period` has elapsed. It double-checks under lock, advances the next deadline by `sbi->iostat_period_ms`, computes deltas from `prev_iostat_bytes` and `prev_iostat_read_folio_count`, emits `trace_f2fs_iostat()`, then calls `__record_iostat_latency()`.

Latency state is separate in `struct iostat_lat_info`, guarded by `sbi->iostat_lat_lock`. Bio completion computes `jiffies - submit_ts`, normalizes `META_FLUSH` to `META`, validates the page type, and updates sum, count, and peak arrays. Periodic recording copies all latency buckets into a stack array, converts jiffies to milliseconds, resets the live buckets, and emits `trace_f2fs_iostat_latency()`.

The bio private pointer is multiplexed carefully. For write bios, unbind restores `bio->bi_private` to `iostat_ctx->sbi`; for read bios, it restores the saved `post_read_ctx`. This is an integration-sensitive contract with the surrounding F2FS bio submission/completion paths.

## Persistence behavior

This file does not write persistent filesystem state. All counters and latency buckets are in-memory telemetry. The only storage-like resources are kernel memory allocations: the global `bio_iostat_ctx_cache` slab, `bio_iostat_ctx_pool` mempool, and per-mount `sbi->iostat_io_lat`.

## Dependencies and integration points

The implementation depends on core kernel folio, bio, mempool, seq-file, time, and spinlock primitives. F2FS-specific dependencies include `struct f2fs_sb_info`, `enum iostat_type`, `enum page_type`, compressed-file detection, `f2fs_kzalloc()`, warnings, and tracepoints from `<trace/events/f2fs.h>`. It is called from F2FS read/write paths, including node I/O in `node.c`, where `f2fs_update_iostat(..., FS_NODE_READ_IO, F2FS_BLKSIZE)` records node-page reads.

## Risks and edge cases

- `iostat_update_and_unbind_ctx()` assumes `bio->bi_private` is a valid `struct bio_iostat_ctx`; callers must bind only once and unbind exactly once.
- A missing `iostat_update_submit_ctx()` before completion yields a near-boot-time latency, because `submit_ts` starts at zero.
- Page type validation protects against out-of-range latency indexing, but invalid page types are dropped after warning.
- Counter arrays are protected by spinlocks for mutation and reset, but printed cumulative counters are read without taking `iostat_lock`; debug output can be slightly inconsistent under concurrent updates.
- Mempool allocation is treated as never failing after global initialization; mount/module init ordering must ensure the pool exists before bio binding.

## Test signals

Useful validation signals include enabling/disabling F2FS iostat at runtime, verifying seq output remains empty when disabled, checking tracepoint deltas over the configured period, issuing buffered/direct/mmap reads and writes, exercising compressed files, reading with larger folio orders, and forcing read/write bios through completion to confirm `bio->bi_private` restoration and latency bucket updates. Fault tests should cover allocation init failure, reset while I/O is active, and invalid page-type warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/iostat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/iostat.h -->
# sources/distributed-fs/ceph-client/fs/f2fs/iostat.h

## Purpose

`iostat.h` is the public F2FS iostat interface. It declares latency classes, configuration bounds, accounting structures, bio-private context helpers, and the external functions implemented by `iostat.c`. It also provides complete no-op fallbacks when `CONFIG_F2FS_IOSTAT` is disabled, allowing the rest of F2FS to call iostat hooks without local preprocessor guards.

## Important APIs and types

- `enum iostat_lat_type` defines `READ_IO`, `WRITE_SYNC_IO`, and `WRITE_ASYNC_IO` latency lanes, plus `MAX_IO_TYPE` for array sizing.
- `NUM_PREALLOC_IOSTAT_CTXS`, `DEFAULT_IOSTAT_PERIOD_MS`, `MIN_IOSTAT_PERIOD_MS`, and `MAX_IOSTAT_PERIOD_MS` define mempool capacity and user-visible tracing period bounds.
- `struct iostat_lat_info` stores latency sums, peaks, and bio counts indexed by latency type and F2FS page type.
- `struct bio_iostat_ctx` stores `sbi`, submit timestamp, page type, and the original `bio_post_read_ctx`.
- `iostat_update_submit_ctx()` records `jiffies` and page type into the bound context at bio submission time.
- `get_post_read_ctx()` retrieves the original read completion context from an iostat-wrapped bio.
- External hooks include `f2fs_reset_iostat()`, `f2fs_update_iostat()`, `f2fs_update_read_folio_count()`, bio bind/unbind helpers, global processing init/destroy, and per-mount init/destroy.

## Control flow and state

When iostat is enabled, callers allocate and bind a `bio_iostat_ctx` before bio submission, set submit metadata with `iostat_update_submit_ctx()`, and let completion call `iostat_update_and_unbind_ctx()`. Read completion users can call `get_post_read_ctx()` to retrieve the saved post-read context while the iostat wrapper is active. Per-mount state is allocated by `f2fs_init_iostat()` and referenced through `struct f2fs_sb_info`.

When iostat is disabled at compile time, the same function names exist as static inline no-ops. The disabled `get_post_read_ctx()` returns `bio->bi_private` directly, preserving the normal read-completion ownership model.

## Persistence behavior

This header defines only in-memory telemetry structures. It does not describe any on-disk layout. However, because `struct iostat_lat_info` is embedded via a pointer in `struct f2fs_sb_info`, changes to its size affect kernel memory footprint and initialization/destruction expectations.

## Dependencies and integration points

The header depends on F2FS enums and constants such as `NR_PAGE_TYPE`, `enum iostat_type`, and `enum page_type`, plus kernel `struct bio`, `struct inode`, `struct folio`, and `struct seq_file`. It is included by F2FS I/O code that wants to remain build-compatible regardless of `CONFIG_F2FS_IOSTAT`.

## Risks and edge cases

- The enabled helper `iostat_update_submit_ctx()` assumes `bio->bi_private` already points to `struct bio_iostat_ctx`; calling it on an unbound bio corrupts type assumptions.
- The disabled `get_post_read_ctx()` intentionally has different implementation semantics from the enabled path, so call sites must use the accessor rather than reading `bio->bi_private` directly.
- Array dimensions are coupled to `MAX_IO_TYPE` and `NR_PAGE_TYPE`; adding new page or latency types requires auditing initialization, reset, trace formatting, and consumers.
- `MAX_IOSTAT_PERIOD_MS` is documented as one day but is `8640000`, which is 2.4 hours in milliseconds; tests or documentation should clarify whether this is intentional or a unit mistake.

## Test signals

Build coverage should include both `CONFIG_F2FS_IOSTAT=y` and disabled configurations. Runtime checks should validate that iostat hooks compile away cleanly when disabled, bio private-pointer restoration works in both modes, period bounds reject too-small/too-large settings in the option/control layer, and latency arrays remain within bounds for all F2FS `page_type` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/iostat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/namei.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/namei.c

## Purpose

`namei.c` implements F2FS VFS namespace operations: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, tmpfile, whiteout creation, rename, exchange rename, parent lookup, and inode operation tables. It is the bridge between Linux VFS dentries/inodes and F2FS directory entry, inode allocation, quota, encryption, compression, inline-data, project-quota, orphan, and checkpoint semantics.

## Important APIs and functions

- `f2fs_update_extension_list()` mutates cold/hot extension lists in the raw superblock, preserving ordering between cold and hot extension ranges.
- `set_compress_new_inode()` and `set_file_temperature()` derive new-inode compression and hot/cold file hints from mount options, inherited directory flags, and raw-super extension lists.
- `f2fs_new_inode()` allocates a VFS inode and F2FS nid, initializes ownership, timestamps, generation, project id, encryption state, quota state, inline/xattr flags, compression state, extent tree, and inode flags.
- Namespace creation functions `f2fs_create()`, `f2fs_mkdir()`, `f2fs_mknod()`, `f2fs_symlink()`, and `f2fs_tmpfile()` allocate or initialize inodes and add directory links or orphan/tmpfile state under `f2fs_lock_op()`.
- Lookup and ancestry functions `f2fs_lookup()` and `f2fs_get_parent()` resolve directory entries through F2FS dir helpers and return VFS dentries/aliases.
- Removal and movement functions `f2fs_unlink()`, `f2fs_rmdir()`, `f2fs_rename()`, `f2fs_cross_rename()`, and `f2fs_rename2()` update directory entries, link counts, parent inode numbers, orphan state, whiteouts, and strict-fsync transaction inode tracking.
- Operation tables `f2fs_dir_inode_operations`, `f2fs_symlink_inode_operations`, `f2fs_encrypted_symlink_inode_operations`, and `f2fs_special_inode_operations` register these functions with VFS.

## Control flow and state

Creation paths first reject checkpoint errors and, except mkdir, require checkpoint readiness. They initialize directory quotas, allocate a nid through `f2fs_new_inode()`, assign operation tables and address-space operations, then take the F2FS operation lock and call `f2fs_add_link()`. On success they call `f2fs_alloc_nid_done()`, instantiate the dentry, optionally sync for `dirsync`, and balance the filesystem. On failure after inode allocation, they call `f2fs_handle_failed_inode()`, which must unwind nid, quota, orphan, and inode state while releasing the operation lock context.

`f2fs_new_inode()` is the central initialization funnel. It sets `FI_NEW_INODE`, optional encryption, `FI_EXTRA_ATTR`, inline xattr/dentry/data eligibility, project-inherit flags, compression context, hot/cold file temperature, inode flags, and extent tree state before returning a locked new inode. Failure before insertion calls `make_bad_inode()` and sets `FI_FREE_NID` when a nid was reserved; failure after insertion drops quota, clears nlink, unlocks, and iputs.

Lookup prepares encrypted/casefolded filenames, searches the directory, reads the target inode, rejects zero-link corruption, validates encrypted context compatibility for encrypted directories, and returns `d_splice_alias()`. For Unicode casefolded negative dentries it returns `NULL` to avoid caching a negative dentry that VFS cannot yet safely represent.

Unlink validates quota, finds the entry, rejects zero-link corruption and one-link directory corruption, acquires orphan capacity, deletes the entry, invalidates casefolded dentries, and optionally syncs. Rmdir delegates to unlink only after `f2fs_empty_dir()`.

Rename has two flows. Normal rename handles optional `RENAME_WHITEOUT`, existing-target replacement, parent directory `..` updates, link-count adjustments, orphan accounting for overwritten targets, old-entry deletion, whiteout insertion, strict fsync tracking, and dirsync. Cross rename swaps two existing dentries and, when directories move across parents, swaps their `..` entries and adjusts parent link counts. `f2fs_rename2()` validates flags, runs fscrypt preparation, and dispatches to normal or exchange rename.

## Persistence behavior

The file changes persistent state through inode allocation, NAT/SIT-visible node creation via lower layers, directory entry insertion/deletion, raw superblock extension list mutation, inode flags, link counts, parent inode numbers, inline/compression metadata, symlink data pages, orphan lists, and checkpoint-triggered syncs. It also marks inodes dirty and records transaction directory inode numbers in strict fsync mode to support crash recovery.

Tmpfiles and whiteouts are notable persistence cases. `__f2fs_tmpfile()` creates a non-linked inode, reserves orphan capacity, calls `f2fs_do_tmpfile()`, adds the inode to the orphan list so unused data can be reclaimed after power loss, and marks whiteout tmpfiles linkable for later rename-whiteout insertion.

## Dependencies and integration points

`namei.c` depends on VFS dentry/inode APIs, fscrypt, quota, idmapped ownership, project quota, folios, and F2FS subsystems in `f2fs.h`, `node.h`, `segment.h`, `xattr.h`, and `acl.h`. It integrates with directory helpers such as `f2fs_add_link()`, `f2fs_find_entry()`, `f2fs_delete_entry()`, `f2fs_set_link()`, and filename preparation/freeing. It relies on node-manager nid allocation from `node.c` and on recovery semantics in `recovery.c` for fsync marks, dentry marks, orphan recovery, and strict rename durability.

## Risks and edge cases

- Extension-list mutation writes raw superblock fields in memory; callers must hold the appropriate superblock lock externally when required. Duplicate checks are asymmetric between hot and cold ranges and should be tested carefully.
- Inode allocation has many staged failure paths; missing `FI_FREE_NID`, `clear_nlink()`, quota drop, or `unlock_new_inode()` in a new path can leak nids or expose bad inodes.
- Casefolded negative dentry behavior intentionally avoids caching; changes in VFS support could require revisiting lookup/unlink invalidation.
- Rename-whiteout has a narrow failure window after old-entry deletion and before whiteout link insertion where it invalidates both dentries and exits through shared cleanup.
- Link-count and parent `i_pino` updates must stay consistent for fsck, especially in cross-directory directory renames and exchange renames.
- Symlink creation instantiates the dentry even when writing encrypted/page symlink data fails, then unlinks to unwind; tests should inspect this rollback path.

## Test signals

Important coverage includes create/link/unlink/mkdir/rmdir/mknod/symlink/tmpfile under normal, encrypted, casefolded, inline dentry, inline data, project quota, and compression configurations. Rename tests should cover no-replace, replace-file, replace-directory-empty/non-empty, exchange file-directory across parents, whiteout, strict fsync mode, dirsync parents, and project-id mismatches. Fault injection should target nid allocation, quota initialization, `f2fs_add_link()`, orphan acquisition, encrypted symlink allocation/encryption, and ENOMEM loops in dentry recovery-adjacent paths. Fsck-oriented tests should validate detection of zero-link lookup/unlink corruption and bad directory link counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/node.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/node.c

## Purpose

`node.c` is the F2FS node manager implementation. It manages node ids, NAT cache entries, NAT journal/page checkpoint flushing, free-nid discovery, node-page read/write paths, dnode traversal/allocation/truncation, xattr-node and inode-page recovery helpers, fsync-node sequencing, and node-manager lifecycle. It is a core persistence file: directory/name operations, data block mapping, checkpoint, garbage collection, fsync, and power-on recovery all depend on its NAT and node-page contracts.

## Important APIs and functions

- Range and memory helpers: `f2fs_check_nid_range()` validates nid bounds and marks fsck-needed corruption; `f2fs_available_free_memory()` throttles caches for free nids, NAT entries, dirty dentries, inode entries, extent caches, discard cache, and compression pages.
- NAT cache: `f2fs_get_node_info()` resolves a nid to `struct node_info` from NAT cache, NAT journal, or NAT block; `set_node_addr()` updates in-memory NAT state and marks dirty sets; `f2fs_flush_nat_entries()` writes dirty NATs to the hot-data journal or NAT blocks during checkpoint.
- Dnode traversal: `f2fs_get_next_page_offset()`, `get_node_path()`, and `f2fs_get_dnode_of_data()` map file block indexes through inode, direct, indirect, and double-indirect node layers, optionally allocating missing nodes.
- Truncation/removal: `truncate_node()`, `truncate_dnode()`, `truncate_nodes()`, `truncate_partial_nodes()`, `f2fs_truncate_inode_blocks()`, `f2fs_truncate_xattr_node()`, and `f2fs_remove_inode_page()` invalidate node/data blocks, update valid counts, and clear NAT entries.
- Node folio lifecycle: `f2fs_new_inode_folio()`, `f2fs_new_node_folio()`, `read_node_folio()`, `f2fs_ra_node_page()`, `f2fs_get_node_folio()`, `f2fs_get_inode_folio()`, and `f2fs_get_xnode_folio()` create, read, validate, and return locked node folios.
- Writeback/fsync: `__write_node_folio()`, `f2fs_write_single_node_folio()`, `f2fs_move_node_folio()`, `f2fs_fsync_node_pages()`, `f2fs_sync_node_pages()`, `f2fs_wait_on_node_pages_writeback()`, and `f2fs_node_aops` implement node page writeback ordering and fsync markers.
- Free nid management: `f2fs_build_free_nids()`, `f2fs_alloc_nid()`, `f2fs_alloc_nid_done()`, `f2fs_alloc_nid_failed()`, and `f2fs_try_to_free_nids()` maintain `FREE_NID` and `PREALLOC_NID` states.
- Recovery helpers: `f2fs_recover_inline_xattr()`, `f2fs_recover_xattr_data()`, `f2fs_recover_inode_page()`, and `f2fs_restore_node_summary()` are used by roll-forward and segment recovery.
- Lifecycle: `f2fs_build_node_manager()`, `f2fs_destroy_node_manager()`, `f2fs_create_node_manager_caches()`, and `f2fs_destroy_node_manager_caches()` allocate and release manager state and slabs.

## Control flow and state

NAT lookup starts in `f2fs_get_node_info()`. It checks the radix-tree NAT cache under `nat_tree_lock`; if absent, it checks the current hot-data summary journal; if still absent, it reads the current NAT block from metadata. It validates block addresses, flags fsck-required corruption on inconsistencies, and opportunistically caches entries unless checkpoint contention makes caching undesirable.

NAT updates go through `set_node_addr()`. The function allocates or finds a `nat_entry`, handles reallocated nids, validates illegal address transitions, bumps versions when nodes are removed, changes the block address to `NEW_ADDR`, `NULL_ADDR`, or a real block address, marks the entry dirty, and updates fsync-related inode NAT flags. Dirty entries are grouped by NAT block in `nat_entry_set` objects so checkpoint can flush them efficiently.

Free-nid allocation is a two-phase state machine. `f2fs_alloc_nid()` removes a `FREE_NID` from the free list and moves it to `PREALLOC_NID`, decrementing `available_nids` and clearing bitmap hints. `f2fs_alloc_nid_done()` removes and frees the preallocated entry after the inode/node is committed. `f2fs_alloc_nid_failed()` either returns it to `FREE_NID` or drops it when memory pressure disallows caching. Free nids are discovered from NAT pages, NAT bits, and current journal entries, with `build_lock` preventing stale-list races during scanning.

Dnode traversal computes the path from file block index to inode/direct/indirect/double-indirect node offsets. `f2fs_get_dnode_of_data()` locks/reads each node in the path, allocates missing nodes in `ALLOC_NODE` mode, updates parent nid slots, and returns a `dnode_of_data` pointing at the target node and data address. It explicitly rejects self-referential nid pointers and updates compressed read extent cache for readonly compressed files when contiguous clusters are found.

Node writeback validates the node footer, fetches old NAT info, rejects truncated or invalid nodes, sets fsync/dentry/cold marks, optionally records fsync-node sequence entries, starts writeback, calls `f2fs_do_write_node_page()`, and updates NAT to the new block address. `f2fs_sync_node_pages()` writes dirty node pages in three passes: indirect nodes, dentry dnodes, then file dnodes. `f2fs_fsync_node_pages()` targets dirty cold dnodes for one inode and ensures the last fsync dnode gets the fsync mark, using retry logic for atomic writes.

Checkpoint NAT flushing first optionally merges NAT journal entries into dirty NAT sets when NAT bits are enabled or journal space is insufficient. It sorts sets by entry count relative to journal capacity, readaheads NAT blocks when block writes will be needed, then flushes each set either into the summary journal or into the next NAT block copy. NAT bitmaps are updated for empty/full NAT blocks.

## Persistence behavior

This file controls the durable mapping from nid to node block address through NAT cache, NAT journal, NAT pages, NAT bitmaps, and checkpoint NAT bit state. It writes node pages through the segment allocator, updates valid node/inode counters, invalidates old node/data blocks, maintains orphan-related inode removal state, and sets node footer fields used by fsync recovery: nid, ino, offset, checkpoint version/CRC, next block address, cold, fsync, and dentry flags.

The NAT area is copy-on-write at NAT-block granularity: `current_nat_addr()` and `next_nat_addr()` in `node.h` select the active copy and `get_next_nat_folio()` copies the current block to the alternate block before modifications. `set_to_next_nat()` flips the NAT bitmap so the next checkpoint version observes the new copy.

## Dependencies and integration points

`node.c` depends on VFS address-space writeback, folios, radix trees, slab caches, block plugging, checkpoint locks, segment allocation, NAT/SIT summaries, quota recovery, compression, inline data/xattr helpers, error handling, tracepoints, and iostat. It is used by `namei.c` for nid allocation and inode-page creation, by data paths for block mapping, by checkpoint for NAT flushing, by GC for node movement, and by `recovery.c` for roll-forward inode/xattr/data reconstruction.

## Risks and edge cases

- NAT cache state spans multiple locks (`nat_tree_lock`, `nat_list_lock`, journal rwsem); lock ordering mistakes can deadlock checkpoint, writeback, or free-nid building.
- Address transitions in `set_node_addr()` are guarded by `f2fs_bug_on()` because illegal transitions imply severe metadata corruption.
- Free-nid scanning races with preallocated nids; `add_free_nid()` has explicit logic to avoid re-adding nids that are being allocated concurrently.
- Node writeback redirties pages during power-on recovery, checkpoint-disabled cold dnode background writeback, or checkpoint errors; callers must not assume every writepage submission makes progress.
- `f2fs_get_dnode_of_data()` returns partial traversal state on `-ENOENT`; callers use `cur_level`, `max_level`, and `ofs_in_node` to skip holes, so changes to this contract affect truncate and fiemap-like users.
- Recovery helpers intentionally rebuild inode/xattr node pages from roll-forward nodes; they must keep NAT, valid counts, inode flags, and dirty state synchronized.

## Test signals

High-value tests include nid allocation success/failure under memory pressure, concurrent free-nid scanning with file creation, NAT cache shrink, checkpoint NAT flush into journal versus NAT block, NAT bits mount/unmount behavior, direct/indirect/double-indirect block allocation and truncate, xattr-node truncate/recovery, fsync of atomic and non-atomic files, node writeback under checkpoint-disabled and cp-error modes, GC node movement, corrupted NAT address detection, corrupted node footer detection, and roll-forward recovery using fsync/dentry-marked nodes. Tracepoints and iostat counters should show node reads/writes in read, fsync, checkpoint, and GC scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/node.h -->
# sources/distributed-fs/ceph-client/fs/f2fs/node.h

## Purpose

`node.h` defines the F2FS node-manager data structures and inline helpers shared across node allocation, NAT persistence, node-page footer handling, fsync recovery, and file block tree traversal. It captures the on-disk NAT address math and the in-memory `node_info`, `nat_entry`, `nat_entry_set`, and `free_nid` abstractions used by `node.c` and recovery code.

## Important APIs, macros, and types

- NAT layout macros `START_NID()`, `NAT_BLOCK_OFFSET()`, `current_nat_addr()`, `next_nat_addr()`, and `set_to_next_nat()` translate nids to active/next NAT block copies.
- Cache thresholds such as `MAX_FREE_NIDS`, `DEF_RAM_THRESHOLD`, `DEF_DIRTY_NAT_RATIO_THRESHOLD`, `DEF_NAT_CACHE_THRESHOLD`, and `DEF_RF_NODE_BLOCKS` provide default memory and recovery limits.
- `struct node_info` is the canonical in-memory nid-to-node mapping: nid, owner ino, block address, version, and flags.
- `struct nat_entry` wraps `node_info` for radix-tree and clean/dirty list membership.
- `struct nat_entry_set` groups dirty NAT entries by NAT block so checkpoint can flush one NAT page or journal batch at a time.
- `struct free_nid` stores a cached free/preallocated nid and state.
- `enum mem_type` identifies cache classes for `f2fs_available_free_memory()`.
- Footer helpers `ino_of_node()`, `nid_of_node()`, `ofs_of_node()`, `cpver_of_node()`, `next_blkaddr_of_node()`, `fill_node_footer()`, `copy_node_footer()`, `fill_node_footer_blkaddr()`, and `is_recoverable_dnode()` read/write node footer metadata.
- Node tree helpers `IS_DNODE()`, `set_nid()`, and `get_nid()` classify node pages and mutate child nid pointers.
- Mark helpers `is_cold_node()`, `is_fsync_dnode()`, `is_dent_dnode()`, `set_cold_node()`, `set_dentry_mark()`, and `set_fsync_mark()` manage footer bits used by writeback and recovery.

## Control flow and state

The NAT address helpers implement the two-copy NAT area scheme. `current_nat_addr()` computes the current physical NAT block using `nat_blkaddr`, block offset, segment size, and the NAT bitmap. `next_nat_addr()` flips the segment-copy bit to locate the alternate block. `set_to_next_nat()` changes the NAT bitmap after checkpoint code prepares the next copy.

`node_info_from_raw_nat()` and `raw_nat_from_node_info()` are the boundary between on-disk little-endian `struct f2fs_nat_entry` and host-endian `struct node_info`. `copy_node_info()` deliberately does not copy `flag`, because cache/checkpoint state bits are not part of the raw NAT mapping.

Node footers carry recovery-critical fields. `fill_node_footer()` initializes nid, owner ino, and node offset while preserving non-offset flag bits if requested. `fill_node_footer_blkaddr()` stamps the current checkpoint version and, when CRC recovery is enabled, checkpoint CRC into `cp_ver`, plus the next block address for roll-forward scanning. `is_recoverable_dnode()` checks a node footer against checkpoint version/CRC flags and supports no-CRC recovery mode.

`IS_DNODE()` encodes the F2FS node tree layout: inode node offset zero, direct nodes, indirect nodes, and double-indirect nodes. It treats xattr blocks as dnodes for data-bearing purposes and excludes indirect node offsets that only contain child nids.

## Persistence behavior

The header directly describes persistent NAT and node footer layout semantics. NAT block selection determines which NAT copy checkpoint will persist. Footer checkpoint version, CRC, next block address, fsync mark, dentry mark, cold mark, nid, ino, and offset are all read after crashes by roll-forward recovery. Child nid writes through `set_nid()` dirty node folios, causing later node writeback and NAT updates.

## Dependencies and integration points

`node.h` depends on F2FS superblock, checkpoint, NAT entry, folio, and node layout definitions from broader F2FS headers. It is consumed by `node.c`, `namei.c`, `recovery.c`, xattr/inline paths, data block mapping code, and fsync/checkpoint code. The helper `set_mark()` conditionally updates inode checksums under `CONFIG_F2FS_CHECK_FS`, so footer flag changes integrate with metadata integrity checks.

## Risks and edge cases

- NAT address math is tightly coupled to segment geometry and mirror-copy layout; incorrect bit arithmetic can make checkpoint read or write the wrong NAT half.
- `MAX_IOSTAT_PERIOD_MS` is elsewhere, but node defaults here also encode policy; changing thresholds without mount-option plumbing may alter memory and recovery behavior globally.
- `fill_node_footer()` preserves low flag bits when `reset` is false; callers must choose reset mode correctly or stale fsync/dentry/cold bits can leak.
- `is_recoverable_dnode()` has different comparison behavior under CRC and no-CRC checkpoint flags; recovery tests need both.
- `set_nid()` waits for node folio writeback before mutating child pointers, so callers must be ready for blocking behavior.
- `IS_DNODE()` depends on exact offset formulas; future changes to the inode node layout must update both the comment and logic.

## Test signals

Tests should verify NAT current/next address selection across segment boundaries, NAT bitmap flips, raw NAT conversion endianness, node footer fill/copy behavior, recovery version matching with CRC and no-CRC checkpoint modes, direct/indirect/double-indirect `IS_DNODE()` classification, xattr-node classification, child nid mutation dirtying, and checksum updates when check-fs instrumentation is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/node.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/recovery.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/recovery.c

## Purpose

`recovery.c` implements F2FS roll-forward recovery for fsynced data after an unclean shutdown. It scans the warm-node segment chain for recoverable fsync-marked dnodes, reconstructs missing inode pages when needed, recovers inode metadata, dentries, inline data, xattrs, and data block mappings, fixes write pointers, and writes a recovery checkpoint when data recovery succeeds.

## Important APIs and functions

- `f2fs_space_for_roll_forward()` checks whether recovery has enough user blocks and does not exceed the configured roll-forward node block limit.
- `find_fsync_dnodes()` scans recoverable warm-node pages, builds a list of inodes requiring recovery, reconstructs missing inode pages for inode+dentry-marked nodes, tracks last dentry blocks, and detects looped node chains.
- `recover_inode()` restores mode, uid/gid, project quota, size, timestamps, advise flags, F2FS inode flags, GC failure count, inline flags, and marks the inode dirty.
- `recover_dentry()` reconstructs the parent directory entry from the raw inode name/pino, handling encrypted and casefolded names and replacing conflicting entries.
- `do_recover_data()` recovers inline xattrs, xattr node data, inline data, and data block addresses for one recovered node page.
- `check_index_in_prev_nodes()` finds and truncates previous mappings for a destination block so recovery does not leave duplicate live references.
- `recover_data()` performs the second pass over recoverable dnodes, applying inode, dentry, and data recovery to entries discovered in the first pass.
- `f2fs_recover_fsync_data()` is the main entry point for check-only and real recovery.
- `f2fs_create_recovery_cache()` and `f2fs_destroy_recovery_cache()` manage the `fsync_inode_entry` slab.

## Control flow and state

Recovery starts in `f2fs_recover_fsync_data()`. It takes `cp_global_sem` for write to block checkpoint, then calls `find_fsync_dnodes()`. In check-only mode, finding recoverable fsync data or a new inode returns `1` without modifying data. In real mode, it sets `need_writecp`, calls `recover_data()`, releases inode lists, truncates temporary meta pages, fixes zoned write pointers, clears `SBI_POR_DOING`, drops recovered directory inodes, sets `SBI_IS_RECOVERED`, and writes a `CP_RECOVERY` checkpoint.

The first pass begins at `NEXT_FREE_BLKADDR()` of `CURSEG_WARM_NODE` and follows `next_blkaddr_of_node()` through recoverable dnodes. It uses `is_recoverable_dnode()` to match checkpoint version/CRC and `is_fsync_dnode()` to select fsynced nodes. It handles the documented roll-forward scenarios where inode and dnode fsync/dentry marks can appear before or after checkpoint. `sanity_check_node_chain()` uses Floyd-style fast pointer scanning to detect loops and stop corrupt recovery chains.

The second pass scans the same recoverable chain. For each node whose inode is in the recovery list, it may recover inode attributes, recover the dentry if this is the last dentry-marked block for the inode, and call `do_recover_data()`. Once the node block matching `entry->blkaddr` is processed, the inode entry moves to a temporary list to show it is done.

`do_recover_data()` first handles xattr and inline data special cases. For normal data addresses, it obtains or allocates the current dnode path, validates source and destination block addresses, adjusts file size unless `file_keep_isize()` applies, truncates stale source blocks for `NULL_ADDR` destinations, reserves blocks for `NEW_ADDR`, removes any previous reference to the destination block, and finally calls `f2fs_replace_block()` to map the recovered destination block with the right NAT version. It then copies the recovered node footer and marks the current dnode dirty.

## Persistence behavior

The file repairs persistent state after a crash. It can create inode pages, allocate quota for recovered inodes, restore inode metadata, recreate directory entries, delete conflicting dentries into orphan handling, recover inline xattr and xattr-node contents, update block mappings, invalidate stale data blocks, reserve new blocks, replace blocks, allocate new segments, clear power-on-recovery state, and write a checkpoint. It also sets quota repair flags if quota transfer fails during recovered uid/gid changes.

The recovery chain depends on node footer persistence from `node.h`: checkpoint version/CRC, fsync mark, dentry mark, inode number, node id, node offset, and next block address. Its output depends on node-manager helpers in `node.c` to rebuild NAT and node-page state consistently.

## Dependencies and integration points

`recovery.c` depends on node helpers, segment summaries, current segment state, directory entry operations, filename hashing/casefolding/encryption helpers, quota APIs, inline data/xattr helpers, block replacement, checkpoint, write-pointer repair, and error handling. It integrates tightly with `namei.c` because recovered dentries must match normal directory formats, and with `node.c` because all recovered data passes through dnode lookup/allocation, node info validation, xattr recovery, and inode-page reconstruction.

## Risks and edge cases

- Recovery follows on-disk `next_blkaddr` links; loop detection and block-address validation are essential to avoid infinite scans or reading arbitrary metadata.
- Encrypted plus casefolded names may not be hashable without keys, so `init_recovered_filename()` uses the saved on-disk hash appended after the encrypted name.
- `recover_dentry()` deletes conflicting entries and retries; failures after orphan acquisition or quota initialization can leave recovery incomplete and force mount failure/repair.
- `check_index_in_prev_nodes()` uses segment summaries to find previous owners of a destination block; inconsistent summaries are treated as corruption.
- `do_recover_data()` must avoid duplicate block references while handling `NULL_ADDR`, `NEW_ADDR`, and valid destination cases differently.
- If recovery fails, node and meta mappings are truncated and `SBI_POR_DOING` may remain set, so subsequent mount behavior depends on the propagated error.

## Test signals

Recovery tests should cover the eight documented inode/dnode ordering scenarios, check-only mode, missing inode reconstruction, encrypted names, encrypted+casefolded saved hashes, conflicting dentries, quota uid/gid/project changes, inline data, inline xattr, external xattr nodes, `NULL_ADDR` and `NEW_ADDR` destinations, duplicate destination block cleanup via previous summaries, looped node chains, invalid block addresses, zoned write-pointer repair, recovery checkpoint writing, and failure paths that truncate node/meta mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/recovery.c -->
