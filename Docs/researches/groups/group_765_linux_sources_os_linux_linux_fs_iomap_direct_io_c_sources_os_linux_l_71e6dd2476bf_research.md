# Group Research: group_765_linux_sources_os_linux_linux_fs_iomap_direct_io_c_sources_os_linux_l_71e6dd2476bf

Scope confirmed against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/direct-io.c -->
# File Research: sources/os/linux/linux/fs/iomap/direct-io.c

Implements iomap-based direct I/O read/write submission and completion. The central object is `struct iomap_dio`, which tracks the `kiocb`, filesystem DIO ops, byte counts, private flags, error state, references for in-flight bios, and either synchronous wait state or async completion work.

Key entry points:
- `__iomap_dio_rw()` creates and submits a direct I/O request and can return a queued `ERR_PTR(-EIOCBQUEUED)`, a completed `iomap_dio`, `NULL`, or an error.
- `iomap_dio_rw()` wraps `__iomap_dio_rw()` and immediately completes synchronous results through `iomap_dio_complete()`.
- `iomap_dio_complete()` applies filesystem `end_io`, reports fs errors, advances `ki_pos`, handles short reads, post-write invalidation, DSYNC writeback, and frees the DIO object.
- `iomap_dio_bio_end_io()` and `iomap_finish_ioend_direct()` bridge block/ioend completions back to DIO refcounting.

Submission flow:
- `__iomap_dio_rw()` initializes `iomap_iter` with `IOMAP_DIRECT`, adds `IOMAP_NOWAIT`, `IOMAP_WRITE`, `IOMAP_ATOMIC`, or `IOMAP_OVERWRITE_ONLY` as needed, invalidates cached pages for writes, initializes the superblock DIO done workqueue for async completions, calls `inode_dio_begin()`, and iterates mappings with `iomap_iter()`.
- `iomap_dio_iter()` dispatches mapping types: holes and unwritten reads are zero-filled, mapped/unwritten writes submit bios, inline extents use iter copy helpers, and delalloc collisions warn and fail.
- `iomap_dio_bio_iter()` validates alignment, selects logical block or filesystem block alignment, handles unwritten/new/shared extents, atomic bio requirements, write-through/FUA optimization, completion-work requirements, sub-block zeroing before and after writes, and iov truncation per extent.
- `iomap_dio_bio_iter_one()` allocates a bio, sets crypto/integrity/ioprio/write hints, pins or bounces iov pages, accounts write bytes, marks user read pages dirty when needed, disables polling for multi-bio I/O, and submits via filesystem `submit_io` or `blk_crypto_submit_bio()`.

Completion behavior:
- Refcounting allows submission and all bio completions to race safely. The final reference calls `iomap_dio_done()`.
- Synchronous completions wake the submitting task; async completions either complete inline or are queued to `s_dio_done_wq`.
- Error completions and writes needing page invalidation or filesystem metadata completion are forced into workqueue context.
- `IOMAP_DIO_WRITE_THROUGH` can suppress later generic sync when all issued writes are FUA or do not need volatile-cache flushes.
- Magic errors `-EAGAIN` and `-ENOTBLK` are treated specially for retry/fallback and not reported through fs error notifications.

Important dependencies:
- Uses iomap iteration from `iter.c`.
- Direct ioend completions are finished by `ioend.c`.
- Tracepoints come from `trace.h`.
- Depends on block crypto, fscrypt bio contexts, bio integrity generation/verification, page-cache invalidation helpers, and `inode_dio_begin/end`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/direct-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/fiemap.c -->
# File Research: sources/os/linux/linux/fs/iomap/fiemap.c

Provides iomap-backed FIEMAP and legacy bmap support.

