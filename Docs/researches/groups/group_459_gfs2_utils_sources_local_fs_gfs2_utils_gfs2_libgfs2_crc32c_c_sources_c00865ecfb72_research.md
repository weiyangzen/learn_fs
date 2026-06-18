# Group Research: group_459_gfs2_utils_sources_local_fs_gfs2_utils_gfs2_libgfs2_crc32c_c_sources_c00865ecfb72

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/crc32c.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/crc32c.c

This file implements CRC-32C calculation for libgfs2, copied from btrfs-progs/kernel code.

Main behavior:
- Provides `crc32c(seed, data, length)`.
- Defaults to table-driven little-endian CRC-32C via `__crc32c_le()`.
- On `__x86_64__`, can switch to Intel SSE4.2 CRC instructions after `crc32c_optimization_init()`.
- Uses `cpuid` ECX bit 20 to detect hardware CRC32 support.
- Avoids hardware word-sized path for unaligned input buffers and falls back to byte-table CRC.

Integration role:
- Used by journal log-header CRC code in `structures.c`.
- Exposed through `crc32c.h`.

State and ownership:
- Maintains static function pointer `crc_function`.
- Maintains static x86 probe state: `crc32c_probed`, `crc32c_intel_available`.
- Does not allocate memory.

Risk notes:
- x86 hardware path uses inline assembly and casts input to `unsigned long *`; alignment check in `crc32c()` is important.
- Probe state is global and not synchronized, though benign for typical single-threaded tool use.
- CRC semantics must remain compatible with GFS2 on-disk journal checksums.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/crc32c.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/crc32c.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/crc32c.h

Small public header for CRC-32C support.

Exports:
- `uint32_t crc32c(uint32_t seed, unsigned char const *data, size_t length);`
- `void crc32c_optimization_init(void);`

Integration role:
- Included by `structures.c` for GFS2 journal log-header CRC generation.
- Pulls in `stdlib.h` and `inttypes.h`.

Risk notes:
- Signature changes affect journal checksum generation.
- Header does not document seed/finalization expectations; callers must follow existing CRC-32C usage.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/crc32c.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/device_geometry.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/device_geometry.c

This file gathers device/file geometry for GFS2 tools.

Public APIs:
- `lgfs2_get_dev_info(fd, info)`: fills `lgfs2_dev_info` from `fstat()`, block ioctls, access mode, and file/device size.
- `lgfs2_fix_device_geometry(sdp)`: converts byte size to filesystem-block count in `sdp->device.length`.

Behavior:
- Accepts regular files and block devices.
- Rejects other file types with `ENOTBLK`.
- For regular files, uses `st_size`, `F_GETFL`, and `st_blksize`.
- For block devices, probes read-ahead, logical/physical block sizes, IO alignment, readonly state, and size via `lseek(SEEK_END)`.
- Rejects devices smaller than 1 MiB with `ENOSPC`.

Risk notes:
- Several ioctls are best-effort and unchecked; unavailable values remain zero.
- `lseek(SEEK_END)` determines block-device size, so unusual devices may fail.
- `lgfs2_fix_device_geometry()` assumes `sdp->sd_bsize` is initialized.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/device_geometry.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/fs_bits.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/fs_bits.c

This file implements GFS2 allocation bitmap search and block-state get/set helpers.

Public APIs:
- `lgfs2_blkst_str()`: maps bitmap state constants to names.
- `lgfs2_bitfit()`: finds the next block with a requested two-bit bitmap state.
- `lgfs2_check_range()`: validates a filesystem block number against superblock limits.
- `lgfs2_set_bitmap()`: updates an rgrp bitmap entry and marks the bitmap dirty.
- `lgfs2_get_bitmap()`: reads a block state from a resource group bitmap.

Important behavior:
- `lgfs2_bitfit()` scans 64 bits at a time using two-bit state matching.
- Bitmap entries encode four block states: free, used, unlinked, dinode.
- `lgfs2_get_bitmap()` can locate the resource group itself or accept one from the caller.
- First bitmap block has a different metadata header size than later bitmap blocks; offset calculations account for that.

Integration role:
- Used by block allocation, resource-group scanning, grow, mkfs, and directory/file allocation flows.

