# subset-b-005651 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/inline.c -->
# sources/distributed-fs/ceph-client/fs/ext4/inline.c

## Purpose
`inline.c` implements ext4 inline-data support for regular files, directories, and symlinks. Inline data stores the first `EXT4_MIN_INLINE_DATA_SIZE` bytes in the raw inode `i_block[]` area and, when extra inode space is available, stores the remaining bytes in the in-inode xattr named `system.data`. The file owns detection, sizing, creation, update, read, write, truncation, directory entry operations, symlink reads, iomap reporting, and conversion from inline representation to normal extent or indirect block representation.

This file is the bridge between ext4's inode/xattr machinery and higher-level VFS operations that expect folios, directory entries, symlink strings, or iomap extents. It protects the inline/xattr state with `EXT4_I(inode)->xattr_sem`, protects block mapping changes with `i_data_sem`, and journals every persistent inode-table mutation through JBD2 handles.

## Important APIs, Types, and Functions
The persistent inline format is identified by the inode flag `EXT4_INODE_INLINE_DATA`, in-memory fields `EXT4_I(inode)->i_inline_off` and `i_inline_size`, and the in-inode xattr `EXT4_XATTR_SYSTEM_DATA` with name `"data"` under `EXT4_XATTR_INDEX_SYSTEM`. `EXT4_MIN_INLINE_DATA_SIZE` is the fixed inline capacity in `i_block[]`, while `EXT4_INLINE_DOTDOT_OFFSET` and `EXT4_INLINE_DOTDOT_SIZE` define the compact inline-directory encoding for the parent inode number.

Sizing and discovery are handled by `ext4_get_max_inline_size()`, `get_max_inline_xattr_value_size()`, and `ext4_find_inline_data_nolock()`. The sizing logic scans in-inode xattrs, accounts for the xattr header, entry table, value offsets, and the mandatory empty gap, and returns zero when there is no room for a `system.data` entry. Discovery is intentionally lockless only for iget-time initialization, before the inode is visible to concurrent users.

Raw inline data movement is centralized in `ext4_read_inline_data()` and `ext4_write_inline_data()`. These copy between caller buffers, raw inode `i_block[]`, and the xattr value region. Creation and growth use `ext4_create_inline_data()`, `ext4_update_inline_data()`, and `ext4_prepare_inline_data()`, which obtain journal write access to the inode-table buffer, set or update the xattr entry, maintain `i_inline_off/i_inline_size`, clear the extents flag on inline creation, set `EXT4_INODE_INLINE_DATA`, and mark the inode location dirty.

Conversion and destruction are handled by `ext4_destroy_inline_data_nolock()`, `ext4_convert_inline_data_to_extent()`, `ext4_da_convert_inline_data_to_extent()`, `ext4_convert_inline_data_nolock()`, and the public `ext4_convert_inline_data()`. These paths either move inline data into the page cache for delayed allocation writeback or allocate a real first data block and copy file/directory contents into it.

VFS-facing file operations include `ext4_readpage_inline()`, `ext4_generic_write_inline_data()`, `ext4_try_to_write_inline_data()`, and `ext4_write_inline_data_end()`. Directory operations include `ext4_try_create_inline_dir()`, `ext4_try_add_inline_entry()`, `ext4_find_inline_entry()`, `ext4_delete_inline_entry()`, `empty_inline_dir()`, `ext4_inlinedir_to_tree()`, and `ext4_read_inline_dir()`. Other exported integration points are `ext4_read_inline_link()`, `ext4_get_first_inline_block()`, `ext4_inline_data_iomap()`, `ext4_inline_data_truncate()`, and `ext4_destroy_inline_data()`.

## Control Flow
Inline file reads take `xattr_sem` in read mode, verify the inode still has inline data, read the first folio through `ext4_read_inline_folio()`, and zero/mark uptodate later folios because inline data can only occupy page zero. The first folio path reads the inode table block, copies at most `min(inline_size, i_size)` bytes from `i_block[]` and the xattr value, zeros the tail, and unlocks the folio in `ext4_readpage_inline()`.

