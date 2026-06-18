# Group Research: group_740_linux_sources_os_linux_linux_fs_ext4_fast_commit_c_sources_os_linux__0f1ed53094d4

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`. This grouped report covers the listed Linux ext4 fast-commit, regular-file, fsmap, fsync, directory-hash, inode-allocation, and indirect-block mapping files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/fast_commit.c -->
# File Research: sources/os/linux/linux/fs/ext4/fast_commit.c

Implements ext4 fast commits: fine-grained TLV journaling for selected inode, dentry, and data-range updates, plus recovery scan/replay logic.

Key behavior:
- Tracks fast-commit eligibility with `ext4_fc_disabled()`, `ext4_fc_eligible()`, and `ext4_fc_mark_ineligible()`.
- Tracks per-inode fast-commit state through `i_sync_tid`, `i_fc_list`, `i_fc_lblk_start`, and `i_fc_lblk_len`.
- Tracks dentry operations for create/link/unlink via `ext4_fc_track_create()`, `ext4_fc_track_link()`, and `ext4_fc_track_unlink()`.
- Marks encrypted filenames, inline data, journal-data mode, xattrs, unsupported operations, and allocation failures as fast-commit ineligible.
- `ext4_fc_track_inode()` waits for an inode already being fast-committed before enqueueing a new update.
- `ext4_fc_track_range()` coalesces modified logical block ranges for later ADD_RANGE / DEL_RANGE emission.
- Commit serialization writes TLVs for:
  - `HEAD`
  - dentry create/link/unlink updates
  - data range adds/deletes
  - raw inode snapshots
  - `TAIL` with transaction id and CRC
- `ext4_fc_reserve_space()` manages fast-commit block packing and emits `PAD` TLVs when records do not fit in the current block.
- `ext4_fc_write_tail()` ends each fast commit on a block boundary and uses barriers/FUA when mounted with barriers.
- `ext4_fc_perform_commit()` flushes inode data, locks journal updates to mark committing inodes, writes TLVs, and submits the tail.
- `ext4_fc_commit()` coordinates with JBD2 fast-commit begin/end APIs, raises I/O priority to journal priority during the commit, updates stats, and falls back to a full commit when needed.
- `ext4_fc_cleanup()` clears committing state, wakes waiters, releases dentry update records, moves staging queues to main queues, and clears ineligibility after the relevant tid.
- Replay scan validates TLV lengths, CRCs, tail tids, and supported features, and records physical regions needed by ADD_RANGE tags.
- Replay handlers enforce idempotent outcomes for unlink, link, create, inode snapshot, add range, and delete range.
- Replay records modified inodes and later reconstructs block bitmap state by walking their extents.
- Exposes fast-commit stats and ineligibility reasons through `ext4_fc_info_show()`.
- Creates/destroys the slab cache for `struct ext4_fc_dentry_update`.

Important interactions:
- Fast commit is built around JBD2 fast-commit callbacks and queues in `struct ext4_sb_info`.
- Uses `s_fc_lock` for global fast-commit queues and `i_fc_lock` for per-inode fast-commit state.
- Uses `EXT4_STATE_FC_FLUSHING_DATA` and `EXT4_STATE_FC_COMMITTING` to coordinate evict, track, and commit paths.
- Replay depends on extent helpers, bitmap marking, inode checksum reset, and regular ext4 namei helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/fast_commit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/fast_commit.h -->
# File Research: sources/os/linux/linux/fs/ext4/fast_commit.h

Defines the ext4 fast-commit on-disk TLV format and in-kernel replay/tracking structures.

Key behavior:
- Defines fast-commit TLV tags:
  - `ADD_RANGE`
  - `DEL_RANGE`
  - `CREAT`
  - `LINK`
  - `UNLINK`
  - `INODE`
  - `PAD`
  - `TAIL`
  - `HEAD`
- Defines on-disk value structures for head, add range, delete range, dentry info, inode snapshot, and tail CRC/tid.
- Defines fast-commit status codes used for stats.
- Defines all fast-commit ineligibility reason enum values.
- Under `__KERNEL__`, defines:
  - `struct ext4_fc_dentry_update`
  - `struct ext4_fc_stats`
  - `struct ext4_fc_alloc_region`
  - `struct ext4_fc_replay_state`
- Provides `tag2str()` for debug/trace-friendly tag names.
- Notes that this header must remain byte-identical with the e2fsprogs copy.

Important interactions:
- Shared contract between kernel fast-commit writer/replay code and userspace fsck/libext2fs understanding of fast-commit records.
- Replay state tracks valid tags, CRC progress, excluded allocation regions, and modified inode lists.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/fast_commit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/file.c -->
# File Research: sources/os/linux/linux/fs/ext4/file.c

Implements ext4 regular-file operations: reads, writes, mmap, open/release, llseek, and file/inode operation tables.

Key behavior:
- `ext4_should_use_dio()` preserves ext4 direct-I/O behavior:
  - unsupported ext4 features fall back to buffered I/O
  - misaligned DIO for otherwise supported files is attempted so iomap can return `EINVAL`
- Read path:
  - rejects forced shutdown
  - skips atime work for zero-length reads
  - routes DAX reads to `dax_iomap_rw()`
  - routes direct reads to `iomap_dio_rw()`
  - otherwise uses generic buffered reads
- `ext4_file_splice_read()` rejects forced shutdown and delegates to `filemap_splice_read()`.
- `ext4_release_file()` flushes delayed allocation close state, discards preallocations for the last writer, and frees htree directory private data if present.
- Write checks enforce immutability, generic write limits, non-extent bitmap max size, timestamp/security updates, and stale-data EOF zeroing for writes beyond EOF.
- Buffered writes lock the inode exclusively and use `generic_perform_write()`.
- Direct writes:
  - choose shared vs exclusive inode locking based on extending writes, overwrite status, unaligned I/O, unwritten extents, and security updates
  - drain outstanding DIO when partial-block zeroing could corrupt concurrent I/O
  - add the inode to the orphan list for extending writes
  - convert unwritten extents at end I/O, including the atomic-write conversion path
  - clean up orphan/truncate state after synchronous extending DIO
  - can fall back to buffered I/O for remaining data and then writeback/invalidate the affected page-cache range
- Atomic writes validate write unit bounds and generic atomic-write constraints before DIO.
- DAX write path uses exclusive locking, orphan protection for extending writes, `dax_iomap_rw()`, and inode extension cleanup.
- DAX fault path starts a journal handle for shared writable faults, handles ENOSPC retries, and completes synchronous DAX faults.
- `ext4_file_mmap_prepare()` validates emergency/forced-shutdown state, DAX synchronous mapping support, and installs DAX or buffered vm ops.
- `ext4_sample_last_mounted()` opportunistically records the current mount path into the superblock.
- `ext4_file_open()` validates shutdown state, samples mount path, runs fscrypt/fsverity open checks, attaches a JBD2 inode for writers, marks atomic-write capability, and delegates quota open handling.
- `ext4_llseek()` supports generic seeks plus `SEEK_HOLE` and `SEEK_DATA` through iomap report ops.
- Defines `ext4_file_operations` and `ext4_file_inode_operations`.

Important interactions:
- Relies on iomap for DIO, DAX, and hole/data seeking.
- Coordinates orphan list, unwritten extent conversion, inode size, and `i_disksize` for crash-safe extending writes.
- Operation tables connect this file to ioctl, fallocate, fsync, xattrs, ACLs, fiemap, and file attributes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/fsmap.c -->
# File Research: sources/os/linux/linux/fs/ext4/fsmap.c

Implements ext4 support for `FS_IOC_GETFSMAP`, reporting filesystem physical-space mappings for the data device and optional external journal device.

Key behavior:
- Converts between public `struct fsmap` byte units and internal `struct ext4_fsmap` block units.
- Uses `struct ext4_getfsmap_info` to track query keys, formatter callback, current device, current block group, next expected block, fixed metadata, retained free extent, and final-record state.
- Reports gaps between known records as `EXT4_FMR_OWN_UNKNOWN`.
- Supports count-only mode when `fmh_count == 0`.
- Builds and reports fixed metadata records for:
  - superblock copies
  - group descriptors
  - reserved GDT blocks
  - block bitmaps
  - inode bitmaps
  - inode tables
- Sorts and merges adjacent fixed metadata records before query output.
- Merges fixed metadata with free-space records from mballoc query callbacks.
- Coalesces free extents that cross block-group boundaries.
- `ext4_getfsmap_logdev()` fabricates one mapping for an external journal device.
- `ext4_getfsmap_datadev()` clamps query ranges to filesystem data blocks, converts global keys to block-group keys, queries each block group through `ext4_mballoc_query_range()`, and emits final unknown tail gaps.
- Validates requested device ids against the filesystem block device and external journal device.
- Validates low/high fsmap key ordering.
- `ext4_getfsmap()` sorts per-device handlers, supports continuation via nonzero low-key length, dispatches matching device handlers, and marks device ids as present in output flags.

Important interactions:
- Uses mballoc’s range-query callbacks for free-space discovery.
- Uses ext4 group descriptor helpers to locate fixed metadata.
- Uses `trace_ext4_fsmap_*` events for low/high keys and emitted mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/fsmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/fsmap.h -->
# File Research: sources/os/linux/linux/fs/ext4/fsmap.h

Declares ext4’s internal fsmap structures, formatter callback type, query entry point, and owner constants.

Key behavior:
- `struct ext4_fsmap` stores device, flags, physical block, owner, length, and list linkage.
- `struct ext4_fsmap_head` stores input/output flags, count/entry counters, and low/high keys.
- Declares conversion helpers:
  - `ext4_fsmap_from_internal()`
  - `ext4_fsmap_to_internal()`
- Declares `ext4_getfsmap()`.
- Defines query callback return values:
  - `EXT4_QUERY_RANGE_ABORT`
  - `EXT4_QUERY_RANGE_CONTINUE`
- Defines special owner values for free space, unknown owners, filesystem metadata, journal log, inodes, group descriptors, reserved GDT, block bitmap, and inode bitmap.

Important interactions:
- Used by `fsmap.c` and ioctl-facing code to translate ext4 physical-space records into generic fsmap output.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/fsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/fsync.c -->
# File Research: sources/os/linux/linux/fs/ext4/fsync.c

Implements ext4 `fsync` / `fdatasync` handling for journaled and non-journaled filesystems.

Key behavior:
- `ext4_sync_parent()` handles no-journal crash safety for newly created files by recursively syncing freshly created parent directories marked `EXT4_STATE_NEWENTRY`.
- `ext4_fsync_nojournal()`:
  - syncs metadata buffer lists without a flush
  - forces inode table writeout
  - syncs parent directories when required
  - requests a block-device flush when barriers are enabled
- `ext4_fsync_journal()`:
  - chooses `i_datasync_tid` for datasync or `i_sync_tid` for full fsync
  - forces a full commit for directories and special files because fast commits do not support those fsync targets
  - requests an extra flush if JBD2 barriers will not cover the transaction’s data barrier
  - invokes `ext4_fc_commit()` for regular-file journal fsync
- `ext4_sync_file()`:
  - rejects emergency state
  - handles read-only mounts as already synced
  - dispatches no-journal vs journal mode
  - writes and waits on the requested file range before journal commit
  - issues a final device flush when needed
  - reports writeback errors through `file_check_and_advance_wb_err()`

Important interactions:
- Regular-file fsync is the main entry point into ext4 fast commits.
- Non-regular journaled fsync deliberately falls back to full JBD2 commit.
- No-journal mode depends on metadata buffer lists and parent directory syncing to narrow crash-loss windows.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/fsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/hash.c -->
# File Research: sources/os/linux/linux/fs/ext4/hash.c

Implements ext4 directory htree filename hashing.

Key behavior:
- Provides TEA, half-MD4, and legacy hash implementations.
- Supports signed and unsigned character variants for legacy, half-MD4, and TEA hashes.
- `__ext4fs_dirhash()`:
  - initializes the default hash seed
  - uses the filesystem hash seed if nonzero
  - dispatches by `hinfo->hash_version`
  - supports encrypted-directory `DX_HASH_SIPHASH` via `fscrypt_fname_siphash()`
  - rejects siphash if the encryption key is unavailable
  - clears the low hash bit and avoids the htree EOF sentinel value
  - fills both major and minor hash outputs
- `ext4fs_dirhash()`:
  - applies Unicode casefolding for casefolded directories when possible
  - permits encrypted casefolding only when the encryption key is available
  - falls back to hashing the opaque byte sequence when casefolding fails or is not applicable

Important interactions:
- Used by htree indexed directory lookup/allocation and by inode placement logic that hashes top-level directory names.
- Integrates with fscrypt for keyed siphash and with Unicode normalization for case-insensitive directories.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/ialloc.c -->
# File Research: sources/os/linux/linux/fs/ext4/ialloc.c

Implements ext4 inode bitmap handling, inode allocation/freeing, orphan validation, inode counters, and lazy inode-table initialization.

Key behavior:
- `ext4_mark_bitmap_end()` marks unused tail bits in bitmap blocks as allocated.
- `ext4_read_inode_bitmap()` validates inode bitmap block locations, handles uninitialized inode bitmaps, reads bitmap buffers, and verifies checksums.
- `ext4_validate_inode_bitmap()` skips checksum verification during fast-commit replay and marks corrupted bitmap groups on checksum failure.
- `ext4_free_inode()`:
  - validates inode refcount and link count
  - clears inode state before freeing bitmap bits
  - updates inode bitmap, group descriptor counts, directory counts, flex-group counters, checksums, and percpu counters
  - marks suspicious bitmap groups corrupt when needed
- Orlov directory allocator:
  - spreads top-level directories by free inode/free cluster averages and directory counts
  - uses directory-name hash or random start point for top-level directories
  - uses flex_bg packing when enabled
  - falls back to above-average free-inode groups
- Non-directory allocator prefers the parent flex group/block group, then quadratic probing, then linear search.
- No-journal mode avoids recently deleted inodes when their inode-table buffer is still dirty, unless needed to prevent false ENOSPC.
- `ext4_mark_inode_used()` is used by recovery/replay to mark a specific inode allocated, initialize related bitmaps, update descriptor counts, and sync metadata immediately.
- `__ext4_new_inode()`:
  - initializes ownership, project id, fscrypt state, quotas, xattr credits, ACL/security needs, and journal credits
  - chooses a target group from explicit goal, Orlov, or parent locality
  - finds and sets a free inode bitmap bit under group lock
  - initializes block bitmap if needed
  - updates group descriptors, checksums, percpu/flex counters, inode core fields, timestamps, flags, checksum seed, inline-data eligibility, extents, fsync tid, ACLs, security xattrs, encryption context, and quota allocation
  - inserts the inode into the inode hash and handles allocation failure cleanup
- `ext4_orphan_get()` validates orphan-list inode numbers, bitmap allocation state, truncatability, bad-inode state, and next-orphan bounds before returning an orphan inode.
- `ext4_count_free_inodes()` and `ext4_count_dirs()` aggregate group descriptor counters.
- `ext4_init_inode_table()` lazily zeroes unused inode-table blocks, coordinates with allocation via `alloc_sem`, validates unused counts, optionally flushes, and sets `EXT4_BG_INODE_ZEROED`.

Important interactions:
- Shares group descriptor and bitmap corruption state with mballoc/group-info code.
- Fast-commit replay uses `ext4_mark_inode_used()` and bypasses some normal bitmap corruption checks while replay state is active.
- New inode creation ties together quota, fscrypt, xattr, ACL, security, extent initialization, journaling, and flex_bg accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/indirect.c -->
# File Research: sources/os/linux/linux/fs/ext4/indirect.c

Implements block mapping, allocation, truncation, and hole punching for non-extent ext4 inodes using traditional direct/indirect block pointers.

Key behavior:
- Defines `Indirect`, a cached pointer-chain entry containing the pointer location, stored key, and backing buffer.
- `ext4_block_to_path()` maps a logical block to direct, single-indirect, double-indirect, or triple-indirect offsets.
- `ext4_get_branch()` walks an indirect pointer chain, reads indirect blocks, validates block references, and stops at holes or I/O/corruption errors.
- Allocation locality helpers:
  - `ext4_find_near()` prefers a previous neighboring pointer, then the indirect block location, then the inode’s goal block.
  - `ext4_find_goal()` limits goals to the 32-bit physical range used by non-extent files.
- `ext4_blks_to_allocate()` counts how many data blocks can be allocated contiguously within the current indirect boundary/hole.
- `ext4_alloc_branch()` allocates needed indirect blocks plus data blocks, initializes newly allocated indirect buffers, links child pointers in memory, and frees all new blocks on failure.
- `ext4_splice_branch()` journals the parent pointer, splices the newly allocated branch into the inode/indirect tree, fills contiguous direct mappings when possible, and dirties either the parent indirect block or inode.
- `ext4_ind_map_blocks()`:
  - looks up existing non-extent mappings
  - reports hole length for lookup-only requests
  - rejects block allocation for non-extent inodes on bigalloc filesystems
  - allocates missing indirect/data branches when requested
  - returns mapped length, physical block, new/mapped/boundary flags, and updates fsync transaction state
- `ext4_ind_trans_blocks()` estimates indirect metadata blocks touched by mapping contiguous blocks.
- Truncation credit helpers restart transactions when needed and temporarily drop `i_data_sem` safely.
- `ext4_find_shared()` identifies partially truncated indirect branches around the truncation boundary.
- `ext4_clear_blocks()` validates ranges, zeroes pointer slots, and frees contiguous blocks with correct metadata/forget flags.
- `ext4_free_data()` coalesces contiguous leaf block runs before freeing.
- `ext4_free_branches()` recursively frees indirect subtrees bottom-up, writes revoke/forget records for indirect metadata blocks, and clears parent pointers.
- `ext4_ind_truncate()` removes all blocks beyond inode size, updates `i_disksize`, removes extent-status cache entries, frees partial branches, and clears whole indirect subtrees.
- `ext4_ind_remove_space()` frees an arbitrary logical block range for punch-hole style operations, handling direct-only ranges, cross-level ranges, same-level ranges, partial branches, and whole subtrees.

Important interactions:
- Used only for inodes without `EXT4_INODE_EXTENTS`.
- Requires `i_data_sem`: write lock for allocation/truncate/punch, read lock for lookup.
- Coordinates with JBD2 metadata access, revoke/forget handling, preallocation discard, extent-status cache invalidation, and ext4 block allocator/freeing paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/indirect.c -->