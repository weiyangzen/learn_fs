# sources/distributed-fs/lizardfs/src/master/locks_unittest.cc

Purpose: tests byte-range lock normalization and `FileLocks` pending queue behavior.

Important APIs/types/functions: helper functions add shared/exclusive/unlock ranges; tests cover exclusive overwrite, same-owner overwrites and splitting, overlapping reads, removals, adjacent range merge, stacked read locks, read hole punching, partial unlock, stress transitions, collision probe, pending unqueue, and candidate gathering.

Control flow: low-level tests call `LockRanges::fits()` then `insert()` directly. `FileLocks` tests use public APIs, remove pending locks by owner predicates, unlock ranges, gather candidates, and apply candidates.

State and persistence behavior: in-memory lock state only; persistence load/store is not tested in this file.

Dependencies/integration: depends on GoogleTest and `locks.h`.

Risks and test signals: this is strong coverage for normalization semantics but lacks serialization round trips, `copyActiveToVector()`/`copyPendingToVector()` checks, loaded pending queue sorting, `clear()` pending behavior, and predicate unlock return ranges.
