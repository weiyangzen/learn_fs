# sources/distributed-fs/lizardfs/src/chunkserver/g_limiters.h

## Purpose
`g_limiters.h` declares the global accessor for chunkserver replication bandwidth limiting.

## Important APIs, Types, And Functions
- `ReplicationBandwidthLimiter& replicationBandwidthLimiter();`

## Control Flow
Consumers call the accessor when they need to wait for or configure replication bandwidth budget.

## State And Persistence
No state in the header. The implementation returns a process-global limiter.

## Dependencies And Integration Points
It includes `replication_bandwidth_limiter.h`. `chunk_replicator.cc` depends on it directly.

## Risks
The accessor exposes mutable global state by non-const reference. Misconfiguration in one module affects all replication operations.

## Test Signals
No direct tests are listed.
