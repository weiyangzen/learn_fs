## sources/distributed-fs/eos/mgm/ofs/fsctl/Chown.cc

Purpose: fsctl wrapper around internal chown for file or directory ownership changes.

Important APIs and types: `XrdMgmOfs::Chown`, `_chown`, `XrdOucEnv`, `uid_t`, access-mode/stall/redirect macros, and `MgmStats`.

Control flow: marks write access, applies stall/redirect, increments `Fuse-Chown`, reads `uid` and `gid`, converts both with `atoi`, calls `_chown(path, uid, gid, error, vid)`, maps failures to `retc`, returns `EINVAL` if either parameter is missing, and responds `chown: retc=<code>` as `SFS_DATA`.

State and persistence behavior: actual metadata ownership changes are delegated to `_chown`.

Dependencies and integration points: used by FUSE/fsctl ownership changes. Relies on `_chown` for authorization, ownership semantics, quota or accounting side effects, and persistence.

Risks: `gid` is stored in a `uid_t` local rather than `gid_t`; this may be harmless on common platforms but is type-inaccurate. `atoi()` makes malformed values zero. Missing opaque/client use after macros may reduce contextual checks to the passed `vid`.

Test signals: valid chown, missing uid/gid, malformed values, permission denial, uid/gid type boundaries, response format, and stats.
