# Group Research: group_806_linux_sources_os_linux_linux_fs_ntfs3_fsntfs_c_sources_os_linux_linu_1a5fd6259e42

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux/fs/ntfs3/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/fsntfs.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/fsntfs.c

## Role

Shared NTFS3 metadata and low-level filesystem utility layer. It defines well-known NTFS system names, handles NTFS record fixups, MFT and cluster allocation, $Extend children, $Secure descriptors, $Reparse/$ObjId indexes, block/run I/O helpers, filesystem dirty-state updates, deallocation, Windows filename validation, and volume-label updates.

## Key Responsibilities

- Defines constant NTFS names for core metadata files and indexes: `$MFT`, `$MFTMirr`, `$LogFile`, `$Volume`, `$AttrDef`, `$Bitmap`, `$BadClus`, `$Secure`, `$Extend`, `$ObjId`, `$Reparse`, `$UsnJrnl`, `$I30`, `$SII`, `$SDH`, `$SDS`, `$O`, `$Q`, `$R`, plus WOF compressed-data name when LZX/XPRESS support is enabled.
- `ntfs_fix_pre_write()` and `ntfs_fix_post_read()` implement NTFS multi-sector update-sequence fixups around MFT/index/log records.
- `ntfs_extend_init()` loads `$Extend` and discovers optional `$ObjId`, `$Quota`, `$Reparse`, and `$UsnJrnl` children.
- `ntfs_loadlog_and_replay()` loads `$LogFile`, temporarily wires `$MFT`, runs log replay, invalidates block-device cache, and clears initialized log content with `ntfs_bio_fill_1()`.
- `ntfs_look_for_free_space()` and `ntfs_check_free_space()` coordinate cluster allocation against the volume bitmap, delayed allocation reservations, and the MFT zone.
- MFT allocation flow:
  - `ntfs_extend_mft()` grows `$MFT::$DATA` and `$MFT::$BITMAP`.
  - `ntfs_look_free_mft()` reserves records for the MFT itself or general use.
  - `ntfs_mark_rec_free()` frees record numbers and updates search hints.
  - `ntfs_clear_mft_tail()` formats new records using `sbi->new_rec`.
  - `ntfs_refresh_zone()` recreates the MFT zone after the current MFT allocation.
- `ntfs_update_mftmirr()` copies the mirrored initial MFT records to `$MFTMirr`.
- `ntfs_bad_inode()` marks an NTFS inode bad without calling `make_bad_inode()` and marks the volume dirty on real metadata errors.
- `ntfs_set_state()` updates `$Volume::$VOLUME_INFORMATION` dirty flags for mount, clean unmount, and detected NTFS errors.

## I/O Helpers

- `ntfs_bread()` wraps `sb_bread_unmovable()` with bounds checks against `sbi->volume.blocks`.
- `ntfs_sb_write()` writes arbitrary byte ranges to block buffers, optionally synchronously, and can fill with `0xff` when `buf == NULL`.
- `ntfs_sb_write_run()`, `ntfs_bread_run()`, `ntfs_read_run_nb_ra()`, `ntfs_get_bh()`, `ntfs_write_bh()`, and `ntfs_read_write_run()` translate NTFS virtual byte offsets through runlists into block/page-cache I/O.
- `ntfs_read_bh_ra()` combines run reading with post-read fixup verification.
- `ntfs_bio_fill_1()` builds chained BIO writes to fill a logfile run with `0xff`.
- `ntfs_vbo_to_lbo()` maps VBO to LBO and reports contiguous byte count.

## Security and System Indexes

- `s_default_security` is the default self-relative Windows security descriptor used for new files when needed.
- `is_sd_valid()` validates self-relative security descriptors, SIDs, SACLs, and DACLs; `is_acl_valid()` validates ACL revision, sizing, and ACE boundaries.
- `ntfs_security_init()` loads `$Secure`, validates `$SDH` and `$SII` index roots, initializes their NTFS index descriptors, scans `$SII` for the next security id, and sets the next `$SDS` append offset.
- `ntfs_get_security_by_id()` looks up a descriptor in `$SII`, verifies the on-disk `$SDS` header matches the index entry, and returns a copied descriptor.
- `ntfs_insert_security()` deduplicates descriptors through `$SDH`, writes `$SDS` primary and mirror copies in 256 KiB buckets, and inserts matching `$SII` and `$SDH` entries.
- `ntfs_reparse_init()` and `ntfs_objid_init()` initialize `$Extend/$Reparse:$R` and `$Extend/$ObjId:$O` indexes.
- `ntfs_objid_remove()`, `ntfs_insert_reparse()`, and `ntfs_remove_reparse()` maintain object-id and reparse indexes.

