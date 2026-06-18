# Group Research: group_982_linux_stable_sources_os_linux_linux_stable_fs_ext4_fast_commit_c_sou_2d673081e8f8

Scope confirmed against `Docs/research_subset_a.md`: all listed files are under `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fast_commit.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/fast_commit.c

This file implements ext4 fast commit tracking, commit emission, cleanup, replay scanning, and replay application. Fast commits store fine-grained filesystem deltas in journal fast-commit space as TLV records and fall back to a full JBD2 commit when an operation is unsupported.

Major responsibilities:
- Track fast-commit-eligible operations:
  - Directory updates via `ext4_fc_track_create()`, `ext4_fc_track_link()`, and `ext4_fc_track_unlink()`.
  - Inode metadata updates via `ext4_fc_track_inode()`.
  - Logical data range changes via `ext4_fc_track_range()`.
- Maintain fast commit queues:
  - `s_fc_q[FC_Q_MAIN/STAGING]` for inodes.
  - `s_fc_dentry_q[FC_Q_MAIN/STAGING]` for directory entry operations.
  - Per-inode `i_fc_list`, `i_fc_dilist`, `i_fc_lblk_start`, and `i_fc_lblk_len`.
- Mark unsupported transactions ineligible with `ext4_fc_mark_ineligible()`, recording the latest ineligible TID and per-reason stats.
- Emit fast commit blocks:
  - `ext4_fc_reserve_space()` allocates TLV space, inserts padding, advances `s_fc_bytes`, and gets fast-commit buffers from JBD2.
  - `ext4_fc_add_tlv()` and `ext4_fc_add_dentry_tlv()` serialize records.
  - `ext4_fc_write_inode()` serializes raw inode state.
  - `ext4_fc_write_inode_data()` serializes added or deleted logical ranges.
  - `ext4_fc_write_tail()` terminates a commit with TID and CRC.
- Execute the commit pipeline:
  - `ext4_fc_commit()` is the main entry point.
  - `ext4_fc_perform_commit()` flushes data, marks inodes committing, writes HEAD/dentry/range/inode/TAIL tags, and submits buffers.
  - `ext4_fc_cleanup()` releases buffers, clears committing state, frees dentry-update records, splices staging queues, clears ineligibility after full commit, and resets fast-commit byte usage after full commits.
- Replay fast commit records during journal recovery:
  - `ext4_fc_replay_scan()` validates TLVs, checks lengths, validates CRC/tail TID, counts replayable tags, and records physical regions that must be excluded from replay allocation.
  - `ext4_fc_replay()` dispatches replay by tag.
  - Replay handlers cover unlink, link, create, raw inode restoration, add-range, and delete-range.
  - `ext4_fc_set_bitmaps_and_counters()` fixes allocation bitmaps for replay-modified inodes.
  - `ext4_fc_replay_cleanup()` releases replay arrays and clears replay mount state.
- Export support hooks:
  - `ext4_fc_init_inode()`, `ext4_fc_del()`, `ext4_fc_init()`, `ext4_fc_info_show()`, `ext4_fc_record_regions()`, `ext4_fc_replay_check_excluded()`, slab init/destroy helpers.

Important design points:
- Fast commits encode outcomes, not procedures, to make replay idempotent. Rename-like sequences are represented as link/unlink/inode-state outcomes.
- A commit is atomic only if a valid tail record with matching TID and CRC is found.
- HEAD is written only at the beginning of a fast-commit area for a transaction.
- TAIL consumes the rest of its block so the next fast commit starts on a fresh block.
- Dentry create records are special: the inode and inode data are written before the create dentry TLV so replay can instantiate the inode then link it.
- Encrypted filenames, journal-data inodes, inline-data range changes, xattr-like cases, and other unsupported cases force full commits through ineligibility.
- The code uses `s_fc_lock` for global queues and `i_fc_lock` for per-inode fast-commit fields. If both are needed, global lock comes first.
- `EXT4_STATE_FC_FLUSHING_DATA` prevents inodes from being evicted while commit-time data flush is in progress.
- `EXT4_STATE_FC_COMMITTING` makes modifiers wait until the inode’s fast commit completes.
- Replay uses arrays of modified inodes and reserved allocation regions because normal allocation decisions during replay may differ from pre-crash allocation.

Key invariants:
- Fast commit tracking is skipped when fast commit is disabled or replay is active.
- Full commit clears the fast-commit area state; fast commit cleanup only consumes committed queue entries.
- `ext4_fc_track_inode()` must not sleep while holding `i_data_sem`.
- TLV lengths are validated before replay dispatch.
- Replay add-range/delete-range must update block allocation accounting and later reconcile bitmaps from modified inode mappings.
- Fast commit recovery intentionally ignores some missing inodes/directories as already-applied or obsolete state, preserving replay idempotence.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fast_commit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fast_commit.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/fast_commit.h

This header defines the ext4 fast commit on-disk TLV format, status codes, ineligibility reason IDs, in-memory tracking records, replay state, and tag-name helper.

Major contents:
- On-disk tags:
  - `EXT4_FC_TAG_ADD_RANGE`
  - `EXT4_FC_TAG_DEL_RANGE`
  - `EXT4_FC_TAG_CREAT`
  - `EXT4_FC_TAG_LINK`
  - `EXT4_FC_TAG_UNLINK`
  - `EXT4_FC_TAG_INODE`
  - `EXT4_FC_TAG_PAD`
  - `EXT4_FC_TAG_TAIL`
  - `EXT4_FC_TAG_HEAD`
- `EXT4_FC_SUPPORTED_FEATURES` is currently `0x0`.
- On-disk structures:
  - `struct ext4_fc_tl`: common tag and length header.
  - `struct ext4_fc_head`: feature bits and transaction ID.
  - `struct ext4_fc_add_range`: inode plus serialized extent bytes.
  - `struct ext4_fc_del_range`: inode, logical block, and length.
  - `struct ext4_fc_dentry_info`: parent inode, target inode, and flexible filename.
  - `struct ext4_fc_inode`: inode number plus flexible raw inode payload.
  - `struct ext4_fc_tail`: transaction ID and CRC.
- Kernel-only structures:
  - `struct ext4_fc_dentry_update`: queued in-memory dentry operation and name snapshot.
  - `struct ext4_fc_stats`: commit counters, block counters, average commit time, and ineligibility reason counters.
  - `struct ext4_fc_alloc_region`: physical block regions reserved during replay.
  - `struct ext4_fc_replay_state`: replay counters, CRC state, region array, and modified-inode array.

Important design points:
- The file comments state this header must remain byte-identical with the e2fsprogs copy.
- TLV structures are little-endian and intentionally compact for journal storage.
- `EXT4_FC_REPLAY_REALLOC_INCREMENT` grows replay arrays in small batches.
- `tag2str()` maps fast-commit tag values to trace/debug names.

Key invariants:
- On-disk format changes must be synchronized with userspace tooling.
- Flexible-array TLV payload lengths must be validated by replay before interpretation.
- `EXT4_FC_REASON_MAX` bounds both stats arrays and reason-name tables.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fast_commit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/file.c

This file implements regular-file VFS operations for ext4: read, write, splice read, mmap preparation, open/release, llseek, and the exported file/inode operation tables.

Major responsibilities:
- Read path:
  - `ext4_file_read_iter()` rejects forced shutdown, skips zero-length atime updates, chooses DAX, direct I/O, or buffered read.
  - `ext4_dio_read_iter()` uses iomap direct I/O under shared inode lock and falls back to buffered I/O when ext4 features do not support DIO.
  - `ext4_dax_read_iter()` uses DAX iomap when DAX remains valid under inode lock.
  - `ext4_file_splice_read()` checks forced shutdown then delegates to `filemap_splice_read()`.
- Write path:
  - `ext4_file_write_iter()` checks emergency state, handles DAX, validates atomic write size, and selects direct or buffered write.
  - `ext4_buffered_write_iter()` performs generic buffered writes under exclusive inode lock and syncs as needed.
  - `ext4_dio_write_iter()` manages direct I/O, fallback to buffered completion, orphan handling for extension, lock sharing, and page-cache invalidation after fallback.
  - `ext4_dax_write_iter()` handles DAX writes, extension orphaning, inode size update, and sync.
- Direct I/O policy:
  - `ext4_should_use_dio()` implements ext4’s historical behavior: feature-unsupported DIO falls back to buffered I/O, but misaligned DIO for otherwise DIO-capable files is left to DIO to reject.
  - `ext4_dio_write_checks()` decides shared vs exclusive inode lock, handles NOWAIT, extending writes, unaligned writes, overwrite checks, security-time updates, DIO drain, and `IOMAP_DIO_FORCE_WAIT`.
  - `ext4_dio_write_end_io()` converts unwritten extents after DIO, including the atomic-write conversion path, and extends inode size if needed.
- Extension cleanup:
  - `ext4_handle_inode_extension()` updates inode size and removes orphan tracking when the full intended write completed.
  - `ext4_inode_extension_cleanup()` truncates failed extension writes or removes stale orphan tracking after races.
- mmap:
  - DAX faults use `ext4_dax_huge_fault()` / `ext4_dax_fault()` with journal handling for shared write faults, invalidate locking, ENOSPC retry, and synchronous fault completion.
  - `ext4_file_mmap_prepare()` checks shutdown/emergency state, validates synchronous mapping support, installs DAX or buffered vm ops, and enables huge pages for DAX.
- Open/release:
  - `ext4_file_open()` samples last mounted path, runs fscrypt/fsverity open checks, attaches a JBD2 inode for writers, enables atomic-write capability when supported, and advertises NOWAIT/ODIRECT.
  - `ext4_release_file()` flushes delayed allocation on close, discards preallocations for the last writer, and frees htree directory private state.
- Seeking:
  - `ext4_llseek()` uses iomap SEEK_DATA/SEEK_HOLE reporting and selects max file size based on extents vs indirect mapping.
- Operation tables:
  - `ext4_file_operations` wires llseek, read/write, iopoll, ioctls, mmap, open/release, fsync, splice, fallocate, lease, and feature flags.
  - `ext4_file_inode_operations` wires setattr/getattr, xattrs, ACLs, fiemap, and file attributes.

Important design points:
- Extending direct/DAX writes use orphan tracking so crashes do not expose partially extended files.
- Unaligned direct writes to unwritten or non-overwrite regions require exclusive locking and DIO draining to avoid partial-block zeroing races.
- Direct I/O fallback to buffered I/O flushes and invalidates the affected page-cache range to preserve DIO semantics.
- Atomic writes are DIO-only and constrained by superblock atomic write unit bounds.
- DAX mmap write faults journal metadata only for shared writable faults, not private COW faults.

Key invariants:
- Forced shutdown returns `-EIO`; emergency state blocks writes.
- Buffered writes do not support `IOCB_NOWAIT`.
- DIO writes must clear `EXT4_STATE_MAY_INLINE_DATA` before allocating blocks.
- Non-extent files are capped at `s_bitmap_maxbytes`.
- DAX vm ops are installed only when the mapping and dax device support the requested semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fsmap.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/fsmap.c

This file implements ext4’s `FS_IOC_GETFSMAP` support. It translates ext4 allocation and fixed metadata information into generic fsmap records for userspace.

Major responsibilities:
- Convert between generic byte-based `struct fsmap` and ext4 block-based `struct ext4_fsmap`:
  - `ext4_fsmap_from_internal()`
  - `ext4_fsmap_to_internal()`
- Drive getfsmap queries:
  - `ext4_getfsmap()` validates flags/devices/key ordering, prepares per-device query keys, sorts data/journal handlers by device ID, calls each matching handler, and sets `FMH_OF_DEV_T`.
- Report mappings:
  - `ext4_getfsmap_helper()` filters records before the low key, counts or formats entries, emits gaps as `EXT4_FMR_OWN_UNKNOWN`, emits real records, tracks `gfi_next_fsblk`, and supports abort when output is full.
- Data device mapping:
  - `ext4_getfsmap_datadev()` clamps keys to filesystem block bounds, computes start/end block groups, builds fixed metadata records, queries free-space ranges via `ext4_mballoc_query_range()`, merges fixed metadata with free extents, emits trailing retained free extents, and uses a dummy terminal record to flush end gaps.
  - `ext4_getfsmap_datadev_helper()` converts buddy free ranges into fsmap records and coalesces free extents across block group boundaries.
  - `ext4_getfsmap_meta_helper()` emits fixed metadata records that overlap the current query range.
- Journal device mapping:
  - `ext4_getfsmap_logdev()` fabricates a single mapping for an external journal device using `j_blk_offset` and `j_total_len`.
- Fixed metadata discovery:
  - `ext4_getfsmap_find_fixed_metadata()` collects superblocks, group descriptors, reserved GDT blocks, block bitmaps, inode bitmaps, and inode tables for all groups.
  - `ext4_getfsmap_find_sb()` records per-group superblock/GDT/reserved-GDT metadata.
  - `ext4_getfsmap_merge_fixed_metadata()` merges adjacent fixed metadata extents with the same owner.
  - `ext4_getfsmap_free_fixed_metadata()` releases temporary metadata lists.
- Validation and ordering:
  - `ext4_getfsmap_is_valid_device()` accepts the data device, optional external journal device, zero, and wildcard-style device values.
  - `ext4_getfsmap_check_keys()` enforces low-key ordering before query execution.
  - `ext4_getfsmap_dev_compare()` sorts handlers by encoded device number.

Important design points:
- ext4 does not have a full reverse-mapping tree, so fsmap output is synthesized from block allocator free-space data plus known fixed metadata; unknown gaps are reported explicitly.
- Fixed metadata is pre-collected and sorted so it can be interleaved with free-space callbacks.
- Free extents at block group ends are retained temporarily to merge with the next group if adjacent.
- The low key’s nonzero length is treated as a continuation cursor and advanced to avoid returning the same mapping twice.
- Data-device records use filesystem block units internally and are converted to bytes at the public boundary.

Key invariants:
- The formatter is called only until `fmh_count` entries are filled unless it aborts earlier.
- A count-only query has `fmh_count == 0` and increments `fmh_entries` without formatting records.
- `gfi_next_fsblk` is the monotonic cursor used to detect unreported allocated/unknown gaps.
- Metadata-list elements are freed as they become obsolete or at function exit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fsmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fsmap.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/fsmap.h

This header defines ext4’s internal fsmap types, formatter callback, exported conversion/query prototypes, query callback return codes, and special owner constants.

Major contents:
- `struct ext4_fsmap`: internal block-based mapping record with list linkage, device, flags, physical block, owner, and block length.
- `struct ext4_fsmap_head`: internal query header with input/output flags, requested/filled entry counts, and low/high keys.
- Conversion prototypes:
  - `ext4_fsmap_from_internal()`
  - `ext4_fsmap_to_internal()`
- Formatter type:
  - `typedef int (*ext4_fsmap_format_t)(struct ext4_fsmap *, void *)`
- Main query prototype:
  - `ext4_getfsmap()`
- Query callback return values:
  - `EXT4_QUERY_RANGE_ABORT`
  - `EXT4_QUERY_RANGE_CONTINUE`
- Special owners:
  - Free space, unknown owner, static filesystem metadata, journal log, inode table, group descriptors, reserved GDT, block bitmap, inode bitmap.

Important design points:
- Internal lengths and offsets are in filesystem blocks, not bytes.
- Owner constants intentionally share some generic/XFS fsmap owner values and define ext4-specific metadata classes.
- The list node embedded in `ext4_fsmap` supports temporary sorted metadata lists in `fsmap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fsync.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/fsync.c

