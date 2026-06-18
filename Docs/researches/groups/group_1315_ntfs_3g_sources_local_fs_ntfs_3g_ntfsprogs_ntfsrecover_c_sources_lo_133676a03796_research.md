# Group Research: group_1315_ntfs_3g_sources_local_fs_ntfs_3g_ntfsprogs_ntfsrecover_c_sources_lo_133676a03796

Scope confirmed against `Docs/research_subset_a.md`: `sources/local-fs/ntfs-3g` is included in subset A. All three listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.c

## Purpose

`ntfsrecover.c` is the main program for `ntfsrecover`, an NTFS-3G utility that inspects an NTFS `$LogFile`, displays its contents, and can replay committed metadata transactions to recover filesystem consistency after Windows left the volume dirty.

The file supports two operating modes:

- Full volume mode: opens an NTFS volume through libntfs-3g, locates `$LogFile`, and can apply redo/undo recovery actions.
- Standalone log-file mode: opens a copied `$LogFile` directly and only analyzes/displays it, because replay requires full volume metadata access.

## Main State And Data Model

The file is built around global recovery/log-walk state:

- Restart metadata: `log_header`, `restart`, `client`.
- Volume geometry: `clustersz`, `clusterbits`, `blocksz`, `blockbits`, `bytespersect`, `mftlcn`, `mftrecsz`, `mftrecbits`, `mftcnt`.
- `$LogFile` access: `log_ni`, `log_na`, `logfilelcn`, `logfilesz`.
- LSN checkpoints: `committed_lsn`, `synced_lsn`, `latest_lsn`, `restart_lsn`, `offset_mask`.
- Option flags: `optb`, `optc`, `optd`, `optf`, `optk`, `optn`, `optr`, `opts`, `optt`, `optu`, `optv`, `optV`, plus replay counts.
- Work tables: `buffer_table` caches log pages; `redirect` maps NTFS 2.x temporary restart/log pages to target blocks; `attrtable` caches logical attribute IDs seen in log records.

`CONTEXT` carries the active input source and queued recovery actions:

- `vol`: mounted `ntfs_volume *` when operating on a full device.
- `file`: `FILE *` when operating on a standalone log copy.
- `firstaction` / `lastaction`: doubly linked queue of `ACTION_RECORD` entries used for redo/undo replay.

## Important Functions

### Block And Buffer Access

- `loclogblk()` maps logical log-block numbers to byte offsets, either through the `$LogFile` attribute runlist or direct file offsets.
- `replaceusa()` verifies and applies NTFS update-sequence-array fixups for protected log record pages.
- `read_buffer()` implements the central log-page cache. It allocates page buffers, handles fixed special blocks, redirects NTFS 2.x temporary pages through `redirect`, reads from `ntfs_attr_pread()` or `fread()`, computes page header size, and rejects pages with failed USA fixups.
- `read_restart()` loads and validates the restart page. In full volume mode it delegates restart-page selection to `ntfs_check_logfile()`. In standalone mode it reads block 0 directly.
- `reset_logfile()` writes clean restart pages back after successful recovery, resets the client state, forces `$LogFile` version 1.1, and writes both restart pages with MST fixups.

### Restart, Geometry, And Volume Setup

- `getboot()` parses the NTFS boot sector for sector size, cluster size, cluster count, MFT location, and MFT record size.
- `locatelogfile()` opens `$LogFile` as an unnamed `$DATA` attribute.
- `getlogfiledata()` initializes enough geometry for standalone `$LogFile` analysis. It validates restart page sizes and estimates cluster size from sequence-number bits.
- `getvolumedata()` selects full-volume versus standalone-log setup.
- `open_volume()` first checks whether the input is directly a `$LogFile` copy, then otherwise mounts it as an NTFS volume. Mutating modes mount with `NTFS_MNT_FORENSIC`; read-only display modes use `NTFS_MNT_RDONLY`.
- `dorest()` interprets restart pages, chooses sync/commit/latest LSNs, copies selected restart/client structures into globals, determines dirty state, and computes `offset_mask`.

### Log Record Discovery

- `likelyop()` validates whether a candidate `LOG_RECORD` looks structurally plausible: supported record type, action IDs in range, aligned offsets/lengths, sane client data length, transaction ID expectations, and consistent redo/undo layout.
- `searchlikely()` scans a page for an aligned plausible record when the expected offset is suspect.
- `firstrecord()` computes the first record offset in the current page based on a previous page and possible overlap.
- `findprevious()` walks backward to locate the page that defines the beginning of the current page’s first record, accounting for circular log wraparound and NTFS 2.x LSN-derived addressing.
- `overlapshow()` reconstructs records spanning multiple forward pages before displaying them.
- `backoverlap()` reconstructs records spanning pages during backward traversal.

