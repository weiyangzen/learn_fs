# Group Research: dosfstools FAT mkfs sources subset A

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/dosfstools` is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/mkfs.fat.c -->
# File Research: sources/local-fs/dosfstools/src/mkfs.fat.c

Implements the `mkfs.fat` command: creates FAT12, FAT16, FAT32, and Atari/GEMDOS-style FAT filesystems on block devices or newly-created image files.

Key elements:
- Defines packed on-disk structures for FAT boot sectors, FAT32 extensions, volume info, and FAT32 FSINFO.
- Maintains formatter state in file-static globals: target path, geometry, FAT size, sector size, cluster size, reserved sectors, root directory size, bad-block state, generated boot sector, FAT image, root directory, and write buffers.
- Provides FAT manipulation helpers:
  - `set_FAT_byte`
  - `read_FAT_cluster`
  - `mark_FAT_cluster`
  - `mark_FAT_sector`
- Implements bad-block handling through `check_blocks`, `do_check`, `get_list_blocks`, and `process_bad_blocks`.
- Computes filesystem geometry and defaults in `establish_params`.
- Builds boot sector, FAT, root directory, FSINFO, and optional fake MBR in `setup_tables`.
- Writes reserved sectors, boot sector, FAT copies, FAT32 backup sectors, FSINFO, and root directory in `write_tables`.
- Parses all command-line behavior in `main`.

Important behavior:
- FAT type selection follows FAT cluster-count boundaries:
  - FAT12 max: `4084`
  - FAT16 min/max: `4087` to `65524`
  - FAT32 min/max: `65525` to `268435446`
- FAT32 can be explicitly forced below the suggested minimum, with a warning.
- Large filesystems auto-select FAT32 when the target is at least 512 MiB unless overridden.
- Alignment is enabled by default and aligns reserved areas, FATs, and root directory layout to cluster size where applicable; it is disabled for tiny filesystems at or below 8192 sectors.
- Atari mode changes boot-sector layout assumptions, serial placement, FAT-size defaults, sector-size tuning, and GEMDOS compatibility checks.
- FAT32 root directory is allocated as cluster 2 unless bad-block processing moves it to the next usable cluster.
- Volume labels are converted through `charconv` helpers, padded to 11 bytes, validated against FAT label rules, and mirrored into both boot-sector volume info and root directory label entry when present.
- Reproducibility support exists through `SOURCE_DATE_EPOCH` and `--invariant`, affecting creation time, volume ID, and generated MBR disk signature.
- `--mbr` can embed a fake MBR partition table into boot-code space so whole fixed disks are more recognizable by Windows.

Dependencies:
- Includes `version.h` for `VERSION` and `VERSION_DATE`.
- Includes `common.h` for shared utility functions such as fatal error reporting, Atari detection, mounted-device checks, and volume ID generation.
- Includes `msdos_fs.h` for FAT directory-entry layout and attribute constants.
- Includes `device_info.h` for target type, geometry, size, partition, sector-size, and child-device detection.
- Includes `charconv.h` for DOS codepage setup, label conversion, and label validation.
- Uses `endian_compat.h` for portable little-endian conversions.

Filesystem construction flow:
1. Parse environment and CLI options.
2. Open or create the target.
3. Collect target device information.
4. Apply safety checks against mounted devices and devices with partitions/mappings.
5. Establish CHS/media/root-directory defaults.
6. Compute FAT geometry and allocate in-memory FAT/root/FSINFO tables.
7. Optionally scan or import bad blocks and mark affected clusters.
8. Write all filesystem metadata to the target and `fsync`.

Research notes:
- This is the central formatter implementation for dosfstools, not a reusable library module.
- The code intentionally writes only metadata regions and leaves most data-area sectors untouched.
- Many calculations are in logical sectors but bad-block and block-count paths still use 1024-byte blocks and 512-byte hard sectors, so unit conversion is a major correctness concern.
- Safety checks are conservative by default: mounted targets and fixed disks with child mappings are rejected unless explicitly overridden.
- `malloc_entire_fat` is only enabled when bad-block marking requires random FAT updates; otherwise only the first FAT sector is materialized and the rest is written as blank sectors.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/mkfs.fat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/msdos_fs.h -->
# File Research: sources/local-fs/dosfstools/src/msdos_fs.h

Defines MS-DOS/FAT directory-entry constants and the packed 32-byte on-disk directory-entry structure used by dosfstools formatter/checker code.

Key elements:
- Fixed logical `SECTOR_SIZE` of 512 for directory-entry density constants.
- Directory-entry density helpers:
  - `MSDOS_DPS`
  - `MSDOS_DPS_BITS`
  - `MSDOS_DIR_BITS`
- FAT attribute constants:
  - `ATTR_NONE`
  - `ATTR_RO`
  - `ATTR_HIDDEN`
  - `ATTR_SYS`
  - `ATTR_VOLUME`
  - `ATTR_DIR`
  - `ATTR_ARCH`
- `ATTR_UNUSED` identifies attribute bits copied as-is.
- `DELETED_FLAG` and `IS_FREE` classify free/deleted directory slots.
- 8.3 name constants:
  - `MSDOS_NAME`
  - `MSDOS_DOT`
  - `MSDOS_DOTDOT`
- `struct msdos_dir_entry` maps the FAT short directory entry, including name, attributes, timestamps, high/low start cluster fields, and file size.

Dependencies:
- Includes `<stdint.h>`.
- Uses GCC `__attribute__((packed))` to preserve on-disk layout.

Research notes:
- The structure is shared by code that needs direct FAT directory-entry serialization.
- `SECTOR_SIZE` here is a fixed directory helper constant; `mkfs.fat.c` separately supports user/device logical sector sizes.
- `IS_FREE` treats both a zero first byte and `0xe5` as free/deleted slot markers.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/msdos_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/testdevinfo.c -->
# File Research: sources/local-fs/dosfstools/src/testdevinfo.c

Small diagnostic utility that opens a supplied file/device, calls dosfstools device probing, and prints the discovered metadata in human-readable form.

Key elements:
- Expects exactly one argument: `FILENAME`.
- Opens the target read-only with `O_NONBLOCK`.
- Sets `device_info_verbose = 100` to force verbose probing.
- Calls `get_device_info(fd, &info)`.
- Prints:
  - device type
  - partition status/number
  - whether the device has children
  - geometry heads
  - geometry sectors
  - geometry start
  - total disk sectors
  - sector size
  - byte size

Dependencies:
- Includes `device_info.h`.
- Uses device type constants:
  - `TYPE_UNKNOWN`
  - `TYPE_BAD`
  - `TYPE_FILE`
  - `TYPE_VIRTUAL`
  - `TYPE_REMOVABLE`
  - `TYPE_FIXED`

Research notes:
- This is a debug/test helper for the device discovery layer, not part of the formatter path.
- Unknown values are represented by negative fields in `struct device_info` and printed as `unknown`.
- The program does not fail if `get_device_info` reports unusable or unknown metadata; it prints whatever was collected.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/testdevinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/version.h.in -->
# File Research: sources/local-fs/dosfstools/src/version.h.in

Autoconf template header that supplies package version metadata to dosfstools builds.

Key elements:
- Include guard: `_version_h`.
- Defines `VERSION` from `@PACKAGE_VERSION@`.
- Defines `VERSION_DATE` from `@RELEASE_DATE@`.

Dependencies:
- Generated by the build configuration process before inclusion as `version.h`.
- Used by `mkfs.fat.c` to print the startup banner: `mkfs.fat VERSION (VERSION_DATE)`.

Research notes:
- This file contains no runtime logic.
- Correct substitution is required for build output to expose meaningful version/date strings.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/version.h.in -->