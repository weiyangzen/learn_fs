# Group Research: group_1353_ocfs2_tools_sources_local_fs_ocfs2_tools_ocfs2console_blkid_blkidP__09b5c19f1c43

Scope verified against `Docs/research_subset_a.md`: the requested files are within `sources/local-fs/ocfs2-tools`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/blkidP.h -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/blkidP.h

Internal header for the bundled `libblkid` snapshot used by `ocfs2console` when system blkid is unavailable.

Key contents:
- Defines the internal cache model:
  - `struct blkid_struct_cache`: global cache with `bic_devs`, tag heads, cache file timestamps, flags, filename.
  - `struct blkid_struct_dev`: cached block device with device path, type, priority, `dev_t`, last probe time, flags, label/UUID shortcuts.
  - `struct blkid_struct_tag`: per-device `NAME=value` tag linked both by device and by tag name.
- Defines cache/probe timing:
  - `BLKID_PROBE_MIN` prevents immediate reprobes.
  - `BLKID_PROBE_INTERVAL` controls in-memory revalidation age.
- Defines cache file path `/etc/blkid.tab`, error constants, device priorities for EVMS/LVM/MD, debug masks, and debug dump helpers.
- Declares internal helpers implemented in sibling files:
  - `blkid_read_cache`, `blkid_flush_cache`
  - `blkid_llseek`
  - `blkid_new_dev`, `blkid_free_dev`
  - `blkid_set_tag`, `blkid_find_tag_dev`, `blkid_free_tag`
  - `blkid_strdup`, `blkid_strndup`

Dependencies:
- Public `blkid/blkid.h`
- Local Linux-style `blkid/list.h`

Notable details:
- The cache design is doubly linked and mutable; tag nodes are cross-linked through device lists and per-name head nodes.
- Debug helpers compile only with `CONFIG_BLKID_DEBUG`.
- This header exposes the private implementation shape to all bundled blkid C files.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/blkidP.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/cache.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/cache.c

Implements allocation, initialization, loading, flushing, and destruction of a blkid cache.

Key functions:
- `blkid_get_cache(blkid_cache *ret_cache, const char *filename)`
  - Initializes debug mask from `BLKID_DEBUG` once.
  - Allocates `blkid_struct_cache`.
  - Initializes device and tag lists.
  - Chooses cache file from explicit filename, `BLKID_FILE`, or `/etc/blkid.tab`.
  - Calls `blkid_read_cache`.
- `blkid_put_cache(blkid_cache cache)`
  - Flushes changed cache with `blkid_flush_cache`.
  - Frees all cached devices and remaining tag head structures.
  - Frees cache filename and cache object.

Behavior:
- Empty filename is treated as no filename.
- `BLKID_FILE` is used only when real/effective UID match.
- Cache destruction warns under debug if tag entries remain under tag heads.

Dependencies:
- `blkid_read_cache` from `read.c`
- `blkid_flush_cache` from `save.c`
- `blkid_free_dev` from `dev.c`
- `blkid_free_tag` from `tag.c`

Notable details:
- `blkid_debug_mask` is defined globally here.
- The `TEST_PROGRAM` path creates a cache, probes all devices, and releases it.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/dev.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/dev.c

Implements blkid device object lifecycle and public device iteration.

Key functions:
- `blkid_new_dev()`
  - Allocates a zeroed device object.
  - Initializes list links.
- `blkid_free_dev(blkid_dev dev)`
  - Removes the device from the cache device list.
  - Frees all attached tags.
  - Frees device name and object.
- `blkid_dev_devname(blkid_dev dev)`
  - Returns cached device path.
- `blkid_dev_iterate_begin`, `blkid_dev_next`, `blkid_dev_iterate_end`
  - Public iterator API over `cache->bic_devs`.

Dependencies:
- `blkid_free_tag` from `tag.c`
- Local list primitives.

Notable details:
- Iterator hides `list.h` internals from public API users.
- Iterator validity is checked with a magic constant.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/devname.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/devname.c

Finds, creates, verifies, and bulk-probes blkid device entries by device name.

Key functions:
- `blkid_get_dev(cache, devname, flags)`
  - Finds cached device by path.
  - Optionally creates a cache entry.
  - Optionally verifies it against disk via `blkid_verify`.
- `probe_one(cache, ptname, devno, pri)`
  - Resolves a `/proc` partition name to a real device path.
  - Reuses existing cached entries by `dev_t`.
  - Falls back to `blkid_devno_to_devname`.
  - Assigns device priority, including MD default priority.
- `lvm_get_devno`, `lvm_probe_all`
  - Walk old `/proc/lvm/VGs/.../LVs` hierarchy and probe logical volumes.
- `evms_probe_all`
  - Reads `/proc/evms/volumes` and probes EVMS devices.
- `blkid_probe_all(cache)`
  - Refreshes cache from disk.
  - Probes EVMS, LVM, and `/proc/partitions`.
  - Skips most whole disks when partition devices are present.
  - Flushes cache after probing.

Dependencies:
- `/proc/partitions`
- `/proc/lvm/VGs`
- `/proc/evms/volumes`
- `blkid_verify` from `probe.c`
- `blkid_devno_to_devname` from `devno.c`

Notable details:
- Whole-disk versus partition detection is heuristic: partition names ending in digits are treated as partitions.
- Extended partitions are skipped by size check `sz > 1`.
- Cache probing is throttled using `BLKID_BIC_FL_PROBED` and `BLKID_PROBE_INTERVAL`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/devname.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/devno.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/devno.c

Resolves block device numbers to device paths and provides string duplication helpers.

Key functions:
- `blkid_strndup`, `blkid_strdup`
  - Local allocation helpers used throughout bundled blkid.
- `blkid_devno_to_devname(dev_t devno)`
  - Searches `/devices`, `/devfs`, and `/dev`.
  - Performs breadth-first directory traversal.
  - Returns allocated path for first block device matching `st_rdev`.
- Internal helpers:
  - `add_to_dirlist`
  - `free_dirlist`
  - `scan_dir`

Dependencies:
- `stat`, `opendir`, `readdir`
- `makedev` availability via system headers

