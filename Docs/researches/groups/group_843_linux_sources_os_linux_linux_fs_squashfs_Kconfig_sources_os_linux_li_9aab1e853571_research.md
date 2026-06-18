# Group Research: group_843_linux_sources_os_linux_linux_fs_squashfs_Kconfig_sources_os_linux_li_9aab1e853571

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. I read every listed file completely and verified the line counts.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/squashfs/Kconfig

Defines the Linux kernel configuration surface for SquashFS 4.0, a compressed read-only filesystem requiring `BLOCK`.

Key options cover file-data decompression strategy (`SQUASHFS_FILE_CACHE` intermediate buffer vs `SQUASHFS_FILE_DIRECT` direct page-cache output), decompressor concurrency (`single`, dynamic `multi`, and `percpu`), optional mount-time `threads=`, xattrs, compression backends, device block size, embedded cache sizing, and fragment cache size.

Notable local option: `SQUASHFS_COMP_CACHE_FULL`, which enables caching all compressed block pages for repeated-read workloads at the cost of memory use.

Compression backend options select kernel libraries: zlib, LZ4, LZO, XZ, and ZSTD. Defaults favor zlib and conservative memory use.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/Makefile -->
# File Research: sources/os/linux/linux/fs/squashfs/Makefile

Builds `squashfs.o` when `CONFIG_SQUASHFS` is enabled.

Always links core objects for block I/O, caches, directories, export support, regular files, fragments, ids, inodes, name lookup, superblock handling, symlinks, decompressor dispatch, and page actors.

Conditionally links the selected file read strategy, decompressor threading implementation, xattr support, and enabled compression wrappers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/block.c -->
# File Research: sources/os/linux/linux/fs/squashfs/block.c

Implements the low-level path for reading compressed or uncompressed SquashFS metadata/data blocks from the block device.

`squashfs_bio_read()` builds BIOs aligned to the device block size, optionally reusing a page-cache mapping for compressed block pages. `squashfs_bio_read_cached()` avoids rereading cached folios and caches partial edge pages; with `CONFIG_SQUASHFS_COMP_CACHE_FULL`, it also tries to cache every page in the BIO.

`squashfs_read_data()` decodes metadata block length headers when needed, validates block bounds against `bytes_used`, submits I/O, and either copies uncompressed data into a page actor or calls the selected decompressor thread ops.

Important failure behavior: read or decompression failures log the failing block and panic when mounted with `errors=panic`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/cache.c -->
# File Research: sources/os/linux/linux/fs/squashfs/cache.c

Provides the generic SquashFS cache used for metadata blocks, fragment blocks, and optionally file data blocks in file-cache mode.

The cache is a fixed-size round-robin set of entries, protected by a spinlock plus wait queues. Entries have refcounts, pending state, per-entry waiters, error storage, and page-actor-backed PAGE_SIZE buffers.

`squashfs_cache_get()` handles lookup, eviction, blocking while all entries are busy, and filling missed entries via `squashfs_read_data()`. `squashfs_read_metadata()` walks packed metadata across compressed blocks using the metadata cache.

Also exposes helpers for fragment/data block lookup and `squashfs_read_table()`, which reads table ranges into kmalloc memory through a page actor.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor.c -->
# File Research: sources/os/linux/linux/fs/squashfs/decompressor.c

Implements compressor-id dispatch and shared decompressor setup.

The static table maps SquashFS compression ids to compiled wrappers or unsupported placeholders. LZMA is explicitly unsupported; disabled algorithms appear as unsupported stubs with names for clear mount errors.

`get_comp_opts()` reads optional compressor-specific data after the superblock when the filesystem flag says options are present, then calls the selected wrapper’s `comp_opts`.

`squashfs_decompressor_setup()` combines compressor options with the selected threading implementation’s `create()` method to produce `msblk->stream`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor.h -->
# File Research: sources/os/linux/linux/fs/squashfs/decompressor.h

Declares `struct squashfs_decompressor`, the common interface implemented by all compression wrappers.

The interface includes optional init, compressor-option parsing, free, and decompress callbacks, plus compression id, name, `alloc_buffer`, and `supported` flags.

`alloc_buffer` matters for direct page-cache decompression: streaming wrappers such as zlib/xz/zstd can request temporary buffers for missing pages.

The header also conditionally declares enabled compressor operation tables.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor_multi.c -->
# File Research: sources/os/linux/linux/fs/squashfs/decompressor_multi.c

Implements dynamic multi-stream decompression.

