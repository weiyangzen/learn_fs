# subset-b-005770 Research

This grouped report covers the UBIFS source files assigned to work item `subset-b-005770`. Each section preserves the source path and is bounded by reconciliation markers for splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/gc.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/gc.c

## Purpose

`gc.c` implements UBIFS out-of-place garbage collection for main-area logical eraseblocks (LEBs). It treats data LEBs and index LEBs differently: data LEB GC copies still-live data, inode, directory-entry, and xattr-entry nodes to the GC journal head and updates the TNC to point at the new locations; index LEB GC marks index nodes dirty in the TNC and defers physical reuse until a subsequent commit has made recovery safe. The file also manages the GC journal head, retained GC LEB state, and the list of index LEBs that were logically freed but cannot yet be unmapped.

## Important APIs, Types, And Functions

The externally used entry points are `ubifs_garbage_collect_leb()`, `ubifs_garbage_collect()`, `ubifs_gc_start_commit()`, `ubifs_gc_end_commit()`, `ubifs_destroy_idx_gc()`, and `ubifs_get_idx_gc_leb()`. Internally, `switch_gc_head()` turns `c->gc_lnum` into a bud on journal head `GCHD`, `sort_nodes()` filters obsolete scanned nodes and orders live nodes for better read locality, `move_node()` writes one node to the GC head and replaces its TNC location, `move_nodes()` drains live nodes into the GC head, and `gc_sync_wbufs()` flushes other journal heads before old LEBs are unmapped.

The file uses `struct ubifs_scan_leb` and `struct ubifs_scan_node` from the scan layer, `struct ubifs_lprops` from the LPT/lprops layer, `struct ubifs_wbuf` from the I/O layer, and `struct ubifs_gced_idx_leb` entries on `c->idx_gc`. The important return protocol distinguishes `LEB_FREED`, `LEB_RETAINED`, and `LEB_FREED_IDX`, plus negative errors such as `-EAGAIN`, `-ENOSPC`, `-EROFS`, and media or allocation failures.

## Control Flow

The main GC loop in `ubifs_garbage_collect()` runs under the commit lock and the GC write-buffer mutex. It first refuses to proceed if a commit is already needed, then repeatedly asks lprops for a dirty or empty/freeable LEB with `ubifs_find_dirty_leb()`. Each selected LEB is passed to `ubifs_garbage_collect_leb()`. A ready freed LEB is returned to the caller by number; a retained LEB becomes `c->gc_lnum`; a freed index LEB only becomes usable after commit, so the loop may continue until soft/hard iteration limits request commit or report no progress.

For a data LEB, `ubifs_garbage_collect_leb()` scans the whole LEB, calls `move_nodes()`, synchronizes non-GC write buffers so obsoleting writes are stable, updates lprops to fully free/clean state, updates `c->gced_lnum` and `c->gc_seq` with memory barriers for TNC race handling, and either retains the LEB as the next GC head or unmaps it. `move_nodes()` sorts live data nodes by inode/block and non-data nodes by inode/hash/size, writes what fits into the GC head, emits authentication nodes when needed, and switches the GC head when necessary.

For an index LEB, `ubifs_garbage_collect_leb()` reads each index node key and level, calls `ubifs_dirty_idx_node()` so the TNC will rewrite it, records the LEB on `c->idx_gc`, and changes lprops to free-space accounting with index status cleaned and `idx_gc_cnt` incremented. `ubifs_gc_start_commit()` unmaps immediately freeable non-index LEBs, marks already-GCed index LEBs as eligible for post-commit unmap, and moves freeable dirty index LEBs to `c->idx_gc`. `ubifs_gc_end_commit()` finally unmaps eligible index LEBs and updates lprops to clear `LPROPS_TAKEN`.

## State And Persistence Behavior

GC is tied to persistent safety. Data nodes are never discarded until their replacements are written to the GC journal head and TNC entries have been replaced. Other write buffers are synchronized before unmapping a freeable/data LEB because they may contain nodes that obsolete content in the LEB being collected. Index LEBs are not physically released until commit has made the new index state durable, preserving recovery from old index nodes after an unclean unmount.

