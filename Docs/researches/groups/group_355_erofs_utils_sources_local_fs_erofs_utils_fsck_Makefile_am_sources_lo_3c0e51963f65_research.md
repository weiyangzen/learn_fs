# Group Research: group_355_erofs_utils_sources_local_fs_erofs_utils_fsck_Makefile_am_sources_lo_3c0e51963f65

Read scope: `Docs/research_subset_a.md`. All listed files were read completely. This group covers `fsck.erofs`, core `liberofs` build wiring, EROFS read/write buffering, compression/decompression, fragments, dedupe, chunk/blob storage, NBD backend helpers, and small shared utilities.

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/fsck/Makefile.am -->
# File Research: sources/local-fs/erofs-utils/fsck/Makefile.am

## Purpose
Automake build file for the `fsck.erofs` executable and optional libFuzzer target.

## Key Details
- Builds `bin_PROGRAMS = fsck.erofs` from `main.c`.
- Uses `-Wall -I$(top_srcdir)/include` and links `$(top_builddir)/lib/liberofs.la`.
- Adds `${libuuid_CFLAGS}` to preprocessor flags.
- Under `ENABLE_FUZZING`, builds `fuzz_erofsfsck` from the same `main.c` with `-DFUZZING`.
- Fuzzer target links with `-fsanitize=address,fuzzer`.

## Interactions
- Depends on `lib/liberofs.la`, which supplies EROFS image parsing, decompression, xattrs, directory iteration, blob devices, and packed-file helpers.
- The fuzz target activates the alternate entry points in `fsck/main.c`.

## Notes
This file is build orchestration only; no runtime logic.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/fsck/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/fsck/main.c -->
# File Research: sources/local-fs/erofs-utils/fsck/main.c

## Purpose
Implements `fsck.erofs`, including image opening, superblock verification, inode traversal, xattr validation/dumping, optional decompression verification, extraction to a host directory, hardlink preservation, packed-fragment verification, compression-ratio accounting, and fuzzing entry points.

## Main Structures
- `struct erofsfsck_cfg`: global fsck state, including traversal stack, extract path, counters, options, target nid/path, and corruption flag.
- `struct erofsfsck_dirstack`: recursion/loop guard for directory traversal.
- `struct erofsfsck_hardlink_entry`: extraction-time nid-to-path table for non-directory hardlinks.
- `struct erofsfsck_get_parent_ctx`: helper context for resolving `..` when checking a non-root directory.

## Important Functions
- `erofsfsck_parse_options_cfg()`: parses CLI options such as `--extract`, `--device`, `--offset`, `--nid`, `--path`, `--xattrs`, `--no-sbcrc`, preserve flags, and verbosity.
- `erofs_verify_xattr()`: validates inode xattr ibody layout and entry boundaries.
- `erofsfsck_dump_xattrs()`: lists and optionally restores xattrs during extraction, with non-root handling for non-user namespaces.
- `erofs_verify_inode_data()`: maps every file extent, validates lengths, optionally decompresses/reads data, writes extraction output, and counts logical/physical blocks.
- `erofs_extract_dir()`, `erofs_extract_file()`, `erofs_extract_symlink()`, `erofs_extract_special()`: extraction handlers by inode type.
- `erofsfsck_dirent_iter()`: directory callback that extends the current path and recurses into `erofsfsck_check_inode()`.
- `erofsfsck_check_inode()`: central recursive verifier for one inode.
- `main()` / `erofsfsck_fuzz_one()`: initialize config, open devices, read superblock, initialize packed file if needed, choose target inode, run verification, and clean up.
- `LLVMFuzzerTestOneInput()`: writes fuzzer input to a temp file and invokes the fuzzing main path.

## Behavior
- Extraction with `--extract=X` implies decompression/data verification and writes files under a bounded `PATH_MAX` buffer.
- Extraction to `/` is blocked unless `--force` is present.
- `--overwrite` may remove/retry existing files or directories, but uses `O_NOFOLLOW` for regular-file creation.
- Packed fragment inode is verified before the root tree when fragments are enabled.
- Directory traversal checks for loops, `.`/`..` correctness, and path length.
- Non-I/O verification failures set `fsckcfg.corrupted`; final exit status is `1` on any error/corruption.

## Interactions
- Uses `erofs_read_superblock`, `erofs_read_inode_from_disk`, `erofs_map_blocks`, `z_erofs_read_one_data`, `erofs_read_one_data`, `erofs_iterate_dir`, `erofs_iopen`, xattr helpers, blob-device helpers, and packed-file helpers.
- Lists available compressors via `z_erofs_list_available_compressors()` from the compressor registry.

## Notes
The file combines verification and extraction. Most corruption findings return negative errno-style values internally but convert to process exit code `1`.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/fsck/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/Makefile.am -->
# File Research: sources/local-fs/erofs-utils/lib/Makefile.am

## Purpose
Automake build file for the internal `liberofs.la` library and optional test programs.

## Key Details
- Defines `noinst_LTLIBRARIES = liberofs.la`.
- Lists installed-in-tree headers under `noinst_HEADERS`, including public `include/erofs/*` headers and internal `lib/liberofs_*` headers.
- Core sources include config, I/O, cache, superblock, inode, xattr, data mapping, compression, decompression, zmap, fragments, dedupe, tar, rebuild, diskbuf, blobchunk, metabox, importer, base64, and more.
- Conditional sources:
  - LZ4/LZ4HC compressors.
  - liblzma compressor.
  - libdeflate compressor.
  - libzstd compressor.
  - bundled `xxhash.c` fallback when system xxhash is unavailable.
  - S3 remote support.
  - workqueue for multithreaded EROFS compression.
  - Linux NBD backend.
  - OCI/docker config remotes and gzran support.
