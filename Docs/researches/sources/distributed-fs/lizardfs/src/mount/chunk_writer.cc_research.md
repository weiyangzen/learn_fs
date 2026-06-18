# sources/distributed-fs/lizardfs/src/mount/chunk_writer.cc

## Purpose
`chunk_writer.cc` implements chunk-level write execution. It batches write-cache blocks into full stripes, reads missing data for parity goals, sends writes to chunkservers through `WriteExecutor`, and tracks completion status back to write operations.

## Important APIs, Types, And Functions
- `ChunkWriter::init(locator, timeout)` creates one executor per chunk part type and sends write-init packets.
- `addOperation(WriteCacheBlock&&)` appends a writable/read block to the journal and groups compatible blocks into operations.
- `startNewOperations(can_expect_next_block)` starts operations when they are full enough and non-conflicting.
- `processOperations(msTimeout)` polls data-chain and chunkserver sockets, sends queued packets, receives statuses, and detects connection errors/timeouts.
- `finish(msTimeout)` sends end packets and returns connections to the connector.
- `abortOperations()` closes sockets immediately.
- Internal `Operation` tracks journal positions, parity buffers, unfinished writes, and end offset.
- `fillStripe`, `readBlocks`, and `computeParityBlock` materialize full stripes for XOR/EC parity writes.
- `processStatus` validates chunk ids, maps write ids to operation ids, updates file length, and erases completed journal blocks.

## Control Flow
Initialization walks master-provided locations, groups multiple chunkservers for the same part into one executor chain, computes least-common-multiple combined stripe size, opens connections, and queues `WRITE_INIT` packets under pending operation id `0`.

New write-cache blocks are converted from writable to read-only before journal insertion. Compatible blocks with the same chunk/range/stripe expand the last operation; otherwise a new operation is created. Starting operations preserves order, holds back the last partial stripe when more data is expected, and avoids overlapping pending operations to prevent parity reads from seeing stale data. `startOperation` fills missing stripe elements by reading old data, computes parity blocks for parity executors, allocates write ids for each data packet, and records the operation as pending.

`processOperations` builds a `pollfd` list for a wakeup pipe and executor sockets. It drains wakeup bytes, sends queued data on writable sockets, receives statuses on readable sockets, raises on poll/hangup/error/timeout, and delegates status completion. Finished non-init operations update locator file length and erase their journal blocks.

## State And Persistence
State is per `ChunkWriter`: connector/stat references, active locator, id counter, accept/flush mode, combined stripe size, optional data-chain fd, executor map keyed by socket fd, journal list, new operation list, write-id map, and pending operation map. Persistent effects are remote chunkserver writes and master-visible file length update later sent by `WriteChunkLocator::unlockChunk`.

## Dependencies And Integration Points
It integrates with `WriteChunkLocator`, `WriteExecutor`, `ChunkConnector`, `ChunkserverStats`, read planners/executors for read-modify-write, XOR/Reed-Solomon helpers, socket polling, request logging, and mount read-data configuration.

## Risks
- Correctness depends on operation ordering and collision detection; regressions can corrupt parity for partial-stripe writes.
- `finish` exits when timeout expires even if executors remain; callers need to treat remaining connections/pending packets carefully.
- `processOperations` throws recoverable exceptions on several transport/status failures, so higher layers must retry or abort while preserving journal data via `releaseJournal`.
- `readBlocks` uses read timeout settings from read path for write parity reads; misconfiguration affects writes.
- Manual fd ownership is split between connector-managed connections and raw `tcpclose` in abort paths.

## Test Signals
Tests should cover full-stripe write batching, partial-stripe read-fill, XOR and EC parity computation, collision blocking, status id mapping, file length update, init/end packet lifecycle, data-chain wakeups, timeout behavior, and journal release after abort.
