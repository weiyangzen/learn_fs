# Group Research: group_1007_linux_stable_sources_os_linux_linux_stable_fs_iomap_direct_io_c_sou_033d3888d116

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/direct-io.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/direct-io.c

Implements iomap direct I/O submission and completion for reads and writes. The central state is `struct iomap_dio`, which tracks the kiocb, filesystem DIO ops, byte counts, i_size snapshot, async/sync completion state, private flags, and first error.

Key paths:
- `__iomap_dio_rw()` prepares the DIO, handles NOWAIT, read/write setup, page-cache invalidation for writes, sync/FUA policy, `inode_dio_begin()`, and iterates mappings with `iomap_iter()`.
- `iomap_dio_iter()` dispatches by iomap type: holes and unwritten reads zero the iterator, mapped/unwritten writes submit bios, inline data copies directly, DELALLOC collisions warn and fail.
- `iomap_dio_bio_iter()` validates alignment, handles new/unwritten/shared extents, atomic bio requirements, write-through/FUA decisions, zeroes sub-block head/tail regions, and submits one or more bios.
- `iomap_dio_bio_end_io()` and `iomap_finish_ioend_direct()` feed bio/ioend completion back into the shared DIO refcount.
- `iomap_dio_complete()` calls filesystem `end_io`, reports fs errors, adjusts short reads to i_size, performs post-write invalidation, ends inode DIO, updates `ki_pos`, and runs write sync if required.

Important invariants:
- Private DIO flags live above public `iomap.h` flag bits.
- Completion can occur inline, on `s_dio_done_wq`, or synchronously by waking the submitter.
- Async errors are forced to workqueue context because filesystem error completion may sleep.
- Polling is only allowed for single-bio non-sync DIO and is cleared once multiple bios or completion work are needed.
- `-ENOTBLK` is a magic fallback-to-buffered-write result and is not reported as an fsnotify I/O error.
- Atomic writes require one full-length bio for the mapped range.

Dependencies:
- Uses `iomap_iter()` from `iter.c`, ioend completion from `ioend.c`, tracepoints from `trace.h`, fscrypt, block integrity, bio bouncing, page-cache invalidation helpers, and filesystem callbacks in `struct iomap_dio_ops`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/direct-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/fiemap.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/fiemap.c

Provides generic iomap-backed FIEMAP and legacy bmap support.

Key paths:
- `iomap_to_fiemap()` converts `IOMAP_*` mapping types and flags into `FIEMAP_EXTENT_*` flags, skipping holes.
- `iomap_fiemap_iter()` delays emitting the previous extent until the next non-hole mapping, allowing final extent marking at the end.
- `iomap_fiemap()` prepares the request with `fiemap_prep()`, iterates mappings with `IOMAP_REPORT`, emits the last extent with `FIEMAP_EXTENT_LAST`, and treats `-ENOENT` as no mapping.
- `iomap_bmap()` implements old `->bmap`, flushes dirty page cache first, maps one block through iomap, and returns 0 on errors per legacy API.

Important details:
- DELALLOC is reported as both delayed allocation and unknown.
- UNWRITTEN, INLINE, MERGED, and SHARED iomap state maps directly to FIEMAP flags.
- `iomap_bmap()` intentionally aborts after the first mapping by leaving `iter.status` unset.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/fiemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/iomap/internal.h

Private iomap header for shared implementation helpers.

Contents:
- Defines `IOEND_BATCH_SIZE` as 4096 for completion batching.
- Provides `iomap_max_bio_size()`, which caps bio size to integrity allocation limits when `IOMAP_F_INTEGRITY` is set and otherwise allows `BIO_MAX_SIZE`.
- Declares buffered read and direct ioend completion helpers.
- Declares `iomap_bio_read_folio_range_sync()` when block support is enabled; otherwise provides an `-EIO` warning stub.

This header is used by direct I/O, buffered I/O, and ioend code to keep bio sizing and completion interfaces consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/ioend.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/ioend.c

