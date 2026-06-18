# Group Research: group_1320_ntfs_3g_sources_local_fs_ntfs_3g_src_ntfs_3g_c_sources_local_fs_ntf_fdce4e821c81

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g.c -->
# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g.c

## Role

`ntfs-3g.c` is the main high-level FUSE filesystem driver for NTFS-3G. It wires FUSE callbacks to libntfs-3g volume, inode, attribute, directory, security, xattr, ioctl, EFS, and reparse-point APIs, then owns process startup, mount setup, logging, FUSE loop execution, and teardown.

It is the regular path-based NTFS-3G frontend, distinct from `lowntfs-3g`, and exposes NTFS objects as POSIX-like files, directories, symlinks, special files, alternate data streams, extended attributes, and optional POSIX ACL-backed metadata.

## Global State And Configuration

- `opts` holds parsed command-line device, mountpoint, and mount options.
- `ctx` is the process-global `ntfs_fuse_context_t` shared by all callbacks. It carries the mounted volume, masks, uid/gid defaults, stream mode, security flags, FUSE channel, reparse plugins, EFS mode, atime policy, delayed mtime setting, and platform feature switches.
- `ntfs_sequence` is used to generate temporary names during overwrite rename emulation.
- `CLOSE_COMPRESSED`, `CLOSE_ENCRYPTED`, `CLOSE_DMTIME`, and `CLOSE_REPARSE` are bit flags stored in `fuse_file_info.fh` to defer close-time work such as compressed stream close, EFS fixup, and delayed mtime update.

## Permission Model

The file compiles different permission-checking behavior from `HPERMSCONFIG`:

- `KERNELPERMS` controls whether basic permissions are delegated to FUSE/kernel.
- `KERNELACLS` controls whether POSIX ACL checks are delegated to the kernel.
- `CACHEING` controls attribute timeout behavior.
- Security checks are performed through `SECURITY_CONTEXT`, filled by `ntfs_fuse_fill_security_context()` from `ctx`, the current FUSE uid/gid/pid, user/group mappings, and optional umask support.
- Parent directory access is explicitly checked for lookup, open, create, unlink, rename, chmod/chown, timestamp changes, and xattr operations when kernel permissions are not sufficient.
- Sticky directory semantics are approximated by checking file ownership when `S_ISVTX`-style access is requested.

## Mount And Startup Flow

1. `main()` ensures descriptors 0, 1, and 2 are open.
2. With external FUSE, setuid/setgid execution is rejected as insecure.
3. Privileges are dropped, locale/logging are initialized, and `ntfs_parse_options()` parses device, mountpoint, and `-o` options.
4. `ntfs_fuse_init()` allocates `ctx` and applies defaults: current uid/gid, Linux stream access as xattr, non-Linux stream access disabled, relative atime, silent mode, and recovery enabled.
5. `parse_mount_options()` builds FUSE options and fills `ctx`.
6. The code rejects conflicting existing mounts except multiple read-only mounts.
7. It resolves an absolute mount point, records mountpoint owner for default mapping, loads/creates FUSE support on Linux if needed, and decides whether to use `fuseblk`.
8. `ntfs_open()` mounts the NTFS volume with flags derived from read-only, recovery, block-device, and hibernation-removal options.
9. Read-only fallback can insert `,ro`; explicit rw can insert `,rw`; `fuseblk` adds `blkdev,blksize=`.
10. Security mappings and optional xattr mappings are built.
11. Internal reparse plugins are registered.
12. `mount_fuse()` mounts the FUSE channel, creates the FUSE handle, and installs signal handlers.
13. `setup_logging()` daemonizes unless requested otherwise and logs volume, options, and permissions mode.
14. `fuse_loop()` runs until unmount.
15. Cleanup unmounts FUSE, closes the NTFS volume, closes plugins, frees mappings/options/context, and reports mount errors.

## Core Behavior

