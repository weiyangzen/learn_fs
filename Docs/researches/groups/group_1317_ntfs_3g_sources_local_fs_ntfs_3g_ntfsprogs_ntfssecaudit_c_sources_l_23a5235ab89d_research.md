# Group Research: group_1317_ntfs_3g_sources_local_fs_ntfs_3g_ntfsprogs_ntfssecaudit_c_sources_l_23a5235ab89d

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfssecaudit.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfssecaudit.c

## File Role

`ntfssecaudit.c` implements `ntfssecaudit`, a standalone NTFS security metadata inspection, backup, restore, audit, and permission-setting utility. It works through libntfs-3g security APIs and can operate on unmounted NTFS volumes as root, mounted NTFS files via extended attributes on Unix builds with xattr support, and Windows paths with drive/path splitting support.

The program covers several distinct command families:

- audit raw `$Secure` metadata: `$SDS`, `$SII`, and `$SDH`
- display security descriptors from raw hex dumps
- display NTFS ACL/security information for a file or recursive tree
- back up ACLs and Windows file attributes in a textual/hex dump format
- restore ACL backups, optionally including Windows attributes
- set file permissions from an octal mode or POSIX ACL description
- generate `.NTFS-3G/UserMapping` proposals from file owner/group SIDs
- optional compile-time self-tests for SID, mode, and POSIX ACL conversions

## Major Dependencies

The file uses ntfs-3g internals heavily:

- `security.h` and `acls.h` for security descriptor parsing, SID mapping, permission conversion, and file security APIs
- `volume.h`, `inode.h`, `attrib.h`, `index.h`, `mft.h`, `layout.h`, `mst.h`, and `runlist.h` for raw NTFS metadata access
- `unistr.h`, `ntfstime.h`, `endians.h`, `types.h`, and `utils.h` for encoding, timestamps, endian-safe fields, and support routines
- `realpath.h` and OS headers for mounted-file and mapping-file path handling
- optional `sys/xattr.h` for mounted Unix file ACL display through `system.ntfs_acl` and `system.ntfs_attrib`

The build entry in `ntfsprogs/Makefile.am` lists `ntfssecaudit.c` with `utils.c` and links it against the normal ntfs-3g libraries plus `NTFSRECOVER_LIBS`.

## Core State

Important file-global state:

- `cmd`: selected command mode (`CMD_AUDIT`, `CMD_BACKUP`, `CMD_HEX`, `CMD_SET`, `CMD_USERMAP`, etc.)
- `opt_e`, `opt_r`, `opt_u`, `opt_v`: restore-extra, recurse, user-map proposal, and verbosity controls
- `errors`, `warnings`: accumulated severe and non-severe diagnostics, which drive exit status
- `ntfs_context`: active `SECURITY_API` returned by `ntfs_initialize_file_security`
- `context.mapping` and `mappingtype`: local/external/dummy SID-to-uid/gid mapping state
- `securdata[]`: sparse block table indexed by NTFS security ID, used to correlate `$SDS`, `$SII`, `$SDH`, recursive file usage counts, descriptor hashes, offsets, lengths, and display deduplication

Key structs local to this file include `SII` and `SDH` on-disk index-entry images, `SECURITY_DATA` for cross-checking security IDs, and small linked-list/callback structs used when recursively enumerating directories.

## Security Descriptor Display

The low-level helpers read and write little-endian fields from raw descriptor bytes (`get2l`, `get4l`, `get6h`, `get8l`, `set2l`, `set4l`), compute NTFS security hashes, and produce hex dumps.

Descriptor presentation is layered:

- `showsid()` decodes and labels well-known SIDs where possible, then prints hex and decimal SID forms.
- `showheader()` prints descriptor revision, control flags, and owner/group/SACL/DACL offsets.
- `showace()` decodes ACE type, inheritance/audit flags, access masks, standard rights, generic rights, SID, and a compact grant/deny summary.
- `showacl()`, `showdacl()`, and `showsacl()` walk ACLs and ACEs.
- `showownership()` prints Windows owner/group SIDs and optional account names on Windows.
- `linux_permissions()` and, when compiled with POSIX ACL support, `linux_permissions_posix()` derive Unix mode or POSIX ACL views from the NTFS descriptor.