- Adds dependency flags/libs for uuid, selinux, lz4, lzma, zlib, libdeflate, zstd, QPL, curl, OpenSSL, libxml2, libnl3, json-c, and pthread as configured.

## Interactions
- This build file determines which compression and backend implementations are compiled and therefore which algorithms/backends `mkfs`, `fsck`, and other tools can use.
- `fsck/Makefile.am` links directly against this library.

## Notes
The file is the main feature-gating point for `liberofs`.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/backends/nbd.c -->
# File Research: sources/local-fs/erofs-utils/lib/backends/nbd.c

## Purpose
Implements Linux Network Block Device helper functions for serving or managing EROFS images through `/dev/nbd*`, using ioctl and optionally generic netlink.

## Main Areas
- NBD ioctl constants and protocol request/reply magic.
- Device state probing through `/sys/block/nbdX`.
- Legacy ioctl connection setup using `socketpair()`.
- Optional libnl generic-netlink connect/reconnect/reconfigure/disconnect.
- NBD request parsing and reply header writing.

## Important Functions
- `erofs_nbd_in_service()`: checks `/sys/block/nbdN/size` and `pid` to determine if a device is connected and returns pid or negative errno.
- `erofs_nbd_devscan()`: scans `/sys/block` for an apparently unused `nbdX`.
- `erofs_nbd_connect()`: creates a socketpair, configures block size, block count, timeout, read-only flags, and socket through ioctls.
- `erofs_nbd_get_identifier()`: reads `/sys/block/nbdN/backend`.
- `erofs_nbd_get_index_from_minor()`: maps NBD minor to `nbdX` by reading `/sys/dev/block/<major>:<minor>/uevent`.
- `erofs_nbd_nl_connect()`, `erofs_nbd_nl_reconnect()`, `erofs_nbd_nl_reconfigure()`, `erofs_nbd_nl_disconnect()`: generic-netlink NBD operations when available; stubs return `-EOPNOTSUPP` otherwise.
- `erofs_nbd_do_it()`: runs `NBD_DO_IT` and treats expected `EPIPE` disconnect as success.
- `erofs_nbd_get_request()`: reads and byte-swaps an NBD request.
- `erofs_nbd_send_reply_header()`: writes the protocol reply header.
- `erofs_nbd_disconnect()`: issues disconnect and clears socket.

## Interactions
- Uses `erofs_io_read`, `erofs_vfile`, `erofs_strerror`, and logging helpers.
- Linux-only source selected by `OS_LINUX` in `lib/Makefile.am`.

## Notes
The code supports both older ioctl setup and newer netlink setup; netlink support is compile-time optional.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/backends/nbd.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/base64.c -->
# File Research: sources/local-fs/erofs-utils/lib/base64.c

## Purpose
Small base64 encode/decode utility implementation for `liberofs`.

## Important Functions
- `erofs_base64_encode()`: encodes bytes into the standard `A-Z a-z 0-9 + /` alphabet and appends `=` padding.
- `erofs_base64_decode()`: decodes a base64 string, tolerates trailing padding, and returns decoded length or negative errors.

## Behavior
- Decode returns `-2` for invalid characters.
- Decode returns `-1` for invalid residual bits or invalid padded residual data.
- No NUL terminator is written by encode; caller receives output length.

## Interactions
- Uses `liberofs_base64.h` and EROFS integer/bit helpers.

## Notes
The implementation is self-contained and does not allocate memory.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/base64.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/bitops.c -->
# File Research: sources/local-fs/erofs-utils/lib/bitops.c

## Purpose
Provides a userspace implementation of a bit-scan helper used by EROFS buffer/cache logic.

## Important Functions
- `erofs_find_next_bit()`: finds the next set bit in an `unsigned long` bitmap starting at `start`, bounded by `nbits`.

## Behavior
- Returns `nbits` if `start >= nbits` or no bit is found.
- Masks bits before `start` in the first word.
- Advances by `BITS_PER_LONG` until a nonzero word is found.

## Interactions
- Used by `cache.c` bucket bitmap scanning.
- Depends on `erofs/bitops.h`.

## Notes
This mirrors kernel-style bitmap search semantics in a small userspace helper.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/bitops.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/blobchunk.c -->
# File Research: sources/local-fs/erofs-utils/lib/blobchunk.c

## Purpose
Implements blob/chunk-based file storage for mkfs/import paths, including chunk dedupe, sparse-hole chunks, external blob device handling, tar source mapping, and chunk index writing.

## Main Structures
- `struct erofs_blobchunk`: hash/list entry containing SHA-256, device id, chunk size or source offset, and block address.
- Global `blob_hashmap`: dedupe map keyed by chunk SHA-256.
- Global `erofs_holechunk`: sentinel chunk for holes.
- `unhashed_blobchunks`: chunks that reference pre-existing external/tar data without content hashing.

