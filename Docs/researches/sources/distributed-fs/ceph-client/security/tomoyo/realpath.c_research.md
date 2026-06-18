# sources/distributed-fs/ceph-client/security/tomoyo/realpath.c

## Purpose

This file converts kernel paths and binary socket/path strings into TOMOYO's canonical, printable policy names. It provides realpath-like resolution that ignores chroot roots where appropriate, appends directory trailing slashes, prefixes local filesystem or device names for non-global paths, and escapes non-printable bytes.

## Important APIs, types, and functions

Public APIs are `tomoyo_encode2()`, `tomoyo_encode()`, `tomoyo_realpath_from_path()`, and `tomoyo_realpath_nofollow()`. Internal helpers are `tomoyo_get_absolute_path()`, `tomoyo_get_dentry_path()`, and `tomoyo_get_local_path()`. `tomoyo_encode2()` is also used by network code for UNIX socket names.

## Control Flow

Encoding first computes the escaped output length, allocates with `GFP_NOFS`, doubles backslashes, keeps printable ASCII above space and below DEL, and emits other bytes as octal `\ooo`. Path resolution grows a temporary buffer by powers of two, uses `d_dname()` for pseudo dentries, otherwise chooses local or absolute naming based on filesystem capabilities and device requirements. If `d_absolute_path()` returns `-EINVAL`, it falls back to local path naming. Successful paths are encoded before returning.

## State and Persistence

The file stores no persistent state. It allocates temporary buffers and returns allocated encoded strings owned by callers. The local path branch uses filesystem metadata, device numbers, procfs pid namespace information, and root inode operations at the time of the call.

## Dependencies and Integration Points

It depends on VFS path helpers, procfs magic and pid namespaces, superblock metadata, device major/minor values, TOMOYO OOM warning, and common TOMOYO path consumers. `tomoyo_realpath_nofollow()` integrates with `kern_path()` and `path_put()`.

## Risks and Test Signals

Risks include buffer growth loops under persistent path errors, incorrect proc `/self` rewriting, missing trailing slash for directories, escaping mismatches with parser validation, and allocation failures under `GFP_NOFS`. Tests should cover procfs, anonymous pipes/sockets, device-backed and device-less filesystems, non-renamable filesystems, long paths, binary bytes, backslashes, and nofollow lookup failures.