Risk notes:
- Bitmap math is dense and relies on correct `rt_bits`, `bi_start`, `bi_len`, `bi_offset`, and `sd_blocks_per_bitmap`.
- Range check treats blocks at or below the superblock address as invalid.
- `lgfs2_get_bitmap()` returns free for an unloaded `bi_data`, which callers must understand.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/fs_bits.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/fs_ops.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/fs_ops.c

This is libgfs2's core inode, block mapping, file I/O, and directory operation implementation.

Major API families:
- Inode lifecycle: `lgfs2_inode_get()`, `lgfs2_inode_read()`, `lgfs2_inode_put()`, `lgfs2_inode_free()`, `lgfs2_is_system_inode()`.
- Allocation: `lgfs2_dinode_alloc()`, `lgfs2_meta_alloc()`, `lgfs2_file_alloc()`, `lgfs2_free_block()`.
- File layout: `lgfs2_space_for_data()`, `lgfs2_calc_tree_height()`, `lgfs2_build_height()`, `lgfs2_find_metapath()`, `lgfs2_lookup_block()`, `lgfs2_block_map()`, `lgfs2_unstuff_dinode()`.
- File I/O: `lgfs2_readi()`, `__lgfs2_writei()`, `lgfs2_write_filemeta()`.
- Directory operations: `lgfs2_init_dinode()`, `lgfs2_createi()`, `lgfs2_dir_add()`, `lgfs2_dir_search()`, `lgfs2_lookupi()`, `lgfs2_dirent_del()`, `lgfs2_dir_split_leaf()`, `lgfs2_get_leaf_ptr()`, `lgfs2_get_leaf()`, `lgfs2_dirent_first()`, `lgfs2_dirent_next()`, `lgfs2_dirent2_del()`.

Important behavior:
- Supports stuffed inodes and unstuffs them when data no longer fits in the dinode body.
- Builds indirect metadata trees on demand for files and journaled-data directories.
- Allocates blocks from resource groups and updates bitmap state, free counts, dinode counts, and superblock accounting.
- Implements linear directories and extended-hash directories.
- Converts stuffed directories to exhash form, doubles hash tables, splits leaves, and chains overflow leaves.
- Initializes new directory dinodes with `.` and `..`.
- `lgfs2_lookupi(".")` returns the input directory inode itself.

Integration role:
- Central implementation behind mkfs, grow, jadd, fsck/edit-like tools, journal construction, metadata language access, and superblock/rindex handling.
- Depends on buffer I/O, bitmap helpers, resource groups, disk hash, and ondisk conversion helpers.

State and ownership:
- `lgfs2_inode_read()` returns an inode owning its buffer head.
- `lgfs2_inode_put()` writes modified in-core dinode fields back into the buffer, releases owned buffers, and frees the inode.
- `lgfs2_inode_free()` discards modifications.
- Directory mutation marks affected inode and leaf buffers modified.

Risk notes:
- This file mutates on-disk metadata directly; allocation, endian conversion, and dirty-buffer handling are high risk.
- Directory splitting and exhash growth contain subtle record-length and entry-count invariants.
- `lgfs2_lookupi(".")` returns an existing inode pointer, so ownership differs from ordinary lookup results.
- `lgfs2_file_alloc()` assumes contiguous extent allocation and is used for mkfs-style construction.
- Error paths can leave partially allocated blocks or directory entries if callers do not recover.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/fs_ops.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/gfs2_disk_hash.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/gfs2_disk_hash.c

This file implements GFS2's on-disk directory/hash CRC.

Public API:
- `lgfs2_disk_hash(const char *data, int len)`

Behavior:
- Uses a standard CRC-32 table.
- Starts with `0xffffffff`, updates per byte, then bitwise complements the result.
- Must match kernel `crc32_le(0xFFFFFFFF, data, len) ^ 0xFFFFFFFF`.

Integration role:
- Used for directory entry hashes.
- Used for metadata checks such as resource group CRC and log-header hash.

Risk notes:
- Signed `char` promotion can matter if changed; current implementation uses `(hash ^ *data) & 0xff`.
- Any change breaks directory lookup compatibility and metadata checksum validation.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/gfs2_disk_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/gfs2l.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/gfs2l.c

This is the command-line frontend for the small GFS2 metadata language implemented by `lang.c`, `lexer.l`, and `parser.y`.

