# Group Research: group_79_9front_sources_os_plan9_9front_sys_src_cmd_ext4srv_ext4_c_sources_os__5e9b25a21d4a

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4.c

Public/ext4 service API layer for the 9front `ext4srv` implementation. It exposes mount/unmount, journal start/stop/recovery, transactions, file open/read/write/truncate/seek/remove/link/rename, metadata get/set, symlink/mknod support, recursive directory removal, directory creation/opening, and directory iteration.

Key behavior:
- Defines Plan 9-style global error strings and mountpoint locking macros wrapping optional OS locks.
- `ext4_mount` initializes CRC32C tables, the block device, filesystem superblock state, logical block size, and block cache.
- `ext4_umount` finalizes filesystem state, cleans/flashes cache, tears down block device state, and clears the mount’s filesystem pointer.
- `ext4_journal_start`, `ext4_journal_stop`, `ext4_recover`, `ext4_trans_start`, `ext4_trans_stop`, and `ext4_trans_abort` bridge normal file operations to the local JBD implementation when the filesystem has a journal.
- `ext4_generic_open2` is the central pathname walker and creator. It descends from the root inode, validates file type expectations, creates missing intermediate directories for `O_CREAT`, truncates regular files for `O_TRUNC`, and fills `ext4_file` state.
- `ext4_link`, `ext4_unlink`, `ext4_create_hardlink`, and `ext4_remove_orig_reference` maintain directory entries, `.`/`..`, htree parent pointers, and link counts.
- `ext4_fread` and `ext4_fwrite` translate file offsets to filesystem blocks, coalesce contiguous block IO, handle short inline symlinks, update positions/counts, and update inode size and mtime on writes.
- Directory operations use `ext4_dir_iter` and the lower directory layer; recursive removal walks depth-first, truncates entries, unlinks them, and frees inodes.

Notable dependencies:
- Core local modules: `ext4_fs`, `ext4_dir`, `ext4_dir_idx`, `ext4_inode`, `ext4_super`, `ext4_block_group`, `ext4_trans`, `ext4_journal`, `ext4_crc32`.
- Plan 9 runtime assumptions appear through `werrstr`, `time(nil)`, `utfrrune`, and Plan 9 error/style conventions.

Research notes:
- This is the main API surface consumed by `ext4srv.c` and related Plan 9 service glue.
- Read-only checks are mostly done at public mutation entry points and creation paths.
- The implementation intentionally does not support file growth through truncate; `ext4_ftruncate_no_lock` returns “space preallocation not supported” when requested size is greater than or equal to current size.
- `ext4_fread` handles sparse holes for an initial unaligned read, but the full-block coalescing path and final partial-block path do not consistently check `fblock == 0`; sparse full-block or trailing reads can read physical block 0 instead of zero-filling.
- `ext4_fwrite` contains an explicit FIXME around partial failure after append allocation. It may update inode size after a short write but leaves nuanced error reporting around `rr` suppressed.
- Several metadata getters open an `ext4_file` only to obtain an inode number and do not call `ext4_fclose`; since `ext4_fclose` only clears local fields, this is not a disk resource leak, but it is an API-state inconsistency.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_balloc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_balloc.c

Ext4 block allocation and freeing implementation. It maps block addresses to block groups, verifies and updates block bitmap checksums, allocates physical blocks near a goal, frees individual or ranged blocks, and updates superblock, block group, inode block counts, transaction revocation, and cache invalidation.

Key behavior:
- `ext4_balloc_get_bgid_of_block` and `ext4_balloc_get_block_of_bgid` convert between absolute block addresses and block group numbers, accounting for `first_data_block`.
- Metadata checksum support computes block bitmap CRC32C from the filesystem UUID seed and bitmap contents.
- `ext4_balloc_free_block` and `ext4_balloc_free_blocks` clear bitmap bits, update free counts and inode block counts, mark group descriptors dirty, revoke blocks from the transaction layer, and invalidate cache lines for freed LBAs.
- `ext4_balloc_alloc_block` first tries the requested goal, then nearby bits within the same group, then the rest of the group, then later block groups modulo the group count.
- `ext4_balloc_try_alloc_block` conditionally allocates a specific physical block and reports whether it was free.