This file implements ext4’s fsync/fdatasync path for regular files and related metadata synchronization.

Major responsibilities:
- `ext4_sync_file()` is the VFS fsync entry point:
  - Rejects emergency state.
  - Asserts there is no current journal handle.
  - Skips work on read-only superblocks.
  - Handles no-journal and journaled modes separately.
  - Issues device flushes when barriers are required.
  - Reports and advances writeback errors.
- No-journal fsync:
  - `ext4_fsync_nojournal()` syncs metadata buffer-head tracking with `mmb_fsync_noflush()`, writes the inode table buffer through `ext4_write_inode()`, recursively syncs fresh parent directories when needed, and requests a barrier flush if mounted with barriers.
  - `ext4_sync_parent()` walks aliases/parents for inodes marked `EXT4_STATE_NEWENTRY`, syncing parent metadata buffers and inode metadata to close crash windows for just-created directory entries.
- Journaled fsync:
  - `ext4_fsync_journal()` chooses `i_datasync_tid` or `i_sync_tid`, forces a full commit for non-regular files, determines if a barrier flush is needed, and calls `ext4_fc_commit()` for the target transaction.

Important design points:
- Fast commit is used for regular-file fsync in journaled mode; directories and special files force a full commit.
- Data writeback is completed before journal commit via `file_write_and_wait_range()`.
- Barrier handling is split between JBD2 transaction behavior and explicit `blkdev_issue_flush()` when needed.
- No-journal mode must explicitly sync parent directories for recently created entries because there is no journal commit ordering to rely on.

