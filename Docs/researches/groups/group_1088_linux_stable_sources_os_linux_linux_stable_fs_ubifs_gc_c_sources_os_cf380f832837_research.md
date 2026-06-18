# Group Research: group_1088_linux_stable_sources_os_linux_linux_stable_fs_ubifs_gc_c_sources_os_cf380f832837

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/gc.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/gc.c

## Summary
Implements UBIFS garbage collection for data and index LEBs. Data LEB GC copies still-live nodes into the GC journal head and frees the old LEB; index LEB GC marks index nodes dirty in the TNC and defers physical reuse until after commit.

## Main Responsibilities
- Switch and synchronize the GC journal head.
- Scan candidate LEBs, distinguish data versus index LEBs, and reclaim or defer them.
- Sort live data, inode, dent, and xent nodes before relocation to preserve useful read patterns.
- Move live nodes through the GC write buffer and update TNC locations.
- Handle authenticated-mode auth-node hashing and dirt accounting.
- Coordinate GC with commits, write-buffer synchronization, lprops state, and the `idx_gc` deferred index-LEB list.

## Key Interfaces
- `ubifs_garbage_collect()` is the top-level GC loop used by journal space reservation.
- `ubifs_garbage_collect_leb()` reclaims one selected LEB.
- `ubifs_gc_start_commit()` and `ubifs_gc_end_commit()` integrate GC state with commit.
- `ubifs_destroy_idx_gc()` and `ubifs_get_idx_gc_leb()` manage deferred index-GC records.
- Internal helpers include `switch_gc_head()`, `sort_nodes()`, `move_nodes()`, `move_node()`, and `gc_sync_wbufs()`.

## Control Flow And Behavior
For a completely freeable non-index LEB, GC syncs write buffers if needed, updates lprops, unmaps the LEB, and either returns it or retains it as the next GC head. For ordinary data LEBs, it scans all nodes, removes obsolete nodes by asking `ubifs_tnc_has_node()`, sorts remaining nodes, copies them into the GC head with `ubifs_wbuf_write_nolock()`, replaces TNC references, syncs non-GC write buffers, updates lprops, and unmaps the old LEB when possible.

Index LEBs are treated differently. GC scans index nodes, reads their keys and levels, marks them dirty with `ubifs_dirty_idx_node()`, records the LEB on `c->idx_gc`, and marks lprops as free but not immediately reusable. Commit later sets `unmap` on eligible `idx_gc` entries and `ubifs_gc_end_commit()` unmaps them after commit recovery guarantees are satisfied.

The top-level GC loop finds dirty LEBs using `ubifs_find_dirty_leb()`, retries with adjusted minimum reclaimable space, respects soft and hard LEB limits, and returns `-EAGAIN` when commit is required or index GC made space that cannot be used yet.

## State And Synchronization
GC requires the commit lock and locks the GC write buffer mutex. It synchronizes all non-GC write buffers before erasing LEBs whose old contents may be obsoleted by buffered data. It updates `c->gced_lnum` and `c->gc_seq` with memory barriers so TNC races can detect relocated nodes.

## Cross-File Interactions
Depends on `io.c` for UBI wrappers and write-buffer operations, `lprops.c` for LEB state changes and dirty LEB selection, `log.c` for adding the GC head bud to the log, and TNC/index code for node validity, replacement, and dirty index-node marking.

## Risks
The sensitive areas are synchronization before unmap, `gc_seq` race signaling, authenticated hash/auth-node placement, deferred index LEB reuse, and correct lprops transitions. A mistake can lose the only valid copy of a node after power cut, expose stale LEB contents, or make GC loop indefinitely under low-space pressure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/io.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/io.c

## Summary
Provides the UBIFS low-level I/O layer: UBI operation wrappers, node validation, node preparation, CRC/HMAC setup, padding, sequence numbering, and journal write-buffer support.

## Main Responsibilities
- Wrap UBI read, write, change, map, unmap, and mapping-status operations with UBIFS assertions, diagnostics, recovery-test hooks, and read-only error handling.
- Validate on-flash UBIFS nodes by magic, type, length range, LEB bounds, and CRC.
- Initialize node common headers, sequence numbers, CRCs, optional HMAC fields, and node-group markers.
- Add UBIFS padding nodes or padding bytes for min-I/O alignment.
- Implement `struct ubifs_wbuf` seek, write, flush, timer, inode tracking, and background synchronization behavior.
- Support reading nodes that overlap an unwritten write buffer.

