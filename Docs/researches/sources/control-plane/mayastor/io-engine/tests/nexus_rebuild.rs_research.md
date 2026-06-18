# sources/control-plane/mayastor/io-engine/tests/nexus_rebuild.rs

Purpose: validates low-level bdev rebuild and nexus rebuild behavior: job lookup/source tracking, pause handling, raw bdev transfer counts, partial bitmap counts, data integrity, and mixed cluster-size rebuilds.

Important APIs/types/functions: `device_create`, `device_destroy`, `device_open`, `nexus_lookup_mut`, `BdevRebuildJob`, `NexusRebuildJob`, `RebuildState`, `SegmentMap`, `MayastorTest`, `Mthread`, `Protocol::Off`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `wait_for_rebuild`, `wait_for_replica_rebuild`, and helpers for temporary disks/devices.

Control flow: helper setup creates temporary aio-backed child devices and optional random data. `rebuild_replica` creates a six-child nexus, adds rebuild targets, checks job lookup and source indexes, pauses one rebuild, starts another, validates MD5 equality, checks history, removes children, and destroys the nexus. `rebuild_bdev` copies one malloc bdev to another. `rebuild_bdev_partial` table-drives dirty `SegmentMap` bitmaps. `rebuild_across_mixed_cluster_sizes` adds a thin child from a 32 MiB-cluster pool to a default-cluster nexus.

State and persistence behavior: no etcd. State is rebuild job registry, source lookup map, rebuild history, dirty bitmap, and child membership.

Dependencies and integration points: SPDK bdevs, local `/tmp` files, DMA reads, MD5 validation, compose RPC builders, and io-engine rebuild internals.

Risks: uses global nexus name and `static mut` error index state; data validation assumes metadata offset layout.

Test signals: job lookup presence/absence, `RebuildState::Completed`, exact block transfer counts, MD5 equality, non-empty history, and child online after mixed-cluster rebuild.
