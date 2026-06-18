# sources/distributed-fs/openafs/src/WINNT/afsclass/c_svr.cpp

## Purpose

`c_svr.cpp` implements `SERVER`, the cached representation of an AFS file/database server within a cell. It owns service and aggregate child caches, BOS/VOS server handles, monitor state, reachability probing, and server refresh orchestration.

## Important APIs, Types, and Functions

Important methods include constructor/destructor, `FreeAll`, `FreeAggregates`, `FreeServices`, `SendDeleteNotifications`, `GetIdentifier`, `OpenBosObject`, `CloseBosObject`, `OpenVosObject`, `CloseVosObject`, invalidation methods, `RefreshAggregates`, `RefreshServices`, `RefreshStatus`, `ShortenName`, `SetMonitor`, `CanTalkToServer`, `RefreshAll`, aggregate open/enumeration, service open/enumeration, and hash key callbacks. Static refresh-section helpers implement cancellable reachability probes.

## Control Flow

Construction captures the parent cell ID, initializes BOS/VOS handle counters, child hash lists, monitor flags, and stale flags. `OpenBosObject` and `OpenVosObject` lazily open worker handles and increment request counters; close methods decrement and close when the count reaches zero. Aggregate refresh clears current aggregates, opens VOS, enumerates partitions, creates `AGGREGATE` objects, seeds storage totals/free space, marks server-entry ghost state, and sends create notifications. Service refresh clears services, opens BOS, creates a synthetic `BOS` service, enumerates BOS process names, creates `SERVICE` objects, and notifies. `CanTalkToServer` spawns a worker thread to probe BOS and VOS quickly and allows cancellation through `AfsClass_SkipRefresh`. `RefreshAll` probes reachability, disables monitoring on failure, refreshes aggregates/filesets and services with progress notifications, then optionally triggers scoped VLDB refresh.

## State and Persistence Behavior

Server state is in-memory: names, BOS/VOS handles, request counters, ghost flags, monitor flag, last status, capability flags, child lists, stale flags, address status, and deletion marker. Persistent server configuration is external BOS/VOS/database-server state.

## Dependencies and Integration Points

The file integrates heavily with `CELL`, `AGGREGATE`, `SERVICE`, `IDENT`, `Worker_DoTask`, BOS/VOS/client worker packets, notification events, Win32 threads/critical sections, and global refresh progress state.

## Risks and Edge Cases

Handle counters must balance exactly; leaks or double-close will leave BOS/VOS handles stale. `RefreshAggregates`, `RefreshServices`, and `RefreshStatus` set `rc = FALSE` but return `TRUE`, which can mask failures. The reachability thread may keep running after cancellation, so it uses `pcsRefSec` to guard server pointers; mistakes here can become use-after-free. Monitoring off frees children and changes cell unmonitored count, so repeated toggles need careful tests.

## Test Signals

Tests should cover BOS/VOS open/close nesting, server address refresh and hash update, service/aggregate enumeration, unreachable server monitor disable, refresh cancellation, progress notifications, scoped VLDB refresh after server refresh, short/long server names, and deletion cascades.
