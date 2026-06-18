# subset-b-005650 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fast_commit.c -->
# sources/distributed-fs/ceph-client/fs/ext4/fast_commit.c

## Purpose
`fast_commit.c` implements ext4 fast commits: a compact TLV log of filesystem deltas that lets fsync avoid a full JBD2 transaction commit when the pending operations are replayable. It covers the full lifecycle: in-memory tracking of changed inodes and dentries, fast-commit block construction, fallback to full commits when an operation is ineligible, post-commit cleanup, recovery scanning, replay, statistics, and the dentry-update slab cache.

## Important APIs, types, and functions
The main public entry points are `ext4_fc_init_inode`, `ext4_fc_del`, `ext4_fc_mark_ineligible`, `ext4_fc_track_unlink`, `ext4_fc_track_link`, `ext4_fc_track_create`, `ext4_fc_track_inode`, `ext4_fc_track_range`, `ext4_fc_commit`, `ext4_fc_record_regions`, `ext4_fc_replay_check_excluded`, `ext4_fc_replay_cleanup`, `ext4_fc_init`, `ext4_fc_info_show`, `ext4_fc_init_dentry_cache`, and `ext4_fc_destroy_dentry_cache`. Commit helpers include `ext4_fc_reserve_space`, `ext4_fc_write_tail`, `ext4_fc_add_tlv`, `ext4_fc_add_dentry_tlv`, `ext4_fc_write_inode`, `ext4_fc_write_inode_data`, `ext4_fc_flush_data`, `ext4_fc_commit_dentry_updates`, `ext4_fc_perform_commit`, `ext4_fc_update_stats`, and `ext4_fc_cleanup`. Replay helpers include `ext4_fc_replay_scan`, `ext4_fc_replay`, `ext4_fc_replay_unlink`, `ext4_fc_replay_link`, `ext4_fc_replay_create`, `ext4_fc_replay_inode`, `ext4_fc_replay_add_range`, `ext4_fc_replay_del_range`, and `ext4_fc_set_bitmaps_and_counters`.

The important state lives in `struct ext4_sb_info` and `struct ext4_inode_info`: `s_fc_q[]`, `s_fc_dentry_q[]`, `s_fc_lock`, `s_fc_bh`, `s_fc_bytes`, `s_fc_subtid`, `s_fc_ineligible_tid`, `s_fc_stats`, and per-inode `i_fc_list`, `i_fc_dilist`, `i_fc_lblk_start`, `i_fc_lblk_len`, `i_sync_tid`, and FC state bits. On-disk TLV structures come from `fast_commit.h`.

## Control flow
Tracking starts from ext4 mutation sites. Dentry operations snapshot names and enqueue `ext4_fc_dentry_update` nodes unless encrypted filenames or allocation failure make the transaction ineligible. Inode and range tracking fold repeated changes within one tid into the per-inode logical-block interval and enqueue the inode in the main or staging fast-commit list, depending on whether a full or fast commit is already running.

`ext4_fc_commit()` is called by fsync through `ext4_fsync_journal()`. It starts a JBD2 fast-commit section with `jbd2_fc_begin_commit`; if another commit already covers the requested tid it skips, and if fast commit is disabled, failed, or ineligible it falls back to `jbd2_complete_transaction`. The successful path raises I/O priority, flushes data for queued inodes, marks them `EXT4_STATE_FC_COMMITTING` under a journal update barrier, emits a HEAD tag for the first sub-commit, writes dentry TLVs, range TLVs, inode TLVs, and finally a TAIL tag with CRC and tid. Buffer submission uses FUA/preflush for the tail when barriers are enabled.

Cleanup releases JBD2 fast-commit buffers, clears committing/flushing bits, wakes waiters, frees dentry updates, moves staging queues to main, clears the ineligible mount flag once the relevant tid is committed, and resets `s_fc_bytes` after full commits. Replay first scans TLVs, validates lengths, features, offset ordering, and CRC-bearing tails, and records physical ranges that must be excluded from allocation. Replay then applies idempotent outcomes: unlink/link/create dentries, restore raw inode bodies, add/remove extents, and rebuild block bitmaps/counters for modified inodes.

