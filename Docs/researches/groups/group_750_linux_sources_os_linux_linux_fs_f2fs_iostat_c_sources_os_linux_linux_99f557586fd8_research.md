# Group Research: group_750_linux_sources_os_linux_linux_fs_f2fs_iostat_c_sources_os_linux_linux_99f557586fd8

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/iostat.c -->
# File Research: sources/os/linux/linux/fs/f2fs/iostat.c

Implements F2FS runtime I/O statistics and latency tracing when `CONFIG_F2FS_IOSTAT` is enabled.

Key responsibilities:
- Exposes `iostat_info_seq_show()` for debugfs/seq output of accumulated write, read, discard, flush, zone reset, and read-folio-order counters.
- Maintains byte/count totals in `sbi->iostat_bytes[]`, `sbi->iostat_count[]`, and `sbi->iostat_read_folio_count[]`.
- Periodically emits `trace_f2fs_iostat()` and `trace_f2fs_iostat_latency()` based on `sbi->iostat_period_ms`.
- Tracks per-bio latency through `bio_iostat_ctx`, recording read, sync write, and async write latency by F2FS page type.
- Allocates and destroys global mempool/slab resources for bio iostat contexts.
- Initializes and tears down per-superblock iostat state.

Important functions:
- `iostat_info_seq_show()`: prints current cumulative counters and averages.
- `f2fs_record_iostat()`: computes periodic deltas and emits tracepoints.
- `f2fs_reset_iostat()`: clears byte, count, read-folio, and latency state.
- `f2fs_update_iostat()`: records I/O bytes and derived aggregate/compressed-data counters.
- `f2fs_update_read_folio_count()`: records folio read order distribution.
- `iostat_alloc_and_bind_ctx()` / `iostat_update_and_unbind_ctx()`: wrap `bio->bi_private` with latency context while preserving read post-processing state.
- `f2fs_init_iostat_processing()` / `f2fs_destroy_iostat_processing()`: module-level cache and mempool lifecycle.
- `f2fs_init_iostat()` / `f2fs_destroy_iostat()`: per-mount lifecycle.

Concurrency and locking:
- Counter arrays use `sbi->iostat_lock`.
- Latency arrays use `sbi->iostat_lat_lock`.
- Periodic tracing double-checks `iostat_next_period` under lock to avoid duplicate trace emission.

Notable behavior:
- `APP_WRITE_IO` and `APP_READ_IO` are aggregate counters updated from buffered/direct app I/O.
- Compression builds add parallel compressed-data counters when the inode is compressed.
- `META_FLUSH` latency is folded into `META`.
- Invalid page types during latency accounting warn and skip the sample.

Dependencies:
- Uses F2FS superblock state from `f2fs.h`.
- Uses public declarations and context structs from `iostat.h`.
- Emits F2FS tracepoints from `<trace/events/f2fs.h>`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/iostat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/iostat.h -->
# File Research: sources/os/linux/linux/fs/f2fs/iostat.h

Header for F2FS iostat support.

Key definitions:
- `enum iostat_lat_type`: latency buckets for `READ_IO`, `WRITE_SYNC_IO`, and `WRITE_ASYNC_IO`.
- `NUM_PREALLOC_IOSTAT_CTXS`: fixed mempool size for bio context wrappers.
- `DEFAULT_IOSTAT_PERIOD_MS`, `MIN_IOSTAT_PERIOD_MS`, `MAX_IOSTAT_PERIOD_MS`: trace period bounds.
- `struct iostat_lat_info`: sum, peak, and count arrays indexed by latency type and F2FS page type.
- `struct bio_iostat_ctx`: per-bio wrapper storing `sbi`, submit timestamp, page type, and optional post-read context.

Public API when enabled:
- Debug/seq: `iostat_info_seq_show()`.
- Counter control: `f2fs_reset_iostat()`, `f2fs_update_iostat()`, `f2fs_update_read_folio_count()`.
- Bio context control: `iostat_update_submit_ctx()`, `get_post_read_ctx()`, `iostat_update_and_unbind_ctx()`, `iostat_alloc_and_bind_ctx()`.
- Lifecycle: `f2fs_init_iostat_processing()`, `f2fs_destroy_iostat_processing()`, `f2fs_init_iostat()`, `f2fs_destroy_iostat()`.

