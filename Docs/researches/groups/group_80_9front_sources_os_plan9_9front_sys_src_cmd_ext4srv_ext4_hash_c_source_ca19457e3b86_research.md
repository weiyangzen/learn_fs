# Group Research: group_80_9front_sources_os_plan9_9front_sys_src_cmd_ext4srv_ext4_hash_c_source_ca19457e3b86

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_hash.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_hash.c

Directory hash implementation for ext2/ext3/ext4 htree indexed directories. It implements the legacy, TEA, and half-MD4 hash variants used by ext directory indexing, including signed and unsigned character modes.

Key behavior:
- Defines local MD4 round macros and `ext2_half_md4`, derived from the RSA MD4 transform but reduced to the half-MD4 form Linux uses for htree directory names.
- Implements `ext2_tea` for the TEA htree hash variant.
- Implements `ext2_legacy_hash` for the older signed/unsigned legacy hash.
- `ext2_prep_hashbuf` packs filename bytes into 32-bit words with length-derived padding, using signed or unsigned character interpretation depending on hash version.
- `ext2_htree_hash` validates the name and hash version, optionally applies a superblock hash seed, computes major/minor hashes, clears the low collision bit, avoids the EOF sentinel, and reports unsupported versions via `werrstr`.

Notable dependencies:
- Hash version constants and `EXT2_HTREE_EOF` are declared in `include/ext4_types.h`.
- Used by indexed directory code through `include/ext4_hash.h` and `ext4_dir_idx.c`.
- Relies on Plan 9-style `werrstr` for error reporting.

Research notes:
- Names must be 1..255 bytes; empty names and overlong names fail.
- The implementation mutates `name`/`len` while processing hash chunks, so callers only receive the final major/minor values.
- The major hash low bit is reserved for htree collision continuation, matching ext directory-index conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_ialloc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_ialloc.c

Inode allocation and freeing logic. It maps inode numbers to block groups, verifies and updates inode bitmap checksums, scans groups for free inodes, and maintains inode counters in group descriptors and the superblock.

Key behavior:
- Converts between absolute inode numbers, per-group inode indexes, and block group IDs.
- Computes inode bitmap CRC32C from the filesystem UUID seed and bitmap contents when `metadata_csum` is enabled.
- `ext4_ialloc_free_inode` clears the inode bitmap bit, updates bitmap checksum, marks the bitmap block and group descriptor dirty, increments free inode counts, decrements used directory counts when applicable, and updates superblock free inode count.
- `ext4_ialloc_alloc_inode` starts searching at `fs->last_inode_bg_id`, wraps once, scans free bits with `ext4_bmap_bit_find_clr`, marks an inode used, updates free/used/unused counters, and records the last successful group.

Notable dependencies:
- Bitmap primitives come from `ext4_bitmap.h`.
- Group descriptor accessors come from `ext4_block_group.h`.
- Metadata checksum support uses `ext4_crc32c`.
- Bitmap blocks are fetched through `ext4_trans_block_get` so journal transactions can capture modifications.

Research notes:
- Inode bitmap checksum mismatches are logged as warnings and allocation/free proceeds.
- Allocation is a simple first-fit group scan, explicitly simpler than Linux's Orlov allocator.
- Error handling in one allocation path calls `ext4_block_set` and then checks the older `rc` value, so a block release error there can be missed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_inode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_inode.c

Endian-safe inode field accessor implementation. It centralizes getting and setting inode mode, ownership, size, checksums, timestamps, link counts, block counts, flags, file ACL pointers, direct/indirect block slots, special-device payloads, and extent root access.

Key behavior:
- Handles Hurd high mode bits when `creator_os` is Hurd.
- Exposes low-level timestamp, UID/GID, link count, generation, extra inode size, and checksum fields.
- `ext4_inode_get_size` returns the high size word only for regular files on dynamic-revision filesystems.
- `ext4_inode_get_blocks_count` and `ext4_inode_set_blocks_count` implement normal, 48-bit, and huge-file block count encoding.
- Supports direct and indirect block pointer access through the inode `blocks[]` array.
- Encodes device numbers into inode direct block slots.
- Provides type and flag predicates and `ext4_inode_can_truncate`.
- Returns the inline extent root header by casting `inode->blocks`.

Notable dependencies:
- Uses superblock feature checks from `ext4_super.h`.
- Public declarations are in `include/ext4_inode.h`.
- Extent users rely on `ext4_inode_get_extent_header`.

