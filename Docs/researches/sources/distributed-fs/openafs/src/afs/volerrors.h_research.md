# sources/distributed-fs/openafs/src/afs/volerrors.h

Purpose: defines volume package error codes and special server-returned conditions.

Important APIs/types: `VREADONLY` maps to `EROFS`; special codes start at `VICE_SPECIAL_ERRORS = 101`. Defined conditions include `VSALVAGE`, `VNOVNODE`, `VNOVOL`, `VVOLEXISTS`, `VNOSERVICE`, `VOFFLINE`, `VONLINE`, `VDISKFULL`, `VOVERQUOTA`, `VBUSY`, `VMOVED`, and negative `VRESTARTING`.

Control flow: constants only. Callers interpret some values specially instead of passing them directly to applications.

State and persistence: none.

Dependencies and integration points: included by `afsincludes.h` and used by vcache/volume/server analysis paths. `afs_CheckFetchStatus` returns `VBUSY` for malformed fetch status, and `afs_FlushActiveVcaches` suppresses some warnings for `VNOVNODE`.

Risks: numeric compatibility is important; old cache managers interpret negative `VRESTARTING` as server-down. Typos or remapping can change retry/offline/quota behavior.

Test signals: server error translation tests for readonly, over quota, disk full, busy, moved, restarting, and salvage/offline cases; verify retry logic handles `VBUSY`/`VRESTARTING` correctly.