Key invariants:
- `ext4_sync_file()` must not run inside an active ext4 journal handle.
- Writeback errors are reported even if the metadata/journal path succeeded.
- Parent sync recursion stops once `EXT4_STATE_NEWENTRY` is cleared or an error occurs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/fsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/hash.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/hash.c

This file implements ext4 directory-entry hash calculation for htree indexed directories.

Major responsibilities:
- Hash algorithms:
  - Legacy signed and unsigned dx hash via `dx_hack_hash_signed()` / `dx_hack_hash_unsigned()`.
  - Half-MD4 transform via `half_md4_transform()`.
  - TEA transform via `TEA_transform()`.
  - SipHash for encrypted/casefold-aware directory names when the fscrypt key is available.
- String packing:
  - `str2hashbuf_signed()` and `str2hashbuf_unsigned()` pack filename bytes into 32-bit words with length-based padding.
- Core hash selection:
  - `__ext4fs_dirhash()` initializes default or supplied hash seed, switches by `hinfo->hash_version`, computes major and minor hash values, clears the low bit of the major hash, and avoids the htree EOF sentinel.
- Public entry point:
  - `ext4fs_dirhash()` optionally casefolds names with the superblock unicode map for casefolded directories before hashing, provided encryption state permits it.

Important design points:
- Seeds allow per-filesystem hash uniqueness; all-zero seed falls back to built-in defaults.
- Signed and unsigned variants preserve compatibility with historical directory hash behavior.
- SipHash requires the directory encryption key; without it the function warns and returns `-EINVAL`.
- Casefolding allocates a `PATH_MAX` buffer, hashes the folded name if conversion succeeds, and falls back to opaque byte hashing if unicode casefolding fails.
- The returned major hash always has its low bit cleared, matching htree split conventions.