## Key Interfaces
- UBI wrappers: `ubifs_leb_read()`, `ubifs_leb_write()`, `ubifs_leb_change()`, `ubifs_leb_unmap()`, `ubifs_leb_map()`, `ubifs_is_mapped()`.
- Node helpers: `ubifs_check_node()`, `ubifs_pad()`, `ubifs_init_node()`, `ubifs_crc_node()`, `ubifs_prepare_node_hmac()`, `ubifs_prepare_node()`, `ubifs_prep_grp_node()`.
- Write-buffer APIs: `ubifs_wbuf_sync_nolock()`, `ubifs_wbuf_seek_nolock()`, `ubifs_bg_wbufs_sync()`, `ubifs_wbuf_write_nolock()`, `ubifs_wbuf_init()`, `ubifs_wbuf_add_ino_nolock()`, `ubifs_sync_wbufs_by_inode()`.
- Direct node I/O: `ubifs_write_node_hmac()`, `ubifs_write_node()`, `ubifs_read_node_wbuf()`, `ubifs_read_node()`.

## Control Flow And Behavior
Writes first check media and mount state, reject `c->ro_error`, use recovery-test wrappers when enabled, and switch the filesystem read-only on hard write/map/unmap failures. Reads allow controlled `-EBADMSG` handling so higher layers can distinguish raw read corruption from validation failures.

`ubifs_check_node()` validates the common header before CRC calculation, including node type range and type-specific size bounds from `c->ranges`. Data-node CRC checks can be skipped by mount option except while mounting, remounting writable, or when forced.

Write buffers are sized for `max_write_size` but flushed only up to the used area rounded to `min_io_size`. After partial flushes, the effective write-buffer size is adjusted so later writes regain optimal `max_write_size` alignment. Large writes may fill and flush the current buffer, write whole max-write chunks directly, then leave a tail buffered with a timer.

`ubifs_read_node_wbuf()` handles data that has been logically written but not flushed by combining flash reads before the write-buffer offset with bytes copied from the in-memory write buffer.

## State And Synchronization
Write buffers use `io_mutex` for caller-level serialization and a spinlock for fields such as `offs`, `used`, `avail`, `next_ino`, and inode tracking. Timers set `need_sync` and wake the background thread. Sequence numbers are allocated under `c->cnt_lock`; overflow forces read-only mode.

## Cross-File Interactions
Journal, log, commit, GC, recovery, and TNC code rely on this file for safe node writes and reads. `journal.c` uses write buffers for atomic grouped journal operations, `gc.c` uses the GC head write buffer, and `lprops.c` debug checks synchronize write buffers before media scans.

## Risks
Alignment arithmetic and partial-buffer flushing are high risk because UBIFS must preserve both flash programming constraints and recoverable node boundaries. Node validation must reject malformed lengths before CRC reads. Read-only transition paths must avoid further writes after media errors. Overlap reads must exactly match pending write-buffer contents.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/ioctl.c

## Summary
Implements UBIFS file attribute and encryption ioctl support. It maps EXT2-style file flags to UBIFS inode flags and delegates fscrypt ioctl commands to the generic fscrypt layer after enabling UBIFS encryption support when needed.

## Main Responsibilities
- Propagate UBIFS inode flags to VFS inode flags.
- Convert between ioctl-visible `FS_*_FL` flags and internal `UBIFS_*_FL` flags.
- Get and set file attributes through the modern `fileattr` API.
- Budget, update, dirty, and optionally synchronously write inode flag changes.
- Dispatch fscrypt policy/key/nonce ioctls and compat variants.

## Key Interfaces
- `ubifs_set_inode_flags()` updates `inode->i_flags` from `ubifs_inode(inode)->flags`.
- `ubifs_fileattr_get()` fills `struct file_kattr` with supported flags.
- `ubifs_fileattr_set()` validates and applies supported flag changes.
- `ubifs_ioctl()` handles fscrypt ioctls.
- `ubifs_compat_ioctl()` maps compat fscrypt ioctls to native handling.

## Control Flow And Behavior
Only compression, sync, append, immutable, and directory-sync flags are settable through file attributes. Encryption is gettable but not settable through this path. Special files return `-ENOTTY`, FS_X-style attributes return `-EOPNOTSUPP`, and unsupported flags are rejected.

`setflags()` budgets one dirtied inode, locks `ui_mutex`, replaces only the settable UBIFS flags, updates VFS inode flags and ctime, marks the inode dirty synchronously, then releases the budget if the inode was already dirty. Synchronous inodes are forced out with `write_inode_now()`.

For `FS_IOC_SET_ENCRYPTION_POLICY`, UBIFS first calls `ubifs_enable_encryption()` and then delegates to `fscrypt_ioctl_set_policy()`. Other fscrypt key and policy operations are direct pass-throughs.