## Important Functions
- `erofs_blob_getchunk()`: hashes chunk data, deduplicates unless disabled, writes new chunks to the blob file, pads to block size, and records hash entries.
- `erofs_inode_fixup_chunkformat()`: upgrades chunk format to 48-bit if device/block addresses exceed 32-bit capacity.
- `erofs_write_chunk_indexes()`: serializes in-memory chunk pointers into on-disk block-map or chunk-index records, including block-list output.
- `erofs_blob_mergechunks()`: coalesces chunk index granularity when contiguous chunks allow a larger chunk size.
- `erofs_blob_write_chunked_file()`: converts a regular file into chunk-based extents, detecting holes with `SEEK_DATA`, deduping chunks, aligning data if needed, and choosing merge size.
- `erofs_write_zero_inode()`: creates a chunk-based inode entirely backed by null-address chunks.
- `tarerofs_write_chunkes()`: builds chunk indexes for tar-imported data, supporting extra device mode and 48-bit addressing.
- `erofs_mkfs_dump_blobs()`: appends the temporary blob data into the final image unless external devices are used.
- `erofs_blob_init()` / `erofs_blob_exit()`: open temp/output blob file, initialize hash map, insert zero-chunk entry, and free all state.

## Interactions
- Uses SHA-256, generic hashmap, buffer manager allocation, block-list source map writing, temp files, and global mkfs config.
- Cooperates with `data.c` chunk-based mapping and EROFS chunk index on-disk formats.

## Notes
Zero-filled chunks are treated as holes by inserting the zero hash with `EROFS_NULL_ADDR`.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/blobchunk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/block_list.c -->
# File Research: sources/local-fs/erofs-utils/lib/block_list.c

## Purpose
Implements optional block/source mapping output for tar/blob chunk workflows.

## Important Functions
- `erofs_blocklist_open()`: registers an output `FILE *` and whether source-map output is enabled.
- `erofs_blocklist_close()`: clears and returns the registered file pointer.
- `tarerofs_blocklist_write()`: writes block address, block count, source offset, and optional zeroed tail length.

## Behavior
- Writes nothing when no file is registered, block count is zero, or source-map mode is disabled.
- Formats values as hex block/source ranges for external tooling.

## Interactions
- Called from `blobchunk.c` when chunk index extents are serialized.

## Notes
The file contains a comment noting the interface needs cleanup.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/block_list.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/cache.c -->
# File Research: sources/local-fs/erofs-utils/lib/cache.c

## Purpose
Implements the EROFS userspace buffer manager used by mkfs-style writers to allocate, pack, map, flush, drop, and account metadata/data buffer blocks.

## Main Concepts
- `erofs_bufmgr`: owns watermeter buckets, bitmap accelerators, block list, tail block address, metablk count, data-unit alignment, and output vfile.
- `erofs_buffer_block`: block-sized logical allocation unit, initially unmapped or mapped.
- `erofs_buffer_head`: individual allocation inside a buffer block with a flush operation.

## Important Functions
- `erofs_buffer_init()`: initializes watermeters, bucket bitmaps, sentinel block, tail block, and output vfile.
- `__erofs_battach()`: core placement routine for attaching/reserving space in a buffer block with alignment and inline-boundary constraints.
- `erofs_bh_balloon()`: grows the tail buffer head.
- `erofs_bfind_for_attach()`: searches watermeter buckets for a reusable block that best fits a new allocation.
- `erofs_balloc()`: allocates a new buffer head, reusing an existing block when possible.
- `erofs_battach()`: attaches a follow-on buffer head after an existing one.
- `erofs_mapbh()` / `__erofs_mapbh()`: assigns physical block addresses and honors data-stripe alignment.
- `erofs_bflush()`: maps and flushes buffer blocks before a boundary.
- `erofs_bdrop()`: drops/revokes a buffer head and frees the block if empty.
- `erofs_total_metablocks()`: returns metadata block accounting.
- `erofs_buffer_exit()`: abort-flushes remaining buffers and frees manager state.

## Interactions
- Flush callbacks are supplied through `struct erofs_bhops`; built-ins include direct drop and skip-write.
- Used by compression, blob dumping, superblock/config writing, inode writing, and other mkfs paths.

## Notes
Watermeter buckets are indexed by used bytes and mapped/unmapped state to reduce fragmentation and find high-fill placements.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compress.c -->
# File Research: sources/local-fs/erofs-utils/lib/compress.c

## Purpose
Core EROFS compression writer. It builds compressed data extents, handles inline tail packing, fragment packing/dedupe, pcluster sizing, compact/full/extent index generation, optional multithreaded compression, directory compression, and compression algorithm initialization/config metadata.

## Main Structures
- `struct z_erofs_compress_ictx`: per-inode compression context.
- `struct z_erofs_compress_sctx`: per-segment compression context.
- `struct erofs_compress_cfg`: compressor handle plus parameter set and on-disk algorithm type.
- `struct z_erofs_mgr`: compression manager with configured compressors and, in MT builds, fragment slots.
- `struct z_erofs_extent_item`: in-memory compressed/raw/fragment extent list node.

## Important Flow
- `erofs_prepare_compressed_file()`: initializes inode compression state, chooses compressor config, determines data alignment and max compressed extent size, and allocates/chooses compression context.
- `erofs_bind_compressed_file_with_fd()`: binds a source fd/vfile offset to the compression context.
- `erofs_begin_compressed_file()`: computes fragment tail hash, optionally finds matching tail fragments, handles all-fragment files, and queues MT work when enabled.
- `erofs_write_compressed_file()`: single-thread compression path; allocates data buffer, compresses segment, and commits metadata/data.
- `erofs_commit_compressed_file()`: commits fragments, writes indexes, checks space savings, finalizes dedupe commits, updates inode layout and block counts.
- `z_erofs_compress_init()` / `z_erofs_compress_exit()`: initialize compressor configs, feature bits, compression config metadata, pcluster limits, MT state, and free resources.

