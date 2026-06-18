# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_access.c

## Purpose

`afs_vnop_access.c` implements AFS vnode access checks. It translates Unix `VREAD`/`VWRITE`/`VEXEC` access requests into AFS protection rights, combines directory ACL rights with file owner/mode restrictions, handles fakestat and disconnected-mode constraints, and exposes a UKERNEL helper for retrieving rights.

## Important APIs, Types, and Functions

- `fileModeMap` maps owner mode-bit combinations to AFS read/write rights that should be masked off.
- `afs_GetAccessBits` returns which requested AFS rights are available from `anyAccess`, per-PAG access cache, or a server `FetchStatus` result.
- `afs_AccessOK` determines whether a vcache grants all requested AFS rights, using directory ACLs for files and ACL-only checks for directories/foreign vnodes.
- `afs_access` is the vnode access operation for Unix modes.
- Under `UKERNEL`, `afs_getRights` verifies the vcache and returns `afs_GetAccessBits` for a requested rights mask.

## Control Flow

`afs_access` creates a `vrequest`, enters the disconnected lock, evaluates fakestat/mountpoint state, verifies the vcache unless a readdir-specific bypass applies, rejects writes to read-only volumes, rejects disconnected writes when disconnected write mode is unavailable, and then maps Unix mode bits. Directory execute maps to `PRSFS_LOOKUP`; directory write accepts insert or delete; regular-file execute requires read plus owner execute bit handling; writes and reads call `afs_AccessOK`.

`afs_AccessOK` handles directories directly from ACL rights. For files, it resolves parent directory rights when parent fid metadata exists, optionally fetches file administer rights, grants read/write when insert and administer imply ownership, and then applies Unix owner mode-bit masks.

## State and Persistence Behavior

This file reads and updates access-related cache state indirectly. `afs_GetAccessBits` consults `avc->f.anyAccess`, `avc->Access`, user token state, and may refresh status through `afs_FetchStatus`. It does not persist state itself but may cause access cache/status changes inside fetch/verify paths.

## Dependencies and Integration Points

It depends on vcache status, per-user token records, `afs_FindAxs`, `afs_FindUser`, `afs_FetchStatus`, fakestat helpers, disconnected-mode macros, NFS translator flags, and `afs_CheckCode`. UKERNEL `uafs_access` and `uafs_getRights` call into this file.

## Risks and Edge Cases

Parentless files assume directory rights are OK (`0xffffffff`), called out as a race condition. Disconnected mode denies rights that would require a server access fetch. NFS translator compatibility includes special handling for anonymous-owner writes and execute-as-read. `afs_InReadDir` deliberately grants only lookup/read to avoid recursive fetch-status problems.

## Test Signals

Test directory and file access under combinations of ACLs, mode bits, owner/admin rights, read-only volumes, bad/missing tokens, foreign cells, fakestat mountpoints, disconnected read-only and disconnected write mode, NFS translator credentials, and active readdir.
