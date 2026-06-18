# Group Research: group_914_linux_apfs_rw_sources_local_fs_linux_apfs_rw_inode_c_sources_local_f_b0a1ffa91e1e

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/linux-apfs-rw`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/inode.c -->
# File Research: sources/local-fs/linux-apfs-rw/inode.c

## Purpose
Implements APFS VFS inode lifecycle, page-cache read/write integration, inode record serialization, dstream and crypto-state bookkeeping, orphan cleanup, metadata updates, and APFS-specific ioctls.

## Main Responsibilities
- Provides address-space operations for regular files, including `read_folio`/`readpage`, readahead, `write_begin`, and `write_end`.
- Performs APFS copy-on-write write setup by reading existing mapped buffers, clearing mappings, then allocating replacement blocks with `apfs_get_new_block`.
- Creates, updates, and deletes catalog inode records and inode xfields for names, dstreams, sparse-byte counts, and device IDs.
- Tracks APFS dstream records and reference counts, including clone-related exclusive dstream creation through `apfs_inode_create_exclusive_dstream()`.
- Manages encrypted-volume crypto-state records and private file keys through APFS ioctls.
- Creates and populates VFS inodes from catalog queries in `apfs_iget()`.
- Handles setattr, truncate, timestamp updates, file attributes, BSD flags, immutable/append/nodump state, and statx birth time.
- Cleans orphan inodes synchronously for trivial cases and asynchronously through `apfs_orphan_cleanup_work()` for large or partial deletions.

## Key Functions
- `apfs_iget()`: looks up an inode catalog record, fills VFS/APFS inode fields, checks dstream sharing, and unlocks a new inode.
- `apfs_inode_from_query()`: parses an APFS inode record, timestamps, ownership, BSD flags, dstream xfields, sparse bytes, rdev, and compressed-file state.
- `apfs_update_inode()`: flushes extent cache, updates name/dstream/sparse xfields, and writes changed inode metadata back into the catalog node.
- `apfs_new_inode()` and `apfs_create_inode_rec()`: allocate a new VFS inode and persist its initial APFS catalog record.
- `apfs_setattr()` / `apfs_setsize()`: validate and apply VFS attribute changes, using APFS transactions and truncation paths.
- `apfs_delete_inode()`, `apfs_clean_single_orphan()`, `apfs_clean_orphans()`: remove xattrs, extents, dstream records, catalog records, and orphan links.
- `apfs_dir_ioctl()` / `apfs_file_ioctl()`: dispatch APFS key-class, PFK, and snapshot ioctls.

## Dependencies
Uses catalog b-tree operations, extent/truncate logic, xattr deletion, compression helpers, transaction joining/commit/abort, dstream extent cloning, APFS superblock counters, VFS inode/page-cache APIs, and kernel-version compatibility branches.

## Notes
The file is heavily version-gated for Linux API changes from older page APIs through folios, idmapped mounts, fileattr APIs, and timestamp helpers. Several TODOs mark incomplete clone support, `write_inode()` uncertainty, sparse xfield cleanup policy, and crypto-record deletion semantics.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/key.c -->
# File Research: sources/local-fs/linux-apfs-rw/key.c

## Purpose
Parses APFS on-disk b-tree keys into the module’s generic `struct apfs_key` representation and implements key and filename comparison behavior.

## Main Responsibilities
- Compares normalized/case-folded APFS filenames when the volume is normalization-insensitive.
- Compares generic APFS keys by object ID, type, numeric discriminator, and optional name.
- Parses catalog keys for directory records, xattrs, file extents, sibling links, inode-like records, and other catalog entries.
- Parses non-catalog tree keys: file extent tree, spaceman free queue, omap, extent reference, snapshot metadata/name, and omap snapshot keys.
- Builds in-memory directory-record query keys, including APFS normalized-name CRC32C hash calculation.

## Key Functions
- `apfs_filename_cmp()`: compares names directly or through APFS Unicode normalization/case folding.
- `apfs_keycmp()`: provides the ordering used by node and b-tree searches.
- `apfs_read_cat_key()`: validates and decodes catalog keys, including NULL-terminated variable-length names.
- `apfs_read_*_key()`: decodes fixed-size keys for APFS auxiliary trees.
- `apfs_init_drec_key()`: initializes directory lookup keys, using name hash for normalization-insensitive volumes.

## Dependencies
Depends on `apfs.h` on-disk structures, APFS volume flags, CRC32C, and `unicode.c` cursor/normalization helpers.

## Notes
Directory key comparisons intentionally ignore normalization at `apfs_keycmp()` level; normalization-sensitive lookup is handled by hashed key construction and dentry/name comparison.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/key.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/libzbitmap.c -->
# File Research: sources/local-fs/linux-apfs-rw/libzbitmap.c

## Purpose
Provides an in-kernel decompressor for APFS LZBITMAP/ZBM compressed payloads, ported from `libzbitmap` with decompression-only support.

## Main Responsibilities
- Validates the `ZBM\x09` stream magic.
- Iterates chunk headers with 24-bit compressed and decompressed lengths.
- Handles uncompressed chunks by copying payload bytes directly.
- Handles compressed chunks using bitmap metadata regions, nibble-coded bitmap selectors, repetition counts, and periodic back-references.
- Tracks total output length and supports a NULL destination mode for length discovery.

## Key Functions
- `zbm_decompress()`: public entry point; validates magic, decodes chunks until a zero-length final chunk, and returns decompressed length.
- `zbm_handle_chunk()`: reads chunk lengths, bounds-checks source/destination, and dispatches compressed vs uncompressed handling.
- `zbm_handle_compressed_chunk()`: initializes metadata pointers, reads bitmap tables, and expands the chunk.
- `zbm_apply_bitmap()`: emits literal bytes or repeats bytes from the current period.
- `zbm_read_bitmaps()` / `zbm_read_single_bitmap()`: parse trailing bitmap table entries.

## Dependencies
Uses kernel `errno`, `string.h`, and the local `libzbitmap.h` API. It is used by `compress.c` for APFS compressed-resource decoding.

## Notes
The decoder is defensive about malformed input: it checks source bounds, destination capacity, maximum decompressed chunk size, invalid periods, corrupt repetitions, and malformed free-running bitmap lists.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/libzbitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/libzbitmap.h -->
# File Research: sources/local-fs/linux-apfs-rw/libzbitmap.h

## Purpose
Declares the APFS LZBITMAP/ZBM decompression API used by the compression subsystem.

## API
- `zbm_decompress(void *dest, size_t dest_size, const void *src, size_t src_size, size_t *out_len)`: decompresses an LZBITMAP buffer or, with `dest == NULL`, computes the expected decompressed length.

## Dependencies
Includes Linux `errno` and `types` headers.

## Notes
The header documents the dual GPL-2.0+/MIT licensing inherited from the Corellium port and upstream `libzbitmap`.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/libzbitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse.h -->
# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse.h

## Purpose
Public BSD-licensed LZFSE decode API header bundled for APFS compressed-file support.

## API
- `lzfse_decode_scratch_size()`: returns required scratch size.
- `lzfse_decode_buffer()`: decompresses an LZFSE buffer into a caller-provided destination buffer with optional scratch storage.

## Dependencies
Uses Linux `stddef` and `types` headers instead of userspace libc headers.

## Notes
The comments retain upstream Apple wording about malloc/free behavior, while this kernel port’s implementation uses `kmalloc()`/`kfree()` when scratch space is not supplied.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_decode.c -->
# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_decode.c

## Purpose
Implements the public LZFSE buffer decode wrapper around the internal streaming decoder state.

## Main Responsibilities
- Reports scratch size as `sizeof(lzfse_decoder_state)`.
- Initializes `lzfse_decoder_state` source/destination pointers.
- Invokes `lzfse_decode()` and maps internal status codes to public byte-count return values.
- Allocates temporary scratch memory with `kmalloc()` if the caller passes no scratch buffer.

## Key Functions
- `lzfse_decode_scratch_size()`
- `lzfse_decode_buffer_with_scratch()`
- `lzfse_decode_buffer()`

## Dependencies
Depends on `lzfse.h`, `lzfse_internal.h`, and Linux slab allocation.

## Notes
A failed decode returns `0`; a full destination returns `dst_size`, matching the upstream LZFSE API contract.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_decode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_decode_base.c -->
# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_decode_base.c

## Purpose
Contains the core LZFSE stream decoder, including compressed header decoding, FSE literal decoding, L/M/D match execution, uncompressed blocks, and LZVN sub-block dispatch.

## Main Responsibilities
- Decodes V2 compressed headers into V1 header form with packed bitfield extraction and compressed frequency-table decoding.
- Validates V1 block headers through `lzfse_check_block_header_v1()`.
- Builds FSE decoder tables for literal, literal-length, match-length, and distance streams.
- Decodes literal streams and L/M/D triplets using backward FSE bitstreams.
- Emits literals and back-referenced matches into the destination buffer, preserving state when the destination fills mid-symbol.
- Handles LZFSE stream block magic values for end-of-stream, uncompressed, LZFSE V1/V2, and LZVN blocks.

## Key Functions
- `lzfse_decode_v1_freq_value()`: decodes compact frequency-table values.
- `lzfse_decode_v1()`: expands a V2 header into a V1 header.
- `lzfse_decode_lmd()`: executes FSE-decoded literal/match/distance records.
- `lzfse_decode()`: top-level internal decoder state machine.

## Dependencies
Uses `lzfse_internal.h`, `lzfse_fse.c/.h` table initialization and bitstream helpers, and `lzvn_decode_base.h` for LZVN block decoding.

## Notes
The decoder requires full encoded block payloads to be available in source while allowing partial destination progress. It performs explicit distance, block-size, header-size, and frequency sanity checks before emitting data.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_decode_base.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_fse.c -->
# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_fse.c

## Purpose
Builds finite-state entropy decoder tables used by the LZFSE decoder.

## Main Responsibilities
- Initializes symbol decoder tables from normalized frequency histograms.
- Initializes value decoder tables for L/M/D streams, combining FSE state transition data with extra-bit counts and base values.
- Validates that cumulative frequencies do not exceed the declared number of states for plain decoder table initialization.

## Key Functions
- `fse_init_decoder_table()`: fills compact 32-bit decoder entries containing symbol, bit count, and delta.
- `fse_init_value_decoder_table()`: fills value decoder entries containing total bits, extra value bits, state delta, and base value.

## Dependencies
Includes `lzfse_internal.h`, which supplies table entry types and L/M/D configuration.

## Notes
This file is decode-only support from Apple’s BSD-licensed LZFSE code; encode-side table generation is not present in this source tree.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_fse.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_fse.h -->
# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_fse.h

## Purpose
Defines the finite-state entropy bitstream types, table entry formats, inline decode helpers, and table initialization declarations used by LZFSE.

## Main Responsibilities
- Selects 64-bit or 32-bit FSE streams based on architecture.
- Provides mask/extract helpers for 32-bit and 64-bit bit containers.
- Defines output and input stream accumulators and inline stream push/pull/flush helpers.
- Defines `fse_decoder_entry` and `fse_value_decoder_entry`.
- Provides inline `fse_decode()` and `fse_value_decode()` routines.
- Provides `fse_check_freq()` and declarations for decoder-table builders.

## Key Types and APIs
- `fse_state`, `fse_bit_count`, `fse_in_stream`, `fse_out_stream`
- `fse_decode()`
- `fse_value_decode()`
- `fse_init_decoder_table()`
- `fse_init_value_decoder_table()`

## Dependencies
Uses Linux `types` and `string` headers.

## Notes
The decoder reads FSE input streams backward. The checked init/flush helpers reject out-of-range pointers and malformed accumulator states.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_fse.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_internal.h -->
# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_internal.h

## Purpose
Defines internal LZFSE/LZVN constants, decoder state structures, block header layouts, utility functions, header validation, and L/M/D coding tables.

## Main Responsibilities
- Defines status codes, state counts, symbol counts, block magic constants, and maximum matches/literals per block.
- Defines decoder state for compressed LZFSE blocks, LZVN blocks, uncompressed blocks, and the overall stream.
- Defines on-stream block headers for uncompressed, LZFSE V1, LZFSE V2, and LZVN blocks.
- Provides unaligned-safe load/store/copy helpers.
- Provides bitfield `extract()` / `insert()` utilities.
- Validates compressed V1 headers and normalized frequency tables.
- Supplies L/M/D extra-bit and base-value tables.

## Key Types
- `lzfse_decoder_state`
- `lzfse_compressed_block_decoder_state`
- `lzfse_compressed_block_header_v1`
- `lzfse_compressed_block_header_v2`
- `lzvn_compressed_block_header`

## Dependencies
Includes `lzfse_fse.h` and Linux limits/stddef headers.

## Notes
`LZFSE_ENCODE_HASH_BITS` is referenced in a hash-values macro but encoding support is otherwise absent; the active decode path uses the decode-specific constants and tables.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzfse_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzvn_decode_base.c -->
# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzvn_decode_base.c

## Purpose
Implements the low-level LZVN decoder used for LZFSE streams that contain LZVN-compressed blocks.

## Main Responsibilities
- Dispatches all 256 opcode values through a computed-goto jump table.
- Handles opcodes for small/medium/large distance literal+match pairs, previous-distance matches, literal-only runs, match-only runs, NOP, EOS, and undefined opcodes.
- Copies literals from source and matches from previously emitted destination bytes.
- Preserves partial literal/match state when the destination buffer fills.
- Maintains previous match distance for opcodes that reuse it.

## Key Function
- `lzvn_decode(lzvn_decoder_state *state)`: updates source pointer, destination pointer, previous distance, partial L/M/D state, and EOS status in place.

## Dependencies
Includes `lzvn_decode_base.h`, Linux compiler/version headers, and utility functions from `lzfse_internal.h`.

## Notes
The decoder uses wide 4-byte and 8-byte copies on fast paths but falls back to byte-wise copies near buffer ends or for overlapping short-distance matches. Invalid match distances and undefined opcodes stop decoding after state has been updated to the last good instruction boundary.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzvn_decode_base.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzvn_decode_base.h -->
# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzvn_decode_base.h

## Purpose
Declares the low-level LZVN decoder state and decode function.

## Main Types and API
- `lzvn_decoder_state`: holds source/destination bounds, current pointers, partial literal/match state, previous distance, and end-of-stream flag.
- `lzvn_decode(lzvn_decoder_state *state)`: decodes source into destination and updates the state in place.

## Dependencies
Includes `lzfse_internal.h` for shared LZFSE/LZVN offset types and utilities.

## Notes
The header labels this as the low-level v2 API and notes that higher-level low-level APIs should switch to it.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/lzfse/lzvn_decode_base.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/message.c -->
# File Research: sources/local-fs/linux-apfs-rw/message.c

## Purpose
Provides the module’s centralized APFS logging helper.

## Main Function
- `apfs_msg()`: formats APFS log messages with kernel log prefix, superblock ID or `?`, optional function and line metadata, and a varargs message.

## Dependencies
Uses Linux `fs.h`, `printk()`, `va_format`, and APFS logging macros declared in `apfs.h`.

## Notes
The helper supports callers without a superblock by printing `APFS (?)`.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/message.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/namei.c -->
# File Research: sources/local-fs/linux-apfs-rw/namei.c

## Purpose
Connects APFS directory lookup, symlink creation, inode operations, and dentry operations to the Linux VFS.

## Main Responsibilities
- Looks up dentries by name through APFS catalog directory records.
- Creates symlinks through the shared `apfs_mkany()` creation path.
- Defines inode operation tables for directories and special files.
- Defines APFS dentry hashing and comparison behavior for case/normalization-insensitive volumes.
- Revalidates negative dentries when create/rename could collide with a normalized equivalent name.

## Key Functions
- `apfs_lookup()`: validates name length, resolves inode number with `apfs_inode_by_name()`, and returns `d_splice_alias()`.
- `apfs_symlink()`: creates APFS symlink inodes with fixed symlink permissions.
- `apfs_dentry_hash()`: hashes normalized Unicode codepoints for normalization-insensitive volumes.
- `apfs_dentry_compare()`: delegates comparison to `apfs_filename_cmp()`.
- `apfs_dentry_revalidate()`: rejects RCU lookup and invalidates relevant negative dentries.

## Dependencies
Uses VFS namei APIs, APFS directory/create/xattr/setattr functions, and Unicode normalization helpers.

## Notes
The file is mostly operation-table wiring, with kernel-version conditionals for symlink and dentry revalidate signatures.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/linux-apfs-rw/node.c -->
# File Research: sources/local-fs/linux-apfs-rw/node.c

## Purpose
Implements APFS b-tree node storage, validation, lookup within nodes, record insertion/replacement, node splitting, free-space management, and node creation/deletion.

## Main Responsibilities
- Reads APFS b-tree nodes from virtual, physical, or ephemeral storage.
- Verifies node checksums and node table-of-contents bounds to protect against crafted filesystems.
- Creates empty b-tree roots for supported physical trees and creates/deletes nonroot nodes.
- Maintains in-memory node metadata and writes it back to on-disk node headers.
- Locates key/value byte ranges for fixed-size and variable-size node formats.
- Parses keys for catalog, omap, free queue, extentref, fext, snapshot metadata, and omap snapshot queries.
- Executes bisection searches, previous/next iteration, exact and multiple-record node-local queries.
- Extracts omap mappings from successful omap queries.
- Increases b-tree height, splits nodes, creates single-record nodes for huge catalog records, and attaches new children to parents.
- Manages fragmented key/value free lists, node defragmentation, TOC expansion, record insertion, and record replacement.

## Key Functions
- `apfs_read_node()`: maps an object ID to a block or ephemeral object, reads node metadata, validates it, and returns an `apfs_node`.
- `apfs_make_empty_btree_root()`: allocates and initializes an empty root node and info footer for supported b-tree subtypes.
- `apfs_delete_node()`: frees catalog/omap/extent/snapshot physical nodes or ephemeral free-queue nodes according to query type.
- `apfs_node_locate_key()` / `apfs_node_locate_value()`: convert TOC entries into checked block offsets and lengths.
- `apfs_node_query()`: searches a node and prepares query offsets for b-tree traversal.
- `apfs_btree_inc_height()` and `apfs_node_split()`: handle growth and split propagation for insertions.
- `apfs_node_has_room()`, `apfs_node_insert()`, `apfs_node_replace()`: implement space checks and record mutation.
- `apfs_defragment_node()` and free-list helpers: rebuild fragmented nodes through temporary full-node copies.

## Dependencies
Uses APFS object mapping, spaceman block allocation/free queues, omap record creation/deletion, transactions, checksums, b-tree query structures from `apfs.h`, and key parsers from `key.c`.

## Notes
The implementation explicitly handles APFS quirks such as root info footers, backward-counted value offsets, fixed key/value TOCs, free-queue ghost records, ephemeral objects, and huge catalog values that may require one-record nodes.
<!-- END FILE RESEARCH: sources/local-fs/linux-apfs-rw/node.c -->