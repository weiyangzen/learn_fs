# subset-b-005675 Research

Grouped research for the requested source files. Each section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/direct-io.c -->
## sources/distributed-fs/ceph-client/fs/iomap/direct-io.c

Purpose: implements iomap direct I/O read/write submission and completion, exporting `__iomap_dio_rw`, `iomap_dio_rw`, `iomap_dio_complete`, `iomap_dio_bio_end_io`, and `iomap_finish_ioend_direct`. It translates filesystem iomaps into bios, handles holes/inline data/unwritten extents, and bridges synchronous kiocb, async kiocb, polled I/O, bounce buffers, fscrypt, integrity payloads, and filesystem completion hooks.

Important types and APIs: private `struct iomap_dio` tracks the kiocb, iomap DIO ops, current `i_size`, completed size, atomic bio references, flags, first error, partial-progress accounting, and either submission state or async work. Private flags encode write, completion work, write-through, sync, invalidate suppression, and user-backed iter status. `iomap_dio_alloc_bio`, `iomap_dio_submit_bio`, `iomap_dio_bio_iter_one`, and `iomap_dio_bio_iter` are the core bio path. Filesystems integrate through `struct iomap_ops` and optional `struct iomap_dio_ops` callbacks such as `submit_io`, `end_io`, and `bio_set`.

Control flow: `__iomap_dio_rw` validates length, allocates `iomap_dio`, sets `IOMAP_NOWAIT`/`IOMAP_WRITE`/`IOMAP_ATOMIC`, serializes reads against writeback, invalidates page cache before writes, starts `inode_dio_begin`, and loops `iomap_iter`. Each extent is dispatched by `iomap_dio_iter`: holes and read-side unwritten extents zero the user iterator, mapped and write-side unwritten extents build bios, and inline data copies through `iomap_inline_data`. Completion drops the submission reference; synchronous callers sleep until `submit.waiter` is cleared, while async callers either complete inline or on `s_dio_done_wq`.

State and persistence: the file does not maintain persistent metadata itself, but it enforces persistence semantics for direct writes. It may zero head/tail sub-block regions for new/unwritten or EOF-extending writes to avoid stale exposure. It chooses FUA for pure datasync overwrites when the device supports it, otherwise sets `IOMAP_DIO_NEED_SYNC` so `generic_write_sync` runs after data I/O. It updates `ki_pos`, ends inode DIO, and reports direct-I/O fs errors through `fserror_report_io`.

Dependencies and integration points: depends on block bios, blk-crypto, fscrypt, bio integrity, folio/page-cache invalidation, task I/O accounting, iomap iterator helpers, and tracepoints. It integrates with buffered I/O correctness through pre/post direct-write invalidation and with iomap ioend completion for filesystems that wrap direct bios in `iomap_ioend`.

Risks and test signals: high-risk areas are races between submission and bio completion, page-cache invalidation fallback to `-ENOTBLK`, partial DIO retry accounting, AIO completion context, user-backed dirty-page tracking, atomic write full-length enforcement, and zeroing around unwritten/new blocks. Useful tests include direct reads over holes/unwritten extents, mmap versus DIO write races, O_DSYNC/O_SYNC writes on devices with and without FUA, NOWAIT invalidation failure, async direct write extending EOF, integrity-enabled DIO, fscrypt DIO, atomic write rejection for split mappings, and partial-page-fault retry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/direct-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/fiemap.c -->
## sources/distributed-fs/ceph-client/fs/iomap/fiemap.c

Purpose: provides generic iomap-backed file extent reporting and legacy block mapping. `iomap_fiemap` converts filesystem-provided iomaps into FIEMAP extents for userspace, while `iomap_bmap` implements the old `->bmap` sector query.

Important APIs: `iomap_to_fiemap` maps iomap types to `FIEMAP_EXTENT_*` flags: holes are skipped, delalloc becomes DELALLOC/UNKNOWN, unwritten becomes UNWRITTEN, inline becomes DATA_INLINE, and shared/merged iomap flags propagate. `iomap_fiemap_iter` delays emission by one extent so the final extent can be marked `FIEMAP_EXTENT_LAST`. `iomap_bmap` flushes dirty mapping data with `filemap_write_and_wait` before looking up one block.

Control flow: `iomap_fiemap` calls `fiemap_prep`, creates an `iomap_iter` with `IOMAP_REPORT`, scans mappings via `iomap_iter`, emits the previous non-hole mapping, and after the loop emits the last mapping with LAST. `-ENOENT` from an inode with no mapping is tolerated as empty output. `iomap_bmap` requests a single block-sized mapping and returns the physical block number only for `IOMAP_MAPPED`.

State and persistence: no durable state is changed, but `iomap_bmap` forces writeback before exposing a physical block number. FIEMAP output is a snapshot of filesystem mapping state supplied by callbacks, including delalloc and shared extent status.

Dependencies and integration points: integrates with VFS FIEMAP, block-device mapping consumers, and filesystem `iomap_ops`. It relies on `iomap_iter_advance_full` to make progress over whole mappings.

Risks and test signals: risks include incorrect last-extent marking, exposing stale mappings if filesystem callbacks do not synchronize, and legacy bmap returning 0 for both holes and errors. Test with sparse files, inline data, delayed allocation, unwritten extents, shared/reflink extents, empty mapping callbacks, and bmap after dirty buffered writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/fiemap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/internal.h -->
## sources/distributed-fs/ceph-client/fs/iomap/internal.h