Notable details:
- Search avoids `.` and `..`, queues subdirectories, and stops on first match.
- Uses fixed 1024-byte path buffer while scanning.
- `blkid_devdirs` is exported for use by `devname.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/devno.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/getsize.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/getsize.c

Computes block device size in bytes for probing code.

Key functions:
- `blkid_get_dev_size(int fd)`
  - Attempts platform-specific ioctls first:
    - Darwin `DKIOCGETBLOCKCOUNT`
    - Linux `BLKGETSIZE64`
    - Linux/compat `BLKGETSIZE`
    - floppy `FDGETPRM`
  - Falls back to binary search over valid seek/read offsets.
- `valid_offset(fd, offset)`
  - Seeks to offset and attempts to read one byte.

Dependencies:
- `blkid_llseek` from `llseek.c`
- platform disk ioctls and headers

Notable details:
- Disables `BLKGETSIZE64` on old Linux 2.x kernels matching a specific release-prefix heuristic.
- Returns `0` on size overflow for too-small `blkid_loff_t`.
- Fallback binary search is slow but portable when no ioctl is available.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/getsize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/list.h -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/list.h

Local copy of a Linux-kernel-style intrusive doubly linked list implementation.

Key contents:
- `struct list_head`
- Initialization macros:
  - `LIST_HEAD_INIT`
  - `LIST_HEAD`
  - `INIT_LIST_HEAD`
- Operations:
  - `list_add`
  - `list_add_tail`
  - `list_del`
  - `list_del_init`
  - `list_empty`
  - `list_splice`
- Iteration and container macros:
  - `list_entry`
  - `list_for_each`
  - `list_for_each_safe`

Usage:
- Used by all bundled blkid cache/device/tag structures.

Notable details:
- Header guard also checks `LIST_HEAD`, avoiding collision with system queue/list headers.
- The implementation trades type safety for compact intrusive list manipulation.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/llseek.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/llseek.c

Portable large-file seek wrapper for blkid probing.

Key function:
- `blkid_llseek(int fd, blkid_loff_t offset, int whence)`
  - Uses plain `lseek` when `off_t` can represent the offset.
  - Uses `lseek64`, `llseek`, or Linux `_llseek` syscall depending on platform/configure probes.
  - On unsupported large offsets, sets `errno = EOVERFLOW`.

Dependencies:
- Linux syscall support when no direct 64-bit seek wrapper exists.
- `blkid_loff_t` from public blkid types.

Notable details:
- Maintains `do_compat` static flag after `ENOSYS` to avoid repeated unsupported syscall attempts.
- Non-Linux path falls back to `lseek64` when available or guarded `lseek`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/llseek.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/probe.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/probe.c

Core content-signature probing implementation for the bundled blkid library.

Key responsibilities:
- Reads known offsets from block devices.
- Matches filesystem or volume-manager magic values.
- Extracts TYPE, LABEL, UUID, and selected secondary tags.
- Verifies cached devices and drops stale/invalid entries.

Supported signatures include:
- Oracle ASM
- NTFS
- JBD, ext2, ext3
- ReiserFS variants
- VFAT/FAT12/FAT16/FAT32
- Minix, VxFS, XFS, ROMFS, BFS, cramfs, QNX4
- UDF and ISO9660
- JFS, HFS, UFS, HPFS, SysV
- swap variants at multiple page-size offsets
- OCFS and OCFS2
- MD RAID superblock at end of device

Key functions:
- `check_mdraid`
  - Reads MD superblock near end of device and reconstructs MD UUID.
- `set_uuid`
  - Converts binary UUID to text and sets `UUID`.
- Filesystem-specific probe helpers:
  - `probe_ext2`, `probe_ext3`, `probe_jbd`
  - `probe_vfat`, `probe_msdos`
  - `probe_xfs`, `probe_reiserfs`, `probe_jfs`, `probe_romfs`
  - `probe_swap0`, `probe_swap1`
  - `probe_udf`
  - `probe_ocfs`, `probe_ocfs2`
  - `probe_oracleasm`
- `blkid_verify(cache, dev)`
  - Revalidates a device path.
  - Throttles reprobes.
  - Opens and stats the device.
  - Tries current cached type first, then all known signatures if current type fails.
  - Sets `TYPE`, `LABEL`, `UUID`, `SEC_TYPE`, `MOUNT` as applicable.
- `blkid_known_fstype(fstype)`
  - Checks whether a type appears in the signature table.

OCFS-specific details:
- `probe_ocfs` reads OCFS v1 label/header layout, sets:
  - `SEC_TYPE=ocfs1` for major 1
  - `SEC_TYPE=ntocfs` for major >= 9
  - `LABEL`, `MOUNT`, `UUID`
- `probe_ocfs2` recognizes `OCFSV2` signatures at 1K, 2K, 4K, and 8K offsets, then sets `LABEL` and `UUID`.

Notable details:
- Cached 1 KiB buffers are indexed by probe offset to avoid duplicate reads.
- If a cached type no longer matches, stale type/label/UUID tags are cleared and probing restarts.
- If probing cannot find any type and no old type remains, the device cache entry is freed.
- File descriptor leak risk: paths returning early after successful open, such as some stale-device branches, do not always close before returning.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/probe.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/probe.h -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/probe.h

Defines probe table metadata, on-disk structure slices, OCFS/OCFS2 layouts, Oracle ASM label layout, ISO descriptor layout, and byte-swap helpers.

Key contents:
- `struct blkid_magic`
  - Filesystem type, kilobyte offset, byte offset, magic length, magic bytes, optional probe callback.
- Probe callback typedef `blkid_probe_t`.
- Partial on-disk structures for:
  - ext2/ext3 superblock
  - XFS superblock
  - ReiserFS superblock
  - JFS superblock
  - ROMFS superblock
  - swap header
  - VFAT/MSDOS boot sectors
  - Minix superblock
  - MD RAID superblock
  - HFS superblock
  - OCFS volume header/label
  - OCFS2 superblock
  - Oracle ASM disk label
  - ISO volume descriptor
- OCFS helpers:
  - `ocfsmajor`
  - `ocfslabellen`
  - `ocfsmountlen`
- Endian helpers:
  - `blkid_swab16`, `blkid_swab32`, `blkid_swab64`
  - `blkid_le*` and `blkid_be*` macros

Notable details:
- Structures are intentionally partial: only fields needed for type/label/UUID probing are represented.
- Contains x86 inline assembly byte-swap fast paths for older GCC/i386 builds.
- OCFS2 superblock signature and supported block size constants are duplicated locally for probing.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/probe.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/read.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/read.c

Parses the blkid cache file into in-memory cache/device/tag objects.

Cache format:
- One device per line:
  - `<device DEVNO="..." TIME="..." TYPE="..." ...>/dev/name</device>`
- Required tags documented:
  - `ID`, `TIME`, `TYPE`
- Optional tags documented:
  - `LABEL`, `UUID`

Key functions:
- Text helpers:
  - `skip_over_blank`
  - `skip_over_word`
  - `strip_line`
- Parsing helpers:
  - `parse_start`
  - `parse_end`
  - `parse_dev`
  - `parse_token`
  - `parse_tag`
- `blkid_parse_line(cache, dev_p, cp)`
  - Parses one cache line.
  - Creates/fetches the device object.
  - Applies tags and direct fields.
  - Drops device if no `TYPE`.
- `blkid_read_cache(cache)`
  - Opens cache file.
  - Skips reread if mtime unchanged or cache is dirty.
  - Handles backslash-continued lines.
  - Parses each line and updates `bic_ftime`.
  - Clears `BLKID_BIC_FL_CHANGED` after successful initial read.

Direct field parsing:
- `DEVNO` into `bid_devno`
- `PRI` into `bid_pri`
- `TIME` into `bid_time`
- Other tags via `blkid_set_tag`

Notable details:
- This is XML-like, not a general XML parser.
- Comments are skipped only when line starts with `#` after leading whitespace.
- Unknown XML-like lines are skipped.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/read.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/resolve.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/resolve.c

