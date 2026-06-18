# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MasterInfo.java

## Purpose
`MasterInfo` is the mutable in-memory record for a standby or lost master known to the primary meta master. It tracks identity, address, heartbeat time, lifecycle times, version/revision, and journal checkpoint progress.

## Important APIs, types, and functions
The constructor requires id and address and initializes last-updated time. Getters expose all fields. Setters update start time, lose-primacy time, version, revision, last checkpoint time, and journal entries since checkpoint. `updateLastUpdatedTimeMs()` records current system time. `toString()` prints diagnostic fields.

## Control flow
There is no complex flow; `DefaultMetaMaster` mutates records on register, heartbeat, lost detection, and lost-master recovery.

## State and persistence behavior
This class is `@NotThreadSafe` and in-memory only. Standby master info is not journaled; it is rebuilt by standby registration/heartbeat.

## Dependencies and integration points
It depends on wire `Address` and Guava preconditions/toString helper. It integrates with `DefaultMetaMaster` indexed sets and conversion to wire master info for RPC/REST/UI responses.

## Risks
No synchronization inside the class means callers must guard concurrent reads/writes. Using `System.currentTimeMillis()` directly makes tests time-sensitive unless wrapped at caller level. Version/revision default to empty strings.

## Test signals
Tests should cover constructor validation, timestamp update, setter/getter values, wire conversion in `DefaultMetaMaster`, and concurrent access assumptions in liveness detection.
