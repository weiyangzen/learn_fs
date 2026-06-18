# subset-b-005767 Research

Grouped source research for the SquashFS implementation under `sources/distributed-fs/ceph-client/fs/squashfs` plus the VFS stacking, stat, and statfs helpers in `sources/distributed-fs/ceph-client/fs`. Each source file has a separate marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/squashfs/Kconfig

## Purpose

This Kconfig file defines the kernel configuration surface for SquashFS 4.0, a compressed read-only block-backed filesystem. It enables the core `SQUASHFS` tristate, chooses the file data decompression strategy, chooses or compiles decompressor threading modes, selects optional xattr and compression backends, and exposes performance/memory tuning options such as 4 KiB device block size and fragment cache size.

## Important APIs, Types, and Functions

There are no C APIs here; the important symbols are `SQUASHFS`, `SQUASHFS_FILE_CACHE`, `SQUASHFS_FILE_DIRECT`, `SQUASHFS_DECOMP_SINGLE`, `SQUASHFS_DECOMP_MULTI`, `SQUASHFS_DECOMP_MULTI_PERCPU`, `SQUASHFS_CHOICE_DECOMP_BY_MOUNT`, `SQUASHFS_MOUNT_DECOMP_THREADS`, `SQUASHFS_XATTR`, `SQUASHFS_COMP_CACHE_FULL`, compression backend symbols (`SQUASHFS_ZLIB`, `SQUASHFS_LZ4`, `SQUASHFS_LZO`, `SQUASHFS_XZ`, `SQUASHFS_ZSTD`), `SQUASHFS_4K_DEVBLK_SIZE`, `SQUASHFS_EMBEDDED`, and `SQUASHFS_FRAGMENT_CACHE_SIZE`.

## Control Flow

The file controls build-time inclusion and mount-time behavior indirectly. The file decompression choice selects either `file_cache.o` or `file_direct.o`; threading choices select one or more `decompressor_*` implementations; compression symbols select wrappers and library dependencies. `threads=` parsing in `super.c` is only available when the relevant mount-choice symbols are enabled.

## State and Persistence Behavior

Kconfig choices become compiled kernel configuration, not runtime state. Persistent effects are the module contents, available compression formats, maximum mount parameter flexibility, and cache/thread behavior for all mounted SquashFS images built with this kernel.

## Dependencies and Integration Points

`SQUASHFS` depends on `BLOCK`. Compression symbols select kernel decompression libraries. `SQUASHFS_XATTR` gates `xattr.o` and `xattr_id.o`. `SQUASHFS_FRAGMENT_CACHE_SIZE` is consumed through `squashfs_fs.h` and `super.c`.

## Risks and Edge Cases

Misconfigured compression support makes valid images unmountable. Thread and direct-decompression choices trade memory footprint, latency, and lock contention. `SQUASHFS_COMP_CACHE_FULL` improves repeated compressed-block reads but expands page-cache pressure. Fragment cache values that are too small cause repeated decompression; too large wastes memory on embedded builds.

## Test Signals

Useful signals include allmodconfig/allyesconfig build coverage, boot/mount tests for each compression format, mount tests for `threads=single`, `threads=multi`, `threads=percpu`, numeric thread counts where enabled, and repeated-read benchmarks with `SQUASHFS_COMP_CACHE_FULL` both disabled and enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/squashfs/Makefile

## Purpose

This Makefile wires the SquashFS source files into the kernel build. It always builds the core object set for `CONFIG_SQUASHFS` and conditionally appends file-data, decompressor-thread, xattr, and compression-wrapper objects according to Kconfig.

## Important APIs, Types, and Functions

The important build targets are `obj-$(CONFIG_SQUASHFS) += squashfs.o` and `squashfs-y` component lists. Core objects are `block.o`, `cache.o`, `dir.o`, `export.o`, `file.o`, `fragment.o`, `id.o`, `inode.o`, `namei.o`, `super.o`, `symlink.o`, `decompressor.o`, and `page_actor.o`.

## Control Flow

Build flow follows Kbuild aggregation: `squashfs.o` is linked from the unconditional object list plus conditionally selected objects. Exactly one file read implementation is expected from the file decompression choice; one or more thread implementations may be linked when mount-time choice is enabled.

## State and Persistence Behavior

No runtime state is owned here. The Makefile defines which symbols and object implementations are present in the final module or built-in kernel image.

## Dependencies and Integration Points

It depends on the Kconfig symbols in this directory. It integrates with kernel Kbuild and the exported symbols expected by `super.c`, `decompressor.c`, and `squashfs.h`.

## Risks and Edge Cases

Missing an object for a selected Kconfig symbol produces unresolved symbols, especially for compression wrappers or thread ops referenced by `super.c` and `decompressor.c`. Accidentally linking multiple file data strategies with the same `squashfs_readpage_block` symbol would conflict, so the Kconfig choice must remain exclusive.

## Test Signals

Build matrix coverage across compression backends, xattr on/off, file cache/direct choices, and each decompressor mode is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/block.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/block.c

## Purpose

`block.c` implements the low-level SquashFS read path for metadata and data blocks. It reads packed, possibly unaligned compressed blocks from the block device into BIO pages, optionally reuses compressed pages through an internal cache mapping, and either copies uncompressed data into a `squashfs_page_actor` or dispatches compressed input to the selected decompressor thread ops.

## Important APIs, Types, and Functions

The exported API is `squashfs_read_data()`. Internal helpers are `copy_bio_to_actor()`, `squashfs_bio_read_cached()`, `squashfs_get_cache_page()`, and `squashfs_bio_read()`. It depends on `struct squashfs_sb_info`, `struct bio`, `struct address_space`, and `struct squashfs_page_actor`.

## Control Flow

`squashfs_read_data()` distinguishes data blocks from metadata blocks by whether `length` is nonzero. For metadata, it first reads the two-byte size header, extracts compressed/uncompressed state, advances the index, and then reads the block payload. For file data, it decodes size and compression state from the supplied block-list entry. After bounds checks against `output->length` and `msblk->bytes_used`, it reads the byte range into a BIO. Compressed payloads go through `msblk->thread_ops->decompress`; uncompressed payloads are copied directly to the actor.

## State and Persistence Behavior

Persistent state lives in `msblk`: device block sizing, filesystem byte limit, optional compressed-page `cache_mapping`, panic-on-error flag, selected decompressor stream, and thread ops. BIO pages are temporary. Cached compressed head/tail pages are inserted into `cache_mapping` when the device block size equals page size; `CONFIG_SQUASHFS_COMP_CACHE_FULL` may cache all compressed BIO pages.

## Dependencies and Integration Points

This is the common dependency for metadata cache fills, fragment reads, file data reads, table reads, symlink reads, and decompressor option reads. It integrates with the block layer (`bio_*`, `submit_bio_wait`), page cache (`filemap_add_folio`, `find_get_page`), decompressor wrappers, and `page_actor`.

## Risks and Edge Cases

Critical risks are malformed image sizes, integer boundary mistakes around unaligned device/page offsets, stale or non-uptodate cached pages, actor length mismatches, and missing decompressor stream. The error path frees BIO pages and can panic when mounted with `errors=panic`.

## Test Signals

Mount and read images with compressed and uncompressed metadata/data blocks, corrupted block sizes, truncated devices, page-sized and non-page-sized device blocks, direct and cached file modes, all compression wrappers, and `errors=panic`/`continue`. Repeated adjacent reads should exercise compressed-page cache reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/block.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/cache.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/cache.c

## Purpose

`cache.c` implements the generic cache used for SquashFS metadata, fragments, and the optional file-data intermediate buffer. It avoids repeated reads and decompressions of packed metadata/fragment blocks and provides metadata stream reading across compressed metadata-block boundaries.

## Important APIs, Types, and Functions