Disabled configuration behavior:
- Under `#else`, all update/lifecycle functions become no-ops or success stubs.
- `get_post_read_ctx()` returns `bio->bi_private` directly when iostat wrapping is disabled, preserving normal read-post-processing behavior.

Notable contract:
- With iostat enabled, callers must treat `bio->bi_private` as a `bio_iostat_ctx` until `iostat_update_and_unbind_ctx()` restores the original private data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/iostat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/namei.c -->
# File Research: sources/os/linux/linux/fs/f2fs/namei.c

Implements F2FS VFS name/inode operations: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, tmpfile, rename, encrypted symlink lookup, and inode operation tables.

Key responsibilities:
- Maintains hot/cold extension lists and applies file-temperature hints.
- Applies compression inheritance and extension-based compression policy to new inodes.
- Allocates and initializes new inodes with NIDs, fscrypt setup, quota setup, extra attributes, inline xattrs, inline dentries, inline data, project quota inheritance, inode flags, timestamps, generation, and extent tree setup.
- Implements all directory entry mutations under F2FS operation locks.
- Handles orphan inode accounting for unlink, tmpfile, and rename overwrite cases.
- Supports casefolding, fscrypt lookup, encrypted symlink targets, and ACL/xattr operation registration.

Important functions:
- `is_extension_exist()`: shared extension matcher for hot/cold and compression extension rules, including optional temporary suffix handling.
- `f2fs_update_extension_list()`: adds/removes hot or cold extensions inside the raw superblock extension list.
- `set_compress_new_inode()`: applies compression or no-compression behavior based on mount options, extension lists, and parent directory flags.
- `set_file_temperature()`: marks files hot or cold based on configured extensions.
- `f2fs_new_inode()`: central inode creation path; allocates a NID, initializes VFS and F2FS inode metadata, prepares encryption/quota state, and sets inline/compression flags.
- `f2fs_create()`, `f2fs_link()`, `f2fs_unlink()`, `f2fs_symlink()`, `f2fs_mkdir()`, `f2fs_rmdir()`, `f2fs_mknod()`: standard VFS operations mapped to F2FS metadata updates.
- `__f2fs_tmpfile()`: common tmpfile and whiteout creation path.
- `f2fs_rename()` and `f2fs_cross_rename()`: handle normal rename, overwrite, whiteout, and exchange rename cases.
- `f2fs_rename2()`: validates flags, performs fscrypt rename preparation, and dispatches to normal or exchange rename.
- `f2fs_encrypted_get_link()` / `f2fs_encrypted_symlink_getattr()`: encrypted symlink support.

Operation tables:
- `f2fs_dir_inode_operations`: directory operations, ACLs, xattrs, fiemap, fileattr get/set.
- `f2fs_symlink_inode_operations`: plain symlink operations.
- `f2fs_encrypted_symlink_inode_operations`: encrypted symlink operations.
- `f2fs_special_inode_operations`: special-file operations.

Consistency and recovery behavior:
- Creation/link/rename paths check checkpoint errors and checkpoint readiness before metadata mutation.
- Directory sync parents trigger `f2fs_sync_fs()`.
- Lookup and unlink detect zero-link or malformed directory inodes, mark `SBI_NEED_FSCK`, and return corruption errors.
- Rename updates parent inode numbers for moved directories so fsck can validate parent links.
- Strict fsync mode tracks transformed directory inodes with `TRANS_DIR_INO`.

Dependencies:
- Uses directory helpers from F2FS core, node allocation from `node.h`, segment/orphan/checkpoint handling from `segment.h`, xattr/ACL helpers, quota, fscrypt, casefolding, and F2FS tracepoints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/node.c -->
# File Research: sources/os/linux/linux/fs/f2fs/node.c

Implements F2FS node management: NAT cache, free-NID allocation, node page lookup/read/writeback/truncation, fsync node tracking, roll-forward helper routines, NAT flushing, and node manager lifecycle.