Notable dependencies:
- Bitmap helpers from `ext4_bitmap.c`.
- Group descriptors via `ext4_block_group` and `ext4_fs`.
- Checksums via `ext4_crc32`.
- Transaction/cache interactions through `ext4_trans` and `ext4_bcache`.

Research notes:
- Bitmap checksum mismatches are warnings in most allocation/free paths; operations continue after logging rather than failing hard.
- Freeing range logic handles group crossing and warns if non-flex-bg continuous ranges cross block groups.
- Count updates are manual and distributed across superblock, block group descriptor, and inode fields; callers rely on these to keep allocation statistics coherent.
- The allocator is simple first-fit around a goal, not a locality-aware multi-block allocator comparable to Linux mballoc.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_bcache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_bcache.c

Dynamic buffer cache for ext4 logical blocks. It stores cached blocks in red-black trees by LBA and LRU id, tracks references, dirty buffers, writeback callbacks, and invalidation/drop behavior.

Key behavior:
- Initializes and finalizes `ext4_bcache` state with configured item count and block-sized item buffers.
- Uses `RB_GENERATE_INTERNAL` trees for fast lookup by logical block address and eviction by lowest LRU id.
- `ext4_bcache_find_get` returns a referenced buffer if already cached, removing it from LRU/dirty-ready lists while referenced.
- `ext4_bcache_alloc` creates a new `ext4_buf` plus data buffer when no cached buffer exists.
- `ext4_bcache_free` decrements the reference count, re-enters unreferenced buffers into LRU, flushes or dirty-lists dirty buffers, and drops invalidated or temporary buffers.
- `ext4_bcache_invalidate_lba` clears dirty/up-to-date state for cached buffers over an LBA range.

Notable dependencies:
- `ext4_blockdev.c` supplies flushing and cache-shaking logic.
- Red-black tree and singly-linked dirty-list macros are expected from included headers/environment.

Research notes:
- The cache counts allocated buffers through `ref_blocks`, despite the name implying referenced blocks.
- `ext4_bcache_drop_buf` decrements `ref_blocks` even if forcibly dropping a referenced buffer after warning; callers normally avoid that path.
- Cache cleanup iterates all LBA entries, flushes each buffer, then drops it.
- Dirty writeback is coupled to `bdev->cache_write_back`; when writeback is off, dirty buffers flush on last release.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_bcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_bitmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_bitmap.c

Small bitmap utility implementation used by block and inode allocation code.

Key behavior:
- `ext4_bmap_bits_free` clears a range of bitmap bits, optimizing byte-aligned middle ranges with `memset`.
- `ext4_bmap_bit_find_clr` scans a bitmap range for the first clear bit, first aligning to a byte boundary, then scanning whole bytes, then the tail bits.
- Reports no-space through both return value `-1` and `*no_space = true`.

Notable dependencies:
- Inline bit operations such as `ext4_bmap_bit_clr`, `ext4_bmap_bit_set`, and `ext4_bmap_is_bit_clr` come from headers.

Research notes:
- The helpers assume caller-provided range bounds are valid for the bitmap buffer.
- `ext4_bmap_bits_free` clears tail bits using bit indexes relative to the advanced byte pointer, which matches the local bit helper convention.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_block_group.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_block_group.c

Block group CRC16 helper for legacy ext4 group descriptor checksum support.

Key behavior:
- Defines a static 256-entry CRC16 lookup table.
- `ext4_bg_crc16` updates a CRC over an input buffer byte by byte and returns the 16-bit result.

Notable dependencies:
- Used by `ext4_fs_bg_checksum` when `EXT4_FRO_COM_GDT_CSUM` is active and metadata_csum is not used.

