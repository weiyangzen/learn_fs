## sources/distributed-fs/eos/mgm/ofs/cmds/Utimes.inc

Purpose: sets modification/change times for files and directories.

Important APIs and types: public `XrdMgmOfs::utimes`, internal `_utimes`, `VirtualIdentity`, `IContainerMD`, `IFileMD`, `RWMutexWriteLock`, `_access`, and metadata store update methods.

Control flow: public `utimes()` maps identity for `AOP_Update`, namespace-maps path, authorizes update, applies write mode, stall, and redirect, then calls `_utimes()`. `_utimes()` increments stats, takes the namespace write lock, checks write access, first attempts to treat the path as a container, sets directory mtime from `tvp[1]`, notifies directory service, and persists the container. If no container was found, it attempts file lookup, sets ctime from `tvp[0]` only when nonzero, sets mtime from `tvp[1]`, and persists file metadata.

State and persistence behavior: updates directory mtime or file ctime/mtime in metadata stores. It does not broadcast FuseX refreshes in this file, so cache coherency may be handled elsewhere or could be a gap.

Dependencies and integration points: standard XRootD utimes path through auth/mapping macros. Depends on `_access` and EOS namespace services.

Risks: `_utimes()` returns `SFS_OK` unconditionally after attempts, even if both container and file lookup failed and `errno` was set. The write lock is held while `_access()` runs, which may have its own lock behavior. Lack of explicit FuseX notification may make timestamp changes less visible to clients.

Test signals: file mtime/ctime update, ctime skipped for zero `tvp[0]`, directory mtime update and notification, write access denial, missing path behavior, namespace/auth macro behavior, and cache notification expectations.