## Compression Details
- `__z_erofs_compress_one()` decides among compressed pcluster, raw block, inline pcluster, fragment packing, and no-compression fallback.
- `z_erofs_compress_dedupe()` searches existing dedupe windows and emits partial extents when matched.
- `write_uncompressed_block()` supports interlaced uncompressed pclusters.
- `tryrecompress_trailing()` attempts a smaller trailing pcluster for inline/tail efficiency.
- Fragment packing integrates with `fragments.c` and marks `Z_EROFS_ADVISE_FRAGMENT_PCLUSTER`.
- Index writing supports legacy full indexes, compacted 2B/4B indexes, big pcluster encoding, 48-bit encoded extents, and simplified all-fragment files.

## Multithreading
- Enabled by `EROFS_MT_ENABLED`.
- Workqueue TLS owns per-worker queue, destination buffer, and compressor handles.
- `z_erofs_mt_compress()` segments files and queues work.
- `erofs_mt_write_compressed_file()` waits for workers, merges segment extents, performs cross-segment dedupe where possible, and commits output.
- Force-on dedupe disables MT because MT dedupe is not implemented.

## Interactions
- Uses `compressor.c` registry/backends, `dedupe.c`, `dedupe_ext.c`, `fragments.c`, `cache.c`, `block_list.c`, `compress_hints.c`, `metabox`, importer params, and global config.
- Writes compression algorithm config metadata read later by `decompress.c`.

## Notes
This is the highest-complexity file in the group. It is the main bridge between source file data and EROFS compressed on-disk metadata.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compress_hints.c -->
# File Research: sources/local-fs/erofs-utils/lib/compress_hints.c

## Purpose
Loads and applies path-based compression hints for mkfs/import compression decisions.

## Main Data
- `compress_hints_head`: list of compiled regex hints.
- Each hint records physical cluster block count and compressor configuration index.

## Important Functions
- `erofs_load_compress_hints()`: parses the configured hints file, validates pcluster sizes and compressor config indexes, compiles patterns, and updates max pcluster blocks if needed.
- `z_erofs_apply_compress_hints()`: matches an inode source path and sets `inode->z_physical_clusterblks` and `inode->z_algorithmtype[0]`.
- `erofs_cleanup_compress_hints()`: frees hint entries.

## Behavior
- Hint file lines accept pcluster size, optional compressor config id, and regex/path pattern.
- Pcluster size `0` means the matched file should not be compressed.
- Invalid regex emits a detailed regex error.

## Interactions
- Called by `compress.c` when choosing pcluster size if `cfg.c_compress_hints_file` is set.
- Uses `erofs_fspath()` so hints match paths relative to the configured root.

## Notes
The `algorithmtype` field is a compressor configuration index here, not directly the on-disk algorithm id.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compress_hints.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor.c -->
# File Research: sources/local-fs/erofs-utils/lib/compressor.c

## Purpose
Central registry and dispatch layer for EROFS compression backends.

## Main Data
- `erofs_algs[]`: maps user-visible names to compressor implementations and on-disk algorithm ids.
- Registered names include `lz4`, optional `lz4hc`, `lzma`, `deflate`, optional `libdeflate`, and `zstd`.

## Important Functions
- `z_erofs_get_compress_algorithm_id()`: returns on-disk algorithm id for a handle.
- `z_erofs_list_supported_algorithms()`: lists unique supported algorithm names, masking duplicate ids/optimizers.
- `z_erofs_list_available_compressors()`: iterates compiled-in compressor entries.
- `erofs_compress_destsize()` and `erofs_compress()`: dispatch to backend callbacks.
- `erofs_compressor_init()`: validates requested algorithm, level, dict size, extra options, runs preinit/setters/init, and binds selected algorithm.
- `erofs_compressor_exit()` / `erofs_compressor_reset()`: backend lifecycle dispatch.

## Interactions
- Used by mkfs compression setup and fsck help/version output.
- Backend implementations are in `compressor_*.c`.

## Notes
Optimizer aliases such as `lz4hc` and `libdeflate` can share an on-disk algorithm id with a base algorithm while exposing a different implementation.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor.h -->
# File Research: sources/local-fs/erofs-utils/lib/compressor.h

## Purpose
Internal compression backend interface.

## Main Types
- `struct erofs_compressor`: backend vtable with lifecycle, level/dict/extra option setters, and compression callbacks.
- `struct erofs_algorithm`: registry entry with name, backend pointer, on-disk algorithm id, and optimizer flag.
- `struct erofs_compress`: active compressor handle with superblock pointer, selected algorithm, threshold, level, dict size, and private data.

## Important Declarations
- Extern declarations for lz4, lz4hc, lzma, deflate, libdeflate, and libzstd compressors.
- Public internal API for compressor initialization, dispatch, exit, reset, and algorithm id lookup.

## Interactions
- Included by `compress.c`, `fsck/main.c`, and all compressor backend files.

## Notes
The interface supports both `compress_destsize` and whole-buffer `compress`; unaligned extent paths rely on backends that implement `compress`.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_deflate.c -->
# File Research: sources/local-fs/erofs-utils/lib/compressor_deflate.c

## Purpose
Built-in DEFLATE compressor backend using the local `kite_deflate` implementation.

## Important Functions
- `deflate_compress_destsize()`: delegates to `kite_deflate_destsize()`.
- `compressor_deflate_init()` / `compressor_deflate_exit()`: create and destroy kite deflate state.
- `erofs_compressor_deflate_setlevel()`: validates level up to 9, default 1.
- `erofs_compressor_deflate_setdictsize()`: validates dictionary size, fixed max/default 32 KiB.