Key functions:
- `iomap_to_fiemap()` converts one `struct iomap` into FIEMAP extent flags and emits it with `fiemap_fill_next_extent()`. Holes are skipped; delalloc, unwritten, inline, merged, and shared mappings become corresponding FIEMAP flags.
- `iomap_fiemap_iter()` delays emission by one mapping so the final mapping can be marked `FIEMAP_EXTENT_LAST`.
- `iomap_fiemap()` prepares FIEMAP, iterates mappings with `IOMAP_REPORT`, emits the saved final extent, and treats `-ENOENT` as “no mapping”.
- `iomap_bmap()` implements the old `->bmap` interface by flushing dirty mapping pages, asking the filesystem for an `IOMAP_REPORT` mapping of one block, and returning the mapped disk block or zero.

This file is a reporting layer: it does not allocate or submit I/O. It depends on filesystem `iomap_ops` for mapping lookup and on `iomap_iter()` for range traversal.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/fiemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/internal.h -->
# File Research: sources/os/linux/linux/fs/iomap/internal.h

Small internal iomap header shared by iomap implementation files.

Contents:
- Defines `IOEND_BATCH_SIZE` as `4096`, used to bound ioend completion batching.
- Defines `iomap_max_bio_size()`, normally `BIO_MAX_SIZE`, but limited by integrity metadata allocation constraints when `IOMAP_F_INTEGRITY` is set.
- Declares buffered read and direct ioend completion helpers:
  - `iomap_finish_ioend_buffered_read()`
  - `iomap_finish_ioend_direct()`
- Provides a `CONFIG_BLOCK`-guarded declaration or stub for `iomap_bio_read_folio_range_sync()`.

The header centralizes internal limits and cross-file prototypes for `direct-io.c`, `ioend.c`, and buffered iomap code outside this group.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/ioend.c -->
# File Research: sources/os/linux/linux/fs/iomap/ioend.c

Implements iomap `ioend` allocation, writeback submission, completion, merging, sorting, splitting, and checkpoint-style finishing for buffered and direct I/O completions.

Key structures and globals:
- Exports `iomap_ioend_bioset`.
- `iomap_init_ioend()` initializes an `iomap_ioend` embedded in a bio with inode, offset, size, sector, flags, and refcount.

Buffered writeback:
- `iomap_add_to_ioend()` appends dirty folio ranges to the current writeback ioend when physical/logical contiguity, flags, integrity size, and batch limits allow it. Otherwise it submits the current ioend and allocates a new one.
- `iomap_ioend_writeback_submit()` sets the default buffered end-io handler, rejects anonymous writes in this path, generates integrity metadata when needed, and submits the bio.
- `iomap_finish_ioend_buffered_write()` handles writeback errors, reports `FSERR_BUFFERED_WRITE`, finishes folio writeback state, frees integrity payloads, and drops the bio.
- Failed buffered write completions are deferred through a global work item so fs error reporting does not recursively acquire locks from bio completion context.

Generic completion:
- `iomap_finish_ioend()` handles child split ioends, propagates errors, waits for all children via `io_remaining`, verifies read integrity, and dispatches to direct, buffered read, or buffered write finishers.
- `iomap_finish_ioends()` finishes a possibly merged list in task context and yields after large batches.

Merging and sorting:
- `iomap_ioend_can_merge()` allows adjacent write ioends to merge only if status, flags, logical offsets, and physical sectors match.
- `iomap_ioend_try_merge()` chains mergeable ioends behind one head.
- `iomap_sort_ioends()` sorts by file offset.

Splitting:
- `iomap_split_ioend()` splits write ioends for max length or zone append limits, aligns the split to filesystem block size, creates a child ioend, increments parent remaining count, and updates offsets/sectors.

Initialization:
- `iomap_ioend_init()` initializes the bioset at `fs_initcall`.

This file is the bridge between iomap folio writeback/direct I/O and block-layer bio completion, with careful batching to limit completion latency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/ioend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/iter.c -->
# File Research: sources/os/linux/linux/fs/iomap/iter.c

Implements the generic iomap range iterator used by direct I/O, FIEMAP, seek, swapfile activation, and other iomap users.

