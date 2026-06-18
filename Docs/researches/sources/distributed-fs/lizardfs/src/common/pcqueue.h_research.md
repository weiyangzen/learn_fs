<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/pcqueue.h -->
# sources/distributed-fs/lizardfs/src/common/pcqueue.h

## Purpose
Declares the opaque C queue API and payload deleter helpers. The source was read completely for this report.

## Important APIs, Types, And Functions
`queue_deleter_dummy`, `queue_deleter_delete<T>`, and all `queue_*` functions are exported using `void*` queue handles.

## Control Flow
Header flow is limited to inline deleters that either do nothing or delete a typed payload pointer cast from `uint8_t*`.

## State And Persistence Behavior
Queue state is opaque and owned by the `.cc` implementation.

## Dependencies And Integration Points
Used by C and C++ legacy threaded components.

## Risks And Edge Cases
The `uint8_t*` payload type is untyped; callers must pair allocation and deleter correctly.

## Test Signals
Compile and multithreaded integration tests should cover API misuse boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/pcqueue.h -->