Buffered writes first check whether `EXT4_STATE_MAY_INLINE_DATA` is set. If the requested end offset still fits in the current or maximum inline capacity, `ext4_generic_write_inline_data()` starts a small inode transaction, prepares or grows inline storage, grabs folio zero, reads current inline contents if needed, and returns with the folio locked and the transaction current. `ext4_write_inline_data_end()` then copies bytes from the folio back into the raw inode/xattr value, clears folio dirty state so writeback does not process it as block data, updates `i_size`, marks the inode dirty after dropping the folio lock, stops the journal handle, and truncates any failed extension.

When inline data no longer fits, non-delalloc writes call `ext4_convert_inline_data_to_extent()`: it starts a write transaction, locks xattrs, reads inline data into folio zero, destroys the inline xattr/state, maps a real block, optionally obtains journal access for data journaling, commits the write to the folio buffers, and handles ENOSPC retry/orphan recovery. Delayed allocation writes use `ext4_da_convert_inline_data_to_extent()`, which reads the inline data into the page cache, prepares delayed allocation buffers through `ext4_da_get_block_prep()`, marks the folio dirty/uptodate, clears `EXT4_STATE_MAY_INLINE_DATA`, and lets `ext4_da_writepages()` perform real allocation later.

Inline directory creation uses only compact `..` storage in the first four bytes of `i_block[]`; `.` is synthesized when reading. Adding entries first tries the free space after the compact `..` area in `i_block[]`, then grows into xattr value space with `ext4_update_inline_dir()`, then converts the directory to a real data block when inline space is exhausted. Directory iteration builds fake `.` and `..` dirents, remaps compact inline offsets to normal directory cookies, validates entries with `ext4_check_dir_entry()`, and uses i_version cookies to rescan if the directory changed during readdir. Htree integration in `ext4_inlinedir_to_tree()` hashes or reads stored hashes for the synthesized and real dirents before storing them in the dx tree.

Truncation starts a journal transaction, locks xattrs, adds the inode to the orphan list, updates `i_disksize`, optionally clears stale extent status when inline writes were converted to delayed allocation, shrinks the xattr value through `ext4_xattr_ibody_set()`, zeroes the truncated tail in `i_block[]`, adjusts `i_inline_size`, marks times/dirty state, and removes the orphan record when safe. Full conversion through `ext4_convert_inline_data_nolock()` reads inline bytes to memory, validates inline directory entries before modifying the inode, destroys inline state, allocates logical block zero, and either copies regular/symlink bytes or initializes a directory block with parent information.

## State and Persistence Behavior
Inline bytes persist in two on-disk places: raw inode `i_block[]` and the value of the `system.data` in-inode xattr. The in-memory offsets only cache where that xattr entry lives inside the inode table record; all durable updates go through the inode-table buffer and xattr helpers. Inline creation clears `EXT4_INODE_EXTENTS` and sets `EXT4_INODE_INLINE_DATA`; destruction clears inline state and can reinitialize an extent tree for regular files, directories, or symlinks when the filesystem supports extents.

Crash consistency relies on JBD2 transactions, `ext4_mark_iloc_dirty()`, orphan-list protection for failed extensions/truncates, and fast-commit tracking via `ext4_fc_track_inode()` and related range calls reached through mapping paths. The delayed allocation conversion path is intentionally two-phase: it may leave `EXT4_INODE_INLINE_DATA` present while `EXT4_STATE_MAY_INLINE_DATA` is cleared and the page cache is dirty; later writeback finishes conversion. `ext4_convert_inline_data()` detects this transitional state and flushes the mapping before attempting a synchronous conversion.

