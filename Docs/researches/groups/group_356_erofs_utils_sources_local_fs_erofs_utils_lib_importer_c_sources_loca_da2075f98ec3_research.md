# Group Research: group_356_erofs_utils_sources_local_fs_erofs_utils_lib_importer_c_sources_loca_da2075f98ec3

Scope checked against `Docs/research_subset_a.md`: `sources/local-fs/erofs-utils` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/importer.c -->
# File Research: sources/local-fs/erofs-utils/lib/importer.c

This file is the high-level importer lifecycle coordinator for mkfs/rebuild flows. It presets importer parameters, performs one-time global initialization, initializes per-filesystem subsystems, flushes pending filesystem state, and tears down importer-managed metadata.

Key functions:
- `erofs_importer_preset()` fills conservative defaults: fixed uid/gid disabled, `fsalignblks = 1`, build time unset, compressed extent size unspecified.
- `erofs_importer_global_init()` lazily initializes the inode manager under `erofs_importer_global_mutex`.
- `erofs_importer_init()` initializes xattrs, compression, packed-file support, metadata managers, optional fragment dedupe, 48-bit mode for omitted dot entries, and build timestamp fields.
- `erofs_importer_flush_all()` flushes metabox content, packed inode data, metadata zones, writes the device table, flushes all non-superblock buffers, and fixes up the root inode.
- `erofs_importer_exit()` exits dedupe, metadata, and packed-file facilities.

Important behavior:
- Packed file support is enabled not only for fragments but also extra EA name prefixes and compressed directories.
- `build_time` handling differs for 48-bit mode: epoch may be adjusted so the 32-bit build time field remains bounded.
- Flush order matters: metabox and packed inode data are finalized before buffer flush and root inode fixup.

Dependencies:
- `erofs_xattr_init`, `z_erofs_compress_init`, `erofs_packedfile_init`, `erofs_metadata_init`, `z_erofs_dedupe_ext_init`, `erofs_metabox_iflush`, `erofs_metazone_flush`, `erofs_bflush`, `erofs_fixup_root_inode`.

Risks / notes:
- Init failure reports the subsystem name, but already-initialized subsystems are not unwound here; callers must pair successful initialization with exit.
- Global inode manager initialization is process-wide and intentionally guarded for repeated importer creation.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/importer.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/inode.c -->
# File Research: sources/local-fs/erofs-utils/lib/inode.c

This is the main inode import, tree traversal, directory serialization, data-write, and on-disk inode flushing implementation for erofs-utils. It bridges host filesystem metadata, rebuild/import sources, compression, packed fragments, metadata zones, and final EROFS inode layout.

Major responsibilities:
- File type translation between POSIX modes, EROFS file types, and dirent `d_type`.
- In-memory inode deduplication by source `(dev, ino)` for hard links.
- Dentry allocation, sorting, NID invalidation, and directory stream generation.
- Data block reservation and writing for unencoded, compressed, chunked, symlink, special, directory, and special packed/metabox inodes.
- On-disk compact/extended inode selection and serialization.
- Whole-tree mkfs import, optionally with a worker thread for nondirectory data jobs.
- Incremental/rebuild integration with base directories and whiteout handling.

Key data/lifecycle functions:
- `erofs_inode_manager_init()`, `erofs_insert_ihash()`, `erofs_remove_ihash()`, `erofs_iget()`, `erofs_iput()` manage the global inode hash and refcounted in-memory inodes.
- `erofs_new_inode()` creates target-associated inodes with default flat-plain layout and unallocated NID.
- `erofs_fill_inode()` and `__erofs_fill_inode()` apply uid/gid fixes, Android fsconfig when enabled, timestamp policy, mode, size, source path, and compact/extended layout choice.
- `erofs_iget_from_local()` imports local `lstat()` metadata and reuses non-directory inodes when hard links are not dereferenced.

Directory handling:
- `erofs_d_alloc()` creates padded dentries.
- `erofs_dentry_mergesort()` sorts directory entries in EROFS order.
- `erofs_prepare_dir_file()` adds `.` unless omitted, always adds `..`, computes packed directory size, and marks layout undecided.
- `erofs_dirwriter_open()` exposes generated directory blocks through an `erofs_vfile`.
- `fill_dirblock()` emits dirent headers followed by names.
- `erofs_rebuild_inode_fix_pnid()` can patch `..` in reused base directories during incremental/rebuild flows.

Data writing:
- `erofs_allocate_inode_bh_data()` reserves data or directory blocks in the main buffer manager or metadata zone.
- `erofs_write_unencoded_data()` copies file data into allocated blocks and stores tail data for possible inline placement.
- `erofs_write_unencoded_file()` routes chunked files to blobchunk code when configured, otherwise flat inline/plain.
- `erofs_write_file_from_buffer()` handles symlinks and in-memory buffers.
- `erofs_write_dir_file()` writes directory data compressed or unencoded.
- `erofs_write_tail_end()` either binds tail data as inline metadata or writes a padded tail block.

On-disk serialization:
- `erofs_lookupnid()` assigns NIDs once inode buffer placement is known; metabox NIDs carry the metabox bit.
- `erofs_prepare_inode_buffer()` chooses inline vs non-inline, handles 48-bit requirements, allocates inode buffers, attaches inline data buffers, and registers flush callbacks.
- `erofs_iflush()` writes compact or extended inode structures, xattr ibodies, compression metadata, or chunk indexes.
- `erofs_fixup_root_inode()` updates `sbi->root_nid` or copies a late root inode back into an earlier root slot when old non-48-bit root constraints require it.

