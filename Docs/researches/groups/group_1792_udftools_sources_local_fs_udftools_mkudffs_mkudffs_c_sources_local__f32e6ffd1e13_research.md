# Group Research: group_1792_udftools_sources_local_fs_udftools_mkudffs_mkudffs_c_sources_local__f32e6ffd1e13

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/udftools`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/mkudffs.c -->
# File Research: sources/local-fs/udftools/mkudffs/mkudffs.c

## Role

Core UDF image construction support for `mkudffs`. This file owns initialization of `struct udf_disc`, UDF revision policy, physical-space partitioning, and construction of the major on-disk descriptor structures written by the formatter.

## Main Responsibilities

- Initializes a new UDF disc model with default descriptors, timestamps, UUID-like Volume Set Identifier prefix, descriptor lists, and default UDF revision 2.01.
- Applies UDF revision changes across domain identifiers, implementation identifiers, file entry policy, and default descriptor templates.
- Splits media into typed extents: boot/MBR area, VRS, anchors, main/reserve VDS, LVID, sparing table, sparing space, partition space, unallocated/reserved space.
- Creates descriptor payloads for MBR, Volume Recognition Sequence, anchors, partition space, file set, root directory, VDS descriptors, LVID, sparing tables, and VAT.
- Adds logical volume partition maps for type 1, type 2 sparable, and type 2 virtual partitions.
- Provides `dump_space()` and `write_disc()` traversal helpers over the extent list.

## Important Functions

- `udf_init_disc()` zeroes the disc, sets defaults, allocates default UDF descriptors, initializes descriptor string lengths, creates the initial `USPACE` extent, and calls `udf_set_version(0x0201)`.
- `udf_set_version()` accepts only UDF 1.01, 1.02, 1.50, 2.00, 2.01, 2.50, and 2.60. It toggles EFE support for UDF >= 2.00, sets NSR02/NSR03 partition content identifiers, and updates revision fields in active/default descriptor templates.
- `split_space()` is the formatter layout engine. It validates start/last blocks, reserves boot/VRS/anchor locations, calculates size requirements, lays out VDS/LVID/sparing/partition extents with alignment rules, updates LVID free/size tables, and removes temporary pre-start reservations.
- `setup_vrs()`, `setup_anchor()`, `setup_vds()`, and the `setup_*` descriptor helpers materialize logical extents into descriptor objects with correct tags and duplicate reserve descriptors when applicable.
- `setup_space()` creates unallocated/freed space bitmap or table entries inside partition space and updates partition header descriptor pointers.
- `setup_fileset()` and `setup_root()` allocate the FSD and root directory, optionally creating stream directory and non-allocatable-space metadata entries.
- `setup_vat()` builds either UDF 1.50 VAT with LV extension EA or UDF 2.00+ VAT header plus table, and records `disc->vat_block`.
- `add_type1_partition()`, `add_type2_sparable_partition()`, and `add_type2_virtual_partition()` append partition maps and resize LVID partition accounting arrays.

## Data Flow

`mkudffs/main.c` and `options.c` configure a `struct udf_disc`; this file turns that model into a linked list of typed extents with descriptor/data chains. `write_disc()` later delegates each extent to the configured write callback.

## Dependencies

- Local headers: `mkudffs.h`, `file.h`, `defaults.h`.
- Shared UDF helpers from `libudffs.h`: extent/list management, allocation helpers, endian conversion, string/CRC helpers through included headers.
- Linux geometry ioctl `HDIO_GETGEO` is used only for CHS fields when emitting an MBR.

## Notable Behaviors

- VAT media avoids the final anchor and has special closed-disc anchor/VAT alignment rules.
- Non-VAT media writes the final anchor at end-of-volume/session and may place a second anchor at end minus 256.
- Space bitmap partitions are rounded so the last bitmap byte is not partial, due to Windows `chkdsk` compatibility concerns.
- UDF 2.50+ is only partially supported in the wider tool; this file has VAT 2.00+ support but no metadata partition creation path for non-VAT media.
- Allocation failures and impossible layouts are fatal via `fprintf` plus `exit(1)`.

## Research Notes

This file is the main place to study if changing formatter layout, descriptor tagging, VAT emission, sparing support, or media alignment. It assumes the shared extent helpers keep the extent list sorted and split correctly.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/mkudffs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/mkudffs.h -->
# File Research: sources/local-fs/udftools/mkudffs/mkudffs.h

## Role

Public internal interface for `mkudffs` support functions and media type constants.

## Contents

- Includes `ecma_167.h`, `osta_udf.h`, and `libudffs.h`.
- Defines UDF implementation strings:
  - `UDF_ID_APPLICATION`
  - `UDF_ID_DEVELOPER`
- Defines default media profile indexes used by `defaults.c`.
- Declares `enum media_type` for HD, optical, write-once, rewritable, MO, WORM, and BD-R categories.
- Exports `udf_space_type_str`.
- Declares formatter functions implemented primarily in `mkudffs.c`, plus `calc_space()` which is declared here but not implemented in this file.

## Dependencies

Consumers need the UDF structure definitions from the included UDF headers and `struct udf_disc` from `libudffs.h`.

## Research Notes

This header is the central contract between `mkudffs/options.c`, `mkudffs/main.c`, and the descriptor-building implementation.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/mkudffs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/options.c -->
# File Research: sources/local-fs/udftools/mkudffs/options.c

## Role

Command-line option parser and media-policy configurator for `mkudffs`.

## Main Responsibilities

- Defines long options and usage text for formatting controls.
- Parses block size, UDF revision, labels/identifiers, ownership strings, UID/GID/mode, boot area policy, allocation strategy, sparing/VAT controls, media type, space accounting, allocation descriptor type, charset, and start/min-block controls.
- Mutates `struct udf_disc` and global default descriptor templates while parsing.
- Auto-detects optical media profile when `--media-type` is omitted.
- Applies media-derived defaults for partition access type, VAT/sparing use, strategy 4096, minimum CD-R track size, and BD-R revision.
- Validates incompatible option combinations before returning final media type.

## Important Functions

- `usage()` prints complete CLI help and exits.
- `parse_args()` performs all parsing, validation, media detection, partition-map setup, and sizing default selection.

## Notable Parsing Details

- `--blocksize` must be a power of two from 512 through 32768 and updates the LVD logical block size.
- `--udfrev` accepts dotted hex-like revisions such as `2.01` or raw hex input; unsupported revisions fail.
- Charset options `--locale`, `--u8`, `--u16`, and `--utf8` must be first argument because string options are encoded as they are parsed.
- `--label` is a synonym for both LVID and VID; if VID is too short for a long label, it stores a truncated version unless the user explicitly used `--vid`.
- `--uuid` must be exactly 16 lowercase hex characters.
- `--vsid` preserves or converts the UUID prefix portion of the Volume Set Identifier depending on 8-bit or 16-bit OSTA dstring form.
- `--media-type` must be supplied before `--udfrev` because media can set the default UDF revision.
- `--spartable` and `--vat` are mutually exclusive.
- `--minblocks` and `--closed` are valid only with VAT/write-once media.
- UDF >= 2.50 is rejected for non-VAT disks because metadata partition creation is not implemented.

## Media Policy

- HD and DVD-RAM map to overwritable access.
- DVD/CD read-only profiles map to read-only access.
- DVD-R, CD-R, and BD-R enable VAT and write-once access.
- DVD-RW and CD-RW enable sparable partitions.
- WORM and MO default to strategy 4096 and blank terminal behavior.
- BD-R defaults to UDF 2.50 if the revision was not explicitly supplied.

## Dependencies

- `mkudffs.h` for media constants and partition map helpers.
- `defaults.h` for default descriptor templates and sizing profiles.
- Linux CD-ROM ioctls for media autodetection.

## Research Notes

This file is policy-heavy. Formatter behavior often depends on parse order: charset options must come before strings, sparing options must precede sparing-space options, and media type must precede explicit revision.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/options.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/options.h -->
# File Research: sources/local-fs/udftools/mkudffs/options.h

## Role

Option token definitions and parser declarations for `mkudffs`.

## Contents

- Declares `usage()` and `parse_args()`.
- Defines numeric option IDs split by range:
  - `0x1000` range for no-argument long switches.
  - `0x2000` range for required-argument settings.
- Covers help, charset options, media/VAT/new-file/no-write/read-only switches, and all label/layout/media/accounting options.

## Dependencies

Requires `struct udf_disc` to be visible to callers through included `mkudffs.h` or compatible forward context.

## Research Notes

Keep token values stable relative to `options.c`; parser switch cases depend directly on these constants.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/options.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/pktsetup/Makefile.am -->
# File Research: sources/local-fs/udftools/pktsetup/Makefile.am

## Role

Automake build/install definition for pktcdvd helper tools.

## Contents

- Builds two sbin programs:
  - `pktsetup` from `pktsetup.c`
  - `pktcdvd-check` from `pktcdvd-check.c`
- Adds `pktsetup.rules` to `EXTRA_DIST`.
- If `UDEVDIR` is configured, installs `pktsetup.rules` as `80-pktsetup.rules` under `$(UDEVDIR)/rules.d`.
- Removes the installed udev rule on uninstall.

## Research Notes

This makefile wires both manual pktcdvd setup and the udev automation path.
<!-- END FILE RESEARCH: sources/local-fs/udftools/pktsetup/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/pktsetup/pktcdvd-check.c -->
# File Research: sources/local-fs/udftools/pktsetup/pktcdvd-check.c

## Role

Standalone validator used to determine whether an optical device/media combination can be used with the Linux `pktcdvd` packet-writing driver.

## Main Flow

- Ensures stdin/stdout/stderr are open, replacing closed descriptors with `/dev/null`.
- Parses optional `-q`/`--quiet` plus required device path.
- Opens the target read-only and verifies it is a block device.
- Uses `CDROM_GET_CAPABILITY` to ensure it is an optical device and not an existing pktcdvd device.
- Requires `CDC_GENERIC_PACKET`.
- Sends MMC `INQUIRY` and requires peripheral device type `0x05`.
- Attempts `GET_CONFIGURATION` to get the current MMC profile; falls back to disc/track info for older drives.
- Reads disc information and track/rzone information in two-stage length-aware commands.
- Validates supported media and formatting constraints.

## Compatibility Rules

Accepted profiles are CD-RW, DVD-RAM, DVD-RW restricted overwrite, DVD+RW, or unknown/pre-MMC2 with CD-RW-style checks. It rejects unsupported profile types, non-erasable CD-RW cases, reserved sessions, non-packet/non-overwritable track modes, blank/unformatted CD-RW/DVD-RW, invalid packet sizes, and non Mode 1/2 tracks.

## Dependencies

- Linux `CDROM_SEND_PACKET` and MMC command definitions from `linux/cdrom.h`.
- Endian helpers from `bswap.h`.

## Research Notes

This program’s exit status is designed for udev `PROGRAM=...` use: success means the rule should create/keep pktcdvd mapping; failure means remove or skip mapping.
<!-- END FILE RESEARCH: sources/local-fs/udftools/pktsetup/pktcdvd-check.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/pktsetup/pktsetup.c -->
# File Research: sources/local-fs/udftools/pktsetup/pktsetup.c

## Role

User-space pktcdvd mapping manager. It sets up, tears down, and lists packet-writing block-device associations.

## Main Responsibilities

- Supports legacy pktcdvd ioctls on packet block device paths.
- Supports newer pktcdvd control character device API via `/dev/pktcdvd/control`.
- Creates the pktcdvd control node when needed by locating `/proc/misc` entry and loading `pktcdvd` with `/sbin/modprobe` if absent.
- Creates/removes packet block device nodes under `/dev/pktcdvd`.
- Supports idempotent behavior with `-i`.
- Lists active mappings with `-s`.

## Important Functions

- `init_cdrom()` probes drive and disc status to force TOC read and reject not-ready/no-disc cases.
- `setup_dev()` implements old API using `PACKET_SETUP_DEV` and `PACKET_TEARDOWN_DEV` ioctls.
- `get_misc_minor()` finds the pktcdvd misc minor in `/proc/misc`.
- `create_ctl_dev()` ensures `/dev/pktcdvd/control` exists and matches the pktcdvd misc device.
- `remove_stale_dev_node()` removes stale block nodes if no active mapping owns them.
- `find_pkdev_for_dev()` maps an underlying block dev to an existing pktcdvd dev via status ioctl.
- `setup_dev_chardev()` handles setup/teardown through `PACKET_CTRL_CMD`.
- `show_mappings()` prints active mapping index and major/minor pairs.
- `main()` parses `-d`, `-i`, `-s`, detects old API by slash-containing pkt device argument, and dispatches.

## Dependencies

- Linux CD-ROM and pktcdvd ioctl ABI.
- `/proc/misc`, `/dev/pktcdvd`, `mknod`, and root-like permissions for node management.

## Notable Behaviors

- `-i` suppresses errors for already-existing mappings or missing teardown targets.
- Teardown can accept either pkt device name or `major:minor`.
- If direct teardown by packet dev fails with `ENXIO`, it tries interpreting the supplied major/minor as the backing device and searches the mapping table.
- Stale custom device nodes are removed; default `pktcdvd*` nodes are preserved.

## Research Notes

This is Linux-specific device-management code. Any modernization should preserve both control-device API and legacy API behavior unless old kernel support is intentionally dropped.
<!-- END FILE RESEARCH: sources/local-fs/udftools/pktsetup/pktsetup.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/pktsetup/pktsetup.rules -->
# File Research: sources/local-fs/udftools/pktsetup/pktsetup.rules

## Role

udev automation rules for creating/removing pktcdvd mappings for compatible optical media.

## Behavior

- Applies only to block devices with `ID_CDROM=1`.
- Removes pktcdvd mapping on device removal, missing media, or eject request.
- Allows only media types supported by kernel `pktcdvd.ko`: CD-RW, DVD+RW, DVD-RW, and DVD-RAM.
- Runs `/usr/sbin/pktcdvd-check -q $devnode`; success jumps to add, failure removes mapping.
- Adds mapping with `/usr/sbin/pktsetup -i $major:$minor`.
- Removes mapping with `/usr/sbin/pktsetup -i -d $major:$minor`.

## Research Notes

This rule depends on fixed installed paths under `/usr/sbin` and on `pktcdvd-check` exit status as the compatibility gate.
<!-- END FILE RESEARCH: sources/local-fs/udftools/pktsetup/pktsetup.rules -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udffsck/Makefile.am -->
# File Research: sources/local-fs/udftools/udffsck/Makefile.am

## Role

Automake definition for a placeholder `udffsck` program.

## Contents

- Builds `udffsck` as `noinst_PROGRAMS`, so it is not installed.
- Uses `main.c`.
- Adds `-I$(top_srcdir)/include`.

## Research Notes

This is not a production fsck tool in this tree; it builds only a local stub.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udffsck/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udffsck/main.c -->
# File Research: sources/local-fs/udftools/udffsck/main.c

## Role

Placeholder implementation for `udffsck`.

## Contents

- GPL header.
- `int main()` returns `0`.

## Research Notes

There is no filesystem checking logic here. The makefile marks this program `noinst`, consistent with a stub or unfinished tool.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udffsck/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udfinfo/Makefile.am -->
# File Research: sources/local-fs/udftools/udfinfo/Makefile.am

## Role

Automake definition for the `udfinfo` utility.

## Contents

- Builds `udfinfo` as a bin program.
- Links against `$(top_builddir)/libudffs/libudffs.la`.
- Sources include `main.c`, `readdisc.c`, option/reader headers, and shared UDF headers.
- Adds include path `-I$(top_srcdir)/include`.

## Research Notes

`readdisc.c` is shared with `udflabel`, making `udfinfo` the read-only frontend over the shared parser.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udfinfo/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udfinfo/main.c -->
# File Research: sources/local-fs/udftools/udfinfo/main.c

## Role

Read-only CLI frontend that opens a UDF device/image, invokes the shared reader, and prints normalized filesystem metadata.

## Main Flow

- Sets `appname` and locale.
- Allocates initial `USPACE` extent and initializes `struct udf_disc`.
- Parses block/start/last/VAT/charset options.
- Opens target with `O_RDONLY|O_EXCL`, falling back to non-exclusive read with a warning if busy.
- Determines byte size and logical sector size.
- Calls `read_disc()`.
- Selects primary/reserve LVD/PVD/PD/IUVD descriptors.
- Computes used/free/behind blocks and Windows-style serial number.
- Extracts UUID and remaining VSID from PVD Volume Set Identifier.
- Prints key-value metadata and discovered non-free extents.

## Printed Metadata

Includes filename, label, uuid, lvid, vid, vsid, fsid, fullvsid, owner, organization, contact, appid, impid, Windows serial number, block counts, file/dir counts, UDF revisions, start/last/VAT block, integrity state, access type, write-protect flags, and typed extent locations.

## Important Helpers

- `get_size()` uses `BLKGETSIZE64`, regular file size, or seek-to-end fallback.
- `get_sector_size()` uses `BLKSSZGET` and validates UDF-compatible powers of two.
- `compute_windows_serial_num()` sums FSD bytes into four checksum lanes.
- `compute_behind_blocks()` counts trailing blocks beyond the last non-free extent.
- `print_dstring()` decodes OSTA Unicode dstrings with newline normalization.
- `print_astring()` converts fixed 7-bit ASCII identifiers into dstring form for common printing.
- `dump_space()` prints non-free/non-reserved extents.

## Dependencies

- Shared UDF parser in `readdisc.c`.
- `libudffs` string, endian, extent, and read helpers.
- Linux block-device ioctls.

## Research Notes

This file does not deeply validate descriptors itself; it relies on `read_disc()`. It is a useful reference for how callers consume the populated `struct udf_disc`.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udfinfo/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udfinfo/options.c -->
# File Research: sources/local-fs/udftools/udfinfo/options.c

## Role

Command-line parser for `udfinfo`.

## Supported Options

- `--help` / `-h`
- `--blocksize` / `-b`
- `--startblock`
- `--lastblock`
- `--vatblock`
- `--locale`
- `--u8`
- `--u16`
- `--utf8`

## Behavior

- Validates block size as power of two from 512 through 32768.
- Stores optional start/last/VAT block hints in `struct udf_disc`.
- Updates charset flags used for string decoding.
- Requires exactly one device argument.

## Dependencies

- `libudffs.h` for numeric parsing and flags.
- `options.h` token definitions.

## Research Notes

Unlike mkudffs/udflabel charset parsing, this parser does not enforce charset options being first because it does not encode user-provided identifier strings, only decodes output.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udfinfo/options.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udfinfo/options.h -->
# File Research: sources/local-fs/udftools/udfinfo/options.h

## Role

Parser declaration and option token definitions for `udfinfo`.

## Contents

- Forward-declares `struct udf_disc`.
- Declares `parse_args(int, char *[], struct udf_disc *, char **)`.
- Defines no-argument tokens for help and charset switches.
- Defines required-argument tokens for block size, VAT block, start block, and last block.

## Research Notes

Small, local API header for `udfinfo/options.c`.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udfinfo/options.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udfinfo/readdisc.c -->
# File Research: sources/local-fs/udftools/udfinfo/readdisc.c

## Role

Shared UDF disk reader used by `udfinfo` and `udflabel`. It discovers the UDF layout, parses descriptor sequences, resolves partition mapping variants, and computes space statistics.

## Main Responsibilities

- Detect UDF block size, start block, last block, VRS, and anchor descriptors.
- Read MBR presence, anchors, main/reserve Volume Descriptor Sequences, and Logical Volume Integrity sequences.
- Select best PVD/LVD/PD/IUVD descriptors by sequence/revision rules.
- Parse sparable, virtual/VAT, and metadata partition maps.
- Resolve logical partition blocks to physical positions.
- Read sparing tables, VAT tables, metadata file maps, and File Set Descriptor.
- Set up partition extents and compute total/free blocks.

## Detection Flow

- `detect_udf()` handles explicit block size first, then logical sector size, then probes 512 through 32768.
- It tries normal first anchor, second/third anchors, and fallback anchor at sector 512.
- It uses multisession and `CDROM_LAST_WRITTEN` information when available to infer start/last positions for optical media.
- `read_vrs()` scans the Volume Recognition Sequence for BEA01, NSR02/NSR03, and TEA01, while tolerating known non-UDF descriptors such as BOOT2 and CD001.

## Descriptor Parsing

- `scan_vds()` walks main or reserve VDS extents from the selected anchor, follows nested Volume Descriptor Pointers with a cap, records extents/descriptors, and loads large LVD/USD bodies when needed.
- PVD selection chooses the smallest primary volume descriptor number and then highest volume descriptor sequence number.
- PD parsing supports up to two partition descriptors.
- LVD parsing requires UDF compliant domain identifiers and checks logical block size mismatches.
- `scan_lvis()` follows LVID sequences, stores the last parsed LVID, validates size limits, and follows next-integrity extents.

## Partition Mapping

- `find_partition()` locates type 1 or type 2 maps by identifier, partition number, or partition map index.
- `find_partition_descriptor()` resolves matching partition descriptors.
- `find_block_position()` maps:
  - Type 1 logical blocks directly.
  - Virtual partitions through VAT entries.
  - Sparable partitions through sparing table remaps.
  - Metadata partitions through metadata file or mirror file allocation maps.

## VAT and Metadata Handling

- `read_vat()` locates the VAT file near expected last/VAT block, supports FE and EFE, supports AD in ICB, short AD, and long AD forms, parses UDF 1.50 and UDF 2.00 VAT formats, updates logical volume identifiers/counts/revisions, and marks the LVID as closed once VAT is found.
- `read_metadata_file()` reads metadata file and mirror file allocation descriptors.
- `read_metadata()` locates metadata partition map and reads both metadata file maps.

## Space Accounting

- `setup_pspace()` creates PSPACE extents from partition descriptors, with overlap warnings.
- `setup_total_space_blocks()` sums one or two partition descriptor lengths.
- `count_bitmap_blocks()` counts set bits in free-space bitmaps.
- `count_table_blocks()` sums allocation descriptors in unallocated/freed space entries.
- `count_free_partition_blocks()` prefers LVID free-space table values unless VAT makes them stale, otherwise falls back to partition header bitmap/table descriptors.
- `scan_free_space_blocks()` totals free blocks over first and optional second partitions.

## Error Handling

The reader distinguishes hard failures from recoverable damage. Many malformed structures emit warnings and leave missing fields unset; only detection failure or allocation/read failures in key paths abort the full read.

## Dependencies

- `libudffs.h` for UDF structs, extent helpers, endian helpers, and no-EINTR reads.
- Linux CD-ROM ioctls for multisession and last-written information.

## Research Notes

This is the primary source of truth for existing UDF volume introspection. `udflabel` depends on its extent/descriptor records to locate blocks for in-place descriptor updates.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udfinfo/readdisc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udfinfo/readdisc.h -->
# File Research: sources/local-fs/udftools/udfinfo/readdisc.h

## Role

Public header for the shared UDF reader.

## Contents

- Forward-declares `struct udf_disc`.
- Declares `int read_disc(int, struct udf_disc *)`.

## Research Notes

This header is intentionally minimal so both `udfinfo` and `udflabel` can reuse the same disk-reading implementation.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udfinfo/readdisc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udflabel/Makefile.am -->
# File Research: sources/local-fs/udftools/udflabel/Makefile.am

## Role

Automake definition for `udflabel`.

## Contents

- Builds `udflabel` as an sbin program.
- Links against `libudffs`.
- Sources include local `main.c` and `options.c`, shared `../udfinfo/readdisc.c`, headers, and shared UDF headers.
- Adds include path `-I$(top_srcdir)/include`.

## Research Notes

The shared `readdisc.c` dependency means label updates are based on the same discovery/parser behavior as `udfinfo`.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udflabel/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udflabel/main.c -->
# File Research: sources/local-fs/udftools/udflabel/main.c

## Role

CLI for reading or updating UDF volume identifiers in-place.

## Main Flow

- Initializes locale, `struct udf_disc`, sentinel values for optional new identifiers, and parses arguments.
- Opens the target read-only when only displaying label, or read-write exclusive when updating.
- Determines size/sector size and calls shared `read_disc()`.
- If no update is requested, decodes and prints the Logical Volume Identifier.
- For updates, validates logical volume integrity, supported write revision, partition access type, descriptor health, write-protect flags, and unsupported VAT/pseudo-overwrite cases.
- Applies requested identifier changes to in-memory descriptors.
- Recomputes descriptor CRC/checksum.
- Writes main descriptors first, syncs, writes FSD and reserve descriptors, then final `fsync()` and close.

## Important Helpers

- `get_size()` and `get_sector_size()` mirror `udfinfo`.
- `compute_crc()` and `compute_checksum()` implement descriptor integrity calculations.
- `check_desc()` validates current descriptor checksum and CRC before modifying.
- `update_desc()` updates descriptor CRC and tag checksum after modifications.
- `write_desc()` searches the discovered extent/descriptor list for the exact descriptor buffer and writes it back to the corresponding disk block unless `FLAG_NO_WRITE` is set.

## Update Coverage

Can update:

- Logical Volume Identifier in LVD, IUVD logicalVolIdent, and FSD logicalVolIdent.
- Volume Identifier in PVD.
- File Set Identifier in FSD.
- Owner, organization, and contact in IUVD implementation-use fields.
- Application Identifier and Implementation Identifier in PVD.
- UUID/VSID/full Volume Set Identifier in PVD.

## Safety and Limitations

- Refuses updates if LVID is not closed.
- Refuses UDF write revision above 2.60.
- Requires both main and reserve descriptors to be valid for PVD/LVD/IUVD updates.
- Refuses read-only, unknown, write-once, and pseudo-overwrite cases unless allowed by `--force` where implemented.
- VAT update support is explicitly not implemented for LVID/FSID changes and write-once handling.
- Does not update VAT structures for identifier changes that would require VAT-level changes.
- `--no-write` simulates and prints target blocks without writing.

## Dependencies

- Shared `read_disc()` from `../udfinfo/readdisc.h`.
- `libudffs` for UDF structures, CRC, string encoding/decoding, I/O wrappers, and endian helpers.

## Research Notes

This file is more conservative than `udfinfo`: it requires descriptor integrity checks before writes and uses exclusive open for real updates to avoid editing mounted/busy devices.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udflabel/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udflabel/options.c -->
# File Research: sources/local-fs/udftools/udflabel/options.c

## Role

Command-line parser and identifier encoder for `udflabel`.

## Supported Options

- Block/read hints: `--blocksize`, `--startblock`, `--lastblock`, `--vatblock`.
- Update controls: `--force`, `--no-write`.
- Identifiers: `--uuid`, `--lvid`, `--vid`, `--vsid`, `--fsid`, `--fullvsid`, `--owner`, `--organization`, `--contact`, `--appid`, `--impid`.
- Charset controls: `--locale`, `--u8`, `--u16`, `--utf8`.
- Positional `new-label`, treated as both `--lvid` and `--vid`.

## Important Functions

- `usage()` prints detailed help.
- `process_uuid_arg()` accepts explicit 16-byte lowercase hex UUID or `random`, which generates a time-prefixed random value.
- `process_vid_lvid_arg()` encodes LVID and/or VID, truncating VID from label input when necessary but rejecting explicit oversized `--vid`.
- `parse_args()` validates and encodes all options into caller-provided buffers with sentinel values.

## Validation Rules

- Block size must be a power of two from 512 through 32768.
- UUID must be 16 lowercase hexadecimal bytes unless set to `random`.
- VSID/full VSID must fit UDF dstring size limits.
- Owner/organization/contact use 36-byte dstring buffers.
- App ID and implementation ID are at most 23 bytes, must be 7-bit ASCII, and if nonempty must start with `*`.
- Charset options must be the first argument because identifier options are encoded during parsing.
- Requires exactly a device argument, plus optional new label.

## Research Notes

The parser is stateful: `--uuid`/`--vsid` clear pending full VSID, while `--fullvsid` clears pending UUID/VSID. This ensures `main.c` receives a single effective Volume Set Identifier update mode.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udflabel/options.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/udflabel/options.h -->
# File Research: sources/local-fs/udftools/udflabel/options.h

## Role

Parser declaration and option token definitions for `udflabel`.

## Contents

- Forward-declares `struct udf_disc`.
- Declares the long `parse_args()` signature that fills update buffers and force flag.
- Defines no-argument tokens for help, charset options, force, and no-write.
- Defines required-argument tokens for block/VAT/start/last controls and all identifier fields.

## Research Notes

This header’s large parser signature mirrors `udflabel/main.c`’s update buffer set. Any new label field requires coordinated changes here, `options.c`, and `main.c`.
<!-- END FILE RESEARCH: sources/local-fs/udftools/udflabel/options.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/Makefile.am -->
# File Research: sources/local-fs/udftools/wrudf/Makefile.am

## Role

Automake definition for the legacy `wrudf` tool.

## Contents

- Builds `wrudf` as a bin program.
- Links against `libudffs`.
- Sources include interactive writer modules, CD-R/CD-RW IO modules, descriptor/command modules, `ide-pc.c`, and UDF headers.
- Adds shared include path.
- If `USE_READLINE` is enabled, links `$(READLINE_LIBS)` and defines `USE_READLINE`.

## Research Notes

The source list shows `ide-pc.c` is a low-level MMC command wrapper used by the higher-level `wrudf` CD writing modules.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/wrudf/ide-pc.c -->
# File Research: sources/local-fs/udftools/wrudf/ide-pc.c

## Role

Low-level ATAPI/MMC packet command wrapper for CD/DVD writer operations via Linux `CDROM_SEND_PACKET`.

## Main Responsibilities

- Provides a thin C function wrapper around many MMC commands.
- Maintains global last ioctl return value and request sense data for diagnostic reporting.
- Handles command descriptor block construction and endian conversion.
- Provides mode sense/select helpers for write parameters and capability pages.

## Important Functions

- `fail()` prints an error and exits.
- `get_sense_data()` and `get_sense_string()` expose the last request sense state.
- `initpc()` zeroes `cdrom_generic_command`, attaches global sense data, and sets defaults.
- Media/drive commands:
  - `blank()`
  - `close_track_session()`
  - `format()`
  - `set_cdspeed()`
  - `synchronize_cache()`
  - `test_unit_ready()`
  - `getDriveState()`
  - `mediumRemoval()`
  - `startStopUnit()`
- Query commands:
  - `inquiry()`
  - `read_reccapacity()`
  - `read_buffercapacity()`
  - `read_discinfo()`
  - `read_header()`
  - `read_trackinfo()`
  - optional `get_configuration()` under `MMC2`
- Data commands:
  - `readCD()`
  - `writeCD()`
  - optional `verify()` under `MMC2`
- Mode-page helpers:
  - `mode_sense()`
  - `mode_select()`
  - `get_writeparams()`
  - `set_writeparams()`
  - `get_capabilities()`

## Notable Behaviors

- Uses fixed 2048-byte sector sizing for `readCD()` and `writeCD()`.
- Converts selected returned structure fields from big-endian to CPU order after reads.
- Converts write parameters to big-endian before `mode_select()` and restores them afterward.
- `mode_sense()` first requests only the mode header to determine full allocation length, then allocates and reads the full page.
- `getDriveState()` retries `TEST UNIT READY` after sleeping and maps selected sense codes to operational/tray-open/no-disc states.

## Dependencies

- Linux `linux/cdrom.h` and `CDROM_SEND_PACKET`.
- `ide-pc.h` for MMC structures and constants.
- `bswap.h` for endian conversion.

## Research Notes

This is older, Linux-specific CD writer plumbing. It deliberately models MMC structures rather than relying only on Linux cdrom abstractions, which makes it useful for `wrudf` but tightly coupled to the kernel packet command ABI.
<!-- END FILE RESEARCH: sources/local-fs/udftools/wrudf/ide-pc.c -->