# sources/distributed-fs/openafs/src/venus/up.c

## Purpose
`up.c` implements `up`, a recursive update/copy utility that mirrors a source file tree to a target while preserving ownership, group, mode bits, timestamps by default, AFS ACLs by default, and optionally AFS mount points. It is similar to a specialized recursive copy tuned for AFS update workflows.

## Important APIs, Types, And Functions
Global flags are set by `ScanArgs`: `-v` verbose, `-1` one level only, `-r` rename existing targets to `.old`, `-f` force overwrite write-protected targets, `-x` do not preserve dates, and `-m` preserve AFS mount points. `MakeParent` recursively creates missing parent directories and sets owner. `Copy` handles regular files, symlinks, mount points, and directories. `isMountPoint` tests a path with `VIOC_AFS_STAT_MT_PT`. `struct OldAcl` supports conversion from older ACL ioctl output.

## Control Flow
`main` parses flags and two paths, then calls `Copy(source, target, !oneLevel, 0)`. `Copy` uses `lstat` to classify the source, creates missing target parents, and branches by object type. Regular files are copied through a temporary `target.UPD`, optionally preserving times, optionally renaming the previous target, then setting owner, group, and mode. Symlinks are recreated from `readlink` output. When `-m` is active, AFS mount points are detected and recreated as symlinks to the mount target plus trailing dot. Directories are recursively traversed, created as needed, ownership/group/mode/times are applied, and ACLs are copied using new-style `_VICEIOCTL(2)` get and `_VICEIOCTL(1)` set, or old-style `_VICEIOCTL(4)` conversion when enabled.

## State And Persistence
The program modifies the target tree: it creates directories, files, symlinks, mount-point symlinks, temporary `.UPD` files, optional `.old` backups, ownership, group, mode, timestamps, and AFS ACLs. Global `setacl` can be turned off after an EINVAL and then suppresses ACL copying for later directories.

## Dependencies And Integration Points
It depends on POSIX directory/file syscalls, AFS pioctl/ioctl constants, `VIOC_AFS_STAT_MT_PT`, and the cache manager's ACL pioctls. It integrates ordinary filesystem metadata copying with AFS-specific ACL and mount-point representation.

## Risks And Test Signals
Risks include destructive target updates, fixed `MAXPATHLEN` buffers, duplicated `strlcpy` and `chown` statements, no cleanup of stale `.UPD` on failures, possible uninitialized symlink text in a verbose message before `readlink`, process-global ACL disabling after one unsupported path, old ACL conversion assumptions, and limited protection against path truncation. Test signals include regular file copy with metadata preservation, force and rename-target behavior, recursive directory copy, one-level mode, symlink recreation, mount-point preservation with `-m`, ACL copy success/fallback, timestamp opt-out with `-x`, and behavior when target files are write-protected.