Behavior:
- Supports `-h`, `-f <script>`, `-T`, and `-F <type>`.
- `-T` prints known metadata structure types sorted by name.
- `-F <type>` prints field offsets and names for one metadata type.
- Opens the target filesystem/device read-write.
- Reads device info, superblock, master directory, and rindex.
- Initializes the language parser, parses the script, iterates results, prints them, and frees state.

Integration role:
- Uses libgfs2 superblock, inode, rindex, metadata table, and language interpreter APIs.
- Provides a direct metadata query/edit tool surface.

Risk notes:
- Opens the filesystem with `O_RDWR`; scripts can modify metadata.
- Some error paths return without closing all descriptors or freeing all state.
- `opts.fspath` is populated but `openfs()` uses `argv[optind]`, so option parsing assumptions matter.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/gfs2l.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/lang.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/lang.c

This file implements AST creation, AST interpretation, block lookup, field printing, and metadata assignment for the GFS2 language.

Public APIs:
- `ast_new()`, `ast_destroy()`
- `lgfs2_lang_result_next()`
- `lgfs2_lang_result_print()`
- `lgfs2_lang_result_free()`

Main behavior:
- Converts lexer tokens into AST nodes with numeric/string/path values.
- Resolves block references by absolute address, named IDs (`sb`, `master`, `root`, `rindex`), paths, resource group subscript (`rgrp[n]`), and offsets.
- `get` reads a block, detects metadata type, and prints all known fields.
- `get ... state` returns allocation bitmap state.
- `set` reads a block, optionally writes a metadata header for an explicit type, assigns listed fields, and writes the block back.
- Field printing handles UUIDs, strings, and 1/2/4/8-byte big-endian numeric values.
- Field assignment handles UUID parsing, bounded strings, and big-endian numeric storage.

Integration role:
- Consumes metadata descriptions from `meta.c`.
- Uses libgfs2 inode lookup, block reads, bitmap access, resource group reads, and field assignment helpers.
- Used by `gfs2l.c`.

State and ownership:
- Results own `lr_buf` and are released by `lgfs2_lang_result_free()`.
- AST nodes own duplicated text/string buffers.
- Path lookup mutates the stored path string through `strtok_r()` and unescaping.

Risk notes:
- Path lookup destructively tokenizes `ast_str`, so reusing the same AST path can behave differently.
- `set` writes metadata directly and has no transaction/recovery wrapper.
- Numeric parsing uses `sscanf(... SCNi64)` into a `uint64_t` field through a mismatched signed format expectation.
- Result iteration stops on the first failing statement and does not continue.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/lang.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/lang.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/lang.h

Header for the GFS2 metadata language.

Defines:
- `struct lgfs2_lang_state`: parser/interpreter cursor and error location state.
- `struct lgfs2_lang_result`: block number, block buffer, metadata type, or bitmap state.
- `ast_node_t`: statement, expression, and keyword node types.
- AST interpreter status constants.
- `struct ast_node`: binary AST node with text/string/numeric payloads.
- `YYSTYPE` as `struct ast_node *` for bison/flex integration.

Exports:
- Language init/parse/result/free APIs.
- AST allocation/destruction APIs.
- `ast_type_string[]`.

Risk notes:
- This header couples parser, lexer, interpreter, and libgfs2 metadata definitions.
- AST ownership is manual and recursive.
- C++-style `//` comments appear in a C header; build mode must tolerate them.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/lang.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/lexer.l -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/lexer.l

Flex lexer for the GFS2 metadata language.

Recognized tokens:
- Punctuation: `{}`, `[]`, comma, colon, semicolon.
- Keywords: `set`, `get`, `state`.
- Values: decimal/hex numbers, signed offsets, identifiers, single-quoted strings, single-quoted absolute paths.
- Comments: `//...` and `#...`.
- Whitespace/newlines with line/column tracking.

Behavior:
- Allocates AST nodes directly for meaningful tokens via `ast_new()`.
- Stores lexer extra data as `struct lgfs2_lang_state *`.
- Increments `ls_linenum` and resets `ls_colnum` on newline/comment.
- Strips surrounding quotes for strings and paths before creating AST nodes.