It maintains a mutex-protected list of available decompressor streams and can grow up to `num_online_cpus() * 2`, or a mount-limited `max_thread_num`. A wait queue blocks callers when all streams are busy.

At least one stream is allocated during create so the filesystem can operate even if later dynamic allocations fail.

Each decompression borrows one stream, calls the selected compression wrapper, returns the stream to the list, and logs corruption-style failures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor_multi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor_multi_percpu.c -->
# File Research: sources/os/linux/linux/fs/squashfs/decompressor_multi_percpu.c

Implements per-CPU decompression streams.

Create allocates one stream per possible CPU and initializes a `local_lock_t` for each. Decompression locks the current CPU’s stream, runs the selected wrapper, and unlocks.

This mode avoids central stream-list contention but preallocates per-CPU decompressor state. Its max decompressor count is `num_possible_cpus()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor_multi_percpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor_single.c -->
# File Research: sources/os/linux/linux/fs/squashfs/decompressor_single.c

Implements the traditional single-stream decompression mode.

The stream contains one compressor-specific state object and one mutex. All decompression serializes through that mutex.

This is the lowest memory/concurrency option and reports max decompressors as `1`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/decompressor_single.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/dir.c -->
# File Research: sources/os/linux/linux/fs/squashfs/dir.c

Implements directory iteration for SquashFS.

Because `.` and `..` are not stored on disk, `squashfs_readdir()` synthesizes them and offsets external `ctx->pos` by 3. It can use long-directory indexes to jump near a requested position, then reads directory headers and entries from packed metadata.

It validates directory counts, name lengths, and directory entry types before emitting entries through `dir_emit()`.

Exports `squashfs_dir_ops` with generic read/llseek, shared iteration, and lease handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/export.c -->
# File Research: sources/os/linux/linux/fs/squashfs/export.c

Provides NFS/exportfs support.

SquashFS directory entries encode inode locations directly, but filehandles use inode numbers. This file maps inode numbers to on-disk inode locations via the compressed inode lookup table and its mount-time index table.

It implements filehandle-to-dentry, filehandle-to-parent, and get-parent operations, all using `squashfs_export_iget()`.

`squashfs_read_inode_lookup_table()` reads and validates the inode lookup index table, checking ordering and metadata-block distance constraints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/file.c -->
# File Research: sources/os/linux/linux/fs/squashfs/file.c

Implements regular-file read, readahead, sparse-block handling, fragment-tail handling, and `SEEK_DATA`/`SEEK_HOLE`.

SquashFS stores per-file compressed block sizes in inode metadata. For large files, this file maintains a small meta-index cache mapping logical block indexes to block-list and data-block positions, avoiding repeated linear scans.

`read_blocklist_ptrs()` locates a block-list entry and returns compressed size plus disk position. `squashfs_read_folio()` chooses between sparse zero fill, full datablock read, or fragment-tail read.

`readahead` expands requests to SquashFS block boundaries and decompresses directly into page batches where possible. `seek_hole_data()` scans block-list entries to report sparse regions.

Exports `squashfs_aops` and `squashfs_file_operations`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/file_cache.c -->
# File Research: sources/os/linux/linux/fs/squashfs/file_cache.c

Implements the intermediate-buffer file-data read strategy.

`squashfs_readpage_block()` reads a compressed datablock through the generic data cache, then copies the decompressed buffer into page-cache folios via `squashfs_copy_cache()`.

This path favors reuse of existing cache/copy infrastructure but adds a memcpy compared with direct mode.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/file_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/file_direct.c -->
# File Research: sources/os/linux/linux/fs/squashfs/file_direct.c

Implements direct decompression into page-cache pages.

It gathers all pages covered by the SquashFS block, skipping already-uptodate pages, creates a special page actor, and calls `squashfs_read_data()` so the decompressor writes into page mappings.

On success it zeroes trailing bytes on the final file page, flushes dcache, marks pages uptodate, unlocks them, and releases non-target pages.

On failure it leaves the caller’s target folio for the caller to finish and unlocks/releases the other grabbed pages.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/file_direct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/fragment.c -->
# File Research: sources/os/linux/linux/fs/squashfs/fragment.c

Handles SquashFS fragments, which are compressed tail-end packed datablocks.

`squashfs_frag_lookup()` maps a fragment index through the fragment index table, reads the fragment entry from metadata, returns its disk block, and decodes its compressed size.

`squashfs_read_fragment_index_table()` reads and validates the mount-time fragment index table, ensuring it does not overlap later tables and points before the table start.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/fragment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/id.c -->
# File Research: sources/os/linux/linux/fs/squashfs/id.c

Maps compact on-disk uid/gid indexes to 32-bit ids.

`squashfs_get_id()` bounds-checks the index, locates the metadata block through the id index table, and reads the little-endian id.

`squashfs_read_id_index_table()` reads and validates the id table index at mount, requiring at least one id and strict monotonic metadata-block ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/id.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/inode.c -->
# File Research: sources/os/linux/linux/fs/squashfs/inode.c

Decodes on-disk SquashFS inodes into VFS inodes.

`squashfs_new_inode()` fills common uid/gid, mode, mtime/ctime/atime, and validates that the base mode does not already contain a file type. `squashfs_iget()` wraps `iget_locked()` and calls `squashfs_read_inode()` for new inodes.

`squashfs_read_inode()` handles regular, long regular, directory, long directory, symlink, device, FIFO, and socket inode formats. It wires file ops, inode ops, address-space ops, fragment metadata, directory indexes, parent inode numbers, nlink, blocks, and xattr metadata.

It validates corrupt states such as zero inode numbers, impossible fragments, negative long sizes, oversized symlinks, unknown inode types, and xattr lookup failures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/lz4_wrapper.c -->
# File Research: sources/os/linux/linux/fs/squashfs/lz4_wrapper.c

Implements the LZ4 decompressor wrapper.

It requires LZ4 compression options and validates the legacy version expected by the kernel format. The stream allocates vmalloc input and output buffers sized to the max of filesystem block size and metadata block size.

Decompression copies BIO segments into the input buffer, calls `LZ4_decompress_safe()`, then copies output pages through the page actor.

Registers compressor id `LZ4_COMPRESSION`, name `lz4`, supported, with no direct-page temporary buffer requirement.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/lz4_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/lzo_wrapper.c -->
# File Research: sources/os/linux/linux/fs/squashfs/lzo_wrapper.c

Implements the LZO decompressor wrapper.

The stream owns vmalloc input and output buffers sized for the larger of SquashFS block size and metadata size. The wrapper copies BIO data into the input buffer, calls `lzo1x_decompress_safe()`, then copies decompressed output through the page actor.

Registers compressor id `LZO_COMPRESSION`, name `lzo`, supported, with no temporary direct-page buffer requirement.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/lzo_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/namei.c -->
# File Research: sources/os/linux/linux/fs/squashfs/namei.c

Implements directory name lookup.

SquashFS directories are sorted and grouped by directory headers sharing inode start blocks. Long directories may include an index mapping names to metadata blocks; `get_dir_index_using_name()` linearly scans this index to jump near the target.

`squashfs_lookup()` validates name length, reads directory headers and entries, stops early when sorted ordering proves absence, and instantiates matching inodes with `squashfs_iget()`.

Exports `squashfs_dir_inode_ops` with lookup and xattr listing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/page_actor.c -->
# File Research: sources/os/linux/linux/fs/squashfs/page_actor.c

Implements page actors, the abstraction used by decompressor code to write output either into kmalloc buffers or directly into page-cache pages.

The cache actor simply returns sequential buffer pages. The direct actor maps page-cache pages with `kmap_local_page()` and can return a temporary buffer or `ERR_PTR(-ENOMEM)` when the requested output page is missing.

`handle_next_page()` tracks logical page indexes so holes in the gathered page array are handled without shifting decompressed output.

`squashfs_page_actor_init_special()` allocates a per-page temporary buffer only when the selected decompressor requires one.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/page_actor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/page_actor.h -->
# File Research: sources/os/linux/linux/fs/squashfs/page_actor.h

Declares `struct squashfs_page_actor` and inline wrappers for first/next/finish operations.

The actor stores either buffer pointers or page pointers, mapping state, optional temporary buffer, last page, output length, page count, current index, and decompressor buffer policy.

`squashfs_page_actor_free()` frees temporary state and returns the last completed page, or `ERR_PTR(-EIO)` if not all expected pages were consumed.

`squashfs_actor_nobuff()` disables temporary-buffer fallback for paths that require direct copying behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/page_actor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/squashfs.h -->
# File Research: sources/os/linux/linux/fs/squashfs/squashfs.h

Central internal header for SquashFS implementation declarations.

Defines trace/error/warning macros, `SQUASHFS_READ_PAGES`, the decompressor-thread-ops interface, and prototypes for block reads, caches, decompressor setup, table readers, inode/fragment/id/xattr lookup, file helpers, and exported VFS operation tables.

It connects the separately compiled strategy files and conditional decompressor threading objects to the rest of the filesystem.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/squashfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/squashfs_fs.h -->
# File Research: sources/os/linux/linux/fs/squashfs/squashfs_fs.h

Defines SquashFS on-disk format constants, helper macros, and packed little-endian structures.

Includes magic/version assumptions, metadata block size, device block size selection, max file block size, name/count limits, filesystem flags, inode types, xattr namespace ids, compression ids, compressed-size decoding, and inode/fragment/id/xattr table indexing macros.

Defines meta-index cache structures used for large-file block-list acceleration.

Declares all on-disk structures: superblock, directory index/header/entry, base and extended inode variants, fragment entries, xattr entries/values/ids, and the xattr id table.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/squashfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/squashfs_fs_i.h -->
# File Research: sources/os/linux/linux/fs/squashfs/squashfs_fs_i.h

Defines the in-memory SquashFS inode extension.

`struct squashfs_inode_info` stores common on-disk location fields, xattr metadata, parent inode number, and a union of regular-file fragment/block-list state or directory-index state, followed by the embedded VFS inode.

`squashfs_i()` converts a VFS inode pointer to the SquashFS inode wrapper via `container_of()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/squashfs_fs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/squashfs_fs_sb.h -->
# File Research: sources/os/linux/linux/fs/squashfs/squashfs_fs_sb.h