- `ntfs_fuse_parse_path()` splits Windows-style `file:stream` paths into base path and NTFS Unicode stream name when that stream interface is active.
- `ntfs_fuse_statfs()` reports cluster and MFT-derived filesystem capacity/inode statistics.
- `ntfs_fuse_getattr()` maps NTFS metadata, directories, regular files, named streams, Interix special files, WSL special reparse points, EFS raw sizes, ownership, permissions, and timestamps into `struct stat`.
- Directory operations use `ntfs_readdir()` or plugin readdir for reparse directories, with `ntfs_fuse_filler()` converting NTFS Unicode names to multibyte names and selecting POSIX mode hints.
- File I/O opens `AT_DATA`, loops through `ntfs_attr_pread()`/`ntfs_attr_pwrite()`, updates timestamps, sets archive state, and defers compressed/EFS/delayed-mtime close work through `fi->fh`.
- Creation paths validate Windows names, open parent directories, compute inherited or allocated security IDs, create files/directories/symlinks/devices or streams, and reject `$Extend` creation.
- Deletion rejects metadata files and `$Extend`, checks sticky-directory semantics where needed, and dispatches to stream removal or `ntfs_delete()`.
- Rename is explicitly non-atomic and implemented through link/unlink/temp-name restoration.
- xattr support maps namespaces to NTFS named data streams, hijacks known NTFS system xattrs, supports `ntfs.streams.list` in Windows stream mode, and handles EFS raw sizing/fixups.
- Reparse support delegates operations to internal or dynamically loaded plugins and falls back to synthetic symlinks for unsupported tags.
- `fsync` syncs the whole device, `ioctl` forwards to `ntfs_ioctl()`, and `bmap` maps physical blocks only for simple nonresident unnamed data.

## Important Dependencies

This file depends on nearly the whole NTFS-3G stack: FUSE 2.6+ APIs, volume mount/unmount/free-space APIs, inode/attribute/directory/index/runlist/time/security/xattr/EFS/object-id/EA/reparse/ioctl/plugin layers, and shared option/plugin/xattr helpers from `ntfs-3g_common.c`.

## Notable Limitations And Risk Areas

- Rename is not atomic, which matters for crash consistency and applications depending on POSIX replacement semantics.
- The global `ctx` and `ntfs_sequence` make concurrency assumptions important.
- Permission behavior changes substantially by build flags, platform, and FUSE version.
- Dynamic reparse plugin failures are logged once and then surface through fallback behavior.
- Colon stream parsing conflicts with filenames containing `:` in Windows stream mode.
- EFS raw correctness depends on close-time fixups.
- Metadata-file protections are repeated across mutation paths, so each path must preserve its own guard.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g.probe.8.in -->
# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g.probe.8.in

## Role

`ntfs-3g.probe.8.in` is the manual page template for `ntfs-3g.probe`, the helper utility that checks whether an NTFS volume can be mounted read-only or read-write. The `.in` suffix indicates build-time substitution, notably `@VERSION@`.

## Documented Interface

The synopsis is:

`ntfs-3g.probe <--readonly|--readwrite> volume`

The page documents:

- `-r`, `--readonly`: test read-only mountability.
- `-w`, `--readwrite`: test read-write mountability.
- `-h`, `--help`: display help and exit.

The example tests read-write mountability of `/dev/sda1`.

## Exit Codes

The man page defines the user-visible status contract:

- `0`: volume is mountable.
- `11`: syntax error.
- `12`: invalid NTFS.
- `13`: inconsistent NTFS, hardware/device fault, or unconfigured RAID.
- `14`: hibernated NTFS.
- `15`: volume not cleanly unmounted.
- `16`: already exclusively opened or in use.
- `17`: unconfigured SoftRAID/FakeRAID hardware.
- `18`: unknown reason.
- `19`: insufficient privilege.
- `20`: out of memory.
- `21`: unclassified FUSE error.

These correspond to `NTFS_VOLUME_*` status values returned by libntfs/NTFS-3G helper code.

## Relationship To Code

The documented options match `ntfs-3g.probe.c`:

- The command requires exactly one probe mode and one device/image.
- The utility exits with the value returned by `ntfs_volume_error(errno)` after a mount attempt.
- For read-only probe mode, the implementation mounts with `NTFS_MNT_RDONLY`; read-write mode uses normal mount flags.

## Notable Limitations And Risk Areas

- The man page says the tool tests mountability, not filesystem health or repair.
- Exit codes are part of external integration behavior; scripts may depend on these exact numeric meanings.
- The known-issues section points users to the NTFS-3G FAQ and issue tracker rather than documenting detailed remediation per status.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g.probe.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g.probe.c -->
# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g.probe.c

## Role

`ntfs-3g.probe.c` implements the `ntfs-3g.probe` command-line utility. It tests whether a device or image can be mounted by libntfs-3g in read-only or read-write mode and exits with a standardized NTFS-3G volume status code.

## Data Model

- `probe_t` has three states: unset, read-only probe, and read-write probe.
- The static `opts` struct stores the selected probe type and copied device path.
- `EXEC_NAME` is `ntfs-3g.probe` for logging and usage output.

## Control Flow

