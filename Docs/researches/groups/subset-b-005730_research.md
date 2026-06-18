# Research Report: subset-b-005730

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/fsntfs.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/fsntfs.c

Purpose: implements NTFS3 superblock-level helpers for NTFS metadata records, allocation bitmaps, raw run I/O, log replay setup, `$Extend` children, `$Secure`, object-id and reparse indexes, cluster deallocation, Windows name validation, and volume-label updates. It is the bridge between on-disk NTFS system files and the higher inode, attribute, index, and VFS layers.

Important APIs and functions: exported helpers include `ntfs_fix_pre_write`, `ntfs_fix_post_read`, `ntfs_extend_init`, `ntfs_loadlog_and_replay`, `ntfs_look_for_free_space`, `ntfs_check_free_space`, `ntfs_look_free_mft`, `ntfs_mark_rec_free`, `ntfs_clear_mft_tail`, `ntfs_refresh_zone`, `ntfs_update_mftmirr`, `ntfs_bad_inode`, `ntfs_set_state`, `ntfs_bread`, `ntfs_sb_write`, run read/write helpers, `ntfs_vbo_to_lbo`, `ntfs_new_inode`, security descriptor helpers, `ntfs_security_init`, `ntfs_get_security_by_id`, `ntfs_insert_security`, `ntfs_reparse_init`, `ntfs_objid_init`, object/reparse insert/remove helpers, `mark_as_free_ex`, `run_deallocate`, `valid_windows_name`, and `ntfs_set_label`. It also defines well-known NTFS system-file and index names used throughout the driver.

Control flow: mount/setup code loads `$Extend`, discovers `$ObjId`, `$Quota`, `$Reparse`, and `$UsnJrnl`, replays `$LogFile` by temporarily loading `$MFT`, and initializes `$Secure` indexes. Allocation requests lock cluster or MFT bitmaps, prefer the MFT zone for MFT growth, extend `$MFT` and `$MFT::$BITMAP` when needed, zero newly available MFT records, and update hints. Raw I/O helpers translate run VBOs to LBOs, read/write buffer_heads with NTFS multi-sector fixups, or fill the logfile with `0xff` bios after replay. `$Secure` lookup searches `$SII`; insertion first deduplicates via `$SDH`, appends mirrored SDS records, then inserts `$SII` and `$SDH` entries. Reparse/object-id helpers initialize and mutate `$R`/`$O` indexes.

State and persistence behavior: persistent state is NTFS metadata on disk: volume dirty flags in `$Volume`, MFT records and MFT mirror, cluster and MFT bitmaps, `$Secure::$SDS` descriptor buckets plus `$SII`/`$SDH`, `$Extend` indexes, and label attributes. Runtime state in `ntfs_sb_info` caches system inode pointers, next allocation hints, bitmap zones, security ids and offsets, volume flags, and run lists. Errors can mark `NTFS_DIRTY_ERROR`, and many mutations mark MFT records or buffer_heads dirty.

Dependencies and integration points: depends on `wnd_bitmap`, run-list helpers, attribute sizing/allocation, MFT record helpers, index APIs, log replay, block-device buffer/bio APIs, discard/unmap helpers, NLS conversion, and NTFS security/reparse structures. It is called by mount, inode creation/removal, directory index operations, setattr/label paths, and writeback/error handling.

Risks: fixup validation and raw buffer writes are corruption-sensitive. Allocation code has nested bitmap, run, and inode locks and must keep MFT-zone accounting consistent. `$Secure` insertion has multi-step persistence without full transaction rollback. Reparse/object-id index mutations must handle missing `$Extend` children. `mark_as_free_ex` marks the volume dirty when freeing already-free clusters, so false positives affect mount state. Name validation must match Windows-reserved names and case-folding semantics.

Test signals: mount dirty/clean volumes, replay small and large `$LogFile` cases, allocate/free clusters under low-space and MFT-zone pressure, extend `$MFT`, validate MFT mirror updates, read/write records with bad fixups, create duplicate and new security descriptors, read security by id, insert/remove reparse points and object ids, discard freed runs, reject reserved Windows names, and change volume labels with length and encoding limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/fsntfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/index.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/index.c

Purpose: implements the NTFS index engine used for directories and metadata indexes such as `$SII`, `$SDH`, `$O`, `$Q`, and `$R`. It provides collation, bitmap management, index-buffer validation, B-tree search/enumeration, insertion with splitting, deletion with replacement/collapse, and duplicate file-name metadata updates.

