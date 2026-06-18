# sources/distributed-fs/lizardfs/src/master/locks.h

Purpose: defines lock range types, owner identity, range-set container, and per-inode file lock manager API.

Important APIs/types/functions: `LockRange::Owner` compares only FUSE owner and session id for lock identity while retaining request/message ids for interrupts; `LockRange` represents half-open `[start,end)` shared/exclusive/unlock ranges with sorted owner sets; `LockRanges` stores normalized active ranges; `FileLocks` manages active and pending locks by inode, collision probes, lock/unlock operations, candidate gathering, pending removal, vector export, load/store, and clear.

Control flow: callers request locks through `FileLocks`; failed blocking locks enter pending queues; unlocks should be followed by `gatherCandidates()` and retry via `apply()`.

State and persistence behavior: state is in active and pending maps. `load()`/`store()` persist both maps to metadata sections.

Dependencies/integration: depends on compact vectors and protocol lock info. Integrated by master client lock handling and metadata store.

Risks and test signals: owner comparisons ignore `reqid` and `msgid`, so interrupt handling must not confuse identity with request tracking. Range end is half-open, unlike `itree` inclusive intervals. Template `unlock(predicate)` returns `{UINT64_MAX,0}` when no lock matched, so callers must check for empty result. Tests should cover owner ordering, half-open endpoint behavior, and predicate unlock effects on candidate ranges.
