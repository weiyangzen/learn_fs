# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Chmod.inc

## Purpose

`Chmod.inc` implements mode changes for EOS directories and files. It exposes the XRootD `chmod` wrapper and the internal `_chmod` mutation that applies ACL/owner/admin rules, updates metadata stores, emits audit records, and broadcasts FUSE refreshes.

## Important APIs, Types, and Functions

- `XrdMgmOfs::chmod()` maps identity with `AOP_Chmod`, performs namespace mapping, external authorization, global access checks, and delegates to `_chmod`.
- `XrdMgmOfs::_chmod()` performs the actual metadata mutation for containers or files.
- For containers, it masks requested mode, strips regular-file and setuid bits, sets `S_IFDIR`, updates ctime and container store.
- For files, it stores only the nine rwx bits in file flags and updates the file store.
- Audit helpers build before/after `eos::audit::Stat` objects for `CHMOD`.

## Control Flow

The low-level function prefetches possible container and file metadata, takes a write lock on `eosViewRWMutex`, and tries directory lookup first, then file lookup. For either object, it resolves the URI to the parent container, constructs an ACL for the parent path, and checks mutability plus ownership/admin/ACL `CanChmod()`.

On success, it updates the parent store, mutates the target directory or file, captures identifiers, releases the namespace lock, and sends FUSE refreshes for the parent, target directory, or target file. It returns `SFS_OK` for either successful directory or file update; otherwise it emits `Emsg`.

## State and Persistence Behavior

The operation persists mode changes through `updateContainerStore()` or `updateFileStore()`, updates ctime for directories, updates parent container store, emits audit records when enabled and allowed, and sends FUSE refresh notifications. File mode is represented in file flags, while directory mode is represented as mode bits with `S_IFDIR`.

## Dependencies and Integration Points

Dependencies include `Acl`, `Prefetcher`, `eosViewRWMutex`, metadata services, audit helpers, FUSE xcast, external authorization, identity mapping, and global access-mode/stall/redirect macros. It is called both directly via XRootD and indirectly through auth-plugin/FSctl command dispatch.

## Risks and Edge Cases

- Permission depends on parent ACL, not only target ownership; this is important for file chmod semantics.
- Immutable ACL state blocks non-root changes.
- File chmod stores only nine permission bits, while directory chmod strips unsupported bits; callers expecting full POSIX mode preservation can be surprised.
- The function updates parent container store before target updates; partial failure paths need careful auditing in implementation changes.
- Audit construction occurs while metadata is live; before/after capture must remain aligned with persisted mutation.

## Test Signals

Tests should cover owner, root, admin uid/gid, ACL `CanChmod`, ACL `CanNotChmod`, immutable ACL, directory mode masking, file flag masking, nonexistent path, FUSE refresh targets, audit before/after records, and direct plus auth-plugin/FSctl invocation.