Important APIs and functions: core entry points are `indx_init`, `indx_clear`, `indx_get_root`, `indx_read_ra`, `indx_find`, `indx_find_sort`, `indx_find_raw`, `indx_used_bit`, `indx_insert_entry`, `indx_delete_entry`, and `indx_update_dup`. Internal helpers include collation functions `cmp_fnames`, `cmp_uint`, `cmp_sdh`, `cmp_uints`, bitmap helpers `bmp_buf_get`, `indx_mark_used`, `indx_mark_free`, `scan_nres_bitmap`, allocation helpers `indx_create_allocate`, `indx_add_allocate`, node creation/read/write helpers, and delete/split helpers such as `indx_insert_into_root`, `indx_insert_into_buffer`, `indx_get_entry_to_replace`, `indx_free_children`, and `indx_shrink`.

Control flow: `indx_init` validates an `INDEX_ROOT` and derives block/VBN geometry. Lookup uses `hdr_find_e` to binary-search root or allocation-buffer entries, descending through child VBNs and recording the path in `ntfs_fnd`. Sorted and raw enumeration walk root entries plus used allocation buffers. Insert first searches for the target leaf; if root or leaf has space, it inserts in place, otherwise it creates/extends allocation and bitmap attributes, splits a buffer around a midpoint, promotes a separator entry to the parent, and recursively splits parents as needed. Delete removes leaf entries directly or replaces node entries with the first leaf from the right subtree, frees empty child buffers, shrinks tail allocation, and can collapse the tree back to an empty resident root.

State and persistence behavior: index roots are resident attributes in an MFT record; large indexes persist allocation buffers in `ATTR_ALLOC` and occupancy in `ATTR_BITMAP`. `ntfs_index` caches allocation and bitmap run lists, derived block geometry, a version counter, and a run semaphore. `ntfs_fnd` temporarily holds a root entry and referenced allocation nodes. Mutations dirty resident MFT records, write index buffers with NTFS fixups, update bitmap valid sizes, adjust directory `i_size` for `$I30`, and free or truncate allocation runs.

Dependencies and integration points: depends on attribute lookup/sizing/loading, run lists, MFT inode locking, buffer-head record I/O and fixups from `fsntfs.c`, name collation/upcase helpers, security and reparse key structures, and directory operations in `inode.c`/`namei.c`. `$Secure`, `$ObjId`, and `$Reparse` helpers use the same generic index operations with different collation rules.

Risks: this is a corruption-sensitive B-tree implementation. Offsets, entry sizes, end entries, child VBN pointers, bitmap bits, and allocation sizes must remain synchronized. Recursive parent splitting has partial rollback but can still leave dirty metadata if later writes fail. Non-resident bitmap scanning may load runs lazily while readdir holds only shared locks. Comparison behavior for case-sensitive names and `$SDH` hash duplicates directly affects lookup correctness.

Test signals: directory lookup and readdir across resident-only and nonresident indexes, insert enough names to split root and multiple levels, delete entries that empty leaves and collapse trees, duplicate name rejection, security descriptor hash collisions, reparse/object-id key deletion by full key and by reference, fixup failure in an index buffer, bitmap growth/shrink with nonresident bitmaps, and `indx_update_dup` after timestamp/size/EA changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/inode.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/inode.c

Purpose: implements NTFS3 inode materialization, file address-space operations, iomap mapping, size changes, inode creation/link/unlink, eviction, symlink/reparse translation, and inode operation tables. It converts MFT records and attributes into Linux `struct inode` behavior and writes new NTFS metadata during create/remove paths.

Important APIs and functions: public helpers include `ntfs_iget5`, `ntfs_set_size`, `ntfs3_write_inode`, `ntfs_sync_inode`, `inode_read_data`, `ntfs_create_inode`, `ntfs_link_inode`, `ntfs_unlink_inode`, and `ntfs_evict_inode`. Major internal paths are `ntfs_read_mft`, `ntfs_iomap_begin`, `ntfs_iomap_end`, `ntfs_writeback_range`, resident/nonresident read and writeback handlers, symlink reparse creation and parsing helpers, and `ntfs_get_link`. It exports `ntfs_aops`, `ntfs_aops_cmpr`, `ntfs_iomap_ops`, `ntfs_iomap_folio_ops`, and inode operation tables for links.

