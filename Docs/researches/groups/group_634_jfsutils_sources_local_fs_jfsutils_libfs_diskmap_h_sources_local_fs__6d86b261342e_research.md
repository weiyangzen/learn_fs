# Group Research: group_634_jfsutils_sources_local_fs_jfsutils_libfs_diskmap_h_sources_local_fs__6d86b261342e

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/jfsutils` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/diskmap.h -->
# File Research: sources/local-fs/jfsutils/libfs/diskmap.h

## Purpose
Declares the userspace JFS disk allocation map helper API used to construct and validate dmap buddy trees and allocation-group sizing.

## Interface
- `ujfs_maxbuddy(unsigned char *)`: computes maximum buddy/free-run state for a bitmap word or byte sequence.
- `ujfs_adjtree(int8_t *, int32_t, int32_t)`: adjusts/rebuilds a fixed-size summary tree.
- `ujfs_complete_dmap(struct dmap *, int64_t, int8_t *)`: completes a dmap page from allocation bitmap state.
- `ujfs_idmap_page(struct dmap *, uint32_t)`: initializes/identifies a dmap page.
- `ujfs_getagl2size(int64_t, int32_t)`: computes allocation-group log2 size from aggregate size/block size context.

## Dependencies
Includes `jfs_types.h` for fixed-width types and forward-declares `struct dmap`; concrete layout comes from `jfs_dmap.h` in callers/implementations.

## Notes
This is a narrow header with no state. It forms the public boundary for `diskmap.c` and overlaps conceptually with the local buddy-tree rebuild logic in `log_map.c`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/diskmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsck_base.h -->
# File Research: sources/local-fs/jfsutils/libfs/fsck_base.h

## Purpose
Provides fsck-wide base macros for inode mode classification and shared page/bit/byte sizing constants.

## Key Definitions
- File type predicates: `ISDIR`, `ISREG`, `ISLNK`, `ISBLK`, `ISCHR`, `ISFIFO`, `ISSOCK`, masking with `IFMT`.
- Fixed page geometry: `BYTESPERPAGE` 4096, `BITSPERPAGE`, `BITSPERDWORD`, `BITSPERBYTE`, and log2 equivalents.
- Workspace allocation unit: `MEMSEGSIZE` is 64 KiB.
- `log2BYTESPERKBYTE` is 10.

## Dependencies
Assumes `IFMT`, `IFDIR`, `IFREG`, and related inode mode constants are already visible from JFS headers included by consumers.

## Notes
The constants are foundational for fsck workspace sizing in `fsckwsp.h` and buffer sizes throughout the fsck/logredo code.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsck_base.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsck_message.h -->
# File Research: sources/local-fs/jfsutils/libfs/fsck_message.h

## Purpose
Defines the message-number namespace, severity/verbosity levels, text-insertion tokens, and message-dispatch macros for JFS fsck and logredo.

## Interface
- Globals: `msg_lvl`, `dbg_output`, and `msg_defs[]`.
- Dispatch functions: `v_fsck_send_msg()` and `v_send_msg()`.
- Convenience macros: `fsck_send_msg(msg_num, ...)` and `send_msg(msg_num, ...)`, which attach `__FILE__` and `__LINE__`.
- `fsck_ref_msg(msg_num)` resolves a message ID to `msg_defs[msg_num].msg_txt`.

## Message Namespace
- Highest defined ID: `fsck_highest_msgid_defined` = 599.
- `0-399`: fsck status, validation, repair, parameter, superblock, inode, directory, block-map, bad-block, xchklog/xchkdmp, and insertion-token messages.
- `400-599`: logredo/recovery messages, including journal scan, map update, redo/no-redo page handling, and low-level read/write failures.
- Several aliases intentionally share numeric IDs for text insertions, e.g. `fsck_ACL`, `fsck_aggr_inode`, and `fsck_aggregate` map into the insertion-token range.

## Data Structures
- `struct fsck_message` contains `msg_num`, fixed text buffer `msg_txt[300]`, and `msg_level`.
- Constants define max log entry length, max message text length, max parameter length, and max parameter count.

## Notes
Uses GNU-style variadic macro syntax (`arg...`, `## arg`), so this header expects a compiler mode compatible with that extension. Undefined/reserved message slots are preserved for compatibility.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsck_message.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsckcbbl.h -->
# File Research: sources/local-fs/jfsutils/libfs/fsckcbbl.h