### Display And Decoding

- `hexdump()` emits hex/ascii dumps.
- `showdate()` converts NTFS timestamps to readable UTC dates, with a fallback for timestamps outside traditional Unix limits.
- `showname()` prints UTF-16LE names as UTF-8-ish output.
- `actionname()` maps log operation numbers to names from `enum ACTIONS`.
- `mftattrname()` maps NTFS attribute type codes to human-readable names.
- `attrname()`, `getattrentry()`, `copy_attribute()`, `refresh_attributes()`, and `showattribute()` maintain and display the log’s transient attribute table.
- `fixup()` decodes operation-specific redo/undo payloads for many NTFS log actions, including MFT record initialization/deallocation, attribute creation, resident/nonresident updates, index entries, file-name updates, bitmap bit changes, and attribute table/name dumps.
- `detaillogr()` prints full `LOG_RECORD` details, LCN lists, redo/undo/extra layout, hex dumps, and operation-specific decoded payloads.
- `showlogr()` prints either verbose record details or compact transaction summaries.
- `showheadrcrd()` and `showrest()` display record-page and restart-page headers.

### Forward And Backward Walking

- `forward_rcrd()` processes records in a page from the computed starting offset, calling `showlogr()` or `overlapshow()` as needed.
- `dorcrd()` wraps verbose page display before calling `forward_rcrd()`.
- `best_start()` chooses the most recent candidate latest page by comparing `last_end_lsn`.
- `find_latest_block()` scans forward from a base page to locate the latest valid record page when records were written directly to target pages.
- `block_sequence()` handles NTFS `$LogFile` version 2.x sequencing: it compares paired temporary blocks, computes target blocks from LSN offsets, fills `redirect`, updates `latest_lsn`, and returns the latest block.
- `backward_rcrd()` processes records in reverse order inside one page, including overlap reconstruction and action enqueueing for replay.
- `walkback()` walks backward through the circular log until the earliest page, requested replay count, or an error is reached.
- `walk()` orchestrates the complete operation: read restart, optionally walk/display forward pages, determine the latest block, then walk backward for transaction display, undo/play, or sync.

### Recovery Queue And Replay Control

- `mark_transactions()` walks queued actions backward and marks committed transaction records with `ACTION_TO_REDO`, using `ForgetTransaction` as the marker for transactions that should be replayed.
- `enqueue_action()` copies log records into the action queue. On checkpoints or sync boundaries it refreshes attribute state, optionally plays undos, marks transactions, plays redos, and frees the processed queue.
- `within_lcn_range()` filters standard log records to a requested cluster range.
- `exception()` checks the undocumented `-x` action exception list.
- Actual mutation logic is delegated to external functions declared in `ntfsrecover.h`: `play_undos()`, `play_redos()`, `show_redos()`, and `freeclusterentry()`.

## CLI Behavior

`getoptions()` supports:

- Display/walk modes: `-b/--backward`, `-f/--forward`, `-r/--range`, `-t/--transactions`, `-v/--verbose`.
- Recovery modes: default sync, `-s/--sync`, `-n/--no-action`, `-p/--play`, `-u/--undo`.
- Filters/controls: `-c/--clusters`, `-i`, `-k/--kill-fast-restart`, `-x/--exceptions`.
- Informational modes: `-h/--help`, `-V/--version`.

Default behavior, when no display/replay mode is selected, is `opts = 1`, meaning sync committed changes.

The option validator enforces incompatible combinations, notably:

- `-b` cannot combine with forward/range/sync.
- `-f` cannot combine with play/sync/undo.
- `-p` cannot combine with range/sync/transactions/undo.
- `-s` cannot combine with transactions/undo.

## Control Flow

`main()` performs:

1. Validate key struct sizes with `checkstructs()`.
2. Parse options.
3. Initialize counters, tables, log handler, and buffers.
4. Open input as standalone log or NTFS volume.
5. Reject mutating modes for standalone log copies.
6. Run `walk()`.
7. If mutating recovery succeeded and not `-n`, call `reset_logfile()`.
8. Close NTFS attributes/inodes/volume or file.
9. Free buffers and attribute table.
10. In volume mode, release cluster recovery state and print redo summary.

## Notable Invariants And Assumptions

- The program expects exact layout sizes for `RECORD_PAGE_HEADER`, `LOG_RECORD`, `RESTART_PAGE_HEADER`, `RESTART_AREA`, `ATTR_OLD`, `ATTR_NEW`, and `LastAction`.
- Log records must be 8-byte aligned and have sizes between `MINRECSIZE` and `MAXRECSIZE`.
- USA fixups are required for normal record pages; restart blocks are treated specially.
- NTFS `$LogFile` version 1.1 is supported directly. Version 2.0 fast restart is treated as dangerous unless `--kill-fast-restart` is provided.
- Standalone `$LogFile` copies cannot be replayed because the tool needs the full volume for MFT, attributes, cluster allocation, and writes.
- Many payload decoders are heuristic and version-aware, especially attribute table dumps and Windows 10 action variants.