Integration role:
- Emits tokens used by `parser.y`.
- Uses bison bridge/reentrant scanner mode.

Risk notes:
- `]` returns a token carrying an `AST_EX_SUBSCRIPT` node, which parser actions depend on.
- Unexpected characters print using `yylineno`, while line tracking otherwise uses custom state fields.
- String/path escaping is minimal and later unescaped by interpreter code.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/lexer.l -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/libgfs2.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/libgfs2.h

This is the main public/internal libgfs2 header.

Content:
- Endian conversion macros for big/little endian hosts.
- Metadata type enum and metadata/field descriptor structures.
- Device, bitmap, resource-group, buffer-head, inum, inode, metadata-directory, superblock, log-header, dirent, leaf, and metapath structures.
- Defaults and bounds for block size, journal size, resource group size, lock protocol, and filesystem format.
- Prototypes for metadata description, buffer I/O, device geometry, bitmap operations, fs ops, misc helpers, recovery, rgrp management, structure builders, superblock/rindex I/O, disk hash, and ondisk conversion.

Integration role:
- Central include for most libgfs2 and mkfs/grow/jadd code.
- Bridges Linux `gfs2_ondisk.h` structures with userland in-core representations.

Risk notes:
- Struct layout and prototypes define broad cross-file contracts.
- Endian macros depend on `__BYTE_ORDER`.
- `LGFS2_SB_ADDR(sdp)` depends on computed `sd_fsb2bb_shift`.
- Many functions expose raw block numbers and direct metadata mutation, so caller invariants are important.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/libgfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/meta.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/meta.c

This file defines metadata schemas, symbolic tables, lookup helpers, formatting, and assignment for GFS2 on-disk structures.

Major data:
- Symbol tables for metatypes, metaformats, dinode flags, log-header flags, and log descriptor types.
- `lgfs2_metadata[]`: schemas for superblock, rindex, rgrp, rgrp bitmap, dinode, indirect, leaf, journal data, log header/descriptor/block, EA blocks, quota change, dirent, EA header, inum range, statfs change, data, and free blocks.
- Per-field metadata: name, offset, length, flags, pointer target types, symbol tables.

Public APIs:
- `lgfs2_find_mfield_name()`
- `lgfs2_find_mtype()`
- `lgfs2_find_mtype_name()`
- `lgfs2_field_str()`
- `lgfs2_flag_sym_value()`
- `lgfs2_field_assign()`

Integration role:
- Drives `gfs2l`, field rendering, field assignment, metadata inspection, and structure listing.
- Uses kernel on-disk structure definitions for offsets and sizes.

Risk notes:
- Schema tables must match `linux/gfs2_ondisk.h` exactly.
- `lgfs2_find_mtype()` returns first matching `mh_type`; multiple historical GFS/GFS2 entries in the enum would require care.
- `lgfs2_field_assign()` reads `uint64_t num = *(uint64_t *)val` before checking UUID/string flags, so callers must pass sufficiently aligned/sized memory for numeric paths.
- String field assignment rejects strings that fill the full field length.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/meta.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/misc.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/misc.c

This file contains filesystem constant calculation and mount/device opening helpers.

Public APIs:
- `lgfs2_compute_heightsize()`
- `lgfs2_compute_constants()`
- `lgfs2_open_mnt()`
- `lgfs2_open_mnt_dev()`
- `lgfs2_open_mnt_dir()`

Behavior:
- Computes max file/journal tree heights and size coverage per metadata height.
- Initializes common superblock-derived constants such as pointer counts, hash sizes, journal block size, and bitmap block coverage.
- Scans `/proc/mounts` for mounted GFS2 filesystems.
- Matches a user path against mount dir, device name, same block device, or same file identity.
- Returns open fds for mount directory and backing device as requested.

Risk notes:
- `lgfs2_open_mnt()` returns success with `*mnt == NULL` when path is not a mounted GFS2 filesystem and closes `dirfd`; callers must distinguish this.
- If `open(path)` succeeds but `setmntent()` later paths fail, fd cleanup is caller-sensitive.
- `fdcmp()` treats block-device identity through `st_rdev` and regular identity through `st_dev/st_ino`.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/ondisk.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/ondisk.c

This file converts selected GFS2 on-disk structures between big-endian disk format and libgfs2 in-core structures.