Major areas:
- Memory pressure policy for free NIDs, NAT cache entries, dirty dentries, inode entries, extent caches, discard cache, and compressed pages.
- NAT cache management using radix trees plus clean/dirty lists.
- Free NID discovery and allocation from NAT pages, NAT bitmaps, free-NID bitmaps, and current segment NAT journals.
- Data-to-node path traversal for direct, indirect, and double-indirect node trees.
- Node page allocation, read, writeback, readahead, dirty accounting, and truncation.
- Fsync node ordering and writeback wait support for roll-forward recovery.
- Checkpoint-time NAT entry flushing to either current segment journal or NAT blocks.
- Mount/unmount lifecycle for node manager state and slab caches.

Important NAT/free-NID functions:
- `f2fs_check_nid_range()`: validates NID bounds and marks filesystem for fsck on corruption.
- `f2fs_get_node_info()`: resolves a NID through NAT cache, current journal, or NAT block and validates block addresses.
- `set_node_addr()`: updates NAT state, dirty set membership, checkpoint/fsync flags, and node version on deletion.
- `f2fs_try_to_free_nats()`: shrinks reclaimable clean NAT cache entries.
- `f2fs_build_free_nids()`: scans NAT state to populate the free-NID cache.
- `f2fs_alloc_nid()`, `f2fs_alloc_nid_done()`, `f2fs_alloc_nid_failed()`: allocate, commit, or roll back NID reservations.
- `f2fs_try_to_free_nids()`: shrinks excess cached free NIDs.
- `f2fs_flush_nat_entries()`: checkpoint path for dirty NAT persistence.

Important node-tree functions:
- `get_node_path()`: maps file block index to inode/direct/indirect node offsets.
- `f2fs_get_dnode_of_data()`: walks or allocates the node path for a data block, returning dnode state and current data block address.
- `f2fs_get_next_page_offset()`: computes skip-ahead offsets when walking sparse node trees.
- `truncate_node()`, `truncate_dnode()`, `truncate_nodes()`, `truncate_partial_nodes()`: remove node pages and underlying data references.
- `f2fs_truncate_inode_blocks()`: truncates node tree ranges from a file offset.
- `f2fs_truncate_xattr_node()` and `f2fs_remove_inode_page()`: remove xattr and inode node pages.

Node folio I/O:
- `f2fs_new_node_folio()` / `f2fs_new_inode_folio()`: create new node pages, update NAT to `NEW_ADDR`, fill node footer, and mark dirty.
- `read_node_folio()`: resolves NAT address and submits node read bio.
- `f2fs_ra_node_page()` and `f2fs_ra_node_pages()`: node readahead helpers.
- `f2fs_sanity_check_node_footer()`: validates nid/type/footer consistency and marks corruption.
- `f2fs_get_node_folio()`, `f2fs_get_inode_folio()`, `f2fs_get_xnode_folio()`: typed node lookup wrappers.
- `__write_node_folio()`: core node writeback path, including fsync/dentry marks, NAT address update, preflush/FUA handling, dirty count decrement, and iostat type propagation.
- `f2fs_sync_node_pages()` and `f2fs_write_node_pages()`: address-space writeback implementation.
- `f2fs_node_aops`: node mapping operations.

Fsync/recovery helpers:
- `f2fs_init_fsync_node_info()`, `f2fs_add_fsync_node_entry()`, `f2fs_del_fsync_node_entry()`, `f2fs_wait_on_node_pages_writeback()`: track fsync node write order.
- `f2fs_need_dentry_mark()`, `f2fs_is_checkpointed_node()`, `f2fs_need_inode_block_update()`: decide roll-forward marks and inode block update needs.
- `f2fs_recover_inline_xattr()`, `f2fs_recover_xattr_data()`, `f2fs_recover_inode_page()`: used by `recovery.c` to rebuild inode/xattr node state.
- `f2fs_restore_node_summary()`: reconstructs node summaries by scanning node segment blocks.