Research notes:
- `uid` and `gid` accessors only use the low 16-bit disk fields despite returning `u32int`; Linux high UID/GID fields are not combined here.
- `ext4_inode_set_file_acl` stores the high ACL bits into a 16-bit field only when creator OS is Linux.
- Huge-file encoding depends on filesystem block size and `EXT4_INODE_FLAG_HUGE_FILE`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_journal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_journal.c

JBD/JBD2-style journal implementation for ext4srv. It loads the journal inode, verifies and writes journal metadata checksums, replays committed transactions, manages revoke records, starts/stops journaling sessions, records dirty buffers into transactions, writes descriptor/data/revoke/commit blocks, and checkpoints completed transactions back to the main filesystem.

Key behavior:
- Defines replay-only revoke entries and runtime recovery state using red-black trees.
- Implements journal superblock, descriptor/revoke metadata, commit block, and data block checksum handling for checksum v1/v2/v3 style feature combinations.
- `jbd_get_fs` binds the journal inode and reads/verifies the journal superblock.
- `jbd_recover` scans valid transactions, builds the revoke tree, replays descriptor data blocks while respecting revokes, clears ext4 `RECOVER`, and advances the journal start.
- Journal block IO maps journal logical blocks through the journal inode with `jbd_inode_bmap` and uses temporary/flushed cache buffers.
- Tag parsing/writing supports 32-bit and 64-bit block numbers, optional UUID fields, escape flags, and last-tag markers.
- `jbd_journal_start` marks the filesystem as needing recovery, initializes transaction IDs and checkpoint queues, and attaches the journal to the block device.
- `jbd_journal_stop` flushes checkpoint transactions, clears recovery state, zeros live journal state, and writes the JBD superblock.
- Transaction code tracks dirty buffers by filesystem LBA, handles ownership when later transactions supersede earlier ones, writes descriptors and data copies to the journal, writes revoke blocks, emits commit blocks, and uses cache write completion callbacks for checkpoint advancement.

Notable dependencies:
- Block cache callbacks and dirty flags from `ext4_bcache`.
- Main filesystem mapping and block IO from `ext4_fs` and `ext4_blockdev`.
- On-disk JBD structures and feature bits from `include/ext4_types.h`.
- Runtime queues and red-black trees from `queue.h` and `tree.h`.

Research notes:
- The code comments still include a stale note elsewhere that lwext4 journaling is not supported, but this file implements a working local JBD layer.
- Journal-device support is explicitly TODO; the journal is expected to be the filesystem journal inode.
- Several writeback/recovery error paths use `assert` for conditions that would be I/O or allocation failures in production.
- `jbd_replay_block_tags` has special handling for block 0 as the ext4 superblock image and preserves mount count/state across replay.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_mkfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_mkfs.c

Filesystem creation support for ext2/ext3/ext4 images on an `ext4_blockdev`. It derives mkfs parameters, lays out block groups, writes superblocks/group descriptors/bitmaps, initializes reserved inodes, creates root and `lost+found`, and optionally creates an internal journal inode.

Key behavior:
- `sb2info` reads an existing superblock into `ext4_mkfs_info`.
- Computes default block size, blocks per group, inode count, inodes per group, journal size, group count, inode table blocks, descriptor blocks, and indirect block geometry.
- `fill_sb` constructs the in-memory ext superblock, including features, UUID, label, default hash seed/version, descriptor size, inode size preferences, and journal inode number.
- `write_bgroups` initializes group descriptors, block/inode bitmap blocks, inode table pointers, free counts, and uninitialized bitmap/table flags.
- `write_sblocks` writes backup superblocks for sparse-super groups and then writes the primary superblock at offset 1024.
- `alloc_inodes` allocates reserved inodes 1..11 and initializes root/journal inode block state where needed.
- `create_dirs` initializes root and `lost+found` directory contents with indexed-directory support when enabled.
- `create_journal_inode` allocates journal blocks and writes a JBD v2 superblock into the first journal data block.
- `ext4_mkfs` controls feature sets for ext2/ext3/ext4, disables unhandled features, enables optional journaling, initializes cache/writeback, formats, mounts internally, populates metadata, and tears down.

Notable dependencies:
- Uses allocation, directory, indexed-directory, inode, superblock, filesystem, block cache, and JBD type definitions from the local ext4srv modules.

