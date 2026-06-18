# sources/control-plane/mayastor/io-engine/tests/nexus_thin_no_space.rs

Purpose: verifies ENOSPC behavior for thin-provisioned nexus children in local and remote layouts, including recovery after freeing pool space.

Important APIs/types/functions: `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `DataSize`, `test_write_to_nexus`, `find_nexus_by_uuid`, `ChildState`, `ChildStateReason`, and helper `test_recover_from_enospc`.

Control flow: single-child local and remote tests create a thin replica, write below capacity successfully, then write beyond backing capacity and expect raw `ENOSPC`. Mirrored local and remote tests create two thin replicas, fill one pool with a thick replica, write enough data to degrade the first child with no space, destroy the filler, online the child, and expect rebuild to start.

State and persistence behavior: no etcd. State is pool allocation, child `NoSpace` degradation, freeing capacity by destroying the filler replica, and transition to `OutOfSync` when onlined.

Dependencies and integration points: local and remote replica sharing, NVMf nexus publishing, gRPC state reads, and Linux `libc::ENOSPC`.

Risks: capacity thresholds depend on allocator metadata overhead; recovery helper verifies rebuild starts but not final online/data equality.

Test signals: ENOSPC errno, child `Degraded/NoSpace`, and child `Degraded/OutOfSync` after online.