`showhex()` reads text containing hex dump lines, reconstructs descriptors, validates them with `ntfs_valid_descr`, computes hashes, estimates file-vs-directory from inheritable ACEs, and displays the descriptor at high verbosity.

## Mapping Handling

`local_build_mapping()` searches for `.NTFS-3G/UserMapping` near a mounted file path on Unix or in the NTFS root on Windows. If no mapping is found, it installs a default single-user mapping using the default security authority constants. This mapping feeds Unix owner/group interpretation and POSIX ACL conversion.

`proposal()` generates a candidate UserMapping snippet when a file owner and group look like Windows domain SIDs (`S-1-5-21-...`). On Unix it tries to locate the NTFS filesystem root by walking toward inode 5 and prints an example `.NTFS-3G/UserMapping` path.

## Backup and Restore

`showfull()` is the central display/backup routine. It gathers owner, group, DACL, SACL, and Windows attributes separately, merges descriptor parts into a single self-relative descriptor, validates it, computes hashes, displays or stores security-key data, and prints interpreted Unix ownership/mode.

`backup()` opens an unmounted volume read-only and recursively calls `recurseshow()` from a root path, producing a textual ACL collection with security-key summaries.

`restore()` parses a backup stream. It detects file/directory markers, security keys, Windows attribute lines, descriptor hex dumps, and expected hashes. `applyattr()` then reuses explicit descriptors or previously stored descriptors by key, optionally restores Windows attributes, and calls `ntfs_set_file_security()` with owner, group, DACL, and SACL selection flags.

`dorestore()` requires root, opens the volume read-write, runs `restore()`, and closes the security API.

## Permission Setting

For non-POSIX-ACL builds, `setfull()` reads the current descriptor, extracts current owner/group SIDs, builds a new descriptor from an octal mode with `ntfs_build_descr()`, and writes owner/group/DACL information back.

For POSIX ACL builds, `encode_posix_acl()` parses strings like `[d:]{u,g,m,o}:id:perms,...` or octal modes into a `POSIX_SECURITY` object, including implicit mask insertion. `setfull_posix()` merges requested ACL/mode changes with the old POSIX descriptor, builds a new NTFS descriptor through `ntfs_build_descr_posix()`, and writes it back.

Recursive setting uses `recurseset()` or `recurseset_posix()` and directory enumeration via `ntfs_read_directory()` plus `callback()`.

## Mounted-File Path

On Unix with xattr support, `processmounted()` handles display or mapping proposal for already mounted NTFS files without root/unmounted-volume access. It reads:

- `system.ntfs_acl` for the raw NTFS security descriptor
- `system.ntfs_attrib` for Windows attributes

It then validates and displays the descriptor using the same conversion/display helpers. Without xattr support, this mode reports that an unmounted partition must be used.

## Raw `$Secure` Audit

The audit mode validates consistency across NTFS security metadata:

- `audit_sds(FALSE)` and `audit_sds(TRUE)` read the two `$SDS` copies, validate descriptor entry sizes, hashes, offsets, security IDs, ordering, and deleted entries.
- `audit_sii()` walks `$SII` index entries sorted by security ID and cross-checks hash, offset, and length against `$SDS`.
- `audit_sdh()` walks `$SDH` index entries sorted by hash/security ID and cross-checks the same metadata.
- `audit_summary()` reports security IDs not present in every expected structure and, with recursion, file-use counts.

`SECURITY_DATA.flags` records whether each ID was seen in `$SDS-1`, `$SDS-2`, `$SII`, and `$SDH`.

## CLI and Control Flow

`parse_options()` accepts `-a`, `-b`, `-e`, `-h`, `-H`, `-r`, `-s`, `-u`, `-v`, `-V`, and compile-time `-t`. It rejects incompatible commands and returns the index of the first non-option argument.

`main()` prints a banner, initializes global tables and mappings, dispatches command-specific argument shapes, reports warnings/errors to stdout and stderr when stdout is redirected, frees split Windows paths and security blocks, and exits nonzero when command syntax failed or severe errors were recorded.

## Notable Risks and Maintenance Notes

