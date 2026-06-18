# Group Research: group_1168_mtd_utils_sources_local_fs_mtd_utils_ubi_utils_ubimkvol_c_sources_l_36739f2e1074

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubimkvol.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubimkvol.c

## Purpose
Implements the `ubimkvol` command-line utility for creating a UBI volume on an existing UBI device node.

## Main Entry Points
- `parse_opt()` parses volume ID, name, byte size, LEB count, max-available-size mode, alignment, and static/dynamic volume type.
- `param_sanity_check()` enforces that a volume name is present and exactly one size mode is selected.
- `main()` opens libubi, validates that the supplied node is a UBI device node, gathers device geometry, constructs `struct ubi_mkvol_request`, calls `ubi_mkvol()`, and prints the created volume summary.

## Control Flow
The utility requires one UBI device node plus a volume name and size. Size can be supplied directly in bytes/KiB/MiB via `ubiutils_get_bytes()`, by LEB count via `-S`, or as all available space via `-m`. For LEB-count sizing, it computes bytes from the device LEB size adjusted by the requested alignment. After creation, it queries the new volume by device number and assigned volume ID to report ID, LEB count, byte size, LEB size, type, name, and alignment.

## Dependencies
Depends on `libubi` for UBI probing, device info, volume creation, and volume info lookup. Uses local `common.h` diagnostics/version helpers and `ubiutils-common.h` byte parsing/printing helpers.

## Risks and Notes
`args.lebs` is an `int` but is assigned from `simple_strtoull()`, so very large values may truncate before later byte-size computation. Alignment is only checked as positive by this file; invalid geometry combinations are left for lower layers to reject. The max-available-size path uses `dev_info.avail_bytes` directly, while the LEB-count path adjusts usable bytes for alignment.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubimkvol.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubinfo.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubinfo.c

## Purpose
Implements the `ubinfo` utility for printing general UBI subsystem information, per-UBI-device information, and per-volume information.

## Main Entry Points
- `parse_opt()` accepts device number, volume ID, volume name, `--all`, optional node path, help, and version options.
- `translate_dev()` converts a supplied UBI device or volume character node into `args.devn` and possibly `args.vol_id`.
- `get_vol_id_by_name()` resolves a volume name to a volume ID on a given UBI device.
- `print_vol_info()`, `print_dev_info()`, and `print_general_info()` format volume, device, and global UBI information.
- `main()` decides which report to print based on parsed selectors.

## Control Flow
Without arguments, the utility prints global UBI version, device count, control-device major/minor, and present devices. With `-a`, it expands global output into every UBI device and optionally every volume. With `-d`, it prints a selected device; with `-d` plus `-n` or `-N`, it prints a selected volume. If a node path is supplied, the utility probes whether it is a device node or volume node and derives the corresponding numeric selectors.

## Dependencies
Uses `libubi` inventory/probing APIs, `common.h` diagnostics/version helpers, and `ubiutils-common.h` byte formatting.

## Risks and Notes
`-N <volume name>` is resolved with the current `args.devn`; if the caller supplies a volume name without a device selector, the subsequent lookup targets device `-1` and fails through libubi rather than being caught as a front-end validation error. Some calls such as `print_vol_info()` in the direct volume path are not checked before returning through the success label, so an error there may be printed but not propagated as the process exit status.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubinize.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubinize.c

## Purpose
Implements `ubinize`, the UBI image generator. It reads an INI configuration describing UBI volumes and writes a complete UBI image for flash geometry supplied on the command line.

## Main Entry Points
- `parse_opt()` parses output path, PEB size, min I/O size, sub-page size, VID header offset, erase counter, UBI version, image sequence, and verbosity.
- `read_section()` parses one INI section into `struct ubigen_vol_info`, including mode, type, image file, volume ID, size, name, alignment, flags, and derived LEB usage.
- `main()` initializes ubigen geometry, creates the volume table, reads all INI sections, writes each volume image, and finally writes the layout volume.

## Control Flow
The program requires an output file, physical eraseblock size, minimum I/O size, and one INI file. It seeds a default random image sequence, validates flash geometry, initializes `struct ubigen_info`, creates an empty volume table, then loads the INI file with `iniparser`.