Key functions:
- `iomap_iter_advance()` advances `iter->pos` and reduces `iter->len`, rejecting advances beyond the current mapping.
- `iomap_iter_clean_fbatch()` releases and reinitializes folio batches when a mapping used `IOMAP_F_FOLIO_BATCH`.
- `iomap_iter_done()` validates mapping invariants, records `iter_start_pos`, and emits destination/source mapping tracepoints.
- `iomap_iter()` drives the two-phase loop:
  - On first entry or after cleanup, calls filesystem `iomap_begin()`.
  - On subsequent entries, computes bytes advanced, calls optional `iomap_end()`, interprets `iter->status`, cleans folio batches, clears previous mappings, and decides whether to continue.

Important semantics:
- Callers loop while return value is positive.
- Leaving `iter.status` unchanged, advancing zero bytes, or exhausting `iter.len` terminates iteration unless a stale mapping is being retried.
- Positive `iter.status` is treated as old invalid semantics and converted to `-EIO`.
- `IOMAP_F_STALE` allows reprocessing when no progress was made.

This file provides the common contract between filesystem mapping providers and iomap consumers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/iter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/seek.c -->
# File Research: sources/os/linux/linux/fs/iomap/seek.c

Implements iomap-based `SEEK_HOLE` and `SEEK_DATA`.

Key functions:
- `iomap_seek_hole()` validates `pos` against `i_size`, iterates mappings with `IOMAP_REPORT`, and returns the first hole position or EOF.
- `iomap_seek_data()` similarly returns the first data position or `-ENXIO`.
- For `IOMAP_UNWRITTEN`, both helpers consult `mapping_seek_hole_data()` over the page cache so dirty cached data inside unwritten extents is considered.
- `IOMAP_HOLE` is immediately a hole and skipped for data.
- Other mapping types are treated as data for `SEEK_DATA` and skipped for `SEEK_HOLE`.

This file layers POSIX seek behavior over filesystem mappings while preserving page-cache-visible data in unwritten regions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/seek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/swapfile.c -->
# File Research: sources/os/linux/linux/fs/iomap/swapfile.c

Implements swapfile activation for filesystems that expose physical extents through iomap.

Key structure:
- `struct iomap_swapfile_info` accumulates physically contiguous mappings, tracks usable page ranges, extent count, and the target `swap_info_struct`.

Main flow:
- `iomap_swapfile_activate()` fsyncs the file first so mappings are committed, iterates the page-aligned file size with `IOMAP_REPORT`, validates mappings, adds the final accumulated extent, rejects files with no usable page, and fills `pagespan`, `sis->max`, and `sis->pages`.
- `iomap_swapfile_iter()` accepts only `IOMAP_MAPPED` or `IOMAP_UNWRITTEN`; rejects inline, holes, dirty/uncommitted metadata, shared extents, and mappings outside the swap device.
- Adjacent physical iomaps are merged before being reported.
- `iomap_swapfile_add_extent()` rounds physical starts up and ends down to page boundaries, skips too-short extents, accounts for the swap header page, updates lowest/highest physical page, and calls `add_swap_extent()`.

This file is strict because swap requires stable, non-shared, page-aligned physical storage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/swapfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/trace.c -->
# File Research: sources/os/linux/linux/fs/iomap/trace.c

Instantiates iomap tracepoints.

It includes `<linux/iomap.h>`, defines `CREATE_TRACE_POINTS`, and includes `trace.h` last so helper definitions and trace event declarations are visible. There is no runtime logic beyond tracepoint generation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/trace.h -->
# File Research: sources/os/linux/linux/fs/iomap/trace.h

Defines the iomap tracepoint ABI used internally for diagnostics. The header explicitly states these tracepoints are not stable kernel ABI.

Trace coverage:
- Read/readahead page count events.
- Range events for writeback, release, invalidate, DIO invalidate failure, queued DIO, and zeroing.
- Iomap mapping events for destination and source mappings, including device, inode, address, offset, length, type, flags, and bdev.
- `iomap_add_to_ioend` for writeback aggregation.
- `iomap_iter` for iterator state, flags, ops pointer, and caller.
- Direct I/O begin and completion events, including inode, size, offset, length, `ki_flags`, DIO flags, async status, error, and return value.

