# Group Research: group_1048_linux_stable_sources_os_linux_linux_stable_fs_ntfs3_fsntfs_c_source_0c4d2af53ff2

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable/fs/ntfs3/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/fsntfs.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/fsntfs.c

## Role

Volume-wide NTFS3 support code. This file owns NTFS system names, multi-sector record fixups, log replay setup, cluster and MFT allocation, raw run I/O helpers, volume dirty-state updates, `$Secure` security descriptor management, `$Extend` reparse/object-id index setup, cluster deallocation, Windows filename validation, and label updates.

## Key Functions

- `ntfs_fix_pre_write()` and `ntfs_fix_post_read()` apply and validate NTFS update-sequence-array fixups for protected records.
- `ntfs_extend_init()` loads `$Extend` and caches `$ObjId`, `$Quota`, `$Reparse`, and `$UsnJrnl` inode references when present.
- `ntfs_loadlog_and_replay()` loads `$MFT`, invokes log replay for `$LogFile`, invalidates block-device cache afterward, and clears initialized logfiles by filling them with `0xff`.
- `ntfs_look_for_free_space()` allocates clusters from the volume bitmap, including special handling for MFT-zone allocations and MFT-zone shrinkage under space pressure.
- `ntfs_check_free_space()` estimates whether requested data clusters and MFT records can fit while accounting for delayed allocation reservations.
- `ntfs_extend_mft()` grows `$MFT::$DATA` and `$MFT::$BITMAP`, refreshes the MFT zone, formats new empty records, and writes the updated MFT inode.
- `ntfs_look_free_mft()` allocates MFT records, extends the MFT when needed, and can fall back to reserved system records in constrained cases.
- `ntfs_mark_rec_free()`, `ntfs_clear_mft_tail()`, and `ntfs_refresh_zone()` maintain the MFT bitmap, empty-record formatting, and MFT allocation zone.
- `ntfs_update_mftmirr()` copies mirrored MFT records from `$MFT` to `$MFTMirr`.
- `ntfs_bad_inode()` marks an NTFS inode bad and marks the volume dirty unless log replay is active.
- `ntfs_set_state()` updates the `$Volume` dirty flag in `ATTR_VOL_INFO`.
- `ntfs_bread()`, `ntfs_sb_write()`, `ntfs_sb_write_run()`, `ntfs_read_run_nb_ra()`, `ntfs_get_bh()`, `ntfs_write_bh()`, `ntfs_read_write_run()`, and `ntfs_vbo_to_lbo()` provide low-level block/run I/O utilities.
- `ntfs_bio_fill_1()` writes `0xff` pages over an entire run list, used to reset initialized log data.
- `ntfs_new_inode()` allocates and initializes a new VFS/NTFS inode pair for a selected MFT record.
- `is_sd_valid()` validates relative Windows security descriptors and nested ACL/SID ranges.
- `ntfs_security_init()`, `ntfs_get_security_by_id()`, and `ntfs_insert_security()` load `$Secure`, initialize `$SDH`/`$SII`, deduplicate descriptors, and append SDS records plus mirrored copies.
- `ntfs_reparse_init()`, `ntfs_objid_init()`, `ntfs_insert_reparse()`, and `ntfs_remove_reparse()` maintain `$Extend` metadata indexes.
- `mark_as_free_ex()` and `run_deallocate()` free allocated clusters, optionally discarding them and adjusting the MFT zone.
- `valid_windows_name()` rejects Windows-forbidden characters, trailing space/dot names, and reserved DOS device names.
- `ntfs_set_label()` replaces the volume label attribute and updates the cached label.

## Synchronization and State

Cluster allocation uses `sbi->used.bitmap.rw_lock` with `BITMAP_MUTEX_CLUSTERS`. MFT record allocation uses `sbi->mft.bitmap.rw_lock` with `BITMAP_MUTEX_MFT`. File run modifications use `ni->file.run_lock`. Security, reparse, object-id, and dirty-state changes use nested NTFS inode mutex classes.

## Research Notes

This is the NTFS3 volume services hub. It connects bitmap allocation, metadata file growth, system-file indexes, security descriptor storage, and raw block I/O. Several paths deliberately mark the volume dirty rather than attempting silent recovery when metadata invariants fail.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/fsntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/index.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/index.c

## Role

Implements NTFS index trees. NTFS directories and metadata indexes are stored as resident `INDEX_ROOT` entries plus optional nonresident `INDEX_ALLOCATION` buffers tracked by `BITMAP` attributes. This file provides collation, index bitmap scanning, node I/O, B+tree search/enumeration, insertion with splitting, deletion with collapse/shrink, and duplicate metadata updates.