Public APIs:
- `lgfs2_inum_in/out()`
- `lgfs2_sb_in/out()`
- `lgfs2_rindex_in/out()`
- `lgfs2_rgrp_in/out()`
- `lgfs2_dinode_in/out()`
- `lgfs2_dirent_in/out()`
- `lgfs2_leaf_in/out()`

Behavior:
- Reads and writes superblock fields, inums, resource-group index fields, resource-group fields, dinode fields, dirent fields, and leaf fields.
- Output helpers set metadata header magic/type/format where applicable.
- `lgfs2_rgrp_out()` recomputes resource group CRC after writing fields.

Integration role:
- Used throughout libgfs2 for reading existing metadata and writing modified/created metadata.
- Provides the endian boundary between userland native structs and Linux GFS2 on-disk structs.

Risk notes:
- Every field conversion must remain synchronized with on-disk structure definitions.
- `lgfs2_leaf_in/out()` assumes leaf hint fields exist in the compiled kernel header layout.
- `lgfs2_dinode_out()` writes in-core header values rather than hardcoding them, so inode initialization must set those correctly.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/ondisk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/parser.y -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/parser.y

Bison parser and parse-state implementation for the GFS2 metadata language.

Grammar:
- Script is semicolon-separated statements.
- Statements: `set <blockspec> [<typespec>] { field: value, ... }` and `get <blockspec> [state]`.
- Block specs can be offsets, numeric addresses, paths, identifiers, or subscripts.
- Field values can be numbers or strings.

Public APIs implemented:
- `lgfs2_lang_init()`
- `lgfs2_lang_free()`
- `lgfs2_lang_parsef()`
- `lgfs2_lang_parses()`

Behavior:
- Builds linked AST statement lists using `ast_left`.
- Uses `ast_right` for statement operands and field/value chains.
- Initializes line number to 1.
- `lgfs2_lang_parses()` duplicates input, wraps it with `fmemopen()`, parses, and treats parser or lexer error state as failure.

Risk notes:
- AST shape is positional and tightly coupled to `lang.c`.
- Field list links are constructed through `ast_left`, so traversal order follows parser construction.
- `lgfs2_lang_free()` assumes `state` and `*state` are non-null.
- Parser is pure/reentrant but AST and result handling remain manually managed.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/parser.y -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/recovery.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/recovery.c

This file implements userland journal-head discovery and clean-journal marking, adapted from GFS2 kernel recovery code.

Public APIs:
- `lgfs2_replay_incr_blk()`
- `lgfs2_replay_read_block()`
- `lgfs2_get_log_header()`
- `lgfs2_find_jhead()`
- `lgfs2_clean_journal()`

Behavior:
- Maps logical journal blocks to physical blocks through `lgfs2_block_map()`.
- Reads log headers, validates block number, legacy hash, and CRC when present.
- Finds a good log header by scanning around invalid segments.
- Binary-searches and scans to find the highest sequence-number journal head.
- Writes a new unmount log header after the head to mark the journal clean.

Integration role:
- Used by fsck/recovery-style tools that need journal state inspection or cleanup.
- Depends on buffer I/O, block mapping, log hash/CRC helpers, and ondisk endian conversion.

Risk notes:
- Comments explicitly say kernel recovery code should be kept in sync.
- Clean-journal writes modify journal metadata directly.
- Zero CRC is accepted for pre-v2 log headers.
- Returns mix negative errno, positive invalid-header code, and zero success; callers must preserve semantics.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/rgrp.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/rgrp.c

This file implements resource group planning, representation, bitmap buffer management, on-disk read/write, and extent search/allocation.

