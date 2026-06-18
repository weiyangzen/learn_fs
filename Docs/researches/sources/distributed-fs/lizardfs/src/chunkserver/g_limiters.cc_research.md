# sources/distributed-fs/lizardfs/src/chunkserver/g_limiters.cc

## Purpose
`g_limiters.cc` defines the process-global replication bandwidth limiter singleton accessor.

## Important APIs, Types, And Functions
- `replicationBandwidthLimiter()` returns a function-local static `ReplicationBandwidthLimiter`.

## Control Flow
The first call constructs the static limiter, and later calls return the same object. C++11 thread-safe local static initialization is relied on.

## State And Persistence
Runtime state lives inside the singleton limiter. There is no persistence in this file.

## Dependencies And Integration Points
`ChunkReplicator` calls this limiter before reading/writing replication batches. Configuration code elsewhere likely adjusts limiter policy through the returned reference.

## Risks
Global mutable state can make tests and concurrent configuration harder. Lifetime lasts until process exit, so shutdown ordering must not use it after dependent static objects have gone away.

## Test Signals
No direct tests are listed.