## State And Synchronization
Flag mutation is protected by the UBIFS inode mutex. Budgeting accounts for the inode node and attached inode data length. The file does not perform journal writes directly; it marks inode state dirty for normal UBIFS writeback.

## Cross-File Interactions
Depends on inode journaling and budgeting code to persist flag changes. It interacts with fscrypt support for encryption policy and key management and with VFS fileattr/ioctl entry points installed elsewhere in UBIFS.

## Risks
The main risks are flag mapping drift between `UBIFS_SETTABLE_IOCTL_FLAGS`, `UBIFS_GETTABLE_IOCTL_FLAGS`, `ioctl2ubifs()`, and `ubifs2ioctl()`, plus incorrect budgeting for inode flag changes. Allowing unsupported flags or setting encryption through the wrong path would break VFS and fscrypt expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/journal.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/journal.c

## Summary
Implements UBIFS journal writes for inode, directory, data, rename, truncate, and xattr operations. It reserves journal space, writes grouped nodes atomically, updates the TNC, handles orphan transitions, and coordinates with commit, GC, authentication, compression, and encryption.

## Main Responsibilities
- Reserve space in journal heads and trigger GC/commit when space is insufficient.
- Write node groups to the base and data journal heads with correct ordering for recovery and fsync semantics.
- Pack inode, dent, xent, data, and truncation nodes into on-flash form.
- Update the TNC with new node locations or remove obsolete key ranges.
- Add dirty space accounting for deletion, truncation, auth nodes, and obsolete nodes.
- Maintain orphan list entries for unlinked but still-open inodes.
- Support compressed, encrypted, authenticated data-node writes.
- Serialize pathological concurrent reservations through a wait queue after repeated retries.

## Key Interfaces
- Reservation helpers: `make_reservation()`, `reserve_space()`, `write_head()`, `release_head()`, `finish_reservation()`.
- Inode/name operations: `ubifs_jnl_update()`, `ubifs_jnl_write_inode()`, `ubifs_jnl_delete_inode()`.
- Data operations: `ubifs_jnl_write_data()`.
- Rename operations: `ubifs_jnl_xrename()` and `ubifs_jnl_rename()`.
- Truncate operation: `ubifs_jnl_truncate()` with `truncate_data_node()`.
- Xattr operations: `ubifs_jnl_delete_xattr()` and `ubifs_jnl_change_xattr()`.

## Control Flow And Behavior
Space reservation takes `commit_sem` for read, then locks the target write buffer. If the current bud lacks space, it looks for free space; if none exists, it unlocks the head, runs GC, may request commit, and retries. After excessive concurrent retries, tasks are queued so one reserver proceeds at a time.

Journal updates build all nodes for an operation in one contiguous buffer before sequence numbers are assigned. Directory updates write dent/xent, child inode, and parent/host inode, with host or parent inode last so fsync of that inode also flushes related metadata. Rename and exchange operations similarly write all affected dent and inode nodes as a recoverable group.

Data writes compress folio data when enabled, encrypt if required, prepare the data node, write it to `DATAHD`, track the inode in the write buffer, calculate node hash, and add it to the TNC. If allocation fails in reclaim contexts, the shared write-reserve buffer is used under its mutex.

Truncation writes an inode node, truncation node, and optionally a recompressed/reencrypted final data node, then removes the truncated key range from the TNC. Inode deletion can avoid writing a second deletion inode if no commit happened since the unlink journal update.

## State And Synchronization
Uses `commit_sem`, per-write-buffer mutexes, inode `ui_mutex` and `ui_lock`, `reserve_space_wq`, and `need_wait_space`. Successful operations clear UBIFS inode dirty state and update `synced_i_size`. Error paths switch UBIFS to read-only after journal/TNC consistency failures.

## Cross-File Interactions
Uses `io.c` write-buffer and node preparation APIs, `log.c` bud insertion through reservation, `gc.c` for space reclamation, key helpers from `key.h`, lprops dirty accounting, TNC add/remove APIs, orphan management, compression, encryption, and authentication helpers.

## Risks
Journal ordering is critical for power-cut recovery and fsync semantics. Risks include releasing a head before all needed state is recorded, mismatching journal node offsets with TNC updates, incorrect orphan cleanup on partial failure, reservation retry starvation, xattr deletion edge cases, and compressed/encrypted truncation of partial final blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/key.h -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/key.h

## Summary
Defines UBIFS key construction, decoding, comparison, hashing, and flash-format conversion helpers. The current implementation supports the simple 64-bit UBIFS key format.

