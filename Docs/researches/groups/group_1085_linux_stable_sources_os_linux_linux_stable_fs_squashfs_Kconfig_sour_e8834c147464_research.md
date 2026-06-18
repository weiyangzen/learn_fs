# Group Research: group_1085_linux_stable_sources_os_linux_linux_stable_fs_squashfs_Kconfig_sour_e8834c147464

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/Kconfig

## Summary
Defines build-time and mount-time configuration for the Linux Squashfs 4.0 read-only compressed filesystem driver.

## Main Responsibilities
- Enables `CONFIG_SQUASHFS` as a block-device filesystem.
- Selects the file data read strategy: intermediate buffer cache or direct page-cache decompression.
- Selects decompressor threading mode: single, dynamically allocated multi-stream, percpu, or mount-time choice.
- Optionally enables the `threads=` mount parameter and compressed-block page-cache caching.
- Enables optional xattrs and compression backends: zlib, lz4, lzo, xz, and zstd.
- Controls default device block size and fragment-cache size for embedded systems.

## Important Behavior
`SQUASHFS_CHOICE_DECOMP_BY_MOUNT` compiles all three decompressor thread implementations and makes `threads=` accept mode names. Without it, a compile-time choice selects one implementation, while `SQUASHFS_MOUNT_DECOMP_THREADS` can still allow numeric thread counts for the multi decompressor.

`SQUASHFS_FILE_CACHE` builds the path that decompresses into an intermediate cache entry before copying to the page cache. `SQUASHFS_FILE_DIRECT` builds the path that decompresses directly into page-cache pages.

## Risks
The options are tightly coupled to the Makefile and `super.c` mount parsing. Invalid combinations would leave missing symbols for selected read or decompressor paths, so the `select` relationships are part of the functional contract.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/Makefile

## Summary
Builds the Squashfs kernel module/object and conditionally includes read-path, decompressor-thread, xattr, and compression-wrapper sources.

## Main Responsibilities
- Always links core files: block I/O, caches, directory lookup/readdir, export support, file reads, fragments, ids, inodes, name lookup, superblock, symlinks, decompressor registry, and page actors.
- Adds either `file_cache.o` or `file_direct.o` depending on the configured file decompression path.
- Adds selected decompressor threading implementations.
- Adds xattr files and selected compression wrappers based on Kconfig.

## Risks
Several core declarations in `squashfs.h` are satisfied by exactly one conditional implementation. Build correctness depends on Kconfig selecting a compatible file read path and at least one decompressor threading mode.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/block.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/block.c

## Summary
Implements low-level reads of compressed or uncompressed Squashfs metadata and data blocks from the block device, including BIO construction, optional compressed-page caching, metadata length decoding, and dispatch to the selected decompressor.

## Key APIs
- `squashfs_read_data()`: reads one metadata block or file data block and fills a `squashfs_page_actor`.

## Important Behavior
Metadata blocks have a two-byte on-disk length header; file data block lengths are supplied from inode block lists. Both encodings use a high bit to mark uncompressed storage.

`squashfs_bio_read()` rounds requested byte ranges to the device block size, allocates one BIO page per covered page, reuses uptodate pages from `msblk->cache_mapping` when available, and returns the intra-device-block offset.

When the device block size is one page, `squashfs_bio_read_cached()` can cache boundary pages that were fetched only because an unaligned compressed block shared them with adjacent data. With `CONFIG_SQUASHFS_COMP_CACHE_FULL`, it attempts to cache all fetched compressed pages.

Compressed blocks call `msblk->thread_ops->decompress()`. Uncompressed blocks copy bytes directly from the BIO into the page actor.

## Risks
Bounds checks against `msblk->bytes_used` are critical because the source length comes from on-disk metadata. The compressed-page cache path manipulates folios carried in BIOs; failure handling must avoid leaking pages or leaving unlocked folios in the cache mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/cache.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/cache.c

## Summary
Provides the shared cache implementation for Squashfs metadata blocks, fragment blocks, and the intermediate data-block read cache used by `CONFIG_SQUASHFS_FILE_CACHE`.

## Key APIs
- `squashfs_cache_init()`, `squashfs_cache_delete()`.
- `squashfs_cache_get()`, `squashfs_cache_put()`.
- `squashfs_copy_data()`.
- `squashfs_read_metadata()`.
- `squashfs_get_fragment()`, `squashfs_get_datablock()`.
- `squashfs_read_table()`.