Research notes:
- Feature masks are conservative: `meta_bg`, `flex_bg`, `64bit`, metadata checksums, group descriptor checksums, dir nlink, extra isize, and huge file are forcibly disabled during mkfs.
- `write_bgroups` computes `bg_start_block` with `first_data_block` added twice; for 1 KiB filesystems that likely shifts group metadata one block too far.
- The mkfs timestamps are initialized to zero rather than current time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_super.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_super.c

Superblock helper implementation. It validates core superblock fields, reads/writes the primary superblock, handles metadata checksums, computes group counts and last-group sizes, and determines sparse-super/group-descriptor metadata placement.

Key behavior:
- `ext4_block_group_cnt`, `ext4_blocks_in_group_cnt`, and `ext4_inodes_in_group_cnt` compute total and per-group counts with last-group adjustment.
- `ext4_sb_csum`, `ext4_sb_set_csum`, and `ext4_sb_verify_csum` implement metadata-csum superblock CRC32C over fields before the checksum.
- `ext4_sb_write` updates checksum before writing 1024 bytes at the ext superblock offset.
- `ext4_sb_check` validates magic, nonzero counts, inode size, first inode, descriptor size bounds, and checksum.
- `ext4_sb_sparse` implements the ext sparse-super rule: groups 0/1 and powers of 3, 5, or 7.
- `ext4_bg_num_gdb` handles descriptor backup counts with and without `meta_bg`.
- `ext4_num_base_meta_clusters` estimates base metadata clusters for a block group.

Notable dependencies:
- Uses inline feature/count helpers from `include/ext4_super.h`.
- CRC32C comes from `ext4_crc32`.
- Block IO is provided by `ext4_blockdev`.

Research notes:
- `ext4_num_base_meta_clusters` shifts by `log_cluster_size` after computing a block-count expression; because `log_cluster_size` is a log2 block-size field, this deserves scrutiny for bigalloc-style calculations.
- Superblock checksum validation only applies when `metadata_csum` is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_trans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_trans.c

Thin transaction integration layer between generic ext4 metadata mutation code and the JBD journal implementation.

Key behavior:
- `ext4_trans_set_block_dirty` reconstructs an `ext4_block` wrapper from an `ext4_buf`; when a journal and current transaction exist, it records the block through `jbd_trans_set_block_dirty`, otherwise it marks the buffer dirty in the cache.
- `ext4_trans_block_get_noread` and `ext4_trans_block_get` currently delegate directly to the block cache get functions.
- `ext4_trans_try_revoke_block` adds a revoke to the current transaction when one is active; if journaling exists but no transaction is active, it flushes the LBA from cache instead.

Notable dependencies:
- Requires `ext4.h`, `ext4_fs.h`, and `ext4_journal.h`.
- Depends on `buf->bc->bdev->fs` being populated.

Research notes:
- The header comments mention a `jbd_trans_get_access` step, but this implementation does not have a separate get-access operation.
- The layer keeps most ext4 code independent from direct JBD calls for dirty marking and revocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4srv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4srv.c

Plan 9 9P file server front end for the ext4 library. It exposes mounted ext filesystems through a 9P `Srv`, maps Plan 9 file requests to ext4 operations, handles user/group permissions through a passwd/group-style table, and provides a command pipe for stats, sync, and halt.

Key behavior:
- `Aux` stores per-fid state: partition pointer, effective uid, path, directory offset, open ext4 file/dir handle, type, and remove-on-close flag.
- `haveperm` converts Plan 9 open modes to read/write/execute bits and checks other/owner/group permissions against ext4 inode mode, uid/gid, and parsed groups.
- `rattach` chooses the requested partition or default device partition, applies `-S` root override behavior, and creates the root fid.
- `ropen`, `rcreate`, `rread`, `rwrite`, `rremove`, `rstat`, `rwstat`, `rwalk1`, `rclone`, and `rdestroyfid` implement the 9P server operations using ext4 API calls.
- Directory reads use `dirread9p` and skip `.`/`..` plus unsupported entry types.
- Writes explicitly zero-fill holes up to the requested offset before writing, then honors append mode.
- `rwstat` supports rename, truncation, mode/append/tmp flags, mtime, and gid changes with Plan 9-style permission checks.
- `cmdsrv` posts `#s/<srvname>.cmd` and accepts `stats`/`df`, `sync`, and `halt`.
- `threadmain` parses service, debug, device, group, mkfs, block size, inode size, label, stdio, and root-override flags.