Each section must have `mode=ubi`; non-UBI sections are skipped. For UBI sections, `read_section()` defaults absent volume type to dynamic, requires an image for static volumes, requires `vol_id` and `vol_name`, derives `vol_size` from the image when omitted, validates image size against volume size, handles `vol_flags=autoresize`, and computes data padding, usable LEB size, and used eraseblocks. `main()` enforces unique volume IDs and names and only one autoresize volume, adds each volume to the volume table, writes image-backed volume data after the first two PEBs, then writes the layout volume at the front.

## Dependencies
Depends on Linux UBI media definitions, `libubigen` for image/layout writing, `libiniparser` for configuration parsing, `libubi` constants, POSIX file/stat APIs, and local `common.h` plus `ubiutils-common.h`.

## Risks and Notes
The VID-header offset validation message says it must be a multiple of the min I/O unit, but the code checks only `% 8`. In `read_section()`, the negative alignment check tests `vi->id < 0` instead of `vi->alignment < 0`, so a negative `vol_alignment` from the INI may pass local validation. If a second autoresize volume is found, the code returns immediately from inside the loop, bypassing normal cleanup of allocated structures, open output, and temporary output removal.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubinize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubirename.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubirename.c

## Purpose
Implements the `ubirename` utility for atomically renaming one or more UBI volumes on a UBI device.

## Main Entry Points
- `get_vol_id()` scans present volumes on a device and resolves a volume name to its volume ID.
- `main()` validates argument pairing, opens libubi, validates the supplied node as a UBI device node, resolves all old names, builds `struct ubi_rnvol_req`, and calls `ubi_rnvols()`.

## Control Flow
The command expects a UBI device node followed by old/new name pairs. It rejects odd argument counts and more than the UBI rename limit. It probes the node to ensure it is not a volume node, reads device info to get the volume ID range, resolves each old name by scanning existing volumes, fills rename entries with volume ID and new name, sets the count, and submits the atomic rename request.

## Dependencies
Depends on `libubi` probing, device info, volume info, and atomic rename APIs. Uses local `common.h` diagnostic helpers.

## Risks and Notes
The limit check compares `argc` to `UBI_MAX_RNVOL + 2`, but each rename consumes two arguments after the node. This appears to cap the command below the documented maximum number of rename entries rather than allowing up to `2 * UBI_MAX_RNVOL` names. New volume names are copied with `strcpy()` into the libubi request entry without a local length check, relying on external structure sizing and lower-level validation.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubirename.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubirmvol.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubirmvol.c

## Purpose
Implements the `ubirmvol` utility for removing a UBI volume by volume ID or volume name from a UBI device.

## Main Entry Points
- `parse_opt()` parses `--vol_id`, `--name`, help, version, and the required UBI device node.
- `param_sanity_check()` requires exactly one of volume ID or volume name.
- `main()` opens libubi, validates the node as a UBI device, resolves a name to a volume ID when needed, and calls `ubi_rmvol()`.

## Control Flow
The utility accepts one UBI device node and either `-n <id>` or `-N <name>`. For name-based removal, it first gets device information and then calls `ubi_get_vol_info1_nm()` to resolve the volume name to an ID on that UBI device. It then removes the volume by ID through libubi.

## Dependencies
Uses `libubi` for node probing, device metadata, name-based volume lookup, and volume removal. Uses `common.h` diagnostics and version printing.

## Risks and Notes
Name length is not locally validated, but lookup is delegated to libubi. Like the other UBI device mutators, this tool rejects volume character nodes and requires the parent UBI device node.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubirmvol.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubirsvol.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubirsvol.c

## Purpose
Implements the `ubirsvol` utility for resizing a UBI volume by ID or name.

## Main Entry Points
- `parse_opt()` parses volume ID, volume name, byte size, LEB-count size, help, version, and UBI device node.
- `param_sanity_check()` requires exactly one volume selector and exactly one size selector.
- `main()` opens libubi, validates the UBI device, resolves the target volume, converts LEB count to bytes when requested, and calls `ubi_rsvol()`.

## Control Flow
The command takes a UBI device node, either `-n` or `-N`, and either `-s` byte size or `-S` LEB count. It probes the node, gets UBI device information, resolves the volume info by name or ID, then resizes by bytes. If the user supplied LEB count, the byte target is `vol_info.leb_size * args.lebs`.