Major APIs:
- Geometry and lookup: `lgfs2_compute_bitstructs()`, `lgfs2_blk2rgrpd()`, `lgfs2_rgblocks2bitblocks()`, `lgfs2_rgsize_for_data()`.
- Resource group handles: `lgfs2_rgrps_init()`, `lgfs2_rgrps_free()`, `lgfs2_attach_rgrps()`.
- Planning/alignment: `lgfs2_rgrp_align_addr()`, `lgfs2_rgrp_align_len()`, `lgfs2_rgrps_plan()`, `lgfs2_rindex_entry_new()`.
- Rindex import: `lgfs2_rindex_read_fd()`, `lgfs2_rindex_read_one()`, `lgfs2_rgrps_append()`.
- I/O: `lgfs2_rgrp_bitbuf_alloc/free()`, `lgfs2_rgrp_read()`, `lgfs2_rgrp_relse()`, `lgfs2_rgrp_write()`, `lgfs2_rgrps_write_final()`.
- Tree iteration: `lgfs2_rgrp_first/last/next/prev()`, `lgfs2_rgrp_insert()`, `lgfs2_rgrp_free()`.
- Bitmap extents: `lgfs2_rbm_from_block()`, `lgfs2_rbm_find()`, `lgfs2_alloc_extent()`.

Important behavior:
- Computes first bitmap block differently from subsequent bitmap blocks because rgrp and bitmap metadata headers differ.
- Stores resource groups in red-black trees.
- Plans one or two resource-group lengths to fit available space while respecting alignment.
- Reads/writes resource group headers and bitmap blocks, validating metadata headers and CRC.
- Searches for free extents using fast byte-aligned bitmap scanning plus unaligned edge handling.
- Allocates extents by setting first block state to dinode/used and remaining blocks used.

Risk notes:
- Alignment math directly affects grow/mkfs layout.
- `lgfs2_rbm_find()` assumes `minext` is non-null even though comment mentions NULL.
- `lgfs2_rgrp_write()` may write rounded-up alignment padding length from the bitmap buffer.
- Dirty bitmap release writes each modified bitmap block individually and logs but does not return write failure.
- Resource group ownership differs between `lgfs2_rgrp_free()` on `sdp->rgtree` and `lgfs2_rgrps_free()` on a handle.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/rgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/rgrp.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/rgrp.h

Private resource group helper header.

Defines:
- `struct rg_spec`: resource group length/count plan entry.
- `struct rgs_plan`: flexible-array plan holder.
- `struct _lgfs2_rgrps`: opaque resource group set backing type.
- `struct lgfs2_rbm`: resource group bitmap cursor.
- Inline helpers `rbm_bi()`, `lgfs2_rbm_to_block()`, and `lgfs2_rbm_eq()`.

Exports:
- `lgfs2_rbm_from_block()`
- `lgfs2_rbm_find()`
- `lgfs2_alloc_extent()`

Integration role:
- Used by `rgrp.c` and `fs_ops.c` for extent allocation.

Risk notes:
- `lgfs2_rbm_to_block()` depends on `bi_start` and bitmap-relative offset being consistent.
- `_lgfs2_rgrps` layout is private but must match `libgfs2.h` opaque typedef assumptions.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/rgrp.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/structures.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/structures.c

This file builds core GFS2 filesystem structures for mkfs-style creation and journal initialization.

Public APIs:
- `lgfs2_build_master()`, `lgfs2_build_root()`
- `lgfs2_sb_write()`
- `lgfs2_log_header_hash()`, `lgfs2_log_header_crc()`
- `lgfs2_write_journal_data()`, `lgfs2_write_journal()`, `lgfs2_build_journal()`
- `lgfs2_build_jindex()`
- `lgfs2_build_inum_range()`, `lgfs2_build_statfs_change()`, `lgfs2_build_quota_change()`
- `lgfs2_build_inum()`, `lgfs2_build_statfs()`, `lgfs2_build_rindex()`, `lgfs2_build_quota()`
- `lgfs2_init_inum()`, `lgfs2_init_statfs()`
- `lgfs2_check_meta()`
- `lgfs2_bm_scan()`

Behavior:
- Creates master and root directories as dinodes.
- Writes superblock at the fixed basic-block address while zeroing preceding blocks.
- Initializes journals with log headers, hashes, CRCs, sequence numbers, physical addresses, and unmount/userspace flags.
- Builds system files/directories: jindex, inum, statfs, rindex, quota, per-node inum/statfs/quota change files.
- Writes rindex entries from the resource-group tree plus an extra zero entry without resizing.
- Scans bitmaps for matching state.

Integration role:
- Heavily used by `mkfs.gfs2` and related structure setup.
- Depends on CRC-32C, disk hash, inode creation, file writes, block mapping, and ondisk conversion.