Public lookup helpers for converting tags to device names and device names to tag values.

Key functions:
- `blkid_get_tag_value(cache, tagname, devname)`
  - Gets a device entry, verifies/probes it through `BLKID_DEV_NORMAL`, and returns an allocated copy of the requested tag value.
  - Creates a temporary cache if caller passes `NULL`.
- `blkid_get_devname(cache, token, value)`
  - If `value` is absent and token lacks `=`, returns a copy of token as a raw device path.
  - If token is `NAME=value`, parses it with `blkid_parse_tag_string`.
  - Finds the best matching cached/probed device by tag via `blkid_find_dev_with_tag`.
  - Returns allocated device path.

Dependencies:
- `blkid_get_cache`, `blkid_put_cache`
- `blkid_get_dev`
- `blkid_find_tag_dev`
- `blkid_find_dev_with_tag`
- `blkid_parse_tag_string`

Notable details:
- Temporary caches are automatically flushed/freed through `blkid_put_cache`.
- Tag lookups can trigger full device probing indirectly through `blkid_find_dev_with_tag`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/resolve.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/save.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/save.c

Serializes an in-memory blkid cache back to disk.

Key functions:
- `save_dev(dev, FILE *file)`
  - Skips non-absolute device names.
  - Writes one XML-like `<device ...>path</device>` line.
  - Includes `DEVNO`, `TIME`, optional `PRI`, and all device tags.
- `blkid_flush_cache(cache)`
  - Skips if no devices or cache not changed.
  - Checks cache file writability.
  - For regular existing files, writes to `filename-XXXXXX` via `mkstemp`.
  - Creates a `.old` backup by link and renames temp file into place.
  - Clears changed flag on successful write.

Dependencies:
- `list_for_each`
- `blkid_struct_dev` and tags from `blkidP.h`

Notable details:
- Does not escape tag names/values or device names when writing, matching the simple parser assumptions.
- Calls `fchmod(fd, 0644)` after `mkstemp`; if `mkstemp` failed, `fd` is invalid but still passed to `fchmod`.
- Returns `1` after successful write, `0` when skipped, negative for parameter error, or errno-like values on open failures.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/save.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/tag.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/tag.c

Implements blkid tag lifecycle, tag assignment, tag parsing, tag iteration, and tag-based device lookup.

Key functions:
- `blkid_new_tag`
  - Allocates and initializes a tag object.
- `blkid_free_tag`
  - Removes tag from both linked lists and frees name/value.
- `blkid_find_tag_dev(dev, type)`
  - Finds a tag on one device by name.
- `blkid_find_head_cache(cache, type)`
  - Finds per-tag-name head in cache.
- `blkid_set_tag(dev, name, value, vlength)`
  - Adds, updates, or deletes a tag.
  - Creates per-name cache head if needed.
  - Updates shortcuts:
    - `bid_type`
    - `bid_label`
    - `bid_uuid`
  - Marks cache changed.
- `blkid_parse_tag_string(token, ret_type, ret_val)`
  - Parses `NAME=value`, with optional quote stripping.
- Tag iterator:
  - `blkid_tag_iterate_begin`
  - `blkid_tag_next`
  - `blkid_tag_iterate_end`
- `blkid_find_dev_with_tag(cache, type, value)`
  - Searches tag-name list for exact value.
  - Chooses highest-priority device.
  - Verifies unverified cached matches.
  - Triggers `blkid_probe_all` if cache has not yet been probed.

Notable details:
- Device priority lets EVMS/LVM/MD aliases win over lower-priority duplicates.
- Tag heads are represented as tag objects without device values.
- Deleting a tag also clears shortcut pointers by assigning `NULL`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/tag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/version.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/version.c

Exports version information for the bundled blkid snapshot.

Key constants:
- `E2FSPROGS_VERSION "1.37"`
- `E2FSPROGS_DATE "21-Mar-2005"`

Key functions:
- `blkid_parse_version_string(ver_string)`
  - Parses digits from version string, ignoring dots until first non-digit/non-dot.
  - Example: `1.37` becomes `137`.
- `blkid_get_library_version(ver_string, date_string)`
  - Optionally returns static version/date strings.
  - Returns parsed integer version.

Notable details:
- Copyright header says GNU Public License rather than LGPL, unlike most bundled blkid files.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/blkid/version.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2console -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2console

Python 2 executable entrypoint for the OCFS2 GUI console.

Behavior:
- Imports `process_args()` from `ocfs2interface.about`.
- Supports node-config-only mode via parsed arguments.
- Temporarily converts warnings to errors during `gtk` import to catch no-display initialization failures.
- On GTK initialization failure:
  - Prints a specific X11-display error when message mentions display.
  - Prints a generic windowing initialization error otherwise.
  - Exits with status `1`.
- Dispatches:
  - `--node-config` / `-N`: `ocfs2interface.nodeconfig.node_config()`
  - default: `ocfs2interface.console.main()`

Notable details:
- Uses Python 2 exception syntax and print redirection.
- Explicitly handles an old PyGTK behavior where missing `DISPLAY` was only a warning.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2console -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2console.8.in -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2console.8.in

Manual page template for `ocfs2console`.

