## sources/distributed-fs/beegfs/storage/source/components/worker/StorageBenchWork.cpp

### Purpose
`StorageBenchWork.cpp` executes one storage benchmark unit on a worker thread. It reads from or writes to an already-open file descriptor and reports completion or failure to the benchmark operator through a pipe.

### Important APIs, Types, And Functions
`StorageBenchWork::process()` switches on `StorageBenchType_READ` or `StorageBenchType_WRITE`. It uses config tuneables `tuneFileReadSize` and `tuneFileWriteSize` to split `bufLen` into repeated `read()` or `write()` calls. It updates node operation stats for read/write ops and writes either `threadID` or `STORAGEBENCH_ERROR_WORKER_ERROR` to `operatorCommunication`.

### Control Flow, State, And Persistence
The work object owns a file descriptor, buffer pointer, buffer length, target ID, type, virtual thread ID, and pipe. Persistent effects are benchmark reads/writes on the target file and operation counters. Short I/O breaks the loop; only `ioRes == -1` logs the underlying system error.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with `StorageBenchOperator`, `Work` queues, config tuneables, `NodeOpStats`, and `Pipe`. Risks include treating short positive I/O as success, not retrying interrupted system calls, raw buffer lifetime ownership outside the object, and no target-specific stats beyond counters. Tests should cover read, write, unknown type, pipe notification, short I/O, and system-call failures.