## Key Functions

- `cmp_fnames()`, `cmp_uint()`, `cmp_sdh()`, and `cmp_uints()` implement supported NTFS collation rules.
- `get_cmp_func()` maps an `INDEX_ROOT` type/rule pair to the comparison callback.
- `bmp_buf_get()` and `bmp_buf_put()` read or map resident/nonresident index bitmaps, zeroing invalid tails and extending valid size as needed.
- `indx_mark_used()` and `indx_mark_free()` update allocation bitmap bits for index buffers.
- `scan_nres_bitmap()` scans nonresident bitmap blocks using the cached run tree, loading runs on demand under `indx->run_lock`.
- `indx_find_free()` and `indx_used_bit()` find free or used index-buffer bits.
- `hdr_find_split()`, `hdr_insert_head()`, `hdr_find_e()`, `hdr_insert_de()`, and `hdr_delete_de()` manipulate entries inside a single index header.
- `index_hdr_check()` and `index_buf_check()` validate index header sizes, fixup metadata, signatures, and VBNs.
- `fnd_clear()`, `fnd_push()`, `fnd_pop()`, and `fnd_is_empty()` manage `ntfs_fnd`, the search-path cache for tree operations.
- `indx_init()` validates an index root and derives index-buffer sizing and VBN conversion shifts.
- `indx_new()` creates and initializes a new on-disk index allocation buffer.
- `indx_get_root()` locates and validates the resident root attribute.
- `indx_read_ra()` reads an index buffer, fixes update-sequence arrays when needed, validates the buffer, and loads missing allocation runs on demand.
- `indx_find()` searches a sorted NTFS index tree and stores the path in `ntfs_fnd`.
- `indx_find_sort()` iterates entries in sorted order.
- `indx_find_raw()` enumerates raw entries across root and allocation buffers, used by metadata scans.
- `indx_create_allocate()` creates initial `INDEX_ALLOCATION` and `BITMAP` attributes.
- `indx_add_allocate()` grows or reuses index allocation space and bitmap bits.
- `indx_insert_into_root()` inserts into the resident root or promotes root entries into a new external buffer.
- `indx_insert_into_buffer()` inserts into an allocation buffer and recursively promotes split entries upward.
- `indx_insert_entry()` is the public insertion API.
- `indx_delete_entry()` removes an entry, handles replacement entries, frees empty branches, shrinks allocation, and collapses a tree back to an empty resident root when possible.
- `indx_update_dup()` updates duplicated file metadata inside a directory entry.

## Synchronization and State

`indx->run_lock` protects `alloc_run` and `bitmap_run` against concurrent read/enumeration and lazy run loading. Caller-side inode locks protect structural modifications to the index attributes. `indx->version` increments on insert/delete to signal structural changes.

## Research Notes

The implementation treats the resident root as both tree root and possible leaf. When it grows too large, entries move to allocation buffers and the root becomes a parent pointer. Deletion is more complex than insertion because it may replace internal entries, free child buffers, shrink attributes, or collapse the entire tree back into a resident root.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/inode.c

## Role

NTFS3 inode bridge between MFT records and Linux VFS/iomap. It reads and validates MFT records, derives VFS inode mode/operations from NTFS attributes, implements folio read/readahead/writeback through iomap, changes file size, creates and deletes inodes, manages hard links, and implements symlink/reparse readback.

## Key Functions

- `ntfs_read_mft()` parses one MFT record into a Linux inode.
  - Validates record sequence, in-use state, base-record status, and record size.
  - Handles `$STANDARD_INFORMATION`, `$ATTRIBUTE_LIST`, `$FILE_NAME`, `$DATA`, `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`, `$REPARSE_POINT`, and `$EA_INFO`.
  - Initializes directory indexes, data run trees, inode size/valid size, timestamps, mode, file operations, and address-space operations.
  - Handles special cases for `$MFT`, `$Bitmap`, `$Secure:$SDS`, `$BadClus`, `$Extend` children, compressed/sparse/encrypted flags, and reparse symlinks.