## Purpose
Defines the fixed communication record between the JFS Clear Bad Block List utility and fsck, stored in the first page of fsck’s in-aggregate workspace block map.

## Key Structure
`struct fsckcbbl_record` is documented as 128 bytes and includes:
- Eyecatcher and reserved bytes.
- Clear-bad-block return code and block-size metadata.
- Fixed metadata/workspace boundary fields: `fs_last_metablk`, `fs_first_wspblk`.
- Bad-block counters: total, resolved, relocated extent count, relocated block count, LVM list count.
- Diagnostic buffer pointer eyecatcher and several pointer fields used by the bad-block utility/fsck implementation.

## Dependencies
Relies on fixed-width integer types but does not include a type header directly; consumers must include suitable definitions before or through surrounding headers.

## Notes
This structure is embedded at the start of `struct fsck_blk_map_hdr` in `fsckwsp.h`. It mixes persistent-looking counters with raw process pointers, so portability depends on the specific writer/reader expectations.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsckcbbl.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/fscklog.h -->
# File Research: sources/local-fs/jfsutils/libfs/fscklog.h

## Purpose
Defines the on-aggregate fsck service log and extracted-check-log record headers.

## Key Definitions
- `flog_eyecatcher_string`: `"fscklog "`.
- `JFSCHKLOG_FIRSTMSGNUM`: first service-log message number, 10000.
- `XCHKLOG_BUFSIZE`: 8192-byte block size for extracted log files.
- `jfs_chklog_eyecatcher`: `"JFS chkdskSvcLog"`.

## Data Structures
- `struct fscklog_entry_hdr`: 16-bit entry length for in-aggregate service log entries.
- `struct fscklog_error`: records failed log write offset, bytes written, and I/O return code.
- `struct chklog_entry_hdr`: 16-bit entry length for extracted check-log files.

## Dependencies
Includes `jfs_types.h` for integer types.

## Notes
`fsckwsp.h` stores `fscklog_error` records in the workspace block-map control page, and `jfs_endian.c` provides byte-swapping for `fscklog_entry_hdr`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/fscklog.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsckmsgdef.c -->
# File Research: sources/local-fs/jfsutils/libfs/fsckmsgdef.c

## Purpose
Instantiates the global fsck/logredo message catalog declared in `fsck_message.h`.

## Main Artifact
`struct fsck_message msg_defs[fsck_highest_msgid_defined + 1]` contains entries `0` through `599`.

## Content Coverage
- Early IDs cover general fsck success/failure, root directory errors, superblock corruption, inode/link/directory problems, duplicate blocks, allocation-map inconsistencies, device and mount messages, and phase banners.
- Midrange IDs include inode allocation map and block allocation map diagnostics, heartbeat text, directory index messages, bad-block/LVM transfer messages, and xchklog/xchkdmp output errors.
- IDs `384-399` are text insertion tokens such as object prefixes (`A`, `D`, `DM`, `F`, `I`, `L0`, `L1`, `L2`, `M`).
- IDs `400-599` cover logredo status and failures: log-end detection, journal superblock validation, replay initialization, map rebuild/writeback, page redo/no-redo handling, buffer reads, and end-of-log/page validation.

## Compatibility Details
- Undefined slots are explicitly present as `*undefined*`.
- A comment states IDs `424-430` should no longer be used but remain defined so fscklog can read older logs.

## Dependencies
Includes `config.h` and `fsck_message.h`; all message numeric constants and levels come from the header.

## Notes
This file is data-only. Message text format specifiers must stay synchronized with all `fsck_send_msg()` call sites; mismatches would be runtime formatting bugs.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsckmsgdef.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsckwsp.h -->
# File Research: sources/local-fs/jfsutils/libfs/fsckwsp.h

## Purpose
Defines the in-memory and in-aggregate workspace model used by JFS fsck: traversal queues, duplicate-block records, inode accounting, block-map workspace pages, service-log state, and the large aggregate-wide fsck control record.

## Major Structures
- Traversal queues: `dtreeQelem` for directory B+ tree nodes and `treeQelem` for non-directory xtree nodes.
- Duplicate allocation tracking: `dupall_blkrec`.
- Workspace block map: `fsck_blk_map_hdr` and `fsck_blk_map_page`.
- Block-map verification workspace: `blkmap_wspace`.
- Inode allocation tracking: `fsck_iag_record`, `fsck_ag_record`, `fsck_iam_record`, `fsck_inode_record`, and extension records.
- Dynamic inode record tables: `inode_tbl_t`, `inode_ext_tbl_t`, `IAG_tbl_t`.
- Workspace extent and reconnect buffers: `wsp_ext_rec`, `recon_buf_record`.
- Main `fsck_agg_record`, which centralizes aggregate geometry, counters, flags, path buffers, traversal queues, duplicate-block lists, inode-table cursors, and all fsck I/O buffers.