1. `main()` directs NTFS logging to stderr.
2. `parse_options()` parses command-line arguments.
3. On parse failure, `usage()` is printed and the process exits with `NTFS_VOLUME_SYNTAX_ERROR`.
4. `ntfs_open()` attempts to mount the selected device.
5. If mount succeeds, it immediately unmounts.
6. The program exits with the returned volume status, or `0` on success.

## Option Parsing

`parse_options()` uses `getopt_long()` with:

- `-r`, `--readonly`
- `-w`, `--readwrite`
- `-h`, `--help`
- one non-option device argument

Behavior:

- The first non-option argument is copied into a `PATH_MAX + 1` buffer allocated by `ntfs_malloc()`.
- A second device argument is rejected.
- Missing device is rejected.
- Missing probe type is rejected.
- Unknown options are reported with the original option spelling.
- `--help` prints usage and exits successfully.

One subtle point: if both `--readonly` and `--readwrite` are supplied, the later option wins; the parser only rejects missing probe type, not conflicting repeated modes.

## Mount Probe Semantics

`ntfs_open()`:

- Sets `NTFS_MNT_RDONLY` only for read-only probe mode.
- Calls `ntfs_mount(device, flags)`.
- Converts mount failure `errno` with `ntfs_volume_error(errno)`.
- If mounting succeeds, calls `ntfs_umount(vol, FALSE)`.
- Converts unmount failure `errno` the same way.
- Returns `NTFS_VOLUME_OK` on full success.

The read-write probe does not set special recovery, hibernation, or FUSE flags; it directly tests libntfs mountability.

## Important Dependencies

- `volume.h` for `ntfs_mount()`, `ntfs_umount()`, and `NTFS_VOLUME_*` status handling.
- `misc.h` for `ntfs_volume_error()`, `ntfs_home`, and allocation helpers.
- `compat.h` and generated `config.h` for portability.
- libc `getopt_long()` for CLI parsing.

## Notable Limitations And Risk Areas

- This utility probes libntfs mountability only; it does not mount through FUSE or validate FUSE availability.
- Read-write probe behavior depends on libntfs mount checks and current volume state such as dirty, hibernated, locked, or invalid NTFS.
- Conflicting `--readonly` and `--readwrite` options are accepted with last-one-wins behavior.
- Device names longer than `PATH_MAX` are truncated by `strncpy()` into the fixed buffer.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g.probe.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g_common.c -->
# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g_common.c

## Role

`ntfs-3g_common.c` contains shared support code for `ntfs-3g` and `lowntfs-3g`. Its main responsibilities are mount option parsing, FUSE option string construction, common command-line parsing, xattr listing helpers, user-xattr eligibility checks, and reparse plugin registration/loading/closing.

## Shared Constants

The file defines xattr namespace strings and lengths:

- `xattr_ntfs_3g = "ntfs-3g."`
- `user.`
- `system.`
- `security.`
- `trusted.`

It also defines:

- `nf_ns_alt_xattr_efsinfo = "user.ntfs.efsinfo"` for encrypted files when xattr mappings are unavailable.
- Default FUSE options `allow_other,nonempty,`.

## Option Table

`optionlist[]` is the recognized NTFS-3G mount option table. Each option has a name, enum type, and validation flags.

Major options include access mode, atime policy, delayed mtime, permissions/security, masks, uid/gid, visibility/name behavior, compression/recovery/hibernation/sync, encoding, stream/xattr behavior, process behavior, mapping files, EFS raw mode, POSIX nlink mode, and special-file mode.

Flags enforce no value, string value, octal value, decimal value, optional value, pass-through append, or unsupported status.

## String Option Helpers

`ntfs_strappend()` appends to dynamically allocated option strings with a hard input-size guard of 8192 bytes per current/appended string. It uses `realloc()` and reports overflow or allocation failure.

`ntfs_strappend_escaped()` escapes backslashes and commas for FUSE versions where the runtime FUSE library is new enough to require it, then delegates to `ntfs_strappend()`.

`ntfs_strinsert()` inserts an option before `,fsname=` when present. This keeps `fsname` last because Solaris device names may contain commas. If no `fsname` is found, it appends.

## Mount Option Parsing

`parse_mount_options()` takes parsed high-level options and fills `ntfs_fuse_context_t`, returning a FUSE option string.

Key behavior:

