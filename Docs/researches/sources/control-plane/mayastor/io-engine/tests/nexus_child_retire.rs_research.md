# sources/control-plane/mayastor/io-engine/tests/nexus_child_retire.rs

Purpose: fault-injection tests for nexus child retirement when persistent-store updates succeed, stall, or time out. It ensures I/O acknowledgement is coupled to durable recording of child health.

Important APIs/types/functions: gated by `fault-injection`. Uses compose `TestCluster` with etcd and three Mayastor nodes, `TestStorage` with two shared replicas and one nexus, `NexusBuilder` fault injection helpers, direct `add_fault_injection`, `PersistentStoreBuilder`, `NexusInfo`, `nexus_lookup_mut`, `bdev_io::write_blocks`, `CoreError`, `IoCompletionStatus::NvmeError`, and `NvmeStatus`.

Control flow: `nexus_child_retire_persist_unresponsive_with_fio` injects a write completion fault on replica 0, pauses etcd, starts fio to the nexus, asserts I/O freezes while etcd is paused, thaws etcd, asserts I/O completes, then checks child states and etcd `NexusInfo` mark replica 0 unhealthy and replica 1 healthy. Ignored `nexus_child_retire_persist_unresponsive_with_bdev_io` performs the same idea with direct bdev I/O. `nexus_child_retire_persist_failure_with_bdev_io` pauses etcd long enough for persistent-store operations to time out, expects frozen I/O to fail with internal device error, waits for nexus shutdown, and checks child states. `init_ms_etcd_test` starts local etcd, connects persistent store with timeout/retries, creates AIO-backed pools/replicas and a loopback nexus; `deinit_ms_etcd_test` destroys resources.

State and persistence: etcd stores serialized `NexusInfo` under nexus name/UUID. Temporary disk files back local pools. Fault injection state is process-local. Tests intentionally manipulate etcd availability.

Dependencies and integration points: etcd binary/client, persistent store builder, fault-injection feature, fio, gRPC v1 builders, nexus retirement state machine, child health persistence, NVMf sharing, and direct bdev I/O.

Risks and edge cases: highly timing-sensitive and feature-gated. One test is ignored. Requires `ETCD_BIN`, container pause/thaw support, and persistent-store timeouts. Shared in-process `MayastorTest` and fixed names/paths can make cleanup important.

Test signals: critical correctness signal for not acknowledging writes until retired-child state is durably recorded, and for shutting down/failing I/O when persistence cannot be completed.