Content:
- Defines `ocfs2console` as a GUI console for OCFS2.
- States it manages OCFS2 volumes and is especially recommended for configuring O2CB clusters.
- Lists capabilities:
  - format OCFS2 volumes
  - tune OCFS2 volumes
  - mount/umount OCFS2 volumes
- See also:
  - `mkfs.ocfs2(8)`
  - `fsck.ocfs2(8)`
  - `tunefs.ocfs2(8)`
  - `mounted.ocfs2(8)`
  - `debugfs.ocfs2(8)`
  - `o2cb(7)`

Notable details:
- Version is substituted through `@VERSION@`.
- Dated September 2010.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2console.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/Makefile

Builds and installs the Python package and C extension modules for `ocfs2interface`.

Key outputs:
- `plistmodule.so`
- `gidlemodule.so`
- `ocfs2module.so`
- `o2cbmodule.so`
- Python package files listed in `PYSRC`
- Generated `confdefs.py` from `confdefs.py.in`

Libraries:
- `libocfs2`
- `libo2dlm`
- `libo2cb`
- optional `ldlm_lt` for fsdlm support
- optional `cmap`
- internal or system blkid:
  - if `HAVE_BLKID` is unset, links `ocfs2console/blkid/libblkid-internal.a`
- UUID, com_err, GLib, Python config libs

Notable build flags:
- `CFLAGS += -fPIC`
- Python module flags include `-fno-strict-aliasing`
- GLib CPP flags disable deprecated APIs.

Install behavior:
- Creates `$(pyexecdir)/ocfs2interface`.
- Installs all shared modules, Python sources, and generated Python file.

Notable details:
- `toolbar.py` and `tune.py` are included in package source list even though they are outside this research group.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/__init__.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/__init__.py

Package marker for `ocfs2interface`.

Content:
- GPL header.
- Module docstring says it is a dummy file so packages work.

Behavior:
- No imports, symbols, or runtime logic.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/__init__.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/about.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/about.py

Command-line argument handling and About dialog for OCFS2 Console.

Key functions:
- `print_version()`
  - Prints `OCFS2Console version <OCFS2TOOLS_VERSION>`.
- `print_usage(name)`
  - Documents `--node-config`, `--version`, and `--help`.
- `process_args()`
  - Parses top-level args.
  - Returns whether node-config-only mode was requested.
  - Exits for version/help.
- `process_gui_args()`
  - Allows only no args or `--clusterconf` / `-C`.
- `about(parent)`
  - For PyGTK >= 2.6, uses `gtk.AboutDialog`.
  - For older PyGTK, falls back to `gtk.MessageDialog`.
- `main()`
  - Processes args and shows About dialog.

Dependencies:
- `confdefs.OCFS2TOOLS_VERSION`
- `guiutil.set_props`
- `gtk`

Notable details:
- `--clusterconf` is accepted by GUI arg validation but not otherwise handled in this file.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/about.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/bosa.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/bosa.py

OCFS2 filesystem browser widget. It displays directory entries from an OCFS2 volume and metadata fields for the selected entry.

Key classes:
- `InfoLabel`
  - Monospace selectable label for one `ls.py` field.
  - Aligns and sizes based on field metadata.
- `Browser(gtk.VBox)`
  - Opens `ocfs2.Filesystem(device)`.
  - Displays current path label.
  - Builds a `gtk.TreeStore` of directory/file entries.
  - Sorts directories before files.
  - Lazily populates directories as tree rows are expanded.
  - Shows metadata labels using `ls.fields`.
- `TreeLevel(IdleBase)`
  - Wraps a directory iterator.
  - Runs incremental population through GLib idle callbacks.
  - Supports foreground/background priority when expanded/collapsed.

Dependencies:
- `ocfs2` Python C extension
- `gidle.Idle` fallback if `gobject.Idle` unavailable
- `ls.fields`
- PyGTK/Pango

Notable behaviors:
- Empty, loading, and error placeholder rows are inserted for UX feedback.
- Directory entries are loaded incrementally so large directories do not freeze the UI as much.
- `refresh()` clears old idle levels, opens filesystem, and starts root listing.

Notable issues:
- `tree_expand_row()` references `level` before assigning it in the branch where `info_obj` is already a `TreeLevel`; it should use `info_obj`.
- `get_fs_path()` assumes each iter maps to a dentry; placeholder rows may need parent fallback handling, which selection code partly manages.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/bosa.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/classlabel.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/classlabel.py

Provides a descriptor that converts class names into human-readable labels.

Key contents:
- Regex `caps = re.compile('(?!\A)[A-Z][a-z]')`
- `make_title(m)`
  - Inserts a leading space before matched capitalized word segments.
- `class_label` descriptor
  - `__get__` returns transformed class name.
  - Example: `MaximumNodes` becomes `Maximum Nodes`.

Usage:
- Used by field classes in `general.py` and `ls.py` to auto-generate labels.

Notable details:
- Exports an instance named `class_label`, replacing the class name binding.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/classlabel.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/confdefs.py.in -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/confdefs.py.in

Template for generated configuration definitions used by Python modules.

Content:
- GPL header.
- Defines:
  - `OCFS2TOOLS_VERSION = '@VERSION@'`

Usage:
- Generated into `confdefs.py`.
- Imported by `about.py` for version display.

Notable details:
- Build system lists `confdefs.py` as `BUILT_PYSRC`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/confdefs.py.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/console.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/console.py

Main OCFS2 Console window.

Key class:
- `Console(gtk.Window)`
  - Creates main window titled `OCFS2 Console`.
  - Adds notebook tabs:
    - `General`
    - `File Listing`
  - Creates `PartitionView` and wires info frames to selected device.
  - Adds menu and toolbar.
  - Connects selection-sensitive menu/toolbar widgets.
  - Provides action methods for:
    - refresh
    - mount/unmount
    - format
    - relabel
    - slot count tuning
    - check/repair
    - node configuration
    - push cluster config
    - about

Dependencies:
- `PartitionView`
- `Menu`
- `Toolbar`
- `mount`, `format`, `fsck`, `tune`
- `General`, `Browser`
- `node_config`, `push_config`

Notable details:
- Delegates most action implementation to helper modules.
- Calls `process_gui_args()` before starting GUI.
- Refreshes partition list at startup.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/console.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/format.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/format.py

GUI workflow for formatting an unmounted partition as OCFS2.

Key classes:
- `Device(BaseCombo)`
  - Lists available unmounted partitions.
  - Extracts device name from combo text.
- `FormatVolumeLabel(VolumeLabel)`
  - Defaults label text to `oracle`.

