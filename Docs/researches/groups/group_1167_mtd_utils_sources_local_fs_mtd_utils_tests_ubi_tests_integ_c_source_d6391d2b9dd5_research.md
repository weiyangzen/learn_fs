# Group Research: group_1167_mtd_utils_sources_local_fs_mtd_utils_tests_ubi_tests_integ_c_source_d6391d2b9dd5

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/mtd-utils`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/integ.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/integ.c

## Role
Randomized UBI integrity stress test. It loads/reloads the UBI module, creates test volumes, performs random writes/erases/verifications on logical eraseblocks, and verifies data survives a UBI module reload.

## Main Behavior
- Maintains in-memory models for UBI devices, volumes, open volume file descriptors, eraseblocks, and write records.
- Creates one dynamic volume per UBI device when needed, using all available bytes or `--maxebs`.
- Writes deterministic pseudo-random data to page-aligned regions and records seed/offset/size for later verification.
- Verifies unwritten gaps contain `0xFF` and written regions match regenerated data.
- Randomly opens/closes volume fds, writes, erases LEBs via `UBI_IOCEBER`, and periodically reloads the UBI module.
- Removes all created volumes at the end.

## Interfaces And Dependencies
- Uses `libubi_open`, `ubi_get_info`, `ubi_get_dev_info1`, `ubi_mkvol`, `ubi_get_vol_info1`, `ubi_rmvol`.
- Uses volume device nodes directly with `open`, `read`, `write`, `lseek`, `dup`, and `close`.
- Depends on test helpers from `common.h` and `helpers.h`, including `seed_random_generator`.

## Notes
- Device-node creation is explicitly marked FIXME and falls back to a shell `mknod` command.
- `open_volume()` returns `0` despite allocating and linking a `struct volume_fd *`; callers ignore the return value.
- Designed for destructive test environments: it rejects pre-existing volumes and removes volumes it creates.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/integ.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/io_basic.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/io_basic.c

## Role
Basic UBI volume I/O test for dynamic and static volumes.

## Main Behavior
- Creates a volume using all available bytes, checks new contents are `0xFF`, writes an `0xA5` pattern through volume update, verifies it, then removes the volume.
- Repeats the same pattern across many alignment values derived from `ALIGNMENTS(dev_info.leb_size)`.
- Tests both `UBI_DYNAMIC_VOLUME` and `UBI_STATIC_VOLUME`.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_dev_info`.
- Relies on helper macros/functions: `initial_check`, `check_vol_patt`, `update_vol_patt`, `failed`.
- Builds volume node names from `UBI_VOLUME_PATTERN`.

## Notes
- Alignment is rounded down to a multiple of `dev_info.min_io_size`, with zero corrected to `min_io_size`.
- The test assumes the passed UBI device has enough free eraseblocks and no conflicting volumes.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/io_basic.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/io_paral.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/io_paral.c

## Role
Parallel UBI volume I/O stress test.

## Main Behavior
- Creates `THREADS_NUM + 1` volumes, with the last static and unchanged to keep wear-leveling pressure.
- Initializes each volume with a full-volume randomized update.
- Starts half the threads doing direct LEB unmap/write/read verification.
- Starts the other half doing randomized volume updates and occasional remove/recreate cycles.
- Cleans up all created volumes and buffers.

## Interfaces And Dependencies
- Uses pthreads, `ubi_mkvol`, `ubi_rmvol`, `ubi_update_start`, `ubi_set_property`, `ubi_leb_unmap`.
- Uses `pread`/`pwrite` for direct eraseblock-size I/O.
- Relies on `initial_check`, `seed_random_generator`, and error helpers.

## Notes
- Uses global `rand()` from multiple threads without synchronization, so randomness is intentionally coarse rather than deterministic per thread.
- Thread functions return `NULL` on failure; `main()` does not collect per-thread success state, so some failures only appear in logs.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/io_paral.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/io_read.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/io_read.c

## Role
Read-boundary and static-volume read semantics test for UBI volumes.