Notable dependencies:
- Uses public ext4 API from `include/ext4.h`, inode accessors, `group.c`, and partition/device helpers from `common.h`/other ext4srv files.
- Uses Plan 9 libraries: `fcall.h`, `thread.h`, `9p.h`, and `bio.h`.

Research notes:
- The server only exposes regular files and directories during walk and directory enumeration; symlinks and special files are effectively hidden from normal traversal.
- Permission checks treat root and group membership through the parsed group table, not through host OS credentials.
- Directory creation relies on `ext4_dir` embedding `ext4_file` as its first field when assigning qids through the union-backed pointer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/group.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/group.c

Parser and lookup helpers for the ext4srv user/group table used by permission checks.

Key behavior:
- `loadgroups` duplicates the raw group file, parses colon-separated records, validates numeric IDs, appends `Group` records, and parses comma-separated member names.
- After parsing all records, member names are resolved to numeric IDs with `findgroup`.
- `freegroups` releases each group's member array plus the group array and raw backing string.
- `findgroup` looks up by name and optionally returns the numeric ID, using `~0` when not found.
- `findgroupid` looks up by numeric ID.
- `ingroup` checks direct identity or membership in a group's resolved member list.

Notable dependencies:
- Uses Plan 9 libc helpers: `getfields`, `strtoll`, `werrstr`, `strdup`, and allocation routines.
- Public structs and prototypes are in `group.h`.

Research notes:
- Group and member names point into `Groups.raw`, so the duplicated raw string must outlive all `Group` records.
- Missing member names resolve to ID `~0`; there is no hard failure for unresolved members in the second pass.
- The parser expects at least three colon fields and, if present, uses the fourth field for members.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/group.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/group.h

Small header defining group table structures and lookup APIs for ext4srv permission handling.

Key behavior:
- `Group` contains a 32-bit ID, name pointer, dynamic member array, and member count.
- `Groups` contains the duplicated raw text backing store, group array, and group count.
- Declares parsing, cleanup, name lookup, ID lookup, and membership-check functions.

Notable dependencies:
- Assumes Plan 9 integer typedefs such as `u32int` are available before inclusion.
- Implemented by `group.c` and consumed by `ext4srv.c` plus partition setup code.

Research notes:
- The header intentionally exposes raw arrays rather than hiding them behind an opaque type.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/group.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4.h

Public ext4srv API header. It defines mountpoint, lock, file, directory entry, directory handle, mount statistics, and all public mount, cache, file, metadata, symlink, special-file, and directory operations.

Key behavior:
- `ext4_mountpoint` aggregates mount state, optional OS locks, core `ext4_fs`, JBD filesystem/session objects, and block cache.
- `ext4_file` tracks mountpoint, inode number, flags, size, and current position.
- `ext4_dir` embeds `ext4_file`, a reusable public directory entry, and next-entry offset.
- Declares mount/unmount, journal start/stop/recovery, stats, lock setup, superblock access, writeback toggle, and cache flush.
- Declares file remove/link/rename/open/close/truncate/read/write/seek/tell/size functions.
- Declares raw inode lookup, existence check, mode/owner/time setters and getters, symlink and mknod support, readlink, directory remove/move/mkdir/open/close/next/rewind.

Notable dependencies:
- Pulls in `ext4_types.h`, `ext4_debug.h`, `ext4_blockdev.h`, `ext4_fs.h`, and `ext4_journal.h`.
- Implemented mainly by `ext4.c`, with lower layers from the rest of ext4srv.

Research notes:
- The API blends libc-like open flags with Plan 9-style error reporting through implementation-side `werrstr`.
- Directory handle layout is used by `ext4srv.c` through a union with `ext4_file *`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_balloc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_balloc.h

Public declarations for ext4 block allocation.

Key behavior:
- Declares block-to-group and group-to-starting-block conversion helpers.
- Declares block bitmap checksum setter.
- Declares single-block and range freeing from an inode.
- Declares goal-based block allocation and try-allocate-at-specific-block.

Notable dependencies:
- Includes `ext4_config.h`, `ext4_types.h`, and `ext4_fs.h`.
- Implemented by `ext4_balloc.c` and used by filesystem block mapping/truncation code.

Research notes:
- The API operates on `ext4_inode_ref` for allocation/freeing so inode block counts and dirty state can be updated with allocation metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_balloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_bcache.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_bcache.h

Block cache data structure and API header. It defines cached buffer state, cache trees/lists, dirty flags, reference counters, and dynamic cache management functions.

