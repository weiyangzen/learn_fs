# sources/distributed-fs/openafs/src/WINNT/afsd/symlink.c

## Purpose
Windows command-line utility for listing, creating, and removing AFS symlinks. It packages operations as pioctls because Windows does not provide a native AFS symlink syscall.

## Important APIs, Types, And Functions
`ListLinkCmd` derives parent/leaf names, fetches FID and file type with query options, verifies type `3` symlink, and prints the target from `VIOC_LISTSYMLINK`. `MakeLinkCmd` validates the parent is in AFS, restricts freelance root updates to admins, normalizes UNC AFS targets into Unix-style paths, and calls `VIOC_SYMLINK`. `RemoveLinkCmd` verifies the link with list, checks freelance admin policy, and calls `VIOC_DELSYMLINK`. `wmain` initializes Winsock, OpenAFS command parsing, UTF-8 argv conversion, and subcommands.

## Control Flow
The command framework dispatches `list`, `make`, `remove`, or `rm`. Each command performs local path checks, adapts `\\afs\` roots to `\\afs\all\` when necessary, fills `ViceIoctl`, and invokes `pioctl_utf8`.

## State And Persistence
Only transient process buffers are local. Persistent effects are AFS symlink creation/deletion and possible root.afs freelance changes through cache-manager/server operations.

## Dependencies And Integration Points
Depends on Windows APIs, Winsock startup, `fs_utils`, command parser, `cm_ioctl.h`, pioctl UTF-8 support, file type query options, and NetBIOS-name helpers. Integrates with SMB/cache-manager symlink pioctl handlers.

## Risks
Fixed 1024-byte path buffers, subtle UNC/trailing-slash conversion, hard-coded symlink type value, and local admin checks that must align with server-side enforcement.

## Test Signals
Test list/make/remove for normal, drive-relative, `\\afs\cell`, `\\afs\all\cell`, non-AFS, non-symlink, freelance admin/non-admin, long path, and UTF-8 names.