Key function:
- `format_partition(parent, device)`
  - Calls `partition_list(..., unmounted=True)`.
  - Shows error if no unmounted partitions exist.
  - Presents dialog fields:
    - available device
    - volume label
    - cluster size
    - number of node slots
    - block size
  - Confirms destructive format action.
  - Builds `mkfs.ocfs2 -x` command plus widget-derived args.
  - Runs via `Process`.
  - Shows error dialog on failure.

Dependencies:
- `plist.partition_list`
- `fswidgets`
- `process.Process`
- `guiutil.Dialog`, `error_box`

Notable details:
- Uses argument list form for `Process`, reducing shell parsing risk here.
- The base command includes `-x`, likely selecting expert/noninteractive behavior for mkfs.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/format.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fsck.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fsck.py

Runs `fsck.ocfs2` inside an embedded terminal dialog for check or repair workflows.

Key functions:
- `fsck_volume(parent, device, check=False)`
  - Creates `TerminalDialog`.
  - Connects terminal child exit to mark completion.
  - Starts command via idle callback.
  - Prevents closing while fsck is still running by warning the user.
- `start_command(terminal, command, dialog)`
  - Calls `terminal.fork_command`.
- `child_exited(terminal, dialog)`
  - Marks dialog finished.
- `fsck_command(device, check)`
  - Builds:
    - check mode: `fsck.ocfs2 -n '<device>'; sleep 1`
    - repair mode: `fsck.ocfs2 -y '<device>'; sleep 1`
  - Runs through `/bin/sh -c`.

Dependencies:
- `terminal.TerminalDialog`
- `terminal.terminal_ok` exported as `fsck_ok`
- PyGTK/GObject

Notable details:
- Command construction uses shell string interpolation with single quotes around `device`; embedded single quotes in device paths would break quoting.
- Menu availability depends on VTE import success through `fsck_ok`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fsck.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fstab.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fstab.py

Simple `/etc/fstab` parser used to prefill mount options.

Key classes:
- `FSTab`
  - `refresh()` reads `/etc/fstab`, skips comments and malformed lines, stores `FSTabEntry` objects.
  - `get(device=None, label=None, uuid=None)` matches entries by raw device path, `LABEL=...`, or lowercase `UUID=...`.
- `FSTabEntry`
  - Stores `spec`, `mountpoint`, `vfstype`, `options`, `freq`, `passno`.
  - Builds a tab-separated string formatter from constructor arg names.
  - Normalizes UUID specs to lowercase.
  - Implements `__str__` and `__repr__`.

Usage:
- `mount.py` uses it to find default mountpoint/options for an OCFS2 device.

Notable details:
- Does not handle escaped whitespace in fstab fields.
- Blank lines fall through to split error and are ignored.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fstab.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fswidgets.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fswidgets.py

Reusable PyGTK widgets for OCFS2 format/tune parameters.

Key classes:
- `BaseCombo`
  - Uses `gtk.ComboBox` for PyGTK >= 2.4.
  - Falls back to `gtk.Combo` on older PyGTK.
  - Provides `get_choice()` and `set_choices()`.
- `ValueCombo`
  - Builds power-of-two size choices from min to max plus `Auto`.
  - Converts chosen text into command-line args.
- `NumSlots`
  - Spin button from 1 to `ocfs2.MAX_SLOTS`, default 4.
  - Produces `('-N', value)`.
- `VolumeLabel`
  - Entry capped at `ocfs2.MAX_VOL_LABEL_LEN`.
  - Produces `('-L', label)`.
- `ClusterSize`
  - Size combo from `ocfs2.MIN_CLUSTERSIZE` to `ocfs2.MAX_CLUSTERSIZE`.
  - Produces `-C`.
- `BlockSize`
  - Size combo from `ocfs2.MIN_BLOCKSIZE` to `ocfs2.MAX_BLOCKSIZE`.
  - Produces `-b`.

Dependencies:
- `ocfs2` constants from C extension
- `guiutil.format_bytes`

Notable details:
- Designed for command assembly in `format.py` and likely tuning modules.
- Old PyGTK compatibility is explicit throughout.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fswidgets.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/general.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/general.py

Displays general OCFS2 filesystem metadata for a selected device.

Key classes:
- `Field`
  - Base class with `fs`, `super`, `dinode`.
  - Returns `N/A` when no superblock is available.
  - Uses `class_label` for labels.
- Field subclasses:
  - `Version`
  - `Label`
  - `UUID`
  - `MaximumNodes`
  - `ClusterSize`
  - `BlockSize`
  - `FreeSpace`
  - `TotalSpace`
- `General(gtk.Table)`
  - Opens `ocfs2.Filesystem(device)`.
  - Reads `fs.fs_super`.
  - Looks up `GLOBAL_BITMAP_SYSTEM_INODE` and reads its cached inode.
  - Renders field labels and values in a table.

Dependencies:
- `ocfs2` C extension
- `classlabel.class_label`
- `guiutil.format_bytes`

Notable details:
- Free/total space are computed from bitmap inode fields and cluster/block sizing.
- OCFS2 open errors are silently converted into `N/A` display.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/general.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/gidlemodule.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/gidlemodule.c

Python 2 C extension exposing richer GLib idle source control as `gidle.Idle`.

Key type:
- `gidle.Idle`
  - Holds `GSource *idle`.
  - Tracks whether attached.
  - Supports instance dictionary and weakrefs.

Methods:
- `attach()`
  - Attaches idle source to default main context and returns source ID.
- `destroy()`
  - Destroys GLib source and marks object destroyed.
- `set_callback(callback, *args)`
  - Stores callback and args in a tuple.
  - Uses `g_source_set_callback`.

Properties:
- `__dict__`
- `priority`
- `can_recurse`
- `id`

Implementation details:
- `handler_marshal` calls Python callback and interprets truthiness as whether to keep source active.
- `destroy_notify` decrefs stored callback tuple.
- `CHECK_DESTROYED` raises `RuntimeError` if methods/properties are accessed after destroy.
- Module init registers `Idle` type.

Usage:
- `bosa.py` uses this as fallback when `gobject.Idle` is unavailable.

Notable details:
- Python 2 C API only: `PyInt`, `PyString`, `Py_InitModule`.
- Type has GC flags but no traverse function, only clear; acceptable for simple state but incomplete for cyclic GC precision.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/gidlemodule.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/guiutil.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/guiutil.py

Small GUI utility module.

