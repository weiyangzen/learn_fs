# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSWrite.cpp

## Purpose
`AFSWrite.cpp` implements the write dispatch path and its completion routine. Unlike most pass-through shims, writes take a second library in-flight reference so the library cannot unload while an asynchronously completed write IRP is still outstanding.

## Important APIs, Control Flow, And State
`AFSWrite` rejects control-device writes, calls `AFSCheckLibraryState` once to guard the caller's submission, then calls it a second time to guard the lifetime of the IRP/completion pair. If the second check fails, it clears the first reference and completes or returns pending as appropriate. On success it copies the stack to the next location, installs `AFSWriteComplete` for success/error/cancel, calls the library device with `IoCallDriver`, and clears the caller's reference.

`AFSWriteComplete` clears the IRP lifetime reference with `AFSClearLibraryRequest`, preserves pending state with `IoMarkIrpPending` when `PendingReturned` is set, traces completion, and returns `STATUS_CONTINUE_COMPLETION`.

## Dependencies And Integration Points
The file depends on library unload accounting from `AFSLibrarySupport.cpp`, common completion, trace and dump helpers, and the control device extension. Actual write caching, service I/O, and file mutation semantics live in the library driver.

## Risks And Test Signals
Balancing the two in-flight references is critical; leaks block unload, undercounts permit unload during completion. Exception handling after references are taken could leave imbalance if not carefully tested. Test signals include control-device rejection, library absent on first and second checks, synchronous and pending writes, cancellation/error completion, unload waiting for write completion, and correct `PendingReturned` propagation.
