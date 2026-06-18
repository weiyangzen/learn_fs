# Group Research: group_1314_ntfs_3g_sources_local_fs_ntfs_3g_ntfsprogs_ntfsfix_c_sources_local__b4d4834a8009

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/ntfs-3g`, which is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfix.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfix.c

## Role

`ntfsfix.c` implements the `ntfsfix` utility. It is not a full NTFS checker; it performs a limited set of startup and metadata repairs, resets/empties the journal when needed, adjusts dirty state, and schedules Windows `chkdsk` by marking the volume dirty.

## Command-Line Contract

Supported options are:

- `-b/--clear-bad-sectors`: clear `$BadClus::$Bad`.
- `-d/--clear-dirty`: clear the dirty flag after a successful mount/repair path.
- `-n/--no-action`: run read-only and report possible fixes.
- `-h/--help`, `-V/--version`.

There is no real `--force` option in this file. `main()` has a local `force = FALSE`, so it refuses to operate on a read-write mounted device.

## Control Flow

1. `main()` parses options and refuses read-write mounted volumes.
2. It first tries a normal `ntfs_mount()`.
3. If full mount fails, `fix_mount()` allocates a device and calls `ntfs_volume_startup()`.
4. If startup fails, `fix_startup()` replays early startup steps manually and may repair a bad primary boot sector from alternate boot sectors or repair the rare self-located MFT condition.
5. On the fallback repair path, `fix_mount()` runs:
   - `fix_mftmirr()`
   - `fix_upcase()`
   - `set_dirty_flag()`
   - `empty_journal()`
6. After mount succeeds, `main()` always runs `check_alternate_boot()`, then either sets or clears `VOLUME_IS_DIRTY`, optionally clears `$BadClus`, reports NTFS version, and unmounts.

## Major Repair Operations

- `fix_mftmirr()` reads `$MFT` and `$MFTMirr` with MST fixups, validates mirrored records, and writes differing mirror records. If `$MFT` is corrupt and `$MFTMirr` appears valid, it may repair `$MFT` from `$MFTMirr`.
- `fix_upcase()` reads `$UpCase`, checks ASCII case mappings, and rewrites the default upcase table if corrupt and not in no-action mode.
- `check_alternate_boot()` compares primary and alternate boot sectors and rewrites the alternate boot sector when the primary is usable and the filesystem does not overflow the partition.
- `try_alternate_boot()` tries to rebuild the primary boot sector from alternate locations when the primary boot sector cannot parse.
- `fix_self_located_mft()` detects and repairs a rare Windows XP-era corruption where MFT data is described by an MFT record inside the MFT extension itself.
- `clear_badclus()` truncates and reallocates `$BadClus::$Bad` so clusters previously marked bad are unmarked, then clears sparse metadata flags.

## Important Dependencies

The tool directly depends on low-level ntfs-3g volume, device, boot-sector, MFT, runlist, bitmap, logfile, MST, inode, and attribute routines. Several repairs intentionally bypass high-level mount assumptions and use `ntfs_pread()`, `ntfs_pwrite()`, mapping-pair decompression, and raw MFT record writes.

## Risk Areas

- The successful initial mount path does not call `fix_mftmirr()`, `fix_upcase()`, `set_dirty_flag()`, or `empty_journal()`; those run only after startup/mount recovery in `fix_mount()`. The log message on immediate mount success says MFT processing completed even though no comparison was performed there.
- `$MFTMirr` repair has comments warning it does not fully verify that the mirror location is truly correct, especially around software RAID experiments.
- `-d/--clear-dirty` can clear the dirty flag after a successful mount, even though `ntfsfix` normally marks the volume dirty to force Windows checking.
- `-b/--clear-bad-sectors` intentionally frees bad-cluster markings and is dangerous if physical media defects are real.
- Several repairs perform raw sector/MFT writes; interruption during these writes could leave the volume worse.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfix.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsinfo.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsinfo.8.in

## Role

`ntfsinfo.8.in` is the manual page template for `ntfsinfo`, describing it as a utility to dump attributes for an inode or path and/or volume/MFT information.

## Documented Interface

The manpage documents:

- `-F/--file FILE`: inspect a file by absolute path.
- `-i/--inode NUM`: inspect an inode/MFT record.
- `-m/--mft`: show volume information.
- `-t/--notime`: suppress timestamps.
- `-f/--force`: use less caution.
- `-q/--quiet`, `-v/--verbose`.
- `-h/--help`, `-V/--version`.

## Relationship To Implementation

The documented read-only inspection role matches `ntfsinfo.c`. One mismatch is important: the C option table maps long `--notime` to `T`, but the parser treats `T` as deprecated/error and accepts lowercase `-t` as the working notime option. The manpage says `--notime` works.

## Notes

The BUGS section says there are no known problems, but `ntfsinfo.c` contains a substantial TODO list and several incomplete attribute dumpers.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsinfo.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsinfo.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsinfo.c

## Role

`ntfsinfo.c` implements the `ntfsinfo` utility. It mounts an NTFS volume read-only, optionally dumps volume-wide metadata, resolves an inode number or path, and prints the MFT record plus decoded NTFS attributes.

## Command-Line Contract

Supported options include:

- `-i/--inode NUM`
- `-F/--file FILE`
- `-m/--mft`
- `-t` for no timestamps
- `-f/--force` to mount with recovery
- `-q`, `-v`, `-V`, `-h`

The long option `--notime` is wired to parser case `T`, which emits a deprecation/error message; lowercase `-t` is the option that actually sets `opts.notime`.

## Control Flow

1. `main()` sets line-buffered stdout and stderr logging.
2. `parse_options()` validates that a device is present and at least one of inode, file, or `--mft` was requested.
3. The volume is mounted read-only through `utils_mount_volume()`, with `NTFS_MNT_RECOVER` if forced.
4. `ntfs_dump_volume()` runs when `opts.mft` is set.
5. If a path or inode is requested, the code opens it with `ntfs_pathname_to_inode()` or `ntfs_inode_open()`.
6. It prints MFT record-level data via `ntfs_dump_inode_general_info()`.
7. It enumerates all attributes with `ntfs_attr_lookup()` and dispatches type-specific dumpers in `ntfs_dump_file_attributes()`.

## Volume Dumping

`ntfs_dump_volume()` reports device state, volume flags/version, sector and cluster sizes, index block size, MFT zone state, `$MFTMirr`, `$AttrDef`, `$Bitmap`, free cluster count, and `$LogFile` state. `$LogFile` details are obtained by opening `FILE_LogFile` and calling `ntfs_check_logfile()`.

## Attribute Dumping

Implemented dumpers cover:

- `$STANDARD_INFORMATION`: timestamps, file attributes, owner/security/quota fields for 72-byte records.
- `$ATTRIBUTE_LIST`: verbose attribute-list entry dump.
- `$FILE_NAME`: parent reference, times, sizes, flags, namespace, filename, reparse tag or EA length.
- `$OBJECT_ID`: object and birth GUIDs.
- `$SECURITY_DESCRIPTOR`: owner/group SIDs plus SACL/DACL ACEs.
- `$VOLUME_NAME` and `$VOLUME_INFORMATION`.
- `$DATA`: metadata-specific verbose handling for `$Secure::$SDS` and `$LogFile`.
- `$INDEX_ROOT` and `$INDEX_ALLOCATION`: index type detection, headers, entries, INDX block fixups, and totals.
- `$REPARSE_POINT`: tag, type name, data length, and first bytes.
- `$EA_INFORMATION` and `$EA`: extended attribute summary and verbose value dump.
- `$LOGGED_UTILITY_STREAM`: verbose hex dump.
- Unknown resident attributes: first 128 bytes are hex dumped.

`$BITMAP` and `$PROPERTY_SET` are placeholders.

## Index And Security Handling

The code recognizes directory `$I30`, `$Secure` indexes (`$SII`, `$SDH`), `$ObjId`, `$Quota`, and `$Reparse` index names. For `$Secure::$SDS`, it opens `$SDS`, walks `$SII`, reads descriptor records by offset, and dumps their security descriptors.

## Risk Areas

- This is a read-only utility, but it casts on-disk structures directly and has limited bounds checking in several dumpers.
- Several TODOs remain, especially around incomplete attribute support, error checking, formatting, ACLs, and indexed attribute coverage.
- `ntfs_dump_attr_ea()` and `ntfs_dump_attr_security_descriptor()` contain comments saying fragmented mapping-pair cases are not fully handled.
- Recursive index dumping depends on bitmap bits and index block reads; damaged metadata can stop dumping early.
- The `--notime` long option mismatch is user-visible.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfslabel.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfslabel.8.in

## Role

`ntfslabel.8.in` is the manual page template for `ntfslabel`, documenting display and modification of an NTFS volume label and volume serial number.

## Documented Interface

The manpage documents:

- Default behavior: print current label.
- Positional `new-label`: set the volume label.
- `--new-serial[=ssssssssssssssss]`: set a full 64-bit serial.
- `--new-half-serial[=ssssssss]`: set only the upper serial half.
- `-n/--no-action`: dry run.
- `-f/--force`: operate despite mounted-volume caution.
- `-q`, `-v`, `-V`, `-h`.

## Relationship To Implementation

The serial-number semantics match `ntfslabel.c`: full serial replacement or upper-half replacement, random when no argument is supplied. The manpage’s 128 Unicode character label limit also matches implementation truncation at `0x100` bytes of UTF-16.

## Notes

The document correctly warns that duplicate serial numbers can prevent simultaneous mounts on the same machine and that this serial is not the Windows object-location volume UUID.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfslabel.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfslabel.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfslabel.c

## Role

`ntfslabel.c` implements the `ntfslabel` utility. It displays or changes an NTFS volume label, and can also display or change the boot-sector volume serial number.

## Command-Line Contract

Supported options include:

- Positional `device [label]`.
- `--new-serial[=hex]` and `--new-half-serial[=hex]`.
- `-n/--no-action`.
- `-f/--force`.
- `-q`, `-v`, `-V`, `-h`.

The short option string includes `I` and `i` internally for serial options, but usage presents them as long options.

## Control Flow

1. `parse_options()` captures the device, optional label, force/no-action/logging flags, and optional serial override.
2. `main()` refuses modifications to mounted devices unless forced or no-action.
3. If no label and no serial operation is requested, it forces read-only/no-action mode.
4. The volume is mounted with read-only when no-action and with recovery when forced.
5. Serial handling runs first:
   - `set_new_serial()` changes primary and backup boot-sector serials.
   - verbose mode without serial change prints the serial.
6. Label handling then either calls `change_label()` or `print_label()`.
7. The volume is unmounted without requesting dirty cleanup.

## Label Handling

`change_label()` converts the input label to NTFS Unicode with `ntfs_mbstoucs()`, truncates labels longer than 128 UTF-16 characters, and calls `ntfs_volume_rename()` unless no-action is set.

## Serial Handling

`set_new_serial()` either uses the provided hex serial or generates a random 64-bit value using `random()` seeded with time and PID. `change_serial()` writes the primary boot sector, then writes the backup boot sector only if it matches the saved original primary sector. The half-serial mode preserves the lower 32 bits.

## Risk Areas

- Bad serial hex input logs an error but does not increment the parse error count, so malformed serial arguments may still proceed with a parsed partial value.
- Backup boot-sector serial changes are skipped if the backup does not match the primary, which avoids overwriting divergent backup data but can leave serials inconsistent.
- `print_label()` warns when the target is mounted read-write because results may be unreliable.
- Forced writes to mounted devices are allowed with `--force` and can race with an active filesystem.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfslabel.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsls.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsls.8.in

## Role

`ntfsls.8.in` is the manual page template for `ntfsls`, documenting directory and file listing inside an NTFS filesystem or image.

## Documented Interface

The manpage documents:

- `-p/--path PATH`: directory or file to list.
- `-a/--all`: include all files / POSIX namespace entries.
- `-s/--system`: include system files.
- `-x/--dos`: show DOS 8.3 names instead of Win32 names.
- `-l/--long`: long listing.
- `-i/--inode`: include MFT reference.
- `-F/--classify`: append classification indicator.
- `-R/--recursive`: recurse below the requested directory.
- `-f`, `-q`, `-v`, `-V`, `-h`.

## Relationship To Implementation

The option list matches `ntfsls.c`. The expanded synopsis omits `-R/--recursive`, although the option is documented in the OPTIONS section and implemented.

## Notes

The documentation says the default path is the root directory and the device may be a block device or NTFS image file. This matches the implementation’s default `opts.path = "/"` and `utils_mount_volume()` usage.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsls.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsls.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsls.c

## Role

`ntfsls.c` implements the `ntfsls` utility. It mounts an NTFS volume read-only and lists a directory’s entries or a single file’s selected name.

## Command-Line Contract

Supported options include:

- `-p/--path PATH`, default `/`.
- `-a/--all`, `-s/--system`, `-x/--dos`.
- `-l/--long`, `-i/--inode`, `-F/--classify`.
- `-R/--recursive`.
- `-f/--force`, `-q`, `-v`, `-V`, `-h`.

If `-s` is not specified, the parser defaults to `-a`, so normal user entries are listed broadly while metadata MFT records below `FILE_first_user` are hidden.

## Control Flow

1. `main()` parses options and mounts the volume read-only, adding recovery mode if forced.
2. It opens `opts.path` with `ntfs_pathname_to_inode()`.
3. If the inode is a directory:
   - non-recursive mode calls `ntfs_readdir()` with `list_dir_entry()`;
   - recursive mode calls `readdir_recursive()`.
4. If the inode is a file, it chooses a preferred `$FILE_NAME` attribute and sends it through `list_dir_entry()`.
5. It closes the inode and unmounts the volume.

## Listing Behavior

`list_dir_entry()` converts NTFS Unicode names to the current locale, filters metadata/system records, filters namespace entries based on `-a` and `-x`, optionally appends `/` for directories, and prints either simple names, inode-prefixed names, or long-format rows.

Long format opens each listed inode, reads `$FILE_NAME` for last data-change time, and reads unnamed `$DATA` length for file size when the entry is not a directory.

## Recursive Traversal

`readdir_recursive()` maintains static list heads for queued directories and path components. It prints each directory header, lists entries, queues subdirectories, then descends by reopening subdirectories relative to the parent inode.

## Risk Areas

- Recursive traversal has no explicit depth limit or cycle detection.
- `list_dir_entry()` appends `/` with `sprintf()` into a `MAX_PATH` buffer, so an already maximum-length converted name can overflow.
- Long-format size reporting only considers unnamed `$DATA`; alternate data streams are not included.
- Error handling in `main()` has FIXME comments and ignores some `ntfs_readdir()` failures.
- Recursive state is stored in static locals, making the function unsuitable for reentrant use.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsls.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmftalloc.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmftalloc.c

## Role

`ntfsmftalloc.c` implements `ntfsmftalloc`, a quarantined/developer utility that allocates and initializes a base or extent MFT record.

## Command-Line Contract

Usage is `ntfsmftalloc [options] device [base-mft-record]`.

Options include:

- `-n`: no-action/read-only mount.
- `-f`: force execution despite mount checks.
- `-q`, `-v`, `-vv`.
- `-V`: version.
- `-l`: license.
- `-h`: help.

If a base MFT record number is supplied, the allocated record is an extent linked to that base inode. Without it, a base MFT record is allocated.

## Control Flow

1. `parse_options()` prints the version banner, parses device and optional base MFT number.
2. `main()` checks whether the device is mounted and refuses unless forced.
3. It mounts read-only for `-n`, otherwise read-write.
4. It registers `ntfsmftalloc_exit()` with `atexit()` to close inodes and unmount on failure.
5. If a base MFT number was supplied, it opens the base inode.
6. It calls `ntfs_mft_record_alloc(vol, base_ni)`.
7. In very verbose mode, it dumps the allocated MFT record header.
8. It closes the allocated/base inode, unmounts, and disables the failure cleanup path by setting `success = TRUE`.

## Important Dependencies

The utility depends on ntfs-3g MFT allocation internals, inode open/close, volume mount/unmount, mount-state checks, and logging. It is built as a quarantined program in `Makefile.am`, not as a normal installed tool.

## Risk Areas

- This is a direct metadata allocator and should be treated as a developer/test tool.
- `-n` only changes the mount flags to read-only; the code still calls `ntfs_mft_record_alloc()`, relying on lower layers to prevent writes.
- The parser rejects base record `0` because it treats `!ll` as invalid.
- Failure cleanup mutates global `ni` to `base_ni` before close, which is intentional but makes ownership subtle.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmftalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmove.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmove.c

## Role

`ntfsmove.c` implements `ntfsmove`, a quarantined/experimental utility intended to relocate non-resident file data runs on an NTFS volume.

## Command-Line Contract

Usage is `ntfsmove [options] device file`.

Location options are mutually exclusive:

- `-S/--start`
- `-B/--best`
- `-E/--end`
- `-C/--cluster NUM`

Other options:

- `-D/--no-dirty`
- `-n/--no-action`
- `-f/--force`
- `-q`, `-v`, `-V`, `-h`

If no location is supplied, `--best` is selected.

## Control Flow

1. `parse_options()` captures device, file, location, mount, logging, and dirty-flag options.
2. `main()` mounts the volume, read-only for `--no-action` and recovery-capable for `--force`.
3. It resolves the target file path to an inode.
4. `move_file()` rejects unsafe files, enumerates all attributes, and relocates non-resident attributes.
5. `move_attribute()` decompresses mapping pairs and calls `move_datarun()` for each mapped run.
6. `move_datarun()` finds free space, rewrites mapping pairs, moves clusters, marks the inode dirty, and syncs it.
7. If bytes moved and dirty marking is not suppressed, `main()` writes `VOLUME_IS_DIRTY`.

## Data Movement Mechanics

- `find_unused()` scans `$Bitmap` for a contiguous free run.
- `move_runlist()` validates source clusters are allocated and destination clusters are free, sets destination bits, copies cluster data, and clears source bits.
- `resize_nonres_attr()` adjusts MFT record layout if the encoded mapping-pair array size changes.
- `ntfs_mapping_pairs_build()` writes the new mapping pairs into the attribute record.

## Safety Filters

`dont_move()` refuses to move metadata files, files with attribute lists, extent inodes lacking `$FILE_NAME`, and `ntldr`.

## Important Limitations And Bugs

- `find_unused()` ignores the requested location and flags, so `--start`, `--best`, `--end`, and `--cluster` do not actually control placement.
- `find_unused()` scans only `allocated_size / 8192` full chunks of the bitmap and can miss a trailing partial chunk.
- `move_datarun()` appears to update only the first runlist entry because it loops over the one-entry destination runlist while indexing the source runlist. Later source runs may be copied without having their mapping-pair LCN updated correctly.
- `--no-action` mounts read-only but does not short-circuit write-oriented bitmap, data-copy, and inode-sync code.
- The operation has crash windows: destination bitmap bits are set, data is copied, source bits are cleared, and only then are mapping pairs committed. Failures have little rollback.
- Several error paths leak temporary runlists or allocated buffers.
- The tool is quarantined in the build system, which is consistent with its incomplete and risky state.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmove.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmove.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmove.h

## Role

`ntfsmove.h` is the private header for `ntfsmove.c`. It defines placement constants and the shared option structure.

## API Contents

It defines:

- `NTFS_MOVE_LOC_START = -1000`
- `NTFS_MOVE_LOC_BEST = -1001`
- `NTFS_MOVE_LOC_END = -1002`

It also defines `struct options` with device path, file path, target location, force/quiet/verbose flags, no-action mode, and no-dirty mode.

## Integration

`ntfsmove.c` owns a global `static struct options opts` using this type. Positive `location` values represent explicit cluster offsets from `--cluster`; negative constants represent symbolic placement modes.

## Risk Note

The header expresses a richer placement model than the implementation currently honors. `ntfsmove.c` parses these values, but its free-space search ignores them.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmove.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsprogs.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsprogs.8.in

## Role

`ntfsprogs.8.in` is the overview manual page for the ntfs-3g NTFS utility suite.

## Content Summary

It describes `ntfsprogs` as a shared-library-based suite of NTFS utilities and lists the major tools:

- creation and resize: `mkntfs`, `ntfsresize`
- inspection/listing: `ntfsinfo`, `ntfsls`, `ntfscluster`, `ntfscmp`
- data movement/copying: `ntfscat`, `ntfscp`
- repair/recovery: `ntfsfix`, `ntfsrecover`, `ntfsundelete`, `ntfsclone`
- mutation/wiping/truncation: `ntfslabel`, `ntfsfallocate`, `ntfstruncate`, `ntfswipe`

## Relationship To This Batch

This overview includes the normal tools researched here: `ntfsfix`, `ntfsinfo`, `ntfslabel`, `ntfsls`, and `ntfsrecover`. It does not mention quarantined developer utilities such as `ntfsmftalloc` and `ntfsmove`.

## Notes

The manpage is descriptive only; it contains no executable logic. It points readers to `ntfs-3g(8)` and the upstream project availability URL.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsprogs.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.8.in

## Role

`ntfsrecover.8.in` is the manual page template for `ntfsrecover`, documenting recovery of Windows-committed NTFS metadata transactions from `$LogFile`.

## Conceptual Model

The page explains NTFS metadata updates as transactions: multiple metadata records must be updated together, and Windows logs requested metadata actions before applying them. If interruption occurs after commit, the log can be replayed to restore metadata consistency.

`ntfsrecover` applies committed Windows log actions that were not completed. It does not recover user data updates, and it cannot repair Linux-side crashes because ntfs-3g does not log its own metadata updates.

## Documented Interface

Normal usage is no option or `-s/--sync`.

Developer/inspection options include:

- `-b/--backward`: inspect log actions backward without applying updates.
- `-f/--forward NUM`: inspect forward without applying updates.
- `-r/--range BLOCK-RANGE`: inspect a log block range.
- `-c/--clusters CLUSTER-RANGE`: filter output by affected clusters.
- `-t/--transactions COUNT`: display transaction parameters.
- `-p/--play COUNT`: undo transaction sets and redo one.
- `-u/--undo COUNT`: undo transaction sets.
- `-k/--kill-fast-restart`: apply log changes and discard Windows fast-restart cached changes.
- `-n/--no-action`, `-v`, `-V`, `-h`.

## Safety Notes

The page explicitly marks `--kill-fast-restart` as dangerous and data-loss-prone. It also notes that undo/play operations may not always be possible because some actions are not undoable.

## Relationship To Build

`Makefile.am` builds `ntfsrecover` from `playlog.c`, `ntfsrecover.c`, `utils.c`, `utils.h`, and `ntfsrecover.h`; those implementation files are outside this work item.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.8.in -->