## Important Behavior
Each cache entry is a set of page-sized kmalloc buffers plus a page actor. `squashfs_cache_get()` searches round-robin, waits if all entries are in use, marks a newly selected entry pending, reads/decompresses it with `squashfs_read_data()`, and wakes waiters.

`squashfs_read_metadata()` reads arbitrary metadata byte ranges from packed metadata blocks, crossing block boundaries by following `entry->next_index`.

`squashfs_read_table()` reads an uncompressed on-disk table into a linear kmalloc buffer by building a page actor over the table buffer.

## Synchronization
The cache uses a spinlock for entry state, wait queues for whole-cache and per-entry contention, entry refcounts to prevent eviction, and a pending flag so concurrent users wait for a fill in progress.

## Risks
The cache assumes metadata and fragments fit into the configured block-size/page-array layout. Callers must release every entry with `squashfs_cache_put()`, including error entries, or cache capacity can be exhausted.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor.c

## Summary
Implements the Squashfs decompressor registry and decompressor setup path.

## Key APIs
- `squashfs_lookup_decompressor()`.
- `squashfs_decompressor_setup()`.

## Important Behavior
The registry always contains entries for zlib, lz4, lzo, xz, lzma, zstd, and unknown compression. Unsupported compiled-out algorithms are represented by stubs with `supported = 0`; lzma is always unsupported.

`get_comp_opts()` reads optional compressor-specific options from immediately after the superblock when the filesystem flags indicate they exist. It passes the raw option block to the selected decompressor's `comp_opts` callback.

`squashfs_decompressor_setup()` obtains compressor options and delegates stream creation to the selected decompressor thread-ops implementation.

## Risks
The raw options block is read through normal Squashfs metadata/block I/O before the main stream exists; this path depends on uncompressed option block handling and early superblock `bytes_used` initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor.h -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor.h

## Summary
Defines the per-compression-algorithm operations table used by Squashfs decompressor wrappers.

## Main Contents
- `struct squashfs_decompressor`.
- Inline `squashfs_comp_opts()`.
- Conditional extern declarations for compiled compression backends.

## Important Details
Each backend can provide `init`, `comp_opts`, `free`, and `decompress`. `alloc_buffer` tells the direct page actor whether missing page-cache pages can be handled with a temporary buffer. `supported` distinguishes usable backends from registry stubs.

## Risks
Backend wrappers and thread implementations share this ABI. The `decompress` function receives the algorithm-private stream selected by the thread implementation, not the global `msblk->stream`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor_multi.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor_multi.c

## Summary
Implements the dynamically allocated multi-stream decompressor threading mode.

## Key APIs
- Exports `squashfs_decompressor_multi`.

## Important Behavior
The mode creates one default decompressor stream at mount time, then allocates additional streams on demand up to `msblk->max_thread_num`, whose maximum is `num_online_cpus() * 2`.

Available streams live on `strm_list`. `get_decomp_stream()` removes one, allocates a new one if allowed, or waits for an existing stream to be returned. `put_decomp_stream()` requeues the stream and wakes a waiter.

## Synchronization
Uses a mutex to protect the stream list and stream count, plus a wait queue for callers blocked by the stream limit or allocation failure.

## Risks
Mount-time setup retains `comp_opts` in the stream object because later dynamic stream allocations need the same options. Destroy assumes no decompressions are still active and frees all idle streams and the retained options.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor_multi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor_multi_percpu.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor_multi_percpu.c

## Summary
Implements the percpu decompressor threading mode, with one decompressor stream per possible CPU.

## Key APIs
- Exports `squashfs_decompressor_percpu`.

## Important Behavior
Mount setup allocates a percpu `squashfs_stream` array and initializes one backend stream for each possible CPU. Decompression uses `local_lock()` and `this_cpu_ptr()` so each CPU serializes access to its local backend stream.

`max_decompressors()` reports `num_possible_cpus()`.

## Risks
Allocation cost scales with possible CPUs, not online CPUs. The cast between percpu pointer and `void *` in `msblk->stream` is deliberate and must be reversed consistently in destroy/decompress paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor_multi_percpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor_single.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor_single.c

## Summary
Implements the single-stream decompressor threading mode.

## Key APIs
- Exports `squashfs_decompressor_single`.

## Important Behavior
Mount setup creates one backend decompressor stream and frees compressor options after initialization. Every decompression takes a mutex around the shared stream, so only one block can be decompressed at a time.

