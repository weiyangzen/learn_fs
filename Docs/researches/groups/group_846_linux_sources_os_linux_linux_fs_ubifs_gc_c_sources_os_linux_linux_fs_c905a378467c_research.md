# Group Research: UBIFS GC, I/O, Journal, Keys, Log, and LEB Properties

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

This grouped report covers the UBIFS files requested in work item `group_846_linux_sources_os_linux_linux_fs_ubifs_gc_c_sources_os_linux_linux_fs_c905a378467c`. Each section is wrapped in the exact file research markers required by the finalizer.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/gc.c -->
# File Research: sources/os/linux/linux/fs/ubifs/gc.c

## Purpose

`gc.c` implements UBIFS out-of-place garbage collection for logical eraseblocks (LEBs). It distinguishes data LEBs from index LEBs: data nodes are copied into the GC journal head and their TNC references are replaced, while index nodes are marked dirty so the next commit can rewrite the index and later release the old index LEB. The file also defines the commit hooks that make GC'd index LEBs safely reusable.

## Main Control Flow

The core entry point is `ubifs_garbage_collect()`. It is called with the commit lock held and the GC write-buffer empty. It first checks whether a commit should run, locks the GC head write-buffer, then repeatedly asks lprops for a dirty or empty candidate via `ubifs_find_dirty_leb()`. Each selected LEB is processed by `ubifs_garbage_collect_leb()`.

`ubifs_garbage_collect_leb()` handles three cases. If `free + dirty == leb_size`, the LEB is immediately freeable: lprops are updated and the block is either retained in `c->gc_lnum` or unmapped and returned. If scanning shows an index LEB, each index node is looked up and dirtied in the TNC with `ubifs_dirty_idx_node()`, then the LEB is added to `c->idx_gc` and marked as freed only after commit. Otherwise the function treats the LEB as data, moves live nodes with `move_nodes()`, syncs other write-buffers to protect recovery, updates lprops, bumps `c->gc_seq`, and either retains or unmaps the LEB.

`move_nodes()` prepares the GC head if needed with `switch_gc_head()`, filters and sorts scanned nodes using `sort_nodes()`, then repeatedly writes data nodes and non-data nodes into the GC head. Data nodes are kept in inode/block order for bulk-read behavior; inode and dent/xent nodes are ordered to favor useful packing and directory iteration locality. Authenticated mounts add an auth node after moved nodes.

## Important Helpers and State

`switch_gc_head()` syncs the current GC write-buffer, unmaps the reserved `c->gc_lnum`, adds it as a new GC bud in the log, and seeks the GC write-buffer to it. This links GC movement to the journal/log machinery.

`gc_sync_wbufs()` syncs all non-GC journal heads before freeing an LEB. This is a recovery invariant: an obsolete-making node may still sit in a write-buffer, so erasing the old LEB before that node reaches flash could lose data after an unclean unmount.

`ubifs_gc_start_commit()` unmaps non-index freeable LEBs, marks already GC'd index LEBs as unmap-ready, and records fully dirty/free index LEBs for post-commit unmapping. `ubifs_gc_end_commit()` performs those unmaps and updates lprops after commit. `ubifs_destroy_idx_gc()` and `ubifs_get_idx_gc_leb()` maintain the index-GC list for unmount and commit allocation.

## Dependencies

This file depends heavily on lprops categorization and accounting (`ubifs_find_dirty_leb()`, `ubifs_change_one_lp()`, `ubifs_return_leb()`), the scanner (`ubifs_scan()`), TNC lookup/update APIs (`ubifs_tnc_has_node()`, `ubifs_tnc_replace()`, `ubifs_dirty_idx_node()`), journal/log functions (`ubifs_add_bud_to_log()`), write-buffer I/O (`ubifs_wbuf_*()`), and authentication hashing.

## Invariants and Edge Cases

GC uses soft and hard movement limits. After `SOFT_LEBS_LIMIT`, index GC work can force `-EAGAIN` so commit can make progress; after `HARD_LEBS_LIMIT`, lack of progress becomes `-ENOSPC`. The dynamic `min_space` threshold starts at `dead_wm`, falls when retained GC makes progress, and rises toward `dark_wm` when a retained LEB does not free space. Error paths sync the GC write-buffer, switch UBIFS to read-only for unexpected failures, and return any taken LEB to lprops when possible.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/io.c -->
# File Research: sources/os/linux/linux/fs/ubifs/io.c