Public functions are `squashfs_cache_init()`, `squashfs_cache_delete()`, `squashfs_cache_get()`, `squashfs_cache_put()`, `squashfs_copy_data()`, `squashfs_read_metadata()`, `squashfs_get_fragment()`, `squashfs_get_datablock()`, and `squashfs_read_table()`. Key types are `struct squashfs_cache`, `struct squashfs_cache_entry`, and `struct squashfs_page_actor`.

## Control Flow

`squashfs_cache_get()` looks for a block in a round-robin cache. On miss, it waits if all entries are referenced, otherwise claims an unused entry, marks it pending, fills it with `squashfs_read_data()`, clears pending, and wakes waiters. On hit, it increments the refcount and waits if another task is still filling the entry. `squashfs_read_metadata()` repeatedly gets metadata blocks, copies from the current offset, advances to `entry->next_index`, and releases entries.

## State and Persistence Behavior

The cache persists per mounted filesystem in `squashfs_sb_info`. Each entry tracks block id, decompressed length, refcount, pending/error state, wait queues, backing page-sized buffers, and actor. The cache is read-only after fill except for eviction/reuse metadata.

## Dependencies and Integration Points

It depends on `squashfs_read_data()` for fills and `page_actor` for decompression destinations. Metadata readers across the filesystem use `squashfs_read_metadata()`. `super.c` allocates metadata, fragment, and read-page caches and releases them on mount failure/unmount.

## Risks and Edge Cases

Concurrency correctness depends on refcount, `unused`, pending state, and wait queue updates under the spinlock. Malformed metadata offsets or negative lengths return `-EIO`. `squashfs_copy_data()` supports `buffer == NULL` for skip/count behavior, which callers rely on heavily; incorrect use can desynchronize metadata offsets.

## Test Signals

Parallel directory/stat/read workloads should cover cache waiters and refcounts. Corrupt metadata-block length, bad offsets, allocation-failure injection, fragment-heavy small files, and xattr/symlink metadata spanning blocks are useful targeted tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/decompressor.c

## Purpose

`decompressor.c` is the SquashFS decompressor registry and setup layer. It maps on-disk compression IDs to compiled backend operations, reports unsupported algorithms, reads optional compression options from the image, and creates the selected threaded decompressor stream.

## Important APIs, Types, and Functions

Public functions are `squashfs_lookup_decompressor()` and `squashfs_decompressor_setup()`. Internal `get_comp_opts()` reads optional compressor-specific metadata. The static `decompressor[]` table contains supported or unsupported `struct squashfs_decompressor` instances for zlib, lz4, lzo, xz, lzma, zstd, and unknown compression.

## Control Flow

Mount code uses `squashfs_lookup_decompressor()` after reading the superblock compression id. Later `squashfs_decompressor_setup()` calls `get_comp_opts()`; if the image has compression options, they are read as a metadata block immediately after the superblock and passed to the backend `comp_opts` hook. Finally the configured thread ops create the runtime stream.

## State and Persistence Behavior

This file owns no long-lived mutable state. It allocates transient option buffers and returns a stream owned by `msblk->stream` through the selected thread implementation. Unsupported compiled-out algorithms remain represented by read-only table entries with `supported = 0`.

## Dependencies and Integration Points

It integrates with `super.c`, `decompressor.h`, `squashfs_read_data()`, backend wrappers, and the thread ops selected by Kconfig/mount options.

## Risks and Edge Cases

Images using unsupported compression must fail cleanly. Bad or truncated compression option blocks must fail mount, not leak buffers. The setup path assumes `msblk->decompressor` and `msblk->thread_ops` are already initialized by `super.c`.

## Test Signals

Mount images for each compiled backend; mount unsupported lzma or disabled-backend images; test images with and without compression options; inject corrupt option sizes for LZ4/XZ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor.h -->
# sources/distributed-fs/ceph-client/fs/squashfs/decompressor.h

## Purpose

This header defines the backend decompressor interface used by SquashFS. It separates algorithm-specific init/options/free/decompress functions from the higher-level thread-mode wrappers.

## Important APIs, Types, and Functions

The central type is `struct squashfs_decompressor`, with hooks `init`, `comp_opts`, `free`, and `decompress`, fields `id`, `name`, `alloc_buffer`, and `supported`. The helper `squashfs_comp_opts()` invokes an optional backend option parser. Conditional externs declare compiled wrappers for XZ, LZ4, LZO, ZLIB, and ZSTD.

## Control Flow

There is no standalone control flow. `decompressor.c` and the thread wrappers call through this interface during mount setup and block decompression.

## State and Persistence Behavior

The struct describes immutable backend operations. Backend `init()` creates per-stream state; `alloc_buffer` influences `page_actor` behavior for direct decompression.

## Dependencies and Integration Points

The header includes `linux/bio.h` and references `struct squashfs_sb_info` and `struct squashfs_page_actor`. It is shared by `block.c`, `decompressor.c`, `decompressor_*`, `page_actor.c`, and all compression wrappers.

## Risks and Edge Cases

Changing hook signatures or `alloc_buffer` semantics affects every backend and direct page-cache decompression. A backend returning an incorrect byte count can corrupt page-cache state in callers.

## Test Signals

Compile coverage for every backend, sparse/smatch type checking, and mount/read tests across direct and cached file modes validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor_multi.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/decompressor_multi.c

## Purpose

This file implements the dynamic multi-decompressor thread mode. It maintains a pool of algorithm-specific decompressor streams and lets parallel I/O callers borrow streams up to `msblk->max_thread_num`.

## Important APIs, Types, and Functions

It exports `squashfs_decompressor_multi`, a `struct squashfs_decompressor_thread_ops`. Internal types are `struct squashfs_stream` for pool state and `struct decomp_stream` for individual backend streams. Internal helpers include `squashfs_max_decompressors()`, `squashfs_decompressor_create()`, `squashfs_decompressor_destroy()`, `get_decomp_stream()`, `put_decomp_stream()`, and `squashfs_decompress()`.

## Control Flow

Create allocates the pool and one default stream so the filesystem can operate even if later dynamic allocation fails. Decompression borrows an available stream, dynamically allocates another if below the max and memory allows, otherwise waits for a stream to return. After backend decompression, it returns the stream to the list and wakes waiters.

## State and Persistence Behavior

Per-mount pool state lives in `msblk->stream`. It owns `comp_opts`, a mutex-protected list of available streams, `avail_decomp`, and a wait queue. Individual backend streams persist until unmount.

## Dependencies and Integration Points

It is selected by `CONFIG_SQUASHFS_DECOMP_MULTI` and used by `super.c` mount option parsing. It calls the selected `msblk->decompressor` backend hooks and is invoked by `block.c`.

## Risks and Edge Cases

Pool accounting must remain balanced during allocation failure and unmount. Waiting uses stream availability, so a leaked stream would deadlock future reads. `max_thread_num` must not exceed the advertised maximum.

## Test Signals

Parallel read/readahead benchmarks, memory-pressure allocation-failure tests, numeric `threads=` mount tests, and unmount under active read stress are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor_multi_percpu.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/decompressor_multi_percpu.c

## Purpose

This file implements the per-CPU decompressor mode. It allocates one backend stream per possible CPU and uses a `local_lock_t` to serialize decompression on the current CPU's stream.

## Important APIs, Types, and Functions

It exports `squashfs_decompressor_percpu`. The internal `struct squashfs_stream` holds a backend stream pointer and local lock. Functions are `squashfs_decompressor_create()`, `squashfs_decompressor_destroy()`, `squashfs_decompress()`, and `squashfs_max_decompressors()`.

## Control Flow

Create allocates percpu storage and initializes a backend stream for each possible CPU, then frees shared compression options. Decompress maps `msblk->stream` back to percpu storage, locks the current CPU stream, runs backend decompression, unlocks, and reports corrupt data on error. Destroy frees all per-CPU backend streams and the percpu allocation.