Risk notes:
- Journal creation has two paths: through mapped file buffers and through direct contiguous writes.
- `lgfs2_write_filemeta()` assumes single-extent allocation created by `lgfs2_file_alloc()`.
- Superblock write uses `pwritev()` and expects full write.
- Incorrect journal hash/CRC or physical address calculation makes recovery fail.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/structures.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/super.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/super.c

This file reads and validates the GFS2 superblock and rindex.

Public APIs:
- `lgfs2_check_sb()`
- `lgfs2_read_sb()`
- `lgfs2_rindex_read()`

Behavior:
- Validates superblock magic/type and a broad filesystem format range.
- Reads the superblock from the fixed GFS2 location.
- Populates in-core superblock fields and recomputes block-size-derived constants.
- Computes file and journal metadata height tables.
- Sets filesystem size from device fd length.
- Reads rindex file entries, inserts resource groups into `sdp->rgtree`, checks ordering/sanity, computes bit structures, and reports whether the rindex appears consistent.

Risk notes:
- `lgfs2_check_sb()` accepts fs format up to 1899 while `LGFS2_FS_FORMAT_VALID` uses a tighter range elsewhere.
- `lgfs2_read_sb()` assumes `lgfs2_bread()` succeeds before dereferencing.
- Rindex consistency checking may continue after bad entries by guessing next address from prior resource group.
- `good_on_disk()` trusts reading the expected rgrp block and only checks metadata type.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/man/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/man/Makefile.am

Automake fragment for installing GFS2 man pages.

Behavior:
- Sets `MAINTAINERCLEANFILES = Makefile.in`.
- Installs man pages for fsck, filesystem format, edit, grow, jadd, mkfs, tune, lockcapture, trace, and glocktop.

Risk notes:
- Build/distribution-only file.
- Missing entries here would omit man pages from distribution/install.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/man/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/Makefile.am

Automake build definition for mkfs/grow/jadd tools.

Targets:
- `mkfs.gfs2`
- `gfs2_jadd`
- `gfs2_grow`

Behavior:
- Defines shared CPP flags with `_GNU_SOURCE`.
- Lists private headers.
- Links all tools against `gfs2/libgfs2/libgfs2.la`.
- Adds blkid, uuid, and intl libraries where needed.
- Includes `checks.am` when Check framework is available.

Risk notes:
- Build flags and libraries differ per binary; changing shared code may require matching link dependencies.
- Unit test targets include production source files with `-DUNITTESTS`.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/check_grow.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/check_grow.c

Check-framework stub test binary for `main_grow.c`.

Behavior:
- Defines one test `test_grow_stub` asserting true.
- Builds suite `main_grow.c` / case `grow.gfs2`.
- Runs tests with `CK_ENV` and returns failure count as process status.

Risk notes:
- Provides build/test harness coverage only; no behavioral assertions for grow logic.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/check_grow.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/check_jadd.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/check_jadd.c

Check-framework stub test binary for `main_jadd.c`.

Behavior:
- Defines one test `test_jadd_stub` asserting true.
- Builds suite `main_jadd.c` / case `jadd.gfs2`.
- Runs tests with `CK_ENV` and returns failure count as process status.

Risk notes:
- Confirms test executable wiring but does not validate journal-add behavior.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/check_jadd.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/check_mkfs.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/check_mkfs.c

Check-framework stub test binary for `main_mkfs.c`.

Behavior:
- Defines one test `test_mkfs_stub` asserting true.
- Builds suite `main_mkfs.c` / case `mkfs.gfs2`.
- Runs tests with `CK_ENV` and returns failure count as process status.

Risk notes:
- No real mkfs functionality is tested here.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/check_mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/checks.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/checks.am

Automake test build fragment for mkfs/grow/jadd Check tests.

Behavior:
- Defines `TESTS = check_grow check_jadd check_mkfs`.
- Builds check programs from production target source lists plus each `check_*.c`.
- Adds `-DUNITTESTS` to suppress production `main()` blocks.
- Adds Check framework CFLAGS/LIBS and suppresses unused-function warnings.

Risk notes:
- Since tests compile production source directly, static helper coverage can be added later.
- Current test source files are stubs.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/checks.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/gfs2_mkfs.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/gfs2_mkfs.h

Small mkfs/grow/jadd support header.