Purpose: private header shared by iomap implementation files. It defines internal batching and helper declarations that are not part of the public `linux/iomap.h` API.

Important APIs/types: `IOEND_BATCH_SIZE` limits buffered/direct ioend completion batching. `iomap_max_bio_size` returns `BIO_MAX_SIZE` normally, but for `IOMAP_F_INTEGRITY` uses `max_integrity_io_size(bdev_limits(iomap->bdev))` so integrity metadata allocations remain bounded. It declares `iomap_finish_ioend_buffered_read`, `iomap_finish_ioend_direct`, and `iomap_bio_read_folio_range_sync`; the latter has a `CONFIG_BLOCK` stub returning `-EIO`.

Control flow and state: this header has no runtime control flow or persistent state, but its inline helper shapes bio sizing in both direct and buffered writeback paths.

Dependencies and integration points: depends on block-layer bio limits, integrity support, and the internal `struct iomap_ioend` used across iomap read/write completion files. The `CONFIG_BLOCK` guard lets non-block builds compile callers with a clear failure path.

Risks and test signals: bio size mistakes can cause integrity-buffer over-allocation or excessive latency. Test signals are integrity-enabled writeback/direct-I/O workloads, very large bios, and non-`CONFIG_BLOCK` compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/ioend.c -->
## sources/distributed-fs/ceph-client/fs/iomap/ioend.c

Purpose: manages `iomap_ioend` lifecycle for buffered writeback, buffered reads, direct ioend completion, ioend merging, sorting, splitting, and bioset initialization. It exports the shared `iomap_ioend_bioset`.

Important APIs: `iomap_init_ioend` initializes an ioend embedded in a bio. `iomap_ioend_writeback_submit` finalizes and submits writeback bios, including integrity generation. `iomap_add_to_ioend` batches dirty folio ranges into ioends. `iomap_finish_ioends`, `iomap_ioend_try_merge`, `iomap_sort_ioends`, and `iomap_split_ioend` provide completion batching and filesystem post-processing helpers.

Control flow: dirty folio writeback calls `iomap_add_to_ioend`, which decides ioend flags from iomap type and flags, submits the previous ioend if merging is unsafe, allocates a new bio-backed ioend, and adds the folio. Completion enters `ioend_writeback_end_bio`; errors are pushed to `failed_ioend_work` to avoid nested locking in fs-error reporting, while success finishes folio writeback immediately. `iomap_finish_ioend` collapses child split ioends into the parent, records the first error, verifies read integrity, and dispatches to direct/read/write finishers.

State and persistence: ioends hold transient state: inode, logical offset/size, starting sector, flags, parent pointer, error, and list links. Persistence is through submitted block I/O and later filesystem completion; EOF-extending writeback clamps `io_size` to incore EOF to avoid recovery exposing zero padding. Checkpoint-like durability is not owned here, but ordering and completion state directly affect writeback correctness.

Dependencies and integration points: depends on buffer/page writeback, cgroup writeback accounting, block bios, integrity helpers, list sorting, and iomap tracepoints. Filesystems supply `iomap_writepage_ctx` ops and may use splitting for zone append or maximum extent limits.

Risks and test signals: risks include merging ioends with incompatible completion work, long completion stalls, parent/child split accounting, stale EOF size on appends, error handling from workqueue context, and integrity verification failure. Test with unwritten/shared extents, dropbehind folios, boundary extents, zone append splits, physical discontinuity, writeback errors, integrity-enabled read/write, and concurrent appending writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/ioend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/iter.c -->
## sources/distributed-fs/ceph-client/fs/iomap/iter.c

Purpose: implements the generic `iomap_iter` state machine used by direct I/O, buffered I/O, fiemap, seeking, swap activation, and other iomap consumers.

Important APIs: `iomap_iter_advance` moves `iter->pos` and reduces `iter->len` with a bounds assertion. `iomap_iter` calls filesystem `iomap_begin` and optional `iomap_end`, resets mapping state between iterations, releases folio batches for `IOMAP_F_FOLIO_BATCH`, and traces destination/source maps.

Control flow: the first call enters `begin` because no current iomap exists. Subsequent calls compute bytes advanced since `iter_start_pos`, call `iomap_end` with the trimmed original mapping range, normalize old positive statuses to `-EIO`, and decide whether to stop on error, zero length, or no progress. Stale mappings (`IOMAP_F_STALE`) may be reprocessed even without progress. A fresh `iomap_begin` then fills `iter->iomap` and `iter->srcmap`.

State and persistence: runtime state lives in `struct iomap_iter`: position, remaining length, status, current mappings, start position, optional folio batch, and caller flags. No durable state is changed directly; persistence semantics are delegated to callers and filesystem ops.

Dependencies and integration points: relies on filesystem `iomap_ops`, public iomap helpers such as `iomap_length` and `iomap_length_trim`, folio-batch lifetime rules, and tracepoints. All iomap clients depend on the progress contract: callers must set `iter.status` or advance the iterator.

