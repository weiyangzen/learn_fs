## sources/distributed-fs/eos/mgm/ofs/fsctl/Chmod.cc

Purpose: fsctl wrapper around internal chmod for FUSE-style callers.

Important APIs and types: `XrdMgmOfs::Chmod`, `_chmod`, `XrdOucEnv`, `XrdSfsMode`, access-mode/stall/redirect macros, and `MgmStats`.

Control flow: marks write access, applies stall/redirect, increments `Fuse-Chmod`, reads `mode`, converts with `atoi`, calls `_chmod(path, newmode, error, vid)`, maps errors to `retc`, returns `EINVAL` when mode is missing, and writes `chmod: retc=<code>` to `error` while returning `SFS_DATA`.

State and persistence behavior: actual mode changes are performed by `_chmod`; this file only parses request and returns fsctl-formatted response.

Dependencies and integration points: FUSE clients depend on this response contract. Authorization and metadata persistence are delegated to `_chmod`.

Risks: malformed modes parse as zero. The `client` and `ininfo` parameters are unused after macros, so all semantic checks depend on the supplied `vid` and `_chmod`.

Test signals: valid mode change, missing mode, malformed mode, permission denial from `_chmod`, response format, and stats.
