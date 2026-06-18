# Group Research: group_631_jfsutils_sources_local_fs_jfsutils_fsck_fsckmeta_c_sources_local_fs__44be84fa0d94

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/local-fs/jfsutils`, which is included in subset A. All four listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckmeta.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckmeta.c

## Role

`fsckmeta.c` is the JFS fsck metadata validation and repair coordinator. It validates superblocks, chooses usable primary/secondary aggregate inode table data, records fixed and inode-described metadata ownership into fsck workspace maps, checks duplicate metadata block references, and repairs limited metadata structures such as the root directory inode/tree.

It depends heavily on global fsck state:

- `sb_ptr`: current superblock buffer.
- `agg_recptr`: aggregate-wide fsck state, buffers, flags, selected AIT parts, block-map state, and inode records.
- `Vol_Label`: message/device label.

## Major Responsibilities

- Superblock validation and replication:
  - `validate_repair_superblock()` reads primary superblock first, then secondary if needed.
  - `validate_super()` checks magic/version, block sizes, device size compatibility, flags, allocation group sizing, fsck workspace placement, journal placement, and secondary AIT/AIM descriptors.
  - `validate_super_2ndaryAI()` validates secondary aggregate inode map/table descriptors and cross-checks them with the alleged secondary AIT self inode and the other superblock.
  - `replicate_superblock()` writes the in-memory superblock to both primary and secondary copies, forcing dirty state if clean replication cannot be trusted.
  - `agg_clean_or_dirty()` reconciles fsck’s computed dirty state with `s_state`, updating superblocks when writable.

- Aggregate inode table selection:
  - `validate_select_agg_inode_table()` validates primary AIT part 1 and part 2, falls back to secondary, and can combine part 1 from one AIT with part 2 from the other.
  - Part 1 covers aggregate metadata inodes 0 through 15.
  - Part 2 covers aggregate fileset inodes 16 through 31, with release 1 using `FILESYSTEM_I`.
  - Selection results are stored in `agg_recptr->primary_ait_4part1` and `agg_recptr->primary_ait_4part2`.

- Metadata inode validation:
  - `verify_ait_part1()` validates aggregate self inode, block map inode, journal inode, and bad block inode.
  - `verify_ait_part2()` validates the aggregate fileset inode.
  - `verify_ait_inode()`, `verify_bmap_inode()`, `verify_log_inode()`, `verify_badblk_inode()`, and `verify_agg_fileset_inode()` perform structural inode checks, then call `verify_metadata_data()`.
  - `verify_metadata_data()` initializes the inode record, validates the inode’s B+ tree/data with `validate_data()`, compares recorded block counts and byte sizes, and backs out recorded blocks if size validation proves the tree unusable.

- Fileset metadata validation and repair:
  - `validate_fs_metadata()` verifies the fileset super extension inode when possible, then verifies/repairs the root directory inode.
  - `verify_fs_super_ext()` validates the reserved fileset extension inode but intentionally ignores its content because release 1 does not use it.
  - `verify_repair_fs_rootdir()` verifies root inode identity, mode, parent reference, EA/ACL fields, directory tree, block counts, and size. In read/write mode it can recreate or normalize root directory metadata.
  - `rootdir_tree_bad()` reinitializes the root directory to an empty valid directory tree and marks `rootdir_rebuilt`.

- Workspace ownership accounting:
  - `record_fixed_metadata()` records reserved aggregate space, primary/secondary superblocks, and phantom blocks described by the final dmap page.
  - `record_other_ait()` records the AIT/AIM copy not selected for active processing.
  - `record_ait_part1_again()` re-records verified part 1 aggregate metadata inodes after earlier backout during mixed primary/secondary selection.
  - `backout_ait_part1()` and `backout_valid_agg_inode()` remove previously recorded ownership for metadata inodes when an AIT path fails.

- Duplicate and first-reference checks:
  - `fatal_dup_check()` emits ranges for duplicate metadata block references and returns `FSCK_DUPMDBLKREF`.
  - `first_ref_check_agg_metadata()`, `first_ref_check_fs_metadata()`, `first_ref_check_fixed_metadata()`, and `first_ref_check_other_ait()` resolve duplicate-allocation first references against aggregate metadata, fileset metadata, fixed metadata, and the non-selected AIT/AIM.

## Important Control Flow

The early fsck metadata path is roughly:

1. `validate_repair_superblock()` obtains a valid superblock.
2. `validate_select_agg_inode_table()` chooses primary, secondary, or mixed AIT parts.
3. Verified metadata inodes are recorded in the workspace block map.
4. `record_fixed_metadata()` and `record_other_ait()` reserve non-inode-described metadata.
5. `validate_fs_metadata()` validates fileset super extension and root directory.
6. Duplicate and first-reference checks operate over the recorded metadata ownership.
7. `agg_clean_or_dirty()` marks final clean/dirty state.

## Data and State Mutations

This file can mutate:

- Superblock state (`sb_ptr->s_state`) and replicated on-disk superblocks.
- `agg_recptr` selection flags, dirty/modified flags, inode stamp, duplicate state, correction flags, and root rebuild flags.
- Per-inode fsck records from `get_inorecptr()`.
- On-disk root directory inode and super extension inode through `inode_put()`.
- Workspace block ownership maps through record/unrecord helpers.

## Error Handling Pattern

The file follows a conservative validation pattern:

- Validate identity fields before parsing deeper structures.
- Stop deep B+ tree validation when basic inode identity is wrong.
- Record block ownership only for validated metadata.
- Back out ownership if a later check fails.
- Treat duplicate metadata block allocation as fatal or dirty.
- In read-only mode, report and mark dirty instead of repairing.

## Notable Observations

- `verify_ait_inode()` checks `di_fileset != AGGREGATE_I` twice with different message suffixes. This looks like duplicated validation logic, possibly a historical copy/paste.
- `verify_badblk_inode()` maps invalid bad-block inode final status to `FSCK_BMINOBAD`, while `verify_ait_part1()` later maps bad-block failures to `FSCK_BBINOBAD` in some paths. This may be intentional reuse, but it is worth checking if diagnostics need to distinguish bad block inode failures.
- `validate_fs_metadata()` intentionally tolerates failures in the fileset super extension inode and proceeds to root directory validation with `goto read_root`; comments say the extension is not important enough to block root validation.
- Root directory repair is aggressive in read/write mode: if identity or tree shape is bad, the code may reinitialize it as an empty root directory, preserving fsck progress at the cost of requiring later reconnection/lost+found handling elsewhere.

## External Dependencies

Key helpers are declared or included via `xfsckint.h`, `devices.h`, `diskmap.h`, `message.h`, `super.h`, and `utilsubs.h`. This file calls many cross-module routines, including:

- Device/superblock helpers: `ujfs_get_superblk()`, `ujfs_put_superblk()`, `ujfs_get_dev_size()`.
- Inode/buffer helpers from `fsckpfs.c`: `ait_special_read_ext1()`, `inode_get()`, `inode_put()`.
- Metadata scanners: `validate_data()`, `validate_dir_data()`, `process_valid_data()`, `process_valid_dir_data()`.
- Workspace map helpers: `blkall_increment_owners()`, `blkall_ref_check()`, `record_valid_inode()`, `unrecord_valid_inode()`, `first_ref_check_inode()`.
- EA/ACL helpers: `validate_EA()`, `validate_ACL()`, `clear_EA_field()`, `clear_ACL_field()`.
- Messaging: `fsck_send_msg()` and `fsck_ref_msg()`.

<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckmeta.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckpfs.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckpfs.c

## Role

`fsckpfs.c` is the physical/persistence support layer for `fsck.jfs`. It centralizes low-level reading, writing, caching, flushing, endian swapping, and traversal for JFS fsck metadata structures.

The file bridges logical fsck operations to on-device data:

- Aggregate inode table nodes.
- Fsck workspace block map pages.
- JFS block allocation map pages.
- Directory dnodes.
- Extended attributes.
- Fsck in-aggregate log.
- Inode allocation groups and inode extents.
- Inode table control pages.
- XTree nodes.
- Device open/close and aligned read/write.
- Directory reconstruction buffers.

## Global State

The file uses:

- `sb_ptr` for filesystem block size and superblock metadata.
- `agg_recptr` for all fsck buffers, buffer offsets, dirty flags, selected AIT parts, map traversal state, and workspace dimensions.
- `Vol_Label` for diagnostics.
- `Dev_IOPort`, `Dev_blksize`, `Dev_SectorSize`, and `ondev_jlog_byte_offset` from device/global fsck state.

## Major Subsystems

### AIT and XTree Access

- `ait_node_get()` reads an AIT xTree node by aggregate block offset, rejects targets beyond the fsck workspace boundary, and swaps `xtpage_t` after read.
- `ait_node_put()` writes an AIT node after swapping to disk format and then swaps back.
- `ait_special_read_ext1()` reads the first extent of the primary or secondary Aggregate Inode Table into the inode buffer. It is used early before normal inode lookup infrastructure is fully available.

### Fsck Workspace Block Map

- `blkmap_find_bit()` maps an aggregate block number to fsck workspace bitmap page, byte offset, and bit mask.
- `blkmap_get_ctl_page()` reads the workspace block map control page.
- `blkmap_put_ctl_page()` writes the control page immediately because it carries serviceability state for interrupted fsck sessions.
- `blkmap_get_page()` pages workspace bitmap data into a shared buffer, flushing dirty data first.
- `blkmap_put_page()` marks the current workspace block map buffer dirty.
- `blkmap_flush()` writes dirty workspace block map pages back to disk.

### JFS Block Allocation Map

- `blktbl_ctl_page_put()` writes the JFS block map control page through the generic map-control buffer.
- `blktbl_dmap_get()` locates and reads a dmap page for a block by using the selected aggregate block map inode and xTree lookup.
- `blktbl_dmap_put()` marks the dmap buffer dirty.
- `blktbl_dmaps_flush()` writes dirty dmap data.
- `blktbl_Ln_page_get()` reads summary-level `dmapctl` pages.
- `blktbl_Ln_page_put()` marks summary-level pages dirty.
- `blktbl_Ln_pages_flush()` writes dirty summary-level pages.

### Directory Nodes and Reconstruction

- `dnode_get()` reads or reuses cached directory dnode pages, bounds-checking against the fsck workspace boundary and marking swapped pages with `BT_SWAPPED`.
- `recon_dnode_assign()` allocates a reconstruction buffer for a new dnode and records its target offset in a trailer record.
- `recon_dnode_get()` allocates and reads an existing dnode into a reconstruction buffer.
- `recon_dnode_put()` writes a reconstruction dnode and releases the buffer.
- `recon_dnode_release()` releases a reconstruction buffer without writing.

### Extended Attributes

- `ea_get()` reads EA data from a block offset into caller-provided storage and returns `FSCK_BADEADESCRIPTOR` if the read is short.

### Fsck Log

- `fscklog_put_buffer()` writes the current fsck log buffer into the in-aggregate fsck log when read/write and not full.
- Log write failures are recorded in the workspace control page but deliberately do not stop fsck processing.
- The routine advances log offsets and marks log full when another buffer will not fit.

### Inode Allocation Groups and Inode Traversal

- `iag_get()` reads a specific IAG by table ownership, table inode, selected AIT, and IAG number.
- `iag_get_first()` initializes sequential IAG traversal, handling both root-leaf inode maps and external imap leaves.
- `iag_get_next()` advances sequential IAG traversal across imap leaves.
- `iag_put()` marks the IAG buffer dirty.
- `iags_flush()` writes dirty IAG data.

### Inode Extent Access

- `inode_get()` returns an inode by choosing the proper AIT part, locating the relevant IAG, finding the inode extent descriptor, reading the inode extent, and endian-swapping it.
- `inode_get_first_fs()` initializes sequential fileset inode traversal, starting at `FILESET_OBJECT_I`.
- `inode_get_next()` advances within an inode extent, then across allocated extents and IAGs.
- `inode_put()` marks the inode buffer dirty.
- `inodes_flush()` writes dirty inode extents after swapping to disk format and swaps back.

### Inode Table Control Pages and Generic Map Control Pages

- `inotbl_get_ctl_page()` locates aggregate or fileset inode table control pages, using AIT fixed offsets or the fileset inode map tree.
- `inotbl_put_ctl_page()` swaps and writes inode table control pages through `mapctl_put()`.
- `mapctl_get()` reads or reuses a generic map-control page buffer.
- `mapctl_put()` marks the generic map-control page buffer dirty.
- `mapctl_flush()` writes dirty generic map-control data.

### Device Access

- `open_device_read()` opens the target device/file read-only and initializes block size globals to `PBSIZE`.
- `open_device_rw()` attempts exclusive read/write open, falls back to non-exclusive read/write for kernels that reject `O_EXCL` on read-only-mounted block devices, and initializes block sizes.
- `open_volume()` chooses read-only or read/write access from fsck options and falls back to read-only if read/write open fails.
- `close_volume()` flushes and closes the device.
- `readwrite_device()` enforces journal target protection, sector alignment, dispatches to `ujfs_rw_diskblocks()`, and reports actual byte count as all-or-nothing.

## Buffering and Write Policy

Most `_put()` functions do not write immediately. They mark the corresponding buffer dirty, and the next get/flush operation writes it. Immediate writes are reserved for metadata where interruption diagnostics matter or where the buffer is transient:

- Immediate: workspace block map control page, fsck log buffer, reconstruction dnode writes.
- Deferred: block map pages, dmaps, summary pages, IAGs, inode extents, generic map control pages.

The standard pattern is:

1. If requested data is already in the matching buffer range, return a pointer.
2. Before reading a different page/extent, flush dirty buffer state.
3. Read from disk into the buffer.
4. Endian-swap into host format.
5. Record buffer offsets, logical positions, lengths, and ownership metadata.
6. Mark dirty with a `_put()` routine if caller mutates data.

## Safety Checks

- `readwrite_device()` refuses targets at or beyond `ondev_jlog_byte_offset`, preventing fsck from accidentally overwriting the journal.
- Many readers reject offsets beyond `agg_recptr->ondev_wsp_fsblk_offset`, treating them as corrupt metadata targets rather than I/O errors.
- Device offset and requested length must be sector-aligned.
- Short reads/writes are converted into explicit `FSCK_FAILED_*` errors with user/debug messages.
- Dirty flushes swap structures to disk format, write, then swap back to preserve in-memory host format.

## Notable Observations

- `checksum(uint8_t *, uint32_t)` is prototyped but not defined or used in this file.
- `mapctl_flush()` writes `mapctl_buf_data_len` bytes but checks `bytes_written == mapctl_buf_length`; this may be correct when those are always equal for control pages, but it is a detail worth verifying.
- Several debug/error messages in `imapleaf_get()` reference `node_*` buffer fields rather than `mapleaf_*` fields, likely due to shared/copy-paste diagnostics.
- The code assumes `readwrite_device()` performs all-or-nothing byte counts because it sets `actual_data_size` to `requested_data_size` on success and `0` otherwise.
- Endian swapping is intentionally caller-aware for generic map control pages because the buffer may contain either `dbmap` or `dinomap`.

## External Dependencies

The file relies on definitions and helpers from `xfsckint.h`, `xchkdsk.h`, `jfs_byteorder.h`, `devices.h`, and `utilsubs.h`.

Key external helpers include:

- Disk I/O: `ujfs_rw_diskblocks()`, `ujfs_flush_dev()`, `fopen_excl()`.
- Tree lookup: `xTree_search()`.
- Buffer allocation: `dire_buffer_alloc()`, `dire_buffer_release()`.
- Message system: `fsck_send_msg()`, `fsck_ref_msg()`, `msg_defs`.
- Byte swapping: `ujfs_swap_*()` and `swap_multiple()` helpers.

<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckpfs.h -->
# File Research: sources/local-fs/jfsutils/fsck/fsckpfs.h

## Role

`fsckpfs.h` is a minimal header for fsck physical I/O mode constants.

## Contents

It contains:

- Include guard `H_FSCKPFS`.
- `#define fsck_READ  1`
- `#define fsck_WRITE 2`