## Key Constants
Defines inode type codes, inode extension record kinds, buffer uses, and concrete buffer sizes such as `VLARGE_BUFSIZE`, `FSCKLOG_BUFSIZE`, `BLKMP_IO_BUFSIZE`, `EA_IO_BUFSIZE`, `IAG_IO_BUFSIZE`, and map/node buffer sizes.

## Dependencies
Includes core JFS disk format headers (`jfs_dmap.h`, `jfs_dtree.h`, `jfs_xtree.h`, `jfs_filsys.h`, `jfs_imap.h`, `jfs_dinode.h`) plus `fsck_base.h`, `fscklog.h`, and `fsckcbbl.h`.

## Notes
This header is the central fsck state contract. It contains many raw pointers and bitfields, so it is primarily an in-process workspace definition, with only selected parts intended for stable on-disk interpretation.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/fsckwsp.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/fssubs.c -->
# File Research: sources/local-fs/jfsutils/libfs/fssubs.c

## Purpose
Provides platform-dependent filesystem/device checks used before running JFS tools: root read-only detection, mounted-device detection, and fstab/type validation.

## Main Functions
- `Is_Root_Mounted_RO()`: attempts to create `/.ismount-test-file`; returns `MSG_JFS_VOLUME_IS_MOUNTED_RO` on `EROFS`, otherwise 0.
- `Is_Device_Mounted(char *Device_Name)`: implemented either via `mntent` (`/proc/mounts`, then `MOUNTED`) or via BSD-style `getmntinfo()`.
- `Is_Device_Type_JFS(char *Device_Name)`: checks `/etc/fstab`/mount metadata for JFS type, depending on platform support.

## Linux/mntent Path
- Reads `/proc/mounts`, falling back to `MOUNTED`.
- Matches `Device_Name` against `mnt_fsname`.
- Special-cases root because mount tables may list `/dev/root`; compares `stat("/")` device with candidate device `st_rdev`.
- Distinguishes mounted JFS, mounted read-only JFS, mounted non-JFS, missing fstab entry, and mount-list access errors.

## BSD/getmntinfo Path
- Normalizes `/dev/` prefixes and raw-device naming.
- Uses `f_fstypename == "jfs"` for type checks.
- Notes read-only detection as unimplemented in this path.

## Dependencies
Uses `devices.h` and `message.h` for return codes and device helpers; build-time feature macros select mount APIs.

## Notes
The root read-only probe writes to `/`, so callers should expect side effects when permissions allow creation/unlink of the test file.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/fssubs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/inode.c -->
# File Research: sources/local-fs/jfsutils/libfs/inode.c

## Purpose
Implements low-level read/write access to JFS aggregate and fileset inodes, plus xtree logical-block-to-disk-offset lookup.

## Main Functions
- `ujfs_rwinode(FILE *fp, struct dinode *di, uint32_t inum, int32_t mode, int32_t fs_block_size, uint32_t which_table, uint32_t sb_flag)`: reads or writes an aggregate/fileset inode.
- `ujfs_rwdaddr(FILE *fp, int64_t *offset, struct dinode *di, int64_t lbno, int32_t mode, int32_t fs_block_size)`: resolves an inode logical block number through the inode xtree to a byte offset.

## Inode Access Logic
- Aggregate inode table reads are direct offsets from `AGGR_INODE_TABLE_START`, with a range check against `NUM_INODE_PER_EXTENT`.
- Fileset inode reads first read the fileset inode allocation map inode, use `ujfs_rwdaddr()` to locate the target IAG, read the IAG, then compute the inode extent address from `iag.inoext[]`.

## Xtree Traversal
`ujfs_rwdaddr()` binary-searches xtree entries, descends through internal pages with `ujfs_rw_diskblocks()`, swaps pages on big-endian builds, and returns the computed byte offset for leaf hits.

## Dependencies
Uses JFS inode/imap/filsys definitions, `devices.h`, endian helpers, `utilsubs.h`, and message/error constants.

