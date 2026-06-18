# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-session.h

## Purpose
Defines the private session data structures used by the public UDS API implementation and index rebuild suspend/resume coordination.

## Important APIs, Types, And Functions
`struct session_stats` stores request outcome counters by operation and location. `enum index_suspend_status` describes load/rebuild state. `struct index_load_context` contains a mutex, condition variable, and suspend status. `struct uds_index_session` stores the current state flags, open `uds_index`, callback queue, copied parameters, load context, request mutex/condition, request count, and stats.

## Control Flow
The implementation in `index-session.c` mutates these fields during open, request launch, callback completion, suspend, resume, close, destroy, and stats collection. `index.c` observes `index_load_context` while replaying chapters during rebuild so suspend and destroy can pause or abort long recovery.

## State And Persistence
The header does not serialize anything directly. It defines volatile session state that gates access to a persistent index and determines when save operations are allowed to run.

## Dependencies And Integration Points
Includes Linux atomic/cache headers, thread utilities, configuration, and public UDS API declarations. The cache-line alignment on `session_stats` reduces false sharing for frequently updated counters.

## Risks
The state integer is intentionally opaque bit state from the C file; adding fields or changing ownership requires preserving locking rules around `request_mutex` and `load_context.mutex`. Stats are not atomic counters, so readers rely on relaxed snapshot semantics rather than exact concurrent totals.

## Test Signals
Compile-time checks should catch structure-user drift. Runtime signals are correct state transitions under concurrent request launch, suspend/resume, close, and rebuild interruption, plus stats snapshots that do not crash or regress under concurrent callbacks.