## Usage

These constants are used by `readwrite_device()` and many caller paths in `fsckpfs.c` to choose read versus write dispatch. They are also passed into diagnostic messages so errors can report the attempted operation.

## Design Notes

The header does not declare the functions implemented in `fsckpfs.c`; those declarations appear to come from broader fsck headers such as `xfsckint.h` or local prototypes inside `fsckpfs.c`. Its only responsibility is the operation mode namespace.

<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckruns.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckruns.c

## Role

`fsckruns.c` implements the fsck heartbeat display. It installs a `SIGALRM` handler that periodically prints rotating heartbeat messages while fsck runs, then can restore the default alarm handler.

## Functions

- `fsck_hbeat(int unused)`:
  - Signal handler for `SIGALRM`.
  - Maintains a static volatile `current_heartbeat` index.
  - Prints heartbeat messages `fsck_HEARTBEAT0` through `fsck_HEARTBEAT8`, then back down through `fsck_HEARTBEAT1`, creating a back-and-forth animation.
  - Flushes stdout.
  - Rearms `alarm(1)`.

- `fsck_hbeat_start(void)`:
  - Initializes a `sigaction`.
  - Sets `sa.sa_handler = &fsck_hbeat`.
  - Uses `SA_RESTART`.
  - Installs the handler for `SIGALRM`.
  - Starts the one-second alarm.

- `fsck_hbeat_stop(void)`:
  - Restores `SIGALRM` handler to `SIG_DFL`.
  - Cancels pending alarms with `alarm(0)`.

## Dependencies

- Includes `signal.h`, `string.h`, `unistd.h`, and `xfsckint.h`.
- Uses `msg_defs[fsck_HEARTBEAT*].msg_txt` for displayed text.
- Declares `extern char *MsgText[]`, though this file uses `msg_defs` directly rather than `MsgText`.

## Notable Behavior

The source comment explicitly says the heartbeat handler is racy and the implementation accepts that. From a strict POSIX signal-safety standpoint, calling `printf()` and `fflush()` inside a signal handler is not async-signal-safe. In this utility context the handler is only for progress display, and the code prioritizes simple status output over signal-handler purity.

## Operational Impact

This file does not affect filesystem repair logic or disk state. Its side effects are limited to:

- Installing/restoring the process alarm handler.
- Printing heartbeat status to stdout.
- Scheduling/canceling periodic alarms.

<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckruns.c -->