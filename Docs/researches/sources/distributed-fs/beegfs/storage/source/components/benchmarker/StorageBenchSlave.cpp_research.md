## sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchSlave.cpp

Purpose: Implements storage benchmark execution by creating per-target files, dispatching read/write work to normal worker queues, tracking worker completions via a pipe, and reporting throughput.

Important APIs/types/functions: `initAndStartStorageBench()` validates inactive status, initializes, starts the thread, and transitions status. `initStorageBench()` stores parameters, initializes thread data/transfer buffer, validates read data or creates write dirs. `run()` opens files, enqueues `StorageBenchWork`, reads worker responses, handles abort/errors, closes files, frees buffers, and sets final status. Other helpers create/check benchmark dirs, open/close files, compute package sizes and throughput, cleanup files, stop/shutdown/wait, and return status/results.

Control flow: For each target/thread pair, `initThreadData()` creates a virtual thread record. `run()` enqueues one work item per record, then each worker response causes the next package to be queued until `size` is reached. Stop/error paths set `STOPPING`, collect outstanding responses while workers run, then map to `ERROR` or `STOPPED`.

State and persistence: Maintains benchmark status, type, block size, total size, thread count, target ID list, per-thread file descriptors/progress/time, aligned random transfer buffer, pipe, and start time. Persists benchmark data under `<targetPath>/benchmark/<targetThreadID>`; `cleanup()` deletes regular files in that directory.

Dependencies and integration: Uses `Program::getApp()` for targets, workers, and work queues; `StorageBenchWork` for actual IO; `StorageTk` and POSIX file APIs; BeeGFS benchmark enums/errors/status types.

Risks and test signals: `targetIDs` is overwritten with `new auto(*targetIDs)` without deleting any previous list, so repeated initializations after finished runs may leak. `threadData[threadID]` in `getNextPackageSize()` assumes valid IDs. O_DIRECT requires block-aligned size and offsets; only buffer alignment is enforced here. Tests should cover repeated benchmark runs, stop during active IO, worker error response, read-before-write validation, cleanup with non-regular files, unknown target handling, and O_DIRECT parameter validation.
