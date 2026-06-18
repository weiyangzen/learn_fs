# Group Research: group_1312_ntfs_3g_sources_local_fs_ntfs_3g_ntfsprogs_mkntfs_c_sources_local_f_1dd292e78320

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/ntfs-3g`.

This grouped report covers six NTFS-3G ntfsprogs files: the NTFS formatter implementation, `ntfscat` source/header/manual, the preliminary `ntfsck` checker, and the `ntfsclone` manual.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/mkntfs.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/mkntfs.c

## Role

`mkntfs.c` is the complete NTFS volume creation utility. It formats a target block device or forced regular file as NTFS 3.1, lays out boot sectors and metadata files, builds the initial MFT, root directory, `$Extend` contents, indexes, security descriptors, allocation bitmaps, and optionally a volume object id.

## Main Structures And State

- `struct mkntfs_options opts` stores command-line state: device, label, quick/no-action/force flags, geometry overrides, sector/cluster sizes, MFT zone multiplier, epoch-time mode, and UUID request.
- Global buffers and runlists hold transient format state: `g_buf` for initial MFT records, `g_mft_bitmap`, dynamic bitmap/log write buffer, runlists for `$MFT`, `$MFTMirr`, `$LogFile`, `$Boot`, `$BadClus`, and allocation bookkeeping.
- `struct BITMAP_ALLOCATION` models allocated cluster runs before the on-disk `$Bitmap` is written.
- `struct UPCASEINFO` is the Windows 8-era `$UpCase:$Info` payload containing a CRC64 of the upcase table.

## Control Flow

1. `main()` sets logging and locale, initializes options, parses CLI, then calls `mkntfs_redirect()` when parsing returns "proceed".
2. `mkntfs_parse_options()` handles formatter options, logging options, help/version/license, device and optional sector count. It returns tri-state status: success-done, error, or proceed.
3. `mkntfs_redirect()` owns the formatting pipeline:
   - allocates `ntfs_volume`, sets NTFS 3.1 version, label, cluster size, attrdef, upcase table, and `$UpCase:$Info` CRC;
   - opens and validates the target with `mkntfs_open_partition()`;
   - computes geometry and NTFS sizing in `mkntfs_override_vol_params()`;
   - initializes allocation bitmaps and runlists for `$MFT`, `$MFTMirr`, `$LogFile`, `$Boot`, and `$BadClus`;
   - optionally zero-fills the volume;
   - creates metadata records in `mkntfs_create_root_structures()`;
   - syncs root index, `$Bitmap`, `$MFT`, `$MFTMirr`, and the device.

## Formatting And Metadata Creation

- Device validation refuses non-block devices and whole disks unless `--force` is set; it checks mounted status through `ntfs_check_if_mounted()`.
- Geometry defaults are inferred through libntfs device helpers, with fallback warnings for sector size, partition start, heads, and sectors per track.
- Cluster size defaults to 4096 bytes, grows for very large volumes, must be power-of-two, at least sector size, not over NTFS maximum, and not too large for Windows compression.
- MFT record size defaults to 1024 bytes and index record size to 4096 bytes, raised to sector size if needed.
- `$Bitmap` allocation is first represented in memory through `bitmap_allocate()`, `bitmap_deallocate()`, `bitmap_get_and_set()`, and `bitmap_build()`, then streamed to disk with `WRITE_BITMAP`.
- `$LogFile` contents are synthesized as `0xff` bytes through `WRITE_LOGFILE`.
- `mkntfs_create_root_structures()` builds 27 system records, including `$MFT`, `$MFTMirr`, `$LogFile`, `$Volume`, `$AttrDef`, root directory, `$Bitmap`, `$Boot`, `$BadClus`, `$Secure`, `$UpCase`, `$Extend`, reserved files, `$Quota`, `$ObjId`, and `$Reparse`.
- Boot sector construction fills BPB geometry, MFT locations, record-size encodings, serial number, checksum, and writes a backup boot sector.
- Security descriptors are initialized through helper functions from `security.h`; `$Secure` gets `$SDS`, `$SDH`, and `$SII`.
- `$Quota`, `$ObjId`, and `$Reparse` are built as view-index system files below `$Extend`.

## Attribute And Index Helpers

- The file includes local versions of attribute lookup/find logic tailored for formatting, with attribute-list support mostly unsupported outside simple paths.
- `insert_resident_attr_in_mft_record()`, `insert_non_resident_attr_in_mft_record()`, and `insert_positioned_attr_in_mft_record()` create attributes and write non-resident data via runlists.
- `add_attr_*` wrappers create standard information, file names, object ids, security descriptors, data streams, volume name/info, index root/allocation, and bitmaps.
- Directory and view indexes are built with simplified insertion logic suitable for initial filesystem creation, not a general-purpose mutable NTFS index implementation.
- `upgrade_to_large_index()` converts root `$I30` from resident-only index root into a large index with `$BITMAP` and `$INDEX_ALLOCATION`.

## Important Dependencies

This file relies heavily on libntfs-3g internals: device I/O, endianness wrappers, MFT layout, mapping pairs, MST fixups, NTFS names/collation, boot-sector validation, security descriptor initialization, upcase table generation, and logging.

## Notable Limitations And Risk Areas

- Many comments explicitly mark incomplete functionality: compressed attributes, sparse/encrypted attribute insertion, attribute-list/extent handling, making attributes non-resident, robust index algorithms, bad-block persistence, and full boot/log exactness.
- The formatter has broad global mutable state, so partial failures depend on `mkntfs_cleanup()` for memory/device cleanup and may leave a partially formatted target.
- `opts.no_action` bypasses writes in several helpers, but most structures are still constructed in memory.
- The code intentionally uses simplified index lookup/insertion because it creates a fresh filesystem. Reusing these helpers as general NTFS mutation code would be unsafe.
- The volume is marked dirty if backup boot sector creation fails, relying on Windows chkdsk to recreate it later.

## External Interface

CLI syntax is `mkntfs [options] device [number-of-sectors]`. Major options include quick format, label, compression/indexing defaults, no-action, cluster/sector geometry, partition start, MFT zone multiplier, epoch time, UUID, force, verbosity, version, license, and help.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/mkntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.8.in

## Role

This is the roff manual page template for `ntfscat`, an ntfs-3g utility that prints an NTFS file or stream to standard output.

## Documented Behavior

- Reads from an NTFS volume and writes selected file/stream contents to stdout.
- Filename lookup is documented as case-insensitive.
- A file can be selected by path or by inode number.
- The default output is the unnamed `$DATA` attribute unless another attribute type is requested.

## Options

- `-a, --attribute TYPE`: select an attribute by decimal, hexadecimal, or symbolic name. The manual lists standard NTFS attribute type ids from `$STANDARD_INFORMATION` through `$LOGGED_UTILITY_STREAM`.
- `-n, --attribute-name NAME`: select a named attribute/stream.
- `-i, --inode NUM`: select file by inode instead of pathname.
- `-f, --force`: override safety defaults, such as mounted-volume checks.
- `-h, --help`, `-q, --quiet`, `-V, --version`, `-v, --verbose`: standard utility controls.

## Examples

The examples show reading `/boot.ini`, reading a nested path such as `/winnt/system32/drivers/etc/hosts`, and dumping the root directory `$INDEX_ROOT` by inode 5 through `hexdump`.

## Cross References

The page points users at `libntfs(8)` for encrypted-file access details and references `ntfsls(8)` and `ntfsprogs(8)`.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.c

## Role

`ntfscat.c` implements the `ntfscat` command-line utility. It mounts an NTFS volume read-only, opens a file by path or MFT inode number, opens a selected attribute, and streams its bytes to stdout.

## Control Flow

1. `main()` installs stderr logging and calls `parse_options()`.
2. After successful parsing, it sets locale and mounts the volume read-only with `utils_mount_volume()`. `--force` maps to `NTFS_MNT_RECOVER`.
3. It opens the target inode via `ntfs_inode_open()` for `-i` or `ntfs_pathname_to_inode()` for a pathname. On Windows builds, the pathname is converted through `ntfs_utils_unix_path()`.
4. It chooses `AT_DATA` by default or the parsed `opts.attr`, then calls `cat()`.
5. It closes inode and unmounts the volume.

## Option Parsing

- `parse_attribute()` accepts symbolic NTFS attribute names with or without leading `$`, or numeric ids in decimal/octal/hexadecimal.
- `parse_options()` accepts `-a`, `-n`, `-i`, `-f`, `-h`, `-q`, `-V`, `-v`, and undocumented `-r/--raw`.
- It enforces one device, exactly one file or inode selector, and disallows quiet plus verbose together.
- Attribute names are converted from multibyte strings to NTFS Unicode via `ntfs_mbstoucs()`.

## Data Streaming

- `cat()` allocates a 4096-byte buffer and opens the requested attribute with `ntfs_attr_open()`.
- For normal reads it uses `ntfs_attr_pread()`.
- For fixup-protected records, it uses `ntfs_attr_mst_pread()` unless `--raw` is set:
  - MFT data for inode numbers below 2 uses `vol->mft_record_size`.
  - `$INDEX_ALLOCATION` uses the index block size read from the inode's `$INDEX_ROOT`.
- Output is written with `fwrite()` and failures are logged.

## Important Dependencies

The utility depends on ntfs-3g volume mounting, inode/path lookup, attribute open/read, MST-protected reads, option/logging utilities, and NTFS Unicode conversion.

## Notable Limitations And Risk Areas

- The `--raw` option exists in code but is intentionally not documented because compressed-file raw display does not work as intended.
- `index_get_size()` assumes a resident `$INDEX_ROOT` exists for index-allocation sizing; if absent, it returns zero and `cat()` falls back to plain reads.
- The tool writes arbitrary attribute bytes to stdout, so binary output is expected.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.h

## Role

`ntfscat.h` declares the option state shared by the `ntfscat` implementation.

## Contents

- Includes `types.h` and `layout.h` for NTFS scalar and attribute types.
- Defines `struct options` with:
  - `device`: target device/file path;
  - `file`: pathname to display;
  - `inode`: MFT inode selector;
  - `attr`: selected `ATTR_TYPES` value;
  - `attr_name` and `attr_name_len`: selected named stream/attribute name in NTFS Unicode;
  - `force`, `quiet`, `verbose`: command behavior/logging flags;
  - `raw`: bypass MST-aware decoding for raw data output.

## Consumers

`ntfscat.c` owns a static instance of this structure and fills it during command-line parsing before mounting and streaming the requested attribute.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsck.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsck.c

## Role

`ntfsck.c` is an early/preliminary NTFS consistency checker. It can open an NTFS device read-only, verify basic boot-sector structure, bootstrap enough metadata to load `$MFT` and `$MFT/$BITMAP`, mount the volume read-only, and perform low-level MFT record and attribute sanity checks. Full repair and comprehensive volume checking are explicitly unfinished.

## Return Codes

The file defines fsck-style return bits for corrected errors, reboot needed, uncorrected errors, operational errors, syntax errors, cancellation, and shared-library errors. In practice, `main()` currently returns simple nonzero statuses based on errors or unsupported paths.

## Global State

- `errors` and `unsupported` count findings and unimplemented checks.
- `bytes_per_sector`, `sectors_per_cluster`, and `current_mft_record` track check context.
- `mft_rl` and `mft_bitmap_rl` hold preliminary runlists.
- `mft_bitmap_records` and `mft_bitmap_buf` hold the loaded `$MFT/$BITMAP`.

## Boot And Metadata Bootstrap

- `verify_boot_sector()` reads the first 512 bytes, checks the x86 jump pattern, NTFS OEM magic, bytes-per-sector sanity, and parses the boot sector into a preliminary `ntfs_volume`.
- `load_runlist()` reads a file record from a byte offset, walks attribute records with minimal defensive checks, and returns a decompressed runlist for the requested attribute type.
- `verify_mft_preliminary()` loads `$MFT/$DATA` and `$MFT/$BITMAP` runlists from `$MFT`, falling back to `$MFTMirr`, then loads the MFT bitmap.
- `mft_bitmap_load()` reads the bitmap through `ntfs_rl_pread()`, and `mft_bitmap_get_bit()` tests whether a record is allocated.

## Record Checking

- `check_file_record()` validates `FILE` magic, update sequence array bounds, attribute area bounds, record flags, USA fixups, and then iterates attributes.
- `check_attr_record()` checks attribute overflow, type range, minimum length, first-attribute expectations, flags, resident/non-resident mode, resident value bounds, resident flags, and reserved fields. Many deeper semantic checks are left as TODO comments.
- `verify_mft_record()` skips bitmap-free records, reads allocated records through `$MFT`, and calls `check_file_record()`.
- `check_volume()` is marked unsupported but still iterates initialized MFT records and calls `verify_mft_record()`.

## Main Flow

`main()` accepts exactly one device argument, opens it read-only with default ntfs device I/O, verifies the boot sector, performs preliminary MFT bootstrap, closes the raw device, mounts the volume read-only through `ntfs_device_mount()`, calls unsupported log replay and volume checking stubs, reports counters, possibly resets the dirty flag if nothing was found, unmounts, and returns status.

## Important Limitations And Bugs

- The large command-line TODO block shows intended fsck features, but only the single-device positional form is implemented.
- `replay_log()` and `check_volume()` both mark unsupported, so clean volumes can still produce unsupported status.
- The checker is read-only and does not actually repair structures.
- `verify_mft_preliminary()` ends with a FIXME return value after loading the bitmap, indicating incomplete control-flow design.
- `reset_dirty()` uses `if (!(vol->flags | VOLUME_IS_DIRTY))`, which tests a bitwise OR rather than whether the dirty bit is set; that condition is effectively wrong for normal flag values.
- Several error paths leak buffers or runlists, which is less severe for a short-lived checker but important if reused as a library routine.

## Dependencies

The file uses ntfs-3g device I/O, boot-sector parsing, mapping-pair decompression, runlist reads, bit operations, MFT/attribute layout definitions, mounting, logging, and volume flag writes.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsclone.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsclone.8.in

## Role

This is the roff manual page template for `ntfsclone`, the ntfs-3g sector-level NTFS cloning, imaging, restore, rescue, and metadata-copy utility.

## Documented Behavior

- `ntfsclone` copies only used NTFS data at disk-sector level.
- Unused space is represented differently depending on target mode:
  - sparse holes when cloning to sparse files;
  - control codes in the special image format;
  - unchanged space when cloning to an existing partition/device;
  - zero-filled output when writing to stdout.
- Non-image clones are exact sector-level NTFS filesystem copies and can be mounted like the original.
- The utility is explicitly filesystem-focused and does not solve Windows boot migration issues such as partition start sector and BIOS geometry dependencies.

## Major Modes

- Normal clone to file/stdout/device.
- `--save-image`: write the special ntfsclone image format.
- `--restore-image`: restore from that image format, including stdin via `-`.
- `--metadata`: copy only NTFS metadata while wiping file contents and most resident user data.
- Rescue mode: ignore disk read errors and mark unreadable sectors with a recognizable marker and filler.

## Options

- `-o, --output FILE`: clone to a non-existent file or stdout.
- `-O, --overwrite FILE`: clone to an existing partition/device or file.
- `-s, --save-image`, `-r, --restore-image`, `-n, --no-action`.
- `--rescue`: continue past read errors.
- `-m, --metadata`: metadata-only clone, limited to sparse file unless combined with save-image.
- `--ignore-fs-check`: metadata-only safety override for consistency-check failures.
- `-t, --preserve-timestamps`: preserve timestamps in metadata-only mode.
- `--full-logfile`: include Windows log file, useful for dirty filesystems and metadata extraction.
- `--new-serial`, `--new-half-serial`: randomize full or upper half of NTFS serial for coexistence with the source filesystem.
- `-f, --force`, `-q, --quiet`, `-h, --help`.

## Operational Guidance

The manual explains sparse-file behavior, limitations of common Linux tools with large sparse files, the purpose of the special image format for streaming/compression, and the privacy limits of metadata-only images. It states metadata-only mode wipes file contents, timestamps unless preserved, and unused metadata spaces, but filenames remain visible and may be sensitive.

## Examples

Examples cover cloning between devices, saving/restoring image files, gzip pipelines, remote ssh backup/restore streams, web-stream restore, sparse-file clone creation, and metadata-only image compression/unpacking.

## Cross References

The page references `ntfsresize(8)`, `ntfsprogs(8)`, `xfs_copy(8)`, `debugreiserfs(8)`, and `e2image(8)`.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsclone.8.in -->