## Backend Capabilities
- Provides `compress_destsize`.
- Does not provide whole-buffer `compress`.
- On-disk algorithm id is `Z_EROFS_COMPRESSION_DEFLATE` via registry.

## Interactions
- Always added to `liberofs_la_SOURCES` with `kite_deflate.c`.

## Notes
Returns `-EFAULT` if the underlying kite compressor returns a nonpositive compressed size.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_deflate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_libdeflate.c -->
# File Research: sources/local-fs/erofs-utils/lib/compressor_libdeflate.c

## Purpose
Optional DEFLATE compressor backend using libdeflate.

## Main Structure
- `struct erofs_libdeflate_context`: libdeflate compressor, temporary fit-block buffer, buffer size, and last chosen uncompressed size.

## Important Functions
- `libdeflate_compress()`: compresses a full input into a bounded destination; returns `-ENOSPC` when it does not fit.
- `libdeflate_compress_destsize()`: searches for the largest input prefix fitting the destination, using ratio estimation and binary fallback.
- `compressor_libdeflate_init()` / `compressor_libdeflate_exit()`: allocate/free context and libdeflate compressor.
- `compressor_libdeflate_reset()`: clears last-size heuristic.
- `erofs_compressor_libdeflate_setlevel()`: default level 1, max 12.

## Special Behavior
- Ensures the first compressed byte is not zero in some cases so EROFS zero-padding length detection remains valid for DEFLATE streams.

## Interactions
- Registered as optimizer for on-disk DEFLATE when `HAVE_LIBDEFLATE` is enabled.

## Notes
Supports both whole-buffer `compress` and `compress_destsize`, making it usable for unaligned compressed extents.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_libdeflate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_liblzma.c -->
# File Research: sources/local-fs/erofs-utils/lib/compressor_liblzma.c

## Purpose
Optional LZMA compressor backend using liblzma MicroLZMA.

## Main Structure
- `struct erofs_liblzma_context`: LZMA options and stream.

## Important Functions
- `erofs_compressor_liblzma_preinit()`: allocates context and initializes stream.
- `erofs_liblzma_compress_destsize()`: runs `lzma_microlzma_encoder()` and returns consumed input/output size.
- `erofs_compressor_liblzma_exit()`: ends stream and frees context.
- `erofs_compressor_liblzma_setlevel()`: supports normal presets and `>=100` extreme presets, max 109.
- `erofs_compressor_liblzma_setdictsize()`: chooses or validates dictionary size within EROFS LZMA limits.
- `erofs_compressor_liblzma_setextraopts()`: parses `lc=`, `lp=`, and `pb=` options.

## Interactions
- Compiled only under `HAVE_LIBLZMA`.
- Compression config dictionary size is later written by `compress.c`.

## Notes
Provides `compress_destsize` only; no whole-buffer `compress` callback.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_liblzma.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_libzstd.c -->
# File Research: sources/local-fs/erofs-utils/lib/compressor_libzstd.c

## Purpose
Optional Zstandard compressor backend using libzstd.

## Main Structure
- `struct erofs_libzstd_context`: ZSTD compression context and temporary fit-block buffer.

## Important Functions
- `libzstd_compress()`: whole-buffer `ZSTD_compress2()` wrapper.
- `libzstd_compress_destsize()`: searches largest input prefix that fits destination.
- `compressor_libzstd_init()` / `compressor_libzstd_exit()`: allocate/free ZSTD context and temp buffer.
- `erofs_compressor_libzstd_setlevel()`: validates level up to 22.
- `erofs_compressor_libzstd_setdictsize()`: requires power-of-two dictionary/window size within EROFS zstd max.

## Behavior
- Sets `ZSTD_c_compressionLevel` and `ZSTD_c_windowLog`.
- Emits a one-time warning that the libzstd compressor is experimental and fit-block is not upstream-supported.

## Interactions
- Registered under name `zstd` when `HAVE_LIBZSTD` is enabled.
- Supports whole-buffer compression and destination-size fitting.

## Notes
The backend uses window log as the dictionary-size representation used by EROFS config metadata.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_libzstd.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_lz4.c -->
# File Research: sources/local-fs/erofs-utils/lib/compressor_lz4.c

## Purpose
LZ4 compressor backend.

## Important Functions
- `lz4_compress_destsize()`: wraps `LZ4_compress_destSize()`, updating consumed source size.
- `compressor_lz4_init()`: updates `sbi->lz4.max_distance` to at least `LZ4_DISTANCE_MAX`.
- `compressor_lz4_exit()`: no-op success.

## Interactions
- Registered as `lz4` when LZ4 support is enabled.
- LZ4 max distance is written/read as part of EROFS compression configuration.

## Notes
No compression level or private stream is used.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_lz4.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_lz4hc.c -->
# File Research: sources/local-fs/erofs-utils/lib/compressor_lz4hc.c

## Purpose
LZ4HC compressor backend, registered as an optimizer for the LZ4 on-disk algorithm.

## Important Functions
- `lz4hc_compress_destsize()`: wraps `LZ4_compress_HC_destSize()`.
- `compressor_lz4hc_init()` / `compressor_lz4hc_exit()`: allocate/free `LZ4_streamHC`.
- `compressor_lz4hc_setlevel()`: validates level and defaults to `LZ4HC_CLEVEL_DEFAULT`.

## Interactions
- Compiled under `ENABLE_LZ4HC`.
- Shares on-disk algorithm id `Z_EROFS_COMPRESSION_LZ4` through the registry.

## Notes
Like normal LZ4, updates `sbi->lz4.max_distance`.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/compressor_lz4hc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/config.c -->
# File Research: sources/local-fs/erofs-utils/lib/config.c