- Initializes security flags and EFS/compression defaults.
- Splits the raw `-o` string on commas and `=`.
- Recognized NTFS-3G options update `ctx`.
- Unknown options are treated as FUSE options and passed through.
- Options marked `FLGOPT_APPEND`, such as `ro` and `sync`, are also added to the FUSE option string.
- `no_def_opts` suppresses default FUSE options and cancels default silent mode.
- `default_permissions` and `permissions` can append `default_permissions`.
- `acl` sets security ACL intent when compiled with POSIX ACL support.
- `umask`, `fmask`, `dmask`, `uid`, and `gid` set default ownership/masks and mark security as wanted.
- `ignore_case` is accepted only for low-level FUSE mode.
- `streams_interface` accepts `none`, `xattr`, `openxattr`, and, for regular `ntfs-3g`, `windows`.
- `user_xattr` maps to `openxattr` on macOS and `xattr` elsewhere.
- `remount` is explicitly unsupported.
- `blksize` is ignored with a warning because NTFS-3G computes it later.
- `special_files` accepts `interix` or `wsl`.
- Atime options are mutually represented by adding one of `relatime`, `atime`, or `noatime`.
- `fsname=<device>` is always appended last, with escaping when needed.
- Read-only mode clears add-security-ID behavior, disables hiberfile removal, and clears explicit rw.

On error, the partially built option string is freed and `NULL` is returned.

## Program Option Parsing

`ntfs_parse_options()` parses the command-line interface shared by `ntfs-3g` variants:

- `-o`, `--options`: append comma-separated mount options.
- `-h`, `--help`: call the supplied usage function and exit with status `9`.
- `-n`, `--no-mtab`: accepted as a no-op for automount compatibility.
- `-s`: accepted as a no-op for sloppy automount compatibility.
- `-v`, `--verbose`: accepted but unused because `mount(8)` may pass it.
- `-V`, `--version`: prints version, FUSE type, and FUSE version, then exits.
- First non-option argument is canonicalized as the device with `ntfs_realpath_canonicalize()`.
- Second non-option argument is the mount point.
- Extra non-option arguments, missing device, or missing mount point are rejected.

## Xattr Listing Helper

When `HAVE_SETXATTR` is enabled, `ntfs_fuse_listxattr_common()` lists NTFS named data streams as extended attributes.

Behavior:

- Iterates `AT_DATA` attributes from an existing search context.
- Skips unnamed data.
- Converts NTFS Unicode stream names to multibyte strings.
- In prefixing mode, hides internal `ntfs-3g.*` attributes and returns user streams as `user.<stream>`.
- In open namespace mode, returns names as stored.
- Checks output buffer size and returns `-ERANGE` if insufficient.
- With `XATTR_MAPPINGS`, appends mapped system attributes when accepted.
- Without mappings, appends `user.ntfs.efsinfo` for encrypted files in EFS raw mode.

The source contains a TODO noting that mapped system xattr listing should only return xattrs that are actually set, which is more complex for object IDs and DOS names.

## Reparse Plugin Registry

When plugins are enabled:

`register_reparse_plugin()` allocates a `plugin_list_t`, records selected tag, operations pointer, dynamic library handle, and links it into `ctx->plugins`.

`select_reparse_plugin()` reads the inode reparse point, masks the tag with `IO_REPARSE_PLUGIN_SELECT`, searches already registered plugins, dynamically loads `ntfs-plugin-XXXXXXXX.so` if needed, resolves `init`, calls the initializer, registers successful operations, logs load failures once, and returns the operations vector plus optional reparse data.

`close_reparse_plugins()` closes dynamically loaded handles and frees registry nodes.

## User Xattr Eligibility

`user_xattrs_allowed()` decides whether user xattrs may be exposed for an inode:

- Plain non-system, non-reparse files are allowed.
- The root directory is allowed even though it is metadata.
- Reparse points are allowed only if a plugin can report them as regular files or directories.
- Metadata files below `FILE_first_user` are denied.
- Interix special files are allowed only when their type is regular file or directory.

This prevents ordinary user xattrs on symlinks, FIFOs, sockets, devices, most metadata files, and unsupported reparse objects.

## Important Dependencies

- FUSE option and version APIs.
- `realpath.h` for device canonicalization.
- `security.h` and `xattrs.h` for security and xattr policy.
- `reparse.h` and `plugin.h` for plugin loading.
- `inode.h`, `dir.h`, and NTFS attribute search APIs for xattr enumeration and inode type checks.
- Optional `dlfcn.h` dynamic loading.

## Notable Limitations And Risk Areas

- Mount option parsing uses `strsep()` and direct comma splitting, so correct escaping matters for pass-through FUSE options and device names.
- The string helper guard prevents very large option strings but also imposes a fixed practical limit.
- Unknown options are passed through to FUSE, so typo behavior depends on whether the option name is known to NTFS-3G.
- Some options are accepted as no-ops for compatibility, which can hide caller assumptions.
- Dynamic plugin loading failures are collapsed to `ELIBACC` and logged once; subsequent unsupported reparse behavior depends on caller fallback.
- The xattr mapping TODO means list results may include mapped system names without fully proving the backing data exists.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g_common.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g_common.h -->
# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g_common.h

