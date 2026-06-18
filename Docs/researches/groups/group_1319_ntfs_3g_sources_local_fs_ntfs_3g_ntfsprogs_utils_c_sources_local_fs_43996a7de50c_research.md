# Group Research: group_1319_ntfs_3g_sources_local_fs_ntfs_3g_ntfsprogs_utils_c_sources_local_fs_43996a7de50c

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/ntfs-3g`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/utils.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/utils.c

## Purpose

Shared utility implementation for NTFS command-line tools. It wraps libntfs-3g primitives with ntfsprogs-compatible helpers for locale setup, device validation, volume mounting diagnostics, size/range parsing, attribute lookup, pathname reconstruction, allocation bitmap checks, metadata classification, memory dumping, and MFT iteration.

## Main Responsibilities

- Provides user-facing diagnostic text for invalid, corrupt, hibernated, busy, dirty, journal-unclean, and FakeRAID-like NTFS mount failures.
- Validates a target device/path before tool use, including existence and mounted-state checks unless forced.
- Mounts NTFS volumes with ntfsprogs-style safety behavior over libntfs-3g.
- Parses numeric size and range arguments with optional decimal suffix scaling.
- Searches raw MFT records and inode-backed records for NTFS attributes.
- Reconstructs an inode path by walking parent `FILE_NAME` attributes up to `$Root`.
- Maps NTFS attribute records to printable attribute type/name strings.
- Tests cluster and MFT-record allocation status through cached reads of `$Bitmap` and `$MFT/$BITMAP`.
- Identifies NTFS metadata files by MFT number, base record, and parent metadata location.
- Iterates MFT records according to filter flags such as in-use, file, directory, metadata, and base-record state.
- Supplies Windows-specific printf format/path compatibility helpers when built with `HAVE_WINDOWS_H`.

## Key Functions

- `utils_set_locale()` calls `setlocale(LC_ALL, "")`; logs and keeps the default locale if unavailable.
- `ntfs_mbstoucs_libntfscompat()` emulates linux-ntfs `ntfs_mbstoucs()` semantics, including support for caller-provided output buffers.
- `utils_valid_device()` checks null input, `stat()`, and mounted state through `ntfs_check_if_mounted()`.
- `utils_mount_volume()` validates then calls `ntfs_mount()`, translating common `errno` values into specific operator guidance; also rejects dirty volumes unless `NTFS_MNT_RECOVER` is present.
- `utils_parse_size()` uses `strtoll()` and accepts decimal `K/M/G/T` suffixes when `scale` is true.
- `utils_parse_range()` parses `start-finish`, defaulting missing start to `0` and missing finish to `LONG_MAX`.
- `find_attribute()` and `find_first_attribute()` wrap `ntfs_attr_lookup()` with search context allocation/cleanup.
- `utils_inode_get_name()` walks `AT_FILE_NAME` parent references, converts UCS names to locale strings, and assembles a slash-separated path.
- `utils_attr_get_name()` converts attribute definition names and optional named-stream names into a caller buffer.
- `utils_cluster_in_use()` and `utils_mftrec_in_use()` use static 512-byte bitmap caches to avoid repeated small bitmap reads.
- `utils_is_metadata()` classifies core NTFS metadata and children of metadata files.
- `utils_dump_mem()` logs formatted hex/ascii memory dumps with optional color/indent flags.
- `mft_get_search_ctx()`, `mft_put_search_ctx()`, and `mft_next_record()` implement a reusable MFT scanner over allocated and unallocated records.
- `ntfs_utils_reformat()` rewrites `%ll*` printf formats to `%I64*` for older Windows C runtimes.
- `ntfs_utils_unix_path()` duplicates a path and converts `\` to `/`.

## Important Details and Edge Cases

- `utils_parse_size()` checks `errno == ERANGE` but does not clear `errno` before `strtoll()`, so stale `errno` can affect callers.
- Size suffix scaling is decimal thousands, not binary powers.
- `utils_inode_get_name()` caps parent walking at 20 path elements and may report overly deep directory structures.
- `utils_inode_get_name()` closes parent inodes it opens but deliberately does not close the original inode.
- `utils_attr_get_name()` returns `0` for unnamed attributes after writing the type and also for several error/truncation paths; callers cannot treat `0` as a simple failure without considering side effects.
- Bitmap allocation helpers use static caches and are not thread-local.
- `mft_next_record()` can synthesize an `ntfs_inode` for unused MFT records by reading raw `$MFT/$DATA`.
- `mft_next_record()` marks records as base/non-base using standard information and attribute list attributes, then optionally detects directories through `$I30` index roots.
- Dirty-volume handling is intentionally different from older libntfs behavior: libntfs-3g is considered capable of handling the dirty bit, but this wrapper still rejects it unless recover/force semantics are requested.

## Dependencies

- Internal NTFS headers: `utils.h`, `types.h`, `volume.h`, `debug.h`, `dir.h`, `logging.h`, `misc.h`.
- libntfs-3g operations: mount/unmount, inode open/close, attribute search/open/read, MFT record read, bitmap access, Unicode conversion.
- Platform headers selected through `config.h` feature macros.

## Role in Source Tree

This file is support infrastructure for `ntfsprogs` utilities. It is not the FUSE driver itself; it gives standalone NTFS utilities consistent parsing, traversal, mount validation, diagnostics, and record-scanning helpers.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/utils.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/utils.h

## Purpose

Public header for shared ntfsprogs utility functions implemented in `utils.c`. It exposes mount/device helpers, parsing helpers, metadata/bitmap inspection helpers, attribute search helpers, MFT scan context APIs, dump formatting flags, and Windows compatibility wrappers.

## Exposed Interfaces

- Diagnostic strings: `ntfs_bugs`, `ntfs_gpl`.
- General helpers: `utils_set_locale()`, `utils_parse_size()`, `utils_parse_range()`, `utils_inode_get_name()`, `utils_attr_get_name()`, `utils_cluster_in_use()`, `utils_mftrec_in_use()`, `utils_is_metadata()`, `utils_dump_mem()`.
- Attribute search: `find_attribute()`, `find_first_attribute()`.
- Device and volume: `utils_valid_device()`, `utils_mount_volume()`.
- MFT scanning: `struct mft_search_ctx`, `mft_get_search_ctx()`, `mft_put_search_ctx()`, `mft_next_record()`.
- Unicode compatibility: `ntfs_mbstoucs_libntfscompat()`.
- Inline attribute-name helper: `ntfs_attr_get_name(ATTR_RECORD *attr)` returns the in-record name pointer based on `name_offset`.

## Important Constants

- `FEMR_*` flags describe MFT search criteria and match state: in-use, not-in-use, file, directory, metadata, not-metadata, base-record, not-base-record, and all-records.
- `DM_*` flags control `utils_dump_mem()` formatting: ASCII divider visibility, indentation, and red/green/blue/bold terminal styling.
- `MAX_PATH` is defined to `1024` if missing.

## Windows-Specific Behavior

When `HAVE_WINDOWS_H` is defined:

- Declares `ntfs_utils_reformat()` and `ntfs_utils_unix_path()`.
- Defines macro wrappers around `ntfs_log_redirect`, `printf`, `fprintf`, and `vfprintf` to rewrite format strings before passing them to older Windows runtimes.
- `MAX_FMT` is `1536`, setting the scratch-buffer size for reformatted output.

## Dependencies

- Includes `config.h`, `types.h`, `layout.h`, and `volume.h`.
- Optionally includes `errno.h` and `stdarg.h`.

## Role in Source Tree

This is the ntfsprogs utility contract consumed by tools that need common NTFS parsing, inspection, and reporting behavior without duplicating libntfs-3g glue code.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/src/Makefile.am -->
# File Research: sources/local-fs/ntfs-3g/src/Makefile.am

## Purpose

Automake build definition for the NTFS-3G FUSE driver programs and probe helper in `src/`.

## Build Products

When `ENABLE_NTFS_3G` is true:

- Installs `ntfs-3g.probe` as a normal binary.
- Installs `ntfs-3g` and `lowntfs-3g` as root binaries.
- Installs man pages: `ntfs-3g.8` and `ntfs-3g.probe.8`.

## FUSE Selection

- If `FUSE_INTERNAL` is enabled, builds against bundled fuse-lite headers and `libfuse-lite.la`.
- Otherwise, uses `$(FUSE_MODULE_CFLAGS)` and `$(FUSE_MODULE_LIBS)` from external FUSE detection.

## Plugin Configuration

When plugins are not disabled:

- Defines plugin installation directory as `$(libdir)/ntfs-3g`.
- Adds `-DPLUGIN_DIR="$(plugindir)"` via `PLUGIN_CFLAGS`.
- Install hook creates the plugin directory.

## Program Definitions

- `ntfs-3g`: sources `ntfs-3g.c`, `ntfs-3g_common.c`; CFLAGS include `-DFUSE_USE_VERSION=26`, FUSE flags, libntfs-3g includes, plugin flags; links with `$(LIBDL)`, FUSE, and `libntfs-3g.la`.
- `lowntfs-3g`: sources `lowntfs-3g.c`, `ntfs-3g_common.c`; uses the same CFLAGS and LDADD pattern as `ntfs-3g`.
- `ntfs-3g.probe`: source `ntfs-3g.probe.c`; links only against `libntfs-3g.la`.

## Static Build Handling

If `REALLYSTATIC` is enabled, each program uses `$(AM_LDFLAGS) -all-static`.

## Install Hooks

- Runs `ldconfig` when `RUN_LDCONFIG` is true.
- If `ENABLE_MOUNT_HELPER` is true, creates `/sbin/mount.ntfs-3g` and `/sbin/mount.lowntfs-3g` symlinks plus matching manpage symlinks.
- Uninstall removes those helper symlinks.

## Role in Source Tree

This file wires the high-level and low-level NTFS-3G FUSE drivers into the autotools build, controlling whether they use bundled or external FUSE, whether reparse plugins are supported, and whether mount-helper compatibility symlinks are installed.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/src/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/src/lowntfs-3g.c -->
# File Research: sources/local-fs/ntfs-3g/src/lowntfs-3g.c

## Purpose

Implementation of the `lowntfs-3g` low-level FUSE NTFS driver. It maps FUSE low-level inode operations directly to libntfs-3g inode, attribute, directory, security, xattr, reparse-point, and volume APIs.

## High-Level Architecture

- Uses the FUSE low-level API through `fuse_lowlevel.h`.
- Maintains a global `ntfs_fuse_context_t *ctx` holding mount options, volume, permissions, security cache, streams/xattr mode, plugin state, and open-file state.
- Converts FUSE inode `1` to NTFS `$Root` with `INODE(ino)`.
- Tracks open descriptors through `struct open_file`, including close-time actions for compressed files, encrypted files, delayed mtime, reparse plugin handles, and ghost unlink handling.
- Supports optional reparse plugins unless `DISABLE_PLUGINS` is set.
- Derives permission/cache behavior from `LPERMSCONFIG`: `KERNELACLS`, `KERNELPERMS`, and `CACHEING`.

## Main Responsibilities

- Implements the FUSE operation table for lookup, getattr, readlink, opendir/readdir/releasedir, open/release, read/write, setattr, statfs, create, mknod, symlink, link, unlink, rename, mkdir/rmdir, fsync, bmap, ioctl, xattrs, access checks, init, and destroy.
- Converts NTFS metadata into POSIX-facing `struct stat` values, including ownership, mode, link count, timestamps, file size, blocks, special files, symlinks, and WSL reparse objects.
- Handles POSIX-like permission checks either in userspace or through kernel/FUSE depending on build configuration.
- Implements file creation with Windows name validation, security descriptor or inherited security ID allocation, special file creation, symlink creation, compression/encryption close-time handling, and parent timestamp updates.
- Implements unlink semantics for open files using hidden `.ghost-ntfs-3g-%020llu` hard links so data survives until the last release.
- Implements rename via link/remove sequences, including temporary backup names when replacing an existing destination.
- Exposes named NTFS data streams as extended attributes when configured.
- Exposes system NTFS metadata xattrs for ACLs, DOS names, attributes, EFS information, and timestamps.
- Starts the mount: parses options, checks existing mounts, builds absolute mount point, loads or creates FUSE support where needed, opens the NTFS volume, builds user/xattr mappings, registers internal plugins, mounts FUSE, enters the FUSE session loop, then tears down.

## Key Function Areas

- Initialization and volume setup:
  - `ntfs_fuse_init()` allocates default context values: caller uid/gid, Linux default streams interface as xattr, relative atime, silent permission handling, and recovery enabled.
  - `ntfs_open()` maps context options to `ntfs_mount()` flags, sets sync/compression/show-file/case behavior, reads free cluster/MFT state, and optionally removes `hiberfil.sys`.
  - `main()` parses command-line options, validates setuid/external FUSE constraints, handles FUSE module/device setup, opens the NTFS volume, builds security mappings, mounts FUSE, and runs `fuse_session_loop()`.

- FUSE operation registration:
  - `ntfs_3g_ops` binds all low-level callbacks.
  - `ntfs_init()` requests FUSE capabilities such as `DONT_MASK`, POSIX ACLs, big writes, and directory ioctl when available.

- Stat and lookup:
  - `ntfs_fuse_getstat()` converts NTFS inodes to POSIX `stat`, with handling for directories, regular files, Interix special files, reparse points, encrypted raw sizing, and owner/mode mapping.
  - `ntfs_fuse_lookup()` opens the parent directory, checks search permission when needed, resolves the multibyte name to an NTFS MFT reference, and fills a FUSE entry.

- Directory handling:
  - `ntfs_fuse_opendir()` creates a fill context and optionally opens plugin-backed reparse directories.
  - `ntfs_fuse_readdir()` builds a chained list of FUSE directory entry buffers on first read and drains it on subsequent reads.
  - `ntfs_fuse_filler()` converts NTFS UCS names, skips DOS-only names, applies platform filename length workarounds, assigns entry type hints, and consults plugins for reparse types.

- Data I/O:
  - `ntfs_fuse_open()` checks permissions, opens unnamed `$DATA`, denies writes to metadata MFT numbers below `FILE_first_user`, and marks close-time fixups.
  - `ntfs_fuse_read()` and `ntfs_fuse_write()` read/write unnamed data attributes or delegate reparse file I/O to plugins.
  - `ntfs_fuse_trunc()` denies truncating metadata files, handles compressed-file extension specially, updates archive/timestamps, and returns refreshed attributes.
  - `ntfs_fuse_release()` performs compressed close, EFS raw fixup, delayed mtime update, plugin release, ghost cleanup, and open-file list removal.

- Namespace mutations:
  - `ntfs_fuse_create()` centralizes file, directory, device, and symlink creation, security inheritance/allocation, parent cache update, and FUSE entry filling.
  - `ntfs_fuse_newlink()` creates hard links and updates parent/file timestamps.
  - `ntfs_fuse_rm()` removes entries, denies metadata and `$Extend` removal, checks sticky-directory rules, and creates ghost links for open files.
  - `ntfs_fuse_rename()` performs a non-atomic rename using link/remove; existing destinations are protected through `ntfs_fuse_rename_existing_dest()` and `ntfs_fuse_safe_rename()`.

- Reparse and special files:
  - Internal plugins register junction/symlink handlers for mount points, symlinks, and LX symlinks, plus WSL stat handlers for AF_UNIX, FIFO, character, and block tags.
  - Unsupported reparse tags are displayed as synthetic symlink text such as `unsupported reparse tag ...`.

- Extended attributes:
  - `xattr_namespace()` classifies user/system/security/trusted/open namespace names.
  - `fix_xattr_prefix()` maps Linux xattr names to NTFS named stream names, stripping `user.` or adding ntfs-3g internal prefixes as needed.
  - `ntfs_fuse_getxattr()`, `setxattr()`, `removexattr()`, and `listxattr()` handle both system xattrs and named stream xattrs, with permission checks and EFS raw sizing.
  - Some system xattrs, such as NTFS ACLs, attributes, EFS info, and timestamps, are explicitly not removable.

- Mount/FUSE plumbing:
  - Linux helpers inspect `/proc/filesystems`, attempt `/sbin/modprobe fuse`, create `/dev/fuse` if privileged, choose fuseblk for block devices, and add `blkdev,blksize=` options.
  - External FUSE builds reject setuid/setgid execution and deny unprivileged block-device mounting.
  - `setup_logging()` daemonizes unless `no_detach`, then logs version, canonicalized device, mount mode, label, NTFS version, command-line options, and FUSE options.

## Important Details and Edge Cases

- Rename is explicitly marked with `FIXME: Rename should be atomic`; the implementation is link/remove based and has recovery paths for existing destinations.
- Open-file unlink handling uses ghost hard links. Multiple opens of the same inode can create multiple ghost names.
- Directory reading caches the full result into chained buffers; rewind clears and rebuilds cached entries.
- Metadata writes/truncates/removes are denied for inodes below `FILE_first_user`.
- Creating or removing entries under `$Extend` is denied.
- `lowntfs-3g` can represent Interix and WSL special files and junctions/symlinks using reparse metadata and plugins.
- The default Linux streams interface is xattr; non-Linux defaults to no named-stream interface.
- `efs_raw` changes visible file and xattr sizes to include encryption padding and triggers close-time EFS attribute fixups.
- `bmap` only supports nonresident, uncompressed, unencrypted unnamed data.
- Cache invalidation for xattr-driven stat changes is conditional on external FUSE 2.8+ and caching builds.
- Startup may force read-only if libntfs-3g opened the volume read-only, then inserts `,ro` into FUSE options.
- `main()` ensures file descriptors 0, 1, and 2 are open before proceeding.

## Dependencies

- FUSE headers and APIs: high-level include plus low-level session, channel, option, reply, mount, signal, ioctl, and bmap interfaces.
- libntfs-3g headers and APIs: bitmap, attrib, inode, volume, directory, Unicode, index, NTFS time, security, reparse, EA, object ID, EFS, xattrs, ioctl, plugin, misc, and common mount-option code.
- Platform APIs: `stat`, `mknod`, `daemon`, `syslog`, `fork/exec/wait`, `sysconf`, xattr headers when available, and platform-specific stat timestamp fields.

## Role in Source Tree

This is the main low-level NTFS-3G FUSE driver executable. It sits beside the higher-level `ntfs-3g.c` variant and shares option parsing/common context code through `ntfs-3g_common.c`, but exposes a lower-level inode-centric FUSE implementation with explicit control over lookup entries, directory buffers, inode attributes, and operation replies.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/src/lowntfs-3g.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g.8.in -->
# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g.8.in

## Purpose

Manual page template for `ntfs-3g`, `mount -t ntfs-3g`, `lowntfs-3g`, and `mount -t lowntfs-3g`. Autotools substitutes `@VERSION@` to produce the installed `ntfs-3g.8` man page.

## Main Content

- Documents the driver as a third-generation read/write NTFS driver.
- Covers both `ntfs-3g` and `lowntfs-3g` invocation forms.
- Explains that the mounted volume can be a block device or an image file.
- Describes read/write support for files, directories, hard links, streams, sparse files, compressed files, symbolic links, devices, FIFOs, ownership, permissions, and POSIX ACLs.
- Calls out differences where relevant, especially lowntfs-specific `ignore_case` and the fact that `streams_interface=windows` is not possible with `lowntfs-3g`.

## Major Documentation Sections

- `NAME`: identifies `ntfs-3g` as the Third Generation Read/Write NTFS Driver.
- `SYNOPSIS`: gives direct and `mount -t` command forms for both driver variants.
- `DESCRIPTION`: summarizes supported NTFS features and driver variants.
- `Windows hibernation and fast restarting`: warns that Windows must be fully shut down before Linux writes to internal NTFS partitions and suggests `powercfg /h off`.
- `Access Handling and Security`: explains default ownership/permission behavior, `uid`, `gid`, masks, `permissions`, POSIX ACLs, and user mappings.
- `Windows Filename Compatibility`: explains NTFS namespaces and `windows_names`.
- `Alternate Data Streams`: explains unnamed and named streams, Windows-style stream syntax, and stream xattr listing.
- `OPTIONS`: documents supported mount options.
- `USER MAPPING`: explains `.NTFS-3G/UserMapping`, SID mapping lines, default mapping examples, and `ntfsusermap`.
- `EXAMPLES`: shows common mount, read-only mount, fstab, and unmount commands.
- `EXIT CODES`: points to `ntfs-3g.probe(8)` for unique status codes.
- `KNOWN ISSUES`, `AUTHORS`, `THANKS`, and `SEE ALSO`.

## Options Documented

- Security and permissions: `acl`, `allow_other`, `permissions`, `uid=`, `gid=`, `umask=`, `fmask=`, `dmask=`, `silent`, `usermapping=`, `inherit`.
- Time/cache behavior: `atime`, `noatime`, `relatime`, `delay_mtime`, `big_writes`, `max_read`.
- Recovery and safety: `force` as obsolete, `recover`, `norecover`, `remove_hiberfile`, `ro`.
- Name and visibility behavior: `windows_names`, `hide_dot_files`, `hide_hid_files`, `show_sys_files`, `ignore_case`.
- Data features: `compression`, `nocompression`, `efs_raw`, `streams_interface=`, `user_xattr`, `special_files=`.
- Mount defaults and debug behavior: `no_def_opts`, `no_detach`, `debug`, `locale=`.

## Important Details and Edge Cases

- Fast restart/hibernation causes internal partitions to be forced read-only unless Windows is fully shut down or hibernation/fast restart are disabled.
- `remove_hiberfile` is documented as destructive to the saved Windows session.
- `recover` clears the Windows logfile and may cause inconsistencies, but is described as the current default.
- `force` is documented as obsolete in favor of `recover`/`norecover`.
- `streams_interface=windows` is explicitly unavailable with `lowntfs-3g`.
- `windows_names` rejects forbidden characters, trailing spaces/dots, and reserved DOS device names for newly created names, while existing names remain readable.
- The fstab example notes that the sixth field should be zero to avoid boot-time filesystem checks.
- Some formatting appears inconsistent in the source text, such as literal `**acl**` and `**permissions**` in a roff file, but the intended meaning is clear.

## Dependencies

- This is a roff man page template consumed by the build/install process in `src/Makefile.am`.
- It references companion documentation and tools: `ntfs-3g.probe(8)`, `ntfsprogs(8)`, `attr(5)`, `getfattr(1)`, and `ntfsusermap`.

## Role in Source Tree

This file is the primary installed operator-facing documentation for NTFS-3G mount behavior. It connects the implementation’s mount options and safety policies to user-visible command usage, examples, and administrative warnings.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g.8.in -->