## Purpose
Global configuration, logging, progress display, SELinux label handle lifecycle, root path trimming, and CPU count helper.

## Main Globals
- `struct erofs_configure cfg`: process-wide configuration.
- `struct erofs_sb_info g_sbi`: global superblock info used by many tools.
- `bool erofs_stdout_tty`: cached stdout TTY status.
- `fullpath_prefix`: prefix length for source-root-relative paths.

## Important Functions
- `erofs_init_configure()` / `erofs_exit_configure()`: initialize defaults and free config strings/SELinux handle.
- `erofs_show_config()`: debug dump.
- `erofs_get_configure()`: returns `&cfg`.
- `erofs_set_fs_root()` / `erofs_fspath()`: configure and compute relative filesystem paths.
- `erofs_selabel_open()`: optional SELinux file contexts setup.
- `erofs_trim_for_progressinfo()`: TTY-width-aware progress path shortening.
- `erofs_msg()`: common logging backend.
- `erofs_update_progressinfo()`: carriage-return progress display when enabled.
- `erofs_get_available_processors()`: returns online processor count when `sysconf` is available.

## Interactions
- Used throughout `liberofs` and tools for global config and logging.
- `global.c` wraps this with library-global init/exit.

## Notes
`erofs_update_progressinfo()` uses `vsprintf()` into an 8192-byte local buffer, assuming callers provide bounded messages.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/config.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/data.c -->
# File Research: sources/local-fs/erofs-utils/lib/data.c

## Purpose
Read-side data and metadata mapping for EROFS inodes, including raw files, inline data, chunk-based files, compressed files, packed fragments, metabox metadata, and variable-sized metadata records.

## Important Functions
- `erofs_bread()`: reads a metadata block into an `erofs_buf`, optionally from metabox inode when no direct vfile is set.
- `erofs_init_metabuf()` / `erofs_read_metabuf()`: initialize/read metadata buffers.
- `__erofs_map_blocks()`: maps non-compressed flat/inline/chunk-based extents.
- `erofs_map_blocks()`: dispatches to compressed zmap for compressed inodes, otherwise raw mapping.
- `erofs_map_dev()`: resolves multi-device physical offsets.
- `erofs_read_one_data()`: reads mapped raw data from the proper device.
- `erofs_read_raw_data()`: reads arbitrary raw inode data, filling holes with zeros and handling inline metabox data.
- `z_erofs_read_one_data()`: reads and decompresses one compressed extent or packed fragment.
- `z_erofs_read_data()`: backward extent iteration for compressed reads over arbitrary ranges.
- `erofs_preadi()` / `erofs_iopen()`: expose an inode as `struct erofs_vfile`.
- `erofs_read_metadata()`: reads length-prefixed metadata either from an inode or block-device metadata area.

## Interactions
- Used by fsck, directory iteration, xattr reading, packed-file handling, and decompression.
- Calls `z_erofs_decompress()` from `decompress.c`.
- Uses packed-file reads from `fragments.c` for fragment-backed data.

## Notes
Inline data crossing a metadata block boundary is treated as corruption.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/data.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/decompress.c -->
# File Research: sources/local-fs/erofs-utils/lib/decompress.c

## Purpose
Userspace decompression dispatcher for EROFS compressed data and parser for on-disk compression configuration records.

## Supported Paths
- Shifted/interlaced uncompressed layouts.
- LZ4 when enabled.
- LZMA when liblzma is enabled.
- DEFLATE through Intel QPL when enabled and suitable, otherwise libdeflate or zlib.
- Zstandard when libzstd is enabled.

## Important Functions
- `z_erofs_fixup_insize()`: skips leading zero padding in padded compressed input.
- `z_erofs_decompress_lz4()`, `z_erofs_decompress_lzma()`, `z_erofs_decompress_deflate()`, `z_erofs_decompress_zstd()`, `z_erofs_decompress_qpl()`: algorithm-specific decode paths.
- `z_erofs_decompress()`: top-level dispatch by `rq->alg`.
- `z_erofs_load_lz4_config()`: loads LZ4 max distance and max pcluster blocks.
- `z_erofs_load_deflate_config()`: under QPL, decides whether QPL can handle the DEFLATE history window.
- `z_erofs_parse_cfgs()`: parses superblock compression algorithm bitmask and per-algorithm config metadata.

## Interactions
- Called by `data.c` and fsck data verification.
- Reads variable-sized compression configs via `erofs_read_metadata()`.
- Uses `erofs_get_available_processors()` for QPL job cache sizing.

## Notes
Many decoders allocate a temporary full output buffer when `decodedskip` is nonzero. Partial decoding behavior varies by backend.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/dedupe.c -->
# File Research: sources/local-fs/erofs-utils/lib/dedupe.c

## Purpose
Rolling-hash based deduplication for uncompressed source windows during compression.

## Main Structures
- `struct z_erofs_dedupe_item`: stored dedupe candidate with rolling hash, xxhash, SHA-256 prefix, pstart/plen, original length, flags, and extra data.
- `dedupe_tree[65536]`: hash buckets.
- `dedupe_subtree`: per-file/transaction insertion chain for commit or rollback.

## Important Functions
- `erofs_memcmp2()`: optimized byte comparison returning matching prefix length.
- `z_erofs_dedupe_match()`: searches backwards over the current queue for the best matching stored window.
- `z_erofs_dedupe_insert()`: inserts an extent's original data as a future dedupe candidate.
- `z_erofs_dedupe_commit()`: either keeps or drops current transaction's inserted candidates.
- `z_erofs_dedupe_init()` / `z_erofs_dedupe_exit()`: initialize buckets/window hash constants and free state.