Research notes:
- This file contains only checksum computation; descriptor field access and checksum placement are handled in `ext4_fs.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_block_group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_blockdev.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_blockdev.c

Block device abstraction and cache integration layer. It wraps physical device callbacks, maps ext4 logical block IO to physical block IO, handles cached block get/release, byte-range IO, cache flushing, and writeback mode.

Key behavior:
- `ext4_block_init` opens the underlying block interface once and maintains a physical reference count.
- `ext4_block_set_lb_size` sets ext4 logical block size and computes logical block count from partition size.
- `ext4_block_get_noread` and `ext4_block_get` allocate cache buffers, optionally read backing storage, and mark buffers up-to-date.
- `ext4_block_set` releases a cached block back through `ext4_bcache_free`.
- `ext4_blocks_get_direct` and `ext4_blocks_set_direct` convert logical block addresses to physical block addresses using `part_offset`, logical block size, and physical block size.
- `ext4_block_writebytes` and `ext4_block_readbytes` implement unaligned byte IO with read-modify-write/read of edge physical blocks.
- `ext4_block_cache_shake`, `ext4_block_cache_flush`, and `ext4_block_cache_write_back` evict/flush LRU and dirty buffers.

Notable dependencies:
- `ext4_bcache` owns buffer objects and dirty/LRU structures.
- Physical IO is delegated to `struct ext4_blockdev_iface` callbacks (`open`, `close`, `bread`, `bwrite`, optional `lock`/`unlock`).

Research notes:
- Lock/unlock wrapper assertions assume the block interface lock callbacks cannot fail.
- Byte-range IO validates against `part_size`, but direct logical block IO relies on logical count checks at cached get time.
- `ext4_block_flush_buf` invokes optional completion callbacks with `dont_shake` set to avoid recursive cache eviction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_blockdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_crc32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_crc32.c

CRC32 and CRC32C implementation, with a standard CRC32 table and a slicing-by-4-style CRC32C table initialized at runtime.

Key behavior:
- `ext4_crc32` computes classic CRC32 over bytes using `crc32_tab`.
- `ext4_crc32c` handles unaligned leading bytes, processes aligned 32-bit words through `ext4_crc32_u`, then handles trailing bytes.
- `ext4_crc32_init` fills the derived CRC32C tables `crc32c_tab[1..3]` once.

Notable dependencies:
- `ext4_crc32_u` is defined inline or as a macro in the CRC header.
- Used throughout metadata checksum support: superblock UUID seed, block/inode bitmaps, group descriptors, inodes, directory tails, htree nodes, and extent blocks.

Research notes:
- The file notes the CRC32 code is based on FreeBSD.
- `crc32c_tab` is global rather than static, likely because the inline word helper references it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_debug.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_debug.c

Minimal debug mask storage for ext4srv.

Key behavior:
- Maintains a static `debug_mask`.
- `ext4_dmask_set` ORs bits into the mask.
- `ext4_dmask_clr` clears bits.
- `ext4_dmask_get` returns the current mask.

Notable dependencies:
- Debug printing macros in headers use this mask to decide which subsystem messages to emit.

Research notes:
- There is no locking around the debug mask; it is process-global mutable state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_dir.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_dir.c

Directory entry manipulation and linear directory iteration/search/add/remove support. It also handles ext4 directory entry checksum tails and delegates to htree indexing when directory indexes are enabled.

Key behavior:
- `ext4_dir_csum_verify`, `ext4_dir_set_csum`, and tail helpers validate and update metadata checksum directory tails.
- `ext4_dir_iterator_init`, `ext4_dir_iterator_next`, and `ext4_dir_iterator_fini` walk directory entries across inode data blocks, validating alignment, record length, and name length.
- `ext4_dir_write_entry` writes an ext4 dirent with inode number, record length, name length, file type, and name bytes.
- `ext4_dir_add_entry` uses htree insertion if `dir_index` and inode index flag are present; otherwise it searches linear blocks for space or appends a new data block.
- `ext4_dir_find_entry` uses htree lookup when available, otherwise scans all directory data blocks linearly.
- `ext4_dir_remove_entry` invalidates an entry, merges its record length into the previous entry when possible, updates checksum, and marks the block dirty.
- `ext4_dir_try_insert_entry` inserts into an invalid entry or splits slack from a valid entry.
- `ext4_dir_find_in_block` performs name-length-first matching inside a single directory block.

Notable dependencies:
- Htree implementation in `ext4_dir_idx.c`.
- Data block mapping via `ext4_fs_get_inode_dblk_idx` and appending via `ext4_fs_append_inode_dblk`.
- Transaction block access and dirty marking through `ext4_trans`.

Research notes:
- Checksum failures on linear leaf blocks are logged as warnings and do not stop lookup/add in most paths.
- `ext4_dir_iterator_next` skips inode-zero entries but assumes `it->curr` is valid on entry.
- The fallback for unsupported file types writes `EXT4_DE_UNKNOWN`.
- Directory insertion with metadata checksums reserves space for `ext4_dir_entry_tail` in new blocks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_dir_idx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_dir_idx.c

Ext4 htree indexed directory implementation. It initializes indexed directories, computes hashes, verifies and updates htree checksums, searches htree nodes, handles hash collision continuation, splits full data blocks, splits/grows index nodes, inserts entries, and updates `..` for indexed directory renames.

Key behavior:
- Inline accessors wrap htree root info, count/limit, entry hash, and child block fields with little-endian conversion.
- `ext4_dir_dx_checksum`, `ext4_dir_dx_csum_verify`, and `ext4_dir_set_dx_csum` implement htree node checksum support using filesystem UUID seed, inode number, generation, entries, and tail.
- `ext4_dir_dx_init` creates root block entries for `.` and `..`, initializes htree metadata, appends the first leaf block, and links it from the root.
- `ext4_dir_hinfo_init` validates root htree metadata, selects signed/unsigned hash variant, loads hash seed, and computes the target name hash.
- `ext4_dir_dx_get_leaf` descends the htree using binary search through index entries and loads child blocks.
- `ext4_dir_dx_find_entry` locates the candidate leaf, linearly searches it, then follows collision-continuation blocks when needed.
- `ext4_dir_dx_split_data` sorts existing leaf dirents by hash, splits them into old/new leaf blocks, initializes checksum tails, and inserts a new htree entry.
- `ext4_dir_dx_split_index` handles root-to-node growth and internal node splits within the ext4 htree height limit used by Linux.
- `ext4_dir_dx_add_entry` combines leaf lookup, index split, direct insertion, data split, and final insertion of the new name.
- `ext4_dir_dx_reset_parent_inode` rewrites the `..` inode in an indexed directory root block.

Notable dependencies:
- Hashing from `ext4_hash.c`/`ext4_hash.h`.
- Directory block operations from `ext4_dir.c`.
- Block mapping/appending from `ext4_fs.c`.
- Checksums from `ext4_crc32.c`.

Research notes:
- Root checksum mismatch paths in `ext4_dir_dx_find_entry` and `ext4_dir_dx_add_entry` return before releasing `root_block`, which can leak a cache reference.
- Several htree checksum mismatch paths treat child/root corruption as hard errors, while lower-level descent may only warn for some internal blocks.
- The implementation supports only htree depth 0 or 1, matching the hardcoded two-block path array and Linux limit noted in comments.
- `ext4_dir_dx_split_data` assumes a valid sortable set of entries; edge cases with no entries or pathological hashes would rely on assertions or surrounding directory invariants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_dir_idx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_extent.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_extent.c

Extent tree implementation for ext4 file block mapping. It verifies extent nodes, searches paths, iterates extents, grows and splits extent trees, inserts/removes mappings, converts unwritten extents, merges adjacent extents, allocates contiguous data blocks, and serves logical-to-physical block requests.

Key behavior:
- Computes and validates extent block metadata checksums using filesystem UUID seed, inode number, generation, and extent block contents up to the tail.
- `ext4_extent_find_extent` walks from the inode-embedded root down to a leaf, binary-searching index/leaf nodes and returning a full path for later modification.
- Path helpers mark extent blocks or inode roots dirty, release loaded blocks, reload invalidated child paths, and increment/decrement to adjacent extents.
- `ext4_extent_grow_tree` moves the inode root into a new extent block and creates a deeper root index in the inode.
- `ext4_extent_split` preallocates tree blocks, grows the tree if needed, splits full leaves/internal nodes, adjusts path pointers, and writes new parent indexes.
- `ext4_extent_insert` inserts one extent into the leaf, splitting first if needed, then updates parent first-key indexes.
- `ext4_extent_remove_space` removes mappings over a logical range, trims partially overlapping extents, frees physical blocks, deletes empty nodes, and collapses empty roots.
- `ext4_extent_convert_written` converts all or part of an unwritten extent to written, zeroing physical blocks and splitting into written/unwritten extents as required.
- `ext4_extent_get_blocks` is the main map/create entry point: finds existing extents, returns holes for reads, allocates new contiguous physical blocks for writes, and appends/prepends/creates extent records.

Notable dependencies:
- Block allocation/freeing from `ext4_balloc.c`.
- Block IO/cache through `ext4_blockdev` and `ext4_trans`.
- Inode flags/root headers from `ext4_inode` and `ext4_super`.

Research notes:
- `ext4_extent_alloc_datablocks` tracks `retnblocks` but returns `nblocks` through `*nblocksp`; if contiguous allocation stops early without an error, callers can believe more blocks were allocated than actually were.
- `ext4_extent_split` leaks the temporary `newfblocks` array if allocation of one of the new blocks fails before reaching the common cleanup label.
- `ext4_extent_find_extent` verifies loaded child blocks, but on verification failure it releases only blocks already represented in the path; the just-loaded failing block is not yet in the path, so that cache reference is at risk.
- The code uses several assertions for extent tree invariants and two insertion cases after pre-splitting; corrupted filesystems can therefore hit assertions depending on build configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_fs.c

Filesystem core layer tying the superblock, feature checks, group descriptors, bitmap/table initialization, inode references, inode allocation/freeing, truncation, and logical-to-physical block mapping together.

Key behavior:
- `ext4_fs_init` reads and validates the superblock, checks supported features, computes indirect block limits, marks writable filesystems dirty/error-state on mount, increments mount count, and seeds UUID CRC32C.
- `ext4_fs_fini` marks the filesystem clean/valid on writable unmount and writes the superblock.
- Feature check helpers log compatible, incompatible, and read-only-compatible feature bits; unsupported incompatible features fail, unsupported RO-compatible features force read-only.
- Lazy group initialization routines create block bitmaps, inode bitmaps, and inode tables for groups marked uninitialized.
- Group descriptor handling locates descriptor blocks across normal/meta_bg layouts, verifies checksums, initializes uninit groups, and recomputes checksums on dirty put.
- Inode reference handling maps inode numbers to inode table blocks, verifies inode checksums, and writes updated checksums/dirty inode table blocks.
- `ext4_fs_alloc_inode` allocates through `ext4_ialloc`, zeroes and initializes inode fields, permissions, mode, timestamps, extra inode size, and block arrays.
- `ext4_fs_free_inode` frees indirect metadata blocks, extended attribute blocks, and the inode allocation bit; extent data is expected to have been removed by truncation first.
- `ext4_fs_truncate_inode` shrinks files/directories/symlinks/devices and dispatches either extent range removal or indirect-block release.
- `ext4_fs_get_inode_dblk_idx_internal`, `ext4_fs_init_inode_dblk_idx`, and `ext4_fs_append_inode_dblk` provide block mapping/allocation for both extent and legacy direct/indirect files.
- Link count helpers implement special directory link count behavior for indexed directories and `DIR_NLINK`.

Notable dependencies:
- Superblock and descriptor field helpers from `ext4_super`, `ext4_block_group`, and `ext4_inode`.
- Allocation via `ext4_balloc` and `ext4_ialloc`.
- Extent mapping via `ext4_extent`.
- Checksums via `ext4_crc32` and `ext4_block_group`.

Research notes:
- `ext4_fs_init` marks writable filesystems as error-state before full operation and `ext4_fs_fini` marks valid on unmount, mirroring ext-style dirty mount semantics.
- `support_unwritten` is accepted in block mapping wrappers but is not materially used in this implementation path.
- Extent append grows inode size immediately after allocating one mapped block.
- Indirect block allocation is careful to zero new indirect blocks before linking/using them, but if some mid-path allocations fail after linking parent state, rollback is limited.
- `ext4_fs_inode_to_goal_block` returns an inode’s block group number, not an actual block address; callers should treat it only as a coarse hint.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_fs.c -->