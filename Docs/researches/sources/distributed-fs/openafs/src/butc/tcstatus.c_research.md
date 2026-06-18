# sources/distributed-fs/openafs/src/butc/tcstatus.c

## Purpose
`tcstatus.c` implements TC status RPCs for polling, scanning, aborting, and ending task status nodes, plus local helpers for worker abort/status checks.

## Important APIs, Types, and Functions
Globals are `statusHead`, `statusQueueLock`, and `cmdLineLock`, used by shared status implementation. RPC wrappers are `STC_GetStatus()`, `STC_EndStatus()`, `STC_RequestAbort()`, and `STC_ScanStatus()`. Static implementations perform permission checks and queue operations. `checkAbortByTaskId()` tests `ABORT_REQUEST`; `getStatusFlag()` tests arbitrary flags.

## Control Flow
`SGetStatus()` copies one status node and refreshes `lastPolled`. `SEndStatus()` deletes a status node. `SRequestAbort()` sets `ABORT_REQUEST`. `SScanStatus()` returns first/next status node depending on `TSK_STAT_FIRST`, sets end/not-found flags, and annotates XBSA/ADSM mode flags.

## State and Persistence Behavior
All status state is volatile. Workers update task name, volume name, progress, failure count, wait/done/error/abort flags, and dump id. Abort is cooperative and observed only when workers call `checkAbortByTaskId()`.

## Dependencies and Integration Points
Depends on `callPermitted()`, runtime XBSA configuration, shared `bucoord/status.c`, audit events, and worker code in dump/restore/scan/DB paths.

## Risks and Test Signals
Risks include unlock-before-delete in `SEndStatus()`, scan instability when tasks change, `SScanStatus()` returning fewer fields than `SGetStatus()`, and delayed abort during blocking I/O. Test existing/missing polling, abort propagation, no/one/many task scans, changing task sets, XBSA/ADSM flags, permissions, and end-status races.