Defines in-memory SquashFS superblock and cache structures.

`struct squashfs_cache` and `struct squashfs_cache_entry` model the generic block cache, including spinlocks, wait queues, refcounts, pending/error state, buffers, and page actors.

`struct squashfs_sb_info` stores decompressor selection, device block geometry, metadata/fragment/data caches, compressed-page cache mapping, table indexes, meta-index cache, decompressor stream, table starts, format counts, error policy, threading ops, and thread limit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/squashfs_fs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/super.c -->
# File Research: sources/os/linux/linux/fs/squashfs/super.c

Implements SquashFS mount, unmount, statfs, fs context, and filesystem registration.

Mount options include `errors=continue|panic` and optional `threads=` selection/count. Defaults select the compile-time decompression mode.

`squashfs_fill_super()` sets block size, reads and validates the superblock, checks version/compressor/device bounds/block geometry/root inode/table ordering, initializes caches and decompressor stream, reads xattr/id/inode/fragment lookup tables, enables export ops when available, creates the root inode, and marks the filesystem read-only.

Unmount frees caches, page-cache mapping inode, decompressor stream, index tables, meta-index cache, and superblock private data.

Also defines inode slab allocation/free, `statfs`, show-options, fs context ops, filesystem type, module init/exit, and module metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/symlink.c -->
# File Research: sources/os/linux/linux/fs/squashfs/symlink.c

