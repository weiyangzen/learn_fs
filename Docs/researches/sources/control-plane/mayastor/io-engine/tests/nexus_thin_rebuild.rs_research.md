# sources/control-plane/mayastor/io-engine/tests/nexus_thin_rebuild.rs

Purpose: ensures rebuilding into a new thin-provisioned replica preserves thin usage accounting and data consistency across local/remote source and destination topologies.

Important APIs/types/functions: `StorConfig`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `DataSize`, `test_write_to_nexus`, `validate_pools_used_space`, `validate_replicas`, and `test_thin_rebuild`.

Control flow: `test_thin_rebuild` creates three thin replicas on configurable nodes, builds a two-child nexus from the first two, writes 14 MiB, adds the third replica with rebuild enabled, waits for all children online, then validates pool used space and replica equality. Four tests place the nexus/source/destination handles as remote-to-local, remote-to-remote, local-to-remote, and local-to-local.

State and persistence behavior: no persistent store. State under test is thin allocation on every pool after rebuild, child online convergence, and byte equality across replicas.

Dependencies and integration points: compose multi-node layouts, remote NVMf sharing, builder APIs, data validation helpers, and pool usage validation helpers.

Risks: used-space checks are sensitive to cluster allocation behavior; rebuild timeout is ten seconds.

Test signals: add-replica rebuild reaches online, pool used-space validation passes, and all replicas validate equal.
