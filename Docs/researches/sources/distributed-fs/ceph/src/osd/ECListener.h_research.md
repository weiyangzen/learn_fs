# sources/distributed-fs/ceph/src/osd/ECListener.h

Purpose: `ECListener.h` declares the abstraction layer used by EC pipeline code to call back into the owning PG/backend implementation. It decouples shared EC logic from classic and Crimson-specific OSD implementations.

Important APIs and types: `ECListener` is a pure virtual interface. It exposes OSD map and PG identity queries, recovery notifications (`on_local_recover`, `on_global_recover`, `on_peer_recover`, `begin_peer_recover`), missing/shard state queries, messaging functions, write ordering, logging (`log_operation`, `add_local_next_event`, `op_applied`), stats accounting, temp-object tracking, and EC RMW helpers such as `should_send_op` and `get_pool`.

Control flow: EC read/recovery/write pipelines use the listener whenever they need PG-global knowledge or side effects: scheduling recovery, sending subop messages, recording log entries, applying stat deltas, or checking pool state. The interface hides whether the caller is running in the classic threaded OSD path or a Crimson build.

State and persistence: the interface owns no state, but many methods mutate persistent or replicated PG state through implementers. `log_operation` is the key persistence integration because it commits object-store transactions and PG log entries; recovery callbacks update durable object state and in-memory recovery bookkeeping.

Dependencies and integration: it depends on `OSDMap`, `PGLog`, `MOSDPGPush`, work queues, object recovery types, and classic-only `ObjectContextRef`/thread-pool context types behind `WITH_CRIMSON` guards.

Risks: because this is a broad interface, semantic drift between implementations can break EC code without compile errors. Several comments are marked `XXX`, indicating older boundary ambiguity. Classic/Crimson conditional members increase the risk of one backend missing coverage.

Test signals: integration tests should exercise EC recovery, failed pulls, async reads/writes, temp-object cleanup, and PG log submission through both optimized and legacy callers. Build tests must cover both `WITH_CRIMSON` and non-Crimson configurations.