Tree import:
- `erofs_mkfs_import_localdir()` reads local directories, applies exclude rules, imports child inodes, and tracks whiteouts.
- `erofs_prepare_dir_inode()` merges local, rebuild, incremental base entries, strips overlayfs whiteouts if configured, and finalizes nlink/counts.
- `erofs_mkfs_begin_nondirectory()` opens file data, sets optional SHA-256 fingerprint xattr, starts compression if available and applicable, then queues the data job.
- `erofs_mkfs_dump_tree()` drives traversal from root, handles hard links, directory write ordering, pending grouped directory data, and root NID assignment.
- `erofs_importer_load_tree()` is the public entry point; incremental builds are rejected for metabox filesystems.
- `erofs_mkfs_build_special_from_fd()` imports generated special files such as packed inode/metabox from an fd.

Concurrency:
- When `EROFS_MT_ENABLED`, a bounded pthread queue handles mkfs job items asynchronously. The queue size is configured or derived from the file descriptor limit.

Important invariants:
- `inode->bh` placement determines NID.
- Special identifiers use pointer identity (`EROFS_PACKED_INODE`, `EROFS_METABOX_INODE`) and are not freed as normal paths.
- Compact inodes are upgraded when uid/gid/nlink/size/mtime/48-bit constraints require extended layout unless compact is forced.
- Directory data is generated lazily from dentries, so dentries hold inode refs until their NIDs are fixed.

Risks / notes:
- Many helper return values from `erofs_prepare_inode_buffer()` / `erofs_write_tail_end()` are assumed in some paths; failures would be serious because they occur late in object construction.
- The file is a central integration point; changes can affect local mkfs, OCI/S3 import, rebuild, incremental mode, compression, metadata zones, and root placement.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/io.c -->
# File Research: sources/local-fs/erofs-utils/lib/io.c

This file implements the generic `erofs_vfile` I/O abstraction plus native fd/device/blob helpers. It supports real file descriptors, dry-run mode, and overrideable virtual file operations.

Main groups:
- Write/read helpers: `__erofs_io_write`, `erofs_io_pwrite`, `erofs_io_pwritev`, `erofs_io_pread`, `erofs_io_read`, `erofs_io_write`.
- File maintenance: `erofs_io_fstat`, `erofs_io_fsync`, `erofs_io_fallocate`, `erofs_io_ftruncate`, `erofs_io_lseek`, `erofs_io_close`.
- Device/blob management: `erofs_dev_open`, `erofs_dev_close`, `erofs_blob_open_ro`, `erofs_blob_closeall`, `erofs_dev_read`.
- Copy helpers: `erofs_copy_file_range`, `erofs_io_sendfile`, `erofs_io_xcopy`.

Important behavior:
- If `cfg.c_dry_run` is set, write/truncate/fallocate/fsync operations become no-ops and fstat returns a synthetic regular-file mode.
- Every public `erofs_vfile` helper first delegates to `vf->ops` when present.
- `erofs_dev_open()` handles regular files and block devices. With truncation on regular files, it may unlink and recreate files on ext4/btrfs to avoid undesirable writeback after `truncate(0)`.
- Block devices are sized with `BLKGETSIZE64` / `BLKGETSIZE`, rounded to EROFS block size, and optionally discarded.
- `erofs_dev_read()` treats short reads as EOF and pads the destination with zeroes.
- Copy paths prefer kernel helpers (`copy_file_range`, `sendfile`, `pwritev`) and fall back to buffered loops.

Notable dependencies:
- `erofs_vfile` ops from `erofs/internal.h`.
- Linux block ioctls and fallocate/discard when available.
- Global config `cfg`.

Risks / notes:
- The native `erofs_io_pwrite()` and `erofs_io_pread()` loops advance `buf` and `pos`, but the syscall length argument remains `len` rather than remaining length. If a short read/write occurs, this should be audited because callers expect exact accounting.
- `erofs_io_xcopy()` decrements requested length by bytes read even if a later pwrite writes fewer bytes than read; it treats negative writes but not partial writes as fatal.
- The abstraction is performance-sensitive because it sits beneath metadata flush, image writes, remote-backed vfiles, and diskbuf copies.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/kite_deflate.c -->
# File Research: sources/local-fs/erofs-utils/lib/kite_deflate.c

This file implements a custom raw DEFLATE encoder named `kite_deflate`. It includes bit emission, fixed/dynamic Huffman generation, block cost selection, a hash-chain LZ matchfinder, and optional test code that validates output through zlib when available.

Core structures:
- `struct kite_deflate_symbol`: literal or match symbol.
- `struct kite_deflate_table`: Huffman code/length tables for literal/length, distance, and code-length alphabets.
- `struct kite_deflate`: encoder state, buffers, bit writer state, frequencies, selected mode, symbol queue, and matchfinder.
- `struct kite_matchfinder`: hash/chain tables, current offset, cyclic window, match limits, and lazy-match state.

Compression flow:
- `kite_deflate_init_once()` initializes fixed Huffman tables, length slot lookup, and distance fast-position table.
- `kite_deflate_init()` allocates the encoder, symbol array, and matchfinder; level 1-9 config controls lazy search and depth.
- `kite_deflate_destsize()` compresses as much source as fits in a target destination size, updates `*srcsize` to consumed bytes, and returns output bytes.
- `kite_deflate_end()` releases hash/chain/symbol memory.

