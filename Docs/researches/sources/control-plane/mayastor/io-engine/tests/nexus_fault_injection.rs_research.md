# sources/control-plane/mayastor/io-engine/tests/nexus_fault_injection.rs

Purpose: validates nexus and replica fault-injection support for submission/completion faults, read/write operations, time windows, block ranges, URI round-tripping, and bdev I/O error propagation.

Important APIs/types/functions: `InjectionBuilder`, `Injection`, `FaultDomain::{NexusChild,BdevIo,BlockDevice}`, `FaultIoOperation`, `FaultIoStage`, `FaultMethod`, `IoCompletionStatus`, `NvmeStatus`, `add_fault_injection`, `list_fault_injections`, `NexusBuilder`, `ReplicaBuilder`, `PoolBuilder`, `ChildState`, `ChildStateReason`, `FioBuilder`, and `test_write_to_nexus`.

Control flow: `create_compose_test` and `create_test_storage` build two thin replicas and a published two-child nexus. `test_injection_uri` installs an injection on a live child device and writes to the nexus. Other tests verify time-delayed activation/expiry, block-range boundaries, URI serialization/deserialization, and replica-level bdev write submission faults through FIO.

State and persistence behavior: no etcd. State is injection registry contents and child state transitions between online, faulted, and online-after-repair.

Dependencies and integration points: compose, gRPC injection helpers, SPDK child state transitions, NVMf connection helpers, FIO, and Linux I/O error mapping.

Risks: `test_injection_uri` appears to compare child `state` against a state-reason enum value, likely intending `state_reason`. Time-window assertions depend on sleeps. The file is feature-gated by `fault-injection`.

Test signals: injection list contents, child `Faulted`/`Online` states, URI field equality, and expected FIO success or `ErrorKind::Other`.
