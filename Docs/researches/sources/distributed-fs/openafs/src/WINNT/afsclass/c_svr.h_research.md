# sources/distributed-fs/openafs/src/WINNT/afsclass/c_svr.h

## Purpose

`c_svr.h` declares `SERVER`, the AfsClass object for a server in a cell, including cached child aggregate/service lists and BOS/VOS handle management.

## Important APIs, Types, and Functions

`SERVERSTATUS` stores up to `AFSCLASS_MAX_ADDRESSES_PER_SITE` socket addresses. Public APIs include close, invalidation, refresh of status/services/aggregates/all, `ShortenName`, monitor get/set, identity/name/status/ghost/user-param accessors, BOS/VOS object open/close, aggregate open/enumeration, and service open/enumeration. Private members store parent cell identity, handles, counters, ghost/monitor state, child hash lists, capability flags, stale flags, status, and deletion marker.

## Control Flow

The header describes a lazy, monitored server cache. When monitoring is disabled, child data is freed and refreshes are skipped; when enabled, refresh can repopulate services, aggregates, filesets, and VLDB-derived information.

## State and Persistence Behavior

Server state is a process-local cache and live worker-handle holder. Persistent server configuration and volume state remain in AFS services.

## Dependencies and Integration Points

It depends on `afsclass.h`, socket structures, `HASHLIST`, `SERVICE`, `AGGREGATE`, `IDENT`, and Win32 worker-thread support in the implementation.

## Risks and Edge Cases

The class combines cache ownership, handle reference counting, and refresh threading, so lifetime correctness depends on balanced `Open*Object`/`Close*Object` and `Open*`/`Close` pairs. `m_fVLDBOutOfDate` is noted in the implementation as a missing-field fix, suggesting historical state consistency risk.

## Test Signals

Compile tests should validate class layout and method linkage. Runtime tests should cover monitor toggling, child enumeration, handle nesting, status address limits, and refresh-all progress/cancel behavior.
