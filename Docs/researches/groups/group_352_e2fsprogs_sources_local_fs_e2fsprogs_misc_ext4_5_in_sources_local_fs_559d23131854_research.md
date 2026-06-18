# Group Research: group_352_e2fsprogs_sources_local_fs_e2fsprogs_misc_ext4_5_in_sources_local_fs_559d23131854

Scope: `Docs/research_subset_a.md`; source tree: `sources/local-fs/e2fsprogs`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/ext4.5.in -->
# File Research: sources/local-fs/e2fsprogs/misc/ext4.5.in

## Purpose
Generated nroff manpage source for `ext2`, `ext3`, and `ext4`, describing filesystem identity, feature flags, mount options, file attributes, and kernel feature support.

## Key Elements
Documents ext-family compatibility and feature evolution. Feature sections cover allocation/layout features, metadata checksums, journals, quotas, encryption, casefolding, verity, MMP, orphan files, project IDs, stable inodes, sparse superblocks, and online resize support.

Mount option sections separate ext2, ext3, and ext4 behavior. ext2 covers ACLs, `bsddf`/`minixdf`, errors behavior, group inheritance, quotas, `sb=`, reserved block user/group, and xattrs. ext3 adds journal device/path, recovery suppression, data journaling modes, barriers, commit interval, journaled quotas, and data error policy. ext4 adds journal checksums, async commit, delayed allocation, inode readahead, RAID stripe tuning, batching, discard, block validity, DIO read locking, directory size limits, inode versioning, mbcache control, and project quotas.

## Dependencies
Uses manpage substitution tokens such as `@E2FSPROGS_VERSION@`, references e2fsprogs tools including `mke2fs`, `e2fsck`, `tune2fs`, `dumpe2fs`, `debugfs`, `mount`, and `chattr`.

## Behavior/Risks
Documentation-only file, but operationally important because it records compatibility expectations and warns about risky options such as `norecovery`, writeback data mode, disabled barriers, bigalloc maturity, and unsupported/experimental feature combinations.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/ext4.5.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/filefrag.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/filefrag.8.in

## Purpose
Manpage source for `filefrag`, a utility that reports file fragmentation.

## Key Elements
Explains that `filefrag` first uses FIEMAP for extent mapping and falls back to FIBMAP if FIEMAP is unsupported. Documents options for forcing FIBMAP, choosing display block size, printing extent format, querying ext4 extent status cache, preloading cache, syncing before mapping, verbose output, version/flag display, xattr mapping, and hexadecimal extent output.

## Dependencies
References Linux FIEMAP and FIBMAP ioctls and ext4-specific extent status cache behavior.

## Behavior/Risks
Warns implicitly through option descriptions that some modes are kernel- and filesystem-specific. `-B` and FIBMAP behavior can require privileges in the implementation.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/filefrag.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/filefrag.c -->
# File Research: sources/local-fs/e2fsprogs/misc/filefrag.c

## Purpose
Implements `filefrag`, reporting extent count and optional detailed extent layout for files.

## Key Elements
Provides a non-Linux stub that exits unsupported. On Linux, parses `-Bb::eEkPsvVxX`, opens each file, determines filesystem block size via `FIGETBSZ`/`fstatfs`, and calculates logical/physical display widths.

Primary path uses `FS_IOC_FIEMAP` or ext4 `EXT4_IOC_GET_ES_CACHE`, printing known FIEMAP flags and counting discontinuities as extents. Fallback path uses `FIBMAP`, with extra accounting for ext2/ext3 indirect blocks and optional forced extent-style output. Supports sync-before-map, xattr map requests, extent cache preload/query, 1K or custom output block size, and hex output.

## Dependencies
Uses Linux ioctls `FS_IOC_FIEMAP`, `FIBMAP`, `FIGETBSZ`, ext4 flags/ioctls from e2fsprogs headers, `statfs`, `fstat`, `open64`/`fstat64` where available, and e2fsprogs helpers such as `ext2fs_log10_u64`.

## Behavior/Risks
FIBMAP may require root and may be unsupported; FIEMAP can reject incompatible flags. Ext4 extent status cache options are explicitly ext4/kernel dependent. The program returns the negated first negative errno encountered across files.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/filefrag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/findfs.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/findfs.8.in