It also defines symbolic strings for iomap types, iterator flags, iomap mapping flags, and public DIO flags, then includes `trace/define_trace.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/Kconfig -->
# File Research: sources/os/linux/linux/fs/isofs/Kconfig

Defines ISO9660 filesystem configuration.

Options:
- `ISO9660_FS`: tristate ISO 9660 CD-ROM filesystem support; selects `BUFFER_HEAD`; module name is `isofs`.
- `JOLIET`: optional Microsoft Joliet Unicode extension support; depends on ISO9660 and selects `NLS`.
- `ZISOFS`: optional transparent decompression extension; depends on ISO9660 and selects `ZLIB_INFLATE`.

The help text documents Rock Ridge support as part of the driver and points to ISOFS documentation/CD-ROM HOWTO material.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/Makefile -->
# File Research: sources/os/linux/linux/fs/isofs/Makefile

Builds the ISO9660 filesystem module/object.

Objects:
- Core `isofs-y`: `namei.o inode.o dir.o util.o rock.o export.o`
- Optional Joliet: `joliet.o`
- Optional zisofs decompression: `compress.o`

The aggregate object is built when `CONFIG_ISO9660_FS` is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/compress.c -->
# File Research: sources/os/linux/linux/fs/isofs/compress.c

Implements transparent zisofs decompression for compressed ISO9660/Rock Ridge files.

Key pieces:
- Uses a global zlib workspace protected by `zisofs_zlib_lock`, avoiding allocation failures during block decompression.
- `zisofs_uncompress_block()` reads compressed filesystem blocks, initializes zlib, inflates one compressed block into one or more page-cache pages, supports sink output for pages not present, marks filled pages uptodate, and handles empty compressed blocks by zeroing pages.
- `zisofs_fill_pages()` locates compressed block pointers from the zisofs header, reads compressed block start/end offsets, validates monotonicity, and calls `zisofs_uncompress_block()` until the requested page is filled.
- `zisofs_read_folio()` determines the compression-block page group, grabs adjacent cache pages opportunistically for readahead-like fill, invokes `zisofs_fill_pages()`, unlocks/releases pages, and returns the critical page error.
- `zisofs_aops` only provides `.read_folio`; bmap is unsupported.
- `zisofs_init()` allocates the zlib workspace; `zisofs_cleanup()` frees it.

The decompressor is read-only and depends on ISOFS block mapping through `isofs_get_blocks()`/`isofs_bread()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/dir.c -->
# File Research: sources/os/linux/linux/fs/isofs/dir.c

Implements ISOFS directory iteration and base ISO name translation.

Key functions:
- `isofs_name_translate()` lowercases ISO names, drops trailing `.;1` or `;1`, and converts remaining `;` or `/` to `.`.
- `get_acorn_filename()` applies Acorn extension naming tweaks when the directory record carries a 32-byte ARCHIMEDES extension.
- `do_isofs_readdir()` walks directory records across ISOFS blocks, handles zero-length records by advancing to the next CD sector, copies split records into a temporary buffer, validates record length, emits `.` and `..`, filters hidden/associated files according to mount options, chooses Rock Ridge, Joliet, Acorn, normal mapping, or raw names, and emits entries with normalized inode numbers.
- `isofs_readdir()` allocates one page for temporary name and directory-entry buffers.
- `isofs_fileattr_get()` reports casefold/case-nonpreserving attributes based on mount/check/mapping mode.

Exports directory file and inode operations:
- `isofs_dir_operations`: llseek, read dir, shared iterate, generic lease.
- `isofs_dir_inode_operations`: lookup and fileattr_get.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/export.c -->
# File Research: sources/os/linux/linux/fs/isofs/export.c

Implements NFS export support for ISOFS, which cannot use default iget-based helpers because ISOFS uses `iget5_locked()` with block/offset identity.

Key functions:
- `isofs_export_iget()` validates block range, gets an inode by block/offset, checks generation, and returns an alias dentry or `-ESTALE`.
- `isofs_export_get_parent()` finds a directory parent by reading the normalized child directory’s `..` entry, normalizing its block/offset, and returning that inode.
- `isofs_export_encode_fh()` encodes block, offset, generation, and optionally parent block/offset/generation. It supports compact NFSv2-sized handles by packing offsets into 16-bit fields.
- `isofs_fh_to_dentry()` and `isofs_fh_to_parent()` decode file handles back to dentries.