## Dependencies
Uses `libubi` probing, device info, volume info, and resize APIs. Uses `common.h` diagnostics/version helpers and `ubiutils-common.h` byte parsing.

## Risks and Notes
If `ubi_probe_node()` returns a negative error other than the volume-node case, the code reports the error but does not jump to cleanup, so it continues into `ubi_get_dev_info()` on a node already known to have failed probing. `args.lebs` is an `int` loaded from `simple_strtoull()`, so very large LEB counts can truncate. The LEB-to-byte multiplication also uses integer-sized `vol_info.leb_size` before assignment to `long long`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubirsvol.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiupdatevol.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiupdatevol.c

## Purpose
Implements `ubiupdatevol`, the utility for updating or truncating the contents of an existing UBI volume node.

## Main Entry Points
- `parse_opt()` parses truncate mode, explicit input size, input skip offset, help, version, volume node, and image path or stdin marker.
- `truncate_volume()` starts a zero-length UBI update to wipe the volume.
- `ubi_write()` writes a buffer fully to the volume, retrying interrupted writes.
- `update_volume()` validates input size against reserved volume bytes, opens the volume and input, starts a UBI update, and streams data in LEB-sized chunks.
- `main()` validates the node as a UBI volume node, fetches volume info, and dispatches truncate or update mode.

## Control Flow
The command expects a UBI volume node. In truncate mode, it opens the node read/write and calls `ubi_update_start()` with size zero. In update mode, it derives the input byte count from `--size` or from `stat(image) - skip`, checks that the data fits in `vol_info.rsvd_bytes`, opens the volume and input file, optionally seeks past skipped input bytes, starts the update with the final byte count, and copies data until the requested byte count is written.

Stdin input is selected by using `-` as the image path and requires an explicit `--size`; skipping stdin is rejected.

## Dependencies
Uses `libubi` for probing, volume info, and update start. Uses POSIX open/read/write/lseek/stat/close APIs and local `common.h` diagnostics.

## Risks and Notes
`parse_opt()` sets `args.img = argv[optind + 1]` even in truncate mode where the image argument is not required; because the global `args` object is zero-initialized this is usually benign when `optind + 1 == argc`, but it still reads one element past the logical argument list. If `stat()` fails before `err` is set to the function’s return value in `update_volume()`, the error path returns the previous uninitialized/local value rather than a deliberate `-1`. The pointer arithmetic in `ubi_write()` advances a `const void *`, which is a GNU C extension rather than strictly portable C.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiupdatevol.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiutils-common.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiutils-common.c

## Purpose
Provides shared helper routines used by UBI utilities for byte-size parsing, byte-size formatting, text wrapping, and pseudo-random seeding.

## Main Entry Points
- `ubiutils_get_bytes()` parses numeric byte strings with optional `KiB`, `MiB`, or `GiB` suffixes.
- `ubiutils_print_bytes()` prints exact bytes plus an approximate KiB/MiB/GiB representation when useful.
- `ubiutils_print_text()` wraps long text to a requested column width.
- `ubiutils_srand()` seeds libc `rand()` from current time and process ID.

## Internal Mechanics
`get_multiplier()` accepts only binary suffixes and skips spaces or tabs before the suffix. `ubiutils_get_bytes()` uses `strtoull()` with base auto-detection, then multiplies by the suffix multiplier if present. `ubiutils_print_text()` builds each folded line in a fixed 1024-byte buffer and breaks either at whitespace or hard width. `ubiutils_srand()` combines seconds, microseconds, and PID, reduces the seed modulo `RAND_MAX`, and calls `srand()`.

## Dependencies
Uses libc time, string, character classification, process, and standard I/O APIs. Includes local `common.h` for shared utility context and is declared to callers through `ubiutils-common.h`.

## Risks and Notes
`ubiutils_get_bytes()` stores `strtoull()` output in a signed `long long`; out-of-range conversions and values above `LLONG_MAX` are not explicitly checked via `errno`, so very large inputs can wrap or become implementation-dependent before the `bytes < 0` check. Suffix multiplication can overflow `long long`. `ubiutils_print_text()` assumes `width > 0`; zero or negative widths would produce invalid indexing behavior.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiutils-common.c -->