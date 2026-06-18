# sources/distributed-fs/lizardfs/src/chunkserver/chunk_replicator.cc

## Purpose
`chunk_replicator.cc` implements modern chunk replication and slice recovery for the chunkserver. It reads source chunk parts from remote chunkservers, reconstructs the requested local chunk type, writes it with `ChunkFileCreator`, and records replication statistics.

## Important APIs, Types, And Functions
- Global `ConnectionPool`, `ChunkConnectorUsingPool`, and `ChunkReplicator gReplicator` provide the default process-wide replicator.
- Constructor stores a `ChunkConnector` and default timeouts.
- `getStats` returns and resets the completed replication counter under a mutex.
- `getChunkBlocks` overload for one source sends version-aware get-blocks requests and validates responses.
- `getChunkBlocks` overload for many sources tries preferred sources first and falls back to `MFSBLOCKSINCHUNK`.
- `replicate` is the main algorithm: determine block count, build available locations, create output chunk, plan/read/write batches, commit, and increment stats.
- `incStats` increments the protected replication counter.

## Control Flow
Replication first asks sources for the number of blocks. For EC-capable sources it serializes modern EC-aware `cstocs::getChunkBlocks`; for XOR-capable pre-EC sources it serializes legacy chunk type; for old standard-only sources it serializes a MooseFS packet. Response validation checks id, version, chunk type, and OK status. Block count is adjusted for parity and data part indexing.

The main `replicate` method converts full-chunk blocks to target-slice blocks, rounds batch size to a data-part multiple, records available chunk types and network locations, and calls `fileCreator.create()`. For each batch it asks `SliceRecoveryPlanner` for a read plan, waits on `replicationBandwidthLimiter`, executes reads with `ReadPlanExecutor`, computes CRC per block, writes blocks into the output creator, and finally commits.

## State And Persistence
Persistent state is the newly replicated chunk file created through `ChunkFileCreator`. Runtime state includes pooled network connections, timeouts, per-run planner/location maps/buffers, and the replication stat counter reset by charts sampling.

## Dependencies And Integration Points
It integrates with `ChunkConnector`, connection pooling, `protocol/cstocs`, MooseFS packet helpers, `ReadPlanExecutor`, `SliceRecoveryPlanner`, `replicationBandwidthLimiter`, CRC utilities, `ChunkFileCreator`, version constants (`kFirstECVersion`, `kFirstXorVersion`), sockets, and LizardFS exceptions.

## Risks
- If all sources fail block-count probing, the fallback assumes a full chunk, which may over-read or replicate extra zero/invalid data depending on lower layers.
- Network operations use fixed 1000 ms write/read waits in `getChunkBlocks`, separate from configurable connection timeout.
- `static const SteadyDuration max_wait_time` inside `replicate` is initialized from `total_timeout_ms_` only once, so later timeout changes may not affect that static duration as intended.
- The code closes a connection on unexpected response before throwing, but other exceptions around network I/O rely on connector/socket cleanup behavior.
- The function assumes `ReadPlanExecutor` fills exactly enough bytes for `nrOfBlocks * MFSBLOCKSIZE`.

## Test Signals
No direct replicator test is listed here. Indirect signals include chart replication counts and background `job_replicate` integration. High-value tests would cover version-specific block-count protocols, partial source failure fallback, timeout setters, bandwidth limiter errors, and rollback through `ChunkFileCreator`.