Control flow: `ntfs_iget5` uses `iget5_locked` and, for new inodes, `ntfs_read_mft`. MFT reading initializes the base record, verifies sequence and in-use flags, enumerates attributes, loads attribute lists, extracts timestamps/security/file names/data runs/index roots/reparse records/EA info, initializes file or directory run lists, sets mode and operation tables, and unlocks the inode. Iomap begin maps resident data, sparse holes, delayed allocation, unwritten ranges beyond valid size, and physical LCNs for read/write/fiemap/direct I/O. Creation allocates an MFT record, builds standard info, file name, optional security, data/root/reparse attributes, initializes ACL/WSL permissions, inserts the directory index entry, instantiates the dentry, and unwinds record, runs, reparse index, EA, and bitmap state on failure. Unlink removes the directory name and updates link counts with undo support.

State and persistence behavior: in-memory `ntfs_inode` stores MFT record state, run lists, resident/compressed flags, valid size, standard attributes, security id, directory index state, and bad-inode state. Persistent mutations include MFT records, attribute lists, nonresident data runs, directory indexes, reparse indexes, security ids, EA/ACL attributes, link counts, timestamps, and pagecache-backed data. `i_valid` is used to zero reads beyond valid data and to classify iomaps as mapped/unwritten.

Dependencies and integration points: integrates with VFS inode/dentry/pagecache/writeback, iomap buffered/direct/fiemap/bmap helpers, NTFS attribute manipulation, index insertion/deletion, MFT allocation from `fsntfs.c`, compression read paths, NLS conversion, POSIX ACL and WSL permission helpers, block-layer bios, and reparse metadata.

Risks: attribute enumeration must reject malformed MFT records without leaking partially initialized runs. Creation has many ordered side effects and rollback paths. Iomap valid-size handling must avoid exposing stale disk contents. Resident data writeback and conversion to nonresident paths are delicate. Symlink parsing handles multiple reparse formats and path translations with fixed-size buffers. Sequence mismatch and reused MFT references must produce `-ESTALE`.

Test signals: iget for regular, resident, compressed, sparse, directory, special, symlink, `$Extend`, and malformed records; file size grow/shrink boundaries; buffered/direct writes with delayed allocation; reads beyond valid size zero-filled; MFT sequence reuse; create/mkdir/mknod/symlink with ACL/EA/reparse rollback; hardlink/unlink/rmdir on nonempty and metadata files; symlink/junction/OneDrive reparse reads; writeback under forced shutdown and bad-inode states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.c

Purpose: provides the shared canonical Huffman decode-table builder used by the NTFS3 XPRESS and LZX decompressors. It translates arrays of codeword lengths into compact direct-lookup and binary-tree tables consumed by `read_huffsym()`.

Important APIs and functions: the file implements `make_huffman_decode_table(u16 decode_table[], u32 num_syms, u32 table_bits, const u8 lens[], u32 max_codeword_len, u16 working_space[])`. The table format stores direct entries as `(codeword_len << 11) | symbol`; entries with high bits `0xC000` point to binary-tree child nodes for codewords longer than `table_bits`.

Control flow: the builder counts symbols per codeword length, verifies the prefix code is neither oversubscribed nor incomplete except for the explicitly allowed empty code, sorts symbols by canonical order using offset buckets, fills direct lookup entries for codewords up to `table_bits`, then allocates tree nodes for longer codewords. Empty codes zero the direct table so accidental decode attempts do not read uninitialized entries.

State and persistence behavior: no persistent state is stored. The caller owns `decode_table` and `working_space`, usually inside a reusable decompressor object. The function mutates only those buffers and returns `0` for valid tables or `-1` for invalid code-length sets.

Dependencies and integration points: included by XPRESS and LZX decompressor code under `fs/ntfs3/lib`. It relies on kernel `memset` and integer types, and its output is interpreted by inline bitstream/Huffman routines in `decompress_common.h`.

Risks: bounds are contractual: callers must supply a large enough decode table and working space, and all lengths must be <= `max_codeword_len`. A bad prefix-code validation bug can turn malformed compressed input into out-of-bounds table traversal. The long-codeword tree encoding shares the `u16` value space with symbols and length-tagged entries, so constants must stay consistent with symbol limits.

Test signals: valid XPRESS and LZX compressed samples, empty-code tables, oversubscribed and incomplete code-length arrays, maximum-length codewords that force tree allocation, short-code fast path coverage, and fuzzed compressed streams under KASAN/UBSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.h -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.h