## Purpose

`io.c` implements UBIFS low-level I/O wrappers, node validation/preparation, write-buffer management, and node read/write helpers. It is the boundary between UBIFS metadata semantics and UBI LEB operations, adding UBIFS-specific checks, CRCs, sequence numbers, padding, timers, and read-only failover.

## UBI Wrappers and Read-Only Failover

`ubifs_leb_read()`, `ubifs_leb_write()`, `ubifs_leb_change()`, `ubifs_leb_unmap()`, `ubifs_leb_map()`, and `ubifs_is_mapped()` wrap the corresponding UBI APIs. Write-like operations assert the filesystem is not mounted read-only, return `-EROFS` after an earlier fatal write error, and call `ubifs_ro_mode()` on I/O failure. `ubifs_ro_mode()` sets `ro_error`, disables skipped data CRC checks, marks the VFS superblock read-only, warns, and dumps the stack.

## Node Checking and Preparation

`ubifs_check_node()` validates the common header magic, node type, length range, LEB bounds, and CRC. It may skip data-node CRCs when `no_chk_data_crc` is active, but not during mount/remount recovery or when forced. It records magic, node type, and CRC error counters when stats are present.

`ubifs_pad()` emits either a padding node or padding bytes. `next_sqnum()`, `ubifs_init_node()`, `ubifs_crc_node()`, `ubifs_prepare_node_hmac()`, `ubifs_prepare_node()`, and `ubifs_prep_grp_node()` initialize common headers, assign monotonically increasing sequence numbers, add padding, optionally insert HMACs, and compute CRCs. Grouped node preparation sets `UBIFS_IN_NODE_GROUP` or `UBIFS_LAST_OF_NODE_GROUP`, which journal operations rely on for atomic multi-node updates.

## Write-Buffer Mechanics

UBIFS write-buffers are sized for `max_write_size` but synchronize only the used region rounded up to `min_io_size`. `ubifs_wbuf_sync_nolock()` pads the dirty tail, writes it, advances `wbuf->offs`, recomputes the next buffer size to regain max-write alignment, clears inode tracking, and invokes an optional sync callback for lprops accounting.

`ubifs_wbuf_write_nolock()` is the central buffered write path. It handles small nodes that fit entirely in the buffer, nodes that fill and flush the buffer, unaligned offsets that must be advanced to the next optimal write boundary, direct writes of full max-write units, and residual data left buffered with an hrtimer. It returns `-ENOSPC` if the node cannot fit in the current LEB and produces detailed dumps on unexpected write failures.

`ubifs_bg_wbufs_sync()` is driven by timer state (`need_sync`, `need_wbuf_sync`) and synchronizes only unlocked write-buffers needing flush. It cancels timers after fatal errors to avoid repeated failures. `ubifs_wbuf_seek_nolock()` retargets an empty write-buffer to a new LEB offset.

## Read Paths

`ubifs_write_node_hmac()` and `ubifs_write_node()` write one prepared, min-IO-aligned node directly to media. `ubifs_read_node()` reads from flash, validates type, CRC, and exact length, and reports mapping status on errors. `ubifs_read_node_wbuf()` overlays unwritten bytes from a write-buffer when the requested node overlaps buffered data, preventing stale reads before flush.

## Inode-Scoped Sync Tracking

`ubifs_wbuf_init()` allocates both the data buffer and an inode-number array. `ubifs_wbuf_add_ino_nolock()` records inodes whose nodes are currently buffered. `ubifs_sync_wbufs_by_inode()` scans non-GC heads for a matching inode and synchronizes those write-buffers, supporting fsync-style guarantees without flushing unrelated GC copies.

## Key Invariants

Offsets are 8-byte aligned and write-buffer writes respect `min_io_size` and `max_write_size`. Unexpected write errors move the filesystem to read-only mode. Buffered writes require the caller to hold `wbuf->io_mutex`; internal fields shared with readers use `wbuf->lock`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/ioctl.c -->
# File Research: sources/os/linux/linux/fs/ubifs/ioctl.c

## Purpose