Key invariants:
- Hash version validation is centralized in `__ext4fs_dirhash()`.
- `len == 0` and `name == NULL` can be used by callers to test hash-version support.
- Minor hash is zero for 32-bit-only hash variants and populated for half-MD4/TEA/SipHash.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ialloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/ialloc.c

This file implements ext4 inode allocation, inode freeing, inode bitmap loading/validation, inode placement policy, replay-time inode marking, orphan validation, inode/directory counting, and lazy inode-table zeroing.

Major responsibilities:
- Inode bitmap management:
  - `ext4_mark_bitmap_end()` marks unused tail bits as allocated.
  - `ext4_end_bitmap_read()` completes async bitmap reads.
  - `ext4_read_inode_bitmap()` loads a group’s inode bitmap, initializes uninitialized inode bitmaps, validates bitmap block bounds, and verifies checksums.
  - `ext4_validate_inode_bitmap()` checks checksum validity unless fast-commit replay is active.
- Inode freeing:
  - `ext4_free_inode()` validates refcount/nlink/inode number, clears inode state before freeing the bitmap bit, updates group descriptor free-inode and used-directory counts, updates checksums, updates percpu/flex counters, journals dirty metadata, and marks bitmap corruption on double-free.
- Inode placement:
  - `find_group_orlov()` implements Orlov directory placement, spreading top-level directories and choosing groups/flex groups by free inodes, free clusters, and used directory counts.
  - `find_group_other()` places non-directories near the parent/flex group, then falls back to Orlov or quadratic/linear searches.
  - `get_orlov_stats()` reads group or flex group stats.
