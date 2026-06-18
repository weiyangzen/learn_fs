# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Mkdir.inc

## Purpose

`Mkdir.inc` implements directory creation for EOS, including normal and recursive `SFS_O_MKPTH` creation. It enforces ACL/POSIX/token permissions, supports `sys.owner.auth` ownership rewriting, inherits parent mode and attributes, records birth time, updates stores and mtime notifications, emits FUSE broadcasts, and audits successful mkdirs.

## Important APIs, Types, and Functions

- `XrdMgmOfs::mkdir(inpath,Mode,error,client,ininfo,outino)` is the public wrapper with identity mapping and path/access gates.
- `XrdMgmOfs::_mkdir(path,Mode,error,vid,ininfo,outino,nopermissioncheck)` performs the actual creation.
- Permission logic uses parent or nearest existing ancestor attributes, `attr::checkDirOwner()`, `Acl`, POSIX `dir->access(X_OK|W_OK)`, immutable checks, explicit ACL `!w`, write-once/write grants, token denial, and optional `nopermissioncheck`.
- Recursive creation walks upward to find the nearest existing ancestor and then creates each missing component.

## Control Flow

The public wrapper maps identity with `AOP_Mkdir`, applies namespace mapping, token scope, global access checks, and calls `_mkdir`. `_mkdir` rejects non-absolute paths, resolves the parent, loads effective parent attributes before ACL construction, applies `sys.owner.auth` ordering so keyed owner auth can rewrite `vid` before permission checks and sticky `*` can rewrite ownership after permission checks.

If `SFS_O_MKPTH` is set and the full path already exists, it returns success. If the parent is missing and recursive mode is set, it finds the closest existing ancestor, repeats permission checks there, applies sticky ownership if needed, and creates each missing subpath under a write lock, inheriting mode and attributes from the current parent, setting mtime/btime, updating stores, notifying mtime changes, releasing the lock, and broadcasting FUSE metadata/refresh messages.

For the final directory, it write-locks the namespace, creates the container, sets uid/gid, inherits parent mode without the VTX bit, sets mtime and `sys.eos.btime`, inherits parent attributes except for version directories, optionally returns the new inode, commits parent and child stores, notifies mtimes, releases the lock, xcasts metadata and parent refresh, audits, and returns `SFS_OK`.

## State and Persistence Behavior

Mkdir persists new container metadata, parent mtime updates, inherited attributes, `sys.eos.btime`, uid/gid, and mode through `eosView->updateContainerStore()`. It notifies the directory service of mtime changes, emits `FuseXCastMD` and `FuseXCastRefresh`, and writes an audit record with a trailing slash path. Recursive mkdir can create multiple persistent containers.

## Dependencies and Integration Points

Dependencies include identity mapping, token authorization, namespace mapping, `Prefetcher`, `Acl`, `attr::checkDirOwner`, namespace locks, metadata stores, FUSE xcast, audit protobuf, and global access/stall/redirect macros. It is used by direct XRootD mkdir, auth-plugin requests, FSctl `mkdir`, and internal code that may set `nopermissioncheck`.

## Risks and Edge Cases

- The ordering around `sys.owner.auth` is security-sensitive and documented in comments; changes can alter both permission and ownership semantics.
- Recursive creation repeats permission checks at the nearest ancestor, then inherits attrs/mode at each level; inherited ACLs can change behavior for subsequent components.
- Explicit ACL `!w` must override POSIX permissions for non-sudo users.
- Version directories intentionally do not inherit attributes in the final branch.
- Partial recursive creation can leave earlier components if a later component fails.
- `nopermissioncheck` bypasses permission checks but still creates persistent metadata, so callers must be trusted.

## Test Signals

Tests should cover absolute-path validation, normal mkdir, recursive mkdir with existing final path, missing parent without recursive flag, parent immutable denial, ACL write/write-once/`!w` cases, POSIX XW denial, token denial, keyed and sticky `sys.owner.auth`, uid/gid/mode inheritance, attribute inheritance and version-directory exception, `sys.eos.btime`, `outino`, partial recursive failure behavior, audit path formatting, and FUSE notifications.
