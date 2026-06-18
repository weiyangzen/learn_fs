<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.h

## Purpose

This header declares the chunkserver network worker thread and the per-connection state records used by the chunkserver event loop. It is the shared contract between socket polling, read/write request handling, forwarding-chain writes, background jobs, request logging, and packet output buffering.

## Important APIs, Types, and Functions

Important enums are `ChunkserverEntryMode` (`HEADER`, `DATA`) and `ChunkserverEntryState` (`IDLE`, `READ`, `GET_BLOCK`, write-chain states, and close states). `packetstruct` tracks packet memory, cursor state, and optional `OutputBuffer`. `csserventry` is the large connection state object: sockets, poll descriptor positions, header buffers, input/output packet queues, read/write job ids, forwarding state, chunk id/version/type/range, serializer, and timers. `NetworkWorkerThread` exposes `operator()()`, `askForTermination()`, `addConnection()`, and `bgJobPool()`.

## Control Flow

The worker owns a list of `csserventry` objects and repeatedly prepares poll descriptors, serves poll events, and terminates on request. Each connection advances through header/data modes and state-machine states. Write forwarding uses `fwdsock`, `fwdinitpacket`, `fwdinputpacket`, and `partiallyCompletedWrites` to synchronize local writes with downstream acknowledgements.

## State and Persistence Behavior

All state is in-memory and connection-scoped except the background job pool pointer shared with worker jobs. `csserventry` owns queued packets and output buffers but not persistent chunk data. The thread uses an atomic termination flag, a mutex-protected connection list, and a notification pipe/wakeup fd.

## Dependencies and Integration Points

It integrates with `network_stats`, `OutputBuffer`, `ChunkPartType`, `NetworkAddress`, `slice_traits`, protocol packet headers, request logging, and a `MessageSerializer`. Implementations in the chunkserver network worker and read/write handlers consume this header.

## Risks and Edge Cases

The state object mixes many ownership domains, so stale sockets, poll positions, packet pointers, or job ids can cause leaks or use-after-close behavior. Move construction is defaulted for `csserventry` even though it holds raw pointers into internal buffers and linked packet queues, so actual list operations must avoid invalid assumptions. Forwarded writes can wedge if local completion and downstream ACK tracking diverge.

## Test Signals

Useful signals are chunkserver read/write integration tests, write-chain forwarding failures, nonblocking socket close paths, worker termination under active jobs, and packet queue flushing through `OutputBuffer`. There is no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/network_worker_thread.h -->
