# sources/control-plane/mayastor/io-engine/tests/snapshot_rebuild.rs

Purpose: local tests for rebuilding from snapshots or snapshot-like source devices into malloc devices and LVS replicas.

Important APIs/types/functions: uses `SnapshotRebuildJob::builder`, `RebuildJobOptions`, `ReadOptions`, `RebuildState`, `device_create`, `device_destroy`, `LvsLvol`, `PoolBuilderLocal`, and helper functions `create_replica`, `destroy_replica`, and `mb_to_blocks`.

Control flow: each test runs in Mayastor context. `malloc_to_malloc` rebuilds one malloc bdev into another and verifies full block transfer. `malloc_to_replica` rebuilds malloc source into a replica by destination UUID. `replica_to_rebuild_full` disables partial reads and expects full transfer. `replica_to_rebuild_partial` uses default read options and expects only the 8 MiB initially written/zeroed region to transfer.

State/persistence: transient malloc devices, local LVS pool, replicas, and rebuild job registry state. Jobs are `.store()`d for lookup and explicitly destroyed after completion.

Dependencies/integration: exercises rebuild job creation, lookup by name/replica UUID, async completion channel, statistics reporting, and logical-volume share URI use as snapshot source.

Risks: exact `blocks_transferred` expectations depend on block size, replica initialization/write-zero behavior, and partial rebuild semantics. Cleanup must destroy replicas/devices/jobs even after failure.

Test signals: passing tests prove snapshot rebuild succeeds across malloc and replica destinations and that full versus partial read options affect transferred block counts correctly.