`max_decompressors()` returns 1.

## Risks
This mode is memory efficient but serializes metadata, fragment, and file-data decompression across the filesystem instance.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/decompressor_single.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/dir.c

## Summary
Implements `readdir` for Squashfs directories over packed, compressed directory metadata.

## Key APIs
- `squashfs_dir_ops`.

## Important Behavior
Squashfs does not store `.` and `..` directory entries, so `squashfs_readdir()` synthesizes them and offsets external `ctx->pos` by 3 relative to on-disk directory positions.

For indexed long directories, `get_dir_index_using_offset()` scans directory index entries to find the metadata block nearest the requested `f_pos`. Index failures are tolerated because the index is an optimization.

The main loop reads directory headers and entries, validates counts, name lengths, and directory entry types, computes inode numbers from the header base plus entry delta, and emits VFS dirents.

## Risks
Malformed directory metadata is handled as a read failure and stops iteration. Correct `ctx->pos` translation is important because seeking in directories depends on stable external offsets that include synthetic entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/export.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/export.c

## Summary
Implements NFS/exportfs support for Squashfs using the inode lookup table.

## Key APIs
- `squashfs_read_inode_lookup_table()`.
- `squashfs_export_ops`.

## Important Behavior
Normal directory operations encode inode disk locations directly in directory entries. Exportfs filehandles only carry inode numbers, so `squashfs_inode_lookup()` maps inode numbers to encoded on-disk inode locations through the compressed inode lookup table.

The lookup-table index is read at mount time. `squashfs_read_inode_lookup_table()` verifies the table size matches its table boundaries and that each compressed lookup-block pointer is monotonic and close enough to the next boundary.

`fh_to_dentry`, `fh_to_parent`, and `get_parent` obtain aliases through `squashfs_iget()`.

## Risks
Export support is only installed when the image has a lookup table. Bad table geometry disables mount rather than allowing stale or out-of-range filehandle resolution.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/file.c

## Summary
Implements regular-file reading, large-file block-list indexing, readahead, sparse block handling, fragment tails, and `SEEK_DATA`/`SEEK_HOLE` for Squashfs.

## Key APIs
- `squashfs_copy_cache()`.
- `squashfs_aops`.
- `squashfs_file_operations`.

## Important Behavior
Regular files are represented by a block list of compressed-size entries plus an optional fragment tail. `read_blocklist_ptrs()` maps a logical block index to the on-disk compressed block and size. A zero block size means a sparse hole.

Large files use an in-memory meta-index cache with 8 slots. `fill_meta_index()` stores coarse mappings from logical block ranges to block-list metadata positions and data-block offsets, reducing repeated scans of long block lists.

`squashfs_read_folio()` chooses between sparse zero-fill, separately compressed data block, or fragment tail. `squashfs_copy_cache()` copies one decompressed Squashfs data block into every page-cache folio it covers and marks each folio uptodate only when the expected bytes were copied.

`squashfs_readahead()` expands readahead to Squashfs block boundaries, batches page-cache pages, and decompresses either a full data block or a fragment directly into the page actor.

`seek_hole_data()` scans block-list entries and treats sparse zero-length blocks as holes, nonzero blocks as data, and fragment tails as data with an implicit hole at EOF.

## Synchronization
The meta-index cache uses `msblk->meta_index_mutex` and per-slot `locked` flags so a slot is not reused while a reader is extending or consuming it.

## Risks
The block-list and meta-index code is sensitive to corrupted size entries and integer scaling between page indexes, Squashfs block indexes, and metadata offsets. Readahead must unlock and put every page on every path.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/file_cache.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/file_cache.c

## Summary
Provides the file data read implementation for `CONFIG_SQUASHFS_FILE_CACHE`.

## Key APIs
- `squashfs_readpage_block()`.

## Important Behavior
Reads a compressed data block through `squashfs_get_datablock()`, which uses the generic Squashfs cache as an intermediate decompression buffer, then calls `squashfs_copy_cache()` to copy bytes into page-cache folios.

## Risks
This path adds an extra copy but avoids direct decompression into page-cache pages. Cache entry lifetime is simple but still requires `squashfs_cache_put()` after copy/error handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/file_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/file_direct.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/file_direct.c

## Summary
Provides the file data read implementation for `CONFIG_SQUASHFS_FILE_DIRECT`.

## Key APIs
- `squashfs_readpage_block()`.