Manages iomap ioend allocation, writeback submission, completion, merging, sorting, and splitting.

Key paths:
- `iomap_init_ioend()` initializes the embedded-bio ioend state.
- `iomap_add_to_ioend()` appends dirty folio ranges to the current writeback ioend or submits/allocates a new one. It tags unwritten, shared, dropbehind, and boundary ioends and clamps append writeback size to in-core EOF for crash consistency.
- `iomap_ioend_writeback_submit()` submits buffered writeback bios and generates integrity metadata when needed.
- `iomap_finish_ioend()` dispatches final completion to direct I/O, buffered read, or buffered write completion once child/split refs drain.
- `iomap_finish_ioends()` drains merged ioends in task context and yields after large batches.
- `iomap_ioend_try_merge()` merges adjacent write ioends with compatible flags, status, logical offsets, and physical sectors.
- `iomap_split_ioend()` splits large ioends, including zone-append hardware-limit handling, while preserving parent completion accounting.

Error handling:
- Buffered write errors are bounced to `failed_ioend_work` to avoid nested lock acquisition in fs error reporting.
- Completion reports buffered write fs errors per folio and sets mapping errors.
- Direct ioends complete through `iomap_finish_ioend_direct()` in `direct-io.c`.

Important invariants:
- Reads are not merged because there is no useful batched completion processing.
- Anonymous writes must not go through the ordinary submit path.
- Splits must remain filesystem-block aligned.
- `iomap_ioend_bioset` is initialized at fs initcall time with embedded `struct iomap_ioend`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/ioend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/iter.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/iter.c

Implements the generic iomap range iterator.

Key paths:
- `iomap_iter_advance()` advances `iter->pos` and reduces `iter->len`, warning if the caller advances beyond the current mapping.
- `iomap_iter()` alternates between ending the previous mapping with optional `ops->iomap_end()` and beginning the next mapping with `ops->iomap_begin()`.
- `iomap_iter_reset_iomap()` releases any folio batch attached via `IOMAP_F_FOLIO_BATCH` and clears `iomap` and `srcmap`.
- `iomap_iter_done()` validates mapping bounds, rejects stale mappings, records `iter_start_pos`, and emits tracepoints for destination and source mappings.

Loop contract:
- Callers continue while `iomap_iter()` returns positive.
- To stop from inside the loop, callers leave `iter.status` unchanged or set it negative.
- Positive `iter.status` is treated as old semantics and converted to `-EIO`.
- If a mapping is marked stale, the iterator can retry without forward progress.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/iter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/seek.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/seek.c

Provides generic `SEEK_HOLE` and `SEEK_DATA` operations using iomap mappings plus page-cache inspection for unwritten extents.

Key paths:
- `iomap_seek_hole()` validates `pos`, iterates to EOF with `IOMAP_REPORT`, and returns either the first hole/unwritten cached hole or EOF.
- `iomap_seek_data()` validates `pos`, iterates to EOF, and returns the first mapped data or page-cache data inside unwritten extents.
- `iomap_seek_hole_iter()` treats holes as holes, mapped extents as data, and uses `mapping_seek_hole_data(..., SEEK_HOLE)` inside unwritten mappings.
- `iomap_seek_data_iter()` skips holes, reports mapped/inline/delalloc-style mappings as data, and uses `mapping_seek_hole_data(..., SEEK_DATA)` for unwritten mappings.

Important behavior:
- Positions before 0 or at/after i_size return `-ENXIO`.
- Unwritten extents can contain cached dirty data, so page-cache checks refine the on-disk mapping answer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/seek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/swapfile.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/swapfile.c

Implements generic swapfile activation for iomap filesystems.