Risks and test signals: no-progress loops, stale mapping retry behavior, incorrect `iomap_end` byte counts, and leaked folio batches are primary risks. Test with filesystem callbacks that return holes, stale mappings, short advances, errors after partial progress, and folio-batch mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/seek.c -->
## sources/distributed-fs/ceph-client/fs/iomap/seek.c

Purpose: implements generic `SEEK_HOLE` and `SEEK_DATA` for iomap filesystems.

Important APIs: `iomap_seek_hole` and `iomap_seek_data` scan from a requested offset to EOF with `IOMAP_REPORT`. Helpers treat `IOMAP_HOLE`, `IOMAP_UNWRITTEN`, and data mappings differently. For unwritten extents, page-cache state is queried with `mapping_seek_hole_data` because dirty cached data can make an otherwise unwritten extent contain visible data.

Control flow: both entry points reject negative or EOF-and-beyond positions with `-ENXIO`. Hole seek advances over mapped data, returns immediately for holes, and probes unwritten extents for cached holes. Data seek advances over holes, probes unwritten extents for cached data, and returns the first non-hole mapping position. If no data is found before EOF, data seek returns `-ENXIO`; hole seek returns EOF.

State and persistence: no state is persisted. Results reflect a combination of filesystem extent mappings and current page-cache state, so they are snapshot-like and can race with writes.

Dependencies and integration points: uses VFS seek semantics, iomap report callbacks, and page-cache hole/data scanning. Filesystems wire these helpers into `llseek` implementations.

Risks and test signals: correctness depends on treating unwritten extents with dirty cache accurately. Test sparse files, unwritten preallocation with and without cached writes, EOF boundary cases, negative offsets, and concurrent buffered writes while seeking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/seek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/swapfile.c -->
## sources/distributed-fs/ceph-client/fs/iomap/swapfile.c

Purpose: validates and activates iomap-backed swapfiles by translating file extents into page-aligned physical swap extents.

Important types and APIs: `struct iomap_swapfile_info` accumulates contiguous physical iomaps, tracks the swap info, lowest/highest physical pages, total pages, extent count, and file for diagnostics. `iomap_swapfile_activate` is the exported entry point. `iomap_swapfile_add_extent` trims physical byte ranges to page boundaries and calls `add_swap_extent`.

Control flow: activation first `vfs_fsync`s the swap file so mapping metadata is committed. It iterates the page-aligned file size with `IOMAP_REPORT`. `iomap_swapfile_iter` accepts only mapped or unwritten extents, rejects inline, holes, dirty/uncommitted, shared, and non-main-device mappings, and merges physically contiguous ranges before adding extents. After iteration, it adds the final accumulated extent, rejects files with no usable page, and updates `pagespan`, `sis->max`, and `sis->pages`.

State and persistence: the function modifies swap subsystem state through `add_swap_extent` and final `swap_info_struct` fields. It relies on prior fsync to make extent metadata persistent enough for swap use and records physical page span information used by memory management.

Dependencies and integration points: integrates with `swapon`, filesystem iomap reporting, block-device identity, and swap extent accounting. It is intentionally conservative because swap cannot tolerate COW, delayed allocation, holes, or moving extents.

Risks and test signals: risks are accepting unstable extents, mishandling page alignment, off-by-one treatment of the swap header page, and multi-device files. Test with sparse files, unwritten preallocated files, reflink/shared files, dirty delalloc metadata, inline data, extents not page-aligned, files smaller than a page, and files crossing devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/swapfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/trace.c -->
## sources/distributed-fs/ceph-client/fs/iomap/trace.c

Purpose: tracepoint definition translation unit for iomap. It defines `CREATE_TRACE_POINTS` after including the public helpers needed by `trace.h`, causing the trace events declared there to be emitted exactly once.

Important APIs: includes `linux/iomap.h` and then `"trace.h"`. There are no callable functions or exported symbols in this file.

Control flow, state, and persistence: no runtime control flow beyond static tracepoint registration generated by the trace infrastructure. It stores no filesystem state and changes no persistent data.

Dependencies and integration points: depends on Linux tracepoint generation conventions. Other iomap files include `trace.h` normally; this file is the single definition site.

Risks and test signals: risks are build/link failures if trace events are defined in multiple translation units or not defined at all. Test signal is successful kernel build with tracing enabled and visible iomap events under tracing infrastructure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/trace.h -->
## sources/distributed-fs/ceph-client/fs/iomap/trace.h

Purpose: declares iomap tracepoints for readpage/readahead, range operations, iterator mappings, ioend additions, direct-I/O begin/completion, and iterator calls.

Important APIs: defines event classes `iomap_readpage_class`, `iomap_range_class`, and `iomap_class`, plus concrete events such as `iomap_readpage`, `iomap_readahead`, `iomap_writeback_folio`, `iomap_dio_invalidate_fail`, `iomap_dio_rw_queued`, `iomap_iter_dstmap`, `iomap_iter_srcmap`, `iomap_add_to_ioend`, `iomap_iter`, `iomap_dio_rw_begin`, and `iomap_dio_complete`. String tables cover iomap types, iterator flags, iomap flags, and DIO flags.

Control flow: no filesystem logic; tracepoint macros define data capture and print formatting. Events collect device/inode identifiers, offsets, lengths, mapping type/flags, bdev, kiocb flags, AIO status, errors, and return values.