The main mutable state is `c->gc_lnum`, `c->jheads[GCHD].wbuf`, `c->idx_gc`, `c->idx_gc_cnt`, lprops free/dirty/index/taken flags, and TNC node locations. Authentication state is updated through `ubifs_shash_update()` on moved nodes and by writing `UBIFS_AUTH_NODE` records to the GC head; the auth node itself is accounted as dirty with `ubifs_add_dirt()`.

## Dependencies And Integration Points

This file integrates with the lprops allocator (`ubifs_find_dirty_leb()`, `ubifs_change_one_lp()`, `ubifs_return_leb()`), log/journal management (`ubifs_add_bud_to_log()`), write-buffer I/O (`ubifs_wbuf_sync_nolock()`, `ubifs_wbuf_seek_nolock()`, `ubifs_wbuf_write_nolock()`), raw UBI operations (`ubifs_leb_unmap()`), scanning (`ubifs_scan()`), key helpers (`key_type()`, `key_inum()`, `key_block()`, `key_hash()`, `key_read()`), TNC mutation (`ubifs_tnc_has_node()`, `ubifs_tnc_replace()`, `ubifs_dirty_idx_node()`), and commit orchestration.

## Risks And Edge Cases

The riskiest paths are partial-progress failures after live nodes have moved, handling `-EAGAIN` without losing a taken lprops entry, and the ordering between write-buffer synchronization, lprops changes, TNC replacement, and LEB unmap. The soft and hard LEB limits defend against pathological no-progress loops, but callers still must handle repeated `-EAGAIN` when nearly full or under tight journal limits. Authentication adds another fitting constraint because `ubifs_auth_node_sz(c)` is subtracted from available GC-head space. The `c->gced_lnum`/`c->gc_seq` barrier protocol is a race-sensitive integration with TNC lookups.

## Test Signals

Useful test signals include GC under low-space workloads, repeated commit-required GC loops, data LEBs containing mixed live/obsolete nodes, index LEB GC followed by power-cut recovery, authenticated mounts, write-buffer error injection, and debug checks such as node order checks, lprops checks, and TNC consistency checks. Expected behavior is that freed LEBs are returned only when safe, index GC is completed after commit, and media write/unmap failures switch UBIFS read-only through the lower I/O path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/io.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/io.c

## Purpose

`io.c` is the UBIFS low-level I/O and write-buffer subsystem. It wraps UBI read/write/change/map/unmap operations, validates node headers and CRCs, prepares nodes for flash by filling common headers, sequence numbers, padding, CRCs, and optional HMACs, and implements journal write buffers that batch small writes while respecting minimum and maximum flash write sizes.

## Important APIs, Types, And Functions

The UBI wrappers are `ubifs_leb_read()`, `ubifs_leb_write()`, `ubifs_leb_change()`, `ubifs_leb_unmap()`, `ubifs_leb_map()`, and `ubifs_is_mapped()`. Validation and node-preparation helpers include `ubifs_check_node()`, `ubifs_pad()`, `ubifs_init_node()`, `ubifs_crc_node()`, `ubifs_prepare_node_hmac()`, `ubifs_prepare_node()`, and `ubifs_prep_grp_node()`. Write-buffer APIs include `ubifs_wbuf_sync_nolock()`, `ubifs_wbuf_seek_nolock()`, `ubifs_bg_wbufs_sync()`, `ubifs_wbuf_write_nolock()`, `ubifs_read_node_wbuf()`, `ubifs_wbuf_init()`, `ubifs_wbuf_add_ino_nolock()`, and `ubifs_sync_wbufs_by_inode()`.

The central type is `struct ubifs_wbuf`, with `buf`, `inodes`, `lnum`, `offs`, `size`, `avail`, `used`, `io_mutex`, `lock`, timer state, optional `sync_callback`, and journal-head identity. `struct ubifs_ch` is the common node header validated by reads and populated by writes.

## Control Flow