## State and Persistence Behavior

The per-mount state is a percpu pointer stored as `msblk->stream`. Stream count is fixed at mount time to `num_possible_cpus()`, not demand-based.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_DECOMP_MULTI_PERCPU`; usable through `threads=percpu` when mount-time choice is compiled. It depends on percpu and local-lock kernel APIs and backend decompressor hooks.

## Risks and Edge Cases

Allocation failures during partial CPU initialization must free already-created streams. CPU hotplug semantics are simplified by allocating for possible CPUs. This mode can consume more memory than single or demand-based multi on large systems.

## Test Signals

Mount/read tests on SMP systems, CPU hotplug stress where available, lockdep/local-lock checking, and memory footprint comparisons across CPU counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor_multi_percpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor_single.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/decompressor_single.c

## Purpose

This file implements the legacy single-stream decompressor mode. It serializes all SquashFS decompression for a mount behind one mutex-protected backend stream.

## Important APIs, Types, and Functions

It exports `squashfs_decompressor_single`. Internal `struct squashfs_stream` holds `void *stream` and a mutex. Functions are `squashfs_decompressor_create()`, `squashfs_decompressor_destroy()`, `squashfs_decompress()`, and `squashfs_max_decompressors()`.

## Control Flow

Create allocates one wrapper and backend stream, frees compression options, and initializes the mutex. Decompression locks the mutex, calls the backend, unlocks, and reports corrupt data on negative return. Destroy frees the backend stream and wrapper.

## State and Persistence Behavior

Per-mount state is a single stream in `msblk->stream`. It minimizes memory use but creates a bottleneck for concurrent reads.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_DECOMP_SINGLE` and used as the default in `super.c` when compiled. `block.c` calls through this implementation via thread ops.

## Risks and Edge Cases

The primary risk is performance under parallel I/O, not correctness. Initialization must free wrapper memory on backend init failure.

## Test Signals

Basic mount/read coverage, lockdep with parallel readers, and performance comparison against multi/percpu modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/decompressor_single.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/dir.c

## Purpose

`dir.c` implements directory iteration for SquashFS. It decodes packed directory metadata, synthesizes `"."` and `".."`, optionally uses long-directory indexes to skip near the current position, and emits VFS directory entries.

## Important APIs, Types, and Functions

The exported object is `squashfs_dir_ops`. Internal helpers are `get_dir_index_using_offset()` and `squashfs_readdir()`. It uses `struct squashfs_dir_header`, `struct squashfs_dir_entry`, `struct dir_context`, and the file-type translation table.

## Control Flow

`squashfs_readdir()` allocates a max-size directory entry buffer, emits synthetic dot entries while `ctx->pos < 3`, uses the directory index to locate the metadata block for the requested position, then loops over directory headers and entries. It validates counts, name sizes, and type values before calling `dir_emit()`.

## State and Persistence Behavior

Directory iteration state is `ctx->pos`; no persistent mutable filesystem state is changed. On-disk directory positions are offset by 3 externally because dot entries are synthetic.

## Dependencies and Integration Points

It depends on `squashfs_read_metadata()`, directory fields stored in `squashfs_inode_info`, and VFS directory operation hooks. `inode.c` assigns `squashfs_dir_ops` to directory inodes.

## Risks and Edge Cases

Malformed directory counts, oversized names, bad types, or read errors cause iteration to stop with an error log but return 0 to userspace. Position translation around synthetic dot entries is subtle.

## Test Signals

Run `find`, `ls -la`, telldir/seekdir-style tests, large indexed directories, corrupted directory metadata images, and short-buffer directory iteration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/export.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/export.c

## Purpose

`export.c` makes SquashFS exportable through exportfs/NFS-style file handles. It maps stable inode numbers from file handles to packed inode locations using the mount-time inode lookup table.

## Important APIs, Types, and Functions

The exported object is `squashfs_export_ops`; public table loader is `squashfs_read_inode_lookup_table()`. Internal functions are `squashfs_inode_lookup()`, `squashfs_export_iget()`, `squashfs_fh_to_dentry()`, `squashfs_fh_to_parent()`, and `squashfs_get_parent()`.

## Control Flow

At mount, `super.c` loads the inode lookup index and installs `s_export_op` when the image has an export table. During handle decode, exportfs passes inode numbers into `squashfs_export_iget()`, which reads the corresponding packed inode location and calls `squashfs_iget()`.

## State and Persistence Behavior

The lookup index persists in `msblk->inode_lookup_table`; actual inode-location entries remain compressed in metadata blocks and are read on demand. No writeback state exists.

## Dependencies and Integration Points

It integrates with VFS export operations, `generic_encode_ino32_fh`, `d_obtain_alias`, `squashfs_iget()`, and metadata reading. Parent lookup depends on `squashfs_inode_info.parent` filled by `inode.c`.

## Risks and Edge Cases

Invalid inode numbers, absent lookup table, corrupt table ordering, and bad parent inode fields can break export handles. Table validation checks size and monotonic metadata-block pointers.

## Test Signals

Mount exportable and non-exportable images, run exportfs/NFS handle round-trips, verify parent lookup for directories, and corrupt lookup index boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/file.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/file.c

## Purpose

`file.c` implements regular file reads, readahead, sparse block handling, fragment-tail reads, large-file block-list indexing, page-cache population, and `SEEK_DATA`/`SEEK_HOLE` support for SquashFS.

## Important APIs, Types, and Functions

Public objects/functions are `squashfs_aops`, `squashfs_file_operations`, and `squashfs_copy_cache()`. Important internals include `locate_meta_index()`, `empty_meta_index()`, `release_meta_index()`, `read_indexes()`, `calculate_skip()`, `fill_meta_index()`, `read_blocklist_ptrs()`, `read_blocklist()`, `squashfs_readpage_fragment()`, `squashfs_readpage_sparse()`, `squashfs_read_folio()`, `squashfs_readahead_fragment()`, `squashfs_readahead()`, `seek_hole_data()`, and `squashfs_llseek()`.

## Control Flow

For a folio read, the file offset is mapped to a SquashFS block index. If the target is a normal data block, `read_blocklist()` finds its compressed size and on-disk address; zero size means a sparse block, nonzero means `squashfs_readpage_block()` from the selected file strategy. If the final partial block is packed in a fragment, it reads from the fragment cache. Readahead expands requests to SquashFS block boundaries and fills batches directly through a page actor. Large-file mapping uses a small meta-index cache to avoid rescanning block lists from the inode for every random read.

## State and Persistence Behavior

Per-inode state in `squashfs_inode_info` stores start block, block-list metadata location, fragment location, and fragment offset. Per-mount mutable state includes the lazily allocated `msblk->meta_index` array guarded by `meta_index_mutex`. Page-cache pages become persistent VFS cache state after successful reads.

## Dependencies and Integration Points

It depends on `cache.c`, `block.c`, `fragment.c`, `page_actor`, and the file strategy implementation in `file_cache.c` or `file_direct.c`. `inode.c` assigns these address-space and file operations to regular file inodes.

## Risks and Edge Cases

The meta-index cache has locking and reuse complexity. Sparse blocks must be zero-filled and reported correctly to `SEEK_DATA`/`SEEK_HOLE`. Fragment tails cannot coincide with block-aligned file sizes. Readahead error paths must unlock and put every page. Corrupt block sizes from metadata must abort safely.

## Test Signals

Sequential and random reads of small, large, sparse, and fragment-tailed files; mmap reads; readahead-heavy workloads; `lseek(SEEK_DATA/SEEK_HOLE)` conformance; corruption tests for block lists; and parallel reads that exercise meta-index locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/file_cache.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/file_cache.c