Key functions:
- `set_props(obj, **kwargs)`
  - Calls `obj.set_property(k, v)` for each keyword.
- `format_bytes(bytes, show_bytes=False)`
  - Formats byte counts with suffixes `K`, `MB`, `GB`, `TB`.
  - Optionally includes exact byte count.
- `error_box(parent, msg)`
  - Shows modal GTK error dialog.
- `make_callback(obj, callback, sub_callback)`
  - Builds menu/toolbar callback wrappers that call object methods by name.

Compatibility:
- Exports `Dialog`.
  - Uses `gtk.Dialog` if it supports `set_alternative_button_order`.
  - Otherwise defines subclass with no-op `set_alternative_button_order`.

Notable details:
- `format_bytes` uses `K` for KiB-scale values and prints rounded integer values unless exact bytes requested.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/guiutil.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ipwidget.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ipwidget.py

IPv4 address editor widget adapted from older Red Hat/Anaconda code.

Key functions/classes:
- `sanityCheckIPString(ip_string)`
  - Regex-validates four decimal octets.
  - Ensures each octet is 0-255.
- Exceptions:
  - `IPError`
  - `IPMissing`
- `IPEditor(gtk.HBox)`
  - Four 3-character `gtk.Entry` widgets separated by dots.
  - Numeric input only.
  - Typing `.` moves focus to next octet.
  - `hydrate(ip_string)` fills entries from a valid IP.
  - `dehydrate()` validates and returns dotted string.
  - Aliases:
    - `get_text = dehydrate`
    - `set_text = hydrate`

Validation behavior:
- Empty all fields raises `IPMissing`.
- First octet must be 1-255.
- Remaining octets must be 0-255.

Usage:
- `nodeconfig.py` uses it for O2CB node IP addresses.

Notable details:
- Python 2 indentation uses tabs/spaces mixed but is consistent enough for the original interpreter.
- Uses old exception syntax and `string.strip`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ipwidget.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ls.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ls.py

Defines file metadata fields shown by the OCFS2 browser, similar to selected `ls -l` columns.

Key classes:
- `Field`
  - Base for rendering a dentry/dinode attribute as text.
- `Mode`
  - Builds file mode string from OCFS2 dentry type and inode mode bits.
- `Links`
  - Link count.
- `ID2Name`
  - Base for UID/GID to name resolution.
- `Owner`
  - Uses `pwd.getpwuid`.
- `Group`
  - Uses `grp.getgrgid`.
- `Size`
  - Inode size.
- `AllocSize`
  - `i_clusters * fs_clustersize`.
- `Timestamp`
  - Formats mtime using GNU-coreutils-style recent/old format decision.
- `Name`
  - Returns dentry name, though not included in exported `fields`.

Export:
- `fields = (Mode, Links, Owner, Group, Size, AllocSize, Timestamp)`

Dependencies:
- Python `stat`, `pwd`, `grp`, `time`
- `ocfs2` file type constants
- `class_label`

Notable details:
- `Mode` maps OCFS2 file types to single-character type indicators.
- Owner/group fall back to numeric IDs if system lookup fails.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ls.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/menu.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/menu.py

Builds the main OCFS2 Console menubar and selection-state widget lists.

Menu groups:
- File:
  - Quit
- Cluster:
  - Configure Nodes
  - Propagate Configuration, only if terminal/VTE support is available
- Tasks:
  - Format
  - Check, only if fsck terminal support is available
  - Repair, only if fsck terminal support is available
  - Change Label
  - Edit Node Slot Count
- Help:
  - About

Key constants:
- `UNMOUNTED_ONLY`
- `NEED_SELECTION`

Key class:
- `Menu`
  - Converts declarative `menu_data` into `gtk.ItemFactory` items.
  - Resolves callbacks through `guiutil.make_callback`.
  - Returns:
    - menubar widget
    - widgets needing a selection
    - widgets needing an unmounted partition

Dependencies:
- `fsck.fsck_ok`
- `pushconfig.pushconfig_ok`
- `guiutil.make_callback`

Notable details:
- Uses legacy `gtk.ItemFactory`.
- Action sensitivity is delegated to `PartitionView`, which receives the special widget lists.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/menu.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/mount.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/mount.py

Mount and unmount workflows for OCFS2 devices.

Key functions:
- `mount(parent, device)`
  - Prompts for mountpoint/options using `query_mount`.
  - Runs `mount -t ocfs2 [-o options] device mountpoint` via `Process`.
  - Returns mountpoint on success.
  - Shows error dialogs on failure or killed process.
- `unmount(parent, device, mountpoint)`
  - Runs `umount mountpoint` via `Process`.
  - Shows error dialogs on failure or killed process.
- `query_mount(parent, device)`
  - Builds dialog with mountpoint and options entries.
  - Enables OK only for absolute mountpoint-like strings.
  - Prefills values from `get_defaults`.
- `get_defaults(device)`
  - Reads OCFS2 label/UUID.
  - Looks in `/etc/fstab` for matching device/LABEL/UUID and `vfstype == 'ocfs2'`.
- `get_ocfs2_id(device)`
  - Opens `ocfs2.Filesystem` and extracts superblock label/UUID.

Dependencies:
- `ocfs2` C extension
- `fstab.FSTab`
- `process.Process`

Notable details:
- Uses command tuple/list form for subprocess execution.
- Mountpoint validation is minimal: starts with `/` and length > 1.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/mount.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/nodeconfig.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/nodeconfig.py

GUI for O2CB cluster node configuration and stack activation.

Key constants:
- Default cluster name: `ocfs2`
- Default node port: `7777`
- Port range: `1000` to `65534`

Key class:
- `ClusterConfig(Dialog)`
  - Shows existing nodes in a `gtk.TreeView`.
  - Allows adding/editing/removing new, unapplied nodes.
  - Existing active nodes are displayed but not editable.
  - Validates:
    - max node count via `o2cb.O2NM_MAX_NODES`
    - non-empty node name
    - max name length via `o2cb.O2NM_MAX_NAME_LEN`
    - IPv4 address via `IPEditor`
    - duplicate names/IPs
  - Applies new nodes through `o2cb_ctl.add_node`.
  - Reloads cluster state after apply.

Key function:
- `node_config(parent=None)`
  - Queries O2CB init status.
  - Attempts to load/start cluster stack if not loaded/mounted.
  - Gets or creates active cluster name.
  - Shows `ClusterConfig`.
  - After dialog, ensures selected cluster is online.