## Notes
The bottom of `ujfs_rwdaddr()` contains unreachable legacy code after an unconditional “not found” return; the active implementation is the xtree traversal above it.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/inode.h -->
# File Research: sources/local-fs/jfsutils/libfs/inode.h

## Purpose
Declares the inode read/write and disk-address lookup helpers implemented in `inode.c`.

## Interface
- `ujfs_rwinode(FILE *, struct dinode *, uint32_t, int32_t, int32_t, uint32_t, uint32_t)`
- `ujfs_rwdaddr(FILE *, int64_t *, struct dinode *, int64_t, int32_t, int32_t)`

## Dependencies
Includes `jfs_types.h` and `devices.h`; consumers must also have the JFS `struct dinode` definition available through included headers.

## Notes
This is a thin API header for shared libfs users that need to address aggregate or fileset inodes by number.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/jfs_endian.c -->
# File Research: sources/local-fs/jfsutils/libfs/jfs_endian.c

## Purpose
Implements byte-swapping for JFS on-disk and fsck workspace structures on big-endian hosts. The file is compiled effectively only under `__BYTE_ORDER == __BIG_ENDIAN`.

## Swap Coverage
Provides swap routines for:
- Allocation maps: `ujfs_swap_dbmap`, `ujfs_swap_dmap`, `ujfs_swap_dmapctl`.
- Inodes and inode maps: `ujfs_swap_dinode`, `ujfs_swap_dinomap`, `ujfs_swap_iag`.
- Trees: `ujfs_swap_dtpage_t`, `ujfs_swap_xtpage_t`.
- Fsck workspace/log records: `ujfs_swap_fsck_blk_map_hdr`, `ujfs_swap_fsck_blk_map_page`, `ujfs_swap_fscklog_entry_hdr`.
- Journal structures: `ujfs_swap_logpage`, `ujfs_swap_logsuper`, `ujfs_swap_lrd`.
- Superblock: `ujfs_swap_superblock`.

## Important Logic
- `ujfs_swap_dinode()` swaps scalar inode fields and then conditionally swaps dtree or xtree roots based on `di_mode`; directory index support depends on `JFS_DIR_INDEX`.
- `ujfs_swap_dtpage_t()` walks directory entries and continuation slots, guarding against out-of-page slot indexes.
- `ujfs_swap_lrd()` switches on log record type and swaps only the relevant union fields.

## Dependencies
Includes `jfs_endian.h`, `devices.h`, and underlying JFS format headers through `jfs_endian.h`.

## Notes
The routines use little-endian conversion helpers because JFS disk structures are little-endian. On little-endian hosts these functions are compiled out and mapped to no-ops by the header.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/jfs_endian.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/jfs_endian.h -->
# File Research: sources/local-fs/jfsutils/libfs/jfs_endian.h

## Purpose
Declares or no-ops the JFS byte-swapping API depending on host endianness.

## Big-Endian Behavior
Declares all swap functions implemented in `jfs_endian.c`, including map, inode, tree, superblock, journal, and fsck workspace swaps. Also defines:
- `ujfs_swap_inoext()`: inline loop over `INOSPEREXT` dinodes.
- `swap_multiple(swap_func, ptr, num)`: helper macro to swap arrays.

## Little-Endian Behavior
All swap functions and `swap_multiple` become empty `do {} while (0)` macros.

## Dependencies
Includes JFS type, byteorder, superblock, dmap, imap, dinode, log manager, and fsck workspace headers.

## Notes
This header centralizes endianness handling for libfs. Callers can invoke swap helpers unconditionally and rely on compile-time no-ops on the common little-endian path.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/jfs_endian.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/libjufs.h -->
# File Research: sources/local-fs/jfsutils/libfs/libjufs.h

## Purpose
Defines shared libfs error return constants for JFS utility callers.

## Constants
- `LIBFS_BADMAGIC` = `-5`: unrecognized magic number.
- `LIBFS_BADVERSION` = `-6`: magic recognized but version incompatible.
- `LIBFS_CORRUPTSUPER` = `-10`: invalid fragment size, allocation group size, or IAG size in the superblock.

## Notes
This is a small status-code header with no dependencies. The negative values are intended to distinguish libfs validation failures from normal system `errno` values.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/libjufs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/log_dump.c -->
# File Research: sources/local-fs/jfsutils/libfs/log_dump.c