Block handling:
- `kite_deflate_startblock()` resets frequencies and starts with fixed Huffman mode.
- `deflate_count_code()` updates symbol frequencies and estimated bit costs, switching/recomputing dynamic tables when needed.
- `kite_deflate_endblock()` compares fixed/dynamic/stored block cost and may force final block if remaining output space is tight.
- `kite_deflate_commitblock()` writes fixed, dynamic, or stored blocks.
- `kite_deflate_writeblock()` writes literal and length/distance symbols and the end-of-block marker.
- `kite_deflate_sendtrees()` emits dynamic Huffman tree metadata.

Matchfinding:
- `kite_mf_getmatches_hc3()` hashes 3-byte prefixes using a CRC-CCITT table and searches a bounded hash chain.
- `kite_deflate_fast()` uses immediate longest matches.
- `kite_deflate_slow()` implements lazy matching.
- Level configuration mirrors zlib-style good/lazy/nice/depth values.

Built-in test support:
- Under `TEST`, the file can run a minimal fixed-Huffman test and file compression test.
- With zlib enabled, it inflates generated raw deflate and compares to the original input.

Risks / notes:
- The encoder writes into caller-provided buffers and relies on cost checks plus `DBG_BUGON` to avoid overflow; changes to cost accounting are high risk.
- Static global initialization is guarded by checking `kstaticHuff_distCodes[31]`, not by a lock; concurrent first-use would be worth reviewing if used from multiple threads.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/kite_deflate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_base64.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_base64.h

This small internal header declares base64 helpers:
- `erofs_base64_encode(const u8 *src, int srclen, char *dst)`
- `erofs_base64_decode(const char *src, int len, u8 *dst)`

It includes `erofs/defs.h` for `u8` and uses a normal include guard.

Known users in this group:
- OCI username/password encoding and decoding.
- Docker config auth field decoding.

The header does not define ownership or output sizing rules; callers must allocate sufficient destination buffers. In observed users, encode size is computed as `4 * DIV_ROUND_UP(input_len, 3)` and decode buffers are sized from encoded length.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_base64.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_cache.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_cache.h

This header defines the buffer manager API used to allocate, attach, map, flush, and drop metadata/data buffers while constructing an EROFS image.

Core types:
- Buffer types: `DATA`, `META`, `INODE`, `DIRA`, `XATTR`, `DEVT`.
- `struct erofs_bhops`: flush callback interface for buffer heads.
- `struct erofs_buffer_head`: linked buffer item with offset, ops, and private data.
- `struct erofs_buffer_block`: physical/logical block bucket containing buffer heads.
- `struct erofs_bufmgr`: global manager with watermeter buckets, block header, target vfile, device-alignment settings, and mapping cache.

Important inline:
- `get_alignsize()` maps logical allocation types to alignment and storage type. Inode, directory, xattr, and device table allocations are redirected to metadata alignment rules.
- `erofs_btell()` computes the byte position of a buffer head from block address and intra-block offset.
- `erofs_bh_flush_generic_end()` removes and frees a buffer head.

External API:
- `erofs_buffer_init()`, `erofs_buffer_exit()`
- `erofs_balloc()`, `erofs_battach()`, `erofs_bdrop()`
- `erofs_bh_balloon()`
- `erofs_mapbh()`, `erofs_bflush()`

Known users:
- Inode placement and inline data.
- Directory and file data block reservation.
- Metadata zone and metabox staging.
- Device table writing.

Risks / notes:
- Many higher-level components assume `erofs_mapbh()` finalizes addresses before NID/blockaddr derivation.
- `watermeter` is sized by `EROFS_MAX_BLOCK_SIZE`, so block-size assumptions are baked into allocation bucketing.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_compress.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_compress.h

This internal compression header declares the interface between inode import and compressed-data construction.

Constants:
- `EROFS_CONFIG_COMPR_MAX_SZ` is 4000 KiB.
- `Z_EROFS_COMPR_QUEUE_SZ` is twice that max size.

Opaque type:
- `struct z_erofs_compress_ictx` represents per-file compression context.

File compression API:
- `erofs_prepare_compressed_file()`
- `erofs_bind_compressed_file_with_fd()`
- `erofs_begin_compressed_file()`
- `erofs_write_compressed_file()`
- `z_erofs_drop_inline_pcluster()`

Directory compression API:
- `erofs_begin_compress_dir()`
- `erofs_write_compress_dir()`

Lifecycle:
- `z_erofs_compress_init()`
- `z_erofs_compress_exit()`
- `z_erofs_mt_global_exit()`

Known users:
- `importer.c` initializes compression.
- `inode.c` prepares/begins/writes compressed files and directories, with fallback to unencoded output on `-ENOSPC`.

Risk / note:
- The API separates “begin” from “write”, enabling async job scheduling, so callers must keep fd/context lifetime valid across both phases.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_compress.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_dockerconfig.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_dockerconfig.h

This header declares Docker registry credential lookup support for OCI import.

Definitions:
- `DOCKER_REGISTRY`: `docker.io`
- `DOCKER_API_REGISTRY`: `registry-1.docker.io`
- `DOCKER_HUB_AUTH_KEY`: Docker Hub’s config auth key.
- `struct erofs_docker_credential` with heap-owned `username` and `password`.