## Allocation and Names

- `mark_as_free_ex()` frees clusters in the used bitmap, optionally discards/unmaps them, detects double-free corruption, and can grow the MFT zone.
- `run_deallocate()` frees all non-sparse extents in a runlist.
- `valid_windows_name()` rejects control characters, Windows-forbidden characters, trailing space/dot, and reserved DOS device names such as `CON`, `NUL`, `AUX`, `PRN`, `COM1`-`COM9`, and `LPT1`-`LPT9`.
- `ntfs_set_label()` converts a user label to UTF-16, replaces `$Volume::$VOLUME_NAME`, updates cached label text, and writes the volume inode.

## Dependencies

Uses NTFS3 core headers `debug.h`, `ntfs.h`, and `ntfs_fs.h`; Linux block, buffer-head, NLS, filesystem, kernel, and BIO APIs. It depends heavily on runlist, attribute, MFT-record, index, bitmap-window, and logfile replay helpers implemented elsewhere in the NTFS3 driver.

## Research Notes

This file is the driver’s central metadata service layer. It is security- and corruption-sensitive: record fixups, descriptor validation, allocation bitmaps, MFT growth, and dirty-volume state all defend against or respond to inconsistent on-disk metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/fsntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/index.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/index.c

## Role

Implements NTFS index B-tree operations used for directories and metadata indexes such as `$Secure::$SII`, `$Secure::$SDH`, `$ObjId:$O`, `$Quota:$Q`, and `$Reparse:$R`. It provides key collation, index bitmap scanning, index-buffer I/O and validation, sorted/raw traversal, insertion with splitting, deletion with subtree cleanup, and duplicate-info updates.

## Key Structures and Constants

- `s_index_names[]` maps internal index mutex classes to index attribute names: `$I30`, `$SII`, `$SDH`, `$O`, `$Q`, `$R`.
- `struct bmp_buf` wraps resident or nonresident index bitmap access, including buffer-head state and valid-size extension tracking.
- `struct ntfs_fnd` is used as a search path/cache across root and allocation-buffer levels; this file clears, pushes, pops, and reuses finder state.

## Collation

- `cmp_fnames()` compares NTFS filename keys using the volume upcase table and mount case-sensitivity policy; it handles CPU-side search names and on-disk `ATTR_FILE_NAME` keys.
- `cmp_uint()` handles integer indexes such as `$SII` and quota `$Q`.
- `cmp_sdh()` orders `$SDH` by security hash and, when requested, security id.
- `cmp_uints()` compares multi-u32 keys for `$O` and `$R`; it has a reparse-removal mode that ignores the reparse tag and compares by file reference.
- `get_cmp_func()` selects the comparison function from an `INDEX_ROOT` type and collation rule.

## Bitmap and Buffer Handling

- `bmp_buf_get()` and `bmp_buf_put()` map resident/nonresident index bitmap storage, zero invalid tails, update valid size, and mark metadata dirty.
- `indx_mark_used()` and `indx_mark_free()` update individual index allocation bits.
- `scan_nres_bitmap()` scans nonresident bitmap blocks under `indx->run_lock`, loading run ranges lazily when needed.
- `indx_find_free()` finds a free index allocation bit; `indx_used_bit()` finds the next used bit for enumeration.

## Validation and Read/Write

- `index_hdr_check()` validates index header offsets, used size, total size, and minimum directory-entry presence.
- `index_buf_check()` validates `INDX` signature, update-sequence array placement/count, VBN, and embedded header.
- `indx_init()` validates an `INDEX_ROOT`, records index block sizing, VBN/VBO shift values, type, and initializes the run lock.
- `indx_read_ra()` reads an index allocation buffer via runlist and fixups, loads missing run ranges, validates the buffer, repairs fixups if needed, and marks bad inodes on corrupt reads.
- `indx_write()` writes an index node through `ntfs_write_bh()`.

