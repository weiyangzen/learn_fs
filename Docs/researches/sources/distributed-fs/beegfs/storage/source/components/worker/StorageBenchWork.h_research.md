## sources/distributed-fs/beegfs/storage/source/components/worker/StorageBenchWork.h

### Purpose
`StorageBenchWork.h` declares the benchmark work item queued to BeeGFS workers. It packages all state needed to perform a read or write benchmark operation.

### Important APIs, Types, And Functions
The constructor records target ID, virtual thread ID, file descriptor, benchmark type, buffer length, operator communication pipe, and buffer pointer. The override `process()` performs the actual I/O in the `.cpp`.

### Control Flow, State, And Persistence
The header stores raw non-owning resources: `fileDescriptor`, `Pipe*`, and `char* buf`. The work item does not own cleanup; it only signals completion through the pipe after processing.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageBench`, `Work`, `Pipe`, and common BeeGFS types. Risks include lifetime/ownership assumptions for the FD, buffer, and pipe, plus no copy/move restrictions despite raw handles. Tests should validate object construction, worker dispatch, and operator communication around success and failure paths.
