# sources/distributed-fs/openafs/src/WINNT/afsclass/c_set.cpp

## Purpose

`c_set.cpp` implements `FILESET`, the cached representation of an AFS volume/fileset on an aggregate. It tracks VOS status, volume IDs, type/state, ghost status, and identifier relationships to read-write/read-only/backup variants.

## Important APIs, Types, and Functions

Key methods include constructor/destructor, `GetIdentifier`, `GetReadWriteIdentifier`, `GetReadOnlyIdentifier`, `GetCloneIdentifier`, `Invalidate`, `RefreshStatus`, parent open methods, `GetStatus`, `GetGhostStatus`, `ProbablyReplica`, and `SetStatusFromVOS`.

## Control Flow

Construction captures parent aggregate/server/cell identifiers, stores the volume ID and name, initializes status, and invalidates aggregate allocation. `GetIdentifier` searches existing file-set identifiers by volume ID and reuses an unreferenced match in the same cell, requiring the same aggregate for probable read-only replicas, then updates moved fileset location/name fields before incrementing refcount. `RefreshStatus` only queries VOS when stale and the fileset has a server-entry ghost flag, opens server and VOS handles, optionally resolves partition ID from the parent aggregate, calls `wtaskVosVolumeGet`, updates status via `SetStatusFromVOS`, and invalidates aggregate allocation. Variant identifier methods refresh and find read-write/read-only/backup identifiers by IDs or `.readonly` naming.

## State and Persistence Behavior

State is an in-memory snapshot of VOS volume metadata and VLDB-derived bits. Persistent volume state is external. The object invalidates parent allocation when quota/status changes can affect aggregate accounting.

## Dependencies and Integration Points

The file depends on `AGGREGATE`, `SERVER`, `CELL`, `IDENT`, VOS worker packets, `NOTIFYCALLBACK`, AfsClass time conversion, and file-set type/state constants from the header.

## Risks and Edge Cases

`RefreshStatus` returns `TRUE` even after setting `rc = FALSE`, matching a recurring pattern in this code. Filesets that exist only in VLDB (`GHOST_HAS_VLDB_ENTRY` without server entry) do not query VOS and may retain VLDB-only status. `ProbablyReplica` relies on `.readonly` naming, while real identity constraints are volume-ID based.

## Test Signals

Tests should cover VOS status mapping for all volume states, read-write/read-only/backup ID lookup, moved fileset identity reuse, VLDB-only ghost status, aggregate allocation invalidation, and failures opening server/VOS handles.