## Interactions
- Called from `compress.c` to replace repeated data with references to earlier compressed/raw extents.
- Uses rolling hash, xxhash, and SHA-256 to avoid expensive full comparisons unless likely matched.

## Notes
The dedupe window must be initialized nonzero; otherwise match/insert are effectively disabled.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/dedupe.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/dedupe_ext.c -->
# File Research: sources/local-fs/erofs-utils/lib/dedupe_ext.c

## Purpose
Deduplicates already encoded extents by comparing compressed/raw output bytes against data already written to the image.

## Main Structures
- `struct z_erofs_dedupe_ext_item`: extent record plus xxhash and revoke-chain link.
- `dupl_ext[65536]`: hash buckets for encoded extents.
- `revoke_list`: transaction list for rollback.

## Important Functions
- `z_erofs_dedupe_ext_insert()`: records an encoded extent under a supplied hash.
- `z_erofs_dedupe_ext_match()`: hashes candidate bytes, reads possible matches from device, compares bytes, and returns matching physical offset or 0.
- `z_erofs_dedupe_ext_commit()`: drops transaction entries on rollback.
- `z_erofs_dedupe_ext_init()` / `z_erofs_dedupe_ext_exit()`: initialize and free state.

## Interactions
- Used by multithreaded compression merge logic in `compress.c`, especially with fragments enabled.
- Reads image data with `erofs_dev_read()` to confirm hash matches.

## Notes
`z_erofs_dedupe_ext_exit()` calls `z_erofs_dedupe_commit(true)`, which appears to target the regular dedupe transaction rather than the ext revoke list; the subsequent bucket cleanup still frees ext items.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/dedupe_ext.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/dir.c -->
# File Research: sources/local-fs/erofs-utils/lib/dir.c

## Purpose
Directory entry iteration, fsck validation, and nid-to-pathname lookup.

## Important Functions
- `erofs_validate_filename()`: rejects names containing `/`.
- `traverse_dirents()`: parses one directory block's dirents, validates name offsets/lengths/order/file types/special entries when fsck mode is enabled, and invokes callback.
- `erofs_iterate_dir()`: opens a directory inode as a vfile and iterates block by block.
- `erofs_get_pathname_iter()`: recursive callback to find a target nid.
- `erofs_get_pathname()`: returns `/` for root or recursively searches from root for a nid.

## Fsck Checks
- Dirent `nameoff` must be sane.
- Names must be nonempty, bounded by `EROFS_NAME_LEN`, and within block.
- In fsck mode names must be sorted.
- `.` and `..` entries must not be duplicated and must point to expected nids.
- Directory filenames may not contain `/`.

## Interactions
- Used heavily by `fsck/main.c`.
- Uses `erofs_iopen()` and `erofs_pread()` from `data.c`.

## Notes
Path lookup recursively descends entries typed as directory or unknown, then verifies inode mode when necessary.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/diskbuf.c -->
# File Research: sources/local-fs/erofs-utils/lib/diskbuf.c

## Purpose
Temporary disk-backed buffer streams used to avoid creating too many temp files and to support large intermediate data.

## Main Structure
- `struct erofs_diskbufstrm`: stream fd, tail offset, device position, atomic reference count, alignment size, and simple lock flag.

## Important Functions
- `erofs_diskbuf_getfd()`: returns stream fd and absolute file position.
- `erofs_diskbuf_reserve()`: reserves current tail offset in a stream and increments refcount.
- `erofs_diskbuf_commit()`: advances stream tail by committed length.
- `erofs_diskbuf_close()`: releases a disk buffer reservation.
- `erofs_tmpfile()`: creates an unlinked temp file in `$TMPDIR` or `/tmp` with mode respecting umask.
- `erofs_diskbuf_init()`: initializes N streams, optionally using a duplicated image fd for stream 0 if it can be grown.
- `erofs_diskbuf_exit()`: validates refcounts, closes fds, and frees streams.

## Interactions
- Used by blob/fragments/importer-style staging paths.
- Uses global `g_sbi.bdev` for stream-0 optimization.

## Notes
The `locked` field has a TODO noting it is not a real multithreaded lock.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/diskbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/exclude.c -->
# File Research: sources/local-fs/erofs-utils/lib/exclude.c

## Purpose
Maintains exact-path and regex-based exclude rules for mkfs/import source traversal.

## Main Data
- `exclude_head`: exact path rules.
- `regex_exclude_head`: compiled regex rules.

## Important Functions
- `erofs_parse_exclude_path()`: inserts an exact or regex exclude rule.
- `erofs_is_exclude_path()`: builds `dir/name`, converts to fs-relative path, and checks exact then regex rules.
- `erofs_cleanup_exclude_rules()`: frees patterns and regex resources.

## Behavior
- Regex rules compile with `REG_EXTENDED | REG_NOSUB`.
- Invalid regex errors are logged with `regerror()`.
- On insertion failure, all existing exclude rules are cleaned up.

## Interactions
- Uses `erofs_fspath()` from `config.c` for root-relative matching.

## Notes
`erofs_is_exclude_path()` uses a fixed `PATH_MAX` stack buffer for `dir/name`.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/exclude.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/fragments.c -->
# File Research: sources/local-fs/erofs-utils/lib/fragments.c

## Purpose
Implements EROFS packed-fragment support: tail-fragment dedupe, fragment packing, packed inode temp storage, packed inode flushing, lazy packed-file reading, and cache management.

