# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Exists.inc

## Purpose

`Exists.inc` implements XRootD/OFS existence checks for EOS paths. It distinguishes directories, files, and missing paths, supports high-level authorization and redirection behavior, and provides lower-level overloads that return metadata handles for internal callers.

## Important APIs, Types, and Functions

- `XrdMgmOfs::exists()` is the public XRootD wrapper with identity mapping, namespace mapping, external authorization, and access-mode/stall/redirect guards.
- `_exists(path, file_exists, error, client, ininfo)` is a lower-level overload that may still issue ENOENT redirects and therefore is documented as not for internal use.
- `_exists(path, file_exists, error, vid, cmd, fmd, ininfo)` returns shared pointers to found container or file metadata without ENOENT redirect handling.
- `_exists(fileName, exists_flag, out_error, vid, opaque, take_lock)` is a wrapper that creates metadata out-params.

## Control Flow

The public wrapper maps the path and identity, checks external authorization for `AOP_Stat`, applies access gates, and calls `_exists`. The client-based lower-level overload first rejects null/empty paths, then prefetches and checks for a container, then prefetches and checks for a file. If missing, it looks up the parent directory, loads parent attributes via `_attr_ls`, and if `sys.redirect.enoent` exists, parses optional host:port and returns `SFS_REDIRECT`.

The identity-based overload uses the same directory-first, file-second lookup but returns only `SFS_OK` and an enum flag with optional metadata pointers. It does not emit ENOENT redirects.

## State and Persistence Behavior

This file is read-only. It updates `MgmStats` for existence checks and ENOENT redirects. It fills caller-provided shared pointers to live metadata objects but does not mutate them.

## Dependencies and Integration Points

Dependencies include identity mapping, external authorization, namespace prefetch, `eosView`, `_attr_ls`, `XrdSfsFileExistence`, stall/redirect macros, and MGM stats. It is used by mkdir, symlink, FSctl locate, find fallback, auth-plugin exists requests, and many internal checks that need file-versus-directory classification.

## Risks and Edge Cases

- The client-based overload can redirect on missing paths via parent `sys.redirect.enoent`; internal callers should use the `VirtualIdentity` overload when redirects are inappropriate.
- Directory lookup wins over file lookup if both somehow exist for a path.
- Null/empty path returns `SFS_ERROR` without setting detailed `XrdOucErrInfo`.
- Parent attribute lookup during ENOENT handling can itself fail silently and skip redirect.

## Test Signals

Tests should cover existing directory, existing file, missing child with and without parent, ENOENT redirect host/port parsing, empty path, auth denial, no-symlink lookup behavior from `false` flags, metadata out-params, and callers that must avoid redirects.