## Main Behavior
- Verifies a newly created static volume has `data_bytes == 0` and reads as EOF before update.
- Writes 10 bytes to a static volume and checks reads return exactly the data length.
- Creates dynamic/static volumes with many alignments, fills them with byte patterns, then tests reads across many offsets and lengths.
- Confirms resulting file offset after each read matches bytes actually read.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_update_start`, `ubi_get_vol_info`, `ubi_get_dev_info`.
- Uses `lseek`, `read`, `write`, and direct volume device nodes.
- Uses `ALIGNMENTS`, `PAGE_SIZE`, `MIN_AVAIL_EBS`, and test error helpers.

## Notes
- `PROGRAM_NAME` is set to `"io_basic"` even though the file is `io_read.c`, so diagnostic labels may be misleading.
- Uses stack VLAs sized by test length and volume size.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/io_read.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/io_update.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/io_update.c

## Role
Tests UBI volume update and atomic LEB change operations.

## Main Behavior
- Defines varied write chunk sequences around min I/O size, page size, and LEB size boundaries.
- For each alignment and volume type, creates a volume and runs full-volume update tests.
- For dynamic volumes, additionally runs atomic LEB change tests on LEB 0.
- Writes chunks containing mixed random data and `0xFF` tails, then reads back and compares the exact data.

## Interfaces And Dependencies
- Uses `ubi_update_start`, `ubi_leb_change_start`, `ubi_mkvol`, `ubi_rmvol`, `ubi_get_vol_info`.
- Includes both `libubi.h` and kernel `mtd/ubi-user.h`.
- Uses randomized data via `seed_random_generator`.

## Notes
- Deliberately passes the original sequence length to `write()` even when the final chunk is truncated; expects UBI to accept only the remaining announced update bytes.
- Static volumes are read with a request larger than data size to confirm static-volume EOF behavior.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/io_update.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_bad.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_bad.c

## Role
Negative tests for UBI volume creation/removal ioctl validation.

## Main Behavior
- Confirms invalid volume IDs, alignments, sizes, volume types, and overlong names fail with expected errno values.
- Tests duplicate volume ID and duplicate volume name rejection.
- Tests failure when no free space remains.
- Creates up to the maximum volume count and tolerates `ENFILE` due to gluebi/MTD restrictions.
- Tests invalid removal IDs, removal of non-existing volumes, and double removal.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_dev_info`.
- Uses helper `check_failed` to assert both failure and expected `errno`.

## Notes
- Cleanup loops attempt removal across possible volume IDs regardless of whether all were created.
- The “maximum size then create more” check expects `EEXIST` because it reuses the same name, even though the message describes space exhaustion.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_bad.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_basic.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_basic.c

## Role
Positive tests for basic UBI volume creation, deletion, alignment, and maximum-volume count behavior.

## Main Behavior
- Creates and removes maximum-size dynamic and static volumes.
- Verifies removed volumes no longer appear via `ubi_get_vol_info1`.
- Creates full-size dynamic volumes across many alignment values and validates computed volume properties.
- Creates many one-byte static volumes up to `max_vol_count` or until `ENFILE`.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_vol_info1`, `ubi_get_dev_info`.
- Uses `check_volume` helper to validate volume metadata against request parameters.

## Notes
- Alignment reduces usable LEB size, and the test computes requested bytes from aligned eraseblock size.
- Destructive test: assumes the target UBI device can be filled and emptied.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_basic.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_paral.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_paral.c

## Role
Parallel create/delete stress test for UBI volumes.

## Main Behavior
- Starts four pthreads.
- Each thread repeatedly creates an automatically numbered dynamic volume, then immediately removes it.
- Uses small volume size `dev_info.avail_bytes / ITERATIONS`.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_dev_info`.
- Uses pthreads and shared `libubi` descriptor.

## Notes
- Threads do not report a failure flag to `main()`; failures are logged but final exit can still be success after thread join.
- Exercises kernel/libubi synchronization around volume ID allocation and removal.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_paral.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/rsvol.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/rsvol.c

## Role
UBI volume resize test for dynamic and static volumes.

## Main Behavior
- Creates volumes, shrinks/grows them, and validates metadata with `check_volume`.
- Tests resize to exact LEB size, larger size, and one byte below a LEB multiple.
- For aligned volumes, shrinks by one LEB, writes data, resizes to data bytes, grows to available LEBs, then verifies data preservation.
- Runs across many alignment values and both volume types.

## Interfaces And Dependencies
- Uses `ubi_rsvol`, `ubi_mkvol`, `ubi_rmvol`, `ubi_get_vol_info`, `ubi_get_vol_info1`, `ubi_update_start`.
- Uses direct volume node I/O for data write/read.

## Notes
- Uses VLAs sized by `vol_info->rsvd_bytes`.
- The file comment has a typo, “Tes UBI volume re-size.”
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/rsvol.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/runtests.sh -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/runtests.sh

## Role
Simple runner for the compiled UBI test suite.