- The file is large and multiplexes raw-volume, mounted-file, Windows-path, backup/restore, and POSIX ACL behaviors through global state.
- Several descriptor parsers assume bounded raw byte layouts and depend on `MAXATTRSZ` and `ntfs_valid_descr()` to reject malformed descriptors.
- Restore mode applies descriptors from text backup streams and trusts security-key reuse after hash checks.
- Root/write operations are guarded by `getuid()` and open mode, but permission-setting and restore paths directly modify NTFS security metadata.
- The optional self-test code is extensive but disabled by `SELFTESTS 0` in this file.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfssecaudit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfstruncate.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfstruncate.8.in

## File Role

`ntfstruncate.8.in` is the manual page template for the `ntfstruncate` utility. It describes the tool as truncating or extending a specified NTFS attribute belonging to a file or directory.

The documented synopsis is:

`ntfstruncate [options] device file [attr-type [attr-name]] new-length`

This presents the target as a file path, not an inode number.

## Documented Interface

The page documents these options:

- `-f`, `--force`: override safety checks such as refusing mounted volumes
- `-h`, `--help`: show help
- `-l`: show license
- `-n`, `--no-action`: simulate without writing
- `-q`, `--quiet`: suppress output
- `-v`, `--verbose`: increase output
- `-V`, `--version`: print version/copyright/license

It also documents advanced attribute selection by numeric NTFS attribute type and optional attribute name. The attribute table lists common NTFS attribute IDs from `$STANDARD_INFORMATION` (`0x10`) through `$LOGGED_UTILITY_STREAM` (`0x100`), with `$DATA` (`0x80`) as the default.

`new-length` is described as accepting decimal sizes plus SI suffixes (`K`, `M`, `G`, `T`, `P`, `E`) and binary suffixes (`Ki`, `Mi`, `Gi`, `Ti`, `Pi`, `Ei`), rounded to a cluster-size multiple.

## Examples and Context

The example shows resizing `/Data/database.db` to `100M` on `/dev/sda1`.

The page links `ntfstruncate` with `ntfs-3g`, `ntfsfallocate`, and `ntfsprogs`, and says it is part of the ntfs-3g package.

## Notable Mismatch

The implementation in `ntfstruncate.c` parses the second positional argument as an MFT inode number, and parses `new-length` with plain `strtoll()` without suffix handling. This man page therefore documents a more user-facing pathname/suffixed-size interface than the current C implementation actually provides.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfstruncate.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfstruncate.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfstruncate.c

## File Role

`ntfstruncate.c` implements the `ntfstruncate` command. It opens an NTFS volume, opens a specified MFT inode and attribute, and calls `ntfs_attr_truncate()` to resize that attribute.

Despite the man page describing a file path, this source expects:

`ntfstruncate [options] device inode [attr-type [attr-name]] new-length`

The default attribute is unnamed `$DATA`.

## Major Dependencies

The utility uses libntfs-3g primitives and layout definitions:

- `ntfs_check_if_mounted`, `ntfs_mount`, `ntfs_umount`
- `ntfs_inode_open`, `ntfs_inode_close`
- `ntfs_attr_open`, `ntfs_attr_close`, `ntfs_attr_truncate`
- `ntfs_mbstoucs`, `ntfs_ucsfree`
- `attrdef_ntfs3x_array` for attribute-name display in verbose MFT dumps
- NTFS layout structs such as `MFT_RECORD`, `ATTR_RECORD`, `VOLUME_INFORMATION`, and `ATTR_DEF`

The Makefile builds it from `attrdef.c`, `ntfstruncate.c`, `utils.c`, and `utils.h`.

## Global State

The file keeps command and resource state globally so `ntfstruncate_exit()` can clean up on error:

- `dev_name`, `inode`, `attr_type`, `attr_name`, `attr_name_len`, `new_len`
- `vol`, `ni`, `na`
- `attr_defs`
- `success`
- `opts` containing `no_action`, `quiet`, `verbose`, and `force`

## Option Parsing

`parse_options()` handles short options only:

- `-f`: force
- `-n`: no-action/read-only mode
- `-q`: quiet
- `-v`: verbose; `-vv` enables debug/trace logging
- `-V`: version
- `-l`: license
- `-h`/`-?`: usage