Exports `isofs_export_ops` with encode, decode, parent decode, and get_parent hooks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/inode.c -->
# File Research: sources/os/linux/linux/fs/isofs/inode.c

Main ISO9660 filesystem implementation: superblock setup, mount option parsing, inode cache, dentry comparison, block mapping, inode reading, fs registration, and module lifecycle.

Mount/context handling:
- Defines `struct isofs_options` and fs parameter table for `norock`, `nojoliet`, `hide`, `showassoc`, `cruft`, `utf8`, `iocharset`, `map`, `session`, `sbsector`, `check`, uid/gid, mode/dmode, `overriderockperm`, block size, and `nocompress`.
- `isofs_init_fs_context()` sets defaults: normal mapping, Rock Ridge and Joliet enabled, blocksize 1024, unset modes, root uid/gid, auto check mode, no specific session/sbsector.
- `isofs_parse_param()` parses options for initial mount only.
- `isofs_reconfigure()` allows readonly reconfiguration only.
- `isofs_show_options()` reconstructs effective mount options.

Superblock setup:
- `isofs_fill_super()` validates block size, resolves multisession start, scans volume descriptors, detects ISO, High Sierra, and Joliet supplementary descriptors, enforces readonly, sets zone size and maximum file size, sets time range, possibly switches to Joliet root, loads NLS, initializes `isofs_sb_info`, reads root inode, chooses Rock Ridge over Joliet unless disabled/broken, installs dentry ops, export ops, super ops, and root dentry.
- Handles broken media cases where primary/Rock Ridge root is unusable or empty but Joliet root works.

Dentry operations:
- Case-sensitive and case-insensitive hash/compare variants exist, plus Joliet/MS variants that ignore trailing periods.
- Selected based on Joliet level and `check=relaxed`.

Block mapping and read path:
- `isofs_get_blocks()` maps logical file blocks to disk blocks, following ISO9660 Level 3 multi-extent sections through chained inodes and limiting runaway chains.
- `isofs_get_block()`, `isofs_bmap()`, `isofs_bread()`, `_isofs_bmap()`, `isofs_read_folio()`, and `isofs_readahead()` provide buffer-head/mpage read support.
- `isofs_aops` supports read_folio, readahead, and bmap.

Inode reading:
- `isofs_read_inode()` reads the directory record, handles records spanning blocks, assigns inode number from normalized block/offset, sets default file/dir modes, uid/gid, timestamps, extent, size, blocks, and multi-extent metadata.
- Applies `cruft` size truncation, rejects interleaved file data by zeroing size, invokes Rock Ridge parser for POSIX metadata/symlinks/devices/compression, then applies mount overrides for uid/gid/modes.
- Installs operations for regular files, directories, symlinks, and special files. Compressed files use `zisofs_aops`; symlinks use `isofs_symlink_aops`.

Inode identity:
- `__isofs_iget()` uses `iget5_locked()` keyed by metadata block and offset. Directory block/offset normalization makes aliases stable for lookup and NFS export.

Lifecycle:
- Creates/destroys `isofs_inode_cache`.
- Initializes optional zisofs support.
- Registers `iso9660` filesystem with `FS_REQUIRES_DEV`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/isofs.h -->
# File Research: sources/os/linux/linux/fs/isofs/isofs.h

Private ISOFS header defining in-memory inode/superblock structures, endian-number helpers, prototypes, and inode numbering helpers.

Key structures:
- `struct iso_inode_info`: ISOFS private inode fields for iget block/offset, first extent, file format, compression parameters, multi-section continuation, section size, and embedded VFS inode.
- `struct isofs_sb_info`: mount-wide ISOFS state including zones, first data zone, logical zone size, Rock Ridge/Joliet/mapping/check/session flags, permission overrides, uid/gid, NLS table, and behavior flags.