Key behavior:
- `ext4_buf` stores flags, LBA, data pointer, LRU state, reference count, owning cache, tree/list nodes, dirty-list state, and optional write-completion callback.
- `ext4_block` is the public handle pairing logical block ID, cache buffer, and data pointer.
- `ext4_bcache` stores cache capacity, item size, LRU counter, allocated/reference counters, owning block device, shake guard, LBA/LRU red-black trees, and dirty list.
- Defines state bits `BC_UPTODATE`, `BC_DIRTY`, `BC_FLUSH`, and `BC_TMP`.
- Provides inline dirty flag, flag, reference, and dirty-list helpers.
- Declares dynamic init/fini, cleanup, LRU selection, drop/invalidate, lookup, allocation, free, and fullness APIs.

Notable dependencies:
- Uses local `tree.h` and `queue.h`.
- Bound to `ext4_blockdev` and used heavily by transaction/journal code.

Research notes:
- The header's `ref_blocks` comments say referenced data blocks, but the implementation uses it as a count of allocated cache buffers.
- `end_write` is central to checkpoint completion in the journal layer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_bcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_bitmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_bitmap.h

Bitmap helper header for allocation bitmaps.

Key behavior:
- Provides inline little-bit-order set, clear, is-set, and is-clear operations.
- Declares `ext4_bmap_bits_free` for clearing bit ranges.
- Declares `ext4_bmap_bit_find_clr` for finding the first clear bit in a bounded range and reporting no-space status.

Notable dependencies:
- Includes `ext4_config.h`.
- Implemented by `ext4_bitmap.c`; used by block and inode allocation.

Research notes:
- Helpers do not bounds-check bitmap memory; callers supply valid bit ranges.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_block_group.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_block_group.h

Inline accessor header for ext4 block group descriptors plus CRC16 declaration.

Key behavior:
- Gets/sets block bitmap, inode bitmap, and inode table first-block addresses with high 32-bit fields when descriptor size permits.
- Gets/sets free block count, free inode count, used directory count, and unused inode table count using high halves for 64-byte descriptors.
- Sets descriptor checksum and manages block group flags.
- Declares `ext4_bg_crc16`.

Notable dependencies:
- Includes `ext4_types.h` and `ext4_super.h`.
- Used by allocation, mkfs, filesystem initialization, and checksum code.

Research notes:
- High address/count fields are used only when descriptor size is greater than the 32-byte minimum.
- `ext4_bg_has_flag` reads the on-disk flag word through `to_le16`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_block_group.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_blockdev.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_blockdev.h

Block device abstraction header. It defines the physical device callback interface, logical block device state, static initialization macro, and cached/direct/block-byte IO APIs.

Key behavior:
- `ext4_blockdev_iface` supplies open, read, write, close, optional lock/unlock callbacks, physical block geometry, physical scratch buffer, reference count, IO counters, and user pointer.
- `ext4_blockdev` stores partition offset/size, bound cache, logical block size/count, writeback reference count, owning filesystem, and journal pointer.
- `EXT4_BLOCKDEV_STATIC_INSTANCE` creates static interface and device objects with a physical scratch buffer.
- Declares lifecycle, cache binding, buffer flush, LBA flush, logical block size setup, cached block get/set, direct block IO, byte-range IO, cache flush, and writeback toggle functions.

Notable dependencies:
- Includes `ext4_bcache.h`.
- Implemented by `ext4_blockdev.c`; used by every storage-facing module.

Research notes:
- `#pragma incomplete struct ext4_blockdev` reflects Plan 9 C conventions.
- The device layer supports partitions by combining callback-level physical geometry with `part_offset` and `part_size`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_blockdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_config.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_config.h

Configuration and platform compatibility header for ext4srv.

Key behavior:
- Includes Plan 9 `u.h` and `libc.h`.
- Defines a local `bool` enum.
- Defines open flag constants used by the ext4 library and an `O_WRMASK`.
- Detects several big-endian architectures and defines `CONFIG_BIG_ENDIAN`.
- Defines static limits for block devices, mountpoints, block cache size, and max single truncate size.
- Declares global Plan 9-style error strings used across the implementation.

Notable dependencies:
- Included by nearly all ext4srv headers and C files.

Research notes:
- Open flag values follow Unix-style bit assignments, not Plan 9's public flag values; `ext4srv.c` translates Plan 9 open modes before calling ext4.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_crc32.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_crc32.h

CRC32/CRC32C API header.