## Dependencies and Integration Points
`inline.c` depends heavily on ext4 xattrs (`ext4_xattr_ibody_find/set/get`, `xattr_sem`, xattr layout macros), inode table access (`ext4_get_inode_loc`, `ext4_raw_inode`, `ext4_mark_iloc_dirty`), journaling (`ext4_journal_start`, `ext4_journal_get_write_access`, `ext4_handle_dirty_metadata`), block mapping (`ext4_map_blocks`, `ext4_block_write_begin`, delayed allocation helpers), directory helpers (`ext4_search_dir`, `ext4_find_dest_de`, `ext4_insert_dentry`, `ext4_check_dir_entry`, dx htree APIs), folio/page-cache helpers, iomap, fscrypt-aware symlink termination, and fast commit/orphan/truncate support.

The major integration callers are in inode write/read/truncate/page-fault paths, directory creation/link/unlink/readdir paths, fiemap/iomap reporting, symlink readlink handling, and iget-time inode initialization. `inode.c` calls inline conversion before mmap write faults and size changes that exceed inline capacity.

## Risks
Inline data correctness depends on xattr geometry. Miscomputed entry offsets, free-space calculations, or stale `i_inline_off` values can overwrite adjacent inode fields or xattrs. The code mitigates this by recalculating inline data after locking xattrs and by validating xattr and directory entries, but many paths still assume `i_inline_size` is sane and contain `BUG_ON()` checks.

Concurrency risk is concentrated around conversion. Inline data can be converted by another writer between preparation and completion, so write paths recheck flags under `xattr_sem`. Delayed allocation conversion intentionally creates a transitional state; missing flushes or stale extent-status entries could expose data loss or block-accounting errors. Directory offset emulation is subtle because inline directories do not physically store full `.` and `..` dirents, so readdir cookies and htree export behavior are easy regression points.

Security and integrity risks include corrupted xattr entries with external xattr inodes, malformed inline directory records, stale data exposure when conversion or partial writes fail, and emergency/shutdown paths that skip writes. The code reports filesystem corruption with `-EFSCORRUPTED` and uses orphan cleanup on failure paths, but these paths require focused crash and fault-injection testing.