Dependencies:
- `ocfs2`, `o2cb` C extensions
- `o2cb_ctl`
- `IPEditor`
- `guiutil.Dialog`, `error_box`

Notable issues:
- `load_cluster_state()` catches `o2cb_ctl.CtlError` but raises `ConfError`, while the defined exception is `ConfigError`; this typo would raise `NameError` on that path.
- `edit_node()` updates row values but does not call `can_apply(True)`, so edited unapplied nodes may not enable Apply unless another change already did.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/nodeconfig.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/o2cb_ctl.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/o2cb_ctl.py

Wrapper around `/etc/init.d/o2cb` and `o2cb_ctl` commands.

Key constants:
- `DEFAULT_CLUSTER_NAME = 'ocfs2'`
- `O2CB_INIT = '/etc/init.d/o2cb'`
- `O2CB_CTL = 'o2cb_ctl'`

Key classes:
- `CtlError`
- `O2CBProcess(Process)`
  - Converts string or tuple args into command form.
- `O2CBCtl`
  - Program `o2cb_ctl`, title `Cluster Control`.
- `O2CBInit`
  - Program `/etc/init.d/o2cb`, title `Cluster Stack`.

Key functions:
- Init wrappers:
  - `init_load`
  - `init_online`
  - `init_status`
- Query wrappers:
  - `query_clusters`
  - `query_nodes`
- Mutation:
  - `add_node(name, cluster_name, ip_address, ip_port, parent)`
- Higher-level parsers:
  - `get_active_cluster_name`
    - Queries clusters.
    - Prefers `ocfs2`.
    - Creates default cluster if none exists.
  - `get_cluster_nodes`
    - Parses colon-delimited node output from `o2cb_ctl -I -t node -o`.

Notable details:
- Some command paths pass raw strings to `Process`, which uses shell-like behavior through `popen2.Popen4`; tuple paths are safer.
- Output parsing silently skips malformed lines and comments.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/o2cb_ctl.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/o2cbmodule.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/o2cbmodule.c

Python 2 C extension binding a subset of `libo2cb`.

Exposed module:
- `o2cb`

Exposed types:
- `o2cb.Cluster`
  - Read-only `name`
  - Property `nodes`
  - Method `add_node`
- `o2cb.Node`
  - Read-only `name`
  - Property `number`

Exposed functions:
- `list_clusters()`
- `get_hb_ctl_path()`

Exposed constants:
- `O2NM_API_VERSION`
- `O2NM_MAX_NODES`
- `O2NM_INVALID_NODE_NUM`
- `O2NM_MAX_NAME_LEN`

Key implementation details:
- Wraps libo2cb calls:
  - `o2cb_create_cluster`
  - `o2cb_list_clusters`
  - `o2cb_list_nodes`
  - `o2cb_get_node_num`
  - `o2cb_add_node`
  - `o2cb_get_hb_ctl_path`
- Creates `o2cb.error` exception from `RuntimeError`.
- Uses `initialize_o2cb_error_table()` and `error_message(ret)`.

Notable details:
- Heartbeat region functions are present but compiled out under `#if 0`.
- Python 2 C API only.
- `Cluster.__init__` creates the cluster as a side effect.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/o2cbmodule.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfs2module.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfs2module.c

Python 2 C extension binding read-oriented `libocfs2` filesystem access for the GUI.

Exposed module:
- `ocfs2`

Exposed types:
- `ocfs2.Filesystem`
  - Opens an OCFS2 device, default flags `OCFS2_FLAG_RO | OCFS2_FLAG_BUFFERED`.
  - Read-only properties for fs sizing, roots, superblocks, UUID string.
  - Methods:
    - `flush`
    - `clusters_to_blocks`
    - `blocks_to_clusters`
    - `blocks_in_bytes`
    - `clusters_in_blocks`
    - `block_out_of_range`
    - `lookup_system_inode`
    - `read_cached_inode`
    - `dir_iterate`
    - `iterdir`
- `ocfs2.SuperBlock`
  - Exposes revision, mount/error state, features, block/cluster bits, max slots, label, UUID, root/system block numbers.
- `ocfs2.DInode`
  - Exposes inode metadata: size, timestamps, block number, flags, mode, uid/gid, links, clusters, bitmap totals, etc.
- `ocfs2.DirEntry`
  - Exposes name, inode, record length, file type.
- `ocfs2.DirScanIter`
  - Python iterator over directory entries.

Key implementation details:
- Opens devices with `ocfs2_open`.
- Closes with `ocfs2_close`.
- Reads cached inodes with `ocfs2_read_cached_inode`.
- Directory scanning uses:
  - `ocfs2_dir_iterate` for callback style
  - `ocfs2_open_dir_scan` / `ocfs2_get_next_dir_entry` for iterator style
- Creates `ocfs2.error` exception.

Exposed constants:
- OCFS2 block/cluster sizing, signatures, flags, feature/system inode constants, directory entry constants, file type constants, and max lengths.

Notable issues:
- `fs_blocks_to_clusters()` calls `ocfs2_clusters_to_blocks(self->fs, blocks)` instead of a blocks-to-clusters helper, which appears semantically wrong.
- `fs_dir_iterate()` ignores `ret` from `ocfs2_dir_iterate` and always returns `None`; callback exceptions are also not propagated robustly.
- `DirEntry` keeps `fs_obj` pointer but its deallocator does not `Py_DECREF(self->fs_obj)`, unlike `DInode` and `SuperBlock`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfs2module.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfsplist.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfsplist.c

C helper for enumerating partitions and classifying filesystem type/mount state for the GUI.

Key exported function:
- `ocfs_partition_list(func, data, filter, fstype, unmounted, async)`
  - Creates blkid cache.
  - Optionally compiles GLib pattern filter.
  - Builds device/partition grouping from `/proc/partitions`.
  - Walks entries and calls callback with `OcfsPartitionInfo`.

Key internal logic:
- `partition_info_fill`
  - Reads `/proc/partitions`.
  - Groups partitions under disk-like keys.
  - Handles whole-disk entries.
  - Optionally yields to GLib main loop for async UI responsiveness.
- `get_device_fstype`
  - Applies filter.
  - Requires block device and writable mode bits.
  - Skips IDE CD-ROM/tape devices using `/proc/ide/.../media`.
  - Opens device read-write to test accessibility.
  - Delegates type detection to `fstype_check`.
- `fstype_check`
  - Uses blkid to read `TYPE`.
  - If no type and no requested `fstype`, returns:
    - `partition table` if MBR signature is present
    - `unknown` otherwise