`ioctl.c` implements UBIFS support for ext2-compatible file attribute operations and fscrypt ioctls. It bridges persistent UBIFS inode flags, VFS inode flags, generic `fileattr` get/set APIs, and encryption policy/key ioctl dispatch.

## Flag Mapping

The file defines two masks. `UBIFS_SETTABLE_IOCTL_FLAGS` includes compression, sync, append-only, immutable, and directory-sync flags. `UBIFS_GETTABLE_IOCTL_FLAGS` adds encryption reporting. `ioctl2ubifs()` maps user-visible `FS_*` flags to `UBIFS_*` inode flags, while `ubifs2ioctl()` maps persistent UBIFS flags back to `FS_*` values and reports encrypted files through `FS_ENCRYPT_FL`.

`ubifs_set_inode_flags()` propagates UBIFS inode flags into `inode->i_flags`, clearing and then setting `S_SYNC`, `S_APPEND`, `S_IMMUTABLE`, `S_DIRSYNC`, and `S_ENCRYPTED`. This function is used after flag changes and during inode setup elsewhere in UBIFS.

## File Attribute Get/Set

`ubifs_fileattr_get()` rejects special dentries with `-ENOTTY`, converts UBIFS flags to generic fileattr flags, and fills the caller's `file_kattr`.

`ubifs_fileattr_set()` rejects special dentries, FS_X-style attributes, and unsupported flags. It masks input down to settable flags and removes `FS_DIRSYNC_FL` for non-directories. Actual persistence happens in `setflags()`.

`setflags()` budgets for a dirtied inode, locks the UBIFS inode mutex, replaces only settable UBIFS flag bits, updates VFS inode flags, sets ctime, and marks the inode dirty synchronously. If the inode was already dirty, it releases the just-reserved budget because existing dirty-inode budget covers the eventual write. If the inode is synchronous, it calls `write_inode_now()`.

## Encryption Ioctls

`ubifs_ioctl()` handles fscrypt policy, key-management, key-status, and nonce ioctls. Setting an encryption policy first calls `ubifs_enable_encryption(c)` so the filesystem feature state is enabled before delegating to fscrypt. Unsupported commands return `-ENOTTY`.

When `CONFIG_COMPAT` is enabled, `ubifs_compat_ioctl()` accepts the same fscrypt commands, converts the userspace pointer through `compat_ptr()`, and delegates to `ubifs_ioctl()`. Other compat commands return `-ENOIOCTLCMD`.

## Dependencies and Invariants

This file depends on VFS fileattr helpers, fscrypt ioctl helpers, UBIFS budgeting, UBIFS inode dirty accounting, and writeback. It intentionally does not allow userspace to set the encryption flag via generic attribute changes; encryption is reported but controlled through fscrypt policy ioctls.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/journal.c -->
# File Research: sources/os/linux/linux/fs/ubifs/journal.c

## Purpose

`journal.c` implements UBIFS journal write operations for metadata, data, directory operations, truncation, inode deletion, and xattrs. UBIFS uses a multi-headed journal: the base head stores inode, direntry, xentry, and truncation nodes, while data heads store data nodes. Journal operations reserve space, write grouped nodes atomically with respect to recovery, update the TNC, manage orphan state, and mark inodes clean.

## Reservation and Write Pipeline

`reserve_space()` locks a journal head write-buffer, checks available space, finds free space through lprops, invokes GC on `-ENOSPC`, syncs the previous write-buffer before adding a new bud to the log, writes the bud reference with `ubifs_add_bud_to_log()`, and seeks the head to the selected LEB. It can return `-EAGAIN` when commit is required.

`make_reservation()` wraps `reserve_space()` with `commit_sem` read locking and retry logic. It converts GC `-ENOSPC` to commit/retry behavior, runs `ubifs_run_commit()` on `-EAGAIN`, and after many retries starts serializing reservation contenders through `reserve_space_wq` using `wait_for_reservation()`, `add_or_start_queue()`, and `wake_up_reservation()`. `release_head()` unlocks the write-buffer; `finish_reservation()` releases the commit read lock.

`write_head()` records the current LEB/offset, hashes nodes for authenticated mounts, writes through `ubifs_wbuf_write_nolock()`, and optionally synchronizes the write-buffer. `ubifs_hash_nodes()` walks grouped nodes and appends an auth node when authentication is enabled.