Checkpoint/NAT flushing:
- Dirty NAT entries are grouped by NAT block in `nat_entry_set`.
- `__flush_nat_entry_set()` writes dirty NATs either to the hot-data journal when space allows or to the alternate NAT block copy.
- NAT bits maintain empty/full NAT block acceleration when enabled.
- Journal NAT entries are merged back into dirty NAT sets when checkpoint needs full NAT-bit consistency.

Lifecycle:
- `f2fs_build_node_manager()` allocates `f2fs_nm_info`, initializes NAT/free-NID structures, loads NAT bits, and builds initial free NIDs.
- `f2fs_destroy_node_manager()` frees free-NID caches, NAT caches, NAT sets, bitmaps, NAT bits, and node manager state.
- `f2fs_create_node_manager_caches()` / `f2fs_destroy_node_manager_caches()` manage slab caches for NAT entries, free NIDs, NAT sets, and fsync node entries.

Error handling:
- Many paths mark `SBI_NEED_FSCK` and call `f2fs_handle_error()` for inconsistent NAT entries, invalid node references, bad block addresses, or footer mismatches.
- Writeback avoids unsafe progress during checkpoint errors and power-on recovery.
- Allocation paths include fault-injection hooks and retry loops for memory pressure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/node.h -->
# File Research: sources/os/linux/linux/fs/f2fs/node.h

Header for F2FS node manager structures, constants, NAT address helpers, node footer helpers, node tree offset logic, and node mark helpers.

Key constants:
- NAT addressing: `START_NID()`, `NAT_BLOCK_OFFSET()`.
- Free-NID scan/cache limits: `FREE_NID_PAGES`, `MAX_FREE_NIDS`, `SHRINK_NID_BATCH_SIZE`, `DEF_RA_NID_PAGES`.
- Node readahead: `MAX_RA_NODE`.
- Memory/cache thresholds: `DEF_RAM_THRESHOLD`, `DEF_DIRTY_NAT_RATIO_THRESHOLD`, `DEF_NAT_CACHE_THRESHOLD`.
- Roll-forward control: `DEF_RF_NODE_BLOCKS`.
- Lookup vector size: `NAT_VEC_SIZE`.
- `LOCKED_PAGE` read-node sentinel and `FILE_NOT_ALIGNED`.

Core structures:
- `struct node_info`: in-memory NAT information for one NID: nid, owner ino, block address, version, and flags.
- `struct nat_entry`: cached NAT entry with list linkage.
- `struct nat_entry_set`: group of dirty NAT entries belonging to one NAT block.
- `struct free_nid`: cached free or preallocated NID entry.

NAT helpers:
- Accessors for nid, block address, owner ino, and version.
- `nat_reset_flag()` resets checkpoint/fsync-related NAT flags after persistence.
- `node_info_from_raw_nat()` and `raw_nat_from_node_info()` convert between on-disk NAT entries and in-memory `node_info`.
- `excess_dirty_nats()` and `excess_cached_nats()` implement threshold checks.

NAT block addressing:
- `get_nat_bitmap()` copies the current NAT version bitmap and optionally verifies its mirror.
- `current_nat_addr()` maps a start NID to the active NAT block copy.
- `next_nat_addr()` returns the alternate NAT block copy.
- `set_to_next_nat()` toggles the NAT version bitmap after NAT block copy-on-write.

Node footer helpers:
- `ino_of_node()`, `nid_of_node()`, `ofs_of_node()`, `cpver_of_node()`, `next_blkaddr_of_node()`.
- `fill_node_footer()` initializes or updates node footer nid/ino/offset while preserving mark bits when requested.
- `copy_node_footer()` copies footer state between node pages.
- `fill_node_footer_blkaddr()` records checkpoint version/CRC and next block address for roll-forward chaining.
- `is_recoverable_dnode()` checks whether a node page belongs to the current recoverable checkpoint version.

Node tree helpers:
- `IS_DNODE()` classifies data nodes versus indirect nodes using F2FS node offset layout.
- `set_nid()` and `get_nid()` read/write child NIDs in inode or indirect node blocks.

