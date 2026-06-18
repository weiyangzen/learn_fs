# sources/distributed-fs/eos/mgm/tgc/TapeGcStats.hh

## Purpose
Defines the snapshot structure returned by a tape-aware GC for monitoring and command output.

## Important APIs, types, and functions
`TapeGcStats` has a default constructor that initializes `nbEvicts`, `lruQueueSize`, and `queryTimestamp` to zero. It carries `SpaceStats spaceStats` plus counters for successful evictions and queued LRU entries.

## Control flow
`TapeGc::getStats()` fills this struct from the collector counter, LRU size, `SmartSpaceStats::get()`, and query timestamp. A default-constructed value is used as the fallback on error.

## State and persistence behavior
This is transient reporting state only. It mirrors runtime counters and cached space stats; it does not persist or own resources.

## Dependencies and integration points
Depends on `SpaceStats` and `Lru::FidQueue::size_type` from the TGC subsystem. `SpaceToTapeGcMap::getStats()` aggregates one instance per space.

## Risks and test signals
Zero is both a valid value and the error sentinel for multiple fields, so consumers need context to distinguish "no evictions" from "failed to query." Tests should cover normal population and fallback defaults when `TapeGc::getStats()` catches exceptions.