## Node Packing and Clean Accounting

`pack_inode()` serializes VFS and UBIFS inode state into an on-flash inode node, optionally omitting attached data when writing a deletion inode. Small helpers zero unused node fields for deterministic on-flash contents. `mark_inode_clean()` clears UBIFS dirty state and releases dirty-inode budget. `set_dent_cookie()` supplies a random cookie for double-hash directory entries.

## Major Journal Operations

`ubifs_jnl_update()` writes a dent/xent node, the target inode, and the parent/host inode as one grouped update. It handles deletion dentries, xattr ordering, synchronous inode/dirsync flushes, orphan insertion for last references, and TNC add/remove updates.

`ubifs_jnl_write_data()` compresses a folio block when enabled, encrypts it when needed, writes the data node on the data head, calculates the node hash, tracks the inode in the write-buffer, and adds the TNC entry. It falls back to `c->write_reserve_buf` under memory pressure so writeback can still proceed.

`ubifs_jnl_write_inode()` writes an inode to the base head, optionally writing deletion records for hosted xattrs. If the inode's last reference is gone, it removes all TNC records for that inode and deletes orphan state. `ubifs_jnl_delete_inode()` avoids writing a second deletion inode when no commit has happened since unlink and the inode has no xattrs.

`ubifs_jnl_xrename()` handles exchange rename by writing two dentries and one or two parent inodes. `ubifs_jnl_rename()` handles regular rename, replacement, whiteout, cross-directory movement, orphan insertion for replaced inodes, TNC updates/removals, and optional whiteout orphan deletion.

`ubifs_jnl_truncate()` writes an inode node and truncation node, and if the new size splits an existing final data block it reads, decompresses/decrypts, truncates, recompresses/reencrypts, and writes that data node. It removes the truncated data-key range from the TNC.

`ubifs_jnl_delete_xattr()` writes deletion xentry, deletion inode, and updated host inode, then removes xentry and xattr inode ranges from the TNC. `ubifs_jnl_change_xattr()` writes the host inode and xattr inode, ordered so syncing the host also flushes the xattr change.

## Invariants and Failure Behavior

Space reservation must happen before sequence numbers are allocated. Grouped writes use node group markers so recovery can discard incomplete multi-node updates. TNC updates occur only after journal data is written. Errors after journal write generally switch UBIFS to read-only because journal/TNC divergence is dangerous. Authenticated mounts add auth-node space to reservations and mark auth nodes dirty in lprops.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/key.h -->
# File Research: sources/os/linux/linux/fs/ubifs/key.h

## Purpose

`key.h` defines UBIFS key format helpers. UBIFS currently uses the simple 64-bit key format, but most helpers accept `struct ubifs_info *c` to preserve an abstraction boundary for possible future key formats. The simple key stores inode number in the first 32 bits and key type plus block/hash payload in the second 32 bits.

## Hash Helpers

`key_mask_hash()` masks hash values to the simple-key hash field and avoids reserved readdir offsets 0, 1, and 2. `key_r5_hash()` implements the ReiserFS-derived R5 name hash. `key_test_hash()` copies up to four name bytes into a hash value for testing. Directory and xattr entry key initialization uses `c->key_hash`, so the selected hash function is filesystem state.

## Key Constructors

The header provides constructors for all logical UBIFS key classes. `ino_key_init()` and `ino_key_init_flash()` create inode keys. `lowest_ino_key()` and `highest_ino_key()` define search bounds for all keys belonging to an inode.

`dent_key_init()`, `dent_key_init_hash()`, and `dent_key_init_flash()` create directory-entry keys using parent inode plus name hash. `lowest_dent_key()` defines the lower bound for scanning a directory's dentries. `xent_key_init()`, `xent_key_init_flash()`, and `lowest_xent_key()` do the same for extended attribute entries hosted by an inode.

`data_key_init()` creates a data key from inode number and UBIFS block number; `highest_data_key()` creates the upper data-key bound for an inode. `trun_key_init()` creates replay-only truncation keys, and `invalid_key_init()` writes a sentinel invalid key.

Flash constructors write little-endian fields and clear unused bytes up to `UBIFS_MAX_KEY_LEN`. In-memory constructors write host-endian `u32` fields.

## Accessors and Conversion