## Test Signals
Useful tests include creating tiny regular files, symlinks, and directories with inline data enabled; growing files across inline capacity under normal, delayed allocation, dioread_nolock, data=journal, encrypted, and ENOSPC conditions; truncating inline data within `i_block[]`, within the xattr value, and to zero; punching or setattr-growing inline files after conversion; readdir and htree lookup of inline directories before and after conversion; adding and deleting entries until inline space is exhausted; fsck validation after injected crashes during conversion/truncation; malformed xattr and inline dir fuzzing; fiemap/iomap on inline files; and mmap write faults that trigger `ext4_convert_inline_data()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/inline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/inode-test.c -->
# sources/distributed-fs/ceph-client/fs/ext4/inode-test.c

## Purpose
`inode-test.c` is a KUnit suite for ext4 inode timestamp decoding. It verifies that `ext4_decode_extra_time()` correctly reconstructs `struct timespec64` seconds and nanoseconds from the legacy 32-bit inode timestamp field plus the ext4 extra timestamp bits. The tested cases are derived from the timestamp range table in `Documentation/filesystems/ext4/inodes.rst`.

The file is intentionally small and self-contained. It does not construct a filesystem, mount ext4, or mutate persistent state; it focuses on the pure decoding contract that inode load paths in `inode.c` use through macros such as `EXT4_INODE_GET_CTIME()`, `EXT4_INODE_GET_ATIME()`, and `EXT4_INODE_GET_MTIME()`.

## Important APIs, Types, and Functions
The central type is `struct timestamp_expectation`, which stores a descriptive case name, expected `struct timespec64`, the raw extra-bit value, whether the most significant bit of the 32-bit timestamp is set, and whether the lower or upper bound of that 32-bit range should be used.

The `test_data[]` table covers negative 32-bit timestamps, nonnegative 32-bit timestamps, the two extra seconds bits used to extend ext4 timestamps past 2038, and nanosecond extraction from the high bits in the extra field. Constants such as `LOWER_MSB_0`, `UPPER_MSB_0`, `LOWER_MSB_1`, `UPPER_MSB_1`, and `MAX_NANOSECONDS` encode boundary raw values.

`timestamp_expectation_to_desc()` provides parameter names for KUnit output. `KUNIT_ARRAY_PARAM(ext4_inode, test_data, timestamp_expectation_to_desc)` generates the parameter set. `get_32bit_time()` maps the `msb_set` and `lower_bound` booleans to a representative signed 32-bit timestamp value. `inode_test_xtimestamp_decoding()` is the actual test body, and the suite is registered through `kunit_test_suites(&ext4_inode_test_suite)`.

## Control Flow
KUnit runs `inode_test_xtimestamp_decoding()` once for each row in `test_data[]`. For a row, the test derives the lower 32-bit timestamp with `get_32bit_time()`, converts both the lower timestamp and extra field to little-endian with `cpu_to_le32()`, and calls `ext4_decode_extra_time()`.

The test then compares decoded `tv_sec` and `tv_nsec` against the expected values using `KUNIT_EXPECT_EQ_MSG()`. The failure message includes the case name, msb flag, lower-bound flag, and extra bits, which makes boundary failures diagnosable without reading the table index.

## State and Persistence Behavior
There is no persistent state and no runtime filesystem state. All inputs are compile-time constants. The only state produced is KUnit test result state. Endianness conversion is included in the call site so the test exercises the same little-endian ABI shape as on-disk ext4 inode fields.

The expectations encode the ext4 timestamp persistence contract: the raw inode stores a 32-bit seconds field and an extra field whose low two relevant seconds bits extend time ranges while other bits encode nanoseconds. The suite verifies that ranges wrap from pre-1970 values through 2038, 2106, 2174, 2310, 2378, and 2446 boundaries as documented.

## Dependencies and Integration Points
The file includes KUnit, kernel time types, and `ext4.h`. Its only ext4 functional dependency is `ext4_decode_extra_time()`, which is normally consumed by inode deserialization macros in `inode.c`. It integrates with the kernel's KUnit module infrastructure via `kunit_test_suites`, `MODULE_DESCRIPTION`, and `MODULE_LICENSE`.

This test is a direct guard for inode timestamp reads. If ext4 changes the timestamp encoding macros, expands valid ranges, or modifies bit layout for extra inode timestamp fields, this table should be updated in lockstep with the documentation and decoder.

## Risks
The main risk is incomplete coverage rather than operational risk. The suite tests representative boundaries and nanosecond maximums, but it does not exhaustively test every combination of extra seconds bits and nanosecond bits. It also tests only decoding, not encoding through raw inode writeback macros. A mismatch between documentation and implementation could survive if both the selected test values and the decoder share an incorrect assumption outside the boundaries listed here.

Because `extra_bits` is a raw `u32`, rows such as `0xFFFFFFFF` test that unrelated high bits still produce `MAX_NANOSECONDS`, but the suite does not validate rejection or sanitization behavior because `ext4_decode_extra_time()` is a decoder, not a validator.

## Test Signals
Expected signals are parameterized KUnit pass/fail entries under the suite name `ext4_inode_test`. High-value regressions include off-by-one seconds at signed 32-bit boundaries, wrong wrap behavior when the low or high extra seconds bit is set, endian mistakes, nanoseconds exceeding `(1 << 30) - 1`, and divergence from the timestamp table in ext4 inode documentation. Complementary coverage would add encode/decode round trips through raw inode macros and randomized valid extra-bit combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/inode-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/inode.c -->
# sources/distributed-fs/ceph-client/fs/ext4/inode.c

## Purpose
`inode.c` is the primary ext4 inode implementation. It owns inode checksums, inode eviction, block mapping, buffered writes, delayed allocation, writeback, DAX/iomap integration, truncate and hole punching, raw inode read/write serialization, iget validation, setattr/getattr, transaction credit estimation, inode dirtying, data-journaling mode transitions, and mmap write faults.

The file sits at the center of ext4's VFS integration. It translates logical file offsets into disk blocks, coordinates page-cache folios and buffer heads with extent or indirect mapping backends, maintains crash-consistent inode metadata through JBD2, and enforces ext4 feature constraints such as inline data, extents, project quotas, fscrypt, fsverity, DAX, fast commit, bigalloc, and huge files.

## Important APIs, Types, and Functions
Checksum helpers are `ext4_inode_csum()`, `ext4_inode_csum_verify()`, and `ext4_inode_csum_set()`. Lifecycle and identity helpers include `ext4_evict_inode()`, `ext4_inode_is_fast_symlink()`, `ext4_get_inode_loc()`, `ext4_get_fc_inode_loc()`, `__ext4_iget()`, `ext4_set_inode_flags()`, `ext4_set_inode_mapping_order()`, and `ext4_get_projid()`.

Block mapping is centered on `ext4_map_blocks()`, with `ext4_map_query_blocks()` for lookup/cache population, `ext4_map_create_blocks()` for allocation or unwritten conversion, `_ext4_get_block()`, `ext4_get_block()`, `ext4_get_block_unwritten()`, `ext4_getblk()`, `ext4_bread()`, and `ext4_bread_batch()`. The mapping layer uses `struct ext4_map_blocks`, extent-status cache entries, `i_data_sem`, and either `ext4_ext_map_blocks()` or `ext4_ind_map_blocks()` depending on the inode format.

Buffered write support includes `ext4_block_write_begin()`, `ext4_write_begin()`, `ext4_write_end()`, `ext4_journalled_write_end()`, `ext4_da_write_begin()`, `ext4_da_write_end()`, and `ext4_da_do_write_end()`. Delayed allocation support uses `ext4_da_reserve_space()`, `ext4_da_release_space()`, `ext4_da_update_reserve_space()`, `ext4_da_map_blocks()`, `ext4_da_get_block_prep()`, and writeback state in `struct mpage_da_data`.

Writeback and I/O submission are implemented through `mpage_prepare_extent_to_map()`, `mpage_map_one_extent()`, `mpage_map_and_submit_extent()`, `mpage_map_and_submit_buffers()`, `mpage_submit_folio()`, `ext4_do_writepages()`, `ext4_writepages()`, `ext4_normal_submit_inode_data_buffers()`, and `ext4_dax_writepages()`. Address-space operations are selected by `ext4_set_aops()` from `ext4_aops`, `ext4_da_aops`, `ext4_journalled_aops`, and `ext4_dax_aops`.

Iomap and direct-I/O/DAX support are provided by `ext4_set_iomap()`, `ext4_iomap_alloc()`, `ext4_iomap_begin()`, `ext4_iomap_begin_report()`, `ext4_iomap_ops`, `ext4_iomap_report_ops`, and `ext4_iomap_swap_activate()`. Atomic-write support appears in `ext4_map_blocks_atomic_write()` and `ext4_map_blocks_atomic_write_slow()`, which ensure a single contiguous mapping and may force a transaction commit for mixed mappings.

Truncate, zeroing, and punching are handled by `ext4_block_zero_eof()`, `ext4_zero_partial_blocks()`, `ext4_update_disksize_before_punch()`, `ext4_truncate_page_cache_block_range()`, `ext4_punch_hole()`, and `ext4_truncate()`. Raw inode writeback and dirtying use `ext4_fill_raw_inode()`, `ext4_do_update_inode()`, `ext4_write_inode()`, `ext4_mark_iloc_dirty()`, `ext4_reserve_inode_write()`, `ext4_expand_extra_isize()`, `__ext4_mark_inode_dirty()`, and `ext4_dirty_inode()`.

## Control Flow
The read/lookup side of block mapping first asks the extent-status cache. Written and unwritten cache hits return physical mappings; delayed or hole hits return no mapping with a useful run length. Cache misses take `i_data_sem` in read mode and query the extent or indirect tree, then cache the result. Allocation callers set `EXT4_GET_BLOCKS_CREATE`; if lookup did not find a sufficient mapped extent, `ext4_map_blocks()` tracks the inode for fast commit, takes `i_data_sem` in write mode, allocates through the extent or indirect backend, optionally zeroes newly allocated blocks before exposing them in the extent-status tree, updates ordered-data tracking, and records the modified logical range.

Buffered non-delalloc writes begin by handling inline data, grabbing and preparing a folio, starting a journal transaction, allocating or mapping buffers with `ext4_block_write_begin()`, obtaining data-journal write access when required, and returning the locked folio. Write end commits copied bytes with `block_write_end()` or journalled buffer dirtying, updates `i_size` under the folio lock, marks the inode dirty after unlock, adds the inode to the orphan list if blocks were allocated past the final size, stops the transaction, and truncates failed extensions.

Delayed allocation writes reserve quota and free-space clusters when buffers are dirtied rather than allocating physical blocks immediately. `ext4_da_get_block_prep()` maps existing written/unwritten extents or inserts delayed extents into the extent-status tree. `ext4_da_write_end()` updates `i_size` and sometimes `i_disksize` if the final block is already mapped; otherwise writeback later advances `i_disksize` after submitting I/O.

Writeback is a two-phase scanner. `ext4_do_writepages()` first submits already mapped dirty folios without starting metadata transactions. It then loops over extents of delayed or unwritten buffers, starts a transaction sized for a bounded chunk, maps or converts one extent, updates buffer-head state, submits bios through `ext4_io_submit`, tracks unwritten extent conversion through `io_end`, updates `i_disksize` after I/O submission, and retries on transient ENOSPC/EAGAIN where possible. Data=journal mode disables delayed mapping and instead commits or checkpoints journalled data buffers.

Iomap direct I/O and DAX begin with a logical range, trim the request to direct-I/O limits, allocate blocks when writing, and return `IOMAP_MAPPED`, `IOMAP_UNWRITTEN`, `IOMAP_DELALLOC`, `IOMAP_HOLE`, or `IOMAP_INLINE` for reporting paths. Direct I/O allocates unwritten extents inside existing `i_size` for extent-based files to avoid stale data exposure; holes in indirect files can return `-ENOTBLK` to force buffered fallback. Atomic writes require the full requested mapping and, for bigalloc mixed mappings, loop through zeroing/allocation until one contiguous mapping is available.

Inode load through `__ext4_iget()` validates inode numbers, reads the inode-table block, checks extra inode size, precomputes checksum seed, verifies metadata checksum, decodes mode, ids, project id, links, flags, size, blocks, timestamps, i_version, xattrs, inline data, extent/indirect metadata, fast symlink data, and feature-dependent flags. It rejects impossible flag combinations such as inline data plus extents and assigns inode operations, file operations, address-space operations, cached symlink data, ACL cache state, and folio order. Failure marks the inode bad through `iget_failed()`.

Setattr handles permission and quota preparation, uid/gid transfer in a journal transaction, size changes, inline conversion when a new size exceeds inline capacity, ordered truncate waits, DAX layout breaking, EOF tail zeroing, orphan-list protection for shrink, synchronized updates of `i_size` and `i_disksize` under `i_data_sem`, page-cache truncation, and `ext4_truncate()` invocation even when size is unchanged but preallocations may need removal. Mmap write faults call `ext4_convert_inline_data()`, use delayed allocation when enabled and safe, otherwise allocate/mapping buffers in a journal transaction and return a locked, stable folio.

## State and Persistence Behavior
Durable inode state lives in ext4 raw inode records: mode, uid/gid/projid, links, timestamps including extra fields, flags, `i_blocks`, `i_file_acl`, size/disksize, generation, i_version, device numbers or `i_block[]`, xattr headers, checksums, and optional high fields. `ext4_fill_raw_inode()` serializes in-memory state to this format under `i_raw_lock`; `ext4_do_update_inode()` journals the inode-table buffer, updates lazytime neighbors in the same inode block when possible, sets the large_file feature if required, and records fsync transaction ids.

In-memory state includes `i_disksize`, extent-status cache, delayed allocation reservations, preallocations, `jinode`, fast-commit lists, xattr/inline offsets, inode flags mirrored into VFS flags, and page-cache buffer-head state. `i_size` is the VFS-visible size, while `i_disksize` is the crash-consistent on-disk size boundary. Many paths update them under `i_data_sem` to avoid writeback races.

Crash consistency uses JBD2 handles, metadata checksums, ordered-data write tracking, orphan-list records for truncates and failed extensions, unwritten extents for direct I/O and dioread_nolock writes, fast-commit tracking of inode and logical ranges, and transaction credit estimates from `ext4_meta_trans_blocks()`, `ext4_chunk_trans_extent()`, and `ext4_chunk_trans_blocks()`. No-journal mode writes inode buffers directly, with metadata buffer tracking through `i_metadata_bhs`.

## Dependencies and Integration Points
This file integrates with the VFS inode, address_space, folio, writeback, iomap, DAX, mmap fault, setattr/getattr, quota, fscrypt, fsverity, fsnotify/statx, and swapfile APIs. Internally it depends on ext4 extents, indirect blocks, mballoc, extent-status cache, xattrs, ACLs, inline data, fast commit, orphan handling, truncate helpers, block validity checks, checksums, superblock feature bits, and JBD2.

Important external entry points include address-space operations selected by `ext4_set_aops()`, iomap ops consumed by direct I/O, fiemap, DAX, bmap, and swap activation, inode operations for file/directory/symlink/special nodes assigned during iget, and exported helpers used by directory, xattr, truncate, and fast-commit code. KUnit static stubbing is present in `ext4_issue_zeroout()`, allowing tests to replace device zeroing behavior.

## Risks
The highest-risk areas are race-sensitive state transitions: delayed allocation to mapped extents, unwritten to written conversion after I/O, inline data conversion, truncate or punch-hole versus writeback, DAX layout breaking, mmap page faults without `i_rwsem`, and data=journal buffer invalidation during commit. Incorrect lock ordering between folio locks, `i_data_sem`, `invalidate_lock`, xattr locks, journal handles, and writeback semaphores can deadlock or expose stale data.

Persistence risks include stale data exposure if newly allocated blocks are cached before zeroing, lost size updates if `i_disksize` is not advanced or shrunk in the right transaction, orphan-list omissions on failed extension/truncate, incorrect transaction credit estimates, and extent-status cache corruption when callers cache ranges without holding required locks. Feature interactions add risk: bigalloc cluster accounting, encrypted DIO alignment, fsverity writes past EOF, fast symlink `i_data` reuse, EA inode constraints, huge-file block counts, and atomic writes all have special-case invariants.

Error paths are intentionally conservative but complex. ENOSPC may retry after journal commits, some writeback failures invalidate dirty pages to avoid infinite loops, and emergency shutdown short-circuits most mutating paths. Corruption detection returns `-EFSCORRUPTED` or `-EFSBADCRC` for invalid inode numbers, checksums, block mappings, xattr blocks, flag combinations, fast symlink lengths, and unsupported feature combinations.

## Test Signals
High-value coverage includes buffered writes in ordered, writeback, journalled, and delayed allocation modes; direct I/O and DAX writes over holes, unwritten extents, EOF, and mixed mappings; atomic write statx reporting and allocation behavior; mmap write faults racing with truncate and fallocate; ENOSPC retries during writeback; bigalloc delayed reservation accounting; inline data conversion through write, setattr, and mmap; fscrypt direct I/O alignment and zeroout; fsverity writes past EOF; hole punch and truncate crash recovery with orphan cleanup; fast symlink iget validation; inode checksum failure injection; lazytime inode table neighbor updates; nojournal write_inode paths; and xfstests that stress dioread_nolock, unwritten conversion, extent-status cache consistency, and data journaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/inode.c -->