## Purpose
Implements `jfs_logdump()`, a diagnostic dumper that opens a JFS journal log, validates the journal superblock, walks log records backward from the discovered end, and writes a human-readable dump to `./jfslog.dmp`.

## Main Flow
- `jfs_logdump(pathname, fp, dump_all)` opens the output file, calls `findLog()`, reads and swaps the journal superblock, prints superblock fields, warns on bad magic/version/redone state, calls `findEndOfLog()`, validates log-end bounds, and iterates log records with `logRead()`.
- Record types handled: `LOG_COMMIT`, `LOG_MOUNT`, `LOG_SYNCPT`, `LOG_REDOPAGE`, `LOG_NOREDOPAGE`, `LOG_NOREDOINOEXT`, `LOG_UPDATEMAP`, and unrecognized records.
- Stops at the last sync point unless `dump_all` requests the full valid chain.

## Helper Functions
- `ldmp_readSuper()`: reads primary superblock, falls back to secondary, then swaps.
- `ldmp_logError()`: reports log read/end/wrap errors and marks `logsup.state = LOGREADERR`.
- `ldmp_xdump()`, `ldmp_x_scmp()`, `ldmp_x_scpy()`: compact hex dump support.
- `disp_redopage()`, `disp_noredopage()`, `disp_noredoinoext()`, `disp_updatemap()`: decode log record payload descriptors.
- `open_outfile()`: opens `./jfslog.dmp`.

## Dependencies
Relies on global logredo state (`Log`, `logsup`, `afterdata`, `prog`, `retcode`), JFS log format definitions, endian helpers, `devices.h`, and `debug.h`.

## Notes
The output path is hard-coded. Error paths sometimes write to `outfp` after the file may have been closed in the normal loop-exit path, so this file is primarily diagnostic legacy code rather than a hardened library interface.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/log_dump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/log_map.c -->
# File Research: sources/local-fs/jfsutils/libfs/log_map.c

## Purpose
Implements the map-reconstruction side of JFS logredo: reads block/inode allocation maps into compact workspaces, applies replay-time state, rebuilds map summaries, and writes corrected imap/bmap pages back.

## Core Functions
- `initMaps(vol)`: initializes block map and fileset inode map by reading trusted map inodes and their xtrees.
- `bMapInit()`, `iMapInit()`: allocate workspace, discover map page offsets from xtree leaves, and read control pages.
- `bMapRead()`, `bMapWrite()`, `iMapRead()`, `iMapWrite()`: page I/O wrappers for allocation maps.
- `dMapGet()`, `iagGet()`: lazily load dmap/IAG pages and allocate compact bitmap/data records.
- `updateMaps()`: writes imap first, then bmap if bmap workspace allocation succeeded.
- `writeImap()`, `updateImapPage()`: rebuild IAG free lists, AG summaries, pmap/wmap state, inode counts, and inode extent state.
- `writeBmap()`, `updDmapPage()`: rebuild dmap summary trees, dmapctl hierarchy, aggregate free counts, AG free counts, max active AG, and preferred AG.
- `rXtree()`: follows the leftmost path of an xtree to the first leaf.
- `adjTree()` and `maxBud()`: rebuild buddy summary trees from leaf bitmap state.
- `bread()`: buffer-cache page reader with LRU/hash management and modified-buffer flushing.

## Key Data/Algorithms
- Uses `maptab[256]` to count zero/free bits in imap/dmap bytes.
- Uses `budtab[256]` to compute maximum binary buddy free-run size in bitmap words.
- Converts between disk blocks, dmap numbers, block-map page numbers, and allocation groups with macros such as `BLKTODMAPN`, `DMAPTOBMAPN`, and `BLKNOTOAG`.
- Treats map xtrees as trusted at logredo time because map xtree updates are journaled and sync-written at commit.
- If bmap workspace allocation fails, logredo can continue without rebuilding the bmap and leave full fsck to rebuild it later; imap allocation failure is fatal to this path.

## Dependencies
Uses global logredo state from `logredo.c` (`vopen`, buffer pool, allocation flags), device I/O, endian helpers, JFS dmap/imap/dinode/xtree formats, and fsck message logging.

## Notes
The file is recovery-critical and stateful. It mutates persistent map pages, interleaves CPU/disk endian conversion before writes, and depends heavily on global volume/buffer state. `iMapWrite()` reports write failures using `bmap_wsp[page_number].page_offset`, which appears suspicious for an imap write path and is worth review if maintaining this code.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/log_map.c -->