Purpose: defines shared inline primitives for XPRESS and LZX decompression: endian-safe bitstream reading, Huffman symbol decoding, unaligned word helpers, byte repetition, and LZ77 match copying.

Important APIs and types: defines `struct input_bitstream`, `init_input_bitstream`, `bitstream_ensure_bits`, peek/remove/pop/read bit helpers, literal byte/u16/u32/bytes readers, `bitstream_align`, `read_huffsym`, and `lz_copy`. It declares `make_huffman_decode_table`. `FAST_UNALIGNED_ACCESS` enables word-at-a-time copying on architectures where it is expected to be safe and fast.

Control flow: decompressor callers initialize a bitstream over compressed bytes, ensure enough bits before peeking/removing them, read Huffman symbols through a direct table lookup or slow tree traversal, and copy LZ matches from already-written output via `lz_copy`. `lz_copy` takes fast paths for non-overlapping word copies and offset-one run filling, otherwise falls back to bytewise overlapping copy.

State and persistence behavior: state is per-bitstream and per-output-buffer only. Missing literal bytes or integers return zero in several helpers, while higher-level decompressor validation is responsible for rejecting invalid streams. `lz_copy` assumes the caller has already validated match bounds and does not persist anything.

Dependencies and integration points: uses Linux compiler/type/string/slab/unaligned helpers and is included by `xpress_decompress.c`, `lzx_decompress.c`, and `decompress_common.c`. It is part of NTFS system-compression support and indirectly participates in compressed file reads.

Risks: bit-buffer semantics are specialized: bits are read from little-endian 16-bit units but ordered high-to-low in `bitbuf`. Callers can overrun logical input if they do not separately validate compressed-stream structure. `lz_copy` can intentionally overcopy up to a word within the output buffer slack, so its bound checks and `bufend` contract are critical. Architecture-specific unaligned access assumptions need build coverage.

Test signals: decode known XPRESS/LZX data on x86 and non-fast-unaligned architectures, fuzz truncated bitstreams, validate overlapping copies for offsets 1 through word size, verify output-tail overcopy never crosses `bufend`, and compare against a reference decompressor for random valid streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/decompress_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/lib.h -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/lib.h

Purpose: declares the small public interface of the NTFS3 XPRESS and LZX decompression library used by system-compressed file handling.

Important APIs and types: forward-declares `struct xpress_decompressor` and `struct lzx_decompressor`; declares allocator/free pairs `xpress_allocate_decompressor`/`xpress_free_decompressor` and `lzx_allocate_decompressor`/`lzx_free_decompressor`; and declares `xpress_decompress` and `lzx_decompress`, each taking compressed input, compressed size, output buffer, and expected uncompressed size.

Control flow: callers allocate a reusable decompressor context, call the relevant format-specific decompressor for one buffer, then free the context. The header itself has no executable control flow.

State and persistence behavior: decompressor contexts are opaque to callers and hold reusable Huffman tables and scratch buffers. There is no persistent on-disk state here; persistence is in the NTFS file data streams that higher layers read.

Dependencies and integration points: includes Linux types and is included by the XPRESS and LZX implementations and by NTFS compression code that chooses the algorithm for WOF/system-compressed data.

Risks: return conventions are `0` success and `-1` decompressor failure for XPRESS/LZX, not Linux `-errno` values. Callers must not assume the opaque contexts are interchangeable, must pass exact uncompressed sizes, and must handle allocation failure with `GFP_NOFS` constraints.

Test signals: compile with and without `CONFIG_NTFS3_LZX_XPRESS`, allocation failure injection, API misuse checks in callers, and known XPRESS/LZX decompression vectors through the public prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/lzx_decompress.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/lzx_decompress.c

Purpose: implements an LZX decompressor for NTFS system-compressed files, specialized for the 32 KiB window size used by this driver. It decodes verbatim, aligned-offset, and uncompressed LZX blocks and applies the x86 E8 postprocessing transform.

Important APIs and functions: public functions are `lzx_allocate_decompressor`, `lzx_decompress`, and `lzx_free_decompressor`. Internal helpers include `lzx_postprocess`, `undo_e8_translation`, Huffman readers for pre/main/length/aligned codes, `lzx_read_codeword_lens`, `lzx_read_block_header`, and `lzx_decompress_block`. `struct lzx_decompressor` holds decode tables, length arrays, precode/aligned-code state, and working space.