Implements symlink page reads.

SquashFS stores symlink bodies inside inode-table metadata. `squashfs_symlink_read_folio()` skips to the requested offset, then reads across metadata cache entries directly while using `kmap_local_folio()`.

It zero-fills the rest of the folio when the symlink tail is copied, flushes dcache, and completes the folio with success or error.

Exports symlink address-space ops and inode ops using `page_get_link` and SquashFS xattr listing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/xattr.c -->
# File Research: sources/os/linux/linux/fs/squashfs/xattr.c

Implements SquashFS xattr listing and get support.

`squashfs_listxattr()` walks an inode’s xattr entries from metadata, maps SquashFS xattr types to Linux handlers, enforces handler list visibility, copies visible names with namespace prefixes, and skips values.

`squashfs_xattr_get()` scans entries for a namespace/name match, handles out-of-line value references, validates buffer size, and reads the value.

Defines user, trusted, and security xattr handlers. Trusted listing requires `CAP_SYS_ADMIN`. Unknown xattr types are ignored.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/xattr.h -->
# File Research: sources/os/linux/linux/fs/squashfs/xattr.h

Declares xattr lookup helpers when `CONFIG_SQUASHFS_XATTR` is enabled.

When xattr support is disabled, provides stubs that still read enough of the on-disk xattr id table to find `xattr_table_start`, logs that xattrs will be ignored, and returns `-ENOTSUPP`.

Disabled builds define `squashfs_listxattr` and `squashfs_xattr_handlers` as `NULL`, while `squashfs_xattr_lookup()` becomes a no-op.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/xattr_id.c -->
# File Research: sources/os/linux/linux/fs/squashfs/xattr_id.c

