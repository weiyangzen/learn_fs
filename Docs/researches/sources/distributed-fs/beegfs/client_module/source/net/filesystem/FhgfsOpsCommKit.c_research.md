# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKit.c

## Purpose
Implements the generic multi-target BeeGFS storage communication engine for read, write, fsync, and stat-storage operations, including socket acquisition, message serialization, polling, retries, buddy-mirror fallback, RDMA/NVFS mapping, and cleanup.

## Important APIs and Functions
`FhgfsOpsCommKit_initEmergencyPools()`/`releaseEmergencyPools()` manage a mempool-backed 4 KiB header buffer cache. `FhgfsOpsCommkit_communicate()` is the generic state-machine driver. State initializers create file, fsync, and stat-storage target states. Specialized operation tables provide prepare/send/receive callbacks for readfile, writefile, fsync, and stat-storage. `__commkit_start_retry()` handles retry waiters, target-state checks, and buddy fallback. `__commkit_message_genericResponse()` maps server generic responses to BeeGFS errors.

## Control Flow
For each target state, the driver loops through `PREPARE`, `SENDHEADER`, optional `SENDDATA`, `RECVHEADER`, optional `RECVDATA`, `CLEANUP`, `SOCKETINVALIDATE`, `RETRYWAIT`, and `DONE`. Prepare resolves mirror group to target, validates target state, references a storage node, acquires a socket, serializes the request into a pooled header buffer, and moves to send. Polling is nonblocking when at least one state can progress and blocking only when all unfinished states wait. Cleanup releases sockets/nodes/buffers and either finishes or moves to retry wait. Read receives length-prefixed data fragments; write streams iov data and parses write responses; fsync and stat-storage only send headers and parse responses.

## State and Persistence
Per-call state is `CommKitContext` plus per-target `CommKitTargetInfo`/derived structs. It tracks acquired sockets, poll state, retry counts, bufferless/unconnectable states, selected target IDs, node results, and optional RDMA mappings. Persistent effects are remote reads/writes/fsync/stat requests and live socket pool state. Header buffer pools are module-global runtime resources.

## Dependencies and Integration Points
Depends on storage net messages, `RemotingIOInfo`, node stores, target mappers, target state stores, mirror buddy groups, socket and polling toolkit, `Config`, `Logger`, `MessagingTk`, fault injection, RDMA/NVFS APIs, and error conversion conventions. Public wrappers are called by remoting and file I/O layers.

## Risks
This is a high-risk state machine. Resource balance across socket invalidation, normal cleanup, RDMA unmap, node references, and header mempool buffers is critical. Retry behavior changes based on target reachability/consistency and can sleep/reset counters indefinitely for non-good buddy states. The `msgLength > BEEGFS_COMMKIT_MSGBUF_SIZE` path assigns `info->state = -CommKitState_SOCKETINVALIDATE`, which is suspicious because `state` is an enum of positive values and may hit the default `BUG()` path. NVFS detection casts `FileOpState` to vector state when using read/write ops, so callers must pass compatible state layouts.

## Test Signals
Use fault injection for send/receive/poll timeouts, connection acquisition failures, buffer pool exhaustion, malformed/oversized responses, generic TRYAGAIN/INDIRECTCOMMERR, target offline/needs-resync/bad states, buddy fallback, finite/infinite retries, interrupted signals, RDMA map failures, quota write headers, session-check flags, and multi-target mixed success/failure.
