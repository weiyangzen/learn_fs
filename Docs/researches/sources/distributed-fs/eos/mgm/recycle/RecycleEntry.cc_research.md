<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecycleEntry.cc -->
# sources/distributed-fs/eos/mgm/recycle/RecycleEntry.cc

## Purpose
`RecycleEntry.cc` implements the object-level move-to-recycle operation used when a file or directory tree is deleted but should be recoverable. It computes the dated recycle-bin shard, creates it if necessary, fixes ownership, mangles the original path into a flat name, and renames the namespace object into the recycle area.

## Important APIs and functions
- Static `sMaxEntriesPerDir` limits one shard directory to 100000 entries before advancing the shard index.
- Static `mRootVid` is used for unrestricted MGM filesystem operations.
- The constructor stores original path, top recycle directory, owner ids, object id, and builds `mRecycleId` as `uid:<owner>` for user recycling or `rid:<rid>` for project recycling. It strips a trailing slash from `mRecycleDir`.
- `GetRecyclePrefix()` builds `<recycle-dir>/<uid|rid>/<YYYY>/<MM>/<DD>/<index>`, reuses an existing shard if not over the entry limit, otherwise creates it with root privileges and changes ownership to the original owner.
- `ToGarbage()` detects directory-tree recycling by a trailing slash, replaces every `/` in the original path with `#:#`, appends the 16-hex namespace id and `.d` for directories, then calls `_rename()` into the computed recycle prefix.

## Control flow
Deletion code constructs `RecycleEntry` with the path, recycle directory, optional project id, virtual identity pointer, owner uid/gid, and file/container id. `ToGarbage()` normalizes directory paths, computes a reusable or new dated shard via `GetRecyclePrefix()`, constructs the final recycle path, and performs one namespace rename. On success, it stores the recycle path in the error object as informational output.

## State and persistence
This file persists recycle state by moving the object in the namespace. No separate metadata record is written here; the encoded file name contains the original path and object id, and the directory layout contains owner/project and deletion date. Ownership of shard directories is updated to the deleted object's original owner/group.

## Dependencies and integration points
It depends on `Recycle.hh` for postfix constants, `XrdMgmOfs` for `_stat`, `_mkdir`, `_chown`, and `_rename`, `VirtualIdentity::Root()`, and XRootD error handling. Callers found in `proc/user/Rm.cc` and `proc/user/RmCmd.cc` invoke `ToGarbage()` for recursive removals.

## Risks and edge cases
- `GetRecyclePrefix()` checks `buf.st_blksize > sMaxEntriesPerDir` to decide shard fullness. `st_blksize` is normally filesystem block size, not entry count; if EOS overloads this value in `_stat`, that should be documented, otherwise sharding may not work as intended.
- Path mangling is reversible only because restore strips the final `.16hex` and optional `.d`; original names containing `#:#` sequences can be ambiguous after demangling.
- The constructor accepts but does not use the `VirtualIdentity* vid` parameter.
- All work uses root identity; safety relies on caller authorization and destination prefix correctness.
- A rename failure leaves the original object in place and returns an MGM error; a prefix creation/chown failure may leave empty directories behind.

## Test signals
No direct `RecycleEntry` tests were found. Existing recycle demangle tests cover the reverse name format partially. Valuable tests would include file versus directory postfix construction, project versus user recycle id construction, shard rollover behavior, ownership update failure, and rename error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecycleEntry.cc -->