## Purpose

`file_cache.c` implements the file-data strategy that decompresses each compressed data block into an intermediate SquashFS cache entry and then copies it into page-cache folios.

## Important APIs, Types, and Functions

It defines `squashfs_readpage_block()`, the strategy function declared in `squashfs.h` and called by `file.c`.

## Control Flow

For a requested folio, the function gets the compressed data block through `squashfs_get_datablock()`, checks `buffer->error`, copies the expected bytes into the relevant page-cache folios using `squashfs_copy_cache()`, then releases the cache entry.

## State and Persistence Behavior

It uses the per-mount `read_page` cache as temporary decompressed storage. Successful copies persist in the VFS page cache.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_FILE_CACHE`. It depends on `cache.c` and `file.c` and is mutually exclusive with `file_direct.c`.

## Risks and Edge Cases

The extra copy costs CPU and memory bandwidth but reduces direct page-cache locking complexity. Error propagation depends on `buffer->error`, and the cache must be available when this strategy is compiled.

## Test Signals

Read tests with `SQUASHFS_FILE_CACHE`, fragment vs normal data paths, repeated reads to see cache reuse, and comparison against direct mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/file_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/file_direct.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/file_direct.c

## Purpose

`file_direct.c` implements the direct file-data strategy, decompressing a compressed SquashFS block directly into page-cache pages covered by that filesystem block.

## Important APIs, Types, and Functions

It defines `squashfs_readpage_block()`. Important local state includes the target folio, grabbed sibling pages, a `struct squashfs_page_actor`, and the last page returned by the actor.

## Control Flow

The function computes all page indexes covered by the SquashFS block, grabs non-target pages opportunistically, skips already-uptodate pages, creates a direct page actor, and calls `squashfs_read_data()`. On exact expected byte count, it zero-fills the tail of the final file page when needed, marks pages uptodate, unlocks them, and releases non-target pages. On failure, it leaves the target page for the caller and unlocks/releases other pages.

## State and Persistence Behavior

No private persistent state is created. Successful decompression populates page-cache pages directly. Temporary page arrays and actor state are freed before return.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_FILE_DIRECT`. It depends on `page_actor`, `block.c`, and `file.c`. Backend `alloc_buffer` flags affect whether direct actor gaps can use a temporary buffer.

## Risks and Edge Cases

Page grabbing can fail for sibling pages; the actor must handle gaps without corrupting output ordering. The return count must match `expected` or pages are treated as errored. Tail zeroing is required for the last page of a file.

## Test Signals

Direct-mode read, mmap, readahead, partial-cache, memory-pressure, and compressed backend coverage; tests should include holes in grabbed page ranges and final partial pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/file_direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/fragment.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/fragment.c

## Purpose

`fragment.c` handles SquashFS fragments, which are tail-end file data packed into shared compressed blocks. It maps fragment numbers from inodes to on-disk block addresses and compressed sizes.

## Important APIs, Types, and Functions

Public functions are `squashfs_frag_lookup()` and `squashfs_read_fragment_index_table()`. It uses `struct squashfs_fragment_entry` and fragment table macros from `squashfs_fs.h`.

## Control Flow

At mount, `squashfs_read_fragment_index_table()` validates and reads the uncompressed fragment index table. At inode load time, `squashfs_frag_lookup()` validates the fragment number, finds the metadata block through `msblk->fragment_index`, reads the fragment entry, returns its start block through an output parameter, and returns the decoded compressed size.

## State and Persistence Behavior

The fragment index is persisted in memory as `msblk->fragment_index`; fragment data itself is read on demand through the fragment cache.

## Dependencies and Integration Points

Used by `inode.c` when regular inodes reference fragments and by `file.c` when reading fragment-backed tail pages. It depends on metadata reading and table read helpers.

## Risks and Edge Cases

Invalid fragment numbers and corrupt fragment sizes must fail reads or mount. Table validation only checks index bounds/order; individual entries are validated when used.

## Test Signals

Small-file and tail-fragment reads, images with no fragments, maximum fragment counts, and corrupt fragment table or entry sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/fragment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/id.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/id.c

## Purpose

`id.c` maps compact uid/gid indexes stored in SquashFS inodes to 32-bit uid/gid values through the on-disk id lookup table.

## Important APIs, Types, and Functions

Public functions are `squashfs_get_id()` and `squashfs_read_id_index_table()`. It uses ID table macros from `squashfs_fs.h` and `msblk->id_table`.

## Control Flow

Mount code loads and validates the id index table. Inode creation calls `squashfs_get_id()` for uid and gid indexes; the function validates the index, reads the `__le32` disk id from compressed metadata, converts to CPU endian, and returns it.

## State and Persistence Behavior

`msblk->id_table` persists for the mount and points to metadata blocks containing actual id values. Inode uid/gid fields are populated in VFS inode state after lookup.

## Dependencies and Integration Points

`inode.c` depends on this for every inode. `super.c` loads and frees the id table. It uses `squashfs_read_table()` and `squashfs_read_metadata()`.

## Risks and Edge Cases

`no_ids == 0`, invalid id indexes, non-monotonic metadata pointers, or mismatched table size should fail mount or inode load. Bad id data can affect ownership visible to userspace.

## Test Signals

Images with many uid/gid values, boundary id indexes, malformed id tables, and stat output verification for file ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/inode.c

## Purpose

`inode.c` creates and initializes VFS inodes from packed SquashFS inode metadata. It decodes all regular, directory, symlink, device, FIFO, socket, and extended inode formats and attaches the correct VFS operations.

## Important APIs, Types, and Functions

Public functions/objects are `squashfs_iget()`, `squashfs_read_inode()`, and `squashfs_inode_ops`. Internal `squashfs_new_inode()` fills common inode fields. Important types are `union squashfs_inode`, on-disk inode structs, and `struct squashfs_inode_info`.

## Control Flow

`squashfs_iget()` uses `iget_locked()` and only reads metadata for new inodes. `squashfs_read_inode()` reads the base inode, validates mode/type setup, resets the metadata cursor, then switches on inode type. Each case reads the type-specific struct, fills VFS mode, size, nlink, operations, address-space operations, device numbers, fragment state, block-list location, directory index state, parent inode, and optional xattr id.

## State and Persistence Behavior

VFS inode fields persist in the inode cache. SquashFS-private inode state stores packed metadata locations and fragment/xattr/directory-index data. The filesystem is read-only; no inode writeback state is generated.

## Dependencies and Integration Points

It depends on id lookup, fragment lookup, xattr lookup, directory/file/symlink operation tables, special inode helpers, and metadata reading. `super.c` calls it for the root inode; directory lookup and export code call `squashfs_iget()`.

## Risks and Edge Cases

Malformed inode types, zero inode numbers, invalid uid/gid indexes, impossible fragments on block-aligned files, symlinks larger than a page, negative large-file sizes, or bad xattr ids must reject the inode. Mode type bits are expected unset in on-disk common mode before the switch sets them.

## Test Signals

Mount images containing every inode type, hard links, large regular files, sparse files, fragments, xattrs, special files, corrupt inode metadata, and repeated lookup/export paths that reuse cached inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/lz4_wrapper.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/lz4_wrapper.c

## Purpose

This wrapper implements SquashFS LZ4 decompression backend support using the kernel LZ4 library and the legacy SquashFS LZ4 option format.

## Important APIs, Types, and Functions

It exports `squashfs_lz4_comp_ops`. Internal types are `struct lz4_comp_opts` and `struct squashfs_lz4`. Functions are `lz4_comp_opts()`, `lz4_init()`, `lz4_free()`, and `lz4_uncompress()`.

## Control Flow

Option parsing requires a present options block and validates the legacy version. Init allocates input and output vmalloc buffers sized to the larger of filesystem block size and metadata size. Decompress copies BIO segments into the input buffer, calls `LZ4_decompress_safe()`, then copies output into the page actor.