## Search and Enumeration

- `hdr_find_e()` performs binary search within one index header and returns the exact match or first greater entry/end entry.
- `indx_find()` descends from root through subnode VBN pointers to find a key, saving the traversal path in `ntfs_fnd`.
- `indx_find_sort()` enumerates entries in sorted B-tree order.
- `indx_find_raw()` enumerates root entries and allocation buffers without sorted traversal, using bitmap bits and resumable offsets.

## Insertion

- `hdr_insert_de()` inserts a directory entry into an index header when space is available.
- `indx_create_allocate()` creates initial `$INDEX_ALLOCATION` and `$BITMAP` attributes.
- `indx_add_allocate()` reuses free index buffers or grows index bitmap/allocation attributes.
- `indx_insert_into_root()` inserts into resident root when possible; otherwise it externalizes entries into a new allocation buffer and converts root into a parent.
- `indx_insert_into_buffer()` splits a full index buffer, promotes a split entry upward, updates bitmap bits, and rolls back critical buffer changes on parent-insertion failure.
- `indx_insert_entry()` is the public insert routine and bumps `indx->version`.

## Deletion and Shrink

- `hdr_delete_de()` removes an entry from one index header.
- `indx_free_children()` recursively frees child index buffers and optionally shrinks tail allocation.
- `indx_get_entry_to_replace()` finds a replacement entry for deleting an internal node entry.
- `indx_delete_entry()` handles leaf deletion, internal deletion with replacement, subtree pruning, reinsertion of separator entries, full tree collapse to an empty resident root, allocation/bitmap removal, and version increment.
- `indx_shrink()` truncates index allocation and bitmap attributes when no used bits remain past a point.

## Directory Metadata Update

`indx_update_dup()` finds a directory entry by filename and updates its duplicated `NTFS_DUP_INFO` fields, writing either the external index buffer or resident MFT record.

## Dependencies

Depends on NTFS runlist, attribute sizing/loading, MFT-record mutation, bitmap helpers, buffer-head I/O, and comparison helpers from NTFS3 core headers. It is called by directory lookup/create/delete/rename paths, `$Secure` handling, and `$Extend` system indexes.

## Research Notes

This file is the NTFS3 B-tree engine. Most correctness risk is around corrupt index validation, split/delete rollback, lazy run loading during unlocked readdir, and maintaining allocation bitmap consistency with on-disk index buffers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/inode.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/inode.c

## Role

Maps NTFS MFT records to Linux inodes and address-space behavior. It parses file records, sets VFS inode operations, implements iomap-backed reads/writes/writeback, handles resident and nonresident data, creates new MFT records, handles hardlink/unlink eviction helpers, and translates NTFS reparse-point symlinks/junctions.

## MFT Read and Inode Setup

- `ntfs_read_mft()` initializes `ntfs_inode`, reads the MFT record, validates sequence/in-use/base-record state, enumerates attributes, and derives Linux inode mode, size, timestamps, flags, operations, runlists, and link count.
- Handles key attributes:
  - `$STANDARD_INFORMATION`: timestamps, file attributes, security id.
  - `$ATTRIBUTE_LIST`: loads external attribute list and restarts enumeration.
  - `$FILE_NAME`: counts names and hardlink-visible names; optionally matches requested name.
  - `$DATA`: resident/nonresident size, valid size, compression/sparse/encryption flags, data runlist.
  - `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`: directory index setup.
  - `$REPARSE_POINT`: symlink/compression/dedup reparse parsing.
  - `$EA_INFO`: WSL permission/xattr state.
- Chooses `ntfs_dir_inode_operations`, `ntfs_link_inode_operations`, `ntfs_file_inode_operations`, or `ntfs_special_inode_operations`.
- Applies `sys_immutable` mount behavior for NTFS system files and sets `S_NOSEC` when there is no xattr/security state.
- `ntfs_iget5()` wraps `iget5_locked()`, reads new inodes, verifies sequence reuse, and marks the volume dirty on read failures.

## Address-Space and Iomap