## Purpose
Manpage source for `findfs`, which locates a filesystem device by label or UUID.

## Key Elements
Documents `findfs LABEL=<label>` and `findfs UUID=<uuid>`, stating that matching device names are printed to stdout.

## Dependencies
Documentation references e2fsprogs packaging and `fsck(8)`.

## Behavior/Risks
Documentation-only. The real lookup behavior depends on system disk probing and label/UUID uniqueness.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/findfs.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/findsuper.c -->
# File Research: sources/local-fs/e2fsprogs/misc/findsuper.c

## Purpose
Standalone raw-device scanner for finding ext2/ext-family superblock signatures.

## Key Elements
Parses optional `-j`, device, skip-byte increment, and starting kilobyte offset. Scans by seeking and reading 512-byte chunks, checking `EXT2_SUPER_MAGIC`, validating basic superblock fields, and printing byte offsets, inferred filesystem start/end, block count, block size, group number, timestamp, UUID prefix, and label.

Tracks duplicate UUID/group-zero superblocks as likely journal copies and hides them unless `-j` is requested. Includes an adaptive progress meter based on elapsed wall time.

## Dependencies
Uses libext2fs superblock structures/helpers, raw `open`, `lseek64`, `read`, NLS support, and ext2 timestamp/string macros.

## Behavior/Risks
Header comments call it a hack and discourage installation. It scans raw devices linearly, can be slow, and only performs heuristic validity checks. Output inference depends on superblock fields and can misidentify journal copies or stale/corrupt metadata.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/findsuper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fsck.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/fsck.8.in

## Purpose
Manpage source for generic `fsck`, the Linux filesystem-check dispatcher.

## Key Elements
Explains that `fsck` is a front-end for filesystem-specific checkers named `fsck.<fstype>`. Documents serial and parallel checking, `/etc/fstab` traversal, pass-number ordering, root filesystem handling, progress reporting, mounted-filesystem skipping, dry-run mode, type filtering, and pass-through filesystem-specific options.

Defines exit status bit meanings and notes that multiple filesystem results are ORed. Documents environment variables `FSCK_FORCE_ALL_PARALLEL`, `FSCK_MAX_INST`, `PATH`, and `FSTAB_FILE`.

## Dependencies
References `/etc/fstab`, checker search paths, e2fsck and many filesystem-specific fsck tools.

## Behavior/Risks
Warns that arbitrary fs-specific option forwarding is intentionally limited and that parallel interactive checks can be unsafe. Also calls out risk of checking root in parallel with other filesystems.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fsck.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fsck.c -->
# File Research: sources/local-fs/e2fsprogs/misc/fsck.c

## Purpose
Implements generic `fsck`, a parallelizing dispatcher for filesystem-specific checkers.

## Key Elements
Loads filesystem entries from `FSTAB_FILE` or `/etc/fstab`, parsing escaped fields and resolving labels/UUIDs through blkid. Tracks entries as `struct fs_info` and child checker processes as `struct fsck_instance`.

Parses fsck options, including `-A`, `-C`, `-M`, `-N`, `-P`, `-R`, `-T`, `-V`, `-s`, `-t`, `--`, and device arguments. Compiles `-t` filters into normal type matches and `opts=` option filters, including historical `loop` handling.

Finds checker binaries along built-in fsck paths plus `PATH`, spawns `fsck.<type>` children, manages progress ownership for ext-family checkers via `-C` and `SIGUSR1`, and waits/ORs exit statuses. `check_all` handles pass-number ordering, root-first behavior, mounted-skip mode, same-base-device serialization, `FSCK_FORCE_ALL_PARALLEL`, and `FSCK_MAX_INST`.

## Dependencies
Uses blkid, e2fsprogs support helpers `get_devname` and `base_device`, NLS/com_err setup, `is_mounted`, POSIX fork/exec/wait/signal APIs, and filesystem checker executables.