- `ntfs_iget5()` wraps `iget5_locked()`, reads fresh inodes, and rejects stale sequence numbers.
- `ntfs_bmap()` maps logical blocks via iomap, forcing delayed allocation materialization first when needed.
- `ntfs_iomap_read_end_io()` zeroes bytes past NTFS valid-data length before completing folio reads.
- `ntfs_read_folio()` reads resident, normal, and compressed data paths.
- `ntfs_readahead()` enables iomap readahead for nonresident, noncompressed files.
- `ntfs_set_size()` grows/truncates the unnamed data attribute and updates `i_size`.
- `ntfs_iomap_begin()` maps NTFS extents into iomap states: inline, mapped, hole, unwritten, or delalloc.
- `ntfs_iomap_end()` writes back inline resident data and advances valid-data length after writes/zeroing.
- `ntfs_iomap_put_folio()` zeroes folio tails past `i_valid` during buffered write/zero operations.
- `ntfs_writeback_range()` maps writeback ranges, forcing delayed allocation blocks when necessary.
- `ntfs_resident_writepage()` writes resident data from folios into the MFT resident attribute.
- `ntfs_writepages()` dispatches resident writeback or iomap writepages.
- `ntfs3_write_inode()` and `ntfs_sync_inode()` flush MFT inode metadata.
- `inode_read_data()` reads file contents page-by-page for metadata files such as `$AttrDef` and `$UpCase`.
- `ntfs_create_reparse_buffer()` builds Windows symlink reparse data from a Linux path.
- `ntfs_create_inode()` creates files, directories, symlinks, and special nodes with rollback on failure.
- `ntfs_link_inode()` constructs a new filename entry and delegates link insertion.
- `ntfs_unlink_inode()` removes a name, checks directory emptiness, drops link count, and attempts undo on failure.
- `ntfs_evict_inode()` truncates cached pages and clears NTFS inode state.
- `ntfs_readlink_hlp()` reads and decodes reparse targets for symlinks, mount points, cloud placeholders, and user tags.
- `ntfs_translate_junction()` converts absolute Windows junction targets into Linux-relative paths.
- `ntfs_get_link()` supplies VFS symlink targets.

## VFS Exports

- `ntfs_link_inode_operations` for symlinks.
- `ntfs_aops` for normal address-space operations.
- `ntfs_aops_cmpr` for compressed-file read support.
- `ntfs_iomap_ops` and `ntfs_iomap_folio_ops` for iomap integration.

## Research Notes

This file is where NTFS metadata semantics become Linux inode behavior. The most important invariants are sequence-number freshness, valid-data-length zeroing, resident versus nonresident data handling, run-tree locking during size/mapping changes, and careful rollback during inode creation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/decompress_common.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/decompress_common.c

## Role

Shared Huffman-table construction for NTFS3 XPRESS and LZX decompressors.

## Key Function

- `make_huffman_decode_table()` builds a fast decode table for canonical prefix codes.
  - Counts codeword lengths.
  - Rejects over-subscribed and incomplete prefix codes, except the fully empty code case allowed by LZX/XPRESS.
  - Sorts symbols by length and symbol value.
  - Fills direct lookup entries for codewords up to `table_bits`.
  - Builds compact binary-tree entries for longer codewords.
  - Encodes fast-path entries as symbol plus codeword length and internal nodes with high marker bits.

## Inputs and Constraints

- `num_syms` is limited by callers to small fixed alphabets.
- `table_bits` controls direct lookup table size.
- `max_codeword_len` bounds accepted lengths.
- `working_space` supplies length counts, offsets, and sorted symbols.

## Research Notes

This is format-agnostic canonical-code infrastructure. The table layout is tuned for the `read_huffsym()` helper in the companion header, where short codewords decode in one table lookup and long codewords traverse a small tree.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/decompress_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/decompress_common.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/decompress_common.h

## Role

Shared inline utilities for LZX and XPRESS decompression: endian-safe unaligned access, little-endian bitstream reading, Huffman symbol decoding, and LZ77 match copying.

## Key Definitions and Helpers

- `forceinline` maps to `__always_inline`.
- `FAST_UNALIGNED_ACCESS` is enabled for x86 and ARM configurations that can benefit from word-copy match copying.
- `copy_unaligned_word()` copies one machine word through kernel unaligned helpers.
- `repeat_byte()` expands one byte to a machine-word-sized repeated pattern.
- `struct input_bitstream` tracks buffered bits, remaining bit count, and input byte pointers.
- `init_input_bitstream()` initializes a bitstream over an input buffer.
- `bitstream_ensure_bits()`, `bitstream_peek_bits()`, `bitstream_remove_bits()`, `bitstream_pop_bits()`, and `bitstream_read_bits()` manage high-to-low bit consumption from little-endian 16-bit coding units.
- `bitstream_read_byte()`, `bitstream_read_u16()`, `bitstream_read_u32()`, and `bitstream_read_bytes()` read literal interleaved data.
- `bitstream_align()` resets the buffered bit state.
- `read_huffsym()` decodes a Huffman symbol using the table produced by `make_huffman_decode_table()`.
- `lz_copy()` copies validated LZ77 matches, using word-at-a-time fast paths for non-overlapping matches and offset-1 run-length cases when available.