- Recently deleted avoidance:
  - `recently_deleted()` checks cached inode table blocks in no-journal mode to avoid quickly reusing recently deleted inodes.
  - `find_inode_bit()` finds a free inode bit, preferring not-recently-deleted candidates but falling back when needed.
- Replay support:
  - `ext4_mark_inode_used()` marks a specific inode allocated, writes/syncs bitmap metadata, initializes block bitmap state if needed, updates group descriptors and checksums, and is used by fast-commit replay.
- New inode creation:
  - `__ext4_new_inode()` performs owner/project/quota setup, fscrypt preparation, journal credit expansion for ACL/security/encryption xattrs, group selection, bitmap bit allocation, group descriptor updates, inode initialization, checksum seed setup, inline-data eligibility, quota allocation, encryption context creation, ACL/security initialization, extent tree initialization, fsync transaction tracking, and dirtying.
- Orphan handling:
  - `ext4_orphan_get()` validates on-disk orphan inode numbers, checks bitmap allocation, loads inode, rejects impossible/bad orphan states, and protects against infinite orphan-list processing.
- Counting:
  - `ext4_count_free_inodes()` sums free inode counts from group descriptors, with optional debug bitmap verification.
  - `ext4_count_dirs()` sums used directory counts.
- Lazy inode-table initialization:
  - `ext4_init_inode_table()` zeros unused inode-table blocks for a group, protects against concurrent allocation with `alloc_sem`, handles partial tables, sets `EXT4_BG_INODE_ZEROED`, updates checksums, and optionally issues a flush barrier.