## Behavior/Risks
Uses fixed `MAX_DEVICES` and `MAX_ARGS` arrays. Parallelism is conservative unless forced, but base-device detection is heuristic and unknown devices serialize. Cancellation sends SIGTERM to outstanding children. The option parser is hand-written, so fs-specific option forwarding remains intentionally simple.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fsck.h -->
# File Research: sources/local-fs/e2fsprogs/misc/fsck.h

## Purpose
Shared declarations and constants for the fsck front-end and mount-detection helper.

## Key Elements
Defines compatibility macros, default filesystem type `ext2`, array limits, fsck exit status bit constants, `struct fs_info`, `struct fsck_instance`, and flags for completed/progress-owning checks.

Declares `base_device`, `identify_fs`, and `is_mounted`.

## Dependencies
Requires standard `time.h`; used by `fsck.c` and `ismounted.c`.

## Behavior/Risks
Header centralizes hard-coded limits and status semantics. No include guard is present in this file.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fsck.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fsmap.h -->
# File Research: sources/local-fs/e2fsprogs/misc/fsmap.h

## Purpose
Compatibility header defining `FS_IOC_GETFSMAP` userspace structures and constants when the platform headers do not provide them.

## Key Elements
Defines `struct fsmap`, `struct fsmap_head`, `fsmap_sizeof`, and `fsmap_advance`. Provides header/output flags, record flags for preallocation/attribute fork/extent map/shared/special owner/last, special owner helpers, and the ioctl number.

## Dependencies
Assumes Linux-style integer types such as `__u32` and `__u64` plus ioctl macros are already available from including context.

## Behavior/Risks
Definitions are guarded by `#ifndef FS_IOC_GETFSMAP`, so system headers win when available. This is a compatibility surface for code that needs stable fsmap ABI definitions across older build environments.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fuse2fs.1.in -->
# File Research: sources/local-fs/e2fsprogs/misc/fuse2fs.1.in

## Purpose
Manpage source for `fuse2fs`, a FUSE client for ext2/ext3/ext4 filesystems.

## Key Elements
Documents mounting a device/image at a mountpoint with options. Lists read-only/read-write, `bsddf`/`minixdf`, ACLs, cache size, direct I/O, dirsync, errors behavior, fakeroot, debug, kernel-like behavior, lockfile, default-option suppression, and journal recovery suppression.

Also documents general FUSE foreground/debug/single-thread options and points users to `mount.fuse` or `--helpfull`.

## Dependencies
References FUSE, ext4, e2fsck, and mount.fuse.

## Behavior/Risks
Manpage describes write-capable behavior, but the implementation has important feature and journaling limitations that users must pair with e2fsck discipline.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fuse2fs.1.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fuse2fs.c -->
# File Research: sources/local-fs/e2fsprogs/misc/fuse2fs.c

## Purpose
Implements `fuse2fs`, a FUSE server that mounts ext2/ext3/ext4 filesystems through libext2fs.

## Key Elements
Defines the main `struct fuse2fs` context, per-open file handles, operation state, debug/log/timing helpers, timestamp encoding/decoding helpers, and a global mutex around libext2fs operations. Opens block devices/images with exclusive locking/retry behavior, optional lockfile, regular-file flocking, cache sizing, journal replay or `norecovery` handling, support checks, MMP background updates, and clean unmount bookkeeping.

Implements FUSE operations for init/destroy, getattr/readlink, mknod/mkdir/create, unlink/rmdir, symlink, rename, hard link, chmod/chown, truncate, open/read/write/release/fsync/statfs, xattrs, readdir, access, utimens, bmap, ioctls, FITRIM, shutdown, and fallocate where supported. Namespace operations use libext2fs allocation/link/unlink APIs and update ctime/mtime/atime, link counts, generation numbers, extra inode size, directory checksums, default ACL propagation, and optional dirsync flushing.

Option parsing handles `ro/rw`, `fakeroot`, debug, `norecovery/noload`, offset, OOM score, kernel-like mount behavior, direct I/O, ACLs, lockfile, timing, cache size, dirsync, and errors behavior. It computes default libfuse args including subtype/fsname/cache options and limits threads because libext2fs work is serialized.