Key paths:
- `iomap_swapfile_activate()` fsyncs the file, iterates the whole page-aligned file with `IOMAP_REPORT`, accumulates usable extents, and fills `swap_info_struct`.
- `iomap_swapfile_iter()` accepts only mapped or unwritten extents, rejects inline, holes, dirty metadata, shared extents, and extents outside the swap device.
- `iomap_swapfile_add_extent()` trims physical ranges to page boundaries, accounts for the header page, tracks lowest/highest physical pages, and calls `add_swap_extent()`.
- `iomap_swapfile_fail()` reports path-qualified activation failures.

Important invariants:
- Swap extents must be physically contiguous, page-aligned, committed, non-shared, and on the main swap block device.
- Logical file offsets do not matter to swap once physical page extents are reported.
- A swapfile with no usable page-aligned range is rejected.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/swapfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/trace.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/trace.c

Tracepoint instantiation unit for iomap.

It includes `<linux/iomap.h>`, defines `CREATE_TRACE_POINTS`, and includes `trace.h` last so helper definitions and trace event implementations are generated exactly once.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/trace.h -->
# File Research: sources/os/linux/linux-stable/fs/iomap/trace.h

Defines iomap tracepoints. The file explicitly notes these tracepoints are not a stable kernel ABI.

Trace coverage:
- Readpage/readahead events with dev, inode, and page count.
- Generic range events for writeback, folio release/invalidate, DIO invalidate failure, queued DIO, and zeroing.
- Iomap mapping events for destination/source maps with type, flags, bdev, addr, offset, and length.
- `iomap_add_to_ioend` for writeback aggregation decisions.
- `iomap_iter` for iterator position, length, status, flags, ops, and caller.
- `iomap_dio_rw_begin` and `iomap_dio_complete` for direct I/O request and completion state.

