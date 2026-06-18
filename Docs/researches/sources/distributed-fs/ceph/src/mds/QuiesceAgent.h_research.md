# sources/distributed-fs/ceph/src/mds/QuiesceAgent.h

Purpose: declares `QuiesceAgent`, the asynchronous bridge between replicated quiesce database state and local MDS quiesce mechanics.

Important APIs and types: `ControlInterface` supplies `submit_request`, `cancel_request`, and `agent_ack`. Public operations include construction/start, `shutdown()`, `reset()`, `reset_async()`, `db_update()`, `tracked_roots()`, `get_tracked_root()`, and `get_current_version()`. `TrackedRoot` records per-root request state and exposes `should_quiesce()`, `should_release()`, `update_committed()`, `get_ttl()`, `get_actual_state()`, and a small spin lock.

State and persistence: `TrackedRootsVersion` stores roots plus `QuiesceDbVersion` and an `armed` bit for pending/current handoff. The agent keeps mutex/condition-variable state, `stop_agent_thread`, and `upkeep_needed`. It does not persist anything; expiry is represented by absolute local time derived from received TTLs.

Dependencies and integration: depends on `QuiesceDb.h` types and Ceph `Thread`. The class is designed for subclass hooks `_agent_thread_will_work()` and `_agent_thread_did_work()` used by tests or integration instrumentation.

Risks and test signals: `reset()` can call cancel outside the mutex and warns about MDS-lock deadlocks; `reset_async()` uses an empty pending version to let the thread release roots. Tests should inspect `get_actual_state()` transitions for successful quiesce, failed quiesce, successful/failed cancel, expiry after committed release, and correct TTL saturation.