## Important Behavior
Computes the page-cache range covered by the Squashfs block, tries to lock/grab all pages in that range, builds a direct page actor, and calls `squashfs_read_data()` so the decompressor writes directly into page-cache pages.

On success, it zeroes the tail of the last file page when needed, flushes dcache, marks pages uptodate, unlocks them, and releases all non-target pages. On decompression failure, non-target pages are unlocked and released while the caller handles the target folio.

## Risks
Direct decompression must cope with missing or already-uptodate pages. `page_actor` and backend `alloc_buffer` behavior determine whether missing pages are skipped safely or fail the read.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/file_direct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/fragment.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/fragment.c

## Summary
Handles Squashfs fragment table lookup for tail-end packed file blocks.

## Key APIs
- `squashfs_frag_lookup()`.
- `squashfs_read_fragment_index_table()`.

## Important Behavior
`squashfs_frag_lookup()` maps a fragment number to its compressed fragment block start and compressed size by reading a fragment entry from the compressed fragment table via the mount-cached fragment index.

`squashfs_read_fragment_index_table()` reads the uncompressed fragment-index table and validates that it does not overlap the next table and that the first fragment metadata block precedes the index table.

## Risks
Fragment indices are used by inode parsing and file tail reads. A bad fragment table can otherwise redirect reads to invalid compressed blocks, so mount-time bounds checks are important.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/fragment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/id.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/id.c

## Summary
Maps compact on-disk uid/gid indices to 32-bit ids using the Squashfs id lookup table.

## Key APIs
- `squashfs_get_id()`.
- `squashfs_read_id_index_table()`.

## Important Behavior
Inodes store uid and gid table indices. `squashfs_get_id()` validates the index, reads the selected 32-bit id from compressed metadata, and returns the host-endian value.

The id index table is read at mount time. Its computed size must exactly match table boundaries, and each compressed id-block pointer must be monotonic and within one metadata block plus header slack of the next boundary.

## Risks
Every inode read depends on this table. Corrupt id geometry is treated as a mount failure, while out-of-range inode uid/gid indices fail individual inode reads.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/id.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/inode.c

## Summary
Reads Squashfs on-disk inodes from compressed metadata and initializes VFS inode objects for every supported inode type.

## Key APIs
- `squashfs_iget()`.
- `squashfs_read_inode()`.
- `squashfs_inode_ops`.

## Important Behavior
Squashfs inode identifiers encode a metadata block and offset. `squashfs_iget()` uses the on-disk inode number as the VFS inode cache key and fills new inodes via `squashfs_read_inode()`.

`squashfs_new_inode()` populates common mode, uid/gid, mtime/atime/ctime, inode number, and validates that the base mode does not already contain a file type.

The main switch handles regular and long regular files, directories and long directories, symlinks and long symlinks, devices, fifos, and sockets. It sets file operations, inode operations, address-space operations, sizes, nlinks, block counts, fragment metadata, block-list start, directory index metadata, parent inode, and special device numbers.

Extended inode forms can carry xattr ids. If xattrs are enabled and an xattr id table exists, `squashfs_xattr_lookup()` fills inode-private xattr location/count/size and charges xattr bytes to `i_blocks`.

## Risks
The parser relies on exact on-disk type-specific structure sizes and offsets. It validates fragment/file-size consistency and symlink size, but bad metadata can still fail reads deep in table lookups.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/lz4_wrapper.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/lz4_wrapper.c

## Summary
Implements the Squashfs LZ4 decompressor backend.

## Key APIs
- Exports `squashfs_lz4_comp_ops`.

## Important Behavior
LZ4 filesystems must carry compression options, and the wrapper accepts only the legacy LZ4 format version. Initialization allocates vmalloc input and output buffers sized to the maximum of filesystem block size and metadata block size.

Decompression copies compressed BIO segments into the input buffer, calls `LZ4_decompress_safe()`, then copies decompressed bytes from the output buffer into the page actor.

## Risks
The wrapper does not stream directly from BIO to actor; it depends on full-size input/output buffers. The legacy option validation is required for format compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/lz4_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/lzo_wrapper.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/lzo_wrapper.c

## Summary
Implements the Squashfs LZO decompressor backend.

## Key APIs
- Exports `squashfs_lzo_comp_ops`.

## Important Behavior
Initialization allocates vmalloc input and output buffers sized to the maximum of filesystem block size and metadata block size. Decompression copies compressed BIO data into the input buffer, calls `lzo1x_decompress_safe()`, and copies the resulting output into the page actor.