API:
- `erofs_docker_config_lookup(const char *registry, struct erofs_docker_credential *cred)`
- `erofs_docker_credential_free(struct erofs_docker_credential *cred)`

Known users:
- `remotes/oci.c` uses this when CLI credentials are absent.

Ownership:
- On success, `cred->username` and `cred->password` must be released through `erofs_docker_credential_free()`, which scrubs sensitive memory in the implementation.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_dockerconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_fragments.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_fragments.h

This header declares packed-fragment support for deduplicating and storing file fragments in a packed inode.

API:
- `z_erofs_fragments_tofh()` computes a fragment hash-like value from file data.
- `erofs_fragment_findmatch()` searches for a matching fragment.
- `erofs_pack_file_from_fd()` packs file data from a vfile/fpos.
- `erofs_fragment_pack()` packs an in-memory fragment region.
- `erofs_fragment_commit()` finalizes fragment metadata for an inode.
- `erofs_flush_packed_inode()` flushes packed inode state at importer finalization.
- `erofs_packedfile()` returns or creates packed file support for an sb.

Known users:
- `importer.c` initializes packed files when fragments, compressed dirs, or extra xattr prefix handling require it, and flushes packed inode data before final metadata flush.
- `inode.c` treats packed inode as a special identifier and avoids extended inode layout for it.

Risk / note:
- The API is tightly coupled to compression/fragments and must be flushed before the main buffer manager is flushed.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_fragments.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_gzran.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_gzran.h

This header declares gzip random-access index builder/open support.

Constant:
- `EROFS_GZRAN_WINSIZE` is 32768 bytes, matching gzip/deflate window size.

Types:
- Opaque `struct erofs_gzran_builder`.

Builder API:
- `erofs_gzran_builder_init(struct erofs_vfile *vf, u32 span_size)`
- `erofs_gzran_builder_read(struct erofs_gzran_builder *gb, char *window)`
- `erofs_gzran_builder_export_zinfo(struct erofs_gzran_builder *gb, struct erofs_vfile *zinfo_vf)`
- `erofs_gzran_builder_final(struct erofs_gzran_builder *gb)`

Reader API:
- `erofs_gzran_zinfo_open(struct erofs_vfile *vin, void *zinfo_buf, unsigned int len)`

Known users:
- `remotes/oci.c` selects the GZRAN decoder when tarindex and zinfo paths are provided, then exports zinfo after processing.

Risk / note:
- This is a stream/index integration point: caller-owned vfiles and zinfo buffers must remain valid for the opened reader/builder lifetime.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_gzran.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_metabox.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_metabox.h

This header declares metadata-zone/metabox support.

Definitions:
- `EROFS_META_NEW_ADDR` marks a not-yet-placed metadata zone.
- `erofs_metabox_identifier` / `EROFS_METABOX_INODE` identify the generated metabox inode by pointer identity.
- `erofs_is_metabox_inode()` checks that special source path.
- `erofs_has_meta_zone()` checks whether metadata-zone support is active or pending.

API:
- `erofs_metadata_init()`, `erofs_metadata_exit()`
- `erofs_metadata_bmgr(struct erofs_sb_info *sbi, bool mbox)`
- `erofs_metabox_iflush(struct erofs_importer *im)`
- `erofs_metazone_flush(struct erofs_sb_info *sbi)`

Known users:
- `importer.c` initializes metadata managers and flushes metabox/metazone data.
- `inode.c` places ordinary inodes in metabox when available, and writes directory data into metadata zone when configured.
- `metabox.c` implements the API.

Risk / note:
- Special metabox inode identity is pointer-based, so callers must use the exported identifier, not a copied string.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_metabox.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_nbd.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_nbd.h

This header defines userspace Network Block Device integration declarations.

Key definitions:
- `EROFS_NBD_MAJOR` is 43.
- Request command enum covers read, write, disconnect, flush, trim, and write-zeroes.
- `struct erofs_nbd_request` mirrors packed NBD request layout with magic, type, cookie/handle, offset, and length.
- `EROFS_NBD_DEAD_CONN_TIMEOUT` is 30 days for recovery behavior.

Classic ioctl/socket style API:
- `erofs_nbd_in_service()`
- `erofs_nbd_devscan()`
- `erofs_nbd_connect()`
- `erofs_nbd_get_identifier()`
- `erofs_nbd_get_index_from_minor()`
- `erofs_nbd_do_it()`
- `erofs_nbd_get_request()`
- `erofs_nbd_send_reply_header()`
- `erofs_nbd_disconnect()`

Netlink API:
- `erofs_nbd_nl_connect()`
- `erofs_nbd_nl_reconnect()`
- `erofs_nbd_nl_reconfigure()`
- `erofs_nbd_nl_disconnect()`

Risk / note:
- The struct uses mixed endian fields and packed layout; implementation must preserve kernel ABI exactly.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_nbd.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_oci.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_oci.h

This header declares OCI image import and OCI-backed vfile support.

Configuration:
- `struct ocierofs_config` includes image reference, platform, optional credentials, optional blob digest or layer index, tarindex/zinfo paths, and insecure transport flag.

Runtime types:
- `struct ocierofs_layer_info` stores digest, media type, and size.
- `struct ocierofs_ctx` stores curl handle, auth header, registry/repository/platform/tag/manifest, layer list, blob selection, and scheme.
- `struct ocierofs_iostream` stores context and sequential read offset for HTTP range-backed vfiles.

