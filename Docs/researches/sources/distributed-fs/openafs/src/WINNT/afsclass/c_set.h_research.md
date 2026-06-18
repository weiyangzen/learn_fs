# sources/distributed-fs/openafs/src/WINNT/afsclass/c_set.h

## Purpose

`c_set.h` declares `FILESET`, the AfsClass wrapper around an AFS volume/fileset.

## Important APIs, Types, and Functions

It defines `FILESETSTATE` bit flags for VOS and VLDB states, `FILESETTYPE` for read-write, replica, and clone, and `FILESETSTATUS` with IDs, timestamps, file count, quota, usage, type, and state. `FILESET` exposes close/invalidate/refresh, parent navigation, identifier getters for related variants, name/ID/status/ghost getters, and user-param accessors.

## Control Flow

The header declares a lazy-refresh object. Status refresh pulls server data, while `RefreshStatus_VLDB` is declared for VLDB refresh integration even though this source set does not show an implementation in `c_set.cpp`.

## State and Persistence Behavior

The class caches volume identity, parent identities, ghost flags, stale status, and the last `FILESETSTATUS`. Durable volume state remains in VOS/VLDB.

## Dependencies and Integration Points

It integrates with `CELL`, `SERVER`, `AGGREGATE`, `IDENT`, `VOLUMEID`, `SYSTEMTIME`, and ghost-state handling performed by `CELL::RefreshVLDB`.

## Risks and Edge Cases

Status bit masks reserve high bits for VLDB state; callers must preserve `fsMASK_VLDB` when updating VOS status. Missing or separately implemented `RefreshStatus_VLDB` should be checked during linking or broader-source review.

## Test Signals

Compile checks should validate `FILESETSTATUS` layout and that all declared methods link. Runtime tests should verify type/state mapping, related identifier lookup, and ghost-status visibility.