## Risks
Like LZ4, LZO uses full intermediate buffers and reports all backend failures as `-EIO`. It does not provide a compressor-options parser.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/lzo_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/namei.c

## Summary
Implements filename lookup in Squashfs directories.

## Key APIs
- `squashfs_dir_inode_ops`.

## Important Behavior
Directories are sorted and organized as headers plus entries sharing a common inode start block. Long directories can have an index that maps names to metadata blocks. `get_dir_index_using_name()` scans that index to find the first indexed name greater than the target and starts the main lookup near that block.

`squashfs_lookup()` validates name length, reads directory headers and entries, stops early when the first character has passed the target in sorted order, and calls `squashfs_iget()` for a matching entry. The inode identifier combines the header start block with the entry offset; the displayed inode number combines the header base with the signed entry delta.

## Risks
The directory index is an optimization and lookup continues if index reading fails. Sorted-order early exit depends on valid image ordering; malformed images are primarily caught by size/count validation and read failures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/page_actor.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/page_actor.c

## Summary
Implements Squashfs page actors, the abstraction used by block reads and decompressors to write output either to intermediate buffers or directly to page-cache pages.

## Key APIs
- `squashfs_page_actor_init()`.
- `squashfs_page_actor_init_special()`.

## Important Behavior
The cache actor returns a caller-provided array of buffers and has no finish work. The direct actor returns kmapped page-cache pages in index order. When the next expected page is missing, it either returns a temporary buffer if the decompressor requires one, or an error pointer.

The direct actor tracks `next_index`, `returned_pages`, `last_page`, and the current kmap address. Finish unmaps any outstanding page.

## Risks
Callers must not sleep between `squashfs_first_page()` and `squashfs_finish_page()` because direct actors may hold local kmaps. The actor-free path reports an error if not all supplied pages were consumed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/page_actor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/page_actor.h -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/page_actor.h

## Summary
Declares `struct squashfs_page_actor` and inline helpers for actor use and teardown.

## Main Contents
- Buffer/page union for intermediate and direct output modes.
- Function pointers for first/next/finish page operations.
- State fields for direct page-cache iteration and temporary buffers.
- Inline wrappers `squashfs_first_page()`, `squashfs_next_page()`, `squashfs_finish_page()`, and `squashfs_actor_nobuff()`.

## Important Details
`squashfs_page_actor_free()` returns the last page if every supplied page was consumed, otherwise `ERR_PTR(-EIO)`. This return value is used by direct read and readahead paths to decide whether decompression filled a complete page set.

## Risks
The actor structure is shared with all compression wrappers. Backend code must honor `ERR_PTR`, `NULL`, and normal page-buffer returns from the page iteration helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/page_actor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/squashfs.h -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/squashfs.h

## Summary
Central internal Squashfs header declaring cross-file APIs, operations tables, trace/error macros, and decompressor-thread operations.

## Main Contents
- Logging macros `TRACE`, `ERROR`, and `WARNING`.
- `SQUASHFS_READ_PAGES` build-time behavior for the intermediate data cache.
- Prototypes for block I/O, caches, decompressor setup, export, fragments, file reads, ids, inodes, xattrs, directories, symlinks, and operations tables.
- `struct squashfs_decompressor_thread_ops`.

## Important Details
This header is the link point between conditional files selected by the Makefile. `squashfs_readpage_block()` is provided by either `file_cache.c` or `file_direct.c`, and decompressor thread ops are provided according to Kconfig.

## Risks
Because this is the shared internal ABI, signature changes require coordinated edits across many Squashfs files and compression wrappers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/squashfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs.h

## Summary
Defines Squashfs on-disk constants, encoding helpers, metadata/table macros, meta-index structures, compression ids, and all on-disk structure layouts.

## Main Contents
- Filesystem version, metadata size, max block/file/name sizes, invalid sentinels, and flags.
- Compression and uncompressed-block encoding macros.
- Inode-number, fragment, inode lookup, id, and xattr table offset macros.
- Meta-index cache constants and structures.
- On-disk little-endian superblock, inode variants, directory entries, fragments, and xattr structures.

## Important Behavior
`squashfs_block_size()` rejects block-list values with high reserved bits set. Table macros convert logical indices into metadata block numbers and offsets for packed compressed tables.

Inode variants are optimized by type and size: short and long forms exist for regular files, directories, symlinks, devices, and IPC nodes when larger values or xattrs are required.