## Role

`ntfs-3g_common.h` declares shared structures, enums, macros, globals, and function prototypes used by `ntfs-3g` and `lowntfs-3g`. It is the contract for common option parsing, stream mode selection, FUSE context state, xattr helpers, and reparse plugin operations.

## Command Option State

`struct ntfs_options` stores command-line state before it is converted into a mounted context:

- `mnt_point`: mount point path.
- `options`: raw comma-separated mount options.
- `device`: canonicalized device path.
- `arg_device`: original device argument.

## Stream Interface Modes

`ntfs_fuse_streams_interface` defines how NTFS alternate data streams are exposed:

- `NF_STREAMS_INTERFACE_NONE`: no named stream access.
- `NF_STREAMS_INTERFACE_XATTR`: named streams mapped to xattrs.
- `NF_STREAMS_INTERFACE_OPENXATTR`: xattr mapping without limiting to `user.` namespace.
- `NF_STREAMS_INTERFACE_WINDOWS`: Windows-style `file:stream` paths.

These modes drive path parsing, xattr namespace handling, and platform defaults.

## Mount Option Definitions

`struct DEFOPTION` describes a recognized mount option with an option name, enum type, and validation/behavior flags.

The option enum covers all NTFS-3G-specific mount options handled by `parse_mount_options()`, including access mode, atime mode, permission/security settings, masks, ownership, visibility, filename policy, compression, recovery, streams, debug, user mappings, xattr mappings, EFS raw mode, POSIX link count mode, special file mode, help, and version.

Option flags include bogus/no-value options, string-valued options, octal-valued options, decimal-valued options, append-to-FUSE options, unsupported options, and optional-valued options.

## Context State

`ntfs_fuse_context_t` is the central runtime context shared by FUSE callbacks.

It contains:

- Mounted `ntfs_volume *vol`.
- Default uid/gid.
- File and directory masks.
- Stream interface mode.
- Atime policy and delayed mtime interval.
- Read-only/read-write flags.
- Visibility and naming flags.
- Compression, ACL, silent, recovery, hibernation, sync, big-write, debug, no-detach, block-device, mounted, and POSIX nlink flags.
- Special file mode for Interix or WSL handling.
- Optional EFS raw and xattr mapping path state.
- FUSE channel pointer.
- NTFS security inheritance and secure flags.
- One-shot logged error flags.
- User mapping path and absolute mount point.
- Reparse plugin list when plugins are enabled.
- Permissions cache and current security context.
- `open_files` for low-level FUSE usage.
- `latest_ghost`, also for low-level or cleanup tracking.

## Plugin State

When plugins are enabled, `plugin_list_t` records the next plugin node, dynamic library handle, plugin operations vector, and selected reparse tag.

The header declares plugin lifecycle functions:

- `register_reparse_plugin()`
- `select_reparse_plugin()`
- `close_reparse_plugins()`

## Shared Globals And Macros

- `EXEC_NAME` is extern so shared code can log using the current executable name.
- `FUSE_TYPE` expands to `"integrated FUSE"` or `"external FUSE"` depending on build configuration.
- xattr namespace constants and prefix lengths are exported for xattr code.

## Shared Function Prototypes

The header declares:

- `ntfs_strappend()`
- `ntfs_strinsert()`
- `parse_mount_options()`
- `ntfs_parse_options()`
- `ntfs_fuse_listxattr_common()`
- `user_xattrs_allowed()`

These are implemented in `ntfs-3g_common.c` and used by the main FUSE frontends.

## Important Dependencies

- Includes `inode.h`, which brings in NTFS inode/volume types used throughout the context.
- Relies on plugin operation types and reparse types being available through the broader NTFS-3G include graph.
- Uses build-time feature macros such as `FUSE_INTERNAL`, `HAVE_SETXATTR`, `XATTR_MAPPINGS`, and `DISABLE_PLUGINS`.

## Notable Limitations And Risk Areas

- `ntfs_fuse_context_t` is broad and mutable; most major subsystems share it, so option parsing, mount setup, and callbacks are tightly coupled.
- Many fields are conditionally compiled, making ABI and behavior dependent on build configuration.
- The stream interface enum affects both path syntax and xattr behavior, so mode changes have broad surface area.
- `open_files` is only defined for `lowntfs-3g`, but remains in the shared context.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/src/ntfs-3g_common.h -->