## State and Persistence Behavior

Each backend stream owns input/output work buffers until the decompressor thread mode frees it. No filesystem data is persisted beyond page-cache/cache consumers.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_LZ4`, uses `<linux/lz4.h>`, and plugs into `decompressor.c` through `struct squashfs_decompressor`.

## Risks and Edge Cases

LZ4 images without options or with non-legacy version are rejected. The full compressed input and decompressed output must fit allocated buffers. Return values below zero map to `-EIO`.

## Test Signals

Mount/read LZ4 images, corrupt options version, truncated compressed blocks, direct and cached file modes, and large block-size images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/lz4_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/lzo_wrapper.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/lzo_wrapper.c

## Purpose

This wrapper implements SquashFS LZO decompression using the kernel LZO library.

## Important APIs, Types, and Functions

It exports `squashfs_lzo_comp_ops`. Internal state is `struct squashfs_lzo` with input and output buffers. Functions are `lzo_init()`, `lzo_free()`, and `lzo_uncompress()`.

## Control Flow

Init allocates vmalloc input/output buffers sized to the larger of block size and metadata size. Decompress copies BIO input into the input buffer, calls `lzo1x_decompress_safe()`, and copies the produced bytes to the output actor.

## State and Persistence Behavior

Workspace buffers persist per backend stream. Output persists only through cache/page-cache consumers.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_LZO`, uses `<linux/lzo.h>`, and is registered through `decompressor.c`.

## Risks and Edge Cases

Allocation failure must free partially allocated buffers. Any non-`LZO_E_OK` result becomes `-EIO`. Since it stages both input and output, large block sizes increase memory use per decompressor stream.

## Test Signals

Mount/read LZO images, corruption tests for compressed data, allocation-failure injection, and parallel read tests with multi decompressor streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/lzo_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/namei.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/namei.c

## Purpose

`namei.c` implements filename lookup in SquashFS directories. It uses sorted directory metadata and optional directory indexes to locate a named child and instantiate its inode.

## Important APIs, Types, and Functions

The exported object is `squashfs_dir_inode_ops`. Internal functions are `get_dir_index_using_name()` and `squashfs_lookup()`. It uses `struct squashfs_dir_index`, `struct squashfs_dir_header`, `struct squashfs_dir_entry`, and `squashfs_iget()`.

## Control Flow

Lookup validates name length, uses the directory index to jump near the name, then scans directory headers and entries. Because entries are sorted, if the first character has advanced beyond the target name it exits early. On exact length/name match it constructs the packed inode value from header start block and entry offset, computes the visible inode number, and calls `squashfs_iget()`.

## State and Persistence Behavior

No directory state is mutated. Negative or positive dentries are returned through `d_splice_alias()`. Directory index metadata remains read-only.

## Dependencies and Integration Points

`inode.c` assigns these operations to directory inodes. It depends on metadata reading, directory private inode fields, xattr list support, and VFS dcache lookup semantics.

## Risks and Edge Cases

Oversized names return `-ENAMETOOLONG`. Corrupt directory counts/sizes produce `-EIO`. The early exit assumes sorted directory order. Index read errors degrade to partial index use rather than immediate failure.

## Test Signals

Lookup existing/missing names in small and large indexed directories, names near `SQUASHFS_NAME_LEN`, corrupt directory metadata, and dcache alias cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/page_actor.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/page_actor.c

## Purpose

`page_actor.c` abstracts decompressor output destinations. It supports output to linear intermediate buffers and direct output to page-cache pages, including handling missing pages with optional temporary buffers for streaming decompressors.

## Important APIs, Types, and Functions

Public constructors are `squashfs_page_actor_init()` and `squashfs_page_actor_init_special()`. Internal operations are cache-mode `cache_first_page()`, `cache_next_page()`, `cache_finish_page()` and direct-mode `direct_first_page()`, `direct_next_page()`, `direct_finish_page()` via `handle_next_page()`.

## Control Flow

Intermediate-buffer actors simply return successive buffer pointers. Direct actors track expected page index and returned page count; when a page is missing they either return a temporary buffer if the backend requires one or an error pointer. Direct next/finish unmap any locally mapped page.

## State and Persistence Behavior

Actor state is temporary for one decompression/read. It tracks page arrays or buffer arrays, current mapping address, last real page, expected output length, page index, and whether a temporary buffer is allowed.

## Dependencies and Integration Points

Used by `block.c`, `cache.c`, `file_direct.c`, `file.c` readahead, compression wrappers, and decompressor setup option reading. It depends on backend `alloc_buffer` semantics.

## Risks and Edge Cases

Callers must not sleep between actor page mapping calls and finish. Direct actor gap handling is subtle: non-streaming wrappers may tolerate skipped pages, streaming wrappers need a temporary page. Failure to unmap local mappings would break highmem/local-map rules.

## Test Signals

Direct and cached file modes, readahead with partially missing pages, highmem/local kmap debug, and every compression backend because wrappers consume actor pages differently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/page_actor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/page_actor.h -->
# sources/distributed-fs/ceph-client/fs/squashfs/page_actor.h

## Purpose

This header defines `struct squashfs_page_actor` and inline helpers for the decompressor output abstraction.

## Important APIs, Types, and Functions

Key fields include the buffer/page union, `pageaddr`, `tmp_buffer`, operation function pointers, `last_page`, page counts, output length, `alloc_buffer`, `returned_pages`, and `next_index`. Public helpers are `squashfs_page_actor_init()`, `squashfs_page_actor_init_special()`, `squashfs_page_actor_free()`, `squashfs_first_page()`, `squashfs_next_page()`, `squashfs_finish_page()`, and `squashfs_actor_nobuff()`.

## Control Flow

Inline helpers dispatch through function pointers set by the constructors. `squashfs_page_actor_free()` frees temporary storage and returns the last real page only if every supplied page was consumed; otherwise it returns an error pointer.

## State and Persistence Behavior

The header defines temporary per-read actor state. It does not own persistent filesystem state.

## Dependencies and Integration Points

It is included by low-level I/O, decompressor wrappers, direct file reads, and cache code. The return convention of `squashfs_page_actor_free()` is used by direct read and readahead code to validate output completion.

## Risks and Edge Cases

The union requires callers to use the constructor matching the destination type. `squashfs_actor_nobuff()` disables fallback buffering and is used for raw copy paths; misuse can turn skipped pages into errors.

## Test Signals

Build coverage, direct/cached read tests, page-gap tests, and backend-specific decompression tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/page_actor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/squashfs.h -->
# sources/distributed-fs/ceph-client/fs/squashfs/squashfs.h

## Purpose

This is the internal SquashFS header that ties the implementation together. It declares logging macros, shared helper APIs, decompressor thread operations, and VFS operation tables exported across compilation units.

## Important APIs, Types, and Functions

Important macros are `TRACE`, `ERROR`, `WARNING`, and `SQUASHFS_READ_PAGES`. The key type is `struct squashfs_decompressor_thread_ops`. The header declares all cross-file helpers for block reads, caches, metadata, decompressor setup, export tables, fragment/id/xattr table lookup, inode loading, file reads, directory/file/symlink/inode ops, and xattr handlers.

## Control Flow

No code flow beyond declarations. It defines the shared call graph: `super.c` initializes state; `inode.c`, `dir.c`, `namei.c`, `file.c`, `xattr.c`, and export code use cache/block/decompressor helpers through this contract.

## State and Persistence Behavior

It declares interfaces that manipulate per-mount `squashfs_sb_info`, per-inode `squashfs_inode_info`, and temporary cache/page actor state, but owns no storage.

## Dependencies and Integration Points

Included by most SquashFS `.c` files. The conditional externs for thread ops mirror Kconfig selections and Makefile object inclusion.