- `ntfs_bmap()` supports FIBMAP/iomap bmap, forcing delayed-allocation blocks to be allocated before mapping.
- `ntfs_iomap_begin()` maps offsets to `IOMAP_INLINE`, `IOMAP_MAPPED`, `IOMAP_HOLE`, `IOMAP_UNWRITTEN`, or `IOMAP_DELALLOC`, using `attr_data_get_block()` and enforcing maximum file sizes.
- `ntfs_iomap_end()` writes back resident inline data and advances `ni->i_valid` after writes or zeroing.
- `ntfs_iomap_put_folio()` zeroes folio tail past valid data.
- `ntfs_iomap_read_end_io()` zero-fills folio ranges beyond NTFS valid data before completing iomap reads.
- `ntfs_read_folio()` handles bad inodes, reads past valid size as zero, dispatches compressed reads to `ni_read_folio_cmpr()`, and otherwise uses iomap.
- `ntfs_readahead()` skips resident and compressed files; otherwise uses iomap readahead.
- `ntfs_writeback_range()` allocates delayed blocks if needed and submits mapped writeback through iomap.
- `ntfs_writepages()` has a resident-data path via `attr_data_write_resident()` and a nonresident iomap writeback path.
- `ntfs_set_size()` changes file size through `attr_set_size()` under inode and runlist locks.

## Inode Write and Utility APIs

- `ntfs3_write_inode()` and `ntfs_sync_inode()` delegate to `_ni_write_inode()`.
- `inode_read_data()` reads metadata-file contents page by page, used for files such as `$AttrDef` and `$UpCase`.
- `ntfs_evict_inode()` truncates page cache, clears VFS inode state, and frees NTFS inode internals.

## Inode Creation

`ntfs_create_inode()` is the shared create path for create, mknod, symlink, mkdir, and atomic open:

- locks parent directory when needed;
- chooses NTFS file attributes from mode, parent attributes, sparse/compressed mount behavior, hidden dotfile option, and readonly mode;
- allocates a free MFT record and formats a new record;
- inserts standard information, filename, optional security descriptor, data/index/reparse attributes, and end marker;
- obtains/inserts security id through `$Secure` for NTFS 3.x volumes;
- creates `$I30` root for directories;
- creates NTFS symlink reparse data for symlinks, resident or nonresident depending on size;
- inserts reparse index entry for symlinks;
- initializes ACL/WSL permissions and updates directory-entry duplicated EA size;
- inserts the new name into parent `$I30` and instantiates the dentry;
- has rollback paths for EA, reparse index, allocated clusters, MFT record, and link count.

## Link, Unlink, and Reparse Reading