API:
- `ocierofs_build_trees()` downloads selected image layers, parses tar content, and populates an importer.
- `ocierofs_io_open()` opens a range-read vfile for a selected blob.
- `ocierofs_encode_userpass()` / `ocierofs_decode_userpass()` handle base64 username/password strings.
- `ocierofs_get_platform_spec()` returns host platform in OCI `os/arch[/variant]` form.

Known implementation:
- `remotes/oci.c`.

Risk / note:
- The same context type supports both full layer import and random-access layer I/O, so cleanup ownership is important: `ocierofs_io_close()` owns and frees the heap context created by `ocierofs_io_open()`.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_oci.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_private.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_private.h

This private header centralizes optional platform/private includes and a compatibility shim.

Conditional includes:
- SELinux headers when `HAVE_LIBSELINUX`.
- Android filesystem config and canned fsconfig headers when `WITH_ANDROID`.

Compatibility:
- Provides an inline `memrchr()` implementation when the platform lacks it. It scans backward through a byte range and returns the last matching byte pointer or `NULL`.

Private API:
- `int erofs_tmpfile(void);`

Known users:
- `inode.c` uses Android/SELinux-related configuration paths.
- `metabox.c` and `remotes/oci.c` use `erofs_tmpfile()` for temporary staging.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_private.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_rebuild.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_rebuild.h

This header declares rebuild/merge support for constructing a target tree from existing EROFS trees and tar/container-like paths.

Data mode enum:
- `EROFS_REBUILD_DATA_BLOB_INDEX`: represent source data through blob chunk indexes.
- `EROFS_REBUILD_DATA_RESVSP`: reserve data space.
- `EROFS_REBUILD_DATA_FULL`: declared, but the implementation in this group does not support it for regular files.

API:
- `erofs_rebuild_get_dentry()` resolves/creates a path under an in-memory directory tree, with AUFS whiteout and opaque-directory detection.
- `erofs_rebuild_load_tree()` loads an existing source EROFS tree into a target root using a selected data mode.
- `erofs_rebuild_load_basedir()` loads entries from a base directory for incremental rebuilds.

Known implementation:
- `rebuild.c`.

Risk / note:
- `erofs_rebuild_get_dentry()` mutates the path buffer while splitting components, so callers must pass writable storage.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_rebuild.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_s3.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_s3.h

This header declares S3 remote import support.

Enums:
- `s3erofs_url_style`: path style or virtual-host style.
- `s3erofs_signature_version`: AWS Signature Version 2 or Version 4.

Constants:
- Access key and secret key buffers are 256 bytes plus NUL.

Configuration/runtime:
- `struct erofs_s3` stores a curl handle, endpoint, region, credentials, URL style, and signature version.

API:
- `s3erofs_build_trees(struct erofs_importer *im, struct erofs_s3 *s3, const char *path, bool fillzero)`

Known implementation:
- `remotes/s3.c`.

Behavior from implementation:
- Lists objects from an S3 bucket/prefix, creates corresponding in-memory EROFS dentries/inodes, and either downloads object contents or fills files with zeroes.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_s3.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_uuid.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_uuid.h

This header declares UUID helper functions:
- `erofs_uuid_generate(unsigned char *out)`
- `erofs_uuid_unparse_lower(const unsigned char *buf, char *out)`
- `erofs_uuid_parse(const char *in, unsigned char *uu)`

Known user in this group:
- `rebuild.c` uses `erofs_uuid_unparse_lower()` to produce a fallback filesystem identifier when a source sb has no `devname`.

Output sizing:
- `erofs_uuid_unparse_lower()` callers should provide space for canonical UUID text plus NUL; `rebuild.c` uses a 37-byte buffer.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_uuid.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_xxhash.h -->
# File Research: sources/local-fs/erofs-utils/lib/liberofs_xxhash.h

This header wraps xxHash support.

Behavior:
- If system xxhash headers/library are available, `xxh32()` and `xxh64()` inline to `XXH32()` and `XXH64()`.
- Otherwise it declares local fallback implementations:
  - `uint32_t xxh32(const void *input, size_t length, uint32_t seed)`
  - `uint64_t xxh64(const void *input, const size_t len, const uint64_t seed)`

It uses a dual BSD-2-Clause/GPL-2.0+ license and C++ extern guards.

Risk / note:
- The wrapper intentionally exposes the same local function names regardless of backend; consumers should include this header rather than directly depending on system xxhash.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/liberofs_xxhash.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/metabox.c -->
# File Research: sources/local-fs/erofs-utils/lib/metabox.c

This file implements metadata-zone and metabox staging managers.

Core type:
- `struct erofs_metamgr` holds a temporary `erofs_vfile` and its own `erofs_bufmgr`.

Lifecycle:
- `erofs_metamgr_init()` creates a temporary file and initializes a buffer manager against it.
- `erofs_metamgr_exit()` exits the buffer manager, closes the temp vfile, and frees the manager.
- `erofs_metadata_init()` creates `sbi->m2gr` when `metazone_startblk == EROFS_META_NEW_ADDR`, and creates `sbi->mxgr` when the superblock has metabox enabled.
- `erofs_metadata_exit()` releases both managers.

Access:
- `erofs_metadata_bmgr(sbi, mbox)` returns the metazone or metabox buffer manager if present.

