# Group Research: group_350_e2fsprogs_sources_local_fs_e2fsprogs_lib_ext2fs_undo_io_c_sources_lo_4e6aeebc0b8e

Scope checked against `Docs/research_subset_a.md`: all files are within `sources/local-fs/e2fsprogs`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/undo_io.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/undo_io.c

## Purpose
Implements the libext2fs undo I/O manager. It wraps a backing I/O manager and records original filesystem data into an `e2undo` file before destructive writes, discards, zeroouts, or byte writes modify the target.

## Data Model
- Undo files begin with an `E2UNDO02` header, a stored superblock copy, and key/data block chunks.
- `struct undo_key` maps filesystem block positions to saved data extents and stores per-block CRCs.
- `struct undo_private_data` tracks the real backing channel, undo-file channel, current key block, next undo block, filesystem offset, block bitmap of already-saved regions, and checksummed header state.

## Main Behavior
- `undo_write_tdb()` is the core pre-write hook: it calculates affected undo-sized blocks, skips blocks already captured, reads original data from the backing device, writes it to the undo file, and appends/extends key records.
- `write_undo_indexes()` writes pending key blocks, captures the current superblock with its magic inverted, updates header metadata, and flushes when requested.
- `try_reopen_undo_file()` validates an existing undo file by magic, header CRC, block-size bounds, feature flags, key-block CRCs, and target superblock match, then reconstructs the written-block map to resume appending.
- `undo_close()` marks the undo file finished unless `UNDO_IO_SIMULATE_UNFINISHED` is set.

## Integration
Exports `undo_io_manager` and setup helpers for selecting the backing manager and undo file name. It forwards normal reads, flushes, readahead, stats, and options to the backing channel while intercepting all write-like operations.

## Risks / Notes
- The file is deliberately single-threaded; `undo_open()` clears `IO_FLAG_THREADS`.
- Undo correctness depends on capturing each affected undo block before the first mutation and on superblock/CRC validation preventing cross-filesystem replay.
- Offset support is propagated to the backing manager and recorded as an undo compatible feature.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/undo_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/unix_io.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/unix_io.c

## Purpose
POSIX/Unix implementation of the libext2fs I/O manager, including raw file/device I/O, a small write-back block cache, optional direct-I/O bounce buffering, stats, locking, discard, zeroout, and file-descriptor-backed channels.

## Main Behavior
- `raw_read_blk()` and `raw_write_blk()` perform positioned reads/writes using `pread/pwrite` when possible, falling back to `llseek` plus `read/write`.
- Unaligned direct I/O uses a bounce buffer and read-modify-write logic.
- The cache stores block-sized buffers, tracks dirty state and access time, flushes dirty entries on eviction/close/blocksize changes, and supports runtime resizing through `cache_blocks`.
- Large or odd-sized reads/writes bypass the cache after flushing.
- `unix_open_channel()` initializes channel metadata, detects block devices, direct-I/O alignment, discard-zeroes behavior, optional thread mutexes, and Linux read-only block-device status.

## Options / Operations
- `offset`: shifts all I/O by a byte offset.
- `cache=on|off`: toggles cache use.
- `cache_blocks`: grows or shrinks the block cache.
- `discard`: uses `BLKDISCARD` for block devices or `fallocate(PUNCH_HOLE)` for files.
- `zeroout`: uses `fallocate(ZERO_RANGE)` or hole punching for files, with regular-file extension when needed.
- `flock`: maps libext2fs flock flags to Unix `flock`.

## Integration
Exports `unix_io_manager` for path-based opening and `unixfd_io_manager` for existing file descriptors. Also supplies portable wrappers `ext2fs_open_file`, `ext2fs_stat`, and `ext2fs_fstat`.