- `ntfs_link_inode()` builds a new filename directory entry and delegates to `ni_add_name()`.
- `ntfs_unlink_inode()` rejects metadata files, checks directory emptiness, removes the name, updates link counts/timestamps, and attempts undo on removal failure.
- `ntfs_create_reparse_buffer()` creates Windows symlink reparse buffers, converts path text to UTF-16, changes `/` to `\`, and decorates absolute paths with `\??\`.
- `ntfs_readlink_hlp()` reads resident or nonresident reparse data, supports symlink, mount point/junction, OneDrive cloud placeholders, and user surrogate tags, converts UTF-16 to mounted NLS, changes `\` to `/`, and translates junction targets relative to the mount point.
- `ntfs_get_link()` allocates PAGE_SIZE link text and registers delayed free.

## Exported Operation Tables

Defines `ntfs_link_inode_operations`, `ntfs_aops`, `ntfs_aops_cmpr`, `ntfs_iomap_ops`, and `ntfs_iomap_folio_ops`.

## Dependencies

Uses NTFS attribute, runlist, directory-index, xattr/ACL, compression, reparse, NLS, iomap, buffer-head, page-cache, writeback, and VFS inode APIs.

## Research Notes

This is the main NTFS3 VFS bridge. It is where on-disk MFT semantics become Linux inode semantics, and where NTFS valid-size, resident attributes, delayed allocation, compressed files, WSL permissions, and Windows reparse points are reconciled with Linux page-cache and namespace behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/decompress_common.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/lib/decompress_common.c

## Role

Shared decompression implementation for NTFS3 XPRESS and LZX decompressors. It builds canonical Huffman/prefix-code decode tables used by both formats.

## Key Function

`make_huffman_decode_table()` takes codeword lengths and creates a fast decode table:

- counts symbols by codeword length;
- validates that the code lengths form a complete prefix code, while allowing an entirely empty code as valid for LZX/XPRESS;
- sorts symbols by canonical code order;
- fills direct lookup table entries for codewords up to `table_bits`;
- builds binary-tree overflow entries for longer codewords;
- stores direct entries as `(length << 11) | symbol`;
- stores internal tree nodes with high bits `0xC000`;
- returns `0` on success and `-1` for invalid lengths.

## Dependencies

Includes `decompress_common.h`, which provides kernel types, unaligned access helpers, bitstream helpers, and shared LZ-copy routines.

## Research Notes

This is format-independent prefix-code infrastructure imported from Eric Biggers’ decompressor code. Validation of over-subscribed or incomplete code length sets is the key safety boundary before XPRESS/LZX symbol decoding.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/decompress_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/decompress_common.h -->
# File Research: sources/os/linux/linux/fs/ntfs3/lib/decompress_common.h

## Role

Shared header for XPRESS and LZX decompression. It defines bitstream primitives, Huffman symbol decoding, unaligned-copy optimizations, and LZ77 match copying.

## Key Definitions

- `forceinline` maps to `__always_inline`.
- `FAST_UNALIGNED_ACCESS` is enabled on x86 and ARM configurations with unaligned support.
- `WORDBYTES` reflects `sizeof(size_t)`.
- `struct input_bitstream` tracks:
  - left-justified bit buffer;
  - number of bits held;
  - next input byte;
  - end pointer.

## Bitstream Helpers

- `init_input_bitstream()` initializes stream state.
- `bitstream_ensure_bits()` loads little-endian 16-bit coding units into the bit buffer.
- `bitstream_peek_bits()`, `bitstream_remove_bits()`, `bitstream_pop_bits()`, and `bitstream_read_bits()` expose bit-level reading.
- `bitstream_read_byte()`, `bitstream_read_u16()`, `bitstream_read_u32()`, and `bitstream_read_bytes()` read literal embedded data.
- `bitstream_align()` discards buffered bits.

## Huffman and LZ Helpers

- Declares `make_huffman_decode_table()`.
- `read_huffsym()` decodes one symbol using the direct table fast path or binary-tree slow path.
- `lz_copy()` copies an already-validated LZ77 match from `dst - offset` to `dst`, with optimized word-at-a-time copies for unaligned-capable architectures and a bytewise fallback.

## Dependencies

Uses Linux string, compiler, type, slab, and unaligned-access headers.

## Research Notes

Callers are responsible for validating match length/offset and output bounds before calling `lz_copy()`. Input exhaustion behavior is deliberately permissive for bit decoding, where missing bits are effectively zero, while byte-array reads can fail via `NULL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/decompress_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/lib.h -->
# File Research: sources/os/linux/linux/fs/ntfs3/lib/lib.h

## Role

Public internal header for NTFS3 decompressor allocation, freeing, and decompression entry points.

## API Surface

- XPRESS:
  - `xpress_allocate_decompressor()`
  - `xpress_free_decompressor()`
  - `xpress_decompress()`
- LZX:
  - `lzx_allocate_decompressor()`
  - `lzx_free_decompressor()`
  - `lzx_decompress()`

## Dependencies

Includes `<linux/types.h>` and forward-declares `struct xpress_decompressor` and `struct lzx_decompressor`.

## Research Notes

This header intentionally hides decompressor internals. NTFS3 callers only manage opaque decompressor workspaces and call the selected format-specific decompression function.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/lib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/lzx_decompress.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/lib/lzx_decompress.c

## Role

LZX decompressor used for NTFS “System Compressed” files. It is based on wimlib-derived code and supports the 32768-byte window size used by system compression.

## Format Constants and State

- Supports LZX block types: verbatim, aligned-offset, and uncompressed.
- Uses 256 literal symbols, match lengths 2-257, 30 offset slots, recent-offset queue of 3, and default block size 32768.
- Defines decode table sizes for main, length, precode, and aligned-offset Huffman codes.
- `struct lzx_decompressor` stores all decode tables, codeword-length arrays, and Huffman table working space.

## Main Flow

- `lzx_allocate_decompressor()` allocates reusable workspace.
- `lzx_decompress()` initializes the input bitstream, clears delta-encoded length arrays, loops over blocks until the output buffer is full, and postprocesses x86 E8 translations when needed.
- `lzx_free_decompressor()` frees workspace.