Raw write-like wrappers assert the filesystem is not mounted read-only and not on read-only media, return `-EROFS` after a prior write error, optionally route through debug recovery hooks, and call `ubifs_ro_mode()` on write/map/unmap failures. Reads report errors but do not make the filesystem read-only. `ubifs_check_node()` validates magic, node type, length range from `c->ranges`, and CRC. It may skip data-node CRC checks only when allowed by mount state and `must_chk_crc`.

Write-buffer writes first check that the aligned node fits in the current LEB. If the node fits in available buffer space, it is copied into RAM and either left pending with a timer or flushed if it exactly fills the buffer. Larger writes flush any partial buffer, write full maximum-write-size chunks directly, and keep only the tail in the buffer. `ubifs_wbuf_sync_nolock()` writes only the used portion rounded to `min_io_size`, pads the remainder, advances offsets, recalculates the temporary buffer size needed to regain `max_write_size` alignment, clears inode tracking, and invokes `sync_callback`.

Reads can overlap a pending write buffer. `ubifs_read_node_wbuf()` copies the overlapping suffix from RAM and reads any prefix from flash before validating the reconstructed node. Background synchronization is timer-driven: timer expiry marks a buffer and wakes the background thread, `ubifs_bg_wbufs_sync()` skips locked buffers, syncs marked buffers, and cancels all timers after an error to avoid repeated failures.

## State And Persistence Behavior

The file owns UBIFS's transition to read-only error mode. `ubifs_ro_mode()` sets `c->ro_error`, clears data-CRC skipping, sets `SB_RDONLY`, logs the reason, and dumps a stack once. Sequence numbers are assigned by `next_sqnum()` under `c->cnt_lock`; near or actual overflow logs warnings or forces read-only. Padding nodes and padding bytes make scanned media unambiguous at minimum-I/O boundaries, while 8-byte alignment preserves UBIFS node layout.

Write buffers intentionally allow recently written nodes to live temporarily in RAM. Callers that require durability call sync paths directly, rely on timer/background sync, or call inode-targeted synchronization. The `inodes` side array records inode numbers represented in a pending buffer so `ubifs_sync_wbufs_by_inode()` can flush the right journal heads for fsync-style operations, excluding the GC head because those nodes are copies of existing media nodes.

## Dependencies And Integration Points

`io.c` integrates directly with UBI, Linux timers and locks, CRC32, UBIFS authentication/HMAC helpers, debugging/recovery hooks, dump helpers, journal heads, and lprops callbacks. Higher layers depend on it for all physical persistence: journal writes use `ubifs_wbuf_write_nolock()`, log writes use `ubifs_write_node()`, GC uses seek/sync/write-buffer functions, scanning and TNC reads use node validation, and error paths rely on `ubifs_ro_mode()`.

## Risks And Edge Cases

The alignment logic is subtle: `wbuf->offs`, `wbuf->size`, `wbuf->avail`, and `wbuf->used` must stay consistent across partial syncs, direct large writes, and end-of-LEB writes. CRC skipping must never apply during mount/recovery or forced checks. `ubifs_read_node_wbuf()` must reconstruct overlap without racing buffer mutation, so it uses `wbuf->lock` only around state/copy and then validates outside. Sequence number exhaustion, buffer allocation failure, stale inode tracking, and sync-callback failures are significant risk points.

## Test Signals

Test signals include UBI error injection for write/change/unmap/map, CRC and bad-magic images, no-data-CRC mounts versus recovery-time checks, writes that cross min/max write-size boundaries, end-of-LEB writes, overlapping reads from a pending write buffer, timer-triggered background sync, inode-specific fsync, authenticated node HMAC preparation, and assertion-enabled runs that exercise alignment invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/ioctl.c

## Purpose

`ioctl.c` implements UBIFS file attribute handling and forwards fscrypt ioctls. It provides EXT2-compatible visible flags for compression, synchronous writes, append-only, immutable, directory sync, and encryption status while translating them to UBIFS private inode flags and VFS inode flags.

## Important APIs, Types, And Functions