## Risks
This header is the exact on-disk format contract. Any interpretation bug propagates into mount validation, inode parsing, directory lookup, xattr handling, and export filehandle lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs_i.h -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs_i.h

## Summary
Defines Squashfs per-inode private state and the `squashfs_i()` container helper.

## Main Contents
- Shared fields: start block, metadata offset, xattr location/size/count, parent inode.
- Regular-file fields: fragment block/size/offset and block-list start.
- Directory fields: directory index start/offset/count.
- Embedded `struct inode vfs_inode`.

## Risks
The regular-file and directory-specific fields share a union. Callers must only interpret the union according to inode type initialized by `inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs_sb.h -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs_sb.h

## Summary
Defines Squashfs in-memory superblock state, generic cache structures, and cache-entry state.

## Main Contents
- `struct squashfs_cache` and `struct squashfs_cache_entry`.
- `struct squashfs_sb_info`.

## Important Details
`squashfs_sb_info` owns decompressor selection, device block size, metadata/fragment/data caches, optional compressed-page cache mapping, id/fragment/xattr/inode lookup tables, the large-file meta-index cache, decompressor stream state, table starts, counts, error policy, decompressor thread ops, and max decompressor count.

Cache entries carry block identity, decompressed length, refcount, next metadata index, pending/error state, wait queue, data pages, and page actor.

## Risks
This is the central mount lifetime object. `super.c` cleanup paths must free every optional pointer consistently after partial mount failures and normal unmount.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/super.c

## Summary
Implements Squashfs mount parsing, superblock validation, in-memory setup, unmount cleanup, statfs, inode-cache allocation, and filesystem registration.

## Key APIs
- Filesystem type `squashfs_fs_type`.
- Super operations `squashfs_super_ops`.
- Mount context operations for get-tree, parse-param, reconfigure, and free.

## Important Behavior
Mount options support `errors=continue|panic` and, when configured, `threads=` by name or numeric count. Default decompressor thread ops are chosen from Kconfig.

`squashfs_fill_super()` sets the device block size, reads the superblock with a temporary `bytes_used`, checks magic, version, compression support, filesystem size against the block device, block size/log consistency, page-size compatibility, and root inode offset.

It allocates metadata and data caches, optional compressed-page cache mapping when device blocks are page-sized, decompressor stream state, xattr id tables, id tables, inode lookup table/export ops, fragment cache/index, then validates table ordering before reading and installing the root inode.

The filesystem is always mounted read-only. `squashfs_statfs()` reports compressed-image block usage, inode count, no free blocks/inodes, max name length, and an fsid derived from the block device.

## Cleanup and Lifetime
Partial mount failure and `squashfs_put_super()` delete caches, drop the optional cache inode, destroy decompressor streams, free table arrays and meta-index state, and free `s_fs_info`. The module owns a slab cache for `squashfs_inode_info`.

## Risks
Mount ordering matters because later table boundaries are derived from earlier optional tables. The cleanup path must tolerate partially initialized state. The filesystem type advertises `FS_ALLOW_IDMAP`, while inode uid/gid mapping is still performed by VFS stat helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/symlink.c

## Summary
Implements page-cache reading for Squashfs symlink bodies stored inline in inode-table metadata.

## Key APIs
- `squashfs_symlink_aops`.
- `squashfs_symlink_inode_ops`.

## Important Behavior
The symlink read path skips to the requested folio offset in metadata, then reads one or more metadata cache entries directly with `squashfs_cache_get()` and copies into a locally mapped folio. It avoids `squashfs_read_metadata()` for the copy loop because that helper can sleep while the folio is kmapped.

The final partial page is zero-filled, dcache is flushed, and the folio is completed through `folio_end_read()`.

## Risks
The path must balance cache puts on every error and avoid sleeping while using `kmap_local_folio()`. Inode parsing limits symlink size to at most one page, simplifying the address-space behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/xattr.c

## Summary
Implements read-only VFS xattr listing and lookup for Squashfs user, trusted, and security namespaces.

## Key APIs
- `squashfs_listxattr()`.
- `squashfs_xattr_handlers`.

## Important Behavior
`squashfs_listxattr()` walks the inode's xattr entries, maps Squashfs xattr types to VFS handlers, applies handler list permissions, emits namespace prefixes plus names, and skips values.

`squashfs_xattr_get()` scans names for the requested namespace/name pair. If an entry has `SQUASHFS_XATTR_VALUE_OOL`, it follows an out-of-line xattr value reference before reading the value size and optional value bytes.

Trusted xattrs are listable only to `CAP_SYS_ADMIN`. Unknown xattr types are ignored.

## Risks
The code allocates a name-sized target buffer even for zero-length names and repeatedly advances metadata cursors through variable-length records. Size checks for caller buffers produce `-ERANGE`, while corrupt metadata read errors propagate from `squashfs_read_metadata()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/xattr.h