String tables:
- Iomap types, iterator flags, iomap mapping flags, and public DIO flags are mapped to readable trace output.
- The trace include path/file footer causes generated trace definitions to come from `trace.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/isofs/Kconfig

Defines ISO 9660 filesystem configuration.

Options:
- `ISO9660_FS`: tristate CD-ROM filesystem support, selects `BUFFER_HEAD`, builds as `isofs`.
- `JOLIET`: optional Microsoft Joliet Unicode filename extension, depends on ISOFS and selects `NLS`.
- `ZISOFS`: optional transparent compressed-file extension, depends on ISOFS and selects `ZLIB_INFLATE`.

The help text describes Rock Ridge support as part of the base ISOFS driver and Joliet/zisofs as optional extensions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/isofs/Makefile

Builds the ISOFS module/object.

Composition:
- `obj-$(CONFIG_ISO9660_FS) += isofs.o`
- Base object list: `namei.o inode.o dir.o util.o rock.o export.o`
- Optional Joliet support adds `joliet.o`
- Optional zisofs compression support adds `compress.o`
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/compress.c -->
# File Research: sources/os/linux/linux-stable/fs/isofs/compress.c

Implements transparent zisofs decompression for compressed files on ISO 9660.

Key paths:
- `zisofs_read_folio()` determines the compression block covering the requested page, opportunistically grabs adjacent pages for readahead, and calls `zisofs_fill_pages()`.
- `zisofs_fill_pages()` reads the compressed block pointer table, validates block boundaries, and invokes decompression for each compression block.
- `zisofs_uncompress_block()` reads compressed disk blocks, serializes zlib use with `zisofs_zlib_lock`, inflates into target pages or a sink page, marks completed pages uptodate, and reports critical-page errors.
- `zisofs_init()` allocates a global zlib workspace with `vmalloc()`, and `zisofs_cleanup()` frees it.

Important details:
- Empty compressed blocks zero-fill target pages.
- Compressed block size is bounded by `deflateBound()`.
- The global workspace avoids allocation failures during decompression but requires a mutex because zlib workspace use is not concurrent.
- `zisofs_aops` only supplies `.read_folio`; bmap is intentionally unsupported.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/isofs/dir.c

Implements ISOFS directory iteration and filename translation.

Key paths:
- `isofs_name_translate()` lowercases ISO names, strips trailing `.;1` or `;1`, and converts remaining `;` and `/` to `.`.
- `get_acorn_filename()` applies Acorn-specific filename decoration and filetype suffix handling.
- `do_isofs_readdir()` scans directory records, handles zero-length sector padding, copies entries spanning buffer boundaries, validates record/name lengths, skips multi-extent continuation records, emits `.` and `..`, filters hidden/associated files, and chooses Rock Ridge, Joliet, Acorn, normal, or raw names.
- `isofs_readdir()` allocates a temporary page for translated names and split directory entries.
- Exports `isofs_dir_operations` and `isofs_dir_inode_operations`.

Important details:
- Inode numbers are derived from normalized block/offset for the first entry of a multi-extent sequence.
- Rock Ridge `RE` entries can return `-1` to suppress relocated directory placeholders.
- Directory records that span block buffers are assembled into temporary storage before parsing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/export.c -->
# File Research: sources/os/linux/linux-stable/fs/isofs/export.c

Provides NFS export operations for ISOFS, which cannot use default inode-number based helpers because ISOFS uses `iget5_locked()` with block/offset identity.

Key paths:
- `isofs_export_encode_fh()` encodes inode block, offset, generation, and optionally parent block/offset/generation into file handles.
- `isofs_fh_to_dentry()` and `isofs_fh_to_parent()` decode handles and call `isofs_export_iget()`.
- `isofs_export_iget()` validates block range, loads the inode with `isofs_iget()`, checks generation, and returns an alias dentry.
- `isofs_export_get_parent()` reads the child directory's `..` entry, normalizes its block/offset, and obtains the parent inode alias.

Important invariants:
- Directory inode identities are normalized to the `.` entry, so parent lookup can find `..` in the same directory block.
- NFSv2 handle length limitations pack child and parent offsets into 16-bit fields.
- Generation mismatches return `-ESTALE`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/isofs/inode.c

Main ISOFS implementation: mount option parsing, superblock setup, inode cache, block mapping, inode loading, and module registration.

Key areas:
- Inode cache: `init_inodecache()`, `isofs_alloc_inode()`, `isofs_free_inode()`, and `destroy_inodecache()`.
- Mount parsing: `isofs_parse_param()` handles Rock Ridge/Joliet toggles, hide/showassoc, cruft, charset, name mapping, sessions, superblock sector, uid/gid, modes, block size, and compression disablement.
- Superblock setup: `isofs_fill_super()` chooses session start, scans ISO/High Sierra/Joliet descriptors, enforces read-only mount, sets block sizes and time bounds, loads NLS for Joliet, selects Rock Ridge vs Joliet root policy, installs dentry ops, and creates the root dentry.
- Name hashing/comparison: ISO and Joliet modes can be case-sensitive or case-insensitive, with Microsoft-style trailing-dot trimming for Joliet.
- Block mapping: `isofs_get_blocks()` maps file logical blocks through first extent and Level 3 multi-extent sections, with a 100-section sanity limit.
- Read operations: normal files use mpage read/readahead and bmap; compressed files switch to `zisofs_aops`.
- Inode loading: `isofs_read_inode()` reads directory records, handles split records, sets default modes, timestamps, extent info, Level 3 size, Rock Ridge overrides, compression format, and final inode/file/address-space ops.
- Identity: `__isofs_iget()` uses block/offset with `iget5_locked()` rather than inode number lookup.
- Registration: `init_iso9660_fs()` initializes inode cache and zisofs, then registers `iso9660`; exit unregisters and cleans up.

Important behaviors:
- Rock Ridge is preferred over Joliet when both are valid unless disabled, but broken empty/corrupt primary roots can force Joliet fallback.
- High Sierra disables Rock Ridge.
- The filesystem is read-only; attempts to mount read-write fail.
- `s_maxbytes` is set to 8 TB for multi-extent files.
- `cruft` truncates bogus high file-size byte for broken media.
- `overriderockperm` lets mount fmode/dmode override Rock Ridge permissions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/isofs.h -->
# File Research: sources/os/linux/linux-stable/fs/isofs/isofs.h

Private ISOFS header defining core in-memory structures, helpers, and cross-file declarations.

Key definitions:
- `enum isofs_file_format`: normal, sparse, compressed.
- `struct iso_inode_info`: iget block/offset identity, first extent, format parameters, Level 3 next-section links, section size, embedded VFS inode.
- `struct isofs_sb_info`: volume counts, zone size, Rock Ridge/Joliet/name mapping state, mount flags, modes, uid/gid, NLS table.
- Numeric helpers `isonum_711` through `isonum_733` parse ISO little/big/both-endian fields, intentionally trusting little-endian for broken mastering tools in 723/733.
- `isofs_get_ino()` derives a convenient inode number from block and offset.
- `isofs_normalize_block_and_offset()` normalizes directory identities to their `.` entry for dcache and NFS export consistency.

Also declares Rock Ridge, Joliet, lookup, bread/get_blocks, iget, directory ops, symlink aops, and export ops.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/isofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/joliet.c -->
# File Research: sources/os/linux/linux-stable/fs/isofs/joliet.c

Implements Joliet Unicode filename conversion.

Key paths:
- `uni16_to_x8()` converts big-endian UTF-16 characters through a loaded NLS table, substituting `?` on conversion failure.
- `get_joliet_filename()` converts the directory-record name to UTF-8 when no NLS table is loaded, otherwise uses `uni16_to_x8()`. It strips trailing `;1` and trailing periods.

Important behavior:
- Joliet names are stored as big-endian 16-bit characters.
- Output is written into a page-sized temporary buffer supplied by callers in directory iteration and lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/joliet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/isofs/namei.c

Implements ISOFS lookup.

Key paths:
- `isofs_cmp()` compares a candidate name against the dentry, using dentry-specific compare ops when present.
- `isofs_find_entry()` scans a directory for the requested name, handling sector padding, split directory records, name translation through Rock Ridge/Joliet/Acorn/normal mappings, hidden and associated-file filtering, and directory block/offset normalization.
- `isofs_lookup()` allocates one page for translated names and split records, calls `isofs_find_entry()`, loads the inode with `isofs_iget()` if found, and returns `d_splice_alias()`.

Important details:
- Lookup returns no match for special one-byte ISO `.`/`..` names via `dlen > 1 || dpnt[0] > 1`.
- Corrupt directory records with name lengths beyond the record length are rejected.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/rock.c -->
# File Research: sources/os/linux/linux-stable/fs/isofs/rock.c

Implements Rock Ridge / SUSP parsing for names, inode attributes, relocation, symlinks, and zisofs metadata.

Key infrastructure:
- `struct rock_state` tracks the current System Use area, continuation area, allocated continuation buffer, loop count, and inode.
- `setup_rock_ridge()` positions parsing after the ISO directory record name and optional Rock Ridge skip offset.
- `check_sp()` validates the SP magic and stores the SUSP skip offset.
- `rock_continue()` follows CE continuation records with bounds checks, volume bounds checks, and a `RR_MAX_CE_ENTRIES` loop cap.
- `rock_check_overflow()` validates minimum record sizes before field access.

Key consumers:
- `get_rock_ridge_filename()` extracts NM alternate names, supports continued names, truncates over `NAME_MAX`, ignores `.`/`..`, and returns `-1` for relocated-directory RE entries.
- `parse_rock_ridge_inode()` calls the internal parser, retrying after XA attributes when the SP offset is still unknown.
- `parse_rock_ridge_inode_internal()` handles PX permissions/ownership/links, PN device numbers, TF timestamps, SL symlink size accounting, CL relocated directories, RE relocation placeholders, ER extension recognition, and ZF compressed-file metadata.
- `rock_ridge_symlink_read_folio()` rereads the directory record and assembles symlink content from SL records and continuations into the folio.

Important safeguards:
- Malformed RR lengths often cause Rock Ridge data to be ignored rather than making files invisible, but verified overflows return `-EIO`.
- Recursive/self directory relocation is rejected.
- Symlink assembly checks page bounds and fails if the link would overflow the page.
- ZF compression is ignored when `nocompress` is set or when block shift is unsupported.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/rock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/rock.h -->
# File Research: sources/os/linux/linux-stable/fs/isofs/rock.h

Defines SUSP and Rock Ridge on-disk record structures.

Structures:
- SUSP: SP, CE, ER.
- Rock Ridge: RR, PX, PN, SL and `SL_component`, NM, CL, PL, TF.
- Linux zisofs extension: ZF with algorithm, parameters, and real size.
- `struct rock_ridge` wraps signature, length, version, and a union of record payloads.

Flags:
- TF timestamp flags for create, modify, access, attributes, backup, expiration, effective, and long form.
- RR presence bits for PX, PN, SL, NM, CL, PL, RE, and TF.

The structures use packed/flexible-array layout where needed to match on-disk variable-length fields.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/rock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/util.c -->
# File Research: sources/os/linux/linux-stable/fs/isofs/util.c

Provides ISO timestamp conversion.

`iso_date()` supports:
- Short 7-byte ISO/High Sierra timestamps.
- Long-form Rock Ridge timestamps.
- Timezone conversion from 15-minute units to UTC.
- High Sierra mode with no timezone byte.
- Sanity bound of +/- 13 hours for timezone offsets.
- Nanosecond conversion from long-form hundredths of a second.

Invalid negative years return zero seconds.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/zisofs.h -->
# File Research: sources/os/linux/linux-stable/fs/isofs/zisofs.h

Header for optional compressed ISOFS support.

Under `CONFIG_ZISOFS`, it declares:
- `zisofs_aops`
- `zisofs_init()`
- `zisofs_cleanup()`

This keeps compressed-file address-space operations and zlib workspace lifecycle separate from the base ISOFS code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/isofs/zisofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/jbd2/Kconfig

Defines JBD2 journaling configuration.

Options:
- `JBD2`: tristate generic journaling layer, selects `CRC32`, used by ext4 and OCFS2 and buildable as module `jbd2` unless required built-in by users.
- `JBD2_DEBUG`: optional runtime debugging support controlled via `/sys/module/jbd2/parameters/jbd2_debug` levels 0-5.

The help text positions JBD2 as a generic journal for block devices with 32-bit and 64-bit block number support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/jbd2/Makefile

Builds the JBD2 journaling object.

Composition:
- `obj-$(CONFIG_JBD2) += jbd2.o`
- `jbd2-objs := transaction.o commit.o recovery.o checkpoint.o revoke.o journal.o`

This group covers `commit.o` and `checkpoint.o`; other objects provide transaction, recovery, revoke, and journal infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/checkpoint.c -->
# File Research: sources/os/linux/linux-stable/fs/jbd2/checkpoint.c

Implements JBD2 checkpointing: writing committed metadata from filesystem locations so journal log space can be reused.

Key paths:
- `__jbd2_log_wait_for_space()` waits until enough journal space exists, checkpointing old transactions, cleaning the tail, or waiting for committing transactions as needed. It aborts on impossible progress.
- `jbd2_log_do_checkpoint()` writes dirty checkpoint buffers from the oldest checkpoint transaction in batches, waits on busy buffers, starts/waits for newer transactions if a buffer is still attached, and cleans the journal tail afterward.
- `jbd2_cleanup_journal_tail()` finds the oldest remaining transaction, optionally flushes the filesystem device, and updates the journal tail.
- `jbd2_journal_shrink_checkpoint_list()` and `__jbd2_journal_clean_checkpoint_list()` free written-back checkpoint buffers under memory pressure or cleanup.
- `jbd2_journal_destroy_checkpoint()` removes all checkpoint state after abort/destroy.
- `__jbd2_journal_remove_checkpoint()` unlinks a buffer from a transaction checkpoint list and drops the transaction if it is finished and empty.
- `jbd2_journal_try_remove_checkpoint()` removes only clean, unlocked, non-transaction buffers.
- `__jbd2_journal_insert_checkpoint()` adds committed dirty buffers to a transaction checkpoint list.
- `__jbd2_journal_drop_transaction()` unlinks a finished transaction from checkpoint tracking and asserts it has no live lists.

Important locking:
- `j_state_lock` protects journal state and space decisions.
- `j_checkpoint_mutex` serializes checkpoint work and is temporarily dropped before waiting for commits that may need it.
- `j_list_lock` protects checkpoint transaction and journal_head lists.
- Buffer locks are used to determine whether checkpointed buffers are clean and stable.

Important invariants:
- Journal tail must not advance past metadata that failed checkpoint writeback.
- Checkpointing can proceed in abort state, but tail updates do not.
- Transactions are only dropped after `T_FINISHED` and empty checkpoint lists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/checkpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/commit.c -->
# File Research: sources/os/linux/linux-stable/fs/jbd2/commit.c

Implements the full JBD2 transaction commit state machine.

Major phases in `jbd2_journal_commit_transaction()`:
- Blocks fast commits and locks the running transaction.
- Waits for outstanding updates, releases unused reserved buffers, cleans checkpoint lists, clears revoke flags, and switches revoke tables.
- Moves the transaction through `T_LOCKED`, `T_SWITCH`, `T_FLUSH`, `T_COMMIT`, `T_COMMIT_DFLUSH`, `T_COMMIT_JFLUSH`, `T_COMMIT_CALLBACK`, and finally `T_FINISHED`.
- Submits ordered data buffers before metadata when required.
- Writes revoke records, descriptor blocks, metadata shadow buffers, checksums, and commit records.
- Waits for metadata and control-buffer I/O, aborting the journal on failures.
- Flushes filesystem or journal devices when barrier and external journal rules require it.
- Updates the journal tail when enough checkpointed space can be freed.
- Processes the forget list, frees frozen/committed copies, handles freed buffers, re-checkpoints dirty buffers, and releases or refiles journal heads.
- Adds the committed transaction to the checkpoint list, runs callbacks, updates commit sequence/timing/statistics, wakes waiters, and drops the transaction if no checkpointing remains.

Supporting functions:
- `journal_end_buffer_io_sync()` handles journal buffer I/O completion and wakes shadowed metadata buffers.
- `release_buffer_page()` tries to strip buffers from truncated detached pages.
- `journal_submit_commit_record()` writes the commit block, including timestamps, checksum fields, and barrier/FUA flags.
- `journal_wait_on_commit_record()` waits for the commit block and detects I/O failure.
- `jbd2_submit_inode_data()` and `jbd2_wait_inode_data()` expose inode data submission/wait helpers.
- `journal_submit_data_buffers()` and `journal_finish_inode_data_buffers()` walk the transaction inode list with `JI_COMMIT_RUNNING` protection.
- `jbd2_checksum_data()`, `write_tag_block()`, and `jbd2_block_tag_csum_set()` implement metadata/tag checksum support.

Important invariants:
- Metadata buffers are written through temporary shadow buffers so original buffers can be protected while journal I/O is in flight.
- Descriptor tags record target block numbers, escape flags, UUID elision, and checksums.
- Async commit writes the commit record before waiting for all earlier log I/O, then flushes appropriately.
- Forget-list processing must tolerate concurrent additions from unmap paths, so it loops with `j_list_lock`.
- `j_list_lock` and `j_state_lock` together protect the transition to `T_FINISHED` against checkpoint races.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/commit.c -->