`ubifs_set_inode_flags()` propagates `struct ubifs_inode::flags` to `inode->i_flags`. `ubifs_fileattr_get()` and `ubifs_fileattr_set()` are the modern fileattr handlers. `ubifs_ioctl()` handles encryption-policy/key ioctls, and `ubifs_compat_ioctl()` maps compat pointers for the same supported fscrypt commands. Internal converters `ioctl2ubifs()` and `ubifs2ioctl()` map `FS_*_FL` values to `UBIFS_*_FL` values and back. `setflags()` budgets and persists changed inode flags.

## Control Flow

Getting attributes rejects special dentries with `-ENOTTY`, converts stored UBIFS flags to ioctl flags, and fills `struct file_kattr`. Setting attributes rejects special dentries, unsupported fsx-style attributes, and unknown flags; masks the request to settable flags; removes `FS_DIRSYNC_FL` for non-directories; then calls `setflags()`.

`setflags()` reserves inode-dirty budget, takes `ui->ui_mutex`, replaces only UBIFS flags represented by the settable ioctl mask, updates VFS flags, updates ctime, marks the inode dirty synchronously, and unlocks. If the inode was already dirty, it releases the newly reserved budget because a previous dirty budget covers persistence. If the resulting inode is synchronous, it forces `write_inode_now()`.

`ubifs_ioctl()` is intentionally narrow: encryption policy setup first calls `ubifs_enable_encryption(c)`, then delegates to fscrypt. All other supported encryption ioctls are direct fscrypt forwards. Unsupported commands return `-ENOTTY`; compat unsupported commands return `-ENOIOCTLCMD`.

## State And Persistence Behavior

Persistent state is `ubifs_inode(inode)->flags`, plus ctime and dirty inode state. Attribute updates become durable through normal UBIFS inode writeback or immediate `write_inode_now()` for synchronous inodes. Encryption status is gettable through `FS_ENCRYPT_FL` but not settable through generic file attributes; actual encryption policy and key state are controlled by fscrypt ioctls.

## Dependencies And Integration Points

The file depends on VFS inode flags, Linux `fileattr` helpers, mount/idmap interfaces, fscrypt ioctls, UBIFS budgeting (`ubifs_budget_space()`, `ubifs_release_budget()`), UBIFS inode locking, and inode writeback. It is the bridge between userspace flag APIs and UBIFS journaled inode persistence.

## Risks And Edge Cases

The flag masks must remain consistent with the conversion functions. Allowing `FS_ENCRYPT_FL` to be set via fileattr would be wrong, so it is gettable but excluded from `UBIFS_SETTABLE_IOCTL_FLAGS`. Budget release depends on whether the inode was already dirty. Non-directory `FS_DIRSYNC_FL` must be stripped. Special files deliberately do not expose these fileattr operations.

## Test Signals

Test coverage should include `chattr`/`lsattr` style get/set for each supported flag, rejection of unknown or fsx fields, special-file `-ENOTTY`, non-directory dirsync masking, synchronous inode immediate writeback, encryption policy/key ioctl forwarding, compat ioctl pointer handling, and budget accounting when the inode is already dirty versus initially clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/journal.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/journal.c

## Purpose

`journal.c` implements UBIFS journal mutation operations. UBIFS journals updates by writing grouped nodes into multi-headed bud LEBs and then updating the in-memory TNC to point at the newest nodes. The log records bud references, while this file writes inode, data, dent, xent, truncate, rename, orphan-related, and xattr updates into journal heads with ordering that is atomic with respect to unclean reboot recovery.

## Important APIs, Types, And Functions

Public mutation APIs include `ubifs_jnl_update()`, `ubifs_jnl_write_data()`, `ubifs_jnl_write_inode()`, `ubifs_jnl_delete_inode()`, `ubifs_jnl_xrename()`, `ubifs_jnl_rename()`, `ubifs_jnl_truncate()`, `ubifs_jnl_delete_xattr()`, and `ubifs_jnl_change_xattr()`. Reservation helpers are `reserve_space()`, `make_reservation()`, `release_head()`, and `finish_reservation()`. Packing helpers include `pack_inode()`, `get_dent_type()`, `set_dent_cookie()`, and zeroing functions for unused on-flash fields. Authentication grouping is handled by `ubifs_hash_nodes()` and `write_head()`.