## Risks and Edge Cases

Prototype drift causes build failures or worse if signatures diverge from implementations. `SQUASHFS_READ_PAGES` changes the `read_page` cache size depending on file-cache mode.

## Test Signals

All SquashFS build configurations and sparse checking are the primary validation signals for this internal interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/squashfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs.h -->
# sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs.h

## Purpose

This header defines the SquashFS on-disk format constants, table indexing macros, compression IDs, packed inode/directory/fragment/xattr structures, and metadata index cache structures.

## Important APIs, Types, and Functions

Important constants include version numbers, metadata size, device block size, max file block size/log, name length, inode type IDs, xattr type IDs, compression IDs, and invalid sentinel values. Important macros decode compressed-size bits, inode block/offset, fragment/id/lookup/xattr table addressing, and meta-index dimensions. Important structs include `meta_entry`, `meta_index`, `squashfs_super_block`, all inode variants, `squashfs_dir_index`, `squashfs_dir_entry`, `squashfs_dir_header`, `squashfs_fragment_entry`, `squashfs_xattr_entry`, `squashfs_xattr_val`, `squashfs_xattr_id`, and `squashfs_xattr_id_table`.

## Control Flow

The only inline executable helper is `squashfs_block_size()`, which rejects impossible encoded block sizes and returns a CPU-endian value. The rest defines the layout consumed by mount, inode, directory, file, fragment, id, export, and xattr code.

## State and Persistence Behavior

The structs mirror persistent on-disk SquashFS metadata. They are read-only when mounted. `meta_index` is in-memory cache state derived from file block lists.

## Dependencies and Integration Points

Included by all SquashFS modules and by superblock/private-state headers. Any format change must remain compatible with SquashFS tools and existing images.

## Risks and Edge Cases

This is ABI-critical. Field order, endian annotations, and size macros must match disk format. Size arithmetic must avoid overflow for large xattr/inode counts and table lengths.

## Test Signals

Mount known-good images from squashfs-tools, fuzz/corruption tests around table sizes and block-size fields, endian-build coverage, and compile-time layout review for format changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs_i.h -->
# sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs_i.h

## Purpose

This header defines SquashFS per-inode private state embedded around the VFS inode.

## Important APIs, Types, and Functions

`struct squashfs_inode_info` stores metadata start/offset, xattr location/count/size, parent inode number, and a union for regular-file fragment/block-list state or directory-index state. The inline `squashfs_i()` converts from `struct inode *` to the private container.

## Control Flow

There is no standalone control flow beyond `container_of` conversion. `inode.c` fills fields and other modules consume them during lookup, reads, readdir, xattr, and export parent lookup.

## State and Persistence Behavior

Instances persist for the lifetime of VFS inodes in the SquashFS inode slab cache. They cache decoded on-disk pointers, not writable filesystem metadata.

## Dependencies and Integration Points

Used by `super.c` inode allocation, `inode.c`, `file.c`, `dir.c`, `namei.c`, `export.c`, `symlink.c`, and `xattr.c`.

## Risks and Edge Cases

The union requires file and directory code to use fields only for the matching inode type. Parent defaults of 0 for non-directories matter for export parent lookup.

## Test Signals

Inode type coverage, export parent tests, xattr listing, directory index lookup, and regular file read tests validate field initialization and use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs_sb.h -->
# sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs_sb.h

## Purpose

This header defines SquashFS per-superblock state and cache entry structures used for a mounted filesystem.

## Important APIs, Types, and Functions

`struct squashfs_cache` tracks cache geometry, current/next slots, unused count, waiters, spinlock, wait queue, and entries. `struct squashfs_cache_entry` tracks one cached decompressed block. `struct squashfs_sb_info` stores decompressor operations, device block sizing, caches, cache mapping, table indexes, metadata-index cache, decompressor stream, table starts, filesystem geometry/counts, error mode, thread ops, and max thread count.

## Control Flow

There is no code flow here. `super.c` initializes and frees `squashfs_sb_info`; other modules read it for all filesystem operations.

## State and Persistence Behavior

This is the central per-mount persistent state. It persists from successful mount until `squashfs_put_super()` and owns all in-memory table indexes, caches, decompressor streams, and mount options.

## Dependencies and Integration Points

Included across the SquashFS implementation. Its fields connect mount-time table parsing to runtime file, directory, xattr, fragment, id, export, and decompression behavior.

## Risks and Edge Cases

Ownership and cleanup must match allocation paths in `super.c`; partial mount failure must handle NULL and ERR_PTR caches. Concurrency-sensitive fields include caches and the meta-index mutex/array.

## Test Signals

Mount failure injection, unmount leak checks, concurrent read/lookup workloads, xattr/export images, and all decompressor modes validate this state container.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/super.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/super.c

## Purpose

`super.c` implements SquashFS mount, superblock validation, per-mount state initialization, VFS filesystem registration, mount option parsing, statfs, unmount cleanup, and inode slab allocation.

## Important APIs, Types, and Functions

Important functions are `squashfs_parse_param_threads_str()`, `squashfs_parse_param_threads_num()`, `squashfs_parse_param()`, `supported_squashfs_filesystem()`, `squashfs_fill_super()`, `squashfs_get_tree()`, `squashfs_reconfigure()`, `squashfs_show_options()`, `squashfs_init_fs_context()`, `squashfs_statfs()`, `squashfs_put_super()`, inode-cache init/destroy helpers, module init/exit, `squashfs_alloc_inode()`, and `squashfs_free_inode()`. Key objects are `squashfs_fs_type` and `squashfs_super_ops`.

## Control Flow

Mount creates `squashfs_sb_info`, parses options, reads the superblock through `squashfs_read_table()`, validates magic/version/compression/device size/block size/root inode/table ordering, initializes caches and optional compressed-page cache mapping, sets up decompressor streams, loads xattr/id/export/fragment indexes in reverse table order, reads the root inode, and creates the root dentry. Failure paths free every partially allocated resource.

## State and Persistence Behavior

`msblk` owns mount-wide state: read-only filesystem geometry, decompressor/thread config, caches, table indexes, panic-on-error setting, and root table starts. Reconfigure only updates the errors behavior and forces read-only. Unmount deletes caches, cache mapping host inode, decompressor streams, indexes, meta-index cache, and `s_fs_info`.

## Dependencies and Integration Points

It integrates with fs_context, block-device mounting, VFS super operations, Kconfig-selected decompressor modes, cache/table readers, id/fragment/export/xattr table loaders, and inode read code. It registers the `squashfs` filesystem type and module metadata.

## Risks and Edge Cases

Mount validation is security-critical because all later reads trust table ordering and sizes. Risks include malformed table starts, unsupported compression, page size greater than filesystem block size, bad root inode offset, optional xattrs when kernel xattr support is disabled, and cleanup after partial initialization.

## Test Signals

Mount valid/corrupt images across compression formats, thread options, xattr/export/no-fragment variants, too-new/too-old versions, block-size boundaries, truncated block devices, remount option changes, statfs output, and kmemleak/failure-injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/symlink.c

## Purpose

`symlink.c` implements symlink page-cache reads for SquashFS. Symlink targets are stored inline in inode-table metadata, not as separate file data blocks.

## Important APIs, Types, and Functions

Exports are `squashfs_symlink_aops` and `squashfs_symlink_inode_ops`. The main function is `squashfs_symlink_read_folio()`.

## Control Flow

The read function starts from the symlink metadata block/offset stored in `squashfs_inode_info`, optionally skips bytes for nonzero folio position, then loops through metadata cache entries copying bytes into the folio via `kmap_local_folio()`. When the requested target bytes are complete it zero-fills the rest of the page, flushes dcache, and completes the folio read.

## State and Persistence Behavior