State and persistence: trace events are observational only. They can expose runtime state to tracing buffers but do not mutate filesystem or I/O state.

Dependencies and integration points: integrates with the Linux trace subsystem and uses VFS/inode fields, iomap structures, and `TRACE_IOCB_STRINGS`. `trace.c` supplies `CREATE_TRACE_POINTS`.

Risks and test signals: risks include stale enum string tables, missing new flags, format mismatches, and excessive trace overhead when enabled. Test with ftrace/perf tracepoint listing and sample workloads for direct I/O, writeback, and fiemap/seek iterator activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/Kconfig -->
## sources/distributed-fs/ceph-client/fs/isofs/Kconfig

Purpose: defines build-time configuration for ISO 9660 filesystem support and optional Joliet and zisofs extensions.

Important options: `ISO9660_FS` is a tristate selecting `BUFFER_HEAD`; it enables the `isofs` module or built-in driver. `JOLIET` depends on `ISO9660_FS` and selects `NLS` for Microsoft Unicode filename extensions. `ZISOFS` depends on `ISO9660_FS` and selects `ZLIB_INFLATE` for transparent decompression.

Control flow and state: no runtime control flow. These symbols determine which source files are compiled and which code paths in `inode.c`, `dir.c`, `namei.c`, `rock.c`, and `compress.c` are enabled.

Dependencies and integration points: integrates with kernel Kconfig, module naming, NLS, zlib inflate, and buffer-head based block reading.

Risks and test signals: risk is a missing select or dependency causing compile failures when optional features are enabled independently. Test matrix should build ISOFS built-in/module, with and without Joliet, and with and without zisofs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/Makefile -->
## sources/distributed-fs/ceph-client/fs/isofs/Makefile

Purpose: declares the ISOFS object composition for kbuild.

Important build rules: `obj-$(CONFIG_ISO9660_FS) += isofs.o`; the base object links `namei.o inode.o dir.o util.o rock.o export.o`. `joliet.o` is conditional on `CONFIG_JOLIET`; `compress.o` is conditional on `CONFIG_ZISOFS`.

Control flow and state: no runtime state. The file controls feature-dependent linkage and therefore whether optional APIs such as `get_joliet_filename` and `zisofs_aops` exist.

Dependencies and integration points: integrates with Kconfig symbols and the kernel module build. The base object must include Rock Ridge support unconditionally because Rock Ridge is core ISOFS behavior controlled at mount time.