Helpers:
- `ISOFS_SB()` and `ISOFS_I()` cast VFS objects to ISOFS private structures.
- `isonum_711/712/721/722/723/731/732/733()` decode ISO 711/721/733-style numeric fields. The dual-endian 723/733 helpers intentionally trust little-endian due to broken mastering programs.
- `isofs_get_ino()` derives stable 32-bit inode numbers from metadata block/offset.
- `isofs_normalize_block_and_offset()` normalizes directory identities to their `.` record.

Prototypes connect inode, directory, Rock Ridge, Joliet, lookup, block mapping, export, symlink, and file attribute operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/isofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/joliet.c -->
# File Research: sources/os/linux/linux/fs/isofs/joliet.c

Implements Joliet Unicode filename conversion.

Key functions:
- `uni16_to_x8()` converts big-endian UTF-16 code units to a configured NLS charset, substituting `?` on conversion failure.
- `get_joliet_filename()` converts the ISO directory record name either to UTF-8 when no NLS table is loaded or through `uni16_to_x8()` otherwise. It strips trailing `;1` and trailing periods to match Windows behavior.

This file is only built with `CONFIG_JOLIET` and is used by directory iteration and lookup when Joliet is active.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/joliet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/namei.c -->
# File Research: sources/os/linux/linux/fs/isofs/namei.c

Implements ISOFS lookup.

Key functions:
- `isofs_cmp()` compares a candidate on-disk name to the dentry name, using dentry operations when casefold/Joliet comparison rules are active.
- `isofs_find_entry()` scans directory records similarly to readdir, handles zero-length sector padding, split records, record validation, Rock Ridge/Joliet/Acorn/normal name conversion, hidden/associated filtering, and returns normalized block/offset for the matching entry.
- `isofs_lookup()` allocates one temporary page, calls `isofs_find_entry()`, gets the inode with `isofs_iget()` if found, frees the page, and returns `d_splice_alias()`.

Lookup and readdir intentionally share name translation behavior so dcache identity matches visible directory entries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/rock.c -->
# File Research: sources/os/linux/linux/fs/isofs/rock.c

Parses Rock Ridge / SUSP extensions for ISOFS names, POSIX inode metadata, symlinks, relocated directories, timestamps, device numbers, and zisofs compression metadata.

Core scanning support:
- `struct rock_state` tracks current SUSP buffer, continuation area, loop count, and inode.
- `setup_rock_ridge()` positions the scanner at the system-use area, applying discovered `s_rock_offset`.
- `check_sp()` validates the SUSP SP magic and records the skip offset.
- `rock_continue()` validates and reads CE continuation records, limiting to `RR_MAX_CE_ENTRIES` and checking volume/block bounds.
- `rock_check_overflow()` validates minimum record sizes before parsing a signature.

Filename extraction:
- `get_rock_ridge_filename()` scans for NM records, handles continuation, ignores `.`/`..` special NM flags, truncates overlong names, returns `-1` for relocated-directory RE entries, and returns zero if no NM field is found.

Inode parsing:
- `parse_rock_ridge_inode_internal()` handles:
  - ER: marks Rock Ridge as active and logs extension id.
  - PX: POSIX mode, links, uid, gid.
  - PN: special device numbers.
  - TF: create/modify/access/attribute timestamps.
  - SL: computes symlink size.
  - CL: relocated directory target, rejecting recursion/self-reference.
  - RE: rejects direct read of relocated directory placeholders.
  - ZF: marks zisofs-compressed files and records header/block parameters and real size.
- `parse_rock_ridge_inode()` retries with XA offset handling if the initial SP offset was not found and Rock Ridge probing is still tentative.

Symlinks:
- `get_symlink_chunk()` translates SL components into path text, handling normal, `.`, `..`, and root components plus continuation slashes.
- `rock_ridge_symlink_read_folio()` rereads the inode directory record, scans SL records and continuations, writes the target into the folio, and completes the folio read.

Exports `isofs_symlink_aops` with `.read_folio`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/rock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/rock.h -->
# File Research: sources/os/linux/linux/fs/isofs/rock.h

