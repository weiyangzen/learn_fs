# sources/distributed-fs/openafs/src/WINNT/afsclass/c_agg.cpp

## Purpose

`c_agg.cpp` implements `AGGREGATE`, the cached representation of an AFS server partition/aggregate and the filesets hosted on it. It bridges server-side VOS partition and volume enumeration into AfsClass objects, status snapshots, ghost flags, and notifications.

## Important APIs, Types, and Functions

Key methods are the constructor/destructor, `GetIdentifier`, `Invalidate`, `InvalidateAllocation`, `RefreshStatus`, `RefreshFilesets`, `CalculateAllocation`, `OpenCell`, `OpenServer`, `OpenFileset` by name or volume ID, `FilesetFindFirst/Next/Close`, `GetStatus`, `GetGhostStatus`, and `GetID`. Hash key callbacks index `m_lFilesets` by fileset name and `VOLUMEID`.

## Control Flow

Construction captures parent server/cell identifiers, stores the partition name/device, and creates a critical-section-backed hash list with name and ID keys. `RefreshStatus` lazily calls `OpenServer`, opens a VOS object, runs `wtaskVosPartitionGet`, fills total/free storage, then computes allocated quota if allocation is stale. `RefreshFilesets` first refreshes status for the partition ID, sends begin/end notifications, deletes cached filesets with destroy notifications, enumerates VOS volumes with `wtaskVosVolumeGetBegin/GetNext/GetDone`, creates `FILESET` objects, seeds each from VOS, marks `GHOST_HAS_SERVER_ENTRY`, and invalidates allocation. `OpenFileset` and enumeration methods force refresh before returning borrowed objects under the AfsClass enter/leave reference discipline.

## State and Persistence Behavior

State is in-memory only: parent `LPIDENT`s, name/device, ghost flags, cached partition ID, status flags, `AGGREGATESTATUS`, and the fileset hash list. It does not persist data directly; it reflects server VOS state and recalculates allocated quota from read-write fileset quotas.

## Dependencies and Integration Points

The file depends on `SERVER` for VOS handles, `FILESET` for child volumes, `IDENT` for stable handles, `HASHLIST`, `Worker_DoTask`, VOS worker packet variants, string conversion helpers, and `NOTIFYCALLBACK`.

## Risks and Edge Cases

Several failure paths set `rc = FALSE` but the method returns `TRUE` at the end of `RefreshStatus` and `RefreshFilesets`, so callers relying only on the boolean may miss failures unless they inspect status and side effects. Refresh deletes and recreates all fileset objects, so stale child pointers are dangerous unless callers respect `Close` and notifications. `GetID` caches `NO_PARTITION` until name-to-ID succeeds; failure leaves later VOS requests under-specified.

## Test Signals

Tests should cover VOS partition lookup failure, empty and multi-volume aggregates, name and ID lookup after refresh, allocation recalculation using only read-write filesets, notification ordering, and ghost aggregates referenced only by VLDB.