## Main Responsibilities
- Define the simple key scheme layout: inode number plus key type plus block number or name hash.
- Provide directory-name hash helpers and reserved readdir hash avoidance.
- Initialize in-memory and on-flash keys for inode, dent, xent, data, truncation, invalid, lowest, and highest key ranges.
- Extract key type, inode number, hash, and block fields from memory and flash formats.
- Convert keys between little-endian on-flash representation and CPU-native in-memory representation.
- Compare, copy, and test key equality.
- Report whether a key is name-hash based and compute max file size for the key format.

## Key Interfaces
- Hash helpers: `key_mask_hash()`, `key_r5_hash()`, `key_test_hash()`.
- Constructors: `ino_key_init()`, `dent_key_init()`, `dent_key_init_hash()`, `xent_key_init()`, `data_key_init()`, `trun_key_init()`, `invalid_key_init()`.
- Flash constructors: `ino_key_init_flash()`, `dent_key_init_flash()`, `xent_key_init_flash()`.
- Range helpers: `lowest_ino_key()`, `highest_ino_key()`, `lowest_dent_key()`, `lowest_xent_key()`, `highest_data_key()`.
- Accessors and converters: `key_type()`, `key_inum()`, `key_hash()`, `key_block()`, flash variants, `key_read()`, `key_write()`, `key_write_idx()`.
- Utility helpers: `key_copy()`, `keys_cmp()`, `keys_eq()`, `is_hash_key()`, `key_max_inode_size()`.

## Control Flow And Behavior
Directory and xattr entry keys hash the fscrypt name bytes via `c->key_hash`, then combine the masked hash with the key type. Hash values 0, 1, and 2 are avoided because they are reserved for `"."`, `".."`, and end-of-readdir markers. Data keys encode a block number in the low bits and assert it fits the simple key block mask.

Most helpers take `struct ubifs_info *c` even though the simple format does not use it directly; this preserves the abstraction for possible future key formats.

## State And Synchronization
This header has no mutable global state. It relies on callers to pass valid names, inode numbers, and blocks. Endianness conversion is explicit for on-flash fields.

## Cross-File Interactions
Used throughout journal, TNC, replay, scan, GC, lprops debug scanning, xattr, directory, and inode paths. `journal.c` uses constructors for all journaled nodes; `gc.c` and `lprops.c` decode keys from scanned nodes; TNC code depends on comparison and range helpers.

## Risks
Any change to bit layout, masks, endian conversion, or ordering semantics affects on-flash compatibility and TNC ordering. Name-hash collision behavior depends on correctly identifying hash keys and preserving minor hash/cookie handling in callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/key.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/log.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/log.c

## Summary
Implements UBIFS log manipulation, bud registration, commit log transitions, post-commit cleanup, and log consolidation. The log records references to journal buds and commit-start nodes rather than file data.

## Main Responsibilities
- Maintain the RB-tree of active buds and journal-head bud lists.
- Map LEB numbers to buds and write buffers.
- Calculate available circular log space.
- Add new bud references to the log while enforcing log and journal size limits.
- Start, end, and post-process commits by writing commit-start and reference nodes, moving the log tail, releasing old buds, and unmapping old log LEBs.
- Consolidate a crowded recovery log by rewriting unique references and the first commit-start node without gaps.
- Validate bud byte accounting in debug mode.

## Key Interfaces
- `ubifs_search_bud()` finds a bud by LEB number.
- `ubifs_get_wbuf()` returns the write buffer associated with a bud LEB.
- `ubifs_add_bud()` inserts a bud into active structures.
- `ubifs_add_bud_to_log()` writes a reference node and registers a new bud.
- `ubifs_log_start_commit()`, `ubifs_log_end_commit()`, and `ubifs_log_post_commit()` implement commit log phases.
- `ubifs_consolidate_log()` rewrites duplicate-filled logs after failed commits.

## Control Flow And Behavior
Adding a bud allocates both in-memory bud state and an on-flash reference node, locks `log_mutex`, verifies enough log space remains for the next commit, checks `max_bud_bytes`, optionally requests background commit, maps empty target buds before referencing them, writes the reference node at the log head, updates the authenticated log hash state, advances `lhead_offs`, and inserts the bud into memory.

Commit start writes a commit-start node plus reference nodes for all still-open journal heads to a fresh log LEB. It resets log hash state, copies hash state to journal heads, advances the log head, and moves closed buds to `old_buds` while preserving open buds by changing their start offset to the current write-buffer offset.

Commit end moves the log tail, restores `min_log_bytes`, subtracts committed bud bytes, and writes the master node. Post-commit returns old bud LEBs to lprops and unmaps obsolete log LEBs only after recovery no longer needs them.