It validates the inode as a nonzero integer, optional attribute type as a nonzero integer, optional attribute name through `ntfs_mbstoucs()`, and new length as a non-negative plain integer. It does not implement the suffix parsing documented in the man page.

## Debug Dump Helpers

When `-vv` is active, the program dumps the MFT record before and after truncation:

- `dump_mft_record()` prints MFT header metadata and iterates attributes.
- `dump_attr_record()` prints type, length, residency, name, flags, and instance.
- `dump_resident_attr()` and `dump_non_resident_attr()` print resident/nonresident details.
- `dump_resident_attr_val()` decodes a small subset of resident values, notably `$VOLUME_NAME` and `$VOLUME_INFORMATION`; many attribute types are explicitly TODO.
- `dump_mapping_pairs_array()` is a placeholder TODO.

These dumps are diagnostic only; truncation itself is entirely delegated to libntfs-3g.

## Main Flow

`main()`:

1. Initializes logging and default NTFS 3.x attribute definitions.
2. Parses CLI arguments.
3. Sets locale.
4. Checks whether the volume is mounted and refuses unless `-f` is set.
5. Mounts read-only for `--no-action`, otherwise read-write.
6. Registers `ntfstruncate_exit()` for cleanup.
7. Opens the target inode and attribute.
8. Optionally dumps the MFT record.
9. Calls `ntfs_attr_truncate(na, new_len)`.
10. Optionally dumps the MFT record again.
11. Closes the attribute and inode, unmounts, frees the attribute name, and marks `success`.

## Safety and Risks

- Mounted-volume protection exists, but `-f` bypasses it.
- `--no-action` only switches the volume mount to read-only; the code still calls `ntfs_attr_truncate()`, relying on lower layers/read-only mount behavior to prevent writes.
- The target is an inode number, so users need precise metadata knowledge.
- Attribute diagnostics are incomplete and some display functions have TODO placeholders.
- Cleanup is centralized and avoids leaking open volume/inode/attribute handles after failures.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfstruncate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.8.in

## File Role

`ntfsundelete.8.in` is the manual page template for `ntfsundelete`, documenting recovery of deleted files from an NTFS volume.

It describes three modes:

- scan: default, list deleted files and recovery likelihood
- undelete: recover files selected by inode range or name pattern
- copy: expert/debug mode that copies MFT record ranges to a host file

The page emphasizes that `ntfsundelete` only reads the NTFS volume and never modifies it.

## Documented Behavior

The caveats section explains important recovery limits:

- deleted data may already have been overwritten
- MFT records may be reused
- extended/multi-record metadata is not reconstructed
- compressed and encrypted files cannot be recovered
- recovered file size and dates may be unreliable because deleted metadata can be inconsistent

The scan output is documented as:

`Inode Flags %age Date Time Size Filename`

with flags for file/directory, resident/nonresident stream, compressed/encrypted stream, and missing/multi-record attributes.

## Documented Options

Main scan filters:

- `-m`, `--match PATTERN`
- `-C`, `--case`
- `-p`, `--percentage NUM`
- `-S`, `--size RANGE`
- `-t`, `--time SINCE`
- `-P`, `--parent` with verbose output

Recovery options:

- `-u`, `--undelete`
- `-i`, `--inodes RANGE`
- `-o`, `--output FILE`
- `-d`, `--destination DIR`
- `-b`, `--byte NUM`
- `-O`, `--optimistic`
- `-T`, `--truncate`

Copy/debug option:

- `-c`, `--copy RANGE`

General options:

- `-f`, `--force`
- `-q`, `--quiet`
- `-v`, `--verbose`
- `-V`, `--version`
- `-h`, `--help`

## Examples

The examples cover scanning a device, matching `*.doc`, filtering by size/percentage/time, undeleting explicit inode ranges, recovering with a custom output path and exact truncation, and copying MFT records to a debug file.

## Integration Notes

The documented behavior aligns closely with `ntfsundelete.c`: read-only volume access, host-side recovered output files, wildcard matching, inode ranges, and MFT-copy mode are all implemented.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.c

## File Role

