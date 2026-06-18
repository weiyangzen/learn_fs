# sources/distributed-fs/beegfs/common/source/common/storage/chunkbalancer/ChunkBalancerJobStatistics.h

## Purpose
Defines chunk-balancer job state and a serializable statistics snapshot.

## Important APIs, Types, And Functions
`ChunkBalancerJobState` enumerates not-started, starting, running, success, interrupted, failure, errors, and idle. `ChunkBalancerJobStatistics` stores status, start/end times, work queue, errors, locked inodes, migrated chunks, and worker count. `reset()` and serialization are provided.

## Control Flow
`reset()` sets `startTime` to `time(NULL)`, clears end time and counters, but leaves `status` unchanged. Serialization writes status as `int32_t` followed by counters.

## State, Persistence, And Dependencies
Value-object state only. Depends on common serialization and time from common includes.

## Integration Points
Used by chunk-balancer control/status messages and management reporting.

## Risks
Because `reset()` does not set status, callers must update status separately to avoid stale state. Field ordering in serialization is protocol-visible.

## Test Signals
Reset semantics, serialization order, all job states, and management display of status/counters should be tested.