## Block Handling

- `lzx_read_block_header()` reads block type and size.
- For aligned blocks, it reads and builds the aligned offset code.
- For verbatim/aligned compressed blocks, it reads main-code and length-code codeword lengths through the precode and builds decode tables.
- For uncompressed blocks, it aligns the stream, reads recent offsets, and rejects zero offsets.

## Symbol and Match Decoding

- `lzx_read_codeword_lens()` decodes delta-coded Huffman lengths using a precode and handles run-length symbols 17, 18, and 19.
- `lzx_decompress_block()` decodes literals and matches, handles recent offsets and explicit offset slots, reads aligned-offset low bits when applicable, validates match length/offset against output bounds, and copies matches with `lz_copy()`.

## E8 Postprocessing

- `undo_e8_translation()` and `lzx_postprocess()` reverse LZX x86 CALL preprocessing using the default 12,000,000-byte file-size convention.
- Postprocessing is skipped when the decoded data cannot contain E8 literals.

## Dependencies

Uses `decompress_common.h` for bitstream, Huffman, and LZ-copy helpers and `lib.h` for exported prototypes.

## Research Notes

The implementation is intentionally narrow: it targets the LZX variant needed by NTFS WOF/System Compression rather than a general cabinet-file LZX decoder. Bounds checks before `lz_copy()` are the primary protection against malformed compressed streams.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/lzx_decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/xpress_decompress.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/lib/xpress_decompress.c

## Role

XPRESS Huffman decompressor used for NTFS “System Compressed” files. It is based on wimlib-derived code and shares Huffman/bitstream/LZ primitives with the LZX decompressor.

## Key Definitions

- `XPRESS_NUM_SYMBOLS`: 512.
- `XPRESS_MAX_CODEWORD_LEN`: 15.
- `XPRESS_MIN_MATCH_LEN`: 3.
- `XPRESS_TABLEBITS`: 12.
- `struct xpress_decompressor` stores the decode table, symbol lengths, and Huffman working space.

## Main Flow

- `xpress_allocate_decompressor()` allocates workspace.
- `xpress_decompress()`:
  - reads 512 4-bit codeword lengths from the compressed header;
  - builds a Huffman decode table;
  - decodes symbols until the output buffer is filled;
  - writes literals for symbols below 256;
  - decodes match length and log2 offset from symbols 256+;
  - reads extra offset bits and extended lengths;
  - validates offset and length against output bounds;
  - copies matches with `lz_copy()`.
- `xpress_free_decompressor()` frees workspace.

## Dependencies

Uses `decompress_common.h` and `lib.h`.

## Research Notes

The decompressor returns `-1` for malformed input rather than errno-style Linux negatives. It depends on caller-provided output size being the exact expected uncompressed size.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lib/xpress_decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lznt.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/lznt.c

## Role

Implements NTFS LZNT1 compression and decompression for NTFS compressed file attributes. It supports standard hash-assisted compression, best-match compression, and chunked decompression.

## Key Structures and Constants

- `LZNT_CHUNK_SIZE` is 0x1000 bytes.
- `LZNT_ERROR_ALL_ZEROS` is an internal compression result indicating an all-zero input buffer.
- `struct lznt_hash` stores two previous match candidates per hash bucket.
- `struct lznt` tracks current uncompressed chunk bounds, best match pointer, maximum match length, compression mode, and optional hash table.
- `s_max_len[]` and `s_max_off[]` encode LZNT1’s changing offset/length bit split by current chunk position.

## Compression

- `get_match_len()` measures a bytewise match up to a maximum.
- `longest_match_std()` uses a 4096-entry hash table with two candidates per bucket.
- `longest_match_best()` scans prior bytes for best compression at high CPU cost.
- `make_pair()` packs offset/length into a 16-bit LZNT token.
- `compress_chunk()` emits control-byte groups of eight items, literals or packed pairs, falls back to an uncompressed chunk when compressed output would not fit, and reports all-zero chunks specially.
- `get_lznt_ctx()` allocates a context sized for standard or best compression.
- `compress_lznt()` compresses all 4 KiB chunks, writes a zero terminator when space permits, returns final compressed size, returns `0` for all-zero input, and returns `unc_size` when compression cannot fit usefully.