Important design points:
- Inode bitmap corruption is tracked in mballoc group info so future allocation skips suspicious groups.
- Fast-commit replay bypasses some normal bitmap validation/corruption checks because replay is reconstructing metadata.
- Flex_bg support makes directory and file placement operate on flex groups, then choose a real group inside the flex group.
- New inode setup deliberately initializes owner/quota-related fields early so transaction credit accounting can include later xattr work.
- Encryption xattrs are created before other xattrs to reduce external xattr block use and avoid deduplication.
- New regular files/directories/symlinks use extents when the filesystem supports them.
- Inline data remains possible for eligible new inodes unless DAX/EA-inode flags or mode rules forbid it.

Key invariants:
- Reserved inode numbers in group 0 must never be allocated.
- Bitmap bit allocation is retried under group lock if another thread raced.
- Group descriptor counts, flex counters, percpu counters, bitmap checksums, and group descriptor checksums must stay consistent.
- `insert_inode_locked()` failure is treated as likely bitmap corruption/double allocation.
- Orphan inodes must be allocated in the bitmap and either truncatable or linkless enough not to loop forever.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/indirect.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/indirect.c

This file implements legacy non-extent block mapping and space removal for ext4 inodes that use direct, indirect, double-indirect, and triple-indirect block pointers.

