# Group Research: group_633_jfsutils_sources_local_fs_jfsutils_fsck_xfsck_h_sources_local_fs_jfs_c7bbc231a6d0

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/jfsutils` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/xfsck.h -->
# File Research: sources/local-fs/jfsutils/fsck/xfsck.h

Defines common fsck-facing constants, record types, message levels, exit codes, and internal return-code namespaces for `fsck.jfs`.

Key contents:
- Includes `jfs_types.h` and `jfs_dmap.h`, so this header is tied to JFS on-disk integer/extent and block-map definitions.
- Defines non-OS/2 extended attribute list structures `FEA` and `FEALIST`, plus `FEA_NEEDEA` and `ERROR_EA_LIST_INCONSISTENT`.
- Declares `jfs_ValidateFEAList()`.
- Defines message metadata: `fsck_msgid_offset`, `fsck_highest_msgid_defined`, message protocol columns, verbosity levels, message file ids, and fsck log text record types.
- Defines dynamic-storage error object/action ids used by fsck allocation diagnostics.
- Defines `struct fsck_bmap_record`, a large workspace/control record for block-map verification and rebuild, tracking aggregate totals, dmap/control-page buffers, AG free tables, offsets, ordinals, and per-level error flags.
- Defines helper message payload structs `fsck_ino_msg_info` and `fsck_imap_msg_info`.
- Defines `process_extent` operation codes such as `FSCK_RECORD`, `FSCK_RECORD_DUPCHECK`, `FSCK_UNRECORD`, and FSIM variants.
- Defines standard fsck process exit codes: clean, corrected, reboot needed, uncorrected errors, operational error, usage error.
- Defines a large internal status-code space: positive informational codes, negative fatal I/O/metadata codes, and catastrophic `FSCK_INTERNAL_ERROR_*` values.

Interactions:
- Used by fsck modules and by `jfs_fscklog` extraction/display code for return codes, message bounds, and error names.
- `struct fsck_bmap_record` directly references JFS allocation-map structures from `jfs_dmap.h`.

Research notes:
- This is not algorithmic code; it is a central ABI-like constants header for fsck diagnostics and control flow.
- Message-id synchronization is explicitly called out as fragile: `fsck_highest_msgid_defined` must track message tables elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/xfsck.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/xfsckint.h -->
# File Research: sources/local-fs/jfsutils/fsck/xfsckint.h

Internal fsck interface header that gathers globals and cross-module function prototypes for `fsck.jfs`.

Key contents:
- Includes `xfsck.h`, message, workspace, physical filesystem, and endian headers.
- Declares device globals provided by `xchkdsk.c`: `Dev_IOPort`, block/sector sizes, and journal byte offset.
- Groups prototypes by implementation module:
  - Directory index/table verification.
  - Block allocation map verify/rebuild.
  - Connectivity, parent, directory integrity, and link-count checks.
  - Directory entry insert/delete/search/rebuild routines.
  - Aggregate and fileset inode map verification/rebuild.
  - Inode validation, EA/ACL backout/clear/validate, path display, release, and record/unrecord flows.
  - Metadata/superblock validation and replication.
  - Physical I/O accessors for inodes, iags, block-map pages, dnodes, xnodes, fscklog, and device open/close.
  - Heartbeat start/stop.
  - Workspace allocation, block ownership accounting, extent record/unrecord, queue helpers, temp buffers, fsck log lifecycle, and cleanup.
  - Xtree traversal/search/processing.
- Defines `inode_type_recognized()` macro over JFS inode mode type bits.

Interactions:
- This file is the main internal call graph surface across fsck modules.
- It exposes low-level I/O entrypoints also mirrored in `fscklog/extract.c`, which comments that duplicated routines should eventually move into `libfs`.

Research notes:
- Strongly procedural, global-state-based design.
- Provides high coupling between fsck subsystems; useful for mapping fsck module boundaries.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/xfsckint.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fscklog/Makefile -->
# File Research: sources/local-fs/jfsutils/fscklog/Makefile

Configured Automake-generated Makefile for building and installing `jfs_fscklog`.

Key contents:
- Generated from `Makefile.in` by configure, based on Automake 1.11.1.
- Builds `sbin_PROGRAMS = jfs_fscklog`.
- Program sources are `fscklog.c`, `display.c`, `extract.c`, and `jfs_fscklog.h`.
- Links against `../libfs/libfs.a`.
- Include paths cover `include`, `libfs`, and `fsck`.
- Installs binary under configured `sbindir` (`/sbin` in this configured file) and man page `jfs_fscklog.8` under man8.
- Contains concrete configured tool paths and build metadata, including version `1.1.15`, compiler `gcc`, `AM_CFLAGS = -Wall -Wstrict-prototypes -fno-strict-aliasing`, and configured `/data2/jfsutils-1.1.15` paths.
- Includes dependency files for `display`, `extract`, and `fscklog`.

Interactions:
- Depends on `libfs.a` for device, disk, superblock, endian, logging, and message helpers.
- Generated file is build artifact/configured output but part of the source snapshot.

Research notes:
- Unlike `Makefile.in`, this file has local configured values and should not be treated as portable template input.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fscklog/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fscklog/Makefile.am -->
# File Research: sources/local-fs/jfsutils/fscklog/Makefile.am

Automake source template for the fsck log utility.

Key contents:
- Adds include paths for top-level `include`, `libfs`, and `fsck`.
- Links `jfs_fscklog` with `../libfs/libfs.a`.
- Declares `jfs_fscklog` as an sbin program.
- Declares `jfs_fscklog.8` as a man page and extra distribution file.
- Sources: `fscklog.c`, `display.c`, `extract.c`, `jfs_fscklog.h`.

Research notes:
- This is the authoritative concise build specification; `Makefile` and `Makefile.in` are generated from it.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fscklog/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fscklog/Makefile.in -->
# File Research: sources/local-fs/jfsutils/fscklog/Makefile.in

Portable Automake-generated template for `fscklog/Makefile`.

Key contents:
- Generated by Automake 1.11.1 from `Makefile.am`.
- Contains configure substitutions such as `@CC@`, `@CFLAGS@`, `@VERSION@`, `@srcdir@`, and install directory placeholders.
- Builds `jfs_fscklog$(EXEEXT)` from `fscklog`, `display`, and `extract` objects.
- Links with `../libfs/libfs.a`.
- Defines install/uninstall rules for sbin program and man8 page.
- Includes conditional dependency tracking using Automake placeholders.

Interactions:
- Consumed by configure to produce `fscklog/Makefile`.
- Mirrors `Makefile.am` intent but with generated portability machinery.

Research notes:
- Should be considered generated source-control template, not hand-authored logic.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fscklog/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fscklog/display.c -->
# File Research: sources/local-fs/jfsutils/fscklog/display.c

Implements display of an already extracted JFS fsck service log.

Key contents:
- Defines `_JFS_XCHKDMP` before including headers to limit unnecessary includes.
- Uses global `local_recptr`, `file_name`, and shared `xchklog_buffer`.
- Entry point `xchkdmp()` initializes input-buffer fields, sets highest fsck message number, opens input file, dumps log records, and closes input.
- `open_infile()` selects default `fscklog.new` or `fscklog.old` if no filename was specified, opens file for reading, reads the first `XCHKLOG_BUFSIZE` buffer, and verifies the 16-byte `jfs_chklog_eyecatcher`.
- `dump_service_log()` iterates over extracted `chklog_entry_hdr` records, validates `entry_length` against remaining buffer bytes, prints message text directly, and refills the buffer until EOF.
- `xchkdmp_fscklog_fill_buffer()` reads more extracted-log bytes from the file and resets buffer offset.
- `xchkdmp_final_processing()` closes the input stream.

Interactions:
- Displays the extraction format written by `extract.c`, not raw on-device fsck log records.
- Uses message sending for format/open/read errors.

Research notes:
- `printf(msg_txt)` prints extracted log text as the format string. If extracted log contents are untrusted, this is a format-string risk.
- The display logic depends on valid record lengths to stay aligned and handles invalid lengths by stopping the current buffer.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fscklog/display.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fscklog/extract.c -->
# File Research: sources/local-fs/jfsutils/fscklog/extract.c

Implements extraction of the on-device fsck service log from a JFS aggregate into a displayable file.

Key contents:
- Uses `libfs` helpers for devices, disk maps, superblocks, endian conversion, utility math, and messages.
- Maintains global superblock buffer `aggr_superblock`, device stream `Dev_IOPort`, output stream `outfp`, raw fsck log buffer, and extracted log buffer.
- Entry point `xchklog()` initializes superblock pointer, performs initial processing, extracts records, and closes files/devices.
- `xchklog_initial_processing()` opens the target device read-only, validates a JFS superblock, computes fsck workspace and service-log offsets from `s_fsckpxd` and `s_fsckloglen`, selects new vs old half of the service-log area based on `s_fscklog`, and opens the output file.
- `extract_service_log()` reads raw fsck log buffers, walks `fscklog_entry_hdr` entries, endian-swaps headers on big-endian hosts, validates entry lengths, and records message text into the extracted output format.
- `xchklog_fscklog_fill_buffer()` reads from device offset, advances aggregate/log offsets, and stops after one half of the reserved fsck log area.
- `open_device_read()` opens a path with `fopen(..., "r")` and sets physical block/sector sizes to `PBSIZE`.
- `open_outfile()` chooses `fscklog.new` or `fscklog.old`, opens for write, writes the extracted-log eyecatcher into the output buffer, and reports output filename.
- `readwrite_device()` enforces sector alignment and delegates to `ujfs_rw_diskblocks()`.
- `record_msg()` wraps a message string in `chklog_entry_hdr`, aligns record length to 4 bytes, flushes full buffers, and tracks the last header to pad records over buffer boundaries.
- `validate_super()` checks magic/version, device size, physical/fs block sizes, flags, group commit, AG size, fsck workspace placement/length, and inline journal placement.
- `validate_superblock()` reads primary, falls back to secondary, validates, records aggregate block size, and reports which superblock is usable.

Interactions:
- Consumes on-disk structures from `jfs_superblock.h`, `jfs_filsys.h`, `jfs_types.h`, and `jfs_dmap.h`.
- Uses `libfs/devices.c` for device size and raw reads.
- Shares record state with `fscklog.c` and `display.c` through `struct fscklog_record`.

Research notes:
- Contains duplicated low-level routines also present in fsck code, explicitly noted as future libfs consolidation candidates.
- `record_msg()` uses `strcpy()` into a fixed 4096-byte stack buffer, assuming source fsck log messages are bounded.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fscklog/extract.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fscklog/fscklog.c -->
# File Research: sources/local-fs/jfsutils/fscklog/fscklog.c

Main program for `jfs_fscklog`, coordinating command-line parsing, extraction, display, and message output.

Key contents:
- Documents usage: `jfs_fscklog [-d] [-e <device>] [-f <file.name>] [-p] [-V]`.
- Global state includes `fscklog_record`, `local_recptr`, `file_name[128]`, `Vol_Label`, and booleans `extract_log`/`display_log`.
- `main()` prints version/date, initializes state, parses arguments, then calls `xchklog()` for extraction and `xchkdmp()` for display if requested.
- `parse_parms()` handles:
  - `-d` display already extracted log.
  - `-e device` extract from device and verifies path can be opened.
  - `-f file.name` sets input/output file name, with a length check.
  - `-p` selects old/prior log.
  - `-V` exits after version output.
- `fscklog_usage()` prints emergency help.
- `v_send_msg()` formats a message from `msg_defs`, appends `[file:line]` detail, and prints both.

Interactions:
- Includes `jfs_version.h`, `jfs_fscklog.h`, `xfsck.h`, and fsck message definitions.
- Delegates real work to `extract.c` and `display.c`.

Research notes:
- File-name length check accepts `arg_len > 128`, but `file_name` is 128 bytes and `strncpy(file_name, optarg, arg_len)` does not append a terminator; exact 128-byte names are risky.
- `printf(msg_string)` in `v_send_msg()` prints formatted message text as a format string.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fscklog/fscklog.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fscklog/jfs_fscklog.h -->
# File Research: sources/local-fs/jfsutils/fscklog/jfs_fscklog.h

Shared control structure and constants for fsck log extraction/display.

Key contents:
- Includes `fscklog.h`.
- Defines `struct fscklog_record`, carrying:
  - On-device fsck workspace and fsck log byte/block offsets and lengths.
  - Input/output buffer pointers, sizes, current offsets, and data lengths.
  - Input aggregate/log offsets.
  - Last output message header pointer.
  - Aggregate block size.
  - State flags for selected log, open device/file streams, buffer state, EOF, and filename selection.
  - Highest fsck message number.
- Defines default extracted log filenames `fscklog.new` and `fscklog.old`.
- Defines `NEWLOG` and `OLDLOG`.
- Defines module return codes for display/extract failures.
- Declares `xchklog()` and `xchkdmp()`.

Interactions:
- Central state passed from `fscklog.c` into extraction/display modules.
- Buffers and offsets are initialized differently by `extract.c` and `display.c`.

Research notes:
- This struct is global-state oriented and mixes device-layout state with file I/O state.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fscklog/jfs_fscklog.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/Makefile -->
# File Research: sources/local-fs/jfsutils/include/Makefile

Configured Automake-generated Makefile for the `include` distribution directory.

Key contents:
- No compile targets; `SOURCES` and `DIST_SOURCES` are empty.
- `EXTRA_DIST` lists all public/shared JFS format headers:
  `jfs_byteorder.h`, `jfs_btree.h`, `jfs_dinode.h`, `jfs_dmap.h`, `jfs_dtree.h`, `jfs_filsys.h`, `jfs_imap.h`, `jfs_logmgr.h`, `jfs_superblock.h`, `jfs_types.h`, `jfs_unicode.h`, `jfs_version.h`, `jfs_xtree.h`.
- Contains configured build variables with concrete paths/version from configure output.
- Provides dist, clean, maintainer-clean, and no-op install targets.

Research notes:
- The include directory is packaged for distribution, not installed as headers by this makefile.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/Makefile.am -->
# File Research: sources/local-fs/jfsutils/include/Makefile.am

Automake source template for distributing JFS shared headers.

Key contents:
- `EXTRA_DIST` lists JFS on-disk format and utility headers.
- No libraries, programs, or installed headers are declared.

Research notes:
- This is the authoritative file list for distribution of the include directory.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/Makefile.in -->
# File Research: sources/local-fs/jfsutils/include/Makefile.in

Automake-generated portable template for the include directory.

Key contents:
- Uses configure substitutions for tools and directories.
- Has no source build products.
- Preserves `EXTRA_DIST` header list from `Makefile.am`.
- Provides generic dist/clean/install no-op machinery.

Research notes:
- Template version of `include/Makefile`; generated but portable.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_btree.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_btree.h

Common JFS B+-tree page definitions used by directory trees and extent trees.

Key contents:
- Defines `struct btpage`, a 4096-byte generic B+-tree page with sibling links, flags, self address, and 4064-byte type-specific entry area.
- Defines flags: root, leaf, internal, rightmost, leftmost, type mask, and endian-swapped marker.

Interactions:
- Included by `jfs_dtree.h` and `jfs_xtree.h`.

Research notes:
- Compact shared on-disk page shape; higher-level headers define typed interpretations.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_byteorder.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_byteorder.h

Endian conversion helper macros for little-endian JFS on-disk fields.

Key contents:
- Includes platform byte-order headers selected by configure.
- Defines byte-swap macros for 16-, 24-, 32-, and 64-bit values.
- Defines CPU-to-little-endian and little-endian-to-CPU macros as identity on little-endian hosts and swap on big-endian hosts.
- Emits compile-time error for unsupported byte order.

Interactions:
- Used by packed extent/address macros in `jfs_types.h`, `jfs_dtree.h`, and `jfs_xtree.h`.

Research notes:
- Uses GNU statement-expression style macros, so portability assumes compatible compiler behavior.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_byteorder.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_dinode.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_dinode.h

Defines the 512-byte JFS on-disk inode format.

Key contents:
- Includes type, directory-tree, and extent-tree headers.
- Defines inode slot/size constants.
- `struct dinode` base area includes inode stamp, fileset, number, generation, inode extent descriptor, size, block count, links, uid/gid, mode, timestamps, ACL/EA descriptors, directory index counter, and ACL type.
- The trailing 384 bytes are a union:
  - Directory form: inline directory table plus `dtroot_t`.
  - File/special form: imap generator, xtree root bytes, device descriptor, rdev/fast symlink, and inline EA.
- Defines macros aliasing union fields such as `di_dtroot`, `di_parent`, `di_xtroot`, `di_fastsymlink`, and `di_inlineea`.
- Defines on-disk mode bits for file types, permissions, and JFS extended mode bits.

Interactions:
- Used by fsck, mkfs, debug, and inode processing modules to interpret disk inodes.
- Depends on `jfs_dtree.h` and `jfs_xtree.h` for embedded root layouts.

Research notes:
- Comments document historical OS/2 compatibility constraints that shaped the union layout.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_dmap.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_dmap.h

Defines JFS block allocation map constants and on-disk structures.

Key contents:
- Constants for dmap tree sizes, leaf counts, blocks per dmap, dmapctl tree sizes, max allocation groups, map levels, and buddy values.
- Macros translate disk block numbers to dmap/L0/L1/control logical blocks and aggregate map size to top control level.
- Defines `struct dmaptree`, `struct dmap`, `struct dmapctl`, and `struct dbmap`.
- `struct dmap` is a 4096-byte page covering 8192 blocks with summary tree, working map, and persistent map.
- `struct dbmap` is a 4096-byte aggregate map descriptor with total map size, free counts, AG control fields, per-AG free table, AG size, and padding.

Interactions:
- Used by fsck block-map verification/rebuild, mkfs map initialization, and `libfs/diskmap.c`.
- `xfsck.h` embeds dmap/dmapctl/dbmap pointers in fsck block-map state.

Research notes:
- Encodes key allocator geometry; mistakes here affect all JFS allocation metadata interpretation.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_dmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_dtree.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_dtree.h

Defines JFS directory B+-tree entry and page formats.

Key contents:
- Defines directory entry data union `ddata_t`.
- Defines 32-byte `dtslot` segments for names.
- Defines internal directory entries `idtentry` with child `pxd_t`.
- Defines leaf directory entries `ldtentry` with inode number, name segment, and persistent directory-table index.
- Defines inline directory table slot format and helpers to store/extract 40-bit-ish leaf page addresses.
- Defines `dtroot_t`, the inline directory root embedded in `dinode`, including DASD limits, flags, parent inode, and sorted table.
- Defines `dtpage_t`, regular directory page layout with sibling links, flags, free list, self pxd, slots, and sorted table location.
- Defines page-size slot geometry constants and `DT_GETSTBL()` helper.
- Defines directory operation flags for create, lookup, remove, and rename.

Interactions:
- Embedded by `jfs_dinode.h`; processed by fsck directory tree routines declared in `xfsckint.h`.
- Uses `jfs_btree.h` flags and endian helpers.

Research notes:
- Supports legacy OS/2 directory entry length differences and newer persistent directory indexes.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_dtree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_filsys.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_filsys.h

Defines JFS filesystem-wide constants, flags, fixed offsets, reserved inode numbers, and states.

Key contents:
- Superblock platform/feature flags: AIX, OS/2, DFS, Linux, Unicode, commit modes, inline log, bad secondary AIT, sparse files, DASD, directory index.
- Fundamental sizes: 4096-byte page, 512-byte physical block, 512-byte inode, inode extent/page/IAG sizes, min/max block size, max file size, link max, minimum JFS partition size.
- Fixed physical block and byte offsets for primary superblock, aggregate inode map/table, secondary superblock, and block map.
- Reserved aggregate inode numbers: aggregate inode map, block map, inline log, bad block inode, fileset inode.
- Reserved fileset inode numbers: root, ACL, extension, first object.
- Directory path/name limits.
- Filesystem state flags: clean, mounted, dirty, logredo failed, extendfs in progress.

Interactions:
- Used throughout JFS utilities for validating and constructing on-disk layouts.
- `extract.c` validates superblock flags and offsets using these constants.

Research notes:
- Defines both legacy physical-block constants and preferred byte-offset constants, with comments noting physical-block macros should be removed.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_filsys.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_imap.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_imap.h

Defines JFS inode allocation map structures.

Key contents:
- Constants for inode allocation groups, extents per IAG, summary maps, pages per inode extent, max IAGs, and allocation-map byte sizes.
- Macros convert inode number to IAG, IAG to logical block, and inode number/PXD to inode page block.
- Defines 4096-byte `struct iag` with AG start, IAG number, inode/extent free-list links, summary maps, free counts, working/persistent allocation maps, and inode extent PXD array.
- Defines per-AG `struct iagctl`.
- Defines 4096-byte `struct dinomap` inode-map control page with global free counts, inode extent block geometry, and per-AG control table.

Interactions:
- Used by fsck inode map verification/rebuild and by inode allocation tooling.

Research notes:
- IAG layout combines allocation bitmaps and extent address table in one page, making endian/layout correctness central.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_imap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_logmgr.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_logmgr.h

Defines JFS journal/log manager disk structures and log record descriptors.

Key contents:
- Log page size constants and log superblock block numbers.
- Defines log magic/version and max active filesystems sharing a log.
- `struct logsuper` stores magic, version, serial, size, block size, flags, state, end pointer, uuid/label, and active filesystem UUIDs.
- Defines log states: mounted, redone, wrapped, read error.
- `struct logpage` defines header/data/trailer page layout with page sequence and end-of-record markers, including split-write detection commentary.
- Defines log record type flags: commit, sync point, mount, redopage, noredopage, noredoinoext, updatemap, noredofile.
- Defines record subtype flags for inode, xtree, dtree, btroot, EA, ACL, data, new, extend, relocate, directory xtree, and allocation/free extent variants.
- `struct lrd` is the fixed log record descriptor with transaction id, backchain, type, length, aggregate, and type-specific union payloads.

Interactions:
- Used by logredo/logdump/log formatting code in `libfs`.
- Depends on `jfs_types.h` and `jfs_filsys.h`.

Research notes:
- Comments document recovery ordering and split-write handling assumptions; this is core journal replay format documentation.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_logmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_superblock.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_superblock.h

Defines the JFS aggregate superblock format.

Key contents:
- Defines `JFS_MAGIC` as `"JFS1"` and version `2`.
- Defines `LV_NAME_SIZE`.
- `struct superblock` includes magic/version, aggregate size/block geometry, AG size, flags/state, compression flag, secondary AIT/AIM PXDs, log device/serial/log extent, fsck workspace extent, update time, fsck log length/current half, legacy volume name, extendfs fields, volume UUID/label, and log UUID.

Interactions:
- Read and validated by `extract.c` and common superblock helpers.
- Uses `pxd_t` and `timestruc_t` from `jfs_types.h`; flags/states come from `jfs_filsys.h`.

Research notes:
- `s_fsckloglen` is total reserved fsck-log blocks divided among kept versions, which `extract.c` interprets as two halves.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_superblock.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_types.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_types.h

Base JFS type and packed descriptor definitions.

Key contents:
- Includes system integer types or defines fallback fixed-width unsigned integer aliases.
- Defines fallback `bool` if `<stdbool.h>` is unavailable.
- Defines `UniChar` as 16-bit on-disk Unicode character.
- Defines JFS `timestruc_t` with 32-bit seconds/nanoseconds.
- Defines utility macros `MIN`, `MAX`, `ROUNDUP`, and bit constants.
- Defines `pxd_t`, a packed physical extent descriptor with 24-bit length and split address fields, plus set/get macros.
- Defines `pxdlist`.
- Defines `dxd_t`, a 16-byte data extent descriptor for ACL/EA/inline/out-of-line descriptors, plus flags and aliases to PXD length/address helpers.
- Defines `component_name`.
- Defines DASD limit/usage structure and accessors.

Interactions:
- Must be included early by JFS C files.
- Relies on endian conversion macros being available when PXD/DXD accessors are used.

Research notes:
- Uses C bitfields for disk format fields; compiler layout assumptions are significant.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_unicode.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_unicode.h

Inline Unicode string and uppercase helpers for JFS 16-bit `UniChar` names.

Key contents:
- Declares `UniUpperTable` and `UniUpperRange` generated uppercase conversion tables.
- Defines `struct UNICASERANGE`.
- Provides inline helpers:
  - `UniStrcpy`
  - `UniStrlen`
  - `UniStrncmp`
  - `UniStrncpy`
  - `UniToupper`
  - `UniStrupr`
- `UniToupper()` uses a 512-entry base table for low characters and range tables for higher characters.

Interactions:
- Used for JFS directory/name handling, especially case handling for OS/2-style semantics.

Research notes:
- Header assumes `UniChar` and `size_t` are already visible from prior includes.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_version.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_version.h

Single version-date macro.

Key contents:
- Defines `JFSUTILS_DATE "04-Mar-2011"`.

Interactions:
- `fscklog.c` prints this date alongside package `VERSION`.

Research notes:
- No include guard; intentionally minimal generated/static version metadata.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_version.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_xtree.h -->
# File Research: sources/local-fs/jfsutils/include/jfs_xtree.h

Defines JFS extent allocation descriptor tree structures.

Key contents:
- Includes `jfs_btree.h`.
- Defines `xad_t`, a 16-byte extent descriptor with flags, split 40-bit file offset, 24-bit length, and split disk address.
- Provides XAD set/get macros for offset, address, and length.
- Defines XAD flags: new, extended, compressed, not recorded, copy-on-write.
- Defines xtree slot geometry and root/page max entry constants.
- Defines `xtpage_t`, a 4096-byte union containing xtree header or XAD array.

Interactions:
- Embedded in dinodes and used by fsck xTree processing.
- Used by log manager record payloads and allocation map updates.

Research notes:
- Supports COW flag in the on-disk extent descriptor even though jfsutils is primarily repair/utility code.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/include/jfs_xtree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/install-sh -->
# File Research: sources/local-fs/jfsutils/install-sh

Portable install helper script from Automake/X Consortium lineage.

Key contents:
- Shell script version `2009-04-28.21`.
- Supports installing files, installing into target directory, creating directories, copy-on-change, owner/group/mode changes, strip, and `-T`.
- Uses overridable command environment variables such as `CHGRPPROG`, `CHMODPROG`, `CPPROG`, `MKDIRPROG`, and `STRIPPROG`.
- Implements portable mkdir handling, including POSIX mkdir detection and slow fallback for old systems.
- Installs through temporary files and rename/unlink fallback, with traps for cleanup.
- Supports `--help` and `--version`.

Interactions:
- Referenced by generated Makefiles as `install_sh`.

Research notes:
- Third-party/generated infrastructure file, not JFS-specific logic.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/install-sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/jfsutils.spec.in -->
# File Research: sources/local-fs/jfsutils/jfsutils.spec.in

RPM spec template for jfsutils packaging.

Key contents:
- Uses `@PACKAGE@` and `@VERSION@` configure substitutions.
- Metadata: group `System/Kernel`, summary “IBM JFS utility programs”, GPL copyright, JFS/Linux team packager, SourceForge URL.
- Description lists included utilities: `jfs_fsck`, `jfs_fscklog`, `jfs_logdump`, `jfs_mkfs`, `jfs_tune`, and `jfs_debugfs`.
- Build runs `./configure --mandir=/usr/share/man/en/` with RPM CFLAGS, then `make`.
- Install runs `make install DESTDIR=${RPM_BUILD_ROOT}`.
- Files include `/sbin/*`, localized man8 pages, and docs.

Research notes:
- Legacy RPM template; uses old spec tags such as `Copyright` and `Buildroot`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/jfsutils.spec.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/Makefile -->
# File Research: sources/local-fs/jfsutils/libfs/Makefile

Configured Automake-generated Makefile for static internal library `libfs.a`.

Key contents:
- Builds `noinst_LIBRARIES = libfs.a`.
- Compiles many utility modules: filesystem subs, Unicode conversion, devices, util subs, superblock, inode, disk map, messages, endian, open-by-label, log dump/format/redo/work/read/map, and fsck message definitions.
- Include path is top-level `include`.
- Uses configured compiler/tools and concrete `/data2/jfsutils-1.1.15` paths.
- Creates archive with `ar cru` and `ranlib`.
- Dependency includes for all listed object files.

Interactions:
- `fscklog` links against this library.
- Other jfsutils programs likely share the same no-install archive.

Research notes:
- Configured generated file; `Makefile.am` is the concise source of library membership.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/Makefile.am -->
# File Research: sources/local-fs/jfsutils/libfs/Makefile.am

Automake source template for the shared static support library.

Key contents:
- Include path: top-level `include`.
- Declares non-installed static library `libfs.a`.
- Lists source modules for device I/O, disk maps, superblocks, inodes, messages, Unicode, endian conversion, open-by-label, journal dump/format/redo/read/map/work, and fsck message definitions.
- Lists internal headers distributed/compiled with the library.

Interactions:
- Produces `../libfs/libfs.a`, linked by `jfs_fscklog` and other utilities.

Research notes:
- Defines libfs as an internal utility archive, not an installed API.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/Makefile.in -->
# File Research: sources/local-fs/jfsutils/libfs/Makefile.in

Portable Automake-generated template for building `libfs.a`.

Key contents:
- Generated from `Makefile.am`.
- Uses configure substitutions for compiler, flags, archiver, ranlib, and directories.
- Builds `libfs.a` from the object set corresponding to `libfs_a_SOURCES`.
- Contains dependency tracking placeholders and generic dist/clean/tag targets.

Interactions:
- Configure turns this into `libfs/Makefile`.

Research notes:
- Generated template; source module membership comes from `Makefile.am`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/debug.h -->
# File Research: sources/local-fs/jfsutils/libfs/debug.h

Simple conditional debug macro header.

Key contents:
- Includes `stdio.h`.
- Defines:
  - `DBG_TRACE(a)` enabled by `TRACE`, printing to stdout and flushing stdout.
  - `DBG_IO(a)` enabled by `TRACE_IO`, printing via `printf` and flushing stderr.
  - `DBG_ERROR(a)` enabled by `TRACE_ERROR`, printing to stdout and flushing stdout.
- When flags are absent, macros expand to empty statements.

Interactions:
- Used by `devices.c` and likely other libfs modules for optional diagnostics.

Research notes:
- `DBG_IO` flushes stderr after `printf` to stdout, which is inconsistent but harmless for compile-time disabled default.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/devices.c -->
# File Research: sources/local-fs/jfsutils/libfs/devices.c

Device validation, size discovery, raw block I/O, and flushing helpers.

Key contents:
- Forces `_LARGEFILE_SOURCE` before `config.h` to avoid an autoconf/glibc `fseeko` issue.
- Includes platform headers for Linux/BSD/DragonFly disk size handling.
- Defines fallback Linux `BLKGETSIZE64` and `BLKGETSIZE` ioctl constants when needed.
- `ujfs_device_is_valid()` accepts block devices or regular files on Linux-like systems, character devices or regular files on DragonFly.
- `ujfs_get_dev_size()`:
  - For regular files, uses file size rounded down to 1024-byte multiple.
  - Uses `BLKGETSIZE64` or `BLKGETSIZE` on Linux when available.
  - Uses DragonFly slices/disklabel or BSD disklabel paths when available.
  - Falls back to exponential seek/read then binary search to find the last readable byte, restoring original file position.
- `ujfs_rw_diskblocks()` seeks to byte offset and reads/writes exact byte counts using `fread`/`fwrite`, returning Windows-like error codes from `devices.h`.
- `ujfs_flush_dev()` calls `fsync()` and optionally `BLKFLSBUF` except for ramdisks.

Interactions:
- Used by fscklog extraction, superblock helpers, mkfs, fsck, and log utilities for raw disk access.
- Error constants and operation modes come from `devices.h`.

Research notes:
- In `ujfs_get_dev_size()`, the exponential loop condition compares `Read_Result == 1`, but `fgetc()` returns a byte value or EOF; only byte value 1 continues, which appears suspect. The fallback may under-detect sizes depending on data byte read.
- `ujfs_rw_diskblocks()` checks `Bytes_Transferred == -1`, but `size_t` cannot equal `-1` in the intended way.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/devices.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/devices.h -->
# File Research: sources/local-fs/jfsutils/libfs/devices.h

Public prototypes and constants for libfs device I/O.

Key contents:
- Includes `<stdint.h>`.
- Defines operation modes `GET`, `PUT`, and `VRFY`.
- Defines open-mode constants `READONLY` and `RDWR_EXCL`.
- Defines Windows-style error code constants used across jfsutils.
- Forward-declares `struct stat`.
- Declares `ujfs_get_dev_size()`, `ujfs_rw_diskblocks()`, `ujfs_flush_dev()`, and `ujfs_device_is_valid()`.

Interactions:
- Included by `devices.c`, `extract.c`, and other disk-access modules.

Research notes:
- `VRFY` is declared but `ujfs_rw_diskblocks()` only implements GET/PUT in this file.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/devices.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/diskmap.c -->
# File Research: sources/local-fs/jfsutils/libfs/diskmap.c

Implements block allocation map helper routines for buddy summaries and dmap initialization.

Key contents:
- Static `budtab[256]` maps byte bit patterns to maximum free-string values for buddy allocation summaries.
- `ujfs_maxbuddy()` computes maximum free string in a 32-bit map word, fast-pathing all-free and half-free cases before table lookup.
- `ujfs_adjtree()` computes a dmap/dmapctl summary tree by combining leaf buddy values and bubbling maxima up through parent levels.
- `ujfs_complete_dmap()` fills dmap page metadata and summary tree from initialized working/persistent maps, returning top tree max.
- `ujfs_idmap_page()` initializes a dmap page as free for existing blocks and allocated for non-existent blocks in a partial final page.
- `ujfs_getagl2size()` computes log2 allocation group size from aggregate size and maximum AG count.

Interactions:
- Uses constants and structs from `jfs_dmap.h`.
- Used by mkfs/fsck map initialization and validation flows.

Research notes:
- Core allocator geometry helper code; no disk I/O here.
- Uses unaligned casts to `uint32_t *`/`uint16_t *` in `ujfs_maxbuddy()`, which may matter on strict-alignment architectures.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/diskmap.c -->