## Summary
Declares xattr table and lookup helpers, with stub implementations when Squashfs xattr support is not compiled in.

## Main Contents
- Real extern declarations under `CONFIG_SQUASHFS_XATTR`.
- Stub `squashfs_read_xattr_id_table()` that reads the xattr table header enough to find the next table, logs that xattrs are ignored, and returns `-ENOTSUPP`.
- Stub `squashfs_xattr_lookup()` returning success without xattr data.
- Macro definitions that disable listxattr and xattr handlers.

## Risks
The no-xattr stub is still part of mount table ordering: it must return `xattr_table_start` so `super.c` can continue locating the id table even though xattrs are ignored.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/xattr_id.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/xattr_id.c

## Summary
Maps Squashfs inode xattr ids to on-disk xattr record locations, sizes, and counts.

## Key APIs
- `squashfs_xattr_lookup()`.
- `squashfs_read_xattr_id_table()`.

## Important Behavior
`squashfs_xattr_lookup()` validates the xattr id, reads the corresponding `squashfs_xattr_id` record from compressed metadata, and returns the xattr table offset, total size, and entry count.

`squashfs_read_xattr_id_table()` reads the xattr id table header, stores the xattr table start and id count, verifies nonzero ids and exact index-table length, reads the index table, checks monotonic compressed-block pointers, and verifies the xattr table precedes the first xattr-id block.

## Risks
The xattr id table sits at the end of the image, so size and ordering checks protect both xattr lookup and the mount-time discovery of earlier tables.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/xattr_id.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/xz_wrapper.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/xz_wrapper.c

## Summary
Implements the Squashfs XZ decompressor backend.

## Key APIs
- Exports `squashfs_xz_comp_ops`.

## Important Behavior
The optional XZ compressor options carry dictionary size. The parser validates the option length and accepts dictionary sizes of the supported XZ forms; without options it defaults to max(filesystem block size, metadata block size).

Initialization preallocates an XZ decoder with the selected dictionary size. Decompression streams input directly from BIO segments into `xz_dec_run()` and streams output through the page actor.

`alloc_buffer = 1`, so direct actors can provide a temporary page buffer when a page-cache target is absent.

## Risks
The decompressor requires `XZ_STREAM_END`; running out of BIO input early is treated as corruption. Dictionary validation is necessary to avoid invalid preallocation sizes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/xz_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/zlib_wrapper.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/zlib_wrapper.c

## Summary
Implements the Squashfs zlib decompressor backend.

## Key APIs
- Exports `squashfs_zlib_comp_ops`.

## Important Behavior
Initialization allocates a `z_stream` and vmalloc zlib inflate workspace. Decompression lazily calls `zlib_inflateInit()`, feeds BIO segments as input, writes output through the page actor, and calls `zlib_inflateEnd()` before returning `total_out`.

`alloc_buffer = 1`, enabling temporary direct-actor output for missing page-cache pages.

## Risks
The wrapper must reach `Z_STREAM_END`; otherwise it reports `-EIO`. The inflate stream state is reused by the selected decompressor thread implementation, so callers must serialize per-stream use.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/zlib_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/zstd_wrapper.c -->
# File Research: sources/os/linux/linux-stable/fs/squashfs/zstd_wrapper.c

## Summary
Implements the Squashfs Zstandard decompressor backend.

## Key APIs
- Exports `squashfs_zstd_comp_ops`.

## Important Behavior
Initialization allocates a workspace sized by `zstd_dstream_workspace_bound()` for a window of max(filesystem block size, metadata block size). Decompression initializes a zstd stream from that workspace, feeds BIO segments through `zstd_decompress_stream()`, and emits output through the page actor.

`alloc_buffer = 1`, so direct page-cache reads can tolerate missing page targets through temporary output buffers.

## Risks
The wrapper treats zstd stream errors and unexpected lack of output pages as `-EIO`. Workspace sizing depends on the image block size accepted at mount time.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/squashfs/zstd_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/stack.c -->
# File Research: sources/os/linux/linux-stable/fs/stack.c