## Research Notes

The header deliberately keeps decompressor hot paths inline. Bounds validation is expected before `lz_copy()` is called; this lets the helper optimize copying without rechecking match validity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/decompress_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/lib.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/lib.h

## Role

Small public header for NTFS3 system-compression decompressors.

## API Surface

- XPRESS:
  - `xpress_allocate_decompressor()`
  - `xpress_free_decompressor()`
  - `xpress_decompress()`
- LZX:
  - `lzx_allocate_decompressor()`
  - `lzx_free_decompressor()`
  - `lzx_decompress()`

## Research Notes

This header exposes only opaque decompressor handles and one-shot decompression entry points. Implementation details and workspace layouts remain private to the corresponding `.c` files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/lib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/lzx_decompress.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/lzx_decompress.c

## Role

LZX decompressor for NTFS “System Compressed” files. It supports the 32768-byte window size used by this NTFS compression mode and is based on wimlib-derived logic.

## Key Structures and Constants

- Defines LZX block types: verbatim, aligned offset, and uncompressed.
- Uses fixed symbol counts for literals, length symbols, offset slots, precode symbols, and aligned-offset symbols.
- `struct lzx_decompressor` owns reusable decode tables, codeword-length arrays, and Huffman working space.

## Key Functions

- `lzx_allocate_decompressor()` allocates the reusable workspace.
- `undo_e8_translation()` reverses x86 CALL-target preprocessing for one offset.
- `lzx_postprocess()` scans decompressed data and reverses E8 preprocessing when relevant.
- `read_presym()`, `read_mainsym()`, `read_lensym()`, and `read_alignedsym()` decode symbols from the relevant Huffman table.
- `lzx_read_codeword_lens()` reads precode lengths, builds the precode table, and decodes delta/RLE-encoded codeword lengths.
- `lzx_read_block_header()` reads block type and size, builds main/length/aligned Huffman tables for compressed blocks, and loads recent offsets for uncompressed blocks.
- `lzx_decompress_block()` decodes literals and matches, maintains recent-offset state, handles aligned offsets, validates match bounds, and copies matches via `lz_copy()`.
- `lzx_decompress()` loops over blocks until the requested output buffer is full, handles compressed and uncompressed blocks, and runs E8 postprocessing if possible.
- `lzx_free_decompressor()` frees the workspace.

## Error Handling

Invalid block types, impossible block sizes, invalid Huffman tables, zero recent offsets, input exhaustion, match underruns, and output overruns all return `-1`.

## Research Notes

The implementation is intentionally constrained to the NTFS/WIM-style LZX profile rather than general cabinet-file LZX. Recent-offset handling and E8 postprocessing are essential compatibility details for Windows system-compressed data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/lzx_decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/xpress_decompress.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/xpress_decompress.c

## Role

XPRESS Huffman decompressor for NTFS “System Compressed” files.

## Key Structures and Constants

- `XPRESS_NUM_SYMBOLS` is 512.
- `XPRESS_MAX_CODEWORD_LEN` is 15.
- `XPRESS_MIN_MATCH_LEN` is 3.
- `struct xpress_decompressor` contains one Huffman decode table, symbol-length array, and canonical-table working space.

## Key Functions

- `xpress_allocate_decompressor()` allocates reusable workspace.
- `xpress_decompress()`:
  - Reads 4-bit codeword lengths packed two per byte.
  - Builds the Huffman decode table.
  - Decodes symbols until the output buffer is full.
  - Emits literal bytes for symbols below 256.
  - Decodes match length and logarithmic offset fields for symbols above 255.
  - Handles extended length encodings.
  - Validates offset and length before copying with `lz_copy()`.
- `xpress_free_decompressor()` frees the workspace.

## Error Handling

The decoder returns `-1` for too-short headers, invalid Huffman length sets, match offsets before output start, and match lengths beyond the output buffer.

## Research Notes

XPRESS is smaller and simpler than the LZX path: one Huffman code drives both literals and match descriptors, with the remaining offset/length detail read directly from the bitstream.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lib/xpress_decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lznt.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/lznt.c

## Role

NTFS LZNT1 compression and decompression support. LZNT1 is used for traditional NTFS compressed files, operating on 4 KiB chunks with packed literal/match groups.