Defines packed on-disk SUSP/Rock Ridge structures used by `rock.c`.

Structures include:
- SUSP records: `SU_SP_s`, `SU_CE_s`, `SU_ER_s`
- Rock Ridge records: `RR_RR_s`, `RR_PX_s`, `RR_PN_s`, `RR_SL_s`, `RR_NM_s`, `RR_CL_s`, `RR_PL_s`, `RR_TF_s`
- Linux zisofs extension: `RR_ZF_s`
- `struct rock_ridge`, a common signature/length/version header plus union of record payloads.

Defines timestamp flags `TF_*` and Rock Ridge presence flags `RR_PX`, `RR_PN`, `RR_SL`, `RR_NM`, `RR_CL`, `RR_PL`, `RR_RE`, and `RR_TF`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/rock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/util.c -->
# File Research: sources/os/linux/linux/fs/isofs/util.c

Provides ISO9660 timestamp conversion.

`iso_date()` converts short or long ISO date formats into `struct timespec64`:
- Long form parses ASCII year/month/day/hour/min/sec/hundredths and timezone.
- Short form parses numeric year since 1900, month/day/time, and optional timezone; High Sierra has no timezone.
- Negative years map to zero seconds.
- Timezone is sign-extended and accepted only within ±52 fifteen-minute units, then subtracted to convert local recorded time to GMT.

Used by inode and Rock Ridge timestamp parsing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/isofs/zisofs.h -->
# File Research: sources/os/linux/linux/fs/isofs/zisofs.h

Small header for optional zisofs decompression support.

When `CONFIG_ZISOFS` is enabled, it declares:
- `zisofs_aops`
- `zisofs_init()`
- `zisofs_cleanup()`

Included by ISOFS inode and compression code to connect compressed file address-space operations and module lifecycle.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/isofs/zisofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jbd2/Kconfig -->
# File Research: sources/os/linux/linux/fs/jbd2/Kconfig

Defines JBD2 journaling configuration.

Options:
- `JBD2`: tristate generic journaling layer for block devices with 32-bit and 64-bit block numbers; selects `CRC32`; used by ext4 and OCFS2.
- `JBD2_DEBUG`: optional runtime debugging support, controlled through `/sys/module/jbd2/parameters/jbd2_debug` levels 0-5.

The config text notes module constraints when dependent filesystems are built in.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jbd2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jbd2/Makefile -->
# File Research: sources/os/linux/linux/fs/jbd2/Makefile

Builds the JBD2 journaling object when `CONFIG_JBD2` is enabled.

`jbd2-objs` consists of:
- `transaction.o`
- `commit.o`
- `recovery.o`
- `checkpoint.o`
- `revoke.o`
- `journal.o`
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jbd2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jbd2/checkpoint.c -->
# File Research: sources/os/linux/linux/fs/jbd2/checkpoint.c

Implements JBD2 checkpointing: writing committed metadata buffers to their home locations so journal log space can be reused.

Space management:
- `__jbd2_log_wait_for_space()` waits until enough journal space exists. It may run checkpointing, clean the journal tail, wait for committing transactions, or abort if no progress is possible.
- `jbd2_cleanup_journal_tail()` gets the oldest needed transaction/block, optionally flushes the filesystem device for barriers, and updates the journal tail unless the journal is aborted.

Checkpoint execution:
- `jbd2_log_do_checkpoint()` cleans the tail, selects the oldest checkpoint transaction, walks its checkpoint buffers, waits for buffers in other running transactions, queues dirty home-location writes in batches, removes clean buffers from checkpoints, yields as needed, and finally cleans the tail.
- `__flush_batch()` writes queued checkpoint buffers with a block plug and releases references.

Checkpoint list maintenance:
- `__jbd2_journal_insert_checkpoint()` links a dirty/jbddirty journal head onto a transaction checkpoint list and grabs a journal-head reference.
- `__jbd2_journal_remove_checkpoint()` unlinks a checkpointed buffer, drops the journal-head reference, updates counters, and if the transaction is finished and empty, drops/frees it.
- `jbd2_journal_try_remove_checkpoint()` removes only if the buffer is not part of a transaction, can be locked, and is clean.
- `__buffer_unlink()` handles circular checkpoint list unlinking.

