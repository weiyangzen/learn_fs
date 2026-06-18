<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.h

## Purpose

The header declares a minimal replication-specific API for IO bandwidth throttling.

## Important APIs, Types, and Functions

`ReplicationBandwidthLimiter` exposes `setLimit(uint64_t limit_kBps)`, `unsetLimit()`, and `wait(uint64_t requestedSize, SteadyDuration timeout)`. The nested `ReplicationLimiter` implements `ioLimiting::Limiter::request()` and owns an `IoLimitsDatabase`.

## Control Flow

Callers configure or clear a limit, then call `wait()` before replication operations. The nested limiter translates group requests into database requests using the current steady-clock time.

## State and Persistence Behavior

The limiter owns volatile limit state and a lazily created `ioLimiting::Group`; no on-disk persistence is provided.

## Dependencies and Integration Points

It integrates chunkserver replication code with `common/io_limiting.h`, `IoLimitsDatabase`, `ioLimiting::SharedState`, and `ioLimiting::Group`.

## Risks and Edge Cases

The API has no explicit synchronization around `setLimit()`/`unsetLimit()` versus `wait()` except the wait mutex in the implementation, so callers should avoid racing configuration changes with active transfers unless `ioLimiting` guarantees safety. Unit conversion is KiB/s as documented, not bytes/s.

## Test Signals

Tests should assert status codes for no-limit, limited, timed-out, and limit-cleared scenarios and should include concurrent waiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.h -->