Risks and test signals: build risk is unresolved symbols if conditional objects do not match preprocessor guards. Test by compiling all combinations of `ISO9660_FS`, `JOLIET`, and `ZISOFS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/compress.c -->
## sources/distributed-fs/ceph-client/fs/isofs/compress.c

Purpose: implements zisofs transparent decompression for compressed ISOFS regular files.

Important APIs and state: exports `zisofs_aops` with `.read_folio = zisofs_read_folio`, plus `zisofs_init` and `zisofs_cleanup`. Global `zisofs_zlib_workspace` is allocated with `vmalloc` at module init and protected by `zisofs_zlib_lock` because zlib inflate workspace is shared. `zisofs_sink_page` discards decompressed output for cache pages that could not be allocated for readahead.

Control flow: `zisofs_read_folio` determines the compression block containing the requested page, allocates an array of cache pages for the compression block, opportunistically grabs neighboring pages, and calls `zisofs_fill_pages`. `zisofs_fill_pages` reads the zisofs block-pointer table, then repeatedly calls `zisofs_uncompress_block` for compressed chunks. The decompressor pre-reads all block buffers, locks zlib, inflates into page mappings or the sink page, marks completed pages uptodate, zero-fills partial tail pages, and reports only whether the critical requested page succeeded.

State and persistence: no on-disk writes occur. Persistent state is the Rock Ridge ZF metadata parsed elsewhere into `ISOFS_I(inode)->i_format_parm` and `i_size`. Runtime state includes page-cache uptodate bits and decompressed folio contents.

Dependencies and integration points: depends on `isofs_get_blocks`, `isofs_bread`, zlib inflate, buffer heads, page cache, and Rock Ridge ZF parsing in `rock.c`. It intentionally has no bmap support for compressed files.

Risks and test signals: risks are malicious or corrupt compressed block tables, block_start/block_end inversion, compressed size exceeding deflate bounds, shared zlib serialization, pages outside EOF, and partial success semantics for readahead pages. Test with valid zisofs media, empty compressed blocks, truncated pointer tables, corrupt compressed streams, large compression blocks, OOM while grabbing readahead pages, and reads near EOF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/dir.c -->
## sources/distributed-fs/ceph-client/fs/isofs/dir.c

Purpose: implements ISOFS directory iteration and basic ISO filename translation.

Important APIs: `isofs_name_translate` lowercases ISO names, removes trailing `.;1` or `;1`, and maps remaining semicolons or slash characters to dots. `get_acorn_filename` handles Acorn extension metadata. `isofs_readdir` allocates a temporary page, then delegates to `do_isofs_readdir`. It exports `isofs_dir_operations` and `isofs_dir_inode_operations`.

Control flow: directory iteration walks `ctx->pos` by filesystem block and offset, reads blocks with `isofs_bread`, handles zero-length records by advancing to the next ISO sector, copies split records into a temporary buffer, validates entry lengths, normalizes inode numbers for first directory entries, skips multi-extent continuation records, emits dot/dotdot specially, applies hide/showassoc filters, resolves Rock Ridge names first, then Joliet/Acorn/normal mapping, and calls `dir_emit`.

State and persistence: ISOFS is read-only, so no persistent state changes. Runtime state is `ctx->pos`, temporary translation buffers, and emitted dcache-visible names/inode numbers.

Dependencies and integration points: integrates with VFS directory iteration, `isofs_lookup`, Rock Ridge/Joliet/Acorn name helpers, mount options in `isofs_sb_info`, and buffer-head block reads.

Risks and test signals: directory records are untrusted media data. Risks include split-record copying, malformed lengths, high-sierra flag offsets, continuation handling, hidden/associated filtering, and name translation buffer limits. Test with plain ISO, Rock Ridge names, Joliet names, Acorn metadata, hidden/associated entries, split directory records across blocks, continuation records, and corrupt short records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/export.c -->
## sources/distributed-fs/ceph-client/fs/isofs/export.c

Purpose: implements NFS export operations for ISOFS because ISOFS uses `iget5_locked` with block/offset inode identity instead of default iget-compatible inode numbers.

Important APIs/types: `isofs_export_ops` supplies `.encode_fh`, `.fh_to_dentry`, `.fh_to_parent`, and `.get_parent`. `struct isofs_fid` stores block, offset, parent offset, generation, parent block, and parent generation. `isofs_export_iget` validates block bounds, reconstitutes an inode with `isofs_iget`, checks generation if supplied, and returns an alias dentry.

Control flow: file handles encode the normalized directory-entry block and offset, plus optional parent identity. Parent lookup relies on the invariant that directory inode identity points to the `.` entry at offset zero; it reads the directory block, steps to the second entry (`..`), validates it, normalizes it, and igets the parent.

State and persistence: no writes. Exported file handles persist identity externally in NFS clients; correctness depends on stable block/offset mapping and generation checks.

Dependencies and integration points: integrates with VFS exportfs, ISOFS inode normalization in `isofs.h`, and NFS file-handle size constraints, including an NFSv2-friendly packed offset layout.

Risks and test signals: risks include stale handles, non-normalized directory inodes, invalid parent records, block bounds, and 16-bit offset packing limitations. Test NFS export of directories/files, reconnect after dcache eviction, parent lookup from child directories, generation mismatch, and malformed media with bad `..` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/inode.c -->
## sources/distributed-fs/ceph-client/fs/isofs/inode.c

Purpose: core ISOFS superblock, mount option, inode, block mapping, and module lifecycle implementation.

Important APIs/types: defines `struct isofs_options`, super operations, dentry operations, address-space operations for normal files, inode cache allocation, fs-context operations, and `iso9660_fs_type`. Mount parsing supports Rock Ridge/Joliet toggles, hide/showassoc, `cruft`, `uid`, `gid`, `mode`, `dmode`, `iocharset`, `session`, `sbsector`, block size, and `nocompress`. Exported internal APIs include `isofs_get_blocks`, `isofs_bread`, and `__isofs_iget`.

Control flow: `isofs_fill_super` validates device block size, finds the volume descriptor from explicit sbsector or CD multisession data, detects ISO/High Sierra/Joliet descriptors, enforces read-only mount, sets block size/time bounds/maxbytes, loads NLS for Joliet, initializes `isofs_sb_info`, reads the root inode, chooses Rock Ridge versus Joliet fallbacks for broken media, sets dentry comparison rules, and creates the root dentry. `isofs_read_inode` reads the directory record, handles split records, sets mode/uid/gid/times/extent/size, processes Level 3 multi-extent files, applies Rock Ridge overrides, and installs file/dir/symlink/special inode operations.

State and persistence: ISOFS is read-only; persistent state is only read from media. Runtime state includes superblock options, inode cache entries with directory-record identity, mapped section chains for multi-extent files, and page-cache address-space ops. `isofs_get_blocks` maps logical file blocks across Level 3 sections and never allocates.

Dependencies and integration points: uses fs_context, block devices, cdrom multisession ioctls, NLS, mpage read/readahead, exportfs, Rock Ridge, Joliet, zisofs, and VFS inode/dentry operations.

Risks and test signals: major risks are untrusted descriptor parsing, block-size mismatches, broken-media fallbacks, multi-extent loops, High Sierra flag offsets, permission override semantics, and optional feature interactions. Test plain ISO, High Sierra, Joliet-only, Rock Ridge plus Joliet, broken empty primary root, multisession media, Level 3 multi-extent files, compressed files, symlinks/devices from Rock Ridge, read-only remount, and malformed descriptors/records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/isofs.h -->
## sources/distributed-fs/ceph-client/fs/isofs/isofs.h

Purpose: private ISOFS header defining in-memory inode/superblock state, numeric decoding helpers, prototypes, and inode identity normalization.

Important types and APIs: `enum isofs_file_format` distinguishes normal, sparse, and compressed files. `struct iso_inode_info` stores iget block/offset, first extent, file format parameters, Level 3 next-section identity, section size, and embedded VFS inode. `struct isofs_sb_info` stores volume sizing, Rock Ridge/Joliet/mapping/check/session flags, ownership/mode defaults, compression behavior, and NLS table. Inline `isonum_*` helpers decode ISO little/big/both-endian numeric fields, intentionally trusting little-endian for some broken-media cases.

Control flow: header logic includes `ISOFS_SB`, `ISOFS_I`, `isofs_iget` wrappers, `isofs_get_ino`, and `isofs_normalize_block_and_offset`. Normalization rewrites directory identities to the `.` entry at extent plus extended-attribute length, offset zero, which underpins stable dcache and NFS export behavior.

State and persistence: defines the runtime state derived from read-only media. No mutations beyond inline calculations. The inode-number scheme encodes metadata block/offset rather than relying on on-disk inode numbers.

Dependencies and integration points: used by all ISOFS C files, VFS inode/dentry/export operations, Rock Ridge/Joliet/zisofs code, and Linux ISO on-disk structure definitions.

Risks and test signals: risks include numeric decoding assumptions, directory normalization invariants, and keeping prototypes consistent with conditional feature compilation. Test with directories reached through parent, dot, and child `..`, NFS export handles, and media generated by tools with inconsistent endian fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/isofs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/joliet.c -->
## sources/distributed-fs/ceph-client/fs/isofs/joliet.c

Purpose: converts Joliet UCS-2 big-endian filenames into Linux-visible names.

Important APIs: `get_joliet_filename` chooses UTF-8 conversion via `utf16s_to_utf8s` when no NLS table is loaded, or `uni16_to_x8` through `nls->uni2char` otherwise. It strips trailing `;1` version suffixes and trailing periods for Windows-compatible behavior.

Control flow: `uni16_to_x8` walks 16-bit characters until NUL or the input character count ends, emits converted bytes or `?` for unmappable characters, and NUL-terminates the output. `get_joliet_filename` passes half the ISO directory name length because Joliet names are 16-bit units.

State and persistence: no persistent state. It reads `s_nls_iocharset` from the mounted superblock and writes a temporary output name buffer used by lookup/readdir.

Dependencies and integration points: depends on `CONFIG_JOLIET`, NLS, UTF-16 helpers, and ISOFS directory/name lookup code.

Risks and test signals: risks are output buffer sizing, odd-length names, unmappable characters, and suffix stripping after multibyte conversion. Test with Unicode names, default UTF-8, explicit legacy iocharset, trailing dot/version suffix, and names containing unmappable characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/joliet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/namei.c -->
## sources/distributed-fs/ceph-client/fs/isofs/namei.c

Purpose: implements directory entry lookup for ISOFS.

Important APIs: `isofs_lookup` allocates a page-sized scratch buffer, calls `isofs_find_entry`, igets the matching inode, and returns `d_splice_alias`. `isofs_cmp` delegates to dentry custom compare operations when present, allowing case-insensitive and Joliet-specific comparisons. `isofs_find_entry` mirrors readdir name resolution for matching.

Control flow: lookup scans the directory from offset zero, reads blocks with `isofs_bread`, handles zero-length sector padding, copies split records, validates name lengths, derives candidate names through Rock Ridge, Joliet, Acorn, normal translation, or raw ISO names, applies hide/showassoc filters, compares against the dentry, normalizes matched block/offset, and returns the identity.

State and persistence: no writes. Lookup populates dcache through returned aliases and depends on stable block/offset inode identity. Temporary page memory carries translated names and split directory records.

Dependencies and integration points: integrates with VFS dcache, dentry operations selected in `inode.c`, Rock Ridge/Joliet/Acorn helpers, `isofs_iget`, and directory-record normalization.

Risks and test signals: lookup and readdir must agree on visible names. Risks include mismatched case folding, hidden/associated option handling, malformed split entries, Rock Ridge ignored entries (`RE`), and scratch-buffer offsets. Test lookup of every name style emitted by readdir, case-insensitive modes, hidden/associated entries, corrupt records, and directories with split entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/rock.c -->
## sources/distributed-fs/ceph-client/fs/isofs/rock.c

Purpose: parses Rock Ridge/SUSP system-use fields for POSIX metadata, alternate names, symlinks, relocated directories, timestamps, device numbers, and zisofs compression metadata.

Important types/APIs: `struct rock_state` tracks the current system-use buffer, continuation extent/offset/size, loop count, and inode. Key functions are `get_rock_ridge_filename`, `parse_rock_ridge_inode`, and symlink aops `isofs_symlink_aops`. Helpers include `check_sp`, `setup_rock_ridge`, `rock_continue`, `rock_check_overflow`, and `get_symlink_chunk`.

Control flow: each parser initializes a rock state from the directory record's system-use area, applies a discovered SP skip offset, then loops SUSP records by signature. CE records trigger bounded continuation reads with strict offset/size/volume checks and a 32-continuation limit. Name parsing consumes NM records, ignores dot/dotdot flags, truncates overlong names, and returns `-1` for relocated entries. Inode parsing processes PX/PN/TF/SL/CL/ZF records, optionally retries after XA attributes, and handles relocated directories by reading the relocation target inode. Symlink reads reconstruct SL components into a folio.

State and persistence: no disk writes. Runtime effects include overriding VFS inode mode, nlink, uid/gid, rdev, times, size, first extent, compressed-file format parameters, and symlink page contents. It also updates superblock Rock Ridge detection state and system-use skip offset.

Dependencies and integration points: depends on `rock.h` record layouts, ISO numeric helpers, `iso_date`, `isofs_iget_reloc`, page-cache symlink read, and optional zisofs support. It is central to POSIX semantics on ISOFS.

Risks and test signals: this is a high-risk untrusted-metadata parser. Risks include record overflow, CE loops, out-of-volume extents, symlink buffer overflow, recursive relocation, malformed ER/NM/TF/SL/ZF lengths, and disabling Rock Ridge incorrectly. Test RRIP media with long NM continuations, symlinks with all component flags, relocated directories, device nodes, timestamps, zisofs ZF records, XA-offset media, corrupt CE extents, and unsupported flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/rock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/rock.h -->
## sources/distributed-fs/ceph-client/fs/isofs/rock.h

Purpose: defines packed SUSP and Rock Ridge record structures and flag constants used by `rock.c`.

Important types: includes `SU_SP_s`, `SU_CE_s`, `SU_ER_s`, RR records for PX, PN, SL, NM, CL, PL, TF, and Linux-specific ZF, plus the top-level `struct rock_ridge` signature/length/version union. `struct SL_component` uses a counted flexible array for symlink components.

Control flow and state: no executable logic. The layouts directly govern how untrusted on-disc system-use bytes are interpreted by the parser. Flag constants define RR capability bits and TF timestamp fields.

Dependencies and integration points: depends on ISO/SUSP/RRIP on-disk formats and is included only by Rock Ridge parsing code.

Risks and test signals: structure packing and minimum-size assumptions are critical. Any layout drift can break parsing or bounds checks. Test with compiler layout validation indirectly through mounting known Rock Ridge images and fuzzing malformed records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/rock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/util.c -->
## sources/distributed-fs/ceph-client/fs/isofs/util.c

Purpose: provides ISO date/time conversion.

Important API: `iso_date(u8 *p, int flags)` converts short ISO directory timestamps or long-form Rock Ridge timestamps into `struct timespec64`. Flags select long form and High Sierra no-timezone behavior.

Control flow: long form parses ASCII year/month/day/hour/minute/second/hundredths and subtracts 1900 from the year. Short form reads binary year offset, month, day, time, and optional timezone byte. Negative years clamp to epoch zero. Otherwise it calls `mktime64`, sign-extends the timezone byte, and subtracts timezone offset only if within +/-52 fifteen-minute units.

State and persistence: pure conversion helper; no state is stored. Results populate inode atime/mtime/ctime elsewhere.

Dependencies and integration points: used by `inode.c` for ISO directory record dates and by `rock.c` for TF records.

Risks and test signals: risks include malformed date fields, timezone sign compatibility, High Sierra handling, and long-form nanosecond scaling. Test with boundary years 1900 and 2155, negative year inputs, timezone extremes, High Sierra records, and Rock Ridge long-form timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/zisofs.h -->
## sources/distributed-fs/ceph-client/fs/isofs/zisofs.h

Purpose: declares the compressed ISOFS interface when `CONFIG_ZISOFS` is enabled.

Important APIs: declares `zisofs_aops`, `zisofs_init`, and `zisofs_cleanup`. The header is included by core inode/module code and the compression implementation.

Control flow and state: no runtime logic. Conditional declarations mirror the optional build path selected by Kconfig/Makefile.

Dependencies and integration points: integrates Rock Ridge ZF parsing and inode operation selection with `compress.c` without exposing compression internals.

Risks and test signals: risk is conditional build mismatch. Test compilation with `CONFIG_ZISOFS=y` and disabled, plus mounting compressed media to verify `zisofs_aops` is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/isofs/zisofs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/Kconfig -->
## sources/distributed-fs/ceph-client/fs/jbd2/Kconfig

Purpose: configures the JBD2 generic journaling layer and optional debugging.

Important options: `JBD2` is a tristate selecting `CRC32`; it is used by ext4 and OCFS2 and may be built-in or modular depending on users. `JBD2_DEBUG` depends on `JBD2` and enables runtime debug output controlled by the `jbd2_debug` module parameter.

Control flow and state: no runtime logic, but config choices enable the entire journaling subsystem and optional debug paths.

Dependencies and integration points: integrates with filesystems requiring JBD2 and with CRC32 checksum support used by journal checksums.

Risks and test signals: build dependency errors would affect ext4/OCFS2. Test by building ext4/OCFS2 with JBD2 built-in and module-compatible configurations, and with debug enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/Makefile -->
## sources/distributed-fs/ceph-client/fs/jbd2/Makefile

Purpose: declares the JBD2 composite object for kbuild.

Important build rules: `obj-$(CONFIG_JBD2) += jbd2.o`; `jbd2-objs` links `transaction.o commit.o recovery.o checkpoint.o revoke.o journal.o`.

Control flow and state: no runtime state. The order and inclusion ensure core transaction, commit, recovery, checkpoint, revoke, and journal-management code are linked into one module/object.

Dependencies and integration points: tied to the `JBD2` Kconfig symbol and consumers such as ext4 and OCFS2.

Risks and test signals: missing object inclusion would cause unresolved symbols or incomplete journaling behavior. Test by compiling JBD2 as module and built-in, and booting/mounting ext4 with journaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/checkpoint.c -->
## sources/distributed-fs/ceph-client/fs/jbd2/checkpoint.c

Purpose: implements JBD2 checkpointing, the process that writes committed metadata buffers back to their home locations and frees journal log space for reuse.

Important APIs: `__jbd2_log_wait_for_space` waits for enough log space, driving checkpoints or waiting for commits. `jbd2_log_do_checkpoint` writes one checkpoint transaction's dirty buffers. `jbd2_cleanup_journal_tail` advances the journal tail after checkpointed data is safe. Checkpoint list APIs include `__jbd2_journal_insert_checkpoint`, `__jbd2_journal_remove_checkpoint`, `jbd2_journal_try_remove_checkpoint`, `jbd2_journal_shrink_checkpoint_list`, `__jbd2_journal_clean_checkpoint_list`, `jbd2_journal_destroy_checkpoint`, and `__jbd2_journal_drop_transaction`.

Control flow: log-space wait drops `j_state_lock` to take `j_checkpoint_mutex`, rechecks space, checkpoints available transactions, tries tail cleanup, waits for a committing transaction, or aborts if no progress is possible. Checkpointing cleans the tail, selects the oldest checkpoint transaction, loops its checkpoint buffers under `j_list_lock`, waits for busy buffers, removes clean buffers, batches dirty buffers into `j_chkpt_bhs`, writes them with block plugging, and retries until the transaction can be released.

State and persistence: persistent correctness hinges on not advancing the journal tail until all relevant home-location writes are durable. With `JBD2_BARRIER`, `jbd2_cleanup_journal_tail` flushes the filesystem device before updating the tail. Runtime state includes circular transaction checkpoint lists, circular buffer checkpoint lists, per-transaction checkpoint stats, `j_shrink_transaction`, and `j_checkpoint_jh_count`.

Dependencies and integration points: depends on buffer-head state, journal locks (`j_state_lock`, `j_list_lock`, `j_checkpoint_mutex`), block flushes, tracepoints, transaction states, and commit code that inserts buffers into checkpoint lists.

Risks and test signals: risks include lock ordering deadlocks, freeing a transaction before `T_FINISHED`, advancing tail after failed checkpoint writes, busy-buffer shrink livelock, and abort-state handling. Test forced small journals, heavy metadata workloads, writeback errors, barrier on/off, unmount during checkpoint, memory pressure shrinker paths, aborted journals, and transactions with buffers relogged into newer transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/checkpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/commit.c -->
## sources/distributed-fs/ceph-client/fs/jbd2/commit.c

Purpose: implements the JBD2 full transaction commit path, writing data dependencies, revoke records, metadata descriptors/data, commit records, checkpoint handoff, callbacks, and transaction statistics.

Important APIs: central entry point is `jbd2_journal_commit_transaction`. Supporting APIs include `jbd2_submit_inode_data`, `jbd2_wait_inode_data`, `jbd2_journal_finish_inode_data_buffers`, `journal_submit_data_buffers`, `journal_finish_inode_data_buffers`, checksum helpers, and commit-record submission/wait helpers. `journal_end_buffer_io_sync` is the end I/O handler for temporary journal buffer_heads.

Control flow: the commit path blocks concurrent fast commits, locks the running transaction, waits for outstanding updates, releases unused reserved buffers, cleans checkpoint lists, switches revoke tables, moves the transaction to flushing/committing states, submits ordered data buffers, writes revoke records, serializes metadata into descriptor-tagged journal blocks, submits journal I/O, waits for metadata/control buffers, writes and waits for the commit block, optionally flushes devices for barriers/async commit, updates the journal tail when safe, processes the forget list into checkpoints or frees buffers, links the transaction onto the checkpoint list, runs callbacks, marks the transaction `T_FINISHED`, and wakes commit waiters.

State and persistence: this is the durable ordering core. It updates transaction states from `T_RUNNING` through `T_LOCKED`, `T_SWITCH`, `T_FLUSH`, `T_COMMIT`, `T_COMMIT_DFLUSH`, `T_COMMIT_JFLUSH`, `T_COMMIT_CALLBACK`, and `T_FINISHED`; advances journal head/tail; writes descriptor, revoke, metadata, and commit blocks; manages frozen/committed buffer copies; maintains inode dirty ranges; and records average commit time/statistics. Barrier and async-commit behavior determine flush/FUA ordering.

Dependencies and integration points: depends on JBD2 transaction/revoke/journal helpers, block I/O, buffer-head shadowing, CRC32/jbd2 checksums, filesystem data-submit callbacks, fast commit coordination, checkpoint code, tracepoints, and callbacks used by ext4/OCFS2.

Risks and test signals: high-risk areas are transaction state races, credit accounting, checksum/tag construction, descriptor space accounting, buffer shadow lifetime, abort cleanup, data=ordered flushing, revoke ordering, device flush ordering for external journals, forget-list races with `journal_unmap_buffer`, and fast/full commit exclusion. Test with fsync-heavy workloads, data writeback errors, external journal devices, async commit, checksums v1/v2/v3, 64-bit block numbers, revoke-heavy deletes/truncates, journal abort injection, small journal pressure, fast commit overlap, and crash-recovery validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jbd2/commit.c -->