## External Dependencies

This file depends heavily on NTFS-3G internal headers and APIs:

- Layout and endian helpers: `layout.h`, `endians.h`, `logfile.h`, `ntfsrecover.h`.
- Volume/inode/attribute access: `volume.h`, `inode.h`, `attrib.h`, `mft.h`.
- Device and metadata helpers: `device_io.h`, `device.h`, `bitmap.h`, `index.h`, `runlist.h`, `mst.h`.
- Logging and utility support: `logging.h`, `utils.h`, `misc.h`.

## Research Notes

This is not a simple display tool; it is a log interpreter plus recovery driver. The central architectural split is:

- `ntfsrecover.c`: log walking, validation, action queueing, display, restart handling, and CLI.
- External replay implementation: functions declared in `ntfsrecover.h` perform actual undo/redo application and cluster bookkeeping.

The highest-risk areas for maintenance are the global mutable state, heuristic record-boundary recovery, multi-page record reconstruction, NTFS 2.x temporary page redirection, and version-specific operation decoding.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.h

## Purpose

`ntfsrecover.h` is the shared declaration header for NTFS log recovery processing. It exposes low-level endian access macros, log action IDs, shared data structures, globals owned by `ntfsrecover.c`, and replay/display helper prototypes used by companion recovery implementation files.

## Key Definitions

### Little-Endian Access Macros

The header defines two groups of pointer-offset helpers:

- `getle16`, `getle32`, `getle64`: read unaligned-looking data at byte offsets and immediately convert from little endian to CPU endian.
- `feedle16`, `feedle32`, `feedle64`: return typed little-endian objects at byte offsets without conversion.

These macros are used throughout `ntfsrecover.c` when decoding packed NTFS log payloads.

### `enum ACTIONS`

The `ACTIONS` enum assigns numeric IDs to NTFS log redo/undo operation codes:

- Core actions: `Noop`, `CompensationlogRecord`, `InitializeFileRecordSegment`, `DeallocateFileRecordSegment`, `WriteEndofFileRecordSegment`.
- Attribute operations: `CreateAttribute`, `DeleteAttribute`, `UpdateResidentValue`, `UpdateNonResidentValue`, `UpdateMappingPairs`, `SetNewAttributeSizes`.
- Index operations: root/allocation add/delete/update actions.
- Bitmap and hotfix operations.
- Transaction lifecycle: `EndTopLevelAction`, `PrepareTransaction`, `CommitTransaction`, `ForgetTransaction`.
- Dump/open records: `OpenNonResidentAttribute`, `OpenAttributeTableDump`, `AttributeNamesDump`, `DirtyPageTableDump`, `TransactionTableDump`.
- Additional record-data and Windows 10 action placeholders: `UpdateRecordDataRoot`, `UpdateRecordDataAllocation`, `Win10Action35`, `Win10Action36`, `Win10Action37`.
- `LastAction` is expected to be `38` and is checked by `checkstructs()` in `ntfsrecover.c`.

### Shared Structures

- `struct BUFFER`: cached log/restart page buffer with logical number, physical/read number, allocation size, computed header size, safety flag, and variable-length union storage for restart page, record page, or raw bytes.
- `struct ACTION_RECORD`: doubly linked replay queue node containing action number, flags, and variable-length `LOG_RECORD`.
- `ACTION_TO_REDO`: flag marking queued actions selected for redo replay.
- `struct ATTR`: cached log attribute table entry containing owning inode, LSN, NTFS attribute type, log attribute key, name length, and UTF-16LE name.

## Shared Globals

The header exposes geometry, option, replay, and `$LogFile` globals defined in `ntfsrecover.c`, including:

- Geometry: `clustersz`, `clusterbits`, `blocksz`, `blockbits`, `bytespersect`, `mftlcn`, `mftrecsz`, `mftrecbits`, `mftcnt`.
- Options/state: `optc`, `optn`, `opts`, `optv`, `redocount`, `undocount`.
- `$LogFile` handles and layout: `log_ni`, `log_na`, `logfilelcn`, `logfilesz`.
- LSNs: `redos_met`, `committed_lsn`, `synced_lsn`, `latest_lsn`, `restart_lsn`.
- Restart structures: `restart`, `client`.

This confirms that recovery implementation is intentionally coupled through shared global process state.

## Function Interface

Functions implemented in `ntfsrecover.c` and exported here include:

- Name/display helpers: `actionname()`, `mftattrname()`, `showname()`, `hexdump()`.
- Data interpretation helpers: `fixnamelen()`, `within_lcn_range()`, `getattrentry()`, `copy_attribute()`.
- Log-record offset helpers: `get_undo_offset()`, `get_redo_offset()`, `get_extra_offset()`.
- Replay exception lookup: `exception()`.

Functions implemented elsewhere and consumed by `ntfsrecover.c` include:

- `play_undos()`: apply undo actions.
- `play_redos()`: apply redo actions.
- `show_redos()`: print redo summary.
- `freeclusterentry()`: release cluster bookkeeping state.

`struct STORE` is forward-declared for `freeclusterentry()`.

## Research Notes

This header is tightly scoped to the `ntfsrecover` program and is not a stable general API. Its most important role is coordinating the log parser in `ntfsrecover.c` with the recovery applier implemented elsewhere. The variable-length structures and global externs mirror the low-level, single-process design of the utility.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsresize.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsresize.8.in

## Purpose

`ntfsresize.8.in` is the manual page template for `ntfsresize`, the NTFS-3G utility for resizing NTFS filesystems without data loss. It is written in roff manpage format and uses `@VERSION@` substitution in the title line.

## Document Structure

The manpage contains:

- `NAME`: identifies `ntfsresize` as resizing an NTFS filesystem without data loss.
- `SYNOPSIS`: documents info mode and resize mode.
- `DESCRIPTION`: explains supported NTFS versions, shrink/enlarge behavior, size suffixes, and relationship between filesystem resizing and partition resizing.
- `Shrinkage`, `Enlargement`, `Partitioning`: workflow guidance for safe partition-table coordination.
- `OPTIONS`: command-line reference.
- `EXIT CODES`: success is `0`, errors are nonzero.
- `KNOWN ISSUES`: limitations, chkdsk behavior, and historical Linux geometry/partitioning issue.
- `AUTHORS`, `ACKNOWLEDGEMENT`, `AVAILABILITY`, `SEE ALSO`.

## Functional Semantics Documented

The manpage makes several important behavioral guarantees and constraints:

- `ntfsresize` resizes the filesystem only; it does not edit partition tables.
- Shrinking requires first shrinking the filesystem, then shrinking the partition.
- Enlarging normally requires first enlarging the partition, then enlarging the filesystem.
- Downward expansion with `--expand` keeps the partition end fixed and shifts the filesystem beginning downward, recreating metadata in expanded space without relocating user data.
- Defragmentation is not required before resizing.
- Backup is strongly recommended, with `ntfsclone(8)` mentioned for NTFS backups.
- The tool marks the filesystem for Windows consistency checking after real resize operations.

## Options Covered

Documented options include:

- `-c`, `--check`: only check whether the device is ready to resize.
- `-i`, `--info`: compute smallest supported shrink size, or with `--expand`, compute downwards expansion sizing.
- `-m`, `--info-mb-only`: print shrinkable size in MB only.
- `-s`, `--size SIZE[k|M|G]`: resize to fit a partition of the requested size; decimal SI suffixes are standard, binary `ki`, `Mi`, `Gi` are also allowed.
- `-x`, `--expand`: expand downwards to current partition size.
- `-f`, `--force`: continue despite prompts or consistency-check marks; double force avoids additional prompting.
- `-n`, `--no-action`: read-only dry run.
- `-b`, `--bad-sectors`: support disks with hardware bad sectors, with strong backup/chkdsk warnings.
- `-P`, `--no-progress-bar`: disable progress bars.
- `-v`, `--verbose`: more output.
- `-V`, `--version`: print version.
- `-h`, `--help`: display help.

## Safety And User Guidance

The manpage emphasizes operational safety:

- Users must resize both filesystem and partition, in the correct order.
- Recreated partitions must preserve starting sector and partition type.
- Bootable flags should be preserved.
- Do not shrink a partition smaller than the NTFS filesystem.
- `--no-action` should be used before real resizing.
- Hardware bad-sector handling is a workaround, not a repair.
- Windows `chkdsk` on first boot after resizing is expected.

## Known Limitations

The documented limitations include:

- Filesystems with unknown bad sectors.
- Relocation of the first MFT extent.
- Resizing into the middle of an `$MFTMirr` extent.
- Potential boot issues after downwards expansion of Windows system partitions.
- Historical partition-table corruption associated with Linux 2.6 `HDIO_GETGEO` behavior and partitioning tools, explicitly described as independent of `ntfsresize` because `ntfsresize` does not touch partition tables.

## Research Notes

This file is documentation only, but it captures important contract-level behavior for `ntfsresize`: filesystem-only resizing, strong dry-run/backup expectations, deliberate Windows consistency-check scheduling, and exact sequencing rules for shrink/enlarge workflows. It should be kept aligned with option parsing and behavior in the corresponding `ntfsresize` implementation.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsresize.8.in -->