Control flow: `lzx_decompress` initializes the bitstream, clears delta-coded main and length code lengths, and loops over blocks until the expected output size is produced. Each block header selects block type and size; compressed blocks rebuild Huffman tables and decode literals or matches; uncompressed blocks align the bitstream, read recent offsets, and copy bytes directly. Match symbols decode length headers, optional length symbols, repeat or explicit offsets, aligned low bits when needed, recent-offset queue updates, bound checks, and `lz_copy`. After output completion, E8 postprocessing runs if literals indicate possible `0xe8` bytes or if an uncompressed block was present.

State and persistence behavior: all decompression state is in the caller-provided context, stack recent-offset queue, input bitstream, and output buffer. Codeword lengths persist across LZX blocks within one compressed buffer because the format delta-encodes them. There is no filesystem persistence in this file.

Dependencies and integration points: uses `decompress_common.h` bitstream, Huffman, and LZ-copy helpers plus prototypes from `lib.h`. It is used by NTFS3 compressed-read support for WOF/system compression.

Risks: malformed streams can target many edge cases: invalid block types, bad Huffman tables, zero recent offsets, block sizes larger than remaining output, offset slots beyond tables, matches before output start, and codeword-length RLE overruns. E8 postprocessing temporarily overwrites the last six output bytes and must restore them. The implementation assumes fixed LZX constants for system compression rather than arbitrary cabinet-style windows.

Test signals: known LZX system-compressed files, blocks of each type, aligned offset blocks with low-bit Huffman decoding, repeat-offset behavior, E8 translation cases near buffer tails and small buffers, invalid/truncated block headers, invalid offsets/lengths, and fuzzing with expected `-1` failures rather than memory errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/lzx_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/xpress_decompress.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lib/xpress_decompress.c

Purpose: implements the Huffman variant of XPRESS decompression used by NTFS system-compressed files.

Important APIs and functions: public functions are `xpress_allocate_decompressor`, `xpress_decompress`, and `xpress_free_decompressor`. `struct xpress_decompressor` stores one Huffman decode table, 512 symbol lengths, and working space for `make_huffman_decode_table`.

Control flow: decompression first reads 256 bytes of packed 4-bit codeword lengths for 512 symbols, builds the Huffman table, initializes a bitstream after the length header, and decodes until the caller-supplied output size is filled. Symbols below 256 emit literal bytes. Symbols 256 and above encode an LZ match: low bits supply a length header, high bits supply `log2_offset`, extra offset bits are read from the bitstream, extended length bytes/u16 may be consumed, bounds are checked, and `lz_copy` copies from prior output.

State and persistence behavior: no persistent state exists. The decompressor context is reusable scratch memory. The output size is authoritative; the function succeeds only after exactly filling it and returns `-1` for malformed data.

Dependencies and integration points: uses shared Huffman, bitstream, and LZ-copy helpers from `decompress_common.h` and is exposed through `lib.h`. Higher NTFS compression code chooses XPRESS for the relevant system-compression format.

Risks: XPRESS input has compact headers, so truncated headers, invalid code-length sets, length extensions, and offset calculations are the main validation points. The code relies on caller-provided output size and validates only match bounds, not trailing compressed-data consumption. Return values are format-style `-1`, so callers must translate or handle consistently.

Test signals: known XPRESS-Huffman samples, literals-only and matches-only streams, long length extension paths, maximum `log2_offset`, offset-before-start rejection, output-overrun rejection, truncated length table, invalid Huffman lengths, and fuzzing with sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lib/xpress_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lznt.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/lznt.c

Purpose: implements NTFS LZNT1 compression and decompression for normal NTFS compressed attributes. It supports a fast hash-based compressor, a slower best-match compressor, and chunked decompression of compressed or stored 4 KiB chunks.

Important APIs and types: public functions are `get_lznt_ctx`, `compress_lznt`, and `decompress_lznt`. Internal state is `struct lznt`, which tracks the current uncompressed chunk, best match, max match length, compression mode, and optional 4 KiB hash table. Helpers include `longest_match_std`, `longest_match_best`, `make_pair`, `parse_pair`, `compress_chunk`, and `decompress_chunk`.