## State and persistence behavior
Persistent state is the fast-commit area in the journal, encoded as TLVs plus CRC-protected tail records. The implementation intentionally logs resulting state, not procedural operations, so replay can be re-run after a crash. The in-memory queues are protected by `s_fc_lock`; per-inode FC fields are protected by `i_fc_lock`; commit uses JBD2 update locking to prevent handles from racing with the set of inodes being serialized. `EXT4_STATE_FC_FLUSHING_DATA` prevents eviction during data writeout, and `EXT4_STATE_FC_COMMITTING` makes new tracking wait until the current inode commit completes.

Replay writes metadata directly and issues buffer syncs/flushes in several places, notably inode replay. It also sets `EXT4_FC_REPLAY` in mount state so allocation and bitmap validation paths can adapt during recovery.

## Dependencies and integration points
This file sits between ext4 mutation paths, `fsync.c`, extents, mballoc, inode loading, namei helpers, the JBD2 fast-commit API, checksumming, tracepoints, and seqfs stats. It depends on `fast_commit.h` for wire format, `ext4_jbd2.h` for handles and commit integration, `ext4_extents.h` for range replay, and `mballoc.h` for bitmap marking and replay allocation exclusion.

## Risks and test signals
Risks include TLV length validation mistakes, CRC or padding accounting errors, stale name snapshots, queue migration races, waiting while holding locks, incorrect fallback eligibility, orphaned committing/flushing bits, replay idempotence gaps, block reallocation conflicts during replay, and direct replay metadata writes that are not journaled. Test signals should cover fsync after create/link/unlink/rename-like sequences, append/truncate/hole operations, repeated fast commits within one tid, fallback reasons such as xattrs, encrypted filenames, journaled data, verity, and resize, crash recovery after each TLV class, CRC corruption, unsupported feature bits, ENOSPC in fast-commit area, external journal devices, barrier/no-barrier mounts, concurrent inode eviction, and debugfs fast-commit statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fast_commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fast_commit.h -->
# sources/distributed-fs/ceph-client/fs/ext4/fast_commit.h

## Purpose
`fast_commit.h` defines the shared on-disk and kernel-private data contracts for ext4 fast commits. The header explicitly notes that the kernel copy and the e2fsprogs/libext2fs copy must remain byte-identical, making this file part of both kernel recovery behavior and userspace filesystem tooling compatibility.

## Important APIs, types, and functions
The wire-format definitions are `EXT4_FC_TAG_ADD_RANGE`, `DEL_RANGE`, `CREAT`, `LINK`, `UNLINK`, `INODE`, `PAD`, `TAIL`, and `HEAD`; `EXT4_FC_SUPPORTED_FEATURES`; and TLV payload structures `struct ext4_fc_tl`, `ext4_fc_head`, `ext4_fc_add_range`, `ext4_fc_del_range`, `ext4_fc_dentry_info`, `ext4_fc_inode`, and `ext4_fc_tail`. Kernel-only state includes `struct ext4_fc_dentry_update`, `struct ext4_fc_stats`, `struct ext4_fc_alloc_region`, and `struct ext4_fc_replay_state`. The header also defines status codes, ineligibility reason codes, `EXT4_FC_REPLAY_REALLOC_INCREMENT`, `region_last()`, and `tag2str()`.

## Control flow
The commit path in `fast_commit.c` serializes the TLV payloads defined here, and the replay path validates and decodes them. Dentry payloads store parent inode, target inode, and variable-length name bytes. Inode payloads store inode number plus raw inode bytes. Range payloads describe either an extent-shaped add or logical deletion interval. TAIL payloads close atomic commit units by carrying tid and CRC.

## State and persistence behavior
All non-`__KERNEL__` structures are persistent ABI. Field sizes, endian annotations, tag values, and payload lengths must not drift from e2fsprogs. Kernel-only replay arrays dynamically track excluded physical regions and modified inodes so recovery can avoid accidental block reuse and later repair allocation bitmaps.