Flush paths:
- `erofs_metabox_iflush()` flushes metabox buffers, checks if the temp file has data, imports it as a special inode from fd, records `sbi->metabox_nid`, and drops the inode.
- `erofs_metazone_flush()` allocates a DATA area in the main image, flushes metazone buffers, balloons the destination buffer head to the metazone length, copies staged metadata into the main image, drops the buffer head, and adjusts `sbi->meta_blkaddr`.

Important behavior:
- Metazone data is staged separately and later copied into the main image.
- Metabox content becomes a regular special inode generated from the temp fd.
- `sbi->meta_blkaddr` is set to `EROFS_META_NEW_ADDR` during new metazone initialization.

Risks / notes:
- `erofs_metazone_flush()` returns success even if the copy loop breaks only after a negative `ret`? It checks and breaks, but final return is `0`; the negative copy result path should be reviewed.
- Temporary file and buffer manager lifetime is tied to `sbi->m2gr` / `sbi->mxgr`.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/metabox.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/namei.c -->
# File Research: sources/local-fs/erofs-utils/lib/namei.c

This file implements on-disk inode reading and path lookup inside an EROFS image.

Inode reading:
- `erofs_read_inode_from_disk(struct erofs_inode *vi)` reads compact or extended inode structures from metadata or metabox storage.
- It validates `i_format`, datalayout, inode version, chunk format, and file mode.
- It handles extended inode records crossing block boundaries.
- It fills inode size, uid/gid, nlink, mtime, xattr ibody size, flat block address, device number, chunk format, and dot-omitted flag.
- Compact inode handling supports the special nlink-1/startblk_hi encoding and respects 32-bit vs 48-bit address masks.

Directory lookup:
- `find_target_dirent()` scans a directory block’s dirent table and compares names while validating name offsets and lengths.
- `erofs_namei()` opens a directory inode with `erofs_iopen()`, reads directory blocks through `erofs_pread()`, validates the first `nameoff`, and returns the target child NID.
- `link_path_walk()` walks slash-separated components from root.
- `erofs_ilookup()` resolves a path into an inode by NID and then reads the inode from disk.

Important behavior:
- Short or malformed directory entries return `-EFSCORRUPTED`.
- Directory block scanning uses `nameoff` as the boundary between dirent records and name strings.
- Device numbers use local Linux-compatible decode logic.

Dependencies:
- Metadata buffer reading via `erofs_read_metabuf`.
- File data reads via `erofs_iopen` / `erofs_pread`.
- Endian conversion and on-disk EROFS structs.

Risk / note:
- This is read-side validation code used by rebuild, incremental, and lookup flows; corruption handling here directly affects importer robustness.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/rebuild.c -->
# File Research: sources/local-fs/erofs-utils/lib/rebuild.c

This file builds/merges an in-memory target tree from existing EROFS filesystems, container layer paths, and incremental base directories.

Path/dentry construction:
- `erofs_rebuild_mkdir()` creates implicit parent directories with inherited uid/gid/mtime and parent-derived write bits.
- `erofs_d_lookup()` searches a directory’s child dentries by name.
- `erofs_rebuild_get_dentry()` walks a writable path string, creates missing intermediate directories, supports `..`, optionally recognizes AUFS whiteouts (`.wh.` prefix) and opaque directory markers, and optionally moves found dentries to list head.

Data conversion:
- `erofs_rebuild_write_blob_index()` converts supported source file mappings into chunk indexes for the target filesystem, creating unhashed blob chunks from mapped physical addresses.
- `erofs_rebuild_update_inode()` normalizes source inodes for the target: encodes device numbers, reads symlink content into memory, marks whiteout parents, and chooses blob-index or reserved-space handling for regular files.

Tree merge:
- `erofs_rebuild_dirent_iter()` is the callback for source-tree traversal. It merges lower-layer directory entries, skips entries shadowed by upper layers or opaque directories, preserves hard links for regular files, reads xattrs, updates source inode data mode, and recursively descends into directories.
- `erofs_rebuild_load_tree()` reads a source superblock/root inode and iterates it into a target root with a selected data mode.

Incremental base:
- `erofs_rebuild_basedir_dirent_iter()` records base directory entries as already-valid NIDs or updates existing in-memory child directory identity for recursive loading.
- `erofs_rebuild_load_basedir()` loads entries from an existing target/base directory into a current in-memory directory and inherits root xattr size.

Overlay/container semantics:
- AUFS whiteouts and opaque directories are understood by `erofs_rebuild_get_dentry()`.
- EROFS whiteouts are detected with `erofs_inode_is_whiteout()` / `erofs_dentry_is_wht()` in inode code.

Important dependencies:
- `erofs_iterate_dir`, `erofs_read_inode_from_disk`, `erofs_read_xattrs_from_disk`, `erofs_map_blocks`, blobchunk helpers, UUID helpers.

Risks / notes:
- `EROFS_REBUILD_DATA_FULL` is declared but regular file handling returns `-EOPNOTSUPP` unless blob-index or reserved-space mode is selected.
- `erofs_rebuild_get_dentry()` mutates path separators while walking, so callers must not pass string literals.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/rebuild.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/remotes/docker_config.c -->
# File Research: sources/local-fs/erofs-utils/lib/remotes/docker_config.c

This file implements Docker `config.json` credential lookup when json-c is available, and stubs it out with `-EOPNOTSUPP` otherwise.