Control flow: compression processes the input in 4 KiB chunks. For each chunk it searches for matches of length at least 3, emits groups controlled by one flag byte per eight tokens, encodes `(offset,length)` pairs with a variable split determined by current output position, and falls back to an uncompressed chunk when compressed output would not fit. All-zero chunks are reported specially so the top-level compressor can return size zero. Decompression reads chunk headers, distinguishes compressed chunks from stored chunks, decodes flag-controlled literals or pairs, validates boundaries and offsets, copies overlapping matches, pads short chunks with zeros when needed, and stops at an all-zero chunk header or when output is full.

State and persistence behavior: the compressor context is heap-allocated and temporary. Persistent effects happen in callers that store compressed NTFS attribute data; this file only produces or consumes buffers. LZNT chunk headers and tokens are on-disk data format.

Dependencies and integration points: uses kernel memory/string helpers and NTFS utility macros from `debug.h`/`ntfs_fs.h`. It is used by compressed attribute read/write paths elsewhere in NTFS3.

Risks: compression and decompression must exactly match LZNT1’s position-dependent offset/length bit split. The standard compressor hashes only two candidate positions, so compression ratio varies by level. Decompression has to reject offset underruns, truncated pairs, chunk-size overflows, and impossible headers without writing past 4 KiB. Returning uncompressed size from `compress_lznt` on compression-buffer exhaustion is a special caller contract.

Test signals: round-trip random and patterned buffers, all-zero chunk return, incompressible fallback chunks, best vs standard compression mode, inputs crossing 4 KiB chunk boundaries, malformed pair offset/length fuzz cases, truncated chunks, short final chunks with zero padding, and comparison against Windows/LZNT1 reference vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/lznt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/namei.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/namei.c

Purpose: provides NTFS3 VFS directory and dentry operations: lookup, create, mknod, link, unlink, symlink, mkdir, rmdir, rename, parent lookup, and case-insensitive dentry hashing/comparison.

Important APIs and functions: exported/registered functions include `fill_name_de`, `ntfs_lookup`, `ntfs_create`, `ntfs_mknod`, `ntfs_link`, `ntfs_unlink`, `ntfs_symlink`, `ntfs_mkdir`, `ntfs_rmdir`, `ntfs_rename`, `ntfs3_get_parent`, `ntfs_d_hash`, and `ntfs_d_compare`. The file defines `ntfs_dir_inode_operations`, `ntfs_special_inode_operations`, and `ntfs_dentry_ops`.

Control flow: lookup converts the VFS name to UTF-16, locks the directory, searches the NTFS directory index, rejects malformed non-base inodes without inode operations, and splices aliases. Create/mknod/symlink/mkdir call `ntfs_create_inode` with the appropriate mode and payload. Link checks directory and link-count constraints, locks parent and target, increments VFS links before `ntfs_link_inode`, and rolls back on failure. Unlink/rmdir lock the directory and call `ntfs_unlink_inode`. Rename rejects unsupported flags and metadata files, unlinks an existing target if present, builds old and new directory entries, locks old dir, inode, and optionally new dir, calls `ni_rename`, then updates timestamps and synchronous-write behavior. Dentry hash/compare use ASCII uppercase fast paths and UTF-16/upcase-table slow paths.

State and persistence behavior: persistent changes are delegated to inode/index helpers that mutate MFT records and directory indexes. This file updates VFS link counts, timestamps, dirty inode state, and dentry instantiation. `fill_name_de` constructs an in-memory `NTFS_DE` containing an `ATTR_FILE_NAME` key for later index insertion/removal.

Dependencies and integration points: depends on NLS conversion, NTFS name collation/upcase tables, inode creation/link/unlink/rename helpers, directory search, ACL/xattr/getattr/setattr/fiemap operations, and VFS dentry/inode operation registration.

Risks: locking order across old directory, target inode, and new directory is important for rename/link correctness. Rename unlinks an existing target before inserting the moved name, so rollback behavior depends on lower helpers. Case-insensitive hashing must match comparison and NTFS collation or dentries can alias incorrectly. UTF-16 conversion failures and `PATH_MAX` scratch buffers limit long names.

Test signals: case-insensitive lookup/hash/compare with ASCII and non-ASCII names, create/mkdir/mknod/symlink and later lookup, hardlink link-count limits, unlink and rmdir on bad/forced-shutdown states, rename same-name no-op, cross-directory rename, rename over existing target, metadata-file rename rejection, parent lookup via `ATTR_NAME`, and Windows-name/NLS edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/namei.c -->