## Main Structures
- `struct erofs_fragmentitem`: fragment data, length, and packed-file position.
- `struct erofs_fragment_bucket`: hash list plus rwsem.
- `struct erofs_packed_inode`: temp fd, hash buckets for mkfs, lazy-read bitmap, mutex, and bitmap size.

## Important Functions
- `z_erofs_fragments_tofh()`: computes tail hash from the last 64 bytes.
- `erofs_fragment_findmatch()`: searches fragment buckets for matching tail data and records matched fragment size/item.
- `erofs_fragment_pack()`: records a fragment in memory or as a reference to packed temp-file position.
- `erofs_pack_file_from_fd()`: appends an entire file to the packed temp inode, using mmap or sendfile/read fallback.
- `erofs_fragment_commit()`: writes in-memory fragment data to packed temp file and finalizes `inode->fragmentoff`.
- `erofs_flush_packed_inode()`: converts accumulated packed data into the special packed inode.
- `erofs_packedfile_init()` / `erofs_packedfile_exit()`: allocate/free packed inode state.
- `erofs_packedfile_read()`: reads from packed inode, using temp-file cache when initialized and falling back to on-disk packed inode reads.
- `erofs_packedfile_preload()`: lazily loads packed inode blocks into the temp fd and marks `uptodate` bits.

## Interactions
- Compression uses this for fragment tail packing and dedupe.
- Fsck initializes packed-file state to verify packed fragments.
- `data.c` calls `erofs_packedfile_read()` for fragment-backed compressed extents.

## Notes
The packed-file read path supports incremental/lazy loading of existing packed inodes and handles ENOSPC by clearing cache state and falling back.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/fragments.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/global.c -->
# File Research: sources/local-fs/erofs-utils/lib/global.c

## Purpose
Library-global initialization and cleanup wrapper for configuration, curl, XML parser, and compression workqueue state.

## Important Functions
- `liberofs_global_init()`: locks a global mutex, initializes `cfg`, optionally initializes libxml parser for S3, and initializes curl once.
- `liberofs_global_exit()`: locks, exits MT compression workqueue, cleans curl/libxml state, exits config, and unlocks.

## Interactions
- Calls `erofs_init_configure()` / `erofs_exit_configure()`.
- Calls `z_erofs_mt_global_exit()` to tear down compression workqueue state.
- Conditional on `HAVE_LIBCURL` and `S3EROFS_ENABLED`.

## Notes
Curl initialization is protected by a static boolean and mutex.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/global.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/gzran.c -->
# File Research: sources/local-fs/erofs-utils/lib/gzran.c

## Purpose
Builds and consumes gzip random-access indexes compatible with AWS SOCI zinfo format, enabling random reads from gzip/zlib streams.

## Main Structures
- `struct erofs_gzran_cutpoint`: 32 KiB window, uncompressed output position, and input bit position.
- `struct erofs_gzran_builder`: streaming inflate state, source buffer, output window, cutpoint list, counters, and span size.
- `struct erofs_gzran_iostream`: vfile wrapper that reads compressed input using zinfo cutpoints.

## Builder Functions
- `erofs_gzran_builder_init()`: initializes zlib inflate with automatic zlib/gzip decoding.
- `erofs_gzran_builder_read()`: inflates up to a 32 KiB window, records cutpoints at block boundaries and span intervals, and supports concatenated gzip streams.
- `erofs_gzran_builder_export_zinfo()`: writes SOCI-compatible zinfo v2 header and checkpoints.
- `erofs_gzran_builder_final()`: ends inflate and frees cutpoints.

## Reader Functions
- `erofs_gzran_zinfo_open()`: parses zinfo v1/v2 buffers and returns an `erofs_vfile`.
- `erofs_gzran_ios_vfpread()`: selects a cutpoint, primes raw inflate if needed, sets dictionary window, skips to requested offset, and fills caller buffer.
- `erofs_gzran_ios_vfclose()`: frees zinfo state.

## Interactions
- Uses `erofs_vfile` operations and zlib.
- Compiled with functional support only under `HAVE_ZLIB`; otherwise stubs return `-EOPNOTSUPP` or no-op success.

## Notes
The reader creates a virtual uncompressed stream over a compressed input plus zinfo checkpoints.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/gzran.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/hashmap.c -->
# File Research: sources/local-fs/erofs-utils/lib/hashmap.c

## Purpose
Generic chained hashmap implementation copied from Git, plus hash helpers and a memory interning pool.

## Hash Helpers
- `strhash()`: FNV-1 32-bit hash over NUL-terminated string.
- `strihash()`: case-insensitive ASCII variant.
- `memhash()`: FNV-1 over arbitrary bytes.
- `memihash()`: case-insensitive ASCII byte variant.

## Hashmap Functions
- `hashmap_init()`: allocates table sized to requested initial size and load factor.
- `hashmap_free()`: frees table only if map is empty, otherwise returns `-EBUSY`.
- `hashmap_get()` / `hashmap_get_next()`: lookup first/next equal entry.
- `hashmap_add()`: inserts and grows table past load threshold.
- `hashmap_remove()`: removes an entry and shrinks table below threshold.
- `hashmap_iter_init()` / `hashmap_iter_next()`: table iteration.

## Interning
- `memintern()`: stores immutable byte strings in a static hashmap and returns a stable interned pointer.

## Interactions
- Used by blob chunk dedupe and other map-based helpers.
- Requires caller entries to embed `struct hashmap_entry`.

## Notes
The table grows/shrinks by a factor of 4 and defaults to an equality callback that treats same-hash entries as equal.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/hashmap.c -->