Key behavior:
- Declares classic CRC32 and CRC32C functions.
- Exposes the four-slice CRC32C table `crc32c_tab`.
- Defines endian-aware `ext4_crc32_u` macro for feeding one 32-bit word into the CRC32C calculation.
- Declares `ext4_crc32_init`.

Notable dependencies:
- Includes `ext4_config.h`.
- Implemented by `ext4_crc32.c`; used by superblock, group, bitmap, inode, directory, extent, and journal checksum code.

Research notes:
- The word-feed macro mutates the `crc` argument as part of the expression, so callers must pass an lvalue.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_debug.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_debug.h

Debug mask and logging macro header for ext4srv modules.

Key behavior:
- Defines one debug mask bit per subsystem, plus `DEBUG_NOPREFIX` and `DEBUG_ALL`.
- Maps debug mask IDs to subsystem prefixes via `ext4_dmask_id2str`.
- Defines text prefixes for info/warn/error messages.
- Declares global debug mask set/clear/get functions.
- Defines `ext4_dbg`, which checks the mask, optionally emits function/subsystem prefix, and prints to file descriptor 2.

Notable dependencies:
- Uses Plan 9 `fprint` through `ext4_config.h`.
- Implemented by `ext4_debug.c`.

Research notes:
- `ext4_dmask_id2str` handles single-bit masks; combined masks get no subsystem prefix.
- Debug output is process-global and not synchronized.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_dir.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_dir.h

Directory entry accessor and directory manipulation API header.

Key behavior:
- Defines `ext4_dir_iter` for internal linear directory traversal and `ext4_dir_search_result` for found entries with their containing block.
- Provides inline accessors for directory entry inode, record length, name length, and inode type, including old revision name-length behavior.
- Declares directory block checksum verification/update and tail initialization helpers.
- Declares iterator init/next/fini, directory entry writing, entry add/find/remove, in-block insertion/search, and search-result destruction.

Notable dependencies:
- Includes `ext4_types.h`, `ext4_misc.h`, `ext4_blockdev.h`, and `ext4_super.h`.
- Implemented by `ext4_dir.c` and used by htree directory code and public directory operations.

Research notes:
- The inline inode type accessor returns `EXT4_DE_UNKNOWN` for older on-disk formats without file type storage.
- Checksum-tail support is exposed here but actual checksum decisions are in the implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_dir_idx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_dir_idx.h

Indexed-directory htree API header.

Key behavior:
- Defines `ext4_dir_idx_block`, which combines a loaded block with entry-base and current-position pointers.
- Defines `EXT4_DIR_DX_INIT_BCNT` for initial indexed directory block count.
- Declares indexed directory initialization, htree lookup, htree insertion, and parent inode reset for `..`.

Notable dependencies:
- Includes `ext4_types.h`, `ext4_fs.h`, and `ext4_dir.h`.
- Implemented by `ext4_dir_idx.c`; hash computation comes from `ext4_hash.c`.

Research notes:
- The reset-parent API is needed by directory rename/move paths for indexed directories.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_dir_idx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_extent.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_extent.h

Extent tree accessor and API header for extent-based file block mapping.

Key behavior:
- Defines `ext4_extent_path`, the traversal path entry used for lookup, insertion, splitting, and truncation.
- Defines macros for unwritten extent state, max written/unwritten lengths, first/last extent/index entry, extent tail offset, in-range checks, and max blocks.
- Provides inline endian-safe accessors for extent logical block, length, physical block, index logical/physical block, and extent header fields.
- `ext4_extent_tree_init` initializes an inode-stored root extent header and marks the inode reference dirty.
- Declares `ext4_extent_get_blocks` for lookup/allocation/conversion and `ext4_extent_remove_space` for truncation/freeing.

Notable dependencies:
- Includes `ext4_inode.h`; implemented by `ext4_extent.c`.
- On-disk extent structs are defined in `ext4_types.h`.

Research notes:
- `EXT4_EXT_SET_UNWRITTEN` and `EXT4_EXT_SET_WRITTEN` directly mutate the little-endian `nblocks` field with masks; this assumes the mask expression matches on-disk endian representation.
- Inline initialization computes inode-root capacity from the fixed inode `blocks[]` area.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_extent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_fs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_fs.h

Core in-memory filesystem state and filesystem helper API header.