Without json-c:
- `erofs_docker_config_lookup()` returns `-EOPNOTSUPP`.
- `erofs_docker_credential_free()` is a no-op.

With json-c:
- `docker_config_path()` resolves `$DOCKER_CONFIG/config.json`, or `$HOME/.docker/config.json`.
- `read_file_to_string()` reads config files up to 4 MiB.
- `registry_match()` treats Docker Hub specially: `docker.io` and `registry-1.docker.io` match `https://index.docker.io/v1/`; other registries match case-insensitively by exact key.
- `decode_auth_field()` base64-decodes `username:password`, splits on the first colon, duplicates both strings, and scrubs the decoded buffer.
- `erofs_docker_config_lookup()` parses JSON, scans `auths`, decodes the matching `auth` field, and returns populated credentials.
- `erofs_docker_credential_free()` scrubs and frees username/password.

Important behavior:
- Missing config, missing auths, or no matching registry returns `-ENOENT`.
- Malformed JSON returns `-EINVAL`.
- Sensitive buffers are cleared with `erofs_free_sensitive()` where implemented.

Risk / note:
- Only inline `auth` entries are supported; external credential helpers/stores are not handled.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/remotes/docker_config.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/remotes/oci.c -->
# File Research: sources/local-fs/erofs-utils/lib/remotes/oci.c

This file implements OCI/Docker registry import and OCI blob-backed virtual I/O. When `OCIEROFS_ENABLED` is not defined, `ocierofs_io_open()` returns `-EOPNOTSUPP`; the full implementation requires curl and json-c feature support.

Registry/auth flow:
- `ocierofs_parse_ref()` parses image references, defaulting Docker Hub to `registry-1.docker.io`, `library/<name>`, and `latest`.
- `ocierofs_get_platform_spec()` maps host OS/architecture to OCI platform strings.
- `ocierofs_prepare_auth()` tries bearer-token auth and falls back to basic auth when credentials exist.
- `ocierofs_get_auth_token()` handles Docker Hub, discovered `WWW-Authenticate` realms, and several fallback auth endpoint patterns.
- Docker config credentials are loaded through `erofs_docker_config_lookup()` when CLI credentials are absent.

Manifest/layer selection:
- `ocierofs_get_manifest_digest()` fetches a manifest or manifest list/index, selects a platform-specific manifest, or treats the tag as manifest digest when appropriate.
- `ocierofs_fetch_layers_info()` loads layer digest, media type, and size from the selected manifest.
- `ocierofs_prepare_layers()` validates requested layer index or blob digest and fills `ctx->blob_digest` when needed.

Full import path:
- `ocierofs_extract_layer()` downloads a layer blob into a temp file.
- `ocierofs_process_tar_stream()` opens the layer as a tar stream. It uses gzip by default, raw tar for tarindex-only, and GZRAN when both tarindex and zinfo are configured. It repeatedly calls `tarerofs_parse_tar()` until archive end and exports zinfo when applicable.
- `ocierofs_build_trees()` initializes context, selects all layers or one selected layer, rejects tarindex mode unless exactly one layer is selected, downloads/processes each layer, and records tar-offset-derived device blocks for tarindex mode.

Range I/O path:
- `ocierofs_download_blob_range()` issues HTTP `Range` requests for the selected blob, handling `206` and some `200` fallback behavior.
- `ocierofs_io_pread()` and `ocierofs_io_read()` expose the selected remote blob as an `erofs_vfile`.
- `ocierofs_io_open()` allocates context and iostream state, requires `blob_digest`, and installs `ocierofs_io_vfops`.
- `ocierofs_io_close()` cleans up context and stream.

Credential helpers:
- `ocierofs_encode_userpass()` base64-encodes `username:password`.
- `ocierofs_decode_userpass()` decodes and splits the same format.

Built-in tests:
- Under `OCIEROFS_ENABLED && TEST`, there is a parse-reference test harness covering Docker Hub defaults, custom registries, ports, nested repositories, and tags.

Risks / notes:
- `ocierofs_extract_layer()` returns a temp fd directly on success; caller closes it after tar processing.
- Range fallback for `HTTP 200` copies from a full response when offset is nonzero, which can be expensive for registries that ignore range requests.
- Auth header parsing is simple string scanning and may not cover all valid quoted/auth parameter edge cases.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/remotes/oci.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/remotes/s3.c -->
# File Research: sources/local-fs/erofs-utils/lib/remotes/s3.c

This file implements S3 object listing, signing, downloading, and importer tree population.

URL/canonicalization:
- `s3erofs_parse_host()` separates optional URL scheme from endpoint.
- `s3erofs_urlencode()` encodes either query parameters or S3 object keys with different safe character sets.
- `s3erofs_prepare_canonical_query()` sorts query key/value pairs and builds SigV4 canonical query text.
- `s3erofs_prepare_url()` builds path-style or virtual-host style request URLs and canonical URI strings for SigV2/SigV4.

Signing:
- `s3erofs_sigv2_header()` creates an AWS SigV2 Authorization header with HMAC-SHA1 and base64.
- `s3erofs_sigv4_header()` creates the SigV4 canonical request, string-to-sign, signing key chain, and Authorization header using HMAC-SHA256.
- `s3erofs_request_insert_auth_v2()` and `_v4()` add required request headers.