## Dependencies and integration points
This header is included by ext4 kernel fast commit code and mirrored into e2fsprogs. It depends on ext4 scalar types, list heads, and name snapshots under `__KERNEL__`, and on the broader fsmap owner namespace for no direct part.

## Risks and test signals
Risks are ABI drift between kernel and userspace, endian/packing mistakes, accepting unsupported feature bits, ineligibility reason/table mismatches, and assuming a fixed inode payload size despite extra inode fields. Test signals include byte-for-byte comparison with e2fsprogs, replay of every TLV type, fuzzed TLV lengths, unknown tag handling, unsupported feature handling, and debug output that exercises `tag2str()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fast_commit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/file.c -->
# sources/distributed-fs/ceph-client/fs/ext4/file.c

## Purpose
`file.c` implements ext4 regular-file VFS operations: read, write, splice read/write, mmap preparation, DAX faults, llseek, open/release, direct-I/O policy, atomic-write validation, and operation tables. It is the main bridge between generic VFS file methods and ext4-specific journaling, DAX, iomap, delayed allocation, fscrypt, fsverity, quota, and writeback rules.

## Important APIs, types, and functions
The exported operation tables are `ext4_file_operations` and `ext4_file_inode_operations`; `ext4_llseek` is a visible helper. Key internal functions are `ext4_should_use_dio`, `ext4_dio_read_iter`, `ext4_dax_read_iter`, `ext4_file_read_iter`, `ext4_file_splice_read`, `ext4_release_file`, `ext4_unaligned_io`, `ext4_extending_io`, `ext4_overwrite_io`, `ext4_generic_write_checks`, `ext4_write_checks`, `ext4_buffered_write_iter`, `ext4_handle_inode_extension`, `ext4_inode_extension_cleanup`, `ext4_dio_write_end_io`, `ext4_dio_write_checks`, `ext4_dio_write_iter`, `ext4_dax_write_iter`, `ext4_file_write_iter`, `ext4_dax_huge_fault`, `ext4_file_mmap_prepare`, `ext4_sample_last_mounted`, and `ext4_file_open`.

## Control flow
Reads first reject forced shutdown and zero-length atime-only work. DAX reads take the DAX iomap path under the shared inode lock and fall back if DAX changed. Direct reads use `iomap_dio_rw` only when `ext4_dio_alignment()` says ext4 feature state allows direct I/O; otherwise they clear `IOCB_DIRECT` and use generic buffered reads.

Writes reject emergency state, route DAX to `dax_iomap_rw`, validate atomic-write sizes against superblock AWU bounds, and choose direct or buffered I/O from `IOCB_DIRECT`. Buffered writes take the exclusive inode lock, run generic and ext4-specific checks, zero a partial block when writing beyond EOF, call `generic_perform_write`, and then `generic_write_sync`. Direct writes start optimistically with a shared lock for likely overwrites, upgrade to exclusive locking for security changes, extending writes, non-overwrites, and dangerous unaligned unwritten writes, and may force synchronous DIO to serialize partial-block zeroing. Extending DIO/DAX adds the inode to the orphan list, updates size in `ext4_handle_inode_extension`, and cleans up with truncate/orphan removal on failure or race.

`ext4_file_open` samples the mount path into the superblock once, opens fscrypt and fsverity state, attaches a `jbd2_inode` for writers, advertises atomic-write capability, and sets `FMODE_NOWAIT` and `FMODE_CAN_ODIRECT`. `ext4_release_file` drains delayed allocation on close and discards preallocations for the last writer.

## State and persistence behavior
Persistent changes include file size, `i_disksize`, orphan-list membership, inode timestamps/security changes, superblock `s_last_mounted`, and extent conversion from unwritten to written after DIO. Orphan handling protects extending DIO/DAX writes from crashes between block allocation and size update. DAX page faults start journal handles only for shared write faults and finish synchronous faults with `dax_finish_sync_fault`.

## Dependencies and integration points
This file depends on VFS iter I/O, iomap, DAX, page-fault machinery, fscrypt, fsverity, quota, xattrs/ACLs, ext4 journaling, delayed allocation, extent mapping, inode state flags, block zeroing, file leases, and traceable writeback errors. `fsync` is delegated to `ext4_sync_file`.

## Risks and test signals
Risks include direct-I/O fallback semantic regressions, unaligned unwritten DIO corruption, orphan cleanup errors after extending writes, atomic-write flag misuse, DAX versus non-DAX races, mmap support mismatches for synchronous mappings, stale page-cache contents after partial DIO fallback, and incorrect maxbytes handling for non-extent files. Test signals include buffered/direct/DAX reads and writes, NOWAIT lock failures, unaligned DIO to holes and unwritten extents, extending DIO with injected ENOSPC/EIO, atomic-write min/max validation, DAX shared and COW faults, fscrypt/fsverity opens, read-only and forced-shutdown behavior, SEEK_HOLE/SEEK_DATA, last-writer preallocation discard, and mount-path sampling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fsmap.c -->
# sources/distributed-fs/ceph-client/fs/ext4/fsmap.c

## Purpose
`fsmap.c` implements ext4 support for `FS_IOC_GETFSMAP`, reporting physical block ownership maps for the data device and optional external journal device. It converts user-visible byte-addressed `struct fsmap` requests into ext4 block/cluster queries, fabricates records for fixed filesystem metadata and journal space, reports free space from mballoc, and emits unknown-owner gaps when no better reverse mapping exists.

## Important APIs, types, and functions
The public helpers are `ext4_fsmap_from_internal`, `ext4_fsmap_to_internal`, and `ext4_getfsmap`. Internal state is carried by `struct ext4_getfsmap_info` and `struct ext4_getfsmap_dev`. Major helpers include `ext4_getfsmap_helper`, `ext4_getfsmap_meta_helper`, `ext4_getfsmap_datadev_helper`, `ext4_getfsmap_logdev`, `ext4_getfsmap_fill`, `ext4_getfsmap_find_sb`, `ext4_getfsmap_compare`, `ext4_getfsmap_merge_fixed_metadata`, `ext4_getfsmap_find_fixed_metadata`, `ext4_getfsmap_datadev`, `ext4_getfsmap_is_valid_device`, and `ext4_getfsmap_check_keys`.

## Control flow
`ext4_getfsmap()` validates flags and device keys, creates sorted device handlers for the main block device and optional external journal, converts the low key into a resume point by adding its length, verifies low/high ordering, and dispatches each selected device. The data-device handler clamps the query to filesystem block bounds, derives start/end block groups, builds a sorted/merged list of fixed-location metadata, and queries each group through `ext4_mballoc_query_range`. Metadata and free-space callbacks merge fixed metadata with free extents, retain free extents at block-group boundaries for cross-group merging, and pass each mapping to `ext4_getfsmap_helper`. The helper handles count-only mode, output-limit aborts, unknown gaps, tracing, and formatter callbacks. The log-device handler fabricates one record for the external journal.

## State and persistence behavior
The file is read-only from the filesystem perspective. Runtime state consists of query cursors (`gfi_next_fsblk`, low/high keys, last retained free extent, metadata list, current group/device) and allocated metadata-list entries. It reports persistent ownership from group descriptors, bitmaps, inode tables, free-space bitmaps, and journal geometry but does not mutate them.

## Dependencies and integration points
It integrates with the generic fsmap ioctl ABI, ext4 block group descriptors, buddy allocator range queries, fixed metadata layout helpers, external journal device state, Linux sorting/list APIs, and ext4 tracepoints. Owner constants are defined in `fsmap.h`.

## Risks and test signals
Risks include unit conversion errors between bytes, blocks, and clusters, off-by-one high-key clipping, resume-key duplication or skipping, missing metadata/free-space merge boundaries, memory leaks on early errors, invalid external journal device ordering, count-only overflow behavior, and unknown-gap over-reporting. Test signals include count-only and bounded-output calls, resumed queries using the last returned record, filesystems with flex_bg/meta_bg/sparse superblocks/bigalloc, external journal devices, first/last block boundary queries, signal interruption, metadata checksum corruption, and comparison against `debugfs`/`filefrag` expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fsmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fsmap.h -->
# sources/distributed-fs/ceph-client/fs/ext4/fsmap.h

## Purpose
`fsmap.h` defines ext4's internal representation and owner namespace for filesystem mapping queries. It isolates the byte-oriented userspace `struct fsmap` ABI from ext4's block-oriented internal query engine.

## Important APIs, types, and functions
The core types are `struct ext4_fsmap`, which stores list linkage, device id, flags, physical block offset, owner, and block length, and `struct ext4_fsmap_head`, which stores ioctl flags, entry counts, and low/high keys. It declares `ext4_fsmap_from_internal`, `ext4_fsmap_to_internal`, `ext4_getfsmap`, and the formatter callback type `ext4_fsmap_format_t`. It also defines callback continuation codes and owner constants for free space, unknown ownership, static filesystem metadata, journal log, inode tables, group descriptors, reserved GDT blocks, block bitmaps, and inode bitmaps.

## Control flow
Callers translate ioctl keys into `ext4_fsmap` keys, call `ext4_getfsmap()`, and supply a formatter that copies or counts records. The implementation in `fsmap.c` fills `ext4_fsmap` records and converts them back before returning to userspace.

## State and persistence behavior
The header itself has no mutable state. Its structures describe transient query state and returned records. Owner constants are part of the user-visible interpretation of persistent disk regions, so renumbering them would affect tooling.

## Dependencies and integration points
It depends on the generic `fsmap` owner definitions and kernel list heads. It is used by ext4 ioctl code and by `fsmap.c`, with owner values shared conceptually with XFS where generic constants exist.

## Risks and test signals
Risks are ABI confusion between byte and block units, insufficient reserved-field clearing in converters, owner-code drift from userspace expectations, and formatter implementations that mishandle `fmh_entries`. Test signals include ioctl structure round trips, owner decoding in xfs_io-style tools, empty/count-only queries, and mappings for each special owner type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fsmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fsync.c -->
# sources/distributed-fs/ceph-client/fs/ext4/fsync.c

## Purpose
`fsync.c` implements ext4's `fsync`, `fdatasync`, and msync-backed file synchronization path. It chooses between no-journal metadata flushing and journal/fast-commit synchronization, handles parent directory persistence for just-created entries in no-journal mode, and issues block-device cache flushes when required for ordering.

## Important APIs, types, and functions
The exported entry point is `ext4_sync_file`. Internal helpers are `ext4_sync_parent`, `ext4_fsync_nojournal`, and `ext4_fsync_journal`. The implementation uses `mmb_fsync_noflush`, `mmb_sync`, `sync_inode_metadata`, `ext4_write_inode`, `file_write_and_wait_range`, `ext4_fc_commit`, `ext4_force_commit`, `jbd2_trans_will_send_data_barrier`, `blkdev_issue_flush`, and `file_check_and_advance_wb_err`.

## Control flow
`ext4_sync_file()` first rejects emergency state, asserts that the caller has no open journal handle, traces entry, and returns quickly for read-only filesystems except for writeback-error reporting. Without a journal, it syncs metadata buffer lists for the target range, forces inode-table writeout, recursively syncs freshly created parent directories while `EXT4_STATE_NEWENTRY` remains set, and requests a cache flush if barriers are enabled. With a journal, it writes and waits file data for the requested range, then calls `ext4_fsync_journal()`. Regular files can use `ext4_fc_commit()` for the relevant sync or datasync tid; directories and special files force a full commit because fast commit does not support them. If JBD2 will not send a data barrier for the transaction, ext4 issues its own flush.

## State and persistence behavior
Persistent ordering is the whole purpose of this file. No-journal mode explicitly writes metadata buffers, inode table blocks, and parent directory metadata to reduce crash windows for new entries. Journal mode persists data before metadata commit and relies on JBD2 or fast commit to make inode changes durable. `file_check_and_advance_wb_err()` advances per-file writeback error cursors so delayed I/O errors are reported once.

## Dependencies and integration points
It integrates VFS fsync, ext4 metadata buffer tracking, inode state flags, JBD2 transactions, fast commit, block-device flushes, and tracepoints. It is referenced by `ext4_file_operations.fsync` in `file.c`.

## Risks and test signals
Risks include missing parent syncs in no-journal mode, overusing fast commit for unsupported inode types, incorrect datasync versus full-sync tid selection, missing flushes when barriers are enabled, and lost writeback errors. Test signals include fsync/fdatasync on regular files, directories, symlinks and special files, no-journal newly-created files with nested fresh parents, barrier and nobarrier mounts, external journal behavior, fast-commit enabled/disabled/ineligible paths, forced shutdown/emergency state, and delayed writeback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/fsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/hash.c -->
# sources/distributed-fs/ceph-client/fs/ext4/hash.c

## Purpose
`hash.c` computes ext4 directory-entry hashes for htree indexed directories. It supports legacy signed/unsigned hashes, half-MD4, TEA, SipHash for encrypted+casefolded directories with keys, optional Unicode casefolding, and seed-based hash randomization.

## Important APIs, types, and functions
The external entry point is `ext4fs_dirhash`. Internal algorithms include `TEA_transform`, `half_md4_transform`, `dx_hack_hash_unsigned`, `dx_hack_hash_signed`, `str2hashbuf_signed`, `str2hashbuf_unsigned`, and `__ext4fs_dirhash`. Hash mode and output live in `struct dx_hash_info`, including `hash_version`, `seed`, `hash`, and `minor_hash`.

## Control flow
`ext4fs_dirhash()` optionally casefolds the input name with the superblock Unicode map when the directory is casefolded and either unencrypted or the encryption key is present. If casefolding fails, it hashes the opaque byte sequence. `__ext4fs_dirhash()` initializes the default MD4-like seed, replaces it with a nonzero caller seed when supplied, dispatches by hash version, and clears the low bit of the major hash. It avoids returning the htree EOF sentinel. SipHash requires an fscrypt key and returns `-EINVAL` with a warning when unavailable.

## State and persistence behavior
Directory hashes are not separately persisted here, but they determine htree lookup/split ordering and therefore persistent directory layout. The hash seed can come from the superblock. Unicode casefolding and encryption-key availability affect whether semantically equivalent names hash identically or as opaque bytes.

## Dependencies and integration points
This file integrates with ext4 directory indexing, fscrypt filename SipHash, Unicode normalization/casefolding, superblock encoding state, and warning paths. It is used by directory lookup/allocation code, including Orlov top-directory placement in `ialloc.c`.

## Risks and test signals
Risks include signedness compatibility regressions, Unicode fallback mismatches, SipHash use without keys, hash-version validation, sentinel handling, PATH_MAX allocation failure for casefolding, and cross-endian seed interpretation. Test signals include all hash versions with known vectors, signed versus unsigned legacy names above ASCII, encrypted casefolded directories with and without keys, invalid hash versions, zero-length support probes, htree splits, and Unicode normalization/casefold collision cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ialloc.c -->
# sources/distributed-fs/ceph-client/fs/ext4/ialloc.c

## Purpose
`ialloc.c` manages ext4 inode allocation and deallocation. It reads and validates inode bitmaps, marks inodes used during normal creation and fast-commit replay, frees inodes, chooses allocation groups with Orlov/flex_bg heuristics, initializes new inode metadata/xattrs/ACL/security/encryption state, validates orphan-list entries at mount recovery, counts inode/directory totals, and zeroes lazy inode tables.

## Important APIs, types, and functions
Public functions include `ext4_mark_bitmap_end`, `ext4_end_bitmap_read`, `ext4_free_inode`, `ext4_mark_inode_used`, `__ext4_new_inode`, `ext4_orphan_get`, `ext4_count_free_inodes`, `ext4_count_dirs`, and `ext4_init_inode_table`. Internal helpers include `ext4_validate_inode_bitmap`, `ext4_read_inode_bitmap`, `get_orlov_stats`, `find_group_orlov`, `find_group_other`, `recently_deleted`, `find_inode_bit`, and `ext4_xattr_credits_for_new_inode`. `struct orlov_stats` summarizes free clusters, free inodes, and used directories for block groups or flex groups.

## Control flow
Bitmap reads validate group descriptors, bitmap block ranges, uninitialized inode bitmap flags, uptodate state, checksums, and corruption markers. `ext4_free_inode()` verifies the inode has no extra references or links, clears in-memory inode state before freeing the bitmap bit, journals the inode bitmap and group descriptor, updates free inode and used directory counters, flex group counters, checksums, and dirty metadata.

Allocation starts in `__ext4_new_inode()`: reject deleted parent directories and emergency state, allocate a VFS inode, initialize owner/project/quota/encryption prerequisites, estimate xattr credits if it must start its own transaction, choose a target group from goal, Orlov, or parent-local search, and scan candidate groups for a free inode bit while avoiding corrupt bitmaps and recently deleted inodes in no-journal mode. Once it claims a bit, it journals bitmap and group descriptor changes, initializes uninitialized block/inode bitmap state if needed, updates descriptor counters and checksums, decrements global/flex counters, initializes ext4 inode fields, inserts the inode into the inode cache, seeds metadata checksums, sets inline-data/extent flags, allocates quota, writes encryption/ACL/security xattrs, initializes the extent tree when appropriate, updates fsync transaction state, and marks the inode dirty. Failure paths drop quota, clear links, unlock new inode state, and iput the inode.

`ext4_mark_inode_used()` is a replay-oriented direct marker that sets an inode bitmap bit, syncs it, initializes block bitmaps if needed, and updates group descriptor counts without a normal handle. `ext4_orphan_get()` verifies orphan inode numbers against bitmap state, inode loadability, truncatability, and next-orphan bounds. `ext4_init_inode_table()` serializes with allocation using `alloc_sem`, zeroes unused inode-table blocks, flushes if requested, and marks the group inode table zeroed.

## State and persistence behavior
Persistent state includes inode bitmap bits, group descriptor free/used counts and flags, inode/table checksums, inode table zeroed state, new inode raw metadata, quota allocation, ACL/security/encryption xattrs, and orphan-list validation. Runtime state includes group corruption flags, per-cpu counters, flex-group atomics, parent `i_last_alloc_group`, inode checksum seeds, and inode state flags such as `EXT4_STATE_NEW` and `EXT4_STATE_MAY_INLINE_DATA`. Fast-commit replay disables some bitmap corruption checks and uses `ext4_mark_inode_used()` to force durable bitmap state.

## Dependencies and integration points
The file integrates with JBD2 handles, ext4 group descriptors, inode/block bitmap checksum helpers, mballoc group info, quota, fscrypt, POSIX ACLs, LSM/security xattrs, integrity xattrs, extents, inline data, orphan recovery, lazy inode-table initialization, hash-based directory placement, and tracepoints.

## Risks and test signals
Risks include bitmap checksum false positives/negatives, races with lazy inode-table initialization, double allocation after stale group counters, incorrect flex_bg counter updates, replay paths bypassing journaling, leaked quota on late failure, orphan-list infinite loops, recent-deletion reuse in no-journal mode, owner/project inheritance errors, and insufficient transaction credits for inherited xattrs. Test signals include inode create/free under heavy concurrency, directory-heavy Orlov allocation, flex_bg and non-flex filesystems, group descriptor checksum and uninit flags, no-journal recent deletion, ENOSPC and EIO injection at every allocation stage, fscrypt/ACL/security/project inheritance, fast-commit replay inode creation, orphan recovery with bad inode numbers and truncate-ineligible inodes, lazyinit races, and counter/checksum validation after fsck.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/ialloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/indirect.c -->
# sources/distributed-fs/ceph-client/fs/ext4/indirect.c

## Purpose
`indirect.c` implements block mapping, allocation, truncation, and hole punching for legacy non-extent ext4 inodes that use direct, single-indirect, double-indirect, and triple-indirect block pointers. Extent-mapped inodes use other code; this file preserves compatibility for old-format files and special cases that cannot use extents.

## Important APIs, types, and functions
The central helper type is `Indirect`, holding a pointer slot, saved key, and containing buffer. Public functions are `ext4_ind_map_blocks`, `ext4_ind_trans_blocks`, `ext4_ind_truncate`, and `ext4_ind_remove_space`. Key helpers include `ext4_block_to_path`, `ext4_get_branch`, `ext4_find_near`, `ext4_find_goal`, `ext4_blks_to_allocate`, `ext4_alloc_branch`, `ext4_splice_branch`, `ext4_ind_trunc_restart_fn`, `ext4_ind_truncate_ensure_credits`, `all_zeroes`, `ext4_find_shared`, `ext4_clear_blocks`, `ext4_free_data`, and `ext4_free_branches`.

## Control flow
Lookup begins by translating a logical block to a path of inode/indirect offsets. `ext4_get_branch()` walks existing pointers under `i_data_sem`, reading and validating indirect blocks, and stops at a missing pointer or I/O/corruption error. If the full path exists, `ext4_ind_map_blocks()` returns the physical block and extends the mapping across contiguous pointers up to the indirect-block boundary. If lookup finds a hole and creation is not requested, it reports the logical hole length. If creation is requested, it rejects bigalloc non-extent allocation, builds an `ext4_allocation_request`, picks a locality goal, calculates data and metadata blocks to allocate, allocates a disconnected branch of indirect/data blocks, then splices the missing pointer atomically into the existing tree and marks the inode or parent indirect block dirty.

Truncation and range removal locate shared partial branches, free data runs bottom-up, clear pointer slots only when journaling credits are available, and recursively free indirect subtrees. Large truncates can restart transactions through `ext4_ind_truncate_ensure_credits`, temporarily dropping `i_data_sem` after marking dirty metadata and discarding preallocations. `ext4_ind_truncate()` removes everything beyond `i_size`, updates `i_disksize` under orphan-list protection, clears extent-status cache past the truncation point, handles direct pointers, shared branch tails, and whole indirect subtrees. `ext4_ind_remove_space()` handles punch-hole ranges that may start/end at different pointer-tree levels and frees start/end partial branches plus full middle subtrees.

## State and persistence behavior
Persistent state consists of inode `i_data` pointer slots, indirect block contents, block/inode dirty metadata, allocation bitmaps, revoke records, and `i_disksize`. Allocation prepares new branches off-tree so failures free unreachable blocks without corrupting the existing tree. Splicing the final pointer is the commit point. Truncation relies on orphan-list protection from higher layers and writes pointer zeroing plus bitmap frees in journaled order; metadata blocks are freed with `EXT4_FREE_BLOCKS_METADATA` and `FORGET` so journal replay cannot resurrect reallocated indirect blocks.

## Dependencies and integration points
This file depends on ext4 journaling helpers, mballoc (`ext4_mb_new_blocks`, `ext4_new_meta_blocks`, `ext4_free_blocks`), block validity checks, buffer-head I/O, extent-status cache invalidation, DAX headers only indirectly, truncate helpers, inode locks, and ext4 tracepoints. It is called by the generic ext4 mapping/truncate/fallocate paths when `EXT4_INODE_EXTENTS` is absent.

## Risks and test signals
Risks include stale chain verification after concurrent truncate, indirect block self-reference or invalid block pointers, journal credit exhaustion during deep truncates, revoke omissions causing journal replay corruption, incorrect hole-length reporting, 32-bit physical block limits for legacy pointers, bigalloc rejection gaps, and off-by-one range removal across direct/indirect boundaries. Test signals include mapping direct/single/double/triple indirect blocks, contiguous map coalescing at boundaries, allocation failure cleanup, concurrent truncate and map-blocks stress, bigalloc non-extent corruption handling, punch holes within one level and across levels, crash recovery after truncation of indirect metadata, circular indirect block detection, invalid pointer injection, and fsck validation of freed metadata/data blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/indirect.c -->