Log consolidation scans from tail to head, keeps only the first commit-start node and unique bud references, writes them compactly with `ubifs_leb_change()`, unmaps trailing log LEBs, and updates the log head.

## State And Synchronization
Bud tree and bud-byte accounting are protected by `buds_lock`; log head/tail and reference writes are serialized by `log_mutex`. Commit start runs in an exclusive phase without taking those locks for all operations because writers are blocked.

## Cross-File Interactions
Journal reservation calls `ubifs_add_bud_to_log()` when switching heads. GC uses it for the GC head. Commit code calls the start/end/post phases. Recovery and replay depend on the exact log records and old-bud retention rules. Authentication code consumes and copies log hash state.

## Risks
The highest-risk areas are circular log space accounting, preserving one full log LEB for future commits, not releasing old buds before commit is durable, mapping empty buds before logging references, and keeping `bud_bytes` consistent. Mistakes can make recovery follow stale references or lose needed journal data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/lprops.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/lprops.c

## Summary
Implements UBIFS LEB properties categorization, heap/list maintenance, lprops mutation, fast lookup helpers, and debug consistency checks. LEB properties drive free-space allocation, garbage collection, and index/data space accounting.

## Main Responsibilities
- Categorize main-area LEBs as dirty, dirty-index, free, unclassified, empty, freeable, or freeable-dirty-index.
- Maintain category heaps for fast dirty/free selection and lists for empty/freeable/unclassified cases.
- Update lprops and global space statistics with copy-on-write LPT handling.
- Maintain dead, dark, used, free, dirty, empty, index, taken-empty, and GC index counters.
- Provide fast find helpers for common allocator and GC queries.
- Validate categories, heaps, lists, and full lprops accounting in debug builds by scanning media.

## Key Interfaces
- Category management: `ubifs_add_to_cat()`, `ubifs_replace_cat()`, `ubifs_ensure_cat()`, `ubifs_categorize_lprops()`.
- Lprops mutation and wrappers: `ubifs_change_lp()`, `ubifs_change_one_lp()`, `ubifs_update_one_lp()`.
- Read/stat helpers: `ubifs_read_one_lp()`, `ubifs_get_lp_stats()`.
- Fast find helpers: `ubifs_fast_find_free()`, `ubifs_fast_find_empty()`, `ubifs_fast_find_freeable()`, `ubifs_fast_find_frdi_idx()`.
- Debug validation: `dbg_check_cats()`, `dbg_check_heap()`, `dbg_check_lprops()`.

## Control Flow And Behavior
Heap categories compare different values depending on category: free space for free LEBs, free plus dirty for dirty-index LEBs, and dirty space for ordinary dirty LEBs. If a heap is full, a new better candidate may replace a lower-value bottom entry, pushing the displaced LEB to the unclassified list.

`ubifs_change_lp()` is the central mutation path. It obtains a dirty copy of lprops when needed, adjusts global accounting by removing the old non-index contribution, applies free/dirty/flag changes, recalculates empty and index counters, adds the new non-index contribution, adjusts taken-empty and `idx_gc_cnt`, then recategorizes or heap-adjusts the LEB under `space_lock`.

Categorization treats taken LEBs as unclassified, fully free LEBs as empty, fully free+dirty non-index LEBs as freeable, fully free+dirty index LEBs as `FRDI_IDX`, index LEBs with enough reclaimable space as `DIRTY_IDX`, and data LEBs as dirty or free based on dirty/free thresholds.

Debug scanning synchronizes write buffers, scans LEB contents, asks the TNC whether nodes are live, recalculates free and dirty bytes, allows specific unclean-unmount index/freeable exceptions, and compares totals with stored lprops statistics.

## State And Synchronization
Most public mutation helpers acquire and release the lprops mutex through `ubifs_get_lprops()` and `ubifs_release_lprops()`. `ubifs_change_lp()` requires `lp_mutex`, updates global space totals under `space_lock`, and accounts for LPT copy-on-write through dirty pnode lookup.

## Cross-File Interactions
Journal and GC rely on lprops to find space and dirty LEBs. Log post-commit returns old buds through lprops. Commit and LPT code use category replacement during copy-on-write. TNC and scanner code are used in debug validation to classify live versus dirty node bytes.

## Risks
Space accounting errors are severe because UBIFS budgeting, GC, and commit all depend on these totals. Heap/list category drift can hide usable LEBs or select unsafe ones. Dead/dark accounting must match GC watermarks. Debug validation has to tolerate legitimate unclean-unmount states without masking real corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/lprops.c -->