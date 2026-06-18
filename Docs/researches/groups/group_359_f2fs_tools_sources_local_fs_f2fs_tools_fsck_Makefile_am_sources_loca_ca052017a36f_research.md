# Group Research: group_359_f2fs_tools_sources_local_fs_f2fs_tools_fsck_Makefile_am_sources_loca_ca052017a36f

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/f2fs-tools`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/Makefile.am -->
# File Research: sources/local-fs/f2fs-tools/fsck/Makefile.am

## Purpose
Autotools build definition for the `fsck.f2fs` binary and its symlinked tool modes: `dump.f2fs`, `defrag.f2fs`, `resize.f2fs`, `sload.f2fs`, `f2fslabel`, and `inject.f2fs`.

## Key contents
- Builds `fsck.f2fs` from the fsck tool sources: `main.c`, `fsck.c`, `dump.c`, `mount.c`, `defrag.c`, `resize.c`, `node.c`, `segment.c`, `dir.c`, `sload.c`, `xattr.c`, `compress.c`, quota sources, and `inject.c`.
- Installs private headers used by this tool directory, including `fsck.h`, `f2fs.h`, `dict.h`, quota headers, `compress.h`, `inject.h`.
- Links against configured optional libraries:
  - `libselinux`
  - `libuuid`
  - `liblzo2`
  - `liblz4`
  - `libwinpthread`
  - local `libf2fs.la`

## Integration notes
The multiple installed command names are symlinks to the same executable. Runtime dispatch is therefore expected to happen in `main.c` based on argv/tool name or options.

## Research notes
This file is purely build/install wiring. It establishes that the fsck directory is a multi-tool frontend sharing the same F2FS mount, metadata, directory, quota, compression, dump, resize, defrag, and injection code.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/common.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/common.h

## Purpose
Small quota/common utility header providing logging macros and compiler attribute compatibility.

## Key contents
- Header guard: `__QUOTA_COMMON_H__`.
- Undefines `DEBUG_QUOTA` by default.
- Defines `__attribute__(x)` away for older/non-GNU compilers under strict conditions.
- Provides:
  - `log_err(format, arg...)`: prints file, line, function, and error message to stderr.
  - `log_debug(format, arg...)`: enabled only if `DEBUG_QUOTA` is defined; otherwise compiles to nothing.

## Dependencies
Uses standard `fprintf`, `stderr`, and `__FILE__`, `__LINE__`, `__func__` assumptions from including translation units.

## Research notes
Despite living in `fsck/`, this header is quota-oriented support code. It does not carry F2FS-specific structures.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/common.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/compress.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/compress.c

## Purpose
Compression support for `sload.f2fs`, plus filename-extension compression filtering.

## Key functionality
- Optional LZO support under `HAVE_LIBLZO2`:
  - Allocates one private buffer containing work memory, raw input buffer, and compressed output buffer.
  - Uses `lzo1x_1_15_compress`.
  - Stores compressed length in little-endian `compress_data.clen`.
- Optional LZ4 support under `HAVE_LIBLZ4`:
  - Allocates one private buffer containing LZ4 state, raw input buffer, and compressed output buffer.
  - Uses `LZ4_compress_fast_extState`.
  - Enforces a max compressed output size based on `c.compress.min_blocks` and `COMPRESS_HEADER_SIZE`.
- `reset_cc()` clears read and compressed buffers for a compression cluster.
- Exposes compression name and ops arrays:
  - `supported_comp_names[] = { "lzo", "lz4", "" }`
  - `supported_comp_ops[]` with NULL operation entries when a library is not compiled in.
- Implements extension filter operations through `ext_filter`:
  - Maintains a linked list of extensions.
  - `add` registers an extension once.
  - `filter` compares path extension against allow/deny mode using `c.compress.filter`.
  - `destroy` frees list nodes.

## Dependencies
- Includes `f2fs.h` and `compress.h`.
- Depends on global config `c.compress`.
- Depends on F2FS constants/types from `f2fs_fs.h`, such as `F2FS_BLKSIZE`, `COMPRESS_HEADER_SIZE`, `compress_ctx`, `compress_data`, `compress_ops`, and `filter_ops`.

## Important behavior
The filter logic uses XOR against `COMPR_FILTER_ALLOW`; this means the same extension list can act as either allow-list or deny-list depending on global compression settings.

## Research notes
The compression buffers are manually laid out inside one allocation. Any changes to cluster size, compression header size, or library work size affect memory layout and must preserve alignment and room for worst-case compressed data.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/compress.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/compress.h

## Purpose
Public declarations for fsck/sload compression support.

## Key contents
- Includes `f2fs_fs.h`.
- Declares:
  - `supported_comp_names[]`
  - `supported_comp_ops[]`
  - `ext_filter`

## Dependencies
The declared types `compress_ops` and `filter_ops` come from the shared F2FS userspace headers.

## Research notes
This is a narrow interface header. Implementation details and optional library handling are confined to `compress.c`.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/compress.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/defrag.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/defrag.c

## Purpose
Implements block migration for `defrag.f2fs`.

## Key functionality
- `migrate_block(sbi, from, to)`:
  - Reads one block from `from`.
  - Gets source segment type from SIT cache.
  - Writes the block to `to` with an F2FS write-life hint based on segment type.
  - Updates source and destination segment valid-block counters and valid maps.
  - Copies SSA summary from old block to new block.
  - Updates owner metadata:
    - data blocks update the owning node address via `update_data_blkaddr`.
    - node blocks update NAT via `update_nat_blkaddr`.
- `f2fs_defragment(sbi, from, len, to, left)`:
  - Flushes NAT/SIT journal entries before migration.
  - Iterates valid blocks in source range.
  - Finds free target blocks with `find_next_free_block`.
  - Migrates each valid source block.
  - Moves current segment info, zeroes journals, writes current segment info, flushes dirty SIT entries, then writes checkpoint.

## Dependencies
Uses fsck/mount/segment-layer helpers:
- `get_seg_entry`
- `get_sum_entry`
- `update_sum_entry`
- `update_data_blkaddr`
- `update_nat_blkaddr`
- `find_next_free_block`
- `move_curseg_info`
- `zero_journal_entries`
- `write_curseg_info`
- `flush_sit_entries`
- `write_checkpoint`

## Research notes
This code mutates core allocation metadata directly. Correctness depends on summary/NAT/SIT consistency updates happening as a unit before checkpoint write.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/defrag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dict.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/dict.c

## Purpose
Embedded Kazlib dictionary implementation, using a red-black tree. In this tree, keys are ordered by a caller-supplied comparator and nodes carry arbitrary data pointers.

## Active fsck-facing functionality
With `DICT_NODEBUG` defined and many blocks under `FSCK_NOTUSED`, the actively compiled core includes:
- Dictionary initialization and allocator selection:
  - `dict_init`
  - `dict_set_allocator`
  - `dict_free_nodes`
- Lookup and insertion:
  - `dict_lookup`
  - `dict_insert`
  - `dict_alloc_insert`
- Traversal:
  - `dict_first`
  - `dict_last`
  - `dict_next`
  - `dict_prev`
- Duplicates and counts:
  - `dict_allow_dupes`
  - `dict_count`
  - `dict_isempty`
  - `dict_isfull`
  - `dict_contains`
- Node lifecycle/accessors:
  - `dnode_create`
  - `dnode_init`
  - `dnode_destroy`
  - `dnode_get`
  - `dnode_getkey`

## Implementation details
- Uses a sentinel nil node stored inside `dict_t`.
- Insertions are standard red-black tree insertions with left/right rotations.
- Duplicate key behavior is opt-in through `dict_allow_dupes`.
- Default node allocation uses `malloc`/`free`; callers can replace allocator hooks.

## Compiled-out sections
Large parts are guarded by `FSCK_NOTUSED`, including:
- dynamic `dict_create` / `dict_destroy`
- delete operations
- lower/upper bound
- sorted bulk load
- merge
- interactive test program under `KAZLIB_TEST_MAIN`

## Dependencies
- Includes `dict.h`.
- Includes `f2fs_fs.h` for the `UNUSED` macro used in allocator signatures.

## Research notes
This is vendored third-party utility code rather than F2FS-specific logic. The header declares a larger API than fsck actually compiles unless build flags enable `FSCK_NOTUSED` or debug/test modes, so new call sites should verify that a function is linked in the normal fsck build.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dict.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dict.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/dict.h

## Purpose
Public API and data structure declarations for the embedded Kazlib red-black-tree dictionary.

## Key structures
- `dnode_t`:
  - left/right/parent pointers
  - red/black color
  - key pointer
  - data pointer
- `dict_t`:
  - embedded nil sentinel
  - node count and max count
  - compare function
  - allocator/free callbacks and context
  - duplicate-key flag
- `dict_load_t`:
  - bulk-load helper state for sorted loading when compiled in.

## Key API groups
- Create/init/destroy/free:
  - `dict_create`, `dict_init`, `dict_destroy`, `dict_free_nodes`, `dict_free`
- Lookup/order:
  - `dict_lookup`, `dict_lower_bound`, `dict_upper_bound`, `dict_first`, `dict_last`, `dict_next`, `dict_prev`
- Mutation:
  - `dict_insert`, `dict_delete`, `dict_alloc_insert`, `dict_delete_free`, `dict_merge`
- Node:
  - `dnode_create`, `dnode_init`, `dnode_destroy`, `dnode_get`, `dnode_getkey`, `dnode_put`
- Utilities:
  - `dict_allow_dupes`, `dict_count`, `dict_isempty`, `dict_isfull`, `dict_contains`, `dict_verify`

## Conditional behavior
When structures are not opaque, the header defines direct macro accessors for count/empty/full and node get/put/key operations. `DICT_IMPLEMENTATION` exposes internal layout to `dict.c`.

## Research notes
This header presents the full Kazlib API, but normal `dict.c` compilation in this tree disables several corresponding implementations. Treat the header as broader than the currently linked fsck subset.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dict.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dir.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/dir.c

## Purpose
Directory and inode creation support for `sload.f2fs` and fsck repair paths. Much of the logic mirrors Linux kernel F2FS directory handling.

## Key functionality
- Directory-entry layout helpers:
  - `make_dentry_ptr` abstracts block dentry vs inline dentry layouts.
  - `room_for_filename` finds consecutive free dentry slots.
  - `find_target_dentry`, `find_in_block`, `find_in_level`, and `f2fs_find_entry` implement hash-directory lookup.
  - `f2fs_lookup` returns inode number for a child name.
- Directory mutation:
  - `f2fs_update_dentry` fills dentry metadata and slot bitmap bits.
  - `f2fs_add_link` adds a child entry, allocating dentry data blocks and updating parent inode depth, size, and link count.
- New inode setup:
  - `make_empty_dir` creates `.` and `..`.
  - `page_symlink` stores symlink target inline or in a warm data block.
  - `set_file_temperature` marks hot/cold files based on superblock extension lists.
  - `init_inode_block` fills inode metadata, footer, inline flags, xattrs, timestamps, name, type, and checksum.
- Inline dentry conversion:
  - `convert_inline_dentry` expands inline directory entries into regular dentry blocks, preserving entries and adding them through normal directory insertion when needed.
- Hardlink cache:
  - Uses libc `tsearch` with `cmp_from_devino`.
  - `f2fs_search_hardlink` tracks source device+inode to F2FS inode mappings for `sload`.
- Creation/path APIs:
  - `f2fs_create`
  - `f2fs_mkdir`
  - `f2fs_symlink`
  - `f2fs_find_path`

## Dependencies
Heavily depends on:
- node helpers from `node.h`
- allocation/write helpers from `segment.c`
- metadata helpers from `fsck.h`
- global configuration `c`
- `f2fs_dentry_hash`, `get_dnode_of_data`, `new_data_block`, `reserve_new_block`, `update_block`, `update_inode`, `update_nat_blkaddr`

## Important behavior
- Directories must convert inline dentries before adding new entries.
- Zoned devices use `update_block` for existing dentry blocks to avoid invalid overwrite patterns.
- Hardlinks reuse the original inode and increment `i_links`; first occurrence records the mapping.

## Research notes
This file is central to repair-time reconnection and image loading. It must preserve F2FS hash-directory placement rules, inline layout rules, and NAT/SIT/summary consistency through helper calls.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dqblk_v2.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/dqblk_v2.h

## Purpose
Header for version-2 quota file format state.

## Key structures
- `struct v2_mem_dqinfo`:
  - embeds quota tree metadata `qtree_mem_dqinfo`
  - stores quota file flags
  - tracks used entries and data blocks, updated during dquot scanning
- `struct v2_mem_dqblk`:
  - stores offset of a dquot record in the quota file

## Key declarations
- Forward-declares `struct quotafile_ops`.
- Externs `quotafile_ops_2`, the operation table for this quota format.

## Dependencies
Includes `quotaio_tree.h`.

## Research notes
This file is quota-format plumbing. It does not implement quota logic itself; it declares format-specific in-memory structures used by quota IO code.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dqblk_v2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dump.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/dump.c

## Purpose
Implements `dump.f2fs` metadata dumps, file recovery/extraction, inode traversal, xattr restoration, and block-address diagnostics.

## Key functionality
- Metadata dump files:
  - `nat_dump` writes `dump_nat`.
  - `sit_dump` writes `dump_sit`.
  - `ssa_dump` writes `dump_ssa`.
- File/directory extraction:
  - `dump_node` validates NAT/SIT and node footer, prints node info, and dumps inode contents.
  - `dump_inode_blk` traverses inline data, inline dentries, direct addresses, direct nodes, indirect nodes, and double-indirect nodes.
  - `dump_data_blk` reads data blocks or recursively dumps directory contents.
  - `dump_file`, `dump_link`, and `dump_folder` create recovered filesystem objects.
  - `dump_filesystem` handles user prompting, base path creation, encrypted/nodump rejection, permission preservation, and recursive directory dumping.
- Xattr restore:
  - `dump_xattr` reads all xattrs, validates bounds, maps F2FS xattr indexes to platform prefixes, and sets xattrs on output files/directories/symlinks when supported.
- Diagnostics:
  - `dump_info_from_blkaddr` classifies an arbitrary block as reserved/metadata/SIT/NAT/SSA/user data, reads SSA summary, maps to NAT/node/inode, and optionally dumps dentry contents.
  - `dump_node_scan_disk` brute-force scans main-area node segments for a given inode/nid.
  - `start_bidx_of_node`, `dump_data_offset`, and `dump_node_offset` compute logical offsets from node offsets.

## Dependencies
Uses:
- `node.h`, `fsck.h`, `xattr.h`
- platform xattr headers when available
- global `c` dump options and file descriptors
- block IO helpers such as `dev_read_block`, `dev_write_dump`, `dev_write_symlink`
- F2FS metadata helpers: `get_node_info`, `get_sum_entry`, `get_sum_block`, `is_sit_bitmap_set`, `make_dentry_ptr`

## Important behavior
- Hard links are not reconstructed as hard links during dump; the code warns they may be duplicated.
- Encrypted files are refused because names/data cannot be safely interpreted.
- File map mode prints extents instead of writing file contents.
- Inline symlinks and inline regular data are handled before normal block traversal.

## Research notes
This file is read-mostly recovery tooling, but it still writes host filesystem output and may set ownership/mode/xattrs. Its F2FS-side writes are not part of normal dumping, aside from shared helper behavior elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/f2fs.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/f2fs.h

## Purpose
Core fsck-side F2FS runtime types, metadata accessors, list helpers, and address/layout macros.

## Key structures
- Lightweight Linux-style list primitives: `struct list_head` plus list add/delete/iterate macros.
- Metadata caches:
  - `struct node_info`
  - `struct f2fs_nm_info`
  - `struct seg_entry`
  - `struct sec_entry`
  - `struct sit_info`
  - `struct curseg_info`
  - `struct f2fs_sm_info`
- Directory/loading state:
  - `struct f2fs_dentry_ptr`
  - `struct dentry`
  - `struct dnode_of_data`
  - `struct hardlink_cache_entry`
- Main fsck mount/runtime state:
  - `struct f2fs_sb_info`

## Key helpers/macros
- Accessors:
  - `F2FS_RAW_SUPER`
  - `F2FS_CKPT`
  - `F2FS_FSCK`
  - `NM_I`
  - `SM_I`
  - `SIT_I`
  - `CURSEG_I`
- Checkpoint/bitmap helpers:
  - `cur_cp_version`
  - `cur_cp_crc`
  - `set_ckpt_flags`
  - `is_set_ckpt_flags`
  - `__bitmap_size`
  - `__bitmap_ptr`
  - `__start_cp_addr`
  - `__start_sum_addr`
- Address mapping:
  - `MAIN_BLKADDR`
  - `SEG0_BLKADDR`
  - `GET_SUM_BLKADDR`
  - `GET_SUM_BLKOFF`
  - `GET_SEGNO`
  - `OFFSET_IN_SEG`
  - `START_BLOCK`
  - `MAX_BLKADDR`
  - `BLKOFF_FROM_MAIN`
- Segment/type helpers:
  - `IS_DATASEG`
  - `IS_NODESEG`
  - `IS_CUR_SEGNO`
- Directory hashing geometry:
  - `dir_buckets`
  - `bucket_blocks`
  - `dir_block_index`
  - `is_dot_dotdot`
- Inline data/xattr helpers:
  - `inline_data_addr`
  - `inline_xattr_addr`
  - `inline_xattr_size`

## External declarations
Declares journal lookup helpers:
- `lookup_nat_in_journal`
- `lookup_sit_in_journal`

## Research notes
This header is the main fsck-local bridge between raw on-disk F2FS definitions from `f2fs_fs.h` and mutable userspace state. Many C files in this directory depend on these macros, so address-calculation changes here have broad blast radius.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/f2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/fsck.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/fsck.c

## Purpose
Main consistency checker and repair engine for `fsck.f2fs`. It validates and repairs relationships among NAT, SIT, SSA summaries, checkpoint counters, inode/node/data trees, dentries, xattrs, quota files, orphan inodes, hard links, lost+found reconnection, and zoned-device write pointers.

## Major responsibilities
- Bitmap accounting:
  - Maintains reconstructed main-area usage bitmap.
  - Maintains NAT-derived nid bitmap.
  - Maintains SIT-derived valid-block bitmap.
  - Compares reconstructed state against on-disk metadata during verification.
- Node/NAT/SSA validation:
  - `sanity_check_nat`
  - `sanity_check_nid`
  - `is_valid_ssa_node_blk`
  - `is_valid_ssa_data_blk`
  - Repairs summary entries when `c.fix_on` is enabled and safe.
- Inode tree traversal:
  - `fsck_chk_node_blk`
  - `fsck_chk_inode_blk`
  - `fsck_chk_dnode_blk`
  - `fsck_chk_idnode_blk`
  - `fsck_chk_didnode_blk`
  - Traverses inline data, inline dentries, direct addresses, direct nodes, indirect nodes, and double-indirect nodes.
- Data block validation:
  - `fsck_chk_data_blk` validates block address, summary entry, SIT bitmap, duplicate block usage, and recursively checks directory blocks.
- Directory validation:
  - Checks dentry NIDs, file types, name lengths, hash codes, hash-directory placement, duplicate `.`/`..`, and child inode consistency.
  - Can clear bad dentries and rewrite fixed dentry blocks.
- Inode repair:
  - Fixes invalid `i_links`, `i_blocks`, compression flags/counts, inline-data reserve addresses, inline sizes, casefold flags, extra attribute sizes, xattr tail garbage, extent info, symlink size, inode checksum, and orphan link counts.
- Hard links:
  - Tracks multi-link files through `hard_link_node`.
  - Detects missing/unreachable links.
  - `fix_hard_links` rewrites actual link counts.
- Quotas:
  - Checks quota inodes with `fsck_chk_quota_node`.
  - Compares and rebuilds quota files through `fsck_chk_quota_files`.
- Orphans:
  - `fsck_chk_orphan_node` validates orphan block entries and can remove invalid ones.
- Metadata/global repair:
  - `fsck_chk_meta`
  - `fsck_chk_checkpoint`
  - `fix_nat_entries`
  - `rewrite_sit_area_bitmap`
  - `fix_checkpoint`
  - `fix_checkpoints`
  - `fix_checksum`
- Lost+found:
  - Reconnects valid unreachable non-directory inodes when the lost+found feature is present.
  - Creates or finds `lost+found`, adds links, updates inode name and parent.
- Zoned devices:
  - Checks current segment offsets against write pointers.
  - Can reset or finish zones and realign SIT/write-pointer state.

## Important entry points
- `fsck_init`: allocates fsck bitmaps and dentry traversal state.
- `fsck_chk_meta`: validates metadata counters and NAT/SIT consistency before full verification.
- `fsck_chk_node_blk`: root recursive checker for an inode/node block.
- `fsck_chk_data_blk`: validates and accounts one data block.
- `fsck_chk_orphan_node`: validates checkpoint orphan lists.
- `fsck_chk_quota_node` / `fsck_chk_quota_files`: quota checks and repair.
- `fsck_chk_and_fix_write_pointers`: early zoned-device write-pointer repair.
- `fsck_chk_curseg_info`: validates current segment SIT/SSA types.
- `fsck_verify`: final consistency summary and global repair decision point.
- `fsck_free`: releases allocated fsck state.

## Dependencies
Includes:
- `fsck.h`
- `xattr.h`
- `quotaio.h`
- `<time.h>`

Relies broadly on other fsck modules:
- mount/segment helpers for NAT/SIT/SSA/checkpoint IO
- dir helpers for dentry creation and lost+found linking
- xattr helpers for xattr validation/writeback
- quota helpers for quota accounting/rebuild
- dump helpers for optional lost-file extraction
- zoned-device helpers when compiled with Linux zoned block support

## Repair model
Most repairs are gated by:
- `c.fix_on`
- `f2fs_dev_is_writable()`
- metadata-specific safety checks

The checker often updates in-memory node blocks unconditionally to continue traversal safely, but writes back only when repair mode and writable device state allow it.

## Research notes
This is the highest-risk file in the group. It encodes the cross-metadata invariants of F2FS userspace fsck: every traversal updates reconstructed counters/bitmaps, and final verification compares those against checkpoint/SIT/NAT state before choosing whether to rewrite global metadata.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/fsck.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/fsck.h

## Purpose
Primary public header for fsck/dump/defrag/sload/resize shared declarations.

## Key constants/enums
- Fsck exit/status bits:
  - corrected errors
  - reboot required
  - uncorrected errors
  - operational error
  - usage error
  - user cancelled
  - shared library error
- Fsck inode/extent flags:
  - `FSCK_UNMATCHED_EXTENT`
  - `FSCK_INLINE_INODE`
- Preen modes:
  - `PREEN_MODE_0`
  - `PREEN_MODE_1`
  - `PREEN_MODE_2`
- Superblock copy identifiers:
  - `SB0_ADDR`
  - `SB1_ADDR`

## Key structures
- `struct orphan_info`: orphan inode list.
- `struct extent_info`: compact extent tuple.
- `struct child_info`: traversal state for directory/inode recursion, parent relationship, dot/dotdot counts, extent tracking, directory level, and name length.
- `struct f2fs_dentry`: linked stack used for dentry tree printing/file map output.
- `struct f2fs_fsck`: fsck runtime state, including:
  - embedded `f2fs_sb_info`
  - orphan state
  - check counters
  - hard-link tracking
  - main/NAT/SIT bitmaps
  - NAT entry cache
  - dentry traversal state
  - quota context
- `struct hard_link_node`: tracks expected vs actual links.
- `struct dump_option`: CLI/options for dump mode.

## Function declarations
Declares cross-module APIs for:
- fsck checking and verification
- metadata bitmap construction/rewrite
- NAT/SIT/SSA access and update
- current segment and checkpoint updates
- dump commands
- defrag, resize, sload
- file/directory creation
- xattr read/write
- node update
- journal flushing
- command-line helper `is_digits`

## Dependencies
Includes `f2fs.h`, so it also brings in raw F2FS disk definitions and fsck-local metadata structures.

## Research notes
This header is the central coupling point for the fsck tools directory. It exposes many implementation-level helpers across modules, which explains why `fsck.c`, `dir.c`, `dump.c`, `defrag.c`, and segment/mount code are tightly linked.
<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/fsck.h -->