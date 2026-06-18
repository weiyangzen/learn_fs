# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild_verify.rs

Purpose: verifies rebuild verification failure handling by injecting corruption/miscompare into rebuild I/O and expecting the rebuilding child to fault.

Important APIs/types/functions: `NexusBuilder`, `ReplicaBuilder`, `PoolBuilder`, `SharedRpcHandle`, `ChildState`, `ChildStateReason`, `RebuildJobState`, `InjectionBuilder`, `FaultDomain::BlockDevice`, `FaultMethod::Data`, and helper `test_rebuild_verify`.

Control flow: `test_rebuild_verify` creates and publishes a two-child nexus, records a child device name, offlines that replica, injects a block-device write-submission data fault at offset 10240, onlines the child, waits for `Faulted/RebuildFailed`, and checks rebuild history. `nexus_rebuild_verify_remote` uses two remote replicas and a nexus node. `nexus_rebuild_verify_local` uses one local replica on the nexus node and one remote replica.

State and persistence behavior: no persistent store. The tests disable partial rebuild with `NEXUS_PARTIAL_REBUILD=0` and enable failure-mode rebuild verification with `NEXUS_REBUILD_VERIFY=fail`, forcing full rebuild I/O and history recording.

Dependencies and integration points: fault injection, rebuild verification environment variables, local/remote replica topology, and gRPC state polling.

Risks: feature-gated by `fault-injection`; the injected offset must be reached during full rebuild.

Test signals: child reaches `Faulted` with `RebuildFailed` reason and history contains exactly one `Failed` rebuild job.
