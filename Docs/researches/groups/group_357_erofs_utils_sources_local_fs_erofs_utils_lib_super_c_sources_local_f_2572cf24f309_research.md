# Group Research: group_357_erofs_utils_sources_local_fs_erofs_utils_lib_super_c_sources_local_f_2572cf24f309

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/local-fs/erofs-utils` library and mkfs files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/super.c -->
# File Research: sources/local-fs/erofs-utils/lib/super.c

## Scope

This file implements EROFS superblock read, validation, teardown, mkfs reservation/writing, checksum handling, device-table handling, and clean/incremental mkfs filesystem initialization.

## Public And Internal APIs Covered

- Read-side lifecycle: `erofs_read_superblock()` and `erofs_put_super()`.
- Write-side lifecycle: `erofs_reserve_sb()`, `erofs_writesb()`, `erofs_mkfs_format_fs()`, and `erofs_mkfs_load_fs()`.
- Checksum helpers: `erofs_enable_sb_chksum()` and `erofs_superblock_csum_verify()`.
- Device table helpers: `erofs_mkfs_init_devices()` and `erofs_write_device_table()`.
- Internal validation/setup: `check_layout_compatibility()` and `erofs_init_devices()`.

## Control Flow And Behavior

- `erofs_read_superblock()` reads the first maximum block, verifies magic, block size, incompatible feature bits, extended superblock size, root nid encoding, optional metabox nid, inode count, checksum fields, timestamps, UUID, shared-xattr prefix constraints, compression config, device table, and xattr prefixes before setting `sbi->sb_valid`.
- Feature compatibility is fail-closed: unknown incompatible bits are rejected against `EROFS_ALL_FEATURE_INCOMPAT`.
- Device-table reads compare user-provided extra-device count with on-disk count when both exist, allocate `sbi->devs`, copy tags and block counts, compute `device_id_mask`, and accumulate `total_blocks`.
- `erofs_put_super()` frees extra-device paths, tears down the buffer manager, compression state, and xattr state, then clears `sb_valid`.
- `erofs_writesb()` materializes an on-disk `struct erofs_super_block`, including 48-bit block/root fields when needed, optional compression config, optional metabox nid, extra device metadata, UUID, volume name, and feature flags. It writes the superblock at the reserved buffer offset or device start.
- `erofs_reserve_sb()` pins the superblock as the first allocation by ballooning a metadata buffer to cover `EROFS_SUPER_OFFSET + sb_size` and asserting that `erofs_btell()` is zero.
- Superblock checksums are enabled by rereading the superblock area, setting the compat checksum feature, computing CRC32C with the checksum field included as zero before final assignment, and rewriting the same bytes.
- Clean mkfs initializes a new buffer manager and reserves the superblock. Incremental mkfs reads an existing superblock, estimates append start from image file size or current block count, then initializes the buffer manager from that start block.

## State And Data Structures

- Populates `erofs_sb_info` fields for feature flags, block size, superblock size, block counts, metadata and xattr block addresses, root and packed nids, metabox nid, inode count, timestamps, checksum, UUID, device table, and xattr prefixes.
- Uses `erofs_buffer_head` handles for reserved superblock and device-table regions.
- Device slots use on-disk `struct erofs_deviceslot` with low 32-bit block fields and fixed-size tags.

## Dependencies

- Depends on block/device I/O helpers, buffer-manager allocation and mapping, CRC32C, compression config parsing, compression teardown, metabox feature helpers, and xattr prefix initialization/cleanup.
- Shares feature-bit contracts with on-disk EROFS format definitions in public/internal headers.

## Risks And Invariants

- Unknown incompatible features, invalid block sizes, invalid extended superblock size, invalid metabox self-loop, and invalid shared-xattr prefix ids are corruption or compatibility boundaries.
- Device table count, slot offset, and block accumulation must match mkfs and mount/read behavior; mismatches are rejected.
- The superblock must stay pinned at image offset zero for mkfs output correctness.
- Checksum computation intentionally skips the first 1024 bytes when block size permits, preserving space for boot-sector oddities.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/tar.c -->
# File Research: sources/local-fs/erofs-utils/lib/tar.c

## Scope

This file implements tar-like stream input for EROFS image generation: buffered stream/decompression wrappers, tar numeric and PAX parsing, tar/PAX xattr collection, overlay handling, file data staging, and one-record-at-a-time tree import.

## Public And Internal APIs Covered

- Stream lifecycle and reads: `erofs_iostream_open()`, `erofs_iostream_close()`, `erofs_iostream_read()`, `erofs_iostream_bread()`, and `erofs_iostream_lskip()`.
- PAX/xattr helpers: `tarerofs_insert_xattr()`, `tarerofs_merge_xattrs()`, `tarerofs_remove_xattrs()`, `tarerofs_apply_xattrs()`, and `tarerofs_parse_pax_header()`.
- Tar tree import: `tarerofs_parse_tar()`.
- Inode removal/staging helpers: `tarerofs_remove_inode()`, `tarerofs_write_uncompressed_file()`, and `tarerofs_write_file_data()`.
- Internal parsers include octal/base-256 numeric parsing and percent-decoding for libarchive xattr names.

## Control Flow And Behavior

- `erofs_iostream_open()` configures the stream for plain fd, gzip, liblzma, gzip-random-access builder, or tar dump mode; plain files are size-detected with `lseek()` and advised sequentially when available.
- `erofs_iostream_read()` maintains a head/tail buffer, compacts unread bytes, fills from the selected decoder, optionally dumps raw bytes, marks EOF, and returns an in-buffer slice rather than always copying.
- `erofs_iostream_lskip()` skips buffered bytes first, uses `lseek()` for seekable plain streams when no dump is active, and otherwise drains through the decoder.
- `tarerofs_parse_pax_header()` consumes PAX records of the form `LEN NAME=VALUE\n`, updating path, linkpath, size, uid/gid, mtime/nsec, and xattrs. It supports SCHILY xattrs as raw values and LIBARCHIVE xattrs as URL-decoded names with base64-decoded values.
- `tarerofs_parse_tar()` aligns to 512-byte records, reads a tar header, validates checksum with unsigned and signed checksum variants, handles two zero blocks as end-of-archive, rejects invalid magic, and interprets POSIX/GNU type flags.
- GNU volume headers set the EROFS volume name. Global and per-file PAX headers update persistent or current extended header state. GNU long path and long link records populate current path/link overrides.
- Normal tar entries are resolved through `erofs_rebuild_get_dentry()`, including AUFS/overlayfs whiteout and opaque-directory handling. Existing non-directory entries are removed/replaced; existing directories can be reused.
- Hardlinks reuse the target inode, increment link count, and replace an existing destination inode if necessary. Directory hardlinks are rejected.
- Symlink content is copied from the link path. Device nodes encode major/minor into EROFS device format. Regular-file payloads can be zero-filled, stored as tar index chunks, reserved-space references, blob chunks, written uncompressed directly in no-reorder mode, or staged into a disk buffer for later compression/import.
- Local PAX xattrs are merged with global xattrs, then applied with `erofs_vfs_setxattr()`.

## State And Data Structures

- `struct erofs_iostream` tracks decoder type, handler, buffer, head/tail cursors, logical stream size, EOF state, dump fd, and optional gzip-random-access builder.
- `struct erofs_pax_header` carries current/global tar overrides and xattr list.
- `struct tarerofs_xattr_item` stores `name\0value` buffers with explicit name and total lengths.
- `struct erofs_tarfile` controls modes such as AUFS compatibility, index/header-only operation, reserved-space import, no-reorder direct writing, dump file, and source-device id.

## Dependencies

- Optional zlib, liblzma, and gzran support.
- EROFS importer, inode, rebuild, xattr, disk-buffer, blob-chunk, base64, and cache helpers.
- POSIX file APIs for `read`, `lseek`, `pwrite`, `open`, and descriptor lifecycle.

## Risks And Invariants

- Tar offset accounting must stay 512-byte aligned even when payload data is skipped, indexed, or staged.
- PAX parsing treats malformed lengths, missing separators, missing trailing newlines, invalid numeric overrides, and bad base64 as hard errors.
- Stream read sizes are bounded by the current buffer and `INT_MAX`; callers must handle short reads.
- `tarerofs_insert_xattr()` deduplicates by xattr name and either skips existing entries or replaces values depending on caller intent.
- AUFS/overlay conversion mutates inode type and parent directory metadata; incorrect handling would expose whiteouts as ordinary device nodes.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/tar.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/uuid.c -->
# File Research: sources/local-fs/erofs-utils/lib/uuid.c

## Scope

This file provides UUID generation and parsing for erofs-utils, using libuuid when available and local fallback logic otherwise.

## Public And Internal APIs Covered

- `erofs_uuid_generate()` fills a 16-byte UUID buffer.
- `erofs_uuid_parse()` parses canonical hyphenated UUID strings into 16 bytes.
- Fallback-only `s_getrandom()` wraps `getrandom()` or the Linux syscall and optionally falls back to `rand()` for insecure generation when the syscall is unavailable.

## Control Flow And Behavior

- With libuuid, generation loops until `uuid_generate()` returns a non-null UUID and parsing delegates to `uuid_parse()`.
- Without libuuid, generation requests random bytes with insecure mode enabled, asserts success, and sets version/variant bits before copying to the caller buffer.
- `s_getrandom()` retries interrupted calls, detects unsupported `GRND_INSECURE` through `EINVAL` and disables the flag for retry, and falls back to `rand()` only for insecure generation when `getrandom` is unavailable.
- Fallback parsing reads exactly 16 two-hex-digit bytes and requires hyphens after the conventional 4th, 6th, 8th, and 10th bytes, with no trailing characters.

## State And Data Structures

- Maintains process-global `erofs_grnd_flag`, initialized to `GRND_INSECURE` or its numeric value, and downgraded to zero if the kernel rejects it.

## Dependencies

- Optional libuuid; otherwise libc, `getrandom()` or Linux `syscall(__NR_getrandom)`, and EROFS definitions/macros.

## Risks And Invariants

- Fallback generation depends on `BUG_ON(res != 0)`, so entropy/syscall failure is fatal outside the explicit insecure fallback path.
- The fallback version/variant bit placement uses local byte indexing; compatibility depends on matching the project’s UUID byte-order conventions.
- Parser rejects malformed hex/hyphen layout strictly and returns `-EINVAL` for local fallback failures.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/uuid_unparse.c -->
# File Research: sources/local-fs/erofs-utils/lib/uuid_unparse.c

## Scope

This small file formats a 16-byte UUID into lowercase canonical text.

## Public And Internal APIs Covered

- `erofs_uuid_unparse_lower()` writes a 36-character hyphenated UUID string plus trailing NUL into the caller-provided output buffer.

## Control Flow And Behavior

- Uses `sprintf()` with eight 16-bit groups assembled from adjacent bytes and hyphens in the `8-4-4-4-12` UUID layout.

## Dependencies

- Standard `stdio.h`, EROFS config, and UUID helper declarations.

## Risks And Invariants

- The caller must provide enough storage for 37 bytes.
- Byte grouping must match `erofs_uuid_parse()` and superblock UUID display expectations.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/uuid_unparse.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/vmdk.c -->
# File Research: sources/local-fs/erofs-utils/lib/vmdk.c

## Scope

This file emits a VMware VMDK descriptor that describes the primary EROFS image and any extra devices as flat extents.

## Public And Internal APIs Covered

- `erofs_dump_vmdk_desc()` writes the full descriptor to a `FILE *`.
- Internal `erofs_vmdk_desc_add_extent()` writes one or more extent lines for a flat image, splitting large sector counts.

## Control Flow And Behavior

- The descriptor CID is derived by XORing four 32-bit words of the filesystem UUID; parent CID is fixed to `0xffffffff`.
- Primary-device block count and extra-device block counts are converted to 512-byte sectors using `blkszbits - 9`.
- Extent lines use `twoGbMaxExtentFlat` and `FLAT` extents. Each line is capped at `0x80000000 >> 9` sectors by the helper loop.
- Extra-device extent filenames prefer `src_path`; otherwise the device tag is used.
- The disk database reports hardware version `4`, IDE adapter type, 16 heads, 63 sectors, and cylinders rounded up from total sectors.

## State And Data Structures

- Reads `erofs_sb_info` UUID, device name, block size, primary-device block count, extra-device array, tags, paths, and block counts.

## Dependencies

- Standard formatted I/O and EROFS internal type/helpers such as `min_t()` and `DIV_ROUND_UP()`.

## Risks And Invariants

- This file assumes block size is at least 512 bytes so `blkszbits - 9` is valid.
- `fprintf()` failures from descriptor templates are not checked, while extent-line failures are converted to `-errno`.
- Device tags used as filenames must be meaningful and NUL-terminated enough for descriptor consumers.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/vmdk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/workqueue.c -->
# File Research: sources/local-fs/erofs-utils/lib/workqueue.c

## Scope

This file implements a simple bounded pthread workqueue used by multi-threaded erofs-utils paths.

## Public And Internal APIs Covered

- `erofs_alloc_workqueue()` initializes and starts worker threads.
- `erofs_queue_work()` enqueues one `struct erofs_work`.
- `erofs_destroy_workqueue()` shuts down workers and destroys queue resources.
- Internal `worker_thread()` drains queued work and invokes optional per-thread start/exit hooks.

## Control Flow And Behavior

- Workers call `on_start`, then loop waiting on `cond_empty` while there are no jobs and shutdown is false.
- A worker exits only when the queue is empty and shutdown is true, allowing queued work to drain after destruction starts.
- Jobs are popped FIFO from `head`, `tail` is cleared when the queue becomes empty, and `cond_full` is broadcast when the queue drops from full to not-full.
- `erofs_queue_work()` blocks while `job_count == max_jobs`, appends to the tail, increments count, signals `cond_empty`, and returns.
- `erofs_destroy_workqueue()` marks shutdown, wakes empty-waiting workers, joins all created workers in reverse order, frees the worker array, and destroys synchronization primitives.

## State And Data Structures

- `struct erofs_workqueue` owns head/tail pointers, worker array/count, max job count, current job count, shutdown flag, mutex, two condition variables, and optional hooks.
- `struct erofs_work` must provide a `next` pointer and callback.

## Dependencies

- POSIX pthreads and standard allocation.

## Risks And Invariants

- `erofs_queue_work()` does not reject enqueue after shutdown, so callers must not race queueing with destruction.
- If thread creation fails, `erofs_alloc_workqueue()` sets `nworker` to the number actually started and calls destroy to join them.
- `erofs_destroy_workqueue()` may return early on `pthread_join()` failure, leaving some cleanup incomplete.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/workqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/xattr.c -->
# File Research: sources/local-fs/erofs-utils/lib/xattr.c

## Scope

This file implements EROFS extended attribute import, interning, shared-xattr selection and emission, inline-xattr export, read-side `getxattr`/`listxattr`, long xattr prefixes, overlayfs helper xattrs, SELinux relabel integration, Android capabilities, and xattr-manager cleanup.

## Public And Internal APIs Covered

- Manager lifecycle: `erofs_xattr_init()` and `erofs_xattr_exit()`.
- Source scanning/import: `erofs_scan_file_xattrs()`, `erofs_read_xattrs_from_disk()`, and `erofs_load_shared_xattrs_from_path()`.
- Set/remove helpers: `erofs_setxattr()`, `erofs_vfs_setxattr()`, `erofs_set_opaque_xattr()`, `erofs_clear_opaque_xattr()`, and `erofs_set_origin_xattr()`.
- Layout preparation/export: `erofs_prepare_xattr_ibody()`, `erofs_xattr_flush_name_prefixes()`, and `erofs_export_xattr_ibody()`.
- Read-side queries: `erofs_getxattr()` and `erofs_listxattr()`.
- Prefix APIs: `erofs_xattr_prefix_matches()`, `erofs_xattr_insert_name_prefix()`, `erofs_xattr_set_ishare_prefix()`, `erofs_xattr_cleanup_name_prefixes()`, `erofs_xattr_prefixes_init()`, and `erofs_xattr_prefixes_cleanup()`.

## Control Flow And Behavior

- Platform wrappers abstract Linux `llistxattr`/`lgetxattr`/`lsetxattr` and macOS `listxattr`/`getxattr`/`setxattr` no-follow variants, normalizing some missing-xattr errors.
- Xattr key/value buffers are stored as `key\0value`. `get_xattritem()` hashes key and value separately, interns duplicates in a large hash table, reference-counts users, detects short predefined prefixes, and upgrades to configured long prefixes when they match.
- File scanning lists all source xattr names, skips labels that will be overridden by SELinux relabeling, ignores inaccessible xattrs, interns readable xattrs, appends inode references, and optionally adds a generated SELinux label.
- `erofs_setxattr()` constructs a key from a short or long-prefix index plus a caller name, interns the key/value, and attaches it to the inode. VFS-style setting uses hidden/raw prefix index zero.
- Overlay helper functions add/remove `trusted.overlay.opaque` and add a zero-length `trusted.overlay.origin`; disk re-read also maps these xattrs into inode `opaque` and `whiteouts` flags.
- Android capability support emits `security.capability` from `inode->capabilities` when built with Android support.
- Shared-xattr loading recursively scans a directory tree to count all xattr occurrences, promotes entries above `inlinexattr_tolerance`, sorts shared entries for deterministic layout, writes them into an XATTR allocation, assigns shared ids, and records `sbi->xattr_blkaddr`.
- Inline xattr preparation computes `inode->xattr_isize`, replacing shareable entries with shared-id array slots up to `UCHAR_MAX`; optional `noroom` enforces an existing target size.
- Long name prefixes can be flushed in plain metadata, metabox metadata, or packed-file/fragments area depending on feature configuration. The superblock records prefix start/count and relevant feature bits.
- `erofs_export_xattr_ibody()` emits the ibody header, optional xattr name bloom-style filter, shared-id array, and inline xattr entries, while dropping inode references and item references as it consumes them.
- Read-side initialization parses an inode’s xattr ibody header and shared-id array lazily. `erofs_getxattr()` and `erofs_listxattr()` iterate inline entries first, then shared entries, handling long-prefix infixes and entries crossing block boundaries.
- `erofs_xattr_prefixes_init()` reads long-prefix records from plain metadata, packed inode, or metabox metadata, depending on feature flags and nids.

## State And Data Structures

- `struct erofs_xattrmgr` owns the intern hash table and linked list of selected shared xattrs.
- `struct erofs_xattritem` carries key/value pointer, key/value lengths, hashes, refcount, shared id, short base index, selected prefix index, and prefix length.
- `struct erofs_inode_xattr_node` links interned items into an inode’s xattr list.
- Global `ea_name_prefixes` and `ea_prefix_count` store mkfs-configured long prefixes.
- Read-side `struct erofs_xattr_iter` carries metadata-buffer cursor state, output buffer state, and lookup key state.

## Dependencies

- EROFS list, xattr format, importer parameters, cache/metabox/fragments, private config, and xxhash helpers.
- Optional Linux/macOS xattr syscalls, optional libselinux, optional Android capability definitions.

## Risks And Invariants

- Key/value length arithmetic includes the trailing key NUL; miscomputing `EROFS_XATTR_KSIZE` or prefix lengths corrupts on-disk xattr entries.
- Shared xattr ids are expressed in 4-byte units relative to `xattr_blkaddr`; offset overflow is guarded when flushing prefixes but shared xattr size still depends on buffer allocation and block placement.
- Long-prefix indexes are limited to 0x80 entries and names to `UINT8_MAX`; invalid on-disk indexes are ignored or return no data.
- Read-side iterators validate entry sizes against remaining ibody bytes and return `-EFSCORRUPTED` for overrun.
- `erofs_export_xattr_ibody()` consumes and frees the inode xattr list, so callers must treat export as a destructive flush step.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/xxhash.c -->
# File Research: sources/local-fs/erofs-utils/lib/xxhash.c

## Scope

This file provides local xxHash32 and xxHash64 implementations copied/adapted from the Linux kernel and original xxHash project, used by erofs-utils for fast non-cryptographic hashing.

## Public And Internal APIs Covered

- `xxh32()` computes a 32-bit xxHash over a byte buffer with a caller seed.
- `xxh64()` computes a 64-bit xxHash over a byte buffer with a caller seed.
- Internal helpers implement 32-bit and 64-bit rounds, rotate operations, and 64-bit merge rounds.

## Control Flow And Behavior

- `xxh32()` processes 16-byte stripes into four accumulators when enough input is present, handles remaining 4-byte and 1-byte tails, mixes length, and applies the avalanche finalization.
- `xxh64()` processes 32-byte stripes into four 64-bit accumulators, merges them, handles 8-byte, 4-byte, and 1-byte tails, mixes length, and applies the 64-bit avalanche finalization.
- Both functions use unaligned little-endian loads from EROFS helper macros.

## State And Data Structures

- Defines xxHash prime constants as file-static 32-bit and 64-bit constants.

## Dependencies

- Depends on `erofs/defs.h` for fixed-width types and unaligned little-endian load helpers.

## Risks And Invariants

- This is non-cryptographic hashing; callers must not use it for authenticity or collision-resistant identity.
- Correctness depends on little-endian unaligned load helpers matching the xxHash reference byte order.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/xxhash.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/zmap.c -->
# File Research: sources/local-fs/erofs-utils/lib/zmap.c

## Scope

This file maps compressed EROFS file logical offsets to physical compressed extents. It supports full indexes, compact indexes, newer extent records, big pclusters, fragments, tail packing, metabox-backed metadata, partial references, and FIEMAP-style full logical length discovery.

## Public And Internal APIs Covered

- Public iterator: `z_erofs_map_blocks_iter()`.
- Lazy inode initialization: `z_erofs_fill_inode_lazy()`.
- Full/compact index loaders: `z_erofs_load_full_lcluster()`, `z_erofs_load_compact_lcluster()`, and `z_erofs_load_lcluster_from_disk()`.
- Extent resolution helpers: `z_erofs_extent_lookback()`, `z_erofs_get_extent_compressedlen()`, `z_erofs_get_extent_decompressedlen()`, `z_erofs_map_blocks_fo()`, and `z_erofs_map_blocks_ext()`.
- Compact-bit helpers: `decode_compactedbits()` and `get_compacted_la_distance()`.

## Control Flow And Behavior

- Full indexes read one `z_erofs_lcluster_index` per logical cluster, recording type, cluster offset, pblk, partial-ref flag, nonhead deltas, and optional compressed-block count.
- Compact indexes compute the packed index region from the inode location, xattr size, cluster bits, initial 4-byte records, optional 2-byte records, and amortized pack size. They decode per-lcluster type/low bits, reconstruct nonhead deltas, derive pblk from the trailing base pblk plus preceding cluster count, and validate big-pcluster markers.
- `z_erofs_extent_lookback()` walks backward from a nonhead lcluster by delta until it finds the corresponding head lcluster and sets the map logical address to the head offset.
- `z_erofs_get_extent_compressedlen()` determines physical compressed length from head type and big-pcluster feature bits, defaulting to one block where allowed or reading the following CBLKCNT marker.
- `z_erofs_get_extent_decompressedlen()` advances through lclusters until EOF or next head to compute full decompressed extent length for FIEMAP-style queries.
- `z_erofs_map_blocks_fo()` handles full/compact-index mapping. It special-cases all-fragment files, maps logical offsets to head or nonhead extents, supports tail-packed inline compressed data, fragment pclusters, physical address calculation, compression algorithm selection, partial-ref flags, and optional full logical mapping.
- `z_erofs_map_blocks_ext()` handles extent-record layout. Depending on record size, it uses implicit sequential physical addresses, fixed lcluster records, or binary search over explicit logical starts. It detects final fragment extents and decodes plen flags into mapped/full/encoded/partial-ref flags and algorithm format.
- `z_erofs_fill_inode_lazy()` reads the compressed map header once per inode, handles the special packed-inode whole-file fragment marker, initializes z-advise flags, lcluster bits, algorithm ids, extent count, fragment offset, inline pcluster size, and tail extent metadata.
- `z_erofs_map_blocks_iter()` returns an unmapped post-EOF extent when `m_la >= i_size`; otherwise it initializes compressed metadata, dispatches to extent or full/compact mapping, and rejects encoded pclusters above maximum physical or decompressed sizes.

## State And Data Structures

- `struct z_erofs_maprecorder` carries current inode, output map, lcn, type/head type, cluster offset, deltas, pblk, compressed block count, next packed offset, and partial-ref flag.
- Populates `struct erofs_map_blocks` fields including `m_la`, `m_pa`, `m_llen`, `m_plen`, `m_flags`, `m_algorithmformat`, and metadata buffer cursor.
- Updates compressed inode fields such as `z_advise`, `z_lclusterbits`, `z_algorithmtype`, `z_idata_size`, `z_fragmentoff`, `fragmentoff`, `z_extents`, and `z_tailextent_headlcn`.

## Dependencies

- Depends on EROFS internal compressed-format macros, metadata buffer reads, inode location helpers, metabox detection, endian conversion, and map flag definitions.

## Risks And Invariants

- Compact index decoding is highly format-sensitive: pack alignment, lcluster bit limits, D0/D1 deltas, and big-pcluster flags must match mkfs output exactly.
- Corruption checks reject unknown lcluster types, invalid cluster offsets, impossible lookback distances, missing CBLKCNT markers, inconsistent algorithm availability, and oversized pclusters.
- Tail-packing and fragment handling mutate inode tail fields during `FINDTAIL`; callers rely on lazy initialization being idempotent.
- Extent binary search assumes sorted extent logical starts and validates that discovered right boundary does not exceed current logical end.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/zmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/mkfs/Makefile.am -->
# File Research: sources/local-fs/erofs-utils/mkfs/Makefile.am

## Scope

This Automake fragment defines the `mkfs.erofs` build target.

## Build Rules Covered

- Sets `AUTOMAKE_OPTIONS = foreign`.
- Builds one program, `mkfs.erofs`.
- Adds libselinux CFLAGS to `AM_CPPFLAGS`.
- Compiles `mkfs_erofs_SOURCES = main.c`.
- Uses `-Wall` and the top-level `include` directory in `mkfs_erofs_CFLAGS`.
- Links against the in-tree `lib/liberofs.la`.

## Dependencies

- Requires the top-level Automake/libtool build to provide `liberofs.la` and configured `${libselinux_CFLAGS}`.

## Risks And Invariants

- `mkfs.erofs` is intentionally a thin target around `main.c`; most functionality is linked from `liberofs`.
- Include paths and libselinux flags must remain consistent with configuration-time feature detection.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/mkfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/mkfs/main.c -->
# File Research: sources/local-fs/erofs-utils/mkfs/main.c

## Scope

This file is the `mkfs.erofs` command-line entry point. It parses options, configures compression/xattr/tar/rebuild/S3/OCI/metabox/blob modes, opens inputs and output image, initializes importer state, builds the source tree, flushes metadata/data, writes the superblock, optionally writes checksums and VMDK descriptors, and cleans up global resources.

## Public And Internal APIs Covered

- User-facing helpers: `usage()`, `version()`, `parse_source_date_epoch()`, and `erofs_show_progs()`.
- Option parsers: `parse_extended_opts()`, `mkfs_apply_zfeature_bits()`, `mkfs_parse_tar_cfg()`, `mkfs_parse_options_cfg()`, compressor parser helpers, numeric parser helpers, and optional S3/OCI parser helpers.
- Source setup: `mkfs_parse_sources()` and `erofs_mkfs_rebuild_load_trees()`.
- Defaults and summaries: `erofs_mkfs_default_options()` and `erofs_mkfs_showsummaries()`.
- Program control: `main()`.

## Control Flow And Behavior

- Static long options expose core mkfs controls: block size, verbosity, xattrs, compression, pcluster sizes, metadata compression, timestamps, UUID, exclusion rules, SELinux labels, uid/gid mapping, tar/index modes, blob devices, incremental/rebuild modes, metazone/metabox controls, xattr prefixes, VMDK output, and optional S3/OCI/gzip/lzma/gzran/multithreaded features.
- `usage()` prints supported compressors dynamically, including level/dictionary ranges and LZMA advanced options.
- Extended options toggle inode format forcing, superblock CRC disabling, data inlining, chunk format forcing, xattr name filters, plain xattr prefixes, ztailpacking, fragments/all-fragments, dedupe, fragment dedupe, 48-bit layout, and dot omission.
- Compression option parsing supports colon-separated algorithm sets, per-algorithm `level=`, `dictsize=`, old numeric level syntax, and extra compressor-specific options.
- Source parsing chooses local directory, rebuild-from-image, tar stream/file, S3, or OCI. Rebuild mode opens one or more existing EROFS images as sources and assigns extra-device ids.
- `mkfs_parse_options_cfg()` validates option interactions: blobdev requires chunksize, blobdev cannot currently use block-map chunk format, chunksize must be a power of two and at least block size, pcluster sizes must be block-size multiples, metabox requires valid pcluster sizing, and tar index mode may force 512-byte blocks.
- `SOURCE_DATE_EPOCH` switches build-time behavior to reproducible-build clamping if valid.
- Main initialization calls global setup, importer preset/defaults, option parsing, output device open, optional Android fs config load, config display, tar/rebuild/OCI block-size adjustment, and clean or incremental filesystem initialization.
- Clean builds generate a UUID unless the user supplied one. Incremental builds load an existing superblock and append through `erofs_mkfs_load_fs()`.
- Disk buffers are initialized for full tar, S3, and OCI imports that need staged file payloads. Compression hints and importer state are then initialized.
- Dedupe setup selects compressed-data dedupe when compression is active, or falls back to chunk-based data dedupe when forced without compression.
- Blob/device-table setup occurs for tar index mode, explicit blob devices, rebuild blob-index mode, or extra-device outputs.
- Local-directory sources pre-scan shared xattrs before root inode creation. All source modes flush configured xattr name prefixes before tree import.
- Tree building dispatches by source: tar records are parsed until end-of-archive, rebuild sources load existing trees, S3 builds from object-store metadata/data, and OCI builds from remote image/layers. Unsupported incremental/reserved-space combinations return `-EOPNOTSUPP`.
- After import, `erofs_importer_load_tree()` finalizes the tree, blob/index metadata is dumped when needed, all importer outputs are flushed, root is dropped, the superblock is written, the device is resized, optional superblock checksum is enabled, and optional VMDK descriptor is generated.
- Exit cleanup drops root, dedupe, blocklist output, compression hints, exclude rules, blob state, xattr prefixes, rebuild sources, disk buffers, tar streams/dump fds/zinfo export, importer state, superblock state, device fd, and global library state.

## State And Data Structures

- `mkfscfg` stores compression parameter sets, inline-xattr tolerance, inode metazone flag, build timestamp, and total compression configs.
- Global/static mode state includes pcluster sizes, tarfile state, incremental flag, metabox algorithm id, source mode, rebuild source list/count, fixed UUID, dsunit, tar decoder, VMDK output file, zinfo output file, optional S3/OCI configs, and data import mode.
- `erofs_importer_params` carries per-build behavior into the shared importer pipeline.
- The program mutates global `cfg` and `g_sbi` throughout option parsing and build execution.

## Dependencies

- Links against `liberofs.la` and uses importer, inode, tar, xattr, dedupe, exclude, block-list, compression hints, blobchunk, compressor, gzran, metabox, OCI, private rebuild, S3, UUID, diskbuf, and superblock/device helpers.
- Optional compile-time dependencies include libselinux, zlib, liblzma, multithreading, Android fs config, S3, and OCI support.

## Risks And Invariants

- Many options mutate global state during parsing; validation order matters because later checks assume `mkfs_blkszbits`, chunk bits, feature bits, and source mode are settled.
- Tar index mode without a mapfile forces 512-byte blocks and creates an extra device entry for the tar source; this must be coordinated with superblock/device-table writing.
- Rebuild blob-index mode assumes each source image has either no extra device or exactly one extra device; mismatches are rejected.
- Cleanup is centralized under `exit:` and must tolerate partially initialized subsystems.
- `--quiet` lowers output and disables progress after parsing; errors still propagate through final formatting failure reporting.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/mkfs/main.c -->