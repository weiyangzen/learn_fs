# sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.cc

## Purpose
`network_worker_thread.cc` implements per-connection chunkserver protocol handling. Each `NetworkWorkerThread` owns a poll loop, a background HDD job pool, and a list of client/peer connections. It serves reads, writes, prefetches, HDD info, charts, chunk tests, get-blocks requests, and chained write forwarding to another chunkserver.

## Important APIs, Types, and Functions
The file defines protocol serializers (`MessageSerializer`, `MooseFsMessageSerializer`, `LizardFsMessageSerializer`), packet allocation/attachment helpers, read handlers (`worker_read_init`, `worker_read_continue`, `worker_read_finished`), write handlers (`worker_write_init`, `worker_write_data`, `worker_write_status`, `worker_write_end`, `worker_write_finished`), forwarding handlers (`worker_initconnect`, `worker_fwdwrite`, `worker_forward`, `worker_fwdread`), misc handlers for ping/HDD list/chart/test/get-blocks, and the `NetworkWorkerThread` methods declared in the header.

## Control Flow
Accepted sockets arrive through `NetworkWorkerThread::addConnection`, which sets TCP options, creates a `csserventry`, and wakes the worker pipe. The thread loop calls `preparePollFds`, polls with a short timeout, drains job completions, and calls `servePoll`. Each connection has a state machine: `IDLE` accepts new commands; `READ` schedules block reads and queues read-data/status packets; `GET_BLOCK` waits for `job_get_blocks`; `WRITELAST` writes locally; `CONNECTING`/`WRITEINIT`/`WRITEFWD` set up and operate a chained write to another chunkserver; `WRITEFINISH` sends final error/success status before closing; close states disable or wait for jobs and release resources.

Read requests are split at block boundaries. The worker builds a response prefix, schedules `job_read` with optional open/read-ahead/read-behind, then sends each output buffer and finally an OK read status while closing the chunk. Write init deserializes a chain, optionally connects to the next chunkserver and forwards the remaining chain init, opens the local chunk, and transitions to local or forwarded write mode. Write data is preserved from the input packet while an HDD write job runs; local completion and forwarded status are matched with `partiallyCompletedWrites` before the upstream client is acked.

## State and Persistence Behavior
Per-connection runtime state includes sockets, packet buffers, output queues, active job IDs, forwarded socket buffers, write IDs awaiting local/remote completion, open chunk flag, chunk identity/type/version, read offset/size, and serializer selection. Persistent effects happen through bgjob calls into `hddspacemgr` for open/read/write/close/prefetch/get-blocks and through forwarded write chains on peer chunkservers. Termination closes open chunks, sockets, and allocated buffers, and deletes the job pool.

## Dependencies and Integration Points
The implementation depends on bgjobs, HDD manager and read-ahead settings, network stats, chart generation, protocol serializers for MooseFS and LizardFS packet variants, socket wrappers, event-loop time helpers, and request logging. `network_main_thread.cc` owns worker creation and dispatch. Legacy replication uses get-blocks/read protocol paths served here.

## Risks and Edge Cases
This is a high-risk state machine. Packet ownership alternates between raw `malloc` buffers, preserved input packets, linked output packets, and `OutputBuffer` objects. Write-chain correctness depends on matching local HDD completion with downstream status by write ID. Closing while a bgjob is active changes callbacks to delayed close, so callback identity and `chunkisopen` must stay consistent. Forwarded packets include headers for write data/end but local processing consumes payloads differently in forwarded vs non-forwarded paths. Timeout/retry logic can close slow but valid clients after `CSSERV_TIMEOUT`.

## Test Signals
Protocol tests should cover legacy and LizardFS read/write variants, EC chunk type deserialization, block-boundary read splitting, partial write validation, write-chain success and downstream failure, premature `WRITE_END`, get-blocks responses, prefetch fire-and-forget, HDD list serialization, and chart requests. Stress tests should exercise connection close during active read/write/get-block jobs, forwarded reconnect retries, packet-too-large rejection, network stats accounting, and leak checks for all packet ownership paths.
