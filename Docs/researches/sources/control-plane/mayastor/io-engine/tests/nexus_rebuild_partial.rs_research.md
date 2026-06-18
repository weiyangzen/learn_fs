# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_partial.rs

Purpose: validates partial rebuild logging and fallback behavior for offlined children, I/O-faulted children, and faults during an active rebuild.

Important APIs/types/functions: `NexusBuilder`, `ReplicaBuilder`, `PoolBuilder`, `validate_replicas`, `test_write_to_nexus`, `ChildState`, `ChildStateReason`, `RebuildJobState`, `InjectionBuilder`, `FaultDomain::NexusChild`, FIO builders, `DataSize`, `create_compose_test`, and `create_test_storage`.

Control flow: storage helpers create two thick shared replicas and a published two-child nexus. `nexus_partial_rebuild_io_fault` injects a write-completion failure after a segment boundary, writes selected ranges, observes `IoFailure` and `has_io_log`, removes the injection, onlines the child, validates replicas, and checks exact partial transfer count. `nexus_partial_rebuild_offline_online` performs two offline/write/online partial rebuild cycles. `nexus_partial_rebuild_double_fault` faults a child during rebuild, then verifies the next recovery is full before a later successful partial rebuild.

State and persistence behavior: state is child I/O log, dirty segment map, child degraded/fault reasons, and rebuild history. No etcd is used.

Dependencies and integration points: fault injection, FIO, NVMf replicas, data validators, and rebuild history RPCs.

Risks: exact block counts depend on segment size and metadata boundaries; double-fault ordering accepts either I/O or rebuild failure.

Test signals: child state/reason, `has_io_log`, exact `blocks_transferred`, `is_partial`, rebuild state sequence, and replica equality.