Cold/fsync/dentry marks:
- `is_cold_node()`, `is_fsync_dnode()`, `is_dent_dnode()` inspect footer mark bits.
- `set_cold_node()`, `set_dentry_mark()`, `set_fsync_mark()` update footer marks and refresh inode checksum under check-FS builds.

Memory type enum:
- `enum mem_type` names memory-pressure accounting categories shared with `node.c`, including free NIDs, NAT entries, dirty dentries, inode entries, extent caches, discard cache, compressed pages, and base checks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/recovery.c -->
# File Research: sources/os/linux/linux/fs/f2fs/recovery.c

Implements F2FS roll-forward recovery for fsynced data after an unclean shutdown.

Recovery model:
- The file documents eight fsync/dentry-mark scenarios around checkpoint boundaries.
- Recovery scans warm-node segment chains starting at the current warm-node curseg next block.
- Recoverable nodes are identified by node footer checkpoint version/CRC via `is_recoverable_dnode()`.
- Fsync-marked dnodes identify inodes requiring replay.
- Dentry-marked inode nodes provide enough parent/name information to restore missing directory entries.

Key responsibilities:
- Determine whether there is space and roll-forward budget for recovery.
- Discover fsynced inode chains.
- Recover missing inode pages for new fsynced inodes.
- Restore inode metadata, dentries, inline xattrs, xattr nodes, inline data, and data block mappings.
- Avoid duplicate ownership of recovered data blocks by checking previous node references.
- Allocate new segments and write a checkpoint after successful replay.
- Provide lifecycle cache for `fsync_inode_entry`.

Important functions:
- `f2fs_space_for_roll_forward()`: checks block and optional rf-node limits.
- `add_fsync_inode()` / `del_fsync_inode()` / `destroy_fsync_dnodes()`: manage recovery inode list entries.
- `init_recovered_filename()`: reconstructs filename/hash state for recovered dentries, including encrypted+casefolded names.
- `recover_dentry()`: restores a dentry in the recorded parent directory, deleting conflicting entries when needed.
- `recover_quota_data()`: transfers UID/GID quota ownership changes before metadata replay.
- `recover_inode()`: restores mode, owner, size, timestamps, advise flags, F2FS flags, GC failures, inline flags, and project quota.
- `sanity_check_node_chain()`: uses Floyd-style cycle detection to prevent looping recovery node chains.
- `find_fsync_dnodes()`: scans recoverable node chain, builds the fsynced inode list, and optionally performs check-only detection.
- `check_index_in_prev_nodes()`: finds and truncates older references to a destination block before replaying a recovered mapping.
- `do_recover_data()`: recovers xattr/inline/data mappings for one recoverable node page.
- `recover_data()`: scans the recoverable node chain and applies inode, dentry, and data recovery for listed fsynced inodes.
- `f2fs_recover_fsync_data()`: top-level recovery flow under `cp_global_sem`.

Top-level recovery flow:
1. Take `cp_global_sem` to prevent checkpoint during recovery.
2. Scan for fsync dnodes with `find_fsync_dnodes()`.
3. In check-only mode, return whether recovery is needed.
4. Replay data and metadata with `recover_data()`.
5. Drop recovery meta pages and, on error, truncate node/meta mappings.
6. Check and fix zoned-device write pointer consistency.
7. Clear `SBI_POR_DOING` on success.
8. Drop directory inode references.
9. If replay happened, set `SBI_IS_RECOVERED` and write a recovery checkpoint.
10. Restore the original superblock read-only flag.

Consistency handling:
- Invalid block addresses, inconsistent summaries, looped node chains, and footer inconsistencies abort recovery.
- Dentry recovery handles encrypted filenames by logging `<encrypted>` instead of raw names.
- `check_index_in_prev_nodes()` uses segment summaries to locate previous owners of a block and truncate stale references.
- New inode recovery removes the recovered inode number from the free-NID cache to avoid reuse.

Dependencies:
- Depends heavily on node helpers from `node.h`/`node.c`, segment summaries and replacement helpers from `segment.h`, quota APIs, fscrypt/casefold directory helpers, and checkpoint/write-pointer logic from broader F2FS.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/recovery.c -->