The file writes `struct ubifs_ino_node`, `struct ubifs_dent_node`, `struct ubifs_data_node`, and `struct ubifs_trun_node`, uses `union ubifs_key` helpers from `key.h`, and updates TNC entries with node hashes for authenticated or hash-checked lookup paths.

## Control Flow

All journal write operations follow a similar pattern: compute exact aligned write size, allocate a single buffer for the atomic node group, call `make_reservation()` before assigning sequence numbers, pack nodes with group markers, calculate hashes, write the group via `write_head()`, release the journal head mutex, update TNC and dirty/orphan accounting, then call `finish_reservation()` to release `commit_sem`.

`make_reservation()` takes a read lock on `c->commit_sem` and calls `reserve_space()`. If the current head lacks room, `reserve_space()` finds a free-space LEB or runs GC after dropping the write-buffer mutex. `-EAGAIN` triggers commit and retry. After many retries, tasks are serialized through `reserve_space_wq` so concurrent writers stop stealing space from one another. More than 128 commit retries is treated as a budgeting or journal-limit failure.

Directory and xattr updates write dent/xent, child inode, and parent/host inode in one base-head group. Data writes use `DATAHD`, compress and optionally encrypt folio data, append an auth node when authenticated, then add the data key to the TNC. Rename and exchange operations write both new and deletion/whiteout dent nodes plus affected parent and victim inodes. Truncation writes an inode node, a truncation node, and optionally a recompressed/reencrypted final data node, then removes the old data-key range from the TNC.

## State And Persistence Behavior

The journal write is made durable before the in-memory TNC is changed. If the media write succeeds but TNC or accounting updates fail, the filesystem is switched read-only because media and memory state may diverge. Node grouping is used for recovery atomicity: after an unclean reboot, recovery can drop incomplete groups. Synchronous and dirsync inodes force write-buffer synchronization through the `sync` argument to `write_head()`.

Orphan handling is integrated into unlink, rename-over, and delete-inode paths. When the last reference is removed, the inode may be added to the orphan list before the journal group is written and `del_cmtno` records the commit number. `ubifs_jnl_delete_inode()` can skip writing a second deletion inode if no commit occurred between unlink and final iput; otherwise it writes an inode deletion to preserve clean-unmount recovery semantics.

## Dependencies And Integration Points

This file depends on the log layer for adding buds, the GC/lprops allocator for free LEBs, the I/O write-buffer layer, commit orchestration, TNC add/remove/range-remove operations, orphan management, compression, encryption, authentication hashing, fscrypt names, Linux folios, inode locking, and UBIFS budgeting. It is the main integration point between VFS-level filesystem changes and UBIFS's persisted tree representation.

## Risks And Edge Cases

The most sensitive invariants are reservation-before-sequence-number allocation, group ordering, journal-head lock lifetime, and TNC updates after write success. Rename and xattr paths have many optional nodes, aligned offsets, and orphan cleanup branches; an error must delete newly added orphan entries when the group does not complete. Data writes must handle low-memory fallback to `c->write_reserve_buf`, compression expansion, encryption block padding, and authenticated write lengths. Truncation must correctly handle holes, short final blocks, compressed/encrypted recompression, and data-key range deletion.

## Test Signals

Strong signals include fsstress-style create/unlink/rename/xattr/truncate workloads, power-cut recovery around multi-node groups, authenticated and encrypted mounts, low-memory data write fallback, synchronous/dirsync operations, rename with whiteout and cross-directory exchange, orphan cleanup across commits, repeated `-EAGAIN` reservation retries, and debug TNC/lprops checks after journal updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/journal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/key.h -->
# sources/distributed-fs/ceph-client/fs/ubifs/key.h

## Purpose

