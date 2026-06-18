<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecycleEntry.hh -->
# sources/distributed-fs/eos/mgm/recycle/RecycleEntry.hh

## Purpose
`RecycleEntry.hh` declares a small value/operation class that models a single file or directory-tree entry being moved into the recycle bin.

## Important APIs and types
- `RecycleEntry(path, recycle_dir, rid, vid, owner_uid, owner_gid, id)` captures all data needed to recycle one namespace object. Empty `rid` means user-based recycling; non-empty `rid` means project recycling.
- `ToGarbage(epname, error)` is the public operation that moves the object into the recycle bin and reports MGM-style status.
- Private static `sMaxEntriesPerDir` controls recycle shard sizing.
- Private fields store source path, top recycle directory, recycle id string, original owner uid/gid, namespace object id, and static root identity.
- Private `GetRecyclePrefix()` computes or creates the dated shard directory.

## Control flow and state model
The class is designed for short-lived use: construct from deletion context, call `ToGarbage()`, then discard. It does not own namespace metadata directly; it delegates all side effects to the implementation through `gOFS` operations. The source path may be modified during directory recycling to remove the trailing slash.

## Persistence behavior
Persistent effects are the namespace rename into the recycle tree and creation/ownership update of recycle shard directories. The object id and original path are encoded into the destination name, while owner/project/date are encoded into directories.

## Dependencies and integration points
The declaration depends on MGM namespace definitions, `XrdOucErrInfo`, string/string_view, uid/gid types, and `VirtualIdentity`. It is consumed by user rm command implementations and pairs with `Recycle::DemanglePath()`/`Restore()` for recovery.

## Risks and test signals
The API exposes only one operation but takes several loosely typed strings and numeric ids, so caller correctness is important. The unused `vid` constructor parameter in the implementation suggests either an incomplete feature or stale signature. Tests should validate path encoding contracts against `Recycle::DemanglePath()` and ensure project recycle id behavior matches `RecycleIdSetup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecycleEntry.hh -->
