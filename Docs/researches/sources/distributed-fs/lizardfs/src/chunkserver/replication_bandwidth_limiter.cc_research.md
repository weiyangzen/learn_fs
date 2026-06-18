<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.cc

## Purpose

This file implements the chunkserver replication bandwidth limiter by wrapping the common `ioLimiting` framework with one logical group named `replication`.

## Important APIs, Types, and Functions

Implemented methods are `ReplicationBandwidthLimiter::ReplicationBandwidthLimiter()`, `setLimit()`, `unsetLimit()`, `wait()`, nested `ReplicationLimiter::request()`, `setLimit()`, and `unsetLimit()`. A static `mutex_` serializes waits.

## Control Flow

Construction initializes shared IO-limiter state with a 20 ms update interval. `setLimit()` programs the database limit in KiB/s and lazily creates a `Group`. `unsetLimit()` drops the group and clears limits. `wait()` returns immediately if no group exists; otherwise it locks the static mutex and delegates to `Group::wait()` with an absolute deadline.

## State and Persistence Behavior

State is in-memory: `IoLimitsDatabase`, `RTClock`, shared state, optional group, and a class-wide mutex. Limit changes are not persisted.

## Dependencies and Integration Points

It depends on `common/io_limiting.h` and LizardFS status codes. Replication paths should call `wait()` before transferring requested bytes.

## Risks and Edge Cases

The static mutex serializes waits across all limiter instances, which is simple but can reduce concurrency. `setLimit()` updates database state but does not recreate an existing group, so correctness relies on the shared state seeing database updates. A limit of zero or very small timeout behavior is delegated to `ioLimiting`.

## Test Signals

Expected tests should verify immediate success without a limit, delayed or timed-out waits with limits, concurrent wait serialization, `unsetLimit()` recovery, and runtime limit updates. No direct test is in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/replication_bandwidth_limiter.cc -->