## Risks / Notes
- Error handlers can be called during raw I/O and deferred cache flush failures.
- Direct-I/O alignment and bounce-buffer paths are central to correctness on block devices.
- `CHANNEL_FLAGS_NODISCARD` and `CHANNEL_FLAGS_NOZEROOUT` cache unsupported operations after `EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/unix_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/unlink.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/unlink.c

## Purpose
Removes a directory entry from an ext filesystem directory.

## Main Behavior
- `ext2fs_unlink()` validates writable filesystem state and requires either a name or inode.
- Iterates the target directory with `DIRENT_FLAG_INCLUDE_EMPTY`.
- `unlink_proc()` matches by name length/content and optionally inode unless `EXT2FS_UNLINK_FORCE` is set.
- If the matched entry is not first in the block, it merges the entry into the previous record by extending `prev->rec_len`; otherwise it clears `dirent->inode`.

## Integration
Uses `ext2fs_dir_iterate()` and returns `DIRENT_CHANGED | DIRENT_ABORT` once the entry is removed.

## Risks / Notes
Returns `EXT2_ET_DIR_NO_SPACE` when no matching entry is found, reusing an existing error code for “not removed”.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/unlink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/utf8n.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/utf8n.h

## Purpose
Declares the userspace UTF-8 normalization interface copied from Linux kernel logic so e2fsprogs hashes and validates casefolded names consistently with ext4.

## API Surface
- Unicode version helpers: `UNICODE_AGE`, `utf8version_is_supported()`, `utf8version_latest()`.
- Normalization data lookup: `utf8nfdi()` and `utf8nfdicf()`.
- Age checks: `utf8agemax/min()` and length-bounded variants.
- Normalized length checks: `utf8len()` and `utf8nlen()`.
- Streaming normalization cursor: `struct utf8cursor`, `utf8cursor()`, `utf8ncursor()`, and `utf8byte()`.

## Integration
Used by ext4 encoding/casefold support where userspace tools must match kernel normalization and hashing semantics.

## Risks / Notes
The header is only declarations and shared data-contract definitions; correctness depends on the generated/table implementation matching kernel behavior.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/utf8n.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/valid_blk.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/valid_blk.c

## Purpose
Determines whether an inode’s `i_block[]` entries should be interpreted as block mappings.

## Main Behavior
- Only directories, regular files, and symlinks can have valid block entries.
- Fast symlinks are detected specially because their target is stored inside `i_block[]`.
- Symlinks with EA blocks use size and `i_block[1]` heuristics because `i_blocks` includes EA storage.
- Inodes with `EXT4_INLINE_DATA_FL` are treated as not having valid external block entries.

## Integration
Provides `ext2fs_inode_has_valid_blocks2(fs, inode)` and compatibility wrapper `ext2fs_inode_has_valid_blocks(inode)`.

## Risks / Notes
The symlink-with-EA case is heuristic by necessity; it distinguishes likely fast symlinks from real block-backed symlinks.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/valid_blk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/version.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/version.c

## Purpose
Exposes libext2fs version and release date.

## Main Behavior
- Uses `E2FSPROGS_VERSION` and `E2FSPROGS_DATE` from `../../version.h`.
- `ext2fs_parse_version_string()` parses digits and at most one dot into a compact integer form, stopping at non-version characters.
- `ext2fs_get_library_version()` optionally returns version/date strings and returns the parsed version number.

## Integration
Used by tools or callers needing the runtime library version.

## Risks / Notes
The parser intentionally ignores suffixes after the numeric major/minor portion.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/version.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/windows_io.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/windows_io.c

## Purpose
Windows implementation of the libext2fs I/O manager using Win32 handles and a small block cache.

## Main Behavior
- Opens devices through `CreateFile`, with fake DOS device aliases for raw NT-style names that need `\\.\...` access.
- Wraps the handle with `_open_osfhandle` for stat/close compatibility.
- Implements raw block reads/writes using `SetFilePointerEx`, `ReadFile`, and `WriteFile`.
- Uses bounce buffers for unaligned or forced-buffered I/O.
- Maintains an 8-entry dirty block cache similar to the Unix manager.
- Supports blocksize changes by flushing and reallocating cache buffers.

## Supported Operations
- Reads, writes, flush, stats, and `offset` option.
- `zeroout` can extend regular files but ultimately reports unimplemented for actual zeroing.
- Readahead, byte writes, discard, and block-device zeroout are not supported.

## Integration
Exports `windows_io_manager` and Windows versions of `ext2fs_open_file`, `ext2fs_stat`, and `ext2fs_fstat`.

## Risks / Notes
- Error values come from `GetLastError()` in raw Win32 paths and `errno` in C runtime paths.
- Fake DOS device cleanup is required on close/open failure.
- The Windows manager is less feature-complete than Unix, especially for discard/zeroout.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/windows_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/write_bb_file.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/write_bb_file.c

## Purpose
Writes an ext2 bad-block list to a `FILE *`.

## Main Behavior
- Starts a badblocks iterator with `ext2fs_badblocks_list_iterate_begin()`.
- Prints each block number as an unsigned decimal line.
- Ends the iterator and returns success.

## Integration
Provides `ext2fs_write_bb_FILE()`, matching the plain text format consumed by e2fsprogs bad-block list readers.

## Risks / Notes
Uses legacy `blk_t` and `%u`, so it is tied to the classic 32-bit badblocks-list format.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/write_bb_file.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/Makefile.in -->
# File Research: sources/local-fs/e2fsprogs/misc/Makefile.in

## Purpose
Autoconf makefile template for building, profiling, statically linking, installing, uninstalling, cleaning, and dependency-tracking the `misc` e2fsprogs tools.

## Build Contents
Defines programs including:
- System/root tools: `mke2fs`, `badblocks`, `tune2fs`, `dumpe2fs`, `blkid`, `logsave`, `e2image`, `fsck`, `e2undo`.
- User tools: `chattr`, `lsattr`, `uuidgen`, `filefrag`, `e2freefrag`, optional `uuidd`, `e4defrag`, `e4crypt`, `fuse2fs`.
- Test/helper/fuzz targets: `base_device`, `check_fuzzer`, `e2fuzz`, `tst_ismounted`.

## Rules
- Builds normal, profiled, and selected static variants.
- Generates `mke2fs.conf` and `default_profile.c`.
- Builds shared journal/recovery/revoke objects from `debugfs` and `e2fsck` sources with special include flags.
- Generates manpages from `.in` templates via substitution.

## Install Behavior
- Installs root/sbin, sbin, bin, libdir helpers, man1/man5/man8 pages.
- Creates compatibility links such as `mkfs.ext2/3/4`, `e2label`, `e2mmpstatus`, and optionally `findfs`.
- Installs or updates `mke2fs.conf`, preserving old/custom configurations when needed.

## Risks / Notes
- Dependency lines are generated and form the trailing section.
- Optional program inclusion is controlled by configure substitutions such as `@BLKID_CMT@`, `@FUSE_CMT@`, `@UUIDD_CMT@`, and Linux-specific comments.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/badblocks.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/badblocks.8.in

## Purpose
Manual page template for `badblocks(8)`.

## Covered Behavior
Documents:
- Device range arguments: `device`, optional `last_block`, optional `first_block`.
- Safety warning to prefer `e2fsck -c` or `mke2fs -c` so block size matches the filesystem.
- Read-only, destructive write, and non-destructive read-write modes.
- Existing bad-block input, output file format, progress, verbosity, delay factor, max bad-block abort, repeat-until-clean passes, direct-I/O bypass, and internal `-X`.

## Integration
Generated by `misc/Makefile.in` into `badblocks.8`.

## Risks / Notes
The manpage explicitly warns that `-w` erases data and that `-e` can produce incomplete bad-block output.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/badblocks.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/badblocks.c -->
# File Research: sources/local-fs/e2fsprogs/misc/badblocks.c

## Purpose
Implements the `badblocks` scanner for finding bad sectors/blocks on a device.

## Main Modes
- `test_ro()`: read-only scan, optionally comparing against a supplied pattern.
- `test_rw()`: destructive write-mode scan using default or user-specified patterns, then reads back and compares.
- `test_nd()`: non-destructive read-write scan that saves original data, writes test data, verifies it, then restores saved data, including signal cleanup restoration.

## Support Logic
- Maintains an in-memory ext2 badblocks list and emits new bad blocks through `bb_output()`.
- Skips known-bad blocks loaded from `-i`.
- Supports progress reporting via alarm-driven status updates.
- Uses aligned buffers and toggles `O_DIRECT` when buffer, size, and offset alignment permit unless `-B` requests buffered I/O.
- `check_mount()` refuses unsafe write tests on mounted or busy devices unless forced/internal bypass options allow it.

## CLI Contract
Parses block size, blocks-at-once, delay factor, max bad blocks, input/output files, clean-pass repetition, test patterns, verbose/progress flags, destructive/non-destructive mode, force, buffered I/O, and internal exclusive-check bypass.

## Integration
Uses libext2fs helpers for device sizing, mount checks, syncing, badblocks list creation, and large seeks. Its output format is consumed by `e2fsck` and `mke2fs`.

## Risks / Notes
- Classic badblocks format is limited to 32-bit block numbers.
- Signal handling in non-destructive mode is important because it restores saved blocks before exiting.
- Incorrect block size makes output unusable for filesystem-level bad block marking.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/badblocks.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/base_device.c -->
# File Research: sources/local-fs/e2fsprogs/misc/base_device.c

## Purpose
Derives a “base device” name from a partition path so fsck scheduling can avoid running multiple checks against partitions on the same physical disk concurrently.

## Main Behavior
Recognizes and truncates:
- `/dev/md*` to the md base.
- DAC960-style `/dev/rd/cXdY`.
- `/dev/hd*` and `/dev/sd*` disk names.
- Old devfs `ide/.../hostN/busN/targetN/lunN` and `scsi/...` hierarchy.
- devfs `/dev/discs/discN` and `/dev/disks/diskN`.

## Integration
Used by fsck logic through `fsck.h`. A `DEBUG` main can run test vectors from stdin.

## Risks / Notes
Returns `NULL` when it cannot confidently parse the device path.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/base_device.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/blkid.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/blkid.8.in

## Purpose
Manual page template for the e2fsprogs `blkid(8)` command-line interface.

## Covered Behavior
Documents:
- Cache file read/write options.
- Cache garbage collection.
- Device lookup by `NAME=value` token.
- Single best lookup mode with priority ordering.
- Output formats: `full`, `value`, `list`, and `device`.
- Tag filtering and explicit device probing.
- Return codes: success, no match/no identifiable devices, usage/other errors.

## Integration
Generated by `misc/Makefile.in` into `blkid.8`.

## Risks / Notes
This documents the older e2fsprogs/libblkid interface and cache path `/etc/blkid.tab`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/blkid.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/blkid.c -->
# File Research: sources/local-fs/e2fsprogs/misc/blkid.c

## Purpose
Implements the `blkid` CLI over `libblkid`.

## Main Behavior
- Loads a blkid cache with optional read/write cache paths.
- Can garbage-collect the cache.
- Probes all devices, probes specified devices, or looks up the first matching token.
- Filters output by requested tags.
- Supports output formats: full `NAME="value"` records, value-only, device-only, and pretty list.

## Output Helpers
- `safe_print()` escapes non-printable bytes and double quotes.
- Pretty list mode gathers device name, filesystem type, label, UUID, and mount status via `ext2fs_check_mount_point()`.
- Terminal width is detected via ioctl or `COLUMNS`.

## Integration
Uses `blkid_get_cache`, `blkid_probe_all`, `blkid_verify`, `blkid_get_dev`, `blkid_find_dev_with_tag`, and tag iteration APIs.

## Risks / Notes
Device/tag arrays are fixed at 128 entries; too many `-s` tags is detected, but device overflow is not explicitly guarded.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/blkid.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/chattr.1.in -->
# File Research: sources/local-fs/e2fsprogs/misc/chattr.1.in

## Purpose
Manual page template for `chattr(1)`.

## Covered Behavior
Documents:
- Symbolic modes `+`, `-`, and `=`.
- Mutable flags such as append-only, no-atime, compressed, no-COW, no-dump, dirsync, extents, casefold, immutable, journal-data, project inheritance, sync, topdir, and DAX.
- Read-only displayed flags such as encrypted, indexed directory, inline data, and verity.
- Recursive, verbose, force, version/generation, and project ID options.

## Integration
Generated by `misc/Makefile.in` into `chattr.1`; behavior corresponds to `misc/chattr.c` and e2p flag helpers.

## Risks / Notes
The document calls out filesystem-specific support differences and flags ignored by ext2/ext3/ext4 kernels.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/chattr.1.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/chattr.c -->
# File Research: sources/local-fs/e2fsprogs/misc/chattr.c

## Purpose
Implements `chattr`, changing Linux filesystem inode flags, generation/version, and project ID.

## Main Behavior
- Parses `+flags`, `-flags`, and `=flags`, plus `-R`, `-V`, `-f`, `-v version`, and `-p project`.
- Maps option letters to ext filesystem flags through `flags_array`.
- `change_attributes()` reads current flags, applies set/add/remove semantics, clears `EXT2_DIRSYNC_FL` on non-directories, writes flags, and optionally writes version/project.
- Recursion uses `iterate_on_dir()` and skips `.`/`..`.

## Integration
Uses e2p helpers `fgetflags`, `fsetflags`, `fsetversion`, `fsetproject`, `print_flags`, and directory iteration support.

## Risks / Notes
- `=` is mutually exclusive with `+` and `-`.
- The same flag cannot be both added and removed.
- Symlink handling relies on `lstat`, but flag operations are path-based through e2p helpers.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/chattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/check_fuzzer.c -->
# File Research: sources/local-fs/e2fsprogs/misc/check_fuzzer.c

## Purpose
Small regression helper for quickly exercising libext2fs paths on a filesystem image to find UBSAN/fuzzer-triggered problems.

## Main Behavior
- Opens the supplied filesystem/device with `ext2fs_open()` and `unix_io_manager`.
- Reads inode and block bitmaps.
- Calls `ext2fs_check_directory()` on the root inode.
- Reports errors with `com_err` and exits nonzero on failure.

## Integration
Built by `misc/Makefile.in` as `check_fuzzer`.

## Risks / Notes
It is intentionally narrow and diagnostic; it does not perform repair.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/check_fuzzer.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/create_inode.c -->
# File Research: sources/local-fs/e2fsprogs/misc/create_inode.c

## Purpose
Creates and populates ext filesystem inodes from host files, directories, special files, symlinks, hardlinks, tar archives, xattrs, sparse extents, and selected file flags. Used by mke2fs population paths.

## Main Creation Helpers
- `add_link()` links an existing inode into a directory and increments link count.
- `set_inode_extra()` copies uid, gid, permissions, and atime/ctime/mtime, clamping fake-time future timestamps.
- `set_inode_xattr()` copies host extended attributes into ext2fs xattr handles when supported.
- `do_mknod_internal()` creates character/block devices, FIFOs, and sockets.
- `do_symlink_internal()` creates symlinks, expanding the parent directory on `EXT2_ET_DIR_NO_SPACE`.
- `do_mkdir_internal()` creates directories with copied flag subset.
- `do_write_internal()` creates a regular file inode, initializes inline-data/extents when appropriate, applies copyable flags, and copies content.

## File Copy Behavior
- Uses 64 KiB buffers.
- Attempts sparse-aware copy with `SEEK_DATA/SEEK_HOLE`, then FIEMAP, then full scan fallback.
- Skips all-zero filesystem blocks instead of writing them.
- When fs-verity support is available and requested, copies Merkle tree, descriptor/signature metadata, records descriptor size, resets logical file size, and sets `EXT4_VERITY_FL`.

## Population Flow
`__populate_fs()`:
- Changes into the source directory, scans entries alphabetically, and recursively creates target entries.
- Preserves hardlinks by tracking `(src_dev, src_ino) -> dst_ino`.
- Handles regular files, directories, symlinks, devices, FIFOs, sockets, and ignores unknown types.
- Copies inode metadata and xattrs after creation.
- Supports callbacks before and after inode creation.

`populate_fs3()`:
- Requires a writable filesystem.
- Initializes hardlink/path tracking and link insertion mode.
- Treats `"-"` or a regular source file as a tar archive through `__populate_fs_from_tar()`.
- Otherwise copies xattrs on the root and recursively populates from a directory.
- `populate_fs2()` and `populate_fs()` are compatibility wrappers.

## Integration
Declared by `create_inode.h`; used by mke2fs image population. Also cooperates with `create_inode_libarchive` for tar input.

## Risks / Notes
- The recursive walker changes process working directory.
- Hardlink tracking lifetime is scoped to a single population run.
- `COPY_FLAGS_MASK` deliberately limits which host flags are copied.
- Path strings are grown manually through `path_append()`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/create_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/create_inode.h -->
# File Research: sources/local-fs/e2fsprogs/misc/create_inode.h

## Purpose
Declares the filesystem population and inode creation API used by mke2fs-related code.

## Types / Flags
- `struct hdlink_s` and `struct hdlinks_s` track source hardlinks mapped to destination inode numbers.
- `struct file_info` stores a growable target path buffer.
- `POPULATE_FS_NO_COPY_XATTRS` disables xattr copying.
- `POPULATE_FS_LINK_APPEND` changes directory link insertion behavior.
- `struct fs_ops_callbacks` provides optional create/end-create hooks.

## API Surface
Declares:
- `populate_fs()`, `populate_fs2()`, `populate_fs3()`.
- Internal-style creators for mknod, symlink, mkdir, and file copy.
- `add_link()` for hardlink creation.
- `set_inode_extra()` for uid/gid/mode/time metadata.

## Integration
Implemented primarily by `create_inode.c`, with tar population delegated through libarchive support.

## Risks / Notes
The header exposes helpers named “internal” to other misc code, so callers need to honor expected cwd/root/path semantics.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/create_inode.h -->