`key_type()` and `key_type_flash()` extract key type. `key_inum()` and `key_inum_flash()` extract inode numbers. `key_hash()` and `key_hash_flash()` return dent/xent hash payloads. `key_block()` and `key_block_flash()` return data block numbers.

`key_read()` converts an on-flash little-endian key to in-memory format. `key_write()` converts in-memory to flash format and clears unused key bytes. `key_write_idx()` writes the compact index form without clearing bytes beyond the key fields. `key_copy()` copies the full 64-bit key value.

## Comparison and Limits

`keys_cmp()` compares inode field first and payload/type field second, matching the sorted TNC key order. `keys_eq()` tests exact equality. `is_hash_key()` identifies dent/xent keys, which can collide and require name-aware handling. `key_max_inode_size()` derives the maximum file size representable by the active key format; for simple keys it is the block-key space multiplied by `UBIFS_BLOCK_SIZE`.

## Consumers

The journal, GC, TNC, replay, xattr, and directory code all depend on these helpers for consistent key construction. Bugs here would affect lookup ordering, collision handling, flash compatibility, and range deletion.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/key.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/log.c -->
# File Research: sources/os/linux/linux/fs/ubifs/log.c

## Purpose

`log.c` manages the UBIFS journal log: the fixed flash area containing commit-start nodes and reference nodes for bud LEBs. It maintains the in-memory bud tree/list state, enforces log and journal size limits, starts and finishes commit log transitions, releases old buds after commit, and can consolidate the log after failed commits.

## Bud Lookup and Registration

`ubifs_search_bud()` searches the red-black tree of buds by LEB number under `buds_lock`. `ubifs_get_wbuf()` finds the journal head write-buffer associated with a bud LEB. `ubifs_add_bud()` inserts a bud into the tree, links it to its journal head list when heads are initialized, and increases `c->bud_bytes` by the bud's remaining LEB span. This accounting bounds mount-time journal replay.

## Adding Buds to the Log

`ubifs_add_bud_to_log()` allocates a bud and ref node, locks `log_mutex`, checks read-only error state, ensures enough empty log bytes remain for the next commit, enforces `max_bud_bytes`, optionally requests background commit after `bg_bud_bytes`, prepares a ref node, unmaps a fresh log LEB when needed, maps empty bud LEBs before referencing them, writes the ref node with `ubifs_write_node()`, updates authentication hash state, advances the log head, and inserts the bud. It returns `-EAGAIN` when log or journal size pressure requires commit.

## Commit Log Lifecycle

`remove_buds()` runs during commit start. It preserves buds still pointed to by active journal heads by advancing their starts to the current write-buffer offsets; closed buds are removed from the active tree and moved to `old_buds` so recovery can still replay them if commit fails.

`ubifs_log_start_commit()` writes a commit-start node plus ref nodes for active journal heads into a fresh log LEB in one write. It resets the log hash, pads to min-I/O size, updates the log head offset, calls `remove_buds()`, and temporarily drops `min_log_bytes` so writers can use log space while commit continues.

`ubifs_log_end_commit()` moves the log tail to the new commit-start LEB, restores `min_log_bytes` to one LEB so the next commit is guaranteed, subtracts committed bud bytes from `bud_bytes`, checks debug accounting, and writes the master node.

`ubifs_log_post_commit()` finally returns old bud LEBs to lprops and unmaps old log LEBs from the previous tail up to the new tail. This delayed release preserves recovery data until commit is fully durable.

## Log Consolidation

`ubifs_consolidate_log()` handles recovery cases where repeated failed commits leave the log too full for another commit. It scans from tail to head, copies only the first commit-start node and unique reference nodes into compacted log LEBs, writes padded LEB images via `ubifs_leb_change()`, unmaps no-longer-used log LEBs, and updates the log head. `done_already()` tracks duplicate referenced LEBs in an rb-tree, and `add_node()` handles LEB-boundary padding and writing.

## Invariants

Log writes are serialized by `log_mutex` except during the exclusive commit-start phase. `bud_bytes` must match the sum of active head bud spans; `dbg_check_bud_bytes()` verifies this under debug checking. Empty bud LEBs are mapped before the log references them to avoid recovery seeing stale physical contents after an unclean reboot.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/lprops.c -->
# File Research: sources/os/linux/linux/fs/ubifs/lprops.c