## Decompression

- `parse_pair()` unpacks offset/length from a token.
- `decompress_chunk()` decodes one compressed chunk, validates token boundaries and backward offsets, truncates final match at the output end, and rejects writes beyond one LZNT chunk.
- `decompress_lznt()` reads chunk headers, handles compressed and uncompressed chunks, zero-fills short chunks as needed, stops at output full/input end/zero header, and returns bytes decompressed or `-EINVAL`.

## Dependencies

Uses Linux kernel, slab, string, type headers, `debug.h`, and `ntfs_fs.h`.

## Research Notes

This file covers classic NTFS compression, distinct from WOF LZX/XPRESS system compression. Decompression has explicit malformed-stream checks for chunk size, token availability, backward offset validity, and output chunk limits.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/lznt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/namei.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/namei.c

## Role

Implements NTFS3 namespace inode and dentry operations: lookup, create, mknod, hardlink, unlink, symlink, mkdir, rmdir, rename, parent lookup for export, and case-insensitive dentry hashing/comparison.

## Name Formatting and Lookup

- `fill_name_de()` converts a Linux `qstr` or existing `cpu_str` UTF-16 name into an NTFS directory entry containing an `ATTR_FILE_NAME`.
- The generated entry uses `FILE_NAME_POSIX`, aligned entry sizing, and key size equal to the full filename attribute size.
- `ntfs_lookup()` converts the dentry name to UTF-16, locks the directory, calls `dir_search_u()`, rejects malformed non-base-record inodes with null `i_op`, and returns `d_splice_alias()`.

## Creation Operations

- `ntfs_create()` delegates regular-file creation to `ntfs_create_inode()`.
- `ntfs_mknod()` delegates special-file creation.
- `ntfs_symlink()` creates an NTFS reparse-point symlink.
- `ntfs_mkdir()` creates a directory through `ntfs_create_inode()` and returns an error dentry pointer on failure.

## Link, Unlink, and Remove

- `ntfs_link()` rejects directory hardlinks and link-count overflow, locks parent and target inode, increments Linux link state before attempting `ntfs_link_inode()`, and rolls back on failure.
- `ntfs_unlink()` checks bad inode and forced shutdown, locks the directory, and delegates to `ntfs_unlink_inode()`.
- `ntfs_rmdir()` follows the same wrapper pattern as unlink; emptiness is checked in `ntfs_unlink_inode()`.

## Rename

`ntfs_rename()` supports `RENAME_NOREPLACE` only:

- no-ops same-name same-directory renames;
- rejects metadata-file renames;
- unlinks an existing target before renaming;
- allocates a PATH_MAX work buffer containing old and new directory entries;
- locks old directory, target inode, and new directory when distinct;
- delegates metadata changes to `ni_rename()`;
- updates timestamps, dirty state, and dirsync writes.

## Parent and Dentry Operations

- `ntfs3_get_parent()` scans `ATTR_NAME` attributes and returns an alias for the parent reference stored in `fname->home`.
- `ntfs_d_hash()` hashes ASCII names quickly using uppercase characters, falling back to UTF-16 conversion and NTFS upcase-table hashing for non-ASCII names.
- `ntfs_d_compare()` compares ASCII names case-insensitively fast, then falls back to UTF-16 conversion and `ntfs_cmp_names_cpu()`.

## Exported Operations

- `ntfs_dir_inode_operations` wires lookup/create/link/unlink/symlink/mkdir/rmdir/mknod/rename plus ACL, setattr/getattr, listxattr, fiemap, and fileattr_get.
- `ntfs_special_inode_operations` provides setattr/getattr/listxattr and ACL operations.
- `ntfs_dentry_ops` provides NTFS-aware hash and compare functions.

## Dependencies

Uses Linux VFS, NLS, ctype, and POSIX ACL headers plus NTFS3 directory, inode, xattr, ACL, Unicode conversion, and rename helpers.

## Research Notes

This file is the Linux namespace front-end for NTFS3. Most heavy metadata work is delegated to `inode.c`, `frecord.c`, and `index.c`; this layer focuses on VFS locking/order, name conversion, casefold-compatible dentry behavior, and operation-table wiring.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/namei.c -->