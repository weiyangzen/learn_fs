# sources/control-plane/mayastor/io-engine/tests/replica_thin.rs

Purpose: validates replica-level thin provisioning usage metrics before and after writing to a thin replica over NVMf.

Important APIs/types/functions: `PoolBuilder`, `ReplicaBuilder`, `GrpcConnect`, `Binary`, `DataSize`, `test_write_to_nvmf`, and replica usage fields `num_allocated_clusters`, `num_clusters`, `allocated_bytes`, and `capacity_bytes`.

Control flow: the test starts one io-engine, creates a 200 MiB pool, creates a 40 MiB thin replica and a 40 MiB thick replica, shares both, captures initial pool and replica usage, and asserts thin allocation is below capacity while thick allocation equals capacity. It writes 30 MiB to the thin replica over NVMf, fetches usage again, and checks allocation and pool used bytes increased while remaining below full thin capacity.

State and persistence behavior: no persistent store. State under test is pool usage and replica usage metadata before and after host I/O.

Dependencies and integration points: compose, NVMf write helper, pool usage reporting, and replica usage reporting.

Risks: cluster allocation expectations depend on allocator behavior and cluster size; freeing space is not covered.

Test signals: thin initially sparse, thick fully allocated, thin allocation increases after write, pool used increases, and thin allocation remains below capacity.
