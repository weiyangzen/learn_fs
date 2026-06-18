# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSShutdown.cpp

## Purpose
`AFSShutdown.cpp` provides the `IRP_MJ_SHUTDOWN` dispatch handler for the redirector library. The current `AFSShutdownFilesystem` helper is empty and returns success, so the dispatch path is primarily a compatibility hook.

## Important APIs, Types, And Functions
The exported functions are `AFSShutdown(PDEVICE_OBJECT, PIRP)` and `AFSShutdownFilesystem(void)`. `AFSShutdown` calls `AFSShutdownFilesystem`, normalizes any failure back to `STATUS_SUCCESS`, completes the IRP with `AFSCompleteRequest`, and returns.

## Control Flow
Shutdown handling is success-biased: even if future shutdown work returns an error, `AFSShutdown` currently replaces it with success. Exceptions are logged and trace files are dumped.

## State And Persistence Behavior
No state is mutated. The file does not set shutdown flags, flush extents, drain workers, close cache files, tear down volumes, or notify the service. Such behavior must occur elsewhere if required.

## Dependencies And Integration Points
The handler integrates with the driver's major-function table for system shutdown and depends on common tracing, exception filtering, and IRP completion.

## Risks And Edge Cases
False success is the main risk if real shutdown work is added later. As written, this path should not be assumed to protect cache consistency or volume teardown ordering.

## Test Signals
Test `IRP_MJ_SHUTDOWN` completion and exception-free behavior. If shutdown work is implemented later, add tests for flush ordering, worker quiescence, volume teardown, failure policy, and read/write races.