`key.h` defines UBIFS key helpers. Keys identify inode, data, directory-entry, xattr-entry, and replay-only truncation nodes in the TNC and on flash. The current simple key format uses 64 bits: inode or parent inode number in the high word, then type bits plus block number or hash bits in the low word. The helpers intentionally take `struct ubifs_info *c` so future key formats can be added without changing callers.

## Important APIs, Types, And Functions

Hash helpers are `key_mask_hash()`, `key_r5_hash()`, and `key_test_hash()`. Key constructors include `ino_key_init()`, `ino_key_init_flash()`, `lowest_ino_key()`, `highest_ino_key()`, `dent_key_init()`, `dent_key_init_hash()`, `dent_key_init_flash()`, `lowest_dent_key()`, `xent_key_init()`, `xent_key_init_flash()`, `lowest_xent_key()`, `data_key_init()`, `highest_data_key()`, `trun_key_init()`, and `invalid_key_init()`.

Accessors and transformers include `key_type()`, `key_type_flash()`, `key_inum()`, `key_inum_flash()`, `key_hash()`, `key_hash_flash()`, `key_block()`, `key_block_flash()`, `key_read()`, `key_write()`, `key_write_idx()`, `key_copy()`, `keys_cmp()`, `keys_eq()`, `is_hash_key()`, and `key_max_inode_size()`.

## Control Flow

Directory and xattr entry constructors hash the fscrypt name bytes with `c->key_hash`, assert the hash fits `UBIFS_S_KEY_HASH_MASK`, and combine it with the entry key type. Data keys combine inode number with block number and `UBIFS_DATA_KEY`. Inode keys use the inode number and an inode type discriminator. Lowest/highest helpers generate range bounds for TNC scans and removals, such as all nodes for an inode or all xattr entries under a host inode.

On-flash helpers write little-endian words and zero unused bytes up to `UBIFS_MAX_KEY_LEN`, except `key_write_idx()` leaves only the active key words because index-node storage has its own layout expectations. Flash accessors convert little-endian words back to CPU order. Comparison is lexicographic by the two 32-bit words, matching the simple-key sort order in the TNC.

## State And Persistence Behavior

Keys are persisted in nodes and index branches and are the stable lookup contract for replay, scan, GC, journal updates, and TNC operations. Hash values `0`, `1`, and `2` are reserved for directory offset semantics, so `key_mask_hash()` shifts small hash values upward. `trun_key_init()` is not an on-media key; it exists for replay logic that needs to represent truncation state in key-like form.

## Dependencies And Integration Points

The helpers are used throughout UBIFS: journal packing writes dent/data/ino/xent keys, GC sorts and validates nodes by key type and value, lprops debug scanning calls `ubifs_tnc_has_node()` with keys read from scanned nodes, directory lookup and readdir depend on hashed dent keys, xattr lookup uses xent keys, and truncation/delete paths use range keys for TNC removal.

## Risks And Edge Cases

The key format limits maximum file size via `UBIFS_S_KEY_BLOCK_BITS * UBIFS_BLOCK_SIZE`, so `key_max_inode_size()` must match the active format. Hash collisions are expected for dent/xent keys and are flagged by `is_hash_key()` so name-aware TNC logic can disambiguate. Encrypted names are not C strings, so constructors correctly use `fname_name()` and `fname_len()`. Endianness mistakes or failure to zero unused flash-key bytes would affect mount/replay compatibility.

## Test Signals

Test signals include directory hash collision workloads, encrypted filenames, xattr enumeration/removal ranges, large-file block key limits, TNC key ordering, flash/in-memory key round-trips, and use of lowest/highest range helpers in inode deletion and truncation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/log.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/log.c

## Purpose

`log.c` manages the UBIFS journal log: the fixed flash area that records references to bud LEBs and commit-start nodes. It tracks bud membership, writes reference nodes, controls log head/tail movement during commit, releases old buds only after commit safety is established, and can consolidate a cluttered log after repeated failed commits.

## Important APIs, Types, And Functions