Key behavior:
- `ext4_fs` stores read-only state, block device, superblock, UUID checksum seed, indirect block limits/geometry, last inode allocation group, journal objects, and current transaction.
- Defines block group and inode reference wrappers carrying the loaded block, typed pointer, owning filesystem, index, and dirty flag.
- Provides inline block-address/group-index conversions.
- Declares filesystem init/fini and feature checking.
- Declares group descriptor and inode reference get/put functions.
- Declares inode block initialization, inode allocation/free, truncation, allocation-goal helpers, block mapping/initialization/append, and link-count increment/decrement.

Notable dependencies:
- Includes `ext4_types.h` and `ext4_misc.h`.
- Implemented primarily by `ext4_fs.c`; used by allocation, directory, file IO, mkfs, and journal code.

Research notes:
- `curr_trans` is the bridge used by `ext4_trans.c` to journal metadata dirtying.
- The address conversion helpers account for `first_data_block` in 1 KiB-block filesystems.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_hash.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_hash.h

Directory htree hash header.

Key behavior:
- Defines `ext4_hash_info`, carrying major hash, minor hash, hash version, and seed pointer.
- Declares `ext2_htree_hash`, the shared name-hash function for indexed directories.

Notable dependencies:
- Includes `ext4_config.h`.
- Implemented by `ext4_hash.c`; consumed by `ext4_dir_idx.c`.

Research notes:
- The public function name uses the ext2 prefix because ext htree hashing is shared across ext2/3/4 directory-index formats.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_ialloc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_ialloc.h

Inode allocation API header.

Key behavior:
- Declares inode bitmap checksum setter.
- Declares inode freeing with directory/non-directory counter adjustment.
- Declares inode allocation and documents that it uses a simpler algorithm than Linux's Orlov allocator.

Notable dependencies:
- Includes `ext4_config.h` and `ext4_types.h`.
- Implemented by `ext4_ialloc.c`; called through higher-level filesystem allocation functions.

Research notes:
- The header refers to `struct ext4_fs` and `struct ext4_bgroup` through included type declarations rather than including the full filesystem header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_ialloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_inode.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_inode.h

Inode accessor API header.

Key behavior:
- Declares getters/setters for mode, UID/GID, size, access/change/modify/delete/create times, link count, blocks count, flags, generation, extra inode size, file ACL, direct and indirect block slots, and device number.
- Declares inode type predicates and flag set/clear/test helpers.
- Declares inode checksum getter/setter.
- Declares truncate eligibility and extent-root access.

Notable dependencies:
- Includes `ext4_config.h` and `ext4_types.h`; forward-declares `ext4_extent_header` as incomplete.
- Implemented by `ext4_inode.c` and used throughout filesystem, directory, public API, mkfs, and service code.

Research notes:
- The API abstracts endian conversion and OS-specific inode layout details from callers.
- It exposes no high-resolution timestamp extra fields beyond raw creation time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_journal.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_journal.h

Runtime JBD journal data structures and API header.

Key behavior:
- `jbd_fs` binds a journal inode reference, journal superblock, block device, UUID checksum seed, and dirty flag.
- `jbd_buf` tracks one journaled copy of a filesystem block and links into transaction and per-block dirty queues.
- `jbd_revoke_rec` and `jbd_block_rec` are red-black-tree records for revoked LBAs and live block ownership.
- `jbd_trans` stores transaction ID, journal block allocation state, data/write counters, checksum/error fields, owning journal, buffer queue, revoke tree, block record list, and checkpoint queue node.
- `jbd_journal` stores active log pointers, transaction IDs, block size, checkpoint queue, live block record tree, and owning JBD filesystem.
- Declares journal load/unload, inode block mapping, recovery, start/stop, transaction allocation, dirty marking, revoke handling, transaction free/commit, and checkpoint purge.

Notable dependencies:
- Includes `queue.h` and `tree.h`; on-disk JBD structs come from `ext4_types.h`.
- Implemented by `ext4_journal.c`; used by `ext4.c` and `ext4_trans.c`.

Research notes:
- Live transaction ownership is per filesystem LBA, allowing later transactions to supersede earlier dirty buffers during checkpointing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_journal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_misc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_misc.h

Miscellaneous arithmetic and endian-conversion helper header.

Key behavior:
- Defines `EXT4_DIV_ROUND_UP` and `EXT4_ALIGN`.
- Implements byte-swap helpers for 16-, 32-, and 64-bit integers.
- Defines host-to/from little-endian and big-endian macros based on `CONFIG_BIG_ENDIAN`.
- Defines field accessor/setter macros for ext4 little-endian structures and JBD big-endian structures.