## Main Behavior
- Requires one argument: a UBI device node.
- Verifies the argument is a character device.
- Runs `mkvol_basic mkvol_bad mkvol_paral rsvol io_basic io_read io_update io_paral volrefcnt` in order.
- Stops on first failure and prints `FAILURE`; prints `SUCCESS` if all pass.

## Interfaces And Dependencies
- Expects test binaries in the current directory.
- Uses POSIX shell with `set -euf`.

## Notes
- The script does not include `integ`; that is a separate integrity stress test.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/runtests.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/stress-test.sh -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/stress-test.sh

## Role
High-level UBI test stress orchestrator over simulated MTD geometries.

## Main Behavior
- Sets `PATH` so test scripts and mtd-utils tools are found.
- Cleans up `ubi`, `nandsim`, and `mtdram` modules on exit/signals.
- Runs `runtests.sh /dev/ubi0` across `mtdram` and `nandsim`, fastmap enabled/disabled, VID header offset factor 0/1, and many flash/PEB/page sizes.
- Loads simulated devices, attaches UBI with `modprobe ubi mtd=...`, runs tests, then unloads modules.

## Interfaces And Dependencies
- Uses `/proc/mtd`, `modprobe`, `rmmod`, `modinfo`, `load_nandsim.sh`, and `runtests.sh`.
- Requires kernel modules `nandsim`, `mtdram`, and `ubi`.

## Notes
- `runtests.sh` failures are ignored with `||:` inside `run_test`, so the full sweep continues even after a failed test run.
- Uses `sudo rmmod` in cleanup inside `run_test`, while earlier module operations are unqualified.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/stress-test.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/volrefcnt.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/volrefcnt.c

## Role
Regression test for UBI volume sysfs reference counting during volume deletion.

