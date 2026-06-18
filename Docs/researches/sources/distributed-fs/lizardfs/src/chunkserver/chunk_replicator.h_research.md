# sources/distributed-fs/lizardfs/src/chunkserver/chunk_replicator.h

## Purpose
`chunk_replicator.h` declares the `ChunkReplicator` class and the global `gReplicator` used by chunkserver background jobs and chart collection.

## Important APIs, Types, And Functions
- Default timeout constants for total replication, per-wave execution, and connection setup.
- Constructor takes a `ChunkConnector&` for dependency injection.
- `replicate(ChunkFileCreator&, const std::vector<ChunkTypeWithAddress>&)` performs replication.
- `getStats` returns/reset replication count.
- Timeout setters adjust total, wave, and connection timeouts.
- Private `getChunkBlocks` overloads determine source block count.
- Private `incStats` records successful replication.
- Fields include `ChunkserverStats`, connector reference, stats counter, mutex, and timeouts.

## Control Flow
Callers create or use a global replicator, optionally set timeouts, then call `replicate` with an output creator and source locations. Stats are sampled separately through `getStats`.

## State And Persistence
The class owns no chunk file directly; persistence is delegated to `ChunkFileCreator`. Runtime mutable state is the stats counter and timeout values.

## Dependencies And Integration Points
It includes creator, recovery planner, connector, chunk type/address, chunkserver stats, and exception headers. `bgjobs.cc` uses `gReplicator` for `job_replicate`, and `chartsdata.cc` samples its stats.

## Risks
The class stores a connector reference, so connector lifetime must outlive the replicator. Timeout setters are unsynchronized relative to concurrent replication calls.

## Test Signals
No direct tests are listed for this header/class.