Notable dependencies:
- Included by most ext4srv modules that touch on-disk fields.

Research notes:
- The `to_le*`/`to_be*` names are symmetric conversion macros: on little-endian hosts `to_le` is identity and `to_be` swaps; on big-endian hosts the reverse applies.
- `ext4_set8` and `jbd_set8` are formatted oddly as multi-token macros but are not prominent in the code read here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_mkfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_mkfs.h

Mkfs parameter and auxiliary-layout header.

Key behavior:
- `ext4_mkfs_info` stores requested/derived filesystem length, block size, blocks per group, inodes per group, inode size/count, journal size, feature masks, reserved descriptor blocks, descriptor size, UUID, journal flag, and label.
- `fs_aux_info` stores allocated superblock and group descriptor buffers plus derived layout values such as first data block, block count, inode table blocks, group count, descriptor blocks, default inode flags, and indirect block geometry.
- Declares aux-info creation/release, superblock writing, existing-filesystem info readback, and `ext4_mkfs`.

Notable dependencies:
- Includes `ext4_blockdev.h` and `ext4_fs.h`.
- Implemented by `ext4_mkfs.c`.

Research notes:
- `fs_aux_info::xattrs` is present but unused in the read implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_mkfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_super.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_super.h

Superblock accessor and validation API header.

Key behavior:
- Provides inline getters/setters for 64-bit block counts and free block counts.
- Provides inline block size and descriptor size helpers.
- Provides inline checks for superblock flags, compatible features, incompatible features, read-only-compatible features, flex group ID/size, and first meta block group.
- Declares group-count, per-group block/inode count, superblock read/write/check, sparse-super presence, group descriptor backup count, base metadata cluster count, and checksum setter functions.

Notable dependencies:
- Includes `ext4_types.h` and `ext4_misc.h`.
- Implemented by `ext4_super.c`; used throughout ext4srv.

Research notes:
- Descriptor size is clamped upward to the 32-byte minimum, while full validation rejects sizes above the 64-byte maximum.
- Feature check helpers return boolean results from bit tests on little-endian on-disk fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_trans.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_trans.h

Transaction wrapper API header for metadata block access and dirty/revoke operations.

Key behavior:
- Declares `ext4_trans_set_block_dirty` for routing dirty buffers into the active transaction or cache.
- Declares transaction-aware cached block get functions with and without read.
- Declares `ext4_trans_try_revoke_block` for revoking or flushing a logical block address.

Notable dependencies:
- Includes `ext4_config.h` and `ext4_types.h`.
- Implemented by `ext4_trans.c`.

Research notes:
- The comments mention write-access acquisition, but the implementation currently only delegates block fetches and handles dirty/revoke semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_trans.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_types.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_types.h

Primary on-disk ext4 and JBD type-definition header. It defines ext block number typedefs, superblock, group descriptor, inode, directory, htree, extent, and journal structures, plus most ext4/JBD feature bits and constants.

Key behavior:
- Defines `ext4_lblk_t` and `ext4_fsblk_t`, checksum and UUID constants, and maps allocation macros to Plan 9 libc allocation routines.
- Defines packed `ext4_sblock` with standard ext4 superblock fields through checksum.
- Defines ext4 magic, superblock size/offset, OS IDs, filesystem flags, filesystem states, error behavior, compatible/read-only/incompatible feature masks, supported feature masks for ext2/ext3/ext4, and ignored incompatible masks.
- Defines packed `ext4_bgroup`, descriptor sizes, block size limits, inode block constants, and packed `ext4_inode`.
- Defines inode modes and inode flags.
- Defines directory entry file types, directory entry and htree root/node/tail structures, checksum tail structures, special inode numbers, link max, and htree hash constants.
- Defines packed extent tail, extent, extent index, and extent header structures and extent magic.
- Defines JBD magic, block types, block header, checksum types, commit header, block tags, tag flags, descriptor/revoke tails, revoke header, journal superblock, and JBD feature masks.

Notable dependencies:
- Includes `ext4_blockdev.h` and `tree.h`, making this central header mutually important to the rest of ext4srv.
- Consumed by nearly every implementation and public header.

Research notes:
- Structures are packed with Plan 9 `#pragma pack on/off` to match disk layout.
- The supported ext4 feature mask includes features later disabled by `ext4_mkfs`, because mount/read support and mkfs defaults are handled separately.
- The ignored feature comment says journaling is not supported, which is stale relative to this batch's JBD implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_types.h -->