The symlink target persists in compressed inode metadata; successful reads populate the page cache. No mutable filesystem state is changed.

## Dependencies and Integration Points

`inode.c` assigns these ops to symlink inodes after validating symlink size. It depends on metadata cache functions and `page_get_link`.

## Risks and Edge Cases

The code avoids `squashfs_read_metadata()` during mapped folio writes because that helper can sleep; direct cache access must still release entries correctly. Symlinks larger than a page are rejected in `inode.c`.

## Test Signals

Readlink tests for short and page-near symlinks, symlink metadata spanning compressed metadata blocks, corrupt metadata, and xattr listing on symlinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/xattr.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/xattr.c

## Purpose

`xattr.c` implements listing and retrieving SquashFS extended attributes for user, trusted, and security namespaces.

## Important APIs, Types, and Functions

Public objects/functions are `squashfs_listxattr()` and `squashfs_xattr_handlers`. Internal functions are `squashfs_xattr_get()`, `squashfs_xattr_handler_get()`, `squashfs_trusted_xattr_handler_list()`, and `squashfs_xattr_handler()`. It uses `struct squashfs_xattr_entry` and `struct squashfs_xattr_val`.

## Control Flow

Listxattr checks that the filesystem has xattr support, then walks the inode's xattr entries. For each entry it selects a namespace handler, optionally emits the namespace prefix and name, skips or reads the value header and value, and tracks remaining user buffer space. Getxattr walks entries until prefix/name match; for out-of-line values it follows the stored xattr pointer before reading the value.

## State and Persistence Behavior

Xattr locations/counts/sizes are cached per inode; xattr id table and xattr table start are per mount. Attribute values remain read-only metadata and are copied to user buffers on demand.

## Dependencies and Integration Points

Integrated through VFS xattr handlers installed by `super.c` and inode operation `listxattr` hooks. It depends on metadata reading and xattr ids populated by `inode.c`/`xattr_id.c`.

## Risks and Edge Cases

Buffer sizing must return `-ERANGE` without overrunning user buffers. Unknown xattr types are ignored. Trusted xattrs require `CAP_SYS_ADMIN` for listing. Out-of-line value pointers must be handled carefully to avoid reading wrong metadata.

## Test Signals

`getfattr`/`listxattr` tests for user/trusted/security namespaces, permission checks for trusted list, no-xattr images, out-of-line values, small buffers, and corrupt xattr metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/xattr.h -->
# sources/distributed-fs/ceph-client/fs/squashfs/xattr.h

## Purpose

This header abstracts xattr support so the rest of SquashFS can mount images with xattr metadata even when kernel xattr support is disabled.

## Important APIs, Types, and Functions

When `CONFIG_SQUASHFS_XATTR` is enabled it declares `squashfs_read_xattr_id_table()` and `squashfs_xattr_lookup()`. Otherwise it provides inline stubs, defines `squashfs_listxattr` and `squashfs_xattr_handlers` as `NULL`, reads only the xattr id table header to find the preceding table start, logs that xattrs are ignored, and returns `-ENOTSUPP`.

## Control Flow

With xattr support disabled, mount code can still call `squashfs_read_xattr_id_table()`. The stub reads enough metadata to set `xattr_table_start`, returns `-ENOTSUPP`, and lets `super.c` continue when that exact error is seen.

## State and Persistence Behavior

No persistent state is owned. The enabled path uses real xattr table state; the disabled path intentionally leaves xattr handlers absent.

## Dependencies and Integration Points

Included by `super.c`, `inode.c`, `namei.c`, and `symlink.c`. It gates references to xattr implementation files according to Kconfig.

## Risks and Edge Cases

The disabled stub must still preserve table-order parsing during mount; otherwise id/export/fragment table boundaries would be wrong. Returning the wrong error would make xattr-bearing images fail unexpectedly.

## Test Signals

Mount xattr-bearing images with `CONFIG_SQUASHFS_XATTR=n`, verify xattrs are ignored but files mount, and build with xattr enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/xattr_id.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/xattr_id.c

## Purpose

`xattr_id.c` maps xattr ids stored in extended inodes to xattr metadata locations, counts, and sizes, and loads the xattr id index table at mount.

## Important APIs, Types, and Functions

Public functions are `squashfs_xattr_lookup()` and `squashfs_read_xattr_id_table()`. It uses `struct squashfs_xattr_id` and `struct squashfs_xattr_id_table`.

## Control Flow

Mount reads the xattr id table header at `table_start`, extracts the xattr table start and id count, validates nonzero count and exact index table length to the end of the filesystem, reads the index table, and validates metadata-block pointer ordering plus xattr table ordering. Inode load calls `squashfs_xattr_lookup()` to read one id record and fill private inode xattr fields.

## State and Persistence Behavior

`msblk->xattr_id_table`, `msblk->xattr_table`, and `msblk->xattr_ids` persist for the mount. Per-inode xattr fields are derived from the id record.

## Dependencies and Integration Points

Used by `super.c` and `inode.c`; `xattr.c` later consumes the per-inode xattr location/count/size. It depends on `squashfs_read_table()` and `squashfs_read_metadata()`.

## Risks and Edge Cases

The table is located at the end of the filesystem, so length checks are tight. Bad index ordering or xattr table start can otherwise send xattr reads into unrelated metadata. `index >= xattr_ids` is rejected.

## Test Signals

Images with many xattr ids, out-of-line xattr values, corrupted xattr id table length/order, and xattr-disabled mount behavior through `xattr.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/xattr_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/xz_wrapper.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/xz_wrapper.c

## Purpose

This wrapper implements SquashFS XZ decompression using the kernel XZ decoder and optional on-disk dictionary-size options.

## Important APIs, Types, and Functions

It exports `squashfs_xz_comp_ops`. Internal types are `struct squashfs_xz`, `struct disk_comp_opts`, and `struct comp_opts`. Functions are `squashfs_xz_comp_opts()`, `squashfs_xz_init()`, `squashfs_xz_free()`, and `squashfs_xz_uncompress()`.

## Control Flow

Option parsing validates option length and dictionary size shape, or defaults to max(block size, metadata size). Init preallocates an XZ decoder with the dictionary size. Decompress resets the decoder, feeds BIO segments into `xz_dec_run()`, advances actor output pages as they fill, requires `XZ_STREAM_END`, and returns total output bytes.

## State and Persistence Behavior

Each stream owns an `xz_dec` state object and buffer descriptor. The parsed dictionary option is owned during stream creation.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_XZ`, uses `<linux/xz.h>`, and sets `alloc_buffer = 1`, which tells direct actors to provide temporary output for missing pages.

## Risks and Edge Cases

Dictionary validation is important for memory use and decoder correctness. Streaming output must handle actor error pointers and NULL pages. Missing `XZ_STREAM_END` is treated as corrupt input.

## Test Signals

XZ images with default and explicit dictionary options, corrupt option lengths/dictionary sizes, truncated streams, direct mode with missing pages, and memory-pressure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/xz_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/zlib_wrapper.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/zlib_wrapper.c

## Purpose

This wrapper implements the default SquashFS ZLIB decompression backend using the kernel zlib inflate implementation.

## Important APIs, Types, and Functions

It exports `squashfs_zlib_comp_ops`. Functions are `zlib_init()`, `zlib_free()`, and `zlib_uncompress()`. Runtime state is a `z_stream` plus vmalloced inflate workspace.

## Control Flow

Init allocates a zlib stream and workspace. Decompress lazily calls `zlib_inflateInit()`, feeds BIO segment input when `avail_in` is empty, advances actor output pages when `avail_out` reaches zero, runs `zlib_inflate(Z_SYNC_FLUSH)` until `Z_STREAM_END`, then calls `zlib_inflateEnd()` and returns `stream->total_out`.

## State and Persistence Behavior