Requests:
- `s3erofs_request_perform()` configures curl, adds auth headers when an access key is present, performs the request, and requires a 2xx HTTP code.
- `s3erofs_curl_easy_init()` sets follow-location, connect timeout, and user agent.
- `s3erofs_curl_easy_exit()` cleans up curl.

Object listing:
- `s3erofs_parse_list_objects_result()` parses ListObjects XML, tracks `IsTruncated`, `NextMarker`, and object entries.
- `s3erofs_list_objects()` sends a bucket listing request with prefix/delimiter/marker query parameters.
- `s3erofs_create_object_iterator()`, `s3erofs_get_next_object()`, and `s3erofs_destroy_object_iterator()` provide paginated iteration.

Object download/import:
- `s3erofs_remote_getobject()` downloads object data. If compression is unavailable and data inline is disabled, it writes directly into preallocated image blocks; otherwise it stages into an inode diskbuf for later importer processing.
- `s3erofs_build_trees()` initializes curl, iterates objects, creates target dentries/inodes with regular-file metadata, fills timestamps from S3 `LastModified`, applies importer inode fields, and downloads or zero-fills file contents.

Built-in tests:
- Under `TEST`, the file contains a URL canonicalization test matrix for path/virtual-host styles, explicit schemes, bucket-domain endpoints, trailing slashes, special characters, spaces, and error cases.

Risks / notes:
- XML timestamps are parsed with `strptime()` then `mktime()`, which interprets as local time rather than UTC; S3 `LastModified` is UTC, so this is worth auditing.
- The object iterator assumes `it->objects` is populated after a successful list; empty truncated/non-truncated edge cases should be handled carefully.
- Credentials are fixed buffers in `struct erofs_s3`, so callers must enforce length limits before populating.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/remotes/s3.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/rolling_hash.h -->
# File Research: sources/local-fs/erofs-utils/lib/rolling_hash.h

This header implements a simple Rabin-Karp-style rolling hash.

Constants:
- `PRIME_NUMBER` is `4294967295LL`.
- `RADIX` is 256.

Functions:
- `erofs_rolling_hash_init(u8 *input, int len, bool backwards)` computes an initial hash forward or backward across a window.
- `erofs_rolling_hash_advance(long long old_hash, unsigned long long RM, u8 to_remove, u8 to_add)` removes the outgoing byte contribution, multiplies by radix, adds the new byte, and normalizes negative results.
- `erofs_rollinghash_calc_rm(int window_size)` computes `RADIX^(window_size - 1) mod PRIME_NUMBER`.

Important note:
- The comment explicitly keeps signed `long long` for hashes because intermediate values may be negative before normalization.

Likely role:
- Used by dedupe/fragment matching code outside this group.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/rolling_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/sha256.c -->
# File Research: sources/local-fs/erofs-utils/lib/sha256.c

This file implements SHA-256, using OpenSSL EVP when configured and otherwise a public-domain LibTomCrypt-derived implementation.

OpenSSL path:
- `erofs_sha256_init()` allocates an `EVP_MD_CTX` and initializes SHA-256.
- `erofs_sha256_process()` calls `EVP_DigestUpdate()`.
- `erofs_sha256_done()` finalizes, writes output, and frees the EVP context.
- `erofs_sha256()` sets one-shot flag before process/done.

Fallback path:
- Defines SHA-256 constants, rotate/shift/logical macros, endian store/load helpers.
- `sha256_compress()` processes one 512-bit block.
- `erofs_sha256_init()` initializes standard SHA-256 state words.
- `erofs_sha256_process()` buffers input, compressing full 64-byte blocks and tracking bit length.
- `erofs_sha256_done()` appends padding, encodes message length, compresses final block, and writes 32-byte digest.

Convenience:
- `erofs_sha256(const unsigned char *in, unsigned long in_size, unsigned char out[32])` performs init/process/done in one call.

Built-in tests:
- Under `UNITTEST`, tests known SHA-256 vectors for empty string, `abc`, and a longer standard test message.

Known users:
- `inode.c` computes `sha256:<digest>` inode fingerprint xattrs when the shared xattr prefix is configured.

Risks / notes:
- OpenSSL init failure leaves `md->ctx` NULL and later functions return `-1`; the convenience wrapper does not check return values.
- Fallback uses `unsigned long`/`u64` length accounting and is intended for byte streams processed through the provided API.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/sha256.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/erofs-utils/lib/sha256.h -->
# File Research: sources/local-fs/erofs-utils/lib/sha256.h

This header declares SHA-256 state and functions.

Backend selection:
- If OpenSSL and `openssl/evp.h` are available, `struct sha256_state` contains `EVP_MD_CTX *ctx` and `__USE_OPENSSL_SHA256` is defined.
- Otherwise `struct sha256_state` contains fallback state: bit length, eight state words, current buffer length, and a 64-byte block buffer.

API:
- `erofs_sha256_init(struct sha256_state *md)`
- `erofs_sha256_process(struct sha256_state *md, const unsigned char *in, unsigned long inlen)`
- `erofs_sha256_done(struct sha256_state *md, unsigned char *out)`
- `erofs_sha256(const unsigned char *in, unsigned long in_size, unsigned char out[32])`

Known implementation:
- `sha256.c`.

Risk / note:
- Callers must provide a 32-byte output buffer. The header does not define a digest-size macro.
<!-- END FILE RESEARCH: sources/local-fs/erofs-utils/lib/sha256.h -->