## Purpose

`lprops.c` maintains UBIFS LEB properties and their fast lookup categories. Each main-area LEB has free, dirty, flags, category, and heap/list position state. The file keeps category heaps/lists coherent, updates global space accounting, exposes quick find helpers, and contains debug scanners that verify lprops against actual flash contents and the TNC.

## Categories and Heaps

LEBs are categorized as dirty, dirty index, free, uncategorized, empty, freeable, or freeable dirty index. `ubifs_categorize_lprops()` implements the rules. Taken LEBs become uncategorized. Fully free LEBs are empty. LEBs whose free plus dirty equals the LEB size are freeable, with index LEBs going to `LPROPS_FRDI_IDX`. Index LEBs with enough reclaimable space for an index node go to `LPROPS_DIRTY_IDX`; data LEBs with meaningful dirty space go to `LPROPS_DIRTY`, and those with free space go to `LPROPS_FREE`.

The dirty, dirty-index, and free categories are heaps. `get_heap_comp_val()` chooses the comparison metric: free bytes for free LEBs, free plus dirty for dirty index LEBs, and dirty bytes otherwise. `move_up_lpt_heap()`, `adjust_lpt_heap()`, `add_to_lpt_heap()`, and `remove_from_lpt_heap()` implement max-heap maintenance. If a heap is full, `add_to_lpt_heap()` may evict a weaker bottom-half entry to the uncategorized list.

List categories are maintained by `ubifs_add_to_cat()`, `ubifs_remove_from_cat()`, `ubifs_replace_cat()`, and `ubifs_ensure_cat()`. Replacement supports LPT copy-on-write during commit, where pnodes and their embedded lprops can be copied and all category references must be redirected.

## Space Accounting

`ubifs_change_lp()` is the central mutation function. It ensures a dirty copy exists through `ubifs_lpt_lookup_dirty()` when needed, updates free/dirty values and flags, adjusts empty/taken-empty/index counters, recomputes total free/dirty/used/dead/dark space under `space_lock`, changes category placement, and adjusts `idx_gc_cnt`. `ubifs_change_one_lp()` and `ubifs_update_one_lp()` are convenience wrappers that take/release lprops locking around a single LEB update.

`ubifs_calc_dark()` estimates unusable "dark" space from a free+dirty byte count. Space smaller than `dark_wm` is treated as dark, while larger regions cap at `dark_wm` except for a small interval where `MIN_WRITE_SZ` is assumed recoverable. This feeds budgeting and GC decisions.

`ubifs_get_lp_stats()` snapshots aggregate lprops statistics. `ubifs_read_one_lp()` reads a single LEB's properties without mutating them.

## Fast Find APIs

`ubifs_fast_find_free()` returns the top free heap entry. `ubifs_fast_find_empty()` returns the first empty-list entry. `ubifs_fast_find_freeable()` returns a non-index LEB whose content is all free/dirty. `ubifs_fast_find_frdi_idx()` returns an index LEB with all free/dirty space. All require `lp_mutex` and assert that returned LEBs are not taken and have category-appropriate flags.

## Debug Validation

`dbg_check_cats()` verifies list and heap membership, category-specific invariants, `freeable_cnt`, and `idx_gc_cnt`. `dbg_check_heap()` checks heap pointer consistency, hpos values, duplicate entries, and correspondence with LPT lookup.

`scan_check_cb()` is the heavy validation callback for `dbg_check_lprops()`. It verifies category placement, scans non-empty/non-freeable LEBs with `ubifs_scan()`, classifies data versus index content, asks the TNC whether scanned nodes are live, computes used/free/dirty bytes, tolerates documented unclean-unmount cases, and accumulates independently calculated totals. `dbg_check_lprops()` first syncs all write-buffers, scans the LPT range, compares calculated totals with `c->lst`, validates dead/dark accounting, and then checks categories.

## Invariants and Consumers

This file is central to allocation and GC. Journal reservation uses free-space categories, GC uses dirty/freeable categories, commit uses category replacement and index-GC counts, and budgeting consumes global totals. Correct locking matters: category mutations require `lp_mutex`, aggregate counters use `space_lock`, and debug full scans avoid taking the LPT mutex because they run during commit-start style locked contexts.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/lprops.c -->