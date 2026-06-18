## sources/distributed-fs/eos/mgm/ofs/fsctl/Access.cc

Purpose: FUSE/fsctl handler for access checks. It converts a request containing `mode` into a call to the normal MGM `access()` API and returns a text response through `XrdOucErrInfo`.

Important APIs and types: `XrdMgmOfs::Access`, `XrdOucEnv`, `XrdOucErrInfo`, `VirtualIdentity`, access-mode/stall/redirect macros, and `MgmStats`.

Control flow: marks the operation read-only, applies stall/redirect behavior, increments `Fuse-Access`, reads `mode` from the environment, calls `access(path, newmode, error, client, 0)` if present, maps failures to `error.getErrInfo()`, otherwise uses `EINVAL`, and returns `SFS_DATA` with `access: retc=<code>`.

State and persistence behavior: no namespace mutation. It may update stats and trigger redirect/stall side effects before the access call.

Dependencies and integration points: FUSE clients depend on the exact response string. The actual authorization and permission semantics live in `XrdMgmOfs::access`.

Risks: `ininfo` and `ininfo`-derived opaque data are not passed to `access()` here, so mode checks may not see caller opaque options. `atoi()` accepts malformed `mode` as zero. A successful access returns retc 0 inside an `SFS_DATA` response rather than `SFS_OK`.

Test signals: missing mode, malformed mode, allowed/denied access modes, stall/redirect behavior, response string format, and stats increment.
