<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats.cc -->
# sources/distributed-fs/lizardfs/src/common/chunkserver_stats.cc

## Purpose

This file implements thread-safe per-chunkserver pending-operation and defect scoring, plus a proxy that auto-unregisters operations.

## Important APIs, Types, and Functions

Implemented methods include `ChunkserverEntry::ChunkserverEntry()`, `score()`, `ChunkserverStats` register/unregister/get/mark methods, and all `ChunkserverStatsProxy` methods including destructor and `allPendingDefective()`.

## Control Flow

`ChunkserverStats` methods lock a mutex and update or return a copy of the entry for an address. Defects increment up to 1000 and reset a timeout; `score()` returns reduced score while the defect timeout is active. The proxy registers operations in both global stats and local maps, and its destructor unregisters all locally pending counts.

## State and Persistence Behavior

Stats are in-memory only. `globalChunkserverStats` is declared in the header but not defined in this file segment. Defect state decays by timeout rather than persistence.

## Dependencies and Integration Points

It depends on `NetworkAddress`, `Timeout`, mutex/unordered_map, and chunkserver selection/read/write code.

## Risks and Edge Cases

Unregister methods decrement unsigned counters without underflow checks. Proxy `unregister*()` decrements local map counters even if not present, which can underflow and cause destructor over-unregistration. `getStatisticsFor()` creates entries on read.

## Test Signals

`chunkserver_stats_unittest.cc` covers counters, defect score, proxy cleanup, and marking pending operations defective.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats.cc -->