## Main Behavior
- Creates a small dynamic volume.
- Opens `/sys/class/ubi/ubiX_Y/usable_eb_size`.
- Removes the volume while the sysfs file remains open.
- Confirms reading from the stale fd fails.
- Closes the fd and confirms the sysfs file cannot be opened again.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_dev_info`.
- Uses direct sysfs path format `SYSFS_FILE`.

## Notes
- `PROGRAM_NAME` is `"rmvol"`, not `volrefcnt`.
- Tests kernel lifetime/reference cleanup, not volume I/O.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/volrefcnt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/dictionary.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/dictionary.c

## Role
Vendored iniparser dictionary implementation for string key/value storage.

## Main Behavior
- Provides hash computation, allocation, deletion, lookup, set, unset, and dump operations.
- Stores keys, values, and hash values in parallel arrays.
- Doubles storage when full.
- Duplicates key/value strings into owned memory.

## Interfaces And Dependencies
- Implements declarations from `include/dictionary.h`.
- Used by `libiniparser.c`.

## Notes
- `mem_double()` can lose original pointers if one of several reallocations fails after assignment.
- API uses non-const `char *` parameters for keys/values, reflecting old upstream style.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/dictionary.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/dictionary.h -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/include/dictionary.h

## Role
Public header for the vendored dictionary module.

## Main Contents
- Defines `dictionary` with `n`, `size`, `val`, `key`, and `hash` arrays.
- Declares `dictionary_hash`, `dictionary_new`, `dictionary_del`, `dictionary_get`, `dictionary_set`, `dictionary_unset`, and `dictionary_dump`.

## Interfaces And Dependencies
- Includes standard C headers.
- Consumed by `libiniparser.h` and `dictionary.c`.

## Notes
- Documentation explains keys are unique strings and hash comparison is followed by string comparison.
- Uses legacy spelling and formatting from upstream iniparser.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/dictionary.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/libiniparser.h -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/include/libiniparser.h

## Role
Public API for the vendored INI parser.

## Main Contents
- Declares section enumeration, dumping, typed getters, setters/unsetters, entry existence check, load, and free functions.
- Exposes compatibility macros `iniparser_getstr` and `iniparser_setstr`.
- Keys are represented as `section:key`.

## Interfaces And Dependencies
- Includes `dictionary.h`.
- Implemented by `libiniparser.c`.

## Notes
- Header declares `iniparser_setstring`, while implementation defines `iniparser_set`; this mismatch is notable in this snapshot.
- Documents parser behavior including integer parsing through `strtol` and boolean first-character matching.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/libiniparser.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/libscan.h -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/include/libscan.h

## Role
Public API for scanning MTD eraseblocks for UBI erase-counter state.

## Main Contents
- Defines special erase-counter/status constants: `NO_EC`, `CORRUPT_EC`, `EB_EMPTY`, `EB_CORRUPTED`, `EB_ALIEN`, `EB_BAD`, and `EC_MAX`.
- Defines `struct ubi_scan_info` with per-eraseblock EC/status array and summary counters.
- Declares `ubi_scan` and `ubi_scan_free`.

## Interfaces And Dependencies
- Depends on `stdint.h`, UBI media constants, and forward-declared `struct mtd_dev_info`.
- Implemented by `libscan.c`.

## Notes
- `vid_hdr_offs` and `data_offs` are set to `-1` when undefined.
- Used heavily by `ubiformat.c`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/libscan.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/libubi.h -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/include/libubi.h

## Role
Primary public libubi API for UBI control, device/volume metadata, volume lifecycle, and volume I/O ioctls.

## Main Contents
- Defines `libubi_t`, `ubi_attach_request`, `ubi_mkvol_request`, `ubi_info`, `ubi_dev_info`, and `ubi_vol_info`.
- Declares library open/close and information lookup APIs.
- Declares attach/detach/remove, mkvol/rmvol/rnvol/rsvol, node probing, block-device creation/removal, update start, atomic LEB change, direct-write property, LEB unmap, and map check functions.

## Interfaces And Dependencies
- Includes `mtd/ubi-user.h` and `mtd/ubi-media.h`.
- Implemented by `libubi.c`.
- Consumed by tests and CLI tools.

## Notes
- Documents compatibility return value `1` from `ubi_attach` when `max_beb_per1024` is ignored by old kernels.
- API is a userspace wrapper over UBI sysfs and ioctls.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/libubi.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/libubigen.h -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/include/libubigen.h

## Role
Public API for generating UBI image structures and writing UBI image volumes.

## Main Contents
- Defines `ubigen_info` for geometry, offsets, version, volume table size, and image sequence.
- Defines `ubigen_vol_info` for volume table/header generation.
- Declares initialization, empty volume table creation, EC/VID header initialization, volume table insertion, data volume writing, and layout volume writing.

## Interfaces And Dependencies
- Includes `stdint.h` and `mtd/ubi-media.h`.
- Implemented by `libubigen.c`.
- Used by `mtdinfo.c` and `ubiformat.c`.

## Notes
- Encapsulates UBI on-flash format calculations such as VID header offset, data offset, LEB size, and volume table size.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/libubigen.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/ubiutils-common.h -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/include/ubiutils-common.h

## Role
Small shared utility header for UBI user tools.

## Main Contents
- Declares byte-string parsing, byte printing, wrapped text printing, and random seeding helpers:
  - `ubiutils_get_bytes`
  - `ubiutils_print_bytes`
  - `ubiutils_print_text`
  - `ubiutils_srand`

## Interfaces And Dependencies
- C/C++ compatible declarations.
- Used by tools such as `mtdinfo`, `ubiattach`, and `ubiformat`.

## Notes
- This header only declares helpers; implementations are outside this file group.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/include/ubiutils-common.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libiniparser.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/libiniparser.c

## Role
Vendored INI parser implementation backed by `dictionary`.

## Main Behavior
- Normalizes keys and sections to lowercase.
- Trims whitespace, parses section headers, key/value lines, quoted values, empty values, and comments.
- Supports line continuation with trailing backslash.
- Provides section enumeration, INI dumping, dictionary dumping, typed getters, entry existence checks, set/unset, load, and free.

## Interfaces And Dependencies
- Includes `ctype.h` and `libiniparser.h`.
- Uses `dictionary_get`, `dictionary_set`, `dictionary_unset`, and `dictionary_del`.

## Notes
- Uses static buffers in `strlwc` and `strstrip`; helper functions are not reentrant.
- Rejects input lines longer than `ASCIILINESZ`.
- Implementation function is named `iniparser_set`, while the header declares `iniparser_setstring`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libiniparser.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libscan.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/libscan.c

## Role
MTD scan library for identifying UBI erase-counter headers and eraseblock status.

## Main Behavior
- Allocates `ubi_scan_info` and one EC/status entry per eraseblock.
- For each eraseblock:
  - checks bad-block status,
  - reads the UBI EC header,
  - classifies empty/non-UBI/corrupted/valid blocks,
  - validates EC header magic, CRC, erase counter limit, VID offset, and data offset consistency.
- Computes mean erase counter over valid EC headers.
- Records good/bad/empty/corrupted/alien counts.

## Interfaces And Dependencies
- Uses `libmtd` functions `mtd_is_bad` and `mtd_read`.
- Uses UBI media structs, endian conversion, and `mtd_crc32`.
- Uses `common.h` logging helpers.

## Notes
- Verbose mode 1 prints progress; verbose mode 2 prints per-block classification.
- Treats inconsistent offsets as corrupted eraseblocks rather than fatal scan errors.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libscan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libubi.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/libubi.c

## Role
libubi implementation: userspace wrapper around UBI sysfs metadata and UBI ioctls.

## Main Behavior
- Builds sysfs path templates for UBI devices and volumes under `/sys/class/ubi`.
- Reads sysfs numeric/string files with validation helpers.
- Converts UBI device/volume character nodes to device and volume numbers by matching major/minor values.
- Opens/closes library descriptors and checks UBI version compatibility.
- Implements attach/detach/remove through UBI control ioctls.
- Implements volume create/remove/rename/resize through UBI device ioctls.
- Implements device and volume info lookup from sysfs.
- Implements volume block create/remove, update start, atomic LEB change, property set, LEB unmap, and mapped check.

## Interfaces And Dependencies
- Implements `include/libubi.h`.
- Uses path constants from `libubi_int.h`.
- Uses `common.h` diagnostics and kernel UBI ioctl structures.

## Notes
- Assumes the old `/sys/class/ubi/ubiX_Y` layout, as documented in `libubi_int.h`.
- `ubi_attach` uses a two-step probe to detect whether the kernel supports `max_beb_per1024`.
- Several parameters are intentionally unused and silenced via assignments like `desc = desc`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libubi.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libubi_int.h -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/libubi_int.h

## Role
Internal libubi sysfs path schema and descriptor definition.

## Main Contents
- Defines UBI sysfs directory names, device file names, volume file names, and format patterns.
- Defines `struct libubi`, which stores allocated full path templates for control, device, and volume sysfs files.

## Interfaces And Dependencies
- Private to `libubi.c`.

## Notes
- Comment explicitly notes older and newer kernel sysfs layouts and states libubi assumes the old layout.
- `struct libubi` owns many heap-allocated path strings freed by `libubi_close`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libubi_int.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libubigen.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/libubigen.c

## Role
Implementation of UBI image-generation primitives.

## Main Behavior
- Computes default VID header offset, data offset, LEB size, max volume count, and volume table size.
- Creates an empty volume table with valid CRCs for every record.
- Adds volume table records with reserved PEB count, alignment, type, data padding, flags, name, and CRC.
- Initializes EC and VID headers with UBI magic, version, erase counter, offsets, sequence, volume metadata, and CRCs.
- Writes regular volume data as full PEB records with EC/VID headers and `0xFF` padding.
- Writes two layout volume copies at selected PEBs.

## Interfaces And Dependencies
- Implements `include/libubigen.h`.
- Uses UBI media definitions, endian conversions, and `mtd_crc32`.
- Uses `common.h` diagnostics.

## Notes
- Static volume VID headers include data size, used EBs, and data CRC.
- Dynamic volume VID headers ignore static-only data parameters.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/libubigen.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/mtdinfo.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/mtdinfo.c

## Role
CLI tool for printing MTD device information and optional UBI layout projections.

## Main Behavior
- Parses `--all`, `--ubi-info`, `--map`, `--help`, and `--version`.
- Opens libmtd and prints general MTD subsystem information.
- Prints per-device metadata: name, type, eraseblock size/count, min I/O size, subpage size, OOB size, region count, major/minor, bad-block support, and writeability.
- Computes default UBI VID/data offsets and LEB size with `ubigen_info_init` when requested.
- Can print erase region maps with locked and bad-block status.

## Interfaces And Dependencies
- Uses `libmtd`, `libubigen`, and `ubiutils-common` formatting helpers.
- Uses MTD ioctls through libmtd helpers.

## Notes
- `--map` requires a concrete MTD node, not `--all`.
- The “Additional erase regions” print uses `mtd.oob_size` instead of `mtd.region_cnt`, which appears suspicious.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/mtdinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiattach.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiattach.c

## Role
CLI tool to attach an MTD device to UBI.

## Main Behavior
- Parses UBI device number, MTD node path, MTD number, VID header offset, maximum expected bad blocks per 1024 PEBs, and control device path.
- Defaults control node to `/dev/ubi_ctrl`.
- Opens libubi, verifies control-device support, builds `ubi_attach_request`, and calls `ubi_attach`.
- Prints summary of the newly created UBI device.

## Interfaces And Dependencies
- Uses `libubi` and `ubiutils-common`.
- Uses `simple_strtoul`, diagnostics, and version helpers from `common.h`.

## Notes
- Supports old-kernel compatibility where `max_beb_per1024` may be ignored and reported as warning.
- Requires either `--mtdn` or `--dev-path`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiattach.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiblock.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiblock.c

## Role
CLI tool to create or remove a block device interface for a UBI volume.

## Main Behavior
- Parses create/remove operation and a UBI volume node.
- Opens libubi and probes the node to ensure it is a volume, not a UBI device.
- Opens the volume and calls either `ubi_vol_block_create` or `ubi_vol_block_remove`.
- Reports missing/unsupported UBI block functionality based on errno.

## Interfaces And Dependencies
- Uses `libubi`, `getopt_long`, and `common.h`.

## Notes
- The `case 'c'` intentionally falls through to `case 'r'` to set `args.node`.
- Long options and short options require an argument for create/remove, matching usage `--create /dev/ubi0_0`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiblock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubicrc32.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubicrc32.c

## Role
CLI tool to calculate UBI-style CRC32 over a file or stdin.

## Main Behavior
- Opens the first positional argument as input, or reads stdin if no file is provided.
- Parses help/version options.
- Reads in 4096-byte chunks and updates CRC using initial value `UBI_CRC32_INIT`.
- Prints the CRC as `0x%08x`.

## Interfaces And Dependencies
- Uses `mtd_crc32` from `crc32.h`.
- Uses UBI media constant `UBI_CRC32_INIT`.

## Notes
- Opens `argv[1]` before option parsing, so option-only invocations like `-h` can be treated as filenames before help parsing.
- Opens files with mode `"r"` rather than binary mode; on Linux this is equivalent.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubicrc32.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubidetach.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubidetach.c

## Role
CLI tool to detach MTD devices from UBI or remove a UBI device by number.

## Main Behavior
- Parses UBI device number, MTD node path, MTD number, and control device path.
- Defaults control node to `/dev/ubi_ctrl`.
- Opens libubi, verifies control-device support, and performs exactly one detach/remove mode:
  - remove by UBI device number,
  - detach by MTD node,
  - detach by MTD number.

## Interfaces And Dependencies
- Uses `ubi_remove_dev`, `ubi_detach`, `ubi_detach_mtd`, and `ubi_get_info`.
- Uses `common.h` parsing and diagnostic helpers.

## Notes
- Rejects ambiguous requests that specify both UBI device and MTD target, or both MTD number and MTD node.
- Error text says “MTD detach/detach feature,” likely intended as attach/detach.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubidetach.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiformat.c -->
# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiformat.c

## Role
Destructive CLI tool to format MTD devices for UBI and optionally flash a UBI image.

## Main Behavior
- Parses geometry overrides, VID offset, no-volume-table mode, flash image/stdin, image size, erase counter override, UBI version, image sequence, yes/quiet/verbose.
- Opens libmtd, validates MTD metadata, writeability, subpage constraints, and VID offset.
- Refuses to format an MTD device currently attached to UBI.
- Scans eraseblocks with `ubi_scan` to preserve/infer erase counters and detect bad/empty/corrupted/non-UBI blocks.
- Prompts before overwriting non-UBI data or questionable erase-counter state unless `--yes`.
- Formats eraseblocks by erasing, writing EC headers, reserving two good PEBs for layout volume, and writing an empty volume table unless disabled.
- When flashing an image, rewrites EC headers with new image sequence and selected erase counter, writes image PEBs, handles write failures by torturing/marking bad blocks, then formats the remaining blocks.

## Interfaces And Dependencies
- Uses `libmtd`, `libubi`, `libscan`, `libubigen`, UBI media headers, CRC helpers, and `ubiutils-common`.
- Calls MTD operations: erase, write, mark bad, torture, and bad-block checks.
- Uses `ubigen_info_init`, `ubigen_init_ec_hdr`, `ubigen_create_empty_vtbl`, and `ubigen_write_layout_vol`.

## Notes
- Consecutive bad-block marking is capped by `MAX_CONSECUTIVE_BAD_BLOCKS`.
- `--image-seq` is documented and parsed in a `case 'Q'`, but `Q` is missing from both `long_options` and the getopt option string in this file.
- `flash_image()` has an unreachable `goto out_close` after a `return sys_errmsg(...)` in the unaligned-image-size branch.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ubi-utils/ubiformat.c -->