## sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchSlave.h

Purpose: Declares the benchmark worker thread and per-virtual-thread data structures.

Important APIs/types/functions: `StorageBenchThreadData` tracks target, virtual thread ID, engaged bytes, file descriptor, and elapsed time. `TransferDataDeleter` frees aligned buffers. `StorageBenchSlave` derives from `PThread` and exposes benchmark start, cleanup, stop, status/result, shutdown, and wait methods. Private helpers implement initialization, IO file handling, package sizing, and result aggregation.

Control flow: Header defines `setStatus()` to update status under `statusMutex` and broadcast `statusChangeCond`. Inline getters expose last error, status, type, and target IDs.

State and persistence: Owns pipe, status mutex/condition, status fields, target list pointer, thread-data map, transfer buffer, and timing. Disk persistence occurs in cpp through benchmark files.

Dependencies and integration: Uses BeeGFS benchmark common definitions, `PThread`, `Condition`, `Pipe`, `TimeFine`, and logging. Driven by `StorageBenchOperator`.

Risks and test signals: Destructor deletes `targetIDs` but lifecycle reuse must manage previous allocations. Status access is partly locked (`getType()` is not), so concurrent reads during init may race. Tests should include thread-safety and lifecycle reuse.