Public APIs are `ubifs_search_bud()`, `ubifs_get_wbuf()`, `ubifs_add_bud()`, `ubifs_add_bud_to_log()`, `ubifs_log_start_commit()`, `ubifs_log_end_commit()`, `ubifs_log_post_commit()`, and `ubifs_consolidate_log()`. Internal helpers include `empty_log_bytes()`, `remove_buds()`, `done_already()`, `destroy_done_tree()`, `add_node()`, and `dbg_check_bud_bytes()`.

The main state is `c->buds` rb-tree, each journal head's `buds_list`, `c->old_buds`, `c->bud_bytes`, `c->cmt_bud_bytes`, `c->lhead_lnum`, `c->lhead_offs`, `c->ltail_lnum`, `c->log_bytes`, `c->min_log_bytes`, and authentication hash state in `c->log_hash` and `jhead->log_hash`.

## Control Flow

`ubifs_add_bud_to_log()` allocates a `struct ubifs_bud` and `UBIFS_REF_NODE`, takes `c->log_mutex`, checks read-only state, ensures enough empty log bytes remain for the next commit, enforces `c->max_bud_bytes`, optionally requests background commit, wraps the log head if needed, unmaps the next log LEB at offset zero, maps empty target buds before referencing them, writes the ref node, updates authentication hash state, advances `lhead_offs`, and adds the bud to both rb-tree and journal-head list.

Commit start writes a `UBIFS_CS_NODE` plus reference nodes for currently open journal heads into a fresh log LEB, resets the log hash, pads to `min_io_size`, advances the log head, and calls `remove_buds()`. `remove_buds()` preserves buds still pointed to by active write buffers by moving their start offset forward, while closed buds are moved to `old_buds` so they cannot be garbage-collected until recovery no longer needs them. Commit end moves `ltail_lnum`, restores `min_log_bytes`, subtracts committed bud bytes, validates accounting, and writes the master node. Post-commit returns old buds to lprops and unmaps old log LEBs.

`ubifs_consolidate_log()` is a recovery-oriented repair path. It scans from tail to head, copies the first commit-start node and only the newest unique ref nodes into compacted log LEBs, pads and changes LEBs as needed, unmaps the remaining old log area, and updates `lhead_lnum`/`lhead_offs`.

## State And Persistence Behavior

The log is the persistent description of journal buds needed for replay. Ref nodes are written before a bud becomes visible in in-memory bud structures. Empty target buds are explicitly mapped before being referenced to avoid recovery seeing stale garbage from an unmapped but not physically erased LEB. Old log LEBs and old buds are not unmapped/returned until after commit completes, preserving recovery from interrupted commits.

## Dependencies And Integration Points

`log.c` integrates with journal reservation (`ubifs_add_bud_to_log()` is called when a journal head switches LEBs), commit logic, master-node persistence, UBI wrappers from `io.c`, scanning for consolidation, lprops return paths, background commit requests, authentication hash helpers, rb-trees, and per-journal-head write buffers.

## Risks And Edge Cases

Important risks are off-by-one log head/tail wraparound, incorrect `bud_bytes` accounting, referencing an unmapped empty bud, reclaiming old buds before commit is fully safe, and failing to preserve open half-indexed buds at commit. Consolidation must avoid duplicate stale refs and must not fill the entire log; it returns `-EINVAL` if compaction still leaves the head at the previous head LEB. Authentication hash state must be copied to each journal head after ref writes and commit-start refs.

## Test Signals

Test signals include journal-head switching, log wraparound, max-bud-byte commit triggers, background commit threshold behavior, commit interruption and recovery, half-indexed bud preservation, repeated failed commits followed by log consolidation, authenticated journal replay, and debug `bud_bytes` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lprops.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/lprops.c

## Purpose

`lprops.c` manages UBIFS logical eraseblock properties and their fast lookup categories. Lprops record per-LEB free space, dirty space, flags such as index/taken/category, and aggregate space statistics. This file keeps category heaps/lists consistent so higher layers can quickly find empty LEBs, freeable LEBs, LEBs with free space, dirty data LEBs for GC, and dirty/freeable index LEBs.

## Important APIs, Types, And Functions