The workspace persists per backend stream. `z_stream` fields are reused per decompression call and finalized after each call.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_ZLIB`, uses `<linux/zlib.h>`, and sets `alloc_buffer = 1` for direct actor fallback behavior.

## Risks and Edge Cases

Failure before `zlib_inflateInit()` must not call inflateEnd incorrectly. Streaming must not run out of actor pages before stream end. zlib errors map to `-EIO`.

## Test Signals

Default zlib image reads, corrupt/truncated streams, direct and cached file modes, metadata-heavy directory traversal, and all decompressor thread modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/zlib_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/zstd_wrapper.c -->
# sources/distributed-fs/ceph-client/fs/squashfs/zstd_wrapper.c

## Purpose

This wrapper implements SquashFS Zstandard decompression using the kernel zstd streaming API.

## Important APIs, Types, and Functions

It exports `squashfs_zstd_comp_ops`. Internal `struct workspace` stores workspace memory, size, and window size. Functions are `zstd_init()`, `zstd_free()`, and `zstd_uncompress()`.

## Control Flow

Init computes a window size from max(block size, metadata size), asks zstd for workspace bound, and vmallocs memory. Decompress initializes a dstream on that workspace, feeds BIO segments into `zstd_decompress_stream()`, advances actor output pages as output buffers fill, stops when zstd returns 0, and returns total produced bytes.

## State and Persistence Behavior

Each backend stream owns one reusable workspace. Decompression stream state is initialized inside that workspace per call.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_ZSTD`, uses `<linux/zstd.h>`, and sets `alloc_buffer = 1` for direct actor fallback behavior.

## Risks and Edge Cases

Workspace sizing must match the maximum possible block/window. The total output accounting subtracts prior `out_buf.pos` before each stream call and adds the new position; regressions here would produce wrong byte counts and failed page reads. Running out of actor pages before stream completion is `-EIO`.

## Test Signals

Zstd image reads across block sizes, corrupt streams, direct mode with page gaps, parallel multi-stream reads, and memory-pressure initialization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/squashfs/zstd_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/stack.c -->
# sources/distributed-fs/ceph-client/fs/stack.c

## Purpose

`stack.c` provides helper functions for stackable filesystems to copy size and attributes from a lower inode to an upper inode.

## Important APIs, Types, and Functions

Exports are `fsstack_copy_inode_size()` and `fsstack_copy_attr_all()`.

## Control Flow

`fsstack_copy_inode_size()` reads lower `i_size` with `i_size_read()`, conditionally locks the source for wide `i_blocks`, then conditionally locks the destination while writing size and block count on architectures where torn reads/writes are possible. `fsstack_copy_attr_all()` copies mode, uid, gid, rdev, atime/mtime/ctime, block bits, flags, and link count.

## State and Persistence Behavior

It mutates only the destination inode fields supplied by callers. There is no persistent module-private state.

## Dependencies and Integration Points

Used by stackable filesystems through exported GPL symbols. It relies on inode locking conventions and VFS timestamp helpers.

## Risks and Edge Cases

The size helper intentionally does not try to make lower `i_size` and `i_blocks` perfectly atomic together. Correctness on 32-bit SMP/preempt systems depends on conditional `i_lock` use around wide fields.

## Test Signals

Stacked filesystem tests on 32-bit and 64-bit builds, concurrent lower-file growth/shrink observations, stat output comparisons, and lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/stat.c -->
# sources/distributed-fs/ceph-client/fs/stat.c

## Purpose

`stat.c` implements VFS attribute retrieval and the user-facing stat/readlink/statx syscall family, including old/new/64-bit/compat ABI conversions and inode block-byte accounting helpers.

## Important APIs, Types, and Functions

Important exported helpers are `fill_mg_cmtime()`, `generic_fillattr()`, `generic_fill_statx_attr()`, `generic_fill_statx_atomic_writes()`, `vfs_getattr_nosec()`, `vfs_getattr()`, `vfs_fstat()`, inode byte accounting helpers, and syscall entry points for stat variants and `statx`. Internal helpers include `statx_lookup_flags()`, `vfs_statx_path()`, `vfs_statx_fd()`, `vfs_statx()`, ABI copy helpers (`cp_old_stat`, `cp_new_stat`, `cp_new_stat64`, `cp_statx`, compat copies), and `do_readlinkat()`.

## Control Flow

Attribute queries resolve a path or fd, call security hooks when appropriate, then dispatch to filesystem `getattr` or `generic_fillattr()`. `vfs_statx_path()` augments results with mount id and mount-root attribute. Syscalls convert `struct kstat` into the requested user ABI while checking overflow. `readlinkat` resolves the path without following symlinks, checks security, touches atime, and calls `vfs_readlink()`. Inode byte helpers update `i_blocks`/`i_bytes` with or without caller-held locks.

## State and Persistence Behavior

Most functions return snapshots of inode/mount state. `fill_mg_cmtime()` can set the queried bit in multigrain ctime state. `touch_atime()` may update atime. Inode byte accounting functions mutate inode block accounting. No file-private persistent state is owned by this module.

## Dependencies and Integration Points

This file is central VFS infrastructure and integrates with path lookup, mount id handling, security hooks, idmapped mounts, block device statx, filesystem `getattr`, user copy APIs, compat syscall wiring, and timestamp tracing.

## Risks and Edge Cases

ABI overflow checks are critical for old and 32-bit layouts. `AT_EMPTY_PATH`, automount/no-follow flags, statx reserved masks, sync flag validation, idmapped uid/gid conversion, multigrain timestamp queried bits, and stale NFS retry behavior are all sensitive. User copy errors must return `-EFAULT`.

## Test Signals

LTP stat/readlink/statx suites, compat syscall tests, idmapped mount stat tests, automount/symlink/no-follow cases, large inode/file/device number overflow tests, multigrain timestamp tracing, and inode byte accounting tests under concurrent updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/statfs.c -->
# sources/distributed-fs/ceph-client/fs/statfs.c

## Purpose

`statfs.c` implements VFS filesystem-stat queries and the statfs/fstatfs/ustat syscall family, including native, 64-bit, and compat ABI conversions.

## Important APIs, Types, and Functions

Public helpers are `vfs_get_fsid()`, `vfs_statfs()`, `user_statfs()`, and `fd_statfs()`. Internal helpers include `flags_by_mnt()`, `flags_by_sb()`, `calculate_f_flags()`, `statfs_by_dentry()`, `do_statfs_native()`, `do_statfs64()`, `vfs_ustat()`, and compat copy/syscall helpers.

## Control Flow

Path-based syscalls resolve a pathname with follow/automount lookup flags and retry on stale dentries. FD-based syscalls get the file path from the descriptor. Both call `vfs_statfs()`, which invokes the filesystem `statfs` super operation after `security_sb_statfs()` and then fills mount/superblock flags. ABI helpers copy `kstatfs` into user layouts with overflow checks where fields may be narrower.

## State and Persistence Behavior

The code returns snapshots of superblock and mount state. It does not mutate filesystem state. `f_flags` is synthesized from mount and superblock flags for each query.

## Dependencies and Integration Points

It integrates with VFS path/fd lookup, superblock `s_op->statfs`, LSM security hooks, user copy, compat syscall tables, `user_get_super()` for `ustat`, and mount flag definitions.

## Risks and Edge Cases

Filesystems without `statfs` return `-ENOSYS`. 32-bit ABI overflow detection must handle fields where `-1` is an accepted sentinel for files/free files. `statfs64` size arguments must match the ABI struct size. Stale path retry behavior matters for network filesystems.

## Test Signals

LTP statfs/fstatfs/ustat tests, compat syscall tests, mount flag visibility tests, overflow cases with huge filesystems, security hook denial tests, and filesystems with missing or custom `statfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/statfs.c -->
