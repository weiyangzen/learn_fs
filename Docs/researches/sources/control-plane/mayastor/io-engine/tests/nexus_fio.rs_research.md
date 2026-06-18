# sources/control-plane/mayastor/io-engine/tests/nexus_fio.rs

Purpose: uses FIO to validate thin-provisioned ENOSPC behavior for a one-child overcommitted nexus and a mirrored nexus with one healthy replica.

Important APIs/types/functions: `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `FioBuilder`, `FioJobBuilder`, `DataSize`, `test_fio_to_nexus`, and constants modeling pool size, thick filler size, thin replica size, and safe/oversized write ranges.

Control flow: `nexus_fio_single_remote` creates a filler thick replica plus an overcommitted thin replica on one node, shares the thin replica, creates a remote nexus, runs a safe FIO job, then expects an oversized job to fail. `nexus_fio_mixed` creates an overcommitted child and another thin child with enough backing space, builds a two-child nexus, and expects both safe and oversized FIO workloads to succeed.

State and persistence behavior: no persistent store. State under test is thin allocation, pool capacity exhaustion, child health after ENOSPC, and mirrored nexus write viability when one child remains writable.

Dependencies and integration points: compose containers, NVMf shared replicas, common FIO wrapper, and io-engine pool/replica/nexus builders.

Risks: exact thresholds depend on metadata overhead and allocator behavior; the single-child failure checks a generic FIO error string.

Test signals: safe FIO succeeds, oversized single-child FIO returns `ErrorKind::Other` with `SPDK FIO error`, and oversized mirrored FIO succeeds.