Category maintenance APIs include `ubifs_add_to_cat()`, `ubifs_replace_cat()`, `ubifs_ensure_cat()`, `ubifs_categorize_lprops()`, `ubifs_change_lp()`, `ubifs_change_one_lp()`, `ubifs_update_one_lp()`, `ubifs_read_one_lp()`, and `ubifs_get_lp_stats()`. Fast lookup APIs include `ubifs_fast_find_free()`, `ubifs_fast_find_empty()`, `ubifs_fast_find_freeable()`, and `ubifs_fast_find_frdi_idx()`. Debug validators include `dbg_check_cats()`, `dbg_check_heap()`, and `dbg_check_lprops()`.

Internal heap functions are `get_heap_comp_val()`, `move_up_lpt_heap()`, `adjust_lpt_heap()`, `add_to_lpt_heap()`, `remove_from_lpt_heap()`, and `lpt_heap_replace()`. They operate on `struct ubifs_lpt_heap` arrays and `struct ubifs_lprops::hpos`.

## Control Flow

`ubifs_categorize_lprops()` is the category policy. Taken LEBs are uncategorized. Fully free LEBs go to `LPROPS_EMPTY`. LEBs whose free plus dirty equals the full LEB size go to `LPROPS_FREEABLE` for data or `LPROPS_FRDI_IDX` for index. Index LEBs with enough reclaimable space go to `LPROPS_DIRTY_IDX`. Data LEBs with dirty space above the dead watermark and greater than free space go to `LPROPS_DIRTY`; otherwise LEBs with free space go to `LPROPS_FREE`; the rest are uncategorized.

`ubifs_change_lp()` is the central mutator. It ensures the lprops pnode is dirty/COW-safe, updates aggregate stats under `space_lock`, aligns free/dirty values to 8 bytes, adjusts empty/index/taken counters, removes and recalculates dead/dark/used accounting for non-index LEBs, recategorizes the LEB, updates `c->idx_gc_cnt`, and returns the possibly copied lprops pointer. Wrapper functions acquire/release lprops locking and look up by LEB number.

Heaps are bounded. If a category heap is full, `add_to_lpt_heap()` may replace a weaker bottom-half candidate; otherwise the new LEB becomes uncategorized. `ubifs_ensure_cat()` gives uncategorized LEBs another chance to enter a useful category when callers encounter them. Fast find helpers assume `c->lp_mutex` is held and return the top/list-head lprops for their category without scanning.

## State And Persistence Behavior

Lprops are persisted through the LPT, but this file manages the in-memory categorized view and aggregate `c->lst` counters used by budgeting, GC, and free-space allocation. Copy-on-write LPT behavior means a lprops pointer can change during `ubifs_change_lp()`, especially around commit. Dark and dead space accounting models unusable tail space so budgeting does not overpromise writes that may not fit future nodes.

## Dependencies And Integration Points

The file is used by journal reservation to find free space, GC to choose dirty/freeable LEBs, commit to update index/data LEB status, budgeting to read aggregate stats, and debug validation to compare lprops against actual media and TNC reachability. It depends on LPT lookup/scan functions, UBIFS scan, TNC node-existence checks, write-buffer sync during debug media scans, and global locks `lp_mutex` and `space_lock`.

## Risks And Edge Cases

Category and aggregate counter drift is the primary risk. A LEB must not appear in multiple categories, heaps must preserve `hpos`, and `freeable_cnt`, `idx_gc_cnt`, `empty_lebs`, `idx_lebs`, and total free/dirty/used/dead/dark counters must match actual lprops. Unclean unmounts complicate debug scans because empty/freeable LEBs may contain stale garbage and index LEB free space may differ due to in-the-gaps commit behavior. Heap overflow intentionally degrades to uncategorized, so callers must handle misses from fast helpers.

## Test Signals

Good signals include lprops mutation under GC, commit, journal allocation, and index GC; category heap overflow; transitions among empty/free/freeable/dirty/index/taken states; debug `dbg_check_lprops()` after syncing write buffers; power-cut recovery with stale empty/freeable LEB content; and budget/free-space tests that compare aggregate counters to scanned media.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lprops.c -->