`ntfsundelete.c` implements the `ntfsundelete` command. It mounts an NTFS volume read-only, scans deleted MFT records, estimates recoverability from the allocation bitmap, and writes recovered data streams to files outside the NTFS volume.

It supports:

- scanning deleted records
- undeleting by inode range
- undeleting by filename pattern
- copying raw MFT record ranges
- filtering by name, size, modification time, and recoverability
- filling unrecoverable regions with a configured byte
- optional optimistic recovery from clusters currently marked in use

## Major Dependencies

The file uses:

- `ntfsundelete.h` for option and recovered-file structs
- `bootsect.h`, `mft.h`, `attrib.h`, `layout.h`, `inode.h`, and `device.h`
- `ntfs_attr_open`, `ntfs_attr_pread`, `ntfs_attr_mst_pread`, `ntfs_attr_close`
- `ntfs_mapping_pairs_decompress`
- `utils_mount_volume`, `utils_cluster_in_use`, `utils_parse_range`
- `ntfs_cluster_read`
- `ntfs_ucstombs`, `ntfs_mbstoucs`
- `ntfs2timespec`
- optional system regex; if absent, an internal wildcard matcher over NTFS Unicode names is compiled

The Makefile builds it from `ntfsundelete.c`, `ntfsundelete.h`, `utils.c`, `utils.h`, and `list.h`.

## Option Parsing

`parse_options()` accepts both short and long options. It enforces a single mode among scan, undelete, and copy. If no mode is selected, scan is default.

Important parsing behavior:

- `--inodes` is parsed by `parse_inode_arg()` into inclusive ranges.
- `--match` is transformed from shell-style wildcards into anchored regex when regex support exists.
- `--time` converts values such as days/weeks/months/years ago into an absolute `time_t`.
- scan rejects output/destination/truncate/fill-byte options.
- copy rejects recovery and scan filters.
- quiet cannot be combined with verbose or scan.
- `--parent` requires verbose mode.

The global `ranges`, `nr_entries`, `with_regex`, and `avoid_duplicate_printing` variables coordinate undelete selection.

## MFT Record Reading

`read_record()` reads a single MFT record from `$MFT/$DATA` using MST-aware reads, builds a `struct ufile`, and gathers:

- standard-information last data change time
- attribute-list presence
- directory status from `$INDEX_ROOT`
- filename attributes through `get_filenames()`
- data streams through `get_data()`

It temporarily disables perror logging while inspecting suspicious deleted records.

`get_filenames()` walks `$FILE_NAME` attributes, converts names to the current locale, tracks parent references when requested, picks a preferred name by lowest namespace value, and updates the maximum seen size. If no filename exists, `rescue_name()` tries to recover a stale name from unused MFT-record space for simple unfragmented cases.

`get_parent_name()` reads the parent MFT record and `verify_parent()` checks it is plausibly the parent directory before using its filename.

`get_data()` walks `$DATA` attributes, records stream names, residency, compression/encryption flags, sizes, resident data pointers, and decompressed runlists.

## Recoverability Calculation

`calc_percentage()` estimates recovery by walking each data stream:

- directories return 0%
- resident data returns 100%
- encrypted and compressed streams are treated as unrecoverable
- unmapped runlist segments count as in-use/unrecoverable
- sparse holes count as recoverable zeroes
- normal LCN runs are checked cluster-by-cluster with `utils_cluster_in_use()`

The best percentage across data streams is returned and stored per stream for display and truncation decisions.

This is only a potential-recovery estimate; the implementation cannot prove that free clusters still contain the old data.

## Scan Mode

`scan_disk()` opens `$MFT/$BITMAP`, iterates bits for records not in use, reads each deleted record, applies filters, calculates recoverability, and prints either one-line summaries or verbose dumps.

Filters include:

- modification time after `opts.since`
- filename regex/pattern match
- size range
- minimum recoverability percentage

If scan is being used as undelete-by-regex, matching records are passed to `undelete_file()` after display, with duplicate printing suppressed.

## Undelete Mode

`handle_undelete()` requires either inode ranges or a match regex. With regex it scans and recovers matches; with inode ranges it loops over every inode in every range and calls `undelete_file()`.