- `partition_walk`
  - Uses `ocfs2_check_mount_point` to determine mountpoint/busy state.
  - If `unmounted=True`, reports only unmounted, not busy, and not excluded pseudo-types.

Dependencies:
- GLib
- `libocfs2`
- bundled/system blkid
- `/proc/partitions`

Notable details:
- Opens devices with `O_RDWR` even for type checks.
- The filter is a GLib glob pattern matched against full device path.
- Async mode manually pumps the default GLib main context every fixed number of iterations.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfsplist.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfsplist.h -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfsplist.h

Header for the OCFS partition-list helper.

Key types:
- `OcfsPartitionInfo`
  - `device`
  - `mountpoint`
  - `fstype`
- `OcfsPartitionListFunc`
  - Callback taking `OcfsPartitionInfo *` and user data.

Key declaration:
- `ocfs_partition_list(func, data, filter, fstype, unmounted, async)`

Dependencies:
- GLib types.

Usage:
- Implemented by `ocfsplist.c`.
- Wrapped for Python by `plistmodule.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfsplist.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/partitionview.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/partitionview.py

Tree view listing OCFS2 partitions and coordinating selected-device UI state.

Key class:
- `PartitionView(gtk.TreeView)`
  - Model columns:
    - device
    - mountpoint
  - Selection change:
    - Enables selection-dependent widgets.
    - Enables mount widgets for mounted rows.
    - Enables unmount/action widgets for unmounted rows.
    - Rebuilds info frames for selected device.
  - `refresh_partitions()`
    - Disables action widgets.
    - Reads optional filter entry.
    - Rebuilds model.
    - Calls `partition_list(..., fstype='ocfs2', async=True)`.
    - Preserves previous device selection where possible.
  - `add_partition`
    - Callback from `plist.partition_list`.
  - Widget-list helpers:
    - `add_sel_widgets`
    - `add_mount_widgets`
    - `add_unmount_widgets`

Dependencies:
- `plist.partition_list`
- PyGTK

Notable details:
- Mounted devices sort before unmounted devices.
- Info tabs are recreated by destroying previous frame child and instantiating the info class with the selected device.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/partitionview.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/plistmodule.c -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/plistmodule.c

Python 2 C extension wrapping `ocfs_partition_list` as module `plist`.

Exposed function:
- `partition_list(callback, data=None, filter=None, fstype=None, unmounted=False, async=False)`

Callback argument behavior:
- Always passes `device`.
- Passes `mountpoint` only when `unmounted` is false.
- Always passes `fstype`.
- Passes `data` if provided.

Implementation:
- `ProxyData` stores Python callback/data and flags.
- `proxy()` converts `OcfsPartitionInfo` into Python tuple and calls callback.
- Stops invoking callback after first Python error, printing the error.
- Module init registers `partition_list`.

Dependencies:
- GLib
- `ocfsplist.h`

Notable details:
- Python callback exceptions are printed and suppress further proxy calls, but `partition_list` still returns `None`.
- Python 2 C API only.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/plistmodule.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/process.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/process.py

Subprocess wrapper with GTK progress dialog and output capture.

Key class:
- `Process`
  - Starts command immediately using `popen2.Popen4`.
  - `reap()`:
    - Sets child stdout/stderr nonblocking.
    - Adds GLib timeout polling.
    - Adds IO watch for output.
    - Runs nested `gtk.main()` until process exits or is killed.
    - Destroys progress dialog and removes watches.
    - Returns `(success, output, killed)`.
  - `timeout()`:
    - Polls process.
    - Sets success from exit status.
    - Kills after timeout.
    - Pulses progress dialog if visible.
  - `kill()`:
    - Sends SIGTERM, schedules SIGKILL fallback.
  - `make_progress_box()`:
    - Builds modal progress window.
  - `read()`:
    - Appends child output.

Constants:
- `INTERVAL = 100`
- `TIMEOUT = 10000`

Notable details:
- If `command` is a string with multiple words, `popen2.Popen4` invokes shell-style command handling.
- `threshold = self.count - INTERVAL * 10` makes delayed progress threshold negative with current constants, so non-`spin_now` operations may never show progress before timeout.
- Uses nested GTK main loop for synchronous command behavior.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/process.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/pushconfig.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/pushconfig.py

Propagates local O2CB cluster configuration to other cluster nodes over SSH.

Key constants:
- `CONFIG_FILE = '/etc/ocfs2/cluster.conf'`
- `command_template`
  - Creates `/etc/ocfs2`.
  - Writes `cluster.conf` through a shell heredoc.
  - Has an O2CB online command commented out.

Key functions:
- `get_hosts(parent=None)`
  - Gets local hostname.
  - Gets active cluster name.
  - Gets cluster nodes.
  - Returns remote node names excluding local hostname.
- `generate_command(cluster_name)`
  - Reads local cluster config.
  - Trims trailing newline.
  - Inserts content into shell heredoc command.
- `propagate(terminal, dialog, remote_command, host_iter)`
  - Starts next SSH command:
    - `ssh root@<host> <remote_command>`
  - Chains on terminal `child-exited`.
  - Marks finished when hosts exhausted.
- `push_config(parent=None)`
  - Gets hosts and generated command.
  - Shows terminal dialog.
  - Runs propagation one host at a time.
  - Warns if user tries to close before finished.

Dependencies:
- `o2cb_ctl`
- `terminal.TerminalDialog`
- VTE availability exported as `pushconfig_ok`

Notable details:
- The remote shell command embeds file contents in a heredoc; config content containing the heredoc delimiter would break the script.
- SSH target uses node names directly as `root@name`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/pushconfig.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/terminal.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/terminal.py

VTE terminal dialog wrapper used by fsck and cluster config propagation workflows.

Key module behavior:
- Attempts `import vte`.
- Exports:
  - `terminal_ok = False` on import failure.
  - `terminal_ok = True` on success.

Key class:
- `TerminalDialog(gtk.Dialog)`
  - Close button only.
  - Adds title label.
  - Embeds `vte.Terminal`.
  - Sets scrollback to 8192 lines.
  - Adds scrollbar bound to terminal adjustment.

Dependencies:
- PyGTK
- VTE Python bindings

Notable details:
- Modules using terminal workflows gate menu items through `terminal_ok`.
- If `vte` import fails, instantiating `TerminalDialog` would fail because `vte` is undefined, but callers normally check `terminal_ok`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/terminal.py -->