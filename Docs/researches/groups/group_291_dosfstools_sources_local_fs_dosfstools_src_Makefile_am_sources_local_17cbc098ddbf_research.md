# Group Research: group_291_dosfstools_sources_local_fs_dosfstools_src_Makefile_am_sources_local_17cbc098ddbf

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/dosfstools`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/Makefile.am -->
# File Research: sources/local-fs/dosfstools/src/Makefile.am

Automake build definition for dosfstools command-line programs in `src`.

Key points:
- Builds installed programs: `fsck.fat`, `mkfs.fat`, and `fatlabel`.
- Builds non-installed helper: `testdevinfo`.
- Defines shared source groups:
  - `charconv_common_sources`: character conversion helpers.
  - `fscklabel_common_sources`: boot/FAT/I/O/common code shared by `fsck.fat` and `fatlabel`.
  - `devinfo_common_sources`: device probing and block-device helpers used by `mkfs.fat` and `testdevinfo`.
- Links `LIBICONV` into `fsck.fat`, `mkfs.fat`, and `fatlabel`.
- Adds `-I$(srcdir)/blkdev` for `mkfs.fat` and `testdevinfo`.
- Optional `COMPAT_SYMLINKS` install hook creates legacy command names such as `dosfsck`, `mkdosfs`, `fsck.vfat`, and `mkfs.msdos`; uninstall hook removes them.

Dependencies surfaced:
- `fsck.fat` combines checker, file-operation rules, LFN handling, boot parsing, FAT handling, and virtual I/O.
- `fatlabel` reuses the fsck/label core without directory repair.
- `mkfs.fat` uses `device_info` and `blkdev` but not the fsck directory checker.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/blkdev/blkdev.c -->
# File Research: sources/local-fs/dosfstools/src/blkdev/blkdev.c

Portable block-device helper implementation, mostly used by mkfs/device discovery.

Main behavior:
- `is_blkdev()` uses `fstat()` and `S_ISBLK`.
- `blkdev_find_size()` probes readable offsets with exponential search followed by binary search.
- `blkdev_get_size()` tries platform-specific size APIs in order:
  - Darwin `DKIOCGETBLOCKCOUNT`
  - Linux `BLKGETSIZE64`, guarded against known broken 2.4 kernels
  - Linux `BLKGETSIZE`
  - FreeBSD `DIOCGMEDIASIZE`
  - floppy `FDGETPRM`
  - older FreeBSD disklabel `DIOCGDINFO`
  - regular-file `st_size`
  - fallback probing for block devices.
- `blkdev_get_sectors()` returns 512-byte sector count.
- `blkdev_get_sector_size()` uses `BLKSSZGET` or defaults to 512.
- `blkdev_get_physector_size()` uses `BLKPBSZGET` where available or defaults to 512.
- `blkdev_is_misaligned()` checks `BLKALIGNOFF`.
- `blkdev_is_cdrom()` checks `CDROM_GET_CAPABILITY`.
- `blkdev_get_geometry()` uses `HDIO_GETGEO` or floppy geometry.
- `blkdev_get_start()` uses Linux sysfs `/sys/dev/block/<maj>:<min>/start`, falling back to `HDIO_GETGEO`.
- `blkdev_scsi_type_to_name()` maps SCSI peripheral type constants to strings.

Notable implementation details:
- The file is public-domain imported utility code.
- It conditionally supports Linux, Darwin, FreeBSD, Solaris-style headers, and floppy devices.
- `blkdev_get_physector_size()` calls `ioctl(fd, BLKPBSZGET, &sector_size)`, passing an `int **` rather than the `int *` parameter. That looks suspicious and should be reviewed before relying on physical-sector reporting.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/blkdev/blkdev.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/blkdev/blkdev.h -->
# File Research: sources/local-fs/dosfstools/src/blkdev/blkdev.h

Public header for block-device helper functions and fallback ioctl definitions.

Contents:
- Defines `DEFAULT_SECTOR_SIZE` as 512.
- Provides Linux ioctl constants when system headers do not define them:
  - basic block ioctls such as `BLKGETSIZE`, `BLKSSZGET`, `BLKRRPART`
  - `BLKGETSIZE64`
  - topology ioctls such as `BLKIOMIN`, `BLKPBSZGET`
  - discard-zeroes and freeze/thaw constants
  - `CDROM_GET_CAPABILITY`
- Defines Darwin `BLKGETSIZE` alias to `DKIOCGETBLOCKCOUNT32` when applicable.
- Provides fallback `HDIO_GETGEO` and `struct hd_geometry` definition.
- Declares block-device query functions implemented in `blkdev.c`.
- Defines SCSI peripheral type constants and declares `blkdev_scsi_type_to_name()`.

Role in system:
- Supplies a portability layer for `device_info.c` and mkfs-side device probing.
- Keeps platform ioctl compatibility isolated from mkfs/fsck higher-level code.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/blkdev/blkdev.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/blkdev/linux_version.c -->
# File Research: sources/local-fs/dosfstools/src/blkdev/linux_version.c

Small Linux kernel-version parser.

Behavior:
- `get_linux_version()` caches its result in a static `kver`.
- Calls `uname()`, parses `uts.release` as `major.minor.teeny`, and returns `KERNEL_VERSION(major, minor, teeny)`.
- Returns cached `0` on `uname()` or parse failure.

Consumers:
- `blkdev_get_size()` uses this to avoid Linux kernels with broken `BLKGETSIZE64` behavior.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/blkdev/linux_version.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/blkdev/linux_version.h -->
# File Research: sources/local-fs/dosfstools/src/blkdev/linux_version.h

Header for Linux kernel-version compatibility.

Contents:
- Includes `<linux/version.h>` when configured.
- Defines fallback `KERNEL_VERSION(a,b,c)` macro if unavailable.
- Declares `get_linux_version()`.

Role:
- Allows block-device code to compare kernel versions without depending unconditionally on Linux kernel headers.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/blkdev/linux_version.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/boot.c -->
# File Research: sources/local-fs/dosfstools/src/boot.c

Boot-sector, FSINFO, backup-boot, root-entry, label, and serial handling for FAT filesystems.

Major functions:
- `alloc_rootdir_entry()` allocates a free root-directory entry. For FAT32 root directories it can extend the root cluster chain; for FAT12/16 it scans the fixed root directory. It can generate unique `FSCK%04dREC`-style names.
- `read_boot()` reads and validates the boot sector, derives `DOS_FS` layout fields, identifies FAT12/16/32, checks last-sector accessibility, initializes FAT offsets, root offsets, data area, FAT size, serial, and label.
- `check_backup_boot()` validates or creates FAT32 backup boot sectors and can copy original to backup or backup to original.
- `read_fsinfo()` validates or creates FAT32 FSINFO, records `fsinfo_start`, and loads `free_clusters`.
- `write_boot_label()`, `write_serial()`, and internal `write_boot_label_or_serial()` update boot-sector label or serial for FAT12/16 and FAT32, including backup boot for FAT32.
- `find_volume_de()` scans the root directory for a volume-label directory entry.
- `write_volume_label()` creates or updates the root-directory volume label and sets FAT timestamps, honoring `SOURCE_DATE_EPOCH`.
- `write_label()` writes both boot-sector and root-directory labels.
- `remove_label()` resets boot label to `NO NAME    ` and marks root volume-label entry deleted.
- `pretty_label()` converts the 11-byte DOS label to printable local text using `charconv`.

Important validation logic:
- Rejects zero logical sector size, zero cluster size, unsupported FAT counts, zero FAT size, inaccessible final sector, no data clusters, too many FAT entries, invalid root directory sizing, and filesystems too large for `off_t`.
- FAT32-specific handling validates root cluster/root entries combinations, warns on too-few clusters, checks backup boot, and reads FSINFO.
- FAT12/FAT16 type is inferred from data-cluster thresholds unless Atari variant rules apply.

Dependencies:
- Uses `fs_read`, `fs_write`, and `fs_test` from `io.c`.
- Uses FAT helpers such as `next_cluster`, `cluster_start`, `set_fat`, `get_fat`, and owner tracking.
- Uses `get_choice`, `die`, `alloc`, and label conversion helpers.

Research notes:
- This file is the authoritative translator from raw boot sector fields into the shared `DOS_FS` runtime model.
- Label operations are shared by both `fsck.fat` and `fatlabel`.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/boot.h -->
# File Research: sources/local-fs/dosfstools/src/boot.h

Public interface for FAT boot-sector and label operations.

Declared functions:
- `read_boot()` initializes a `DOS_FS` from the open filesystem.
- `write_label()`, `write_boot_label()`, `write_volume_label()`, `remove_label()`, and `write_serial()` mutate label/serial metadata.
- `find_volume_de()` locates the root-directory volume-label entry.
- `pretty_label()` formats an 11-byte DOS label for display.
- `alloc_rootdir_entry()` allocates a root-directory slot, optionally generating a unique name.

Role:
- Exposes boot/layout parsing and root-label manipulation to `fsck.fat`, `fatlabel`, `fat.c`, and checker repair code.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/boot.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/charconv.c -->
# File Research: sources/local-fs/dosfstools/src/charconv.c

DOS OEM codepage conversion layer for short names and labels.

Main behavior:
- Provides an internal CP850 Unicode table and transliteration table.
- With `HAVE_ICONV`:
  - Initializes conversions between DOS codepage and local charset.
  - Initializes conversions between DOS codepage and `WCHAR_T`.
  - Falls back to the internal CP850 table when iconv cannot initialize CP850.
- Without `HAVE_ICONV`:
  - Supports only CP850 through internal conversion functions.
- Public functions:
  - `set_dos_codepage()`
  - `dos_char_to_printable()`
  - `local_string_to_dos_string()`
  - `dos_string_to_wchar_string()`
  - `wchar_string_to_dos_string()`

Error handling:
- Reports conversion failures, too-long strings, and illegal input sequences to `stderr`.
- Returns `0` on conversion failure and nonzero on success.

Consumers:
- `file.c` uses printable conversion for short filenames.
- `boot.c`, `fatlabel.c`, and `check.c` use it for volume labels.
- `common.c` uses wchar conversion to validate lowercase label characters independent of the raw DOS codepage.

Research notes:
- The conversion state is process-global and initialized once.
- Label length enforcement is partly done before conversion and partly by conversion output buffer sizing.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/charconv.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/charconv.h -->
# File Research: sources/local-fs/dosfstools/src/charconv.h

Header for DOS/local/wide-character conversion helpers.

Contents:
- Defines `DEFAULT_DOS_CODEPAGE` as 850.
- Declares public conversion functions:
  - `set_dos_codepage`
  - `dos_char_to_printable`
  - `local_string_to_dos_string`
  - `dos_string_to_wchar_string`
  - `wchar_string_to_dos_string`

Role:
- Centralizes codepage handling for labels and FAT short-name display.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/charconv.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/check.c -->
# File Research: sources/local-fs/dosfstools/src/check.c

Core `fsck.fat` directory-tree and metadata repair engine.

Major responsibilities:
- Builds an in-memory tree of `DOS_FILE` entries from root and subdirectories.
- Tracks cluster ownership through `fat.c` owner table.
- Validates and repairs:
  - bad short names
  - duplicate directory entries
  - broken `.` and `..` entries
  - invalid start clusters
  - directories with nonzero size
  - self-referential or parent-referential directories
  - free/bad clusters inside file chains
  - circular cluster chains
  - cross-linked cluster chains
  - file-size versus cluster-chain length mismatches
  - requested drop/undelete operations
  - dirty flags
  - boot-sector and root-directory label mismatches.

Important helpers:
- `path_name()` builds display paths, preferring LFN names.
- `file_stat()` formats size/date metadata for duplicate-entry decisions.
- `bad_name()` validates 8.3 names, with Atari and `-S` no-middle-space modes.
- `drop_file()`, `truncate_file()`, `auto_rename()`, and `rename_file()` implement repair actions.
- `handle_dot()` validates or creates `.` and `..` entries.
- `check_file()` validates cluster chains, ownership, file sizes, and shared cluster handling.
- `check_dir()` checks bad names and duplicate names inside one directory.
- `test_file()` detects loops and optionally read-tests clusters.
- `undelete()` reconstructs a deleted file’s chain by linking contiguous free clusters.
- `add_file()` reads one directory slot, handles LFN state, applies drop/undelete rules, and adds a `DOS_FILE`.
- `scan_dir()`, `subdirs()`, and `scan_root()` perform recursive traversal.
- `check_dirty_bits()` clears FAT dirty/clean-shutdown state for FAT12/16/32.
- `check_label()` reconciles root-directory and boot-sector labels, validates label characters, and optionally enforces uppercase-only labels.

Key dependencies:
- `fat.c`: cluster chain traversal, ownership, FAT mutation.
- `io.c`: queued or immediate on-disk writes.
- `lfn.c`: long filename sequence parsing and repair.
- `file.c`: user-requested drop/undelete path descriptors and short-name formatting.
- `boot.c`: label and root-directory allocation helpers.
- `common.c`: interactive choices, memory queue, input, diagnostics.
- `charconv.c`: label validation and conversion.

Control-flow significance:
- `scan_root()` returns nonzero when repair invalidates traversal enough to require another pass.
- `fsck.fat.c` loops `read_fat(...), scan_root(...)` until scanning stabilizes.
- Cluster owner bookkeeping is first used transiently by `test_file()` and then permanently by `check_file()` for cross-link detection.

Research notes:
- This file is the highest-level FAT repair policy layer.
- Most repair choices are routed through `get_choice()`, so the same code supports interactive and automatic/noninteractive modes.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/check.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/check.h -->
# File Research: sources/local-fs/dosfstools/src/check.h

Public checker interface.

Declared functions:
- `check_dirty_bits(DOS_FS *fs)`
- `scan_root(DOS_FS *fs)`
- `check_label(DOS_FS *fs)`

Role:
- Exposes the repair engine entry points used by `fsck.fat.c`.
- Also lets `boot.c`/`fat.c` share checker-related declarations through the common source set.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/check.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/common.c -->
# File Research: sources/local-fs/dosfstools/src/common.c

Shared utilities and process-global mode state.

Globals:
- `interactive`
- `write_immed`
- `atari_format`
- `program_name`

Main functions:
- `die()` and `pdie()` print diagnostics and terminate.
- `alloc()` wraps `malloc()` and exits on failure.
- `qalloc()` and `qfree()` implement a simple linked allocation queue used for per-pass allocations such as `DOS_FILE` and LFN strings.
- `min()` returns the smaller integer.
- `xasprintf()` wraps `vasprintf()` and exits on failure; includes fallback `vasprintf()` when unavailable.
- `get_choice()` drives interactive/noninteractive repair choices. In noninteractive mode it prints a message and returns the provided default result.
- `get_line()` prompts and reads a line, temporarily restoring canonical terminal input and echo.
- `check_atari()` enables Atari FAT variant by inspecting `/proc/hardware` on configured m68k Linux builds.
- `generate_volume_id()` creates deterministic IDs from `SOURCE_DATE_EPOCH`, otherwise time/usec-based IDs, with random fallback.
- `validate_volume_label()` checks FAT volume-label constraints after DOS-codepage conversion.

Research notes:
- `get_choice()` includes a nested quit confirmation path for interactive fsck.
- `SOURCE_DATE_EPOCH` support makes labels/serials reproducible.
- Label validation returns a bitmask, allowing callers to distinguish lowercase warnings from hard invalidity.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/common.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/common.h -->
# File Research: sources/local-fs/dosfstools/src/common.h

Shared declarations for utilities, globals, and FAT variant state.

Contents:
- Defines fallback `OFF_MAX`.
- Declares global modes:
  - `interactive`
  - `write_immed`
  - `atari_format`
  - `program_name`
- Declares fatal diagnostics, allocation helpers, queued allocation cleanup, `xasprintf`, interactive choice/input helpers, Atari detection, volume ID generation, and volume-label validation.

Role:
- Provides common infrastructure used across fsck, fatlabel, boot parsing, FAT repair, file operations, and I/O.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/common.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/device_info.c -->
# File Research: sources/local-fs/dosfstools/src/device_info.c

Device discovery layer used by `mkfs.fat` and `testdevinfo`.

Main behavior:
- Initializes `struct device_info` with unknown/default sentinel values.
- `get_device_info()` classifies target file descriptor:
  - regular file: `TYPE_FILE`, partition 0, size from `st_size`
  - non-block non-file: `TYPE_BAD`
  - block device: gathers size, geometry, sector size, and Linux sysfs metadata.
- Linux-specific `get_block_linux_info()`:
  - Opens `/sys/dev/block/<major>:<minor>`.
  - Detects partition number from `partition`.
  - Reads whole-disk sector size from parent `../size`.
  - Detects children by scanning partition subdirectories and `holders`.
  - Detects virtual devices through `slaves`.
  - Detects loop devices backed by regular files via `LOOP_GET_STATUS64`.
  - Reads `removable` to classify fixed versus removable.
- `is_device_mounted()` checks mount tables through `getmntent()` or `getmntinfo()` depending on platform.

Dependencies:
- Uses `blkdev_get_size`, `blkdev_get_geometry`, `blkdev_get_start`, and `blkdev_get_sector_size`.
- Uses Linux `major`/`minor`, sysfs, and optional loop headers when available.

Research notes:
- This file intentionally separates mkfs safety heuristics from raw block-device ioctl helpers.
- `device_info_verbose` is declared but not used inside this file; likely consumed elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/device_info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/device_info.h -->
# File Research: sources/local-fs/dosfstools/src/device_info.h

Public model and declarations for mkfs-side target-device analysis.

Contents:
- `enum device_type`:
  - `TYPE_UNKNOWN`
  - `TYPE_BAD`
  - `TYPE_FILE`
  - `TYPE_VIRTUAL`
  - `TYPE_REMOVABLE`
  - `TYPE_FIXED`
- `struct device_info` fields:
  - device type
  - partition number
  - child-device presence
  - geometry heads/sectors/start/size
  - sector size
  - byte size
- Declares `device_info_verbose`, `get_device_info()`, and `is_device_mounted()`.

Role:
- Provides mkfs with enough target information to choose geometry defaults and warn about unsafe targets.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/device_info.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/endian_compat.h -->
# File Research: sources/local-fs/dosfstools/src/endian_compat.h

Endian conversion compatibility header.

Behavior:
- Includes `<endian.h>` when available.
- Else includes `<sys/endian.h>` when available.
- Else, on Apple platforms with `libkern/OSByteOrder.h`, maps `htobe*`, `htole*`, `be*toh`, and `le*toh` macros to `OSSwap...` functions.
- Emits a preprocessor error if no endian support is available.

Role:
- Supplies consistent little-endian conversions for FAT on-disk structures.
- Included by `fsck.fat.h`, so most FAT metadata code gets these conversions transitively.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/endian_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/fat.c -->
# File Research: sources/local-fs/dosfstools/src/fat.c

FAT table access, repair, ownership tracking, bad-cluster handling, and orphan-chain recovery.

Core functions:
- `get_fat()` decodes FAT12, FAT16, or FAT32 entries. FAT32 preserves high reserved bits separately.
- `release_fat()` frees FAT bytes and cluster owner table.
- `read_fat()` loads FAT data, compares redundant FATs, chooses/repairs a FAT copy, initializes `cluster_owner`, and truncates out-of-range cluster links.
- `set_fat()` updates an entry in memory and queues writes to all FAT copies.
- `bad_cluster()` tests FAT bad-cluster markers.
- `next_cluster()` follows a cluster chain, returning `-1` on EOF and aborting on bad-cluster traversal.
- `cluster_start()` maps a cluster number to byte offset.
- `set_owner()` and `get_owner()` manage cluster-to-`DOS_FILE` ownership used by checker passes.
- `fix_bad()` read-tests unowned clusters and marks unreadable ones bad.
- `reclaim_free()` frees allocated but unowned clusters.
- `reclaim_file()` recovers unowned cluster chains into generated root files, breaking orphan cycles and cross-links.
- `update_free()` recomputes free cluster count and repairs FAT32 FSINFO summary.

Important repair behavior:
- Can use user-selected `fat_table` or choose between first/second FAT.
- Refuses to proceed if FAT corruption is too severe and no usable copy exists.
- Maintains FAT32 reserved high bits when rewriting entries.
- Uses `alloc_rootdir_entry()` to create recovered `FSCK%04dREC` files.

Dependencies:
- `boot.c` for root-entry allocation.
- `check.c` types and owner relationships through `DOS_FILE`.
- `io.c` for all disk I/O.
- `common.c` for choices and fatal errors.

Research notes:
- This file owns the low-level mutation semantics for FAT entries; checker code should use these helpers instead of writing FAT bytes directly.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/fat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/fat.h -->
# File Research: sources/local-fs/dosfstools/src/fat.h

Public interface for FAT table operations.

Declared capabilities:
- Load/release FAT state.
- Get/set individual FAT entries.
- Detect bad clusters.
- Traverse chains and map clusters to offsets.
- Set/get cluster ownership.
- Scan for bad clusters.
- Reclaim unowned clusters by freeing or salvaging to files.
- Update FAT32 free-cluster summary.

Role:
- Provides the shared cluster-chain API used by boot/root allocation, directory checking, fsck main flow, and label handling on FAT32.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/fatlabel.c -->
# File Research: sources/local-fs/dosfstools/src/fatlabel.c

Command-line interface for displaying/changing FAT volume label or serial number.

Main flow:
- Defines the same global knobs required by shared fsck/label code: `rw`, `list`, `test`, `verbose`, `fat_table`, `n_files`, `mem_queue`, etc.
- Parses options:
  - `-i/--volume-id`
  - `-r/--reset`
  - `-c/--codepage`
  - `-V/--version`
  - `-h/--help`
- Initializes Atari variant detection and DOS codepage conversion.
- Chooses read-write mode only for change/reset operations.
- `handle_label()`:
  - validates new labels, converts local text to DOS codepage, pads to 11 bytes
  - opens filesystem, reads boot sector
  - reads FAT only for FAT32 when root-directory traversal needs cluster chains
  - prints existing label, writes new label, or removes label.
- `handle_volid()`:
  - validates hexadecimal 32-bit serial input
  - resets serial using `generate_volume_id()` when requested
  - reads/writes boot serial.

Dependencies:
- Reuses `fs_open`, `read_boot`, `read_fat`, `find_volume_de`, `write_label`, `remove_label`, `write_serial`, `pretty_label`, and char conversion helpers.

Research notes:
- This command does not perform full fsck repair; it uses only enough FAT support to locate root label entries on FAT32.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/fatlabel.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/file.c -->
# File Research: sources/local-fs/dosfstools/src/file.c

Path descriptor and short-name utility code for fsck drop/undelete operations.

Main functions:
- `file_name()` formats an 11-byte DOS 8.3 name as printable text, using codepage conversion and octal escapes.
- `file_cvt()` converts user-entered pretty names to fixed 8.3 uppercase DOS form, accepting `\ooo` octal escapes.
- `file_add()` registers an absolute path for later drop or undelete action in an `FDSC` tree.
- `file_cd()` descends into the descriptor tree for subdirectory traversal.
- `file_type()` returns whether a current directory entry should be dropped or undeleted.
- `file_modify()` applies the registered operation to an in-memory directory entry name and consumes the descriptor.
- `file_unused()` reports registered drop/undelete requests that were never matched.

Data model:
- Global `fp_root` points to a tree of `FDSC` path descriptors.
- `FD_TYPE` differentiates no action, drop, and undelete.

Consumers:
- `fsck.fat.c` registers `-d PATH` and `-u PATH`.
- `check.c` calls `file_type`, `file_modify`, `file_cd`, and `file_unused`.

Research notes:
- The path matching is based on fixed 8.3 names, not long filenames.
- Undelete matching ignores the first byte when the on-disk entry has `DELETED_FLAG`.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/file.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/file.h -->
# File Research: sources/local-fs/dosfstools/src/file.h

Public interface for fsck path-specific operations.

Contents:
- Defines `FD_TYPE`: `fdt_none`, `fdt_drop`, `fdt_undelete`.
- Defines `FDSC`, a linked tree of fixed 8.3 names and requested operation.
- Declares global `fp_root`.
- Declares short-name formatting/conversion and descriptor-tree functions.

Role:
- Connects CLI `-d`/`-u` path arguments to directory traversal in `check.c`.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/file.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/fsck.fat.c -->
# File Research: sources/local-fs/dosfstools/src/fsck.fat.c

Main command-line driver for `fsck.fat`.

Main flow:
- Sets terminal to noncanonical/no-echo mode for single-key interactive choices, restoring at exit.
- Initializes globals: read-write mode, interactivity, list/test/verbose flags, FAT table choice, label policy, memory queue.
- Parses options for auto repair, Atari variant, boot-only check, codepage, drop/undelete, salvage, FAT table selection, listing, read-only, interactive repair, name policy, bad-cluster test, uppercase labels, verbose, verification pass, immediate writes, and long `--variant`.
- Opens target with `fs_open()`.
- Calls `read_boot()`.
- If not boot-only:
  - loops `read_fat(..., repair mode)` and `scan_root()` until stable
  - checks labels
  - optionally marks bad clusters
  - either salvages unowned chains to files or frees them
  - checks dirty bits
  - updates free-cluster summary
  - reports unused drop/undelete requests
  - optionally runs verification pass.
- Prompts whether to write queued changes unless immediate writes are enabled.
- Prints final file/cluster summary.
- Returns `1` if filesystem changed, otherwise `0`.

Dependencies:
- This is orchestration only; substantive repair is delegated to `boot.c`, `fat.c`, `check.c`, `file.c`, and `io.c`.

Research notes:
- Automatic modes `-a`, `-p`, and `-y` enable noninteractive repair and salvage.
- `-n` disables writes and interactivity.
- `-t` and `-w` are rejected in read-only mode.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/fsck.fat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/fsck.fat.h -->
# File Research: sources/local-fs/dosfstools/src/fsck.fat.h

Central shared FAT filesystem structures, constants, and globals.

Key definitions:
- FAT/VFAT constants:
  - `VFAT_LN_ATTR`
  - dirty/surface-test flags
  - FAT16/FAT32 clean-shutdown and hard-error flags
- Packed on-disk structures:
  - `struct boot_sector`
  - `struct boot_sector_16`
  - `struct info_sector`
  - `DIR_ENT`
- Runtime structures:
  - `DOS_FILE`: directory tree node with short entry, optional LFN, offsets, parent/child links.
  - `FAT_ENTRY`: decoded FAT value plus FAT32 reserved high bits.
  - `DOS_FS`: parsed filesystem layout, FAT metadata, root/data positions, cluster size/count, FSINFO, FAT buffer, cluster owner table, serial, and label.
- Global variables shared by commands and modules:
  - `rw`, `list`, `verbose`, `test`, `no_spaces_in_sfns`
  - `fat_table`
  - `only_uppercase_label`
  - `n_files`
  - `mem_queue`
- FAT marker macros:
  - `FAT_EOF`
  - `FAT_IS_EOF`
  - `FAT_BAD`
  - `FAT_MIN_BAD`
  - `FAT_MAX_BAD`
  - `FAT_IS_BAD`
  - `FAT_EXTD`

Role:
- This header is the core contract between boot parsing, FAT manipulation, directory checking, LFN handling, CLI drivers, and I/O.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/fsck.fat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/io.c -->
# File Research: sources/local-fs/dosfstools/src/io.c

Virtual disk I/O layer with optional deferred write queue.

Main behavior:
- `fs_open()` opens the target read-only or read-write and resets pending changes.
- `fs_read()` reads from the device/file and overlays any queued pending writes that overlap the requested range.
- `fs_test()` checks whether a byte range can be read fully.
- `fs_write()` either writes immediately when `write_immed` is set or appends a `CHANGE` record to an in-memory queue.
- `fs_flush()` writes queued changes in order and frees them.
- `fs_close(write)` flushes or discards queued changes, closes the descriptor, and returns whether changes existed.
- `fs_changed()` reports queued or immediate changes.

Research notes:
- Deferred writes let interactive fsck repair decisions be previewed before committing.
- Reads see queued changes, so later repair logic operates against the intended post-repair image even before flush.
- The file uses a single static file descriptor and queue, so the layer is process-global and single-target.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/io.h -->
# File Research: sources/local-fs/dosfstools/src/io.h

Public interface for virtual filesystem/device I/O.

Declared operations:
- `fs_open`
- `fs_read`
- `fs_test`
- `fs_write`
- `fs_close`
- `fs_changed`

Role:
- Abstracts all on-disk reads/writes for fsck and fatlabel.
- Supports both immediate and queued write semantics through `write_immed`.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/lfn.c -->
# File Research: sources/local-fs/dosfstools/src/lfn.c

VFAT long-filename parser and repair helper.

Data model:
- Defines packed `LFN_ENT` for VFAT LFN slots.
- Maintains parser state in module globals:
  - `lfn_unicode`
  - `lfn_checksum`
  - `lfn_slot`
  - `lfn_offsets`
  - `lfn_parts`

Main functions:
- `cnv_unicode()` converts UTF-16LE LFN slot data to local multibyte text, falling back to Linux-style `:xxx` escapes for unconvertible characters.
- `lfn_fix_checksum()` recalculates and writes LFN alias checksums over a range of LFN slots.
- `lfn_reset()` clears parser state.
- `lfn_add_slot()` processes one LFN directory slot, detecting and optionally repairing:
  - nested/new LFN starts inside old sequence
  - missing start bit
  - wrong sequence numbers
  - checksum mismatches
  - nonzero reserved field
  - nonzero start-cluster field.
- `lfn_get()` attaches the accumulated LFN to the following short directory entry, handling unfinished sequences and checksum mismatch.
- `lfn_check_orphaned()` detects an LFN sequence not followed by a real short entry and can delete it.

Dependencies:
- Uses `fs_write()` for slot repairs.
- Uses `get_choice()` and `xasprintf()` for repair decisions.
- Uses `qalloc()` via `mem_queue` so returned LFN strings live for the current scan pass.
- Uses `file_name()` to describe short aliases.

Research notes:
- LFN parsing is intentionally stateful across sequential directory entries.
- Directory scanners must call `lfn_reset()` at new directory boundaries and `lfn_check_orphaned()` at sequence boundaries/end.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/lfn.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dosfstools/src/lfn.h -->
# File Research: sources/local-fs/dosfstools/src/lfn.h

Public interface for VFAT long-filename handling.

Declared functions:
- `lfn_reset()`
- `lfn_add_slot()`
- `lfn_get()`
- `lfn_check_orphaned()`
- `lfn_fix_checksum()`

Role:
- Lets `check.c` stream directory entries through an LFN state machine and repair malformed LFN metadata.
<!-- END FILE RESEARCH: sources/local-fs/dosfstools/src/lfn.h -->