`undelete_file()`:

1. Reads the MFT record.
2. Optionally displays file info.
3. Rejects records still in use unless forced.
4. Calculates recoverability and skips records with 0%.
5. For each data stream, creates a host output pathname from destination, chosen filename, and optional stream name.
6. Writes resident data directly.
7. For nonresident data, walks runlists:
   - unmapped segments are filled with `opts.fillbyte`
   - sparse holes are written as zeroes
   - in-use clusters are filled unless `--optimistic` is set
   - free/optimistic clusters are read from the NTFS volume with `ntfs_cluster_read()`
8. Applies `--truncate` only for fully recoverable, internally consistent nonresident streams.
9. Sets the host output file timestamp to the recovered last-data-change time.

Named NTFS streams are written as `filename:stream`.

## Copy Mode

`copy_mft()` writes a requested MFT record range into a host file. It clamps the end of the range to the volume’s initialized MFT record count, reads `$MFT/$DATA`, and writes fixed-size records to `opts.output` or default `mft`.

## Output and Diagnostics

`list_record()` produces the compact scan table. `dump_record()` prints detailed file, filename, date, flag, stream, runlist, and recoverability data. Logging is routed through ntfs-3g logging APIs, with quiet/verbose settings parsed into `opts`.

## Main Flow

`main()` initializes logging, parses options, sets locale, mounts the volume read-only with optional `NTFS_MNT_RECOVER` under `--force`, dispatches the selected mode, unmounts, frees match regex text, and returns the mode result.

## Notable Risks and Limitations

- The NTFS volume is mounted read-only; recovered data is written only to host files.
- Multi-record attribute-list cases are flagged, but data from missing/extended records is not reconstructed.
- Compressed and encrypted streams are not recovered.
- Recovery trusts deleted MFT metadata that may be stale, inconsistent, or reused.
- Output path buffers are fixed-size 256-byte arrays in recovery/copy paths, so long destination/name combinations may be truncated by `snprintf()`.
- `write_data()` handles one partial write retry; callers detect short writes as failure.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.h

## File Role

`ntfsundelete.h` defines the shared data structures for `ntfsundelete.c`. It contains no function prototypes beyond included library headers; its main purpose is to model command options and recovered MFT-record contents.

## Includes

The header includes:

- `types.h` for NTFS/basic types
- `list.h` for intrusive linked-list heads
- `runlist.h` for `runlist_element`
- `utils.h` for utility types and declarations used by the implementation

## Command Mode and Options

`enum optmode` defines:

- `MODE_NONE`
- `MODE_SCAN`
- `MODE_UNDELETE`
- `MODE_COPY`
- `MODE_ERROR`

`struct options` stores parsed CLI state:

- device path and mode
- scan filters: percentage, match pattern/case, size range, time cutoff, parent display
- undelete selectors and outputs: inode, destination, output filename, fill byte, truncate, optimistic recovery
- copy range: `mft_begin`, `mft_end`
- verbosity and force flags

## Recovered Metadata Structures

`struct filename` represents one `$FILE_NAME` attribute:

- Unicode and locale-converted names
- allocated/data sizes
- file attribute flags
- created/altered/MFT-changed/accessed times
- namespace type
- parent MFT reference and optional resolved parent name

`struct data` represents one `$DATA` stream:

- stream name in locale and Unicode forms
- resident/compressed/encrypted flags
- allocated/data/initialized/VCN sizes
- decompressed runlist
- recoverability percentage
- resident data pointer when applicable

`struct ufile` represents one candidate deleted MFT record:

- inode number and last modification date
- lists of names and data streams
- preferred filename and parent name
- maximum observed size
- flags for attribute-list and directory records
- raw MFT record buffer

## Integration Notes

The implementation initializes `struct ufile.name` and `struct ufile.data` with `NTFS_INIT_LIST_HEAD`, appends `struct filename` and `struct data` entries while parsing MFT records, and releases all owned memory through `free_file()` in `ntfsundelete.c`.

The structs intentionally preserve multiple redundant NTFS size/date/name sources because deleted records may be partially inconsistent and recovery chooses conservative values such as the maximum observed size.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsundelete.h -->