## Summary
Provides helper functions for stackable filesystems to copy inode size/block accounting and inode attributes from lower to upper inodes.

## Key APIs
- `fsstack_copy_inode_size()`.
- `fsstack_copy_attr_all()`.

## Important Behavior
`fsstack_copy_inode_size()` reads `i_size` with `i_size_read()` and copies `i_blocks`, using `src->i_lock` on 32-bit-sized block counters and `dst->i_lock` when required to keep 64-bit `i_size` and/or `i_blocks` updates safe on 32-bit or preemptible/SMP systems.

`fsstack_copy_attr_all()` copies mode, uid/gid, rdev, atime/mtime/ctime, block bits, inode flags, and nlink.

## Risks
The helpers deliberately do not require `i_rwsem`. They avoid guaranteeing atomic consistency between `i_size` and `i_blocks`, which is acceptable for stackable filesystem attribute mirroring but not for quota-style accounting invariants.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/stack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/stat.c -->
# File Research: sources/os/linux/linux-stable/fs/stat.c

## Summary
Implements VFS file metadata retrieval, stat/statx/readlink syscalls, kernel-to-userspace stat structure conversions, compat variants, and inode block-byte accounting helpers.

## Key APIs
- `fill_mg_cmtime()`.
- `generic_fillattr()`, `generic_fill_statx_attr()`, `generic_fill_statx_atomic_writes()`.
- `vfs_getattr_nosec()`, `vfs_getattr()`, `vfs_fstat()`, `vfs_fstatat()`.
- `do_statx()`, `do_statx_fd()`.
- Inode byte accounting helpers: `inode_add_bytes()`, `inode_sub_bytes()`, `inode_get_bytes()`, `inode_set_bytes()`.

## Important Behavior
`generic_fillattr()` fills `struct kstat` from an inode, applying mount idmapping to uid/gid, mgtime handling when enabled, block size/count, and optional i_version change cookies.

`vfs_getattr_nosec()` initializes result masks, sets automount/DAX attributes, calls filesystem `getattr` or `generic_fillattr()`, and lets block device inodes override relevant statx fields through `bdev_statx()`. `vfs_getattr()` adds the LSM `security_inode_getattr()` check.

Path and fd helpers add mount ids, unique mount ids when requested, and mount-root attributes. Filename lookups handle symlink/no-automount flags, `AT_EMPTY_PATH`, and ESTALE retry with `LOOKUP_REVAL`.

The syscall conversion helpers support old stat, new stat, stat64, statx, and compat structures with overflow checks for device numbers, inode numbers, nlink, file sizes, block counts, and block sizes. `readlinkat` performs path lookup without following symlinks, checks LSM readlink permission, touches atime, and calls `vfs_readlink()`.

## Risks
This file is ABI-sensitive. Conversion helpers must preserve historical structure layouts and overflow semantics across architectures. `STATX_CHANGE_COOKIE` and `STATX_ATTR_CHANGE_MONOTONIC` are kept kernel-only by masking them before copying to userspace.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/stat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/statfs.c -->
# File Research: sources/os/linux/linux-stable/fs/statfs.c

## Summary
Implements VFS filesystem-stat retrieval and the `statfs`, `fstatfs`, `statfs64`, `fstatfs64`, and `ustat` syscall families, including compat variants.

## Key APIs
- `vfs_get_fsid()`.
- `vfs_statfs()`.
- `user_statfs()`.
- `fd_statfs()`.

## Important Behavior
`statfs_by_dentry()` zeroes a `kstatfs`, performs `security_sb_statfs()`, calls the filesystem `statfs` super operation, and defaults `f_frsize` to `f_bsize` when the filesystem leaves it unset.

`vfs_statfs()` adds `f_flags` derived from mount flags and superblock flags. Path-based lookup follows symlinks and automounts, retrying with revalidation on ESTALE. FD-based lookup stats the file path.

Native and 64-bit copy helpers convert `kstatfs` to user ABI structures and perform overflow checks for 32-bit-sized fields. `ustat` locates a superblock by device and returns legacy free block/inode counts. Compat syscall handlers mirror the native logic into compat structures.

## Risks
Like `stat.c`, this file is syscall ABI-sensitive. Overflow behavior and compat layout handling must remain consistent with architecture expectations, and all user copies must return `-EFAULT` on failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/statfs.c -->