Shrinker/destruction:
- `journal_shrink_one_cp_list()` and `jbd2_journal_shrink_checkpoint_list()` opportunistically remove written-back checkpoint buffers for memory reclaim.
- `__jbd2_journal_clean_checkpoint_list()` scans checkpoint transactions with selectable behavior for busy buffers.
- `jbd2_journal_destroy_checkpoint()` removes all checkpoint buffers during journal abort/destruction.
- `__jbd2_journal_drop_transaction()` unlinks a finished transaction from the checkpoint transaction ring and asserts all lists/references are clear.

The file is heavily lock-sensitive, using `j_state_lock`, `j_list_lock`, and `j_checkpoint_mutex` to coordinate committing, checkpointing, reclaim, and journal tail updates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jbd2/checkpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jbd2/commit.c -->
# File Research: sources/os/linux/linux/fs/jbd2/commit.c

Implements the full JBD2 transaction commit path.

Support helpers:
- `journal_end_buffer_io_sync()` completes journal bio writes for temporary buffer_heads and wakes any shadowed original buffer.
- `release_buffer_page()` attempts to strip buffers from truncated, unmapped folios after forget-list processing.
- Checksum helpers set commit-block checksums, descriptor tag checksums, and data CRCs.
- `journal_submit_commit_record()` allocates and writes the commit block, adding timestamps, checksums, and PREFLUSH/FUA when barriers require it.
- `journal_wait_on_commit_record()` waits for commit block I/O and returns `-EIO` on failure.

Data=ordered inode handling:
- `jbd2_submit_inode_data()` and `jbd2_wait_inode_data()` are exported helpers for individual journaled inodes.
- `journal_submit_data_buffers()` walks committing transaction inode list, marks each inode `JI_COMMIT_RUNNING`, calls filesystem data-submit hook, and wakes waiters.
- `journal_finish_inode_data_buffers()` waits for required inode data writeback and refiles inodes to the next transaction or clears dirty ranges.

Main commit function:
- `jbd2_journal_commit_transaction()` performs the complete transaction state machine:
  - Handles prior journal flush state.
  - Blocks overlapping fast commits and marks full commit ongoing.
  - Locks the running transaction, waits for outstanding updates, and releases unused reserved buffers.
  - Cleans checkpoint lists opportunistically.
  - Clears revoked flags and switches revoke tables.
  - Moves transaction from running to committing, records log start, and wakes waiters.
  - Submits ordered data buffers and writes revoke records.
  - Logs metadata through descriptor blocks and temporary shadow buffers, writing tags with block numbers, flags, UUID elision, and checksums.
  - Waits for metadata I/O, reclassifies shadowed buffers onto forget lists, then waits for descriptor/revoke control buffers.
  - Flushes filesystem device when needed before journal commit for external journals or tail updates.
  - Writes and waits for the commit record, with async-commit support.
  - Updates log tail when enough space is freed.
  - Processes the forget list: frees frozen/committed copies, removes old checkpoints, handles freed buffers, inserts new checkpoint records for dirty metadata, refiles/unfiles buffers, and may free truncated pages.
  - Adds the committed transaction to the checkpoint transaction ring.
  - Records run statistics, updates commit sequence and average commit time, invokes commit and fast-commit cleanup callbacks.
  - Marks transaction `T_FINISHED`, drops it immediately if no checkpoint buffers remain, wakes commit waiters, and accumulates history stats.

Important transaction states:
- `T_RUNNING`
- `T_LOCKED`
- `T_SWITCH`
- `T_FLUSH`
- `T_COMMIT`
- `T_COMMIT_DFLUSH`
- `T_COMMIT_JFLUSH`
- `T_COMMIT_CALLBACK`
- `T_FINISHED`

This file is the core durability path for JBD2: it orders data, metadata journal records, revoke records, cache flushes, commit blocks, checkpoint enrollment, callback execution, and transaction retirement.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jbd2/commit.c -->