## Dependencies
Depends heavily on libfuse, libext2fs internals, e2p, uuid, com_err, pthreads, e2fsprogs bthread/thread helpers, Linux filesystem ioctls/xattrs/fallocate/FITRIM where available, and optional NLS.

## Behavior/Risks
Rejects unsupported ext4 features including quota, verity, encryption, and casefolding. Shared-block filesystems and bigalloc with cluster ratio greater than one force read-only mode. Write mode warns that fuse2fs does not use the journal, so ungraceful unmount can cause corruption or data loss.

Error translation maps libext2fs failures to errno values, records first/last error data in the superblock, marks the filesystem erroneous, flushes metadata, and follows `errors=continue|remount-ro|panic`. Permission enforcement is partly internal unless `kernel` mode delegates to FUSE/kernel default permissions; group membership handling is best-effort. The file is large and stateful, with many operations relying on careful lock, inode, bitmap, and flush ordering.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/fuse2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/ismounted.c -->
# File Research: sources/local-fs/e2fsprogs/misc/ismounted.c

## Purpose
Provides `is_mounted`, used to decide whether a filesystem/device is currently mounted.

## Key Elements
Parses mount-table-like files with small local word parsing helpers. `check_mntent_file` opens `/proc/mounts` or `/etc/mtab`, compares requested path by literal device name, block-device `st_rdev`, or non-block `st_dev/st_ino`, and validates matching mountpoint entries to avoid stale mtab data. Includes root-device fallback for `/dev/root` style cases.

`is_mounted` checks `/proc/mounts` first on Linux, then `/etc/mtab`.

## Dependencies
Uses `setmntent`/`endmntent` when available, POSIX `stat`, mount table formats, and `fsck.h`.

## Behavior/Risks
If mount table files cannot be opened or parsed, callers receive “not mounted” behavior. Some logic is disabled for GNU/Hurd due to device stat limitations. Commented paranoia reflects historically stale `/etc/mtab` issues.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/ismounted.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/logsave.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/logsave.8.in

## Purpose
Manpage source for `logsave`, which captures command or stdin output to a logfile while also showing it on the console.

## Key Elements
Documents `logsave [-asv] logfile cmd_prog [...]`, append mode, skip mode for control-A/control-B bracketed progress text, verbose console output, and stdin mode using `-` as the command.

## Dependencies
References `fsck(8)` and early boot logging use cases.

## Behavior/Risks
Explains deferred logging when the logfile directory is unavailable, making it relevant for boot sequences before `/var` is mounted.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/logsave.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/logsave.c -->
# File Research: sources/local-fs/e2fsprogs/misc/logsave.c

## Purpose
Implements `logsave`, running a command or copying stdin while saving output to a logfile that may not yet be writable.

## Key Elements
Parses `-a`, `-s`, and `-v`. Opens the target log for append or truncate; if opening fails, buffers output in memory. Writes a header with command/stdin and timestamp, then either forks/execs a child with stdout/stderr piped back or reads stdin directly.

`send_output` writes to console, log, or both, with skip-mode filtering so control-A/control-B bracketed text can appear on console but be omitted from the log. After command completion, writes a footer timestamp. If output was buffered because the log was unavailable, forks a background session that retries opening the log and writes buffered data later.

## Dependencies
Uses POSIX pipe/fork/execvp/waitpid, signal forwarding, read/write/open, and time APIs.

## Behavior/Risks
Buffers deferred log data entirely in memory. Background retry loops until the log can be opened. Signal handlers forward SIGINT/SIGTERM to the child. Output multiplexing is byte-stream based and intentionally simple for boot-time use.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/logsave.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/lsattr.1.in -->
# File Research: sources/local-fs/e2fsprogs/misc/lsattr.1.in

## Purpose
Manpage source for `lsattr`, which lists ext2/ext3/ext4 file attributes.

## Key Elements
Documents recursive listing, version display, all-files listing, directory-as-file handling, long option names, project number display, and generation/version display.

## Dependencies
References `chattr(1)` for attribute meanings and e2fsprogs availability.

## Behavior/Risks
Documentation-only. It intentionally delegates semantic explanation of individual attribute flags to `chattr`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/lsattr.1.in -->