Content:
- Includes `copyright.cf`.
- Defines copied inode ioctl constants: `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FIEMAP`.
- Defines `FS_JOURNAL_DATA_FL`.

Reason:
- Avoids duplicate symbol problems from including both Linux filesystem headers and `sys/mount.h`.

Risk notes:
- Local ioctl/flag copies must remain compatible with Linux `fs.h`.
- `FS_IOC_FIEMAP` references `struct fiemap`, so users must include the appropriate fiemap definition before use or in the same translation unit.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/gfs2_mkfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/main_grow.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/main_grow.c

This file implements the `gfs2_grow` command, which expands an existing mounted GFS2 filesystem after its underlying device has grown.

Main behavior:
- Parses options: help, quiet/verbose, test mode, version, skip discard, and developer-only override device size.
- Opens a mounted GFS2 filesystem and its backing device.
- Reads device info and superblock.
- Mounts the GFS2 metafs.
- Opens the metafs `rindex` file.
- Reads existing resource groups from rindex.
- Calculates current filesystem end and growth size.
- Plans new resource groups with topology-derived alignment from blkid.
- Optionally discards the new device range.
- Writes new resource group headers/bitmaps to the new portion.
- Appends new rindex entries to the live metafs `rindex` file.
- Handles test mode by planning without changing filesystem data.

Important helpers:
- `rgrps_init()` probes blkid topology and initializes aligned rgrp planning.
- `filesystem_size()` derives filesystem end from the last resource group.
- `initialize_new_portion()` creates and writes new resource groups.
- `fix_rindex()` appends new rindex entries and truncates partial writes when possible.
- `open_rindex()` opens the metafs rindex path.

Integration role:
- Uses libgfs2 geometry, constants, superblock, resource group planning/writing, and mount helpers.
- Uses metafs helpers to safely access GFS2 system files while mounted.

Risk notes:
- Directly mutates on-disk resource groups and the mounted filesystem's rindex.
- Partial rindex write handling is careful but still high risk.
- `devflags` is computed before option parsing sets `test`, so test-mode read-only intent may not apply as written.
- `lgfs2_rgrps_write_final()` is called even in paths where test mode skipped individual writes.
- Discard errors are ignored by `initialize_new_portion()`.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/main_grow.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/main_jadd.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/main_jadd.c

This file implements the `gfs2_jadd` command for adding journals to a mounted GFS2 filesystem.

Main behavior:
- Parses options for journal count, journal size, quota-change size, quiet/debug, help, and version.
- Opens and verifies a mounted GFS2 filesystem.
- Mounts GFS2 metafs and builds paths for `new_inode`, `per_node`, and `jindex`.
- Counts existing journals in `jindex`.
- Checks available filesystem space for each new journal's inum-range, statfs-change, quota-change, and journal file.
- For each new journal number:
  - Creates an `inum_rangeN` file via `new_inode`, marks it journaled data, writes zero structure, fsyncs, renames into `per_node`.
  - Creates a `statfs_changeN` file similarly.
  - Creates a `quota_changeN` file, writes quota-change metadata blocks, fsyncs, renames into `per_node`.
  - Creates `journalN`, allocates/fills journal space, finds physical block addresses with FIEMAP, writes log headers with hash/CRC, fsyncs, and renames into `jindex`.

Important helpers:
- `set_flags()` wraps `FS_IOC_GETFLAGS`/`FS_IOC_SETFLAGS`.
- `create_new_inode()` uses metafs `new_inode`.
- `find_block_address()` uses `FS_IOC_FIEMAP`.
- `alloc_new_journal()` prefers `fallocate()` and falls back to zero writes.
- `check_fit()` estimates required block count using `lgfs2_space_for_data()`.

Integration role:
- Uses mounted GFS2 metafs rather than raw block allocation.
- Uses libgfs2 constants, log hash/CRC helpers, and filesystem sizing helpers.

Risk notes:
- Directly creates system files in metafs; rename ordering is the safety boundary.
- FIEMAP must return exactly one mapped extent for each journal block lookup.
- Journal log headers rely on correct physical block addresses and CRC/hash values.
- `decode_arguments()` debug output prints `sdp->md.journals`, not `opts->journals`.
- Error paths can leave temporary `new_inode` or partially renamed system files.

<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/main_jadd.c -->