Maps inode xattr ids to xattr data locations.

`squashfs_xattr_lookup()` bounds-checks the id, reads the xattr id entry from metadata via the xattr id index table, and returns xattr location, size, and count.

`squashfs_read_xattr_id_table()` reads the xattr id table header and index table, validates nonzero ids, exact table length, monotonic compressed metadata block pointers, and that the xattr data table precedes the first id block.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/xattr_id.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/xz_wrapper.c -->
# File Research: sources/os/linux/linux/fs/squashfs/xz_wrapper.c

Implements the XZ decompressor wrapper.

Compression options may specify dictionary size; the parser validates expected option length and dictionary-size shape, otherwise defaults to max(block size, metadata size).

The stream uses `xz_dec_init(XZ_PREALLOC, dict_size)`. Decompression resets the decoder, feeds BIO segments incrementally through `xz_dec_run()`, and writes output page-by-page via the page actor.

Registers compressor id `XZ_COMPRESSION`, name `xz`, supported, with `alloc_buffer = 1`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/xz_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/zlib_wrapper.c -->
# File Research: sources/os/linux/linux/fs/squashfs/zlib_wrapper.c

Implements the zlib decompressor wrapper.

Initialization allocates a `z_stream` and vmalloc workspace sized by `zlib_inflate_workspacesize()`. Decompression feeds BIO segments, lazily calls `zlib_inflateInit()`, advances page-actor output buffers, requires `Z_STREAM_END`, and finalizes with `zlib_inflateEnd()`.

Registers compressor id `ZLIB_COMPRESSION`, name `zlib`, supported, with `alloc_buffer = 1`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/zlib_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/squashfs/zstd_wrapper.c -->
# File Research: sources/os/linux/linux/fs/squashfs/zstd_wrapper.c

Implements the ZSTD decompressor wrapper.

The workspace stores window size, workspace size, and vmalloc memory. Window size is max(filesystem block size, metadata size), and workspace size comes from `zstd_dstream_workspace_bound()`.

Decompression initializes a zstd dstream from the workspace, streams BIO segments into it, writes output through the page actor, and treats zstd errors or premature page exhaustion as `-EIO`.

Registers compressor id `ZSTD_COMPRESSION`, name `zstd`, supported, with `alloc_buffer = 1`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/squashfs/zstd_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/stack.c -->
# File Research: sources/os/linux/linux/fs/stack.c

Provides helper exports for stackable filesystems.

`fsstack_copy_inode_size()` copies `i_size` and `i_blocks` from a lower inode to an upper inode. It accounts for 32-bit SMP/preemption constraints by taking locks only when field width requires synchronization.

`fsstack_copy_attr_all()` copies mode, uid/gid, rdev, atime/mtime/ctime, block bits, flags, and link count.

Both functions are exported GPL symbols for filesystem stacking users.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/stack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/stat.c -->
# File Research: sources/os/linux/linux/fs/stat.c

Implements VFS file-attribute query plumbing and stat-family syscalls.

Core helpers fill `struct kstat` from inodes, including idmapped uid/gid, multigrain ctime/mtime handling, VFS-enforced statx attributes, atomic-write attributes, inode version/change-cookie support, DAX/automount/mount-root flags, block-device overrides, and security checks.

Path/fd wrappers implement `vfs_getattr`, `vfs_fstat`, `vfs_fstatat`, `vfs_statx`, `do_statx`, and `do_statx_fd`, including lookup flag validation, automount/symlink behavior, stale retry, and mount id reporting.

Syscall sections translate `kstat` into old stat, new stat, stat64, statx, readlink/readlinkat, and compat layouts with overflow checks and `copy_to_user()` handling.

The tail implements inode byte accounting helpers for `i_blocks`/`i_bytes`, with locked and caller-locked variants.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/stat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/statfs.c -->
# File Research: sources/os/linux/linux/fs/statfs.c

Implements filesystem-stat query plumbing and statfs-family syscalls.

`statfs_by_dentry()` calls the filesystem `statfs` operation after LSM permission checks and fills default fragment size. `vfs_statfs()` adds mount/superblock-derived flags such as read-only, nosuid, nodev, noexec, noatime, relatime, nosymfollow, synchronous, and mandlock.

Path and fd helpers back `statfs`, `statfs64`, `fstatfs`, and `fstatfs64`, including size validation and user-copy translation with overflow checks.

Also implements legacy `ustat` by device and compat statfs/statfs64/ustat conversions under `CONFIG_COMPAT`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/statfs.c -->