Major responsibilities:
- Block path lookup:
  - `ext4_block_to_path()` translates a logical block into offsets through direct/indirect/double/triple-indirect levels and reports boundary distance.
  - `ext4_get_branch()` reads and validates the indirect block chain, returning either a full chain or the first missing/failed link.
- Allocation goal and length:
  - `ext4_find_near()` chooses an allocation goal near the previous pointer, the containing indirect block, or the inode’s goal block.
  - `ext4_find_goal()` clamps the goal for non-extent 32-bit physical block limits.
  - `ext4_blks_to_allocate()` decides how many contiguous data blocks can be allocated without crossing indirect-block boundaries or existing mappings.
- Block allocation and insertion:
  - `ext4_alloc_branch()` allocates required indirect metadata blocks and data blocks, initializes new indirect blocks, links child pointers inside the new branch, journals create access, and frees all newly allocated blocks on failure.
  - `ext4_splice_branch()` journals the parent, installs the missing pointer, fills contiguous direct pointers when possible, dirties metadata or inode, and frees the new branch on splice failure.
  - `ext4_ind_map_blocks()` is the main non-extent implementation for `ext4_map_blocks()`: it looks up existing mappings, reports holes, allocates missing branches when requested, sets map flags, updates fsync transaction state, and releases indirect buffers.
- Transaction credit estimation:
  - `ext4_ind_trans_blocks()` estimates indirect metadata blocks touched for a contiguous mapping.
- Truncation support:
  - `ext4_ind_truncate_ensure_credits()` extends or restarts truncate transactions and reacquires write access as needed.
  - `ext4_ind_trunc_restart_fn()` dirties metadata/inode, discards preallocations, drops `i_data_sem` during transaction restart, and marks that the lock was dropped.
  - `ext4_find_shared()` finds partially shared branches at a truncate boundary.
  - `ext4_clear_blocks()`, `ext4_free_data()`, and `ext4_free_branches()` clear pointers, validate block ranges, accumulate contiguous frees, handle revoke/forget flags, free subtrees bottom-up, and journal parent metadata.
  - `ext4_ind_truncate()` removes all blocks beyond the inode size for non-extent files, updates extent status cache and `i_disksize`, handles direct/indirect/double/triple branches, and frees whole subtrees.
- Hole punching/range removal:
  - `ext4_ind_remove_space()` frees blocks in a logical range, handling direct-only ranges, ranges crossing levels, and same-level partial branches until start/end paths converge.

Important design points:
- Indirect mapping uses an `Indirect` chain of pointer location, key value, and buffer head to detect missing links and preserve references during updates.
- Allocation prepares the whole disconnected branch first, then atomically splices the final missing link, so failed allocation does not expose partial trees.
- Bigalloc is rejected for allocating non-extent inodes.
- Truncate frees data and indirect blocks bottom-up, using journal revoke/forget flags to prevent replay from resurrecting freed indirect blocks.
- Transaction restarts during truncate must temporarily drop `i_data_sem` to avoid deadlock with block mapping, then reacquire it.
- Pointers are cleared only after journal credit handling and block-range validation.

Key invariants:
- Allocation requires a non-null journal handle; lookup can run without one.
- Callers must hold `i_data_sem` for mapping: write mode when allocating, read mode when only looking up.
- `ext4_get_branch()` validates indirect block references after reading.
- Non-extent files cannot map blocks beyond legacy bitmap maxbytes semantics.
- Truncate and punch-hole logic must preserve blocks below the target range while freeing all complete right-hand subtrees.
- Invalid block references are reported as inode corruption and not freed blindly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/indirect.c -->