## Key Structures and Constants

- `LZNT_CHUNK_SIZE` is `0x1000`.
- `struct lznt_hash` stores two recent candidates per hash bucket for standard compression.
- `struct lznt` stores chunk bounds, selected best match, current maximum match length, mode, and optional hash table.
- `s_max_len[]` and `s_max_off[]` encode the changing LZNT pair layout as the current position advances within a chunk.

## Key Functions

- `get_match_len()` computes bounded bytewise match length.
- `longest_match_std()` uses a 4096-entry rolling hash with two candidates for faster compression.
- `longest_match_best()` does exhaustive prior-position search for slower, stronger compression.
- `make_pair()` and `parse_pair()` pack/unpack LZNT offset/length pairs for the current chunk position.
- `compress_chunk()` emits one compressed or uncompressed LZNT chunk.
  - Groups eight items behind one control byte.
  - Emits literals or two-byte match pairs.
  - Detects all-zero chunks.
  - Falls back to uncompressed chunk format when compression does not fit.
- `decompress_chunk()` expands one compressed chunk, validating pair boundaries and output size.
- `get_lznt_ctx()` allocates standard or best-compression context.
- `compress_lznt()` compresses an input buffer chunk-by-chunk and appends a zero terminator when space allows.
- `decompress_lznt()` parses chunk headers, dispatches compressed versus raw chunks, zero-fills partial chunk gaps, and returns decompressed byte count.

## Error Handling

Decompression rejects too-short streams, chunk sizes beyond the compressed buffer, pair references before the chunk start, malformed pair boundaries, and attempts to emit more than one 4 KiB chunk from a compressed chunk.

## Research Notes

This file contains both compression and decompression, unlike the XPRESS/LZX library files. The compressor returns `0` for all-zero input as a special NTFS compression convention and returns the uncompressed size when compression cannot fit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/lznt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/namei.c

## Role

NTFS3 VFS name-operation implementation. This file handles lookup, create, mknod, link, unlink, symlink, mkdir, rmdir, rename, parent lookup for export-style traversal, and dentry hash/compare behavior.

## Key Functions

- `fill_name_de()` formats an NTFS directory entry (`NTFS_DE`) containing an `ATTR_FILE_NAME`, converting Linux names to UTF-16 when needed.
- `ntfs_lookup()` converts the dentry name to UTF-16, searches the directory index, rejects malformed non-base inodes with missing operations, and returns `d_splice_alias()`.
- `ntfs_create()` creates a regular file via `ntfs_create_inode()`.
- `ntfs_mknod()` creates special files via `ntfs_create_inode()`.
- `ntfs_link()` enforces no directory hard links and NTFS link-count limits, then inserts a new NTFS name and instantiates the dentry.
- `ntfs_unlink()` locks the parent directory and delegates to `ntfs_unlink_inode()`.
- `ntfs_symlink()` creates an NTFS reparse-point symlink.
- `ntfs_mkdir()` creates a directory inode.
- `ntfs_rmdir()` delegates to `ntfs_unlink_inode()` after forced-shutdown/bad-inode checks.
- `ntfs_rename()` implements rename with `RENAME_NOREPLACE` support.
  - Rejects unsupported flags and metadata-file renames.
  - Unlinks an existing target first.
  - Builds old/new UTF-16 directory entries.
  - Locks old directory, renamed inode, and new directory in NTFS order.
  - Calls `ni_rename()` and updates timestamps/dirty state.
- `ntfs3_get_parent()` finds a filename attribute and returns an alias for the parent MFT reference.
- `ntfs_d_hash()` computes case-insensitive dentry hashes, using a fast ASCII uppercase path and a UTF-16/upcase-table path for non-ASCII.
- `ntfs_d_compare()` compares dentries case-insensitively, again using a fast ASCII path before falling back to UTF-16 name comparison.

## VFS Exports

- `ntfs_dir_inode_operations` registers directory operations: lookup, create, link, unlink, symlink, mkdir, rmdir, mknod, rename, ACLs, setattr/getattr, xattrs, and fiemap.
- `ntfs_special_inode_operations` registers metadata operations for special files.
- `ntfs_dentry_ops` registers NTFS case-insensitive hash and compare callbacks.

## Research Notes

This file is the VFS entry layer for namespace changes. Actual MFT and index mutations are delegated to inode/index helpers, while `namei.c` focuses on Linux operation semantics, locking order, name conversion, dentry instantiation, and timestamp/dirty bookkeeping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/namei.c -->