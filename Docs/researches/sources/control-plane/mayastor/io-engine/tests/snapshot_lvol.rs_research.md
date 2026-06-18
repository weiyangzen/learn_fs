# sources/control-plane/mayastor/io-engine/tests/snapshot_lvol.rs

Purpose: broad local and gRPC-backed test suite for LVS logical-volume snapshots, clones, snapshot metadata, allocation accounting, deletion semantics, and restore data integrity.

Important APIs/types/functions: helpers include `get_ms`, `create_test_pool`, `find_snapshot_device`, `check_snapshot`, `check_clone`, `clean_snapshots`, `test_lvol_alloc_after_snapshot`, and `check_snapshot_descriptor`. Tests use `Lvs`, `Lvol`, `LvsLvol`, `LogicalVolume`, `LvolSnapshotOps`, `ISnapshotDescriptor`, `SnapshotParams`, `CloneParams`, `SnapshotXattrs`, `CloneXattrs`, `PoolArgs`, `PoolBackend`, `UntypedBdev`, `device_create/open`, and gRPC helper builders for replica snapshot/clone validation.

Control flow: early tests create malloc or aio-backed pools and lvols, create snapshots through either `Lvol` or a bdev handle, validate xattrs and UUIDs, and enumerate snapshots by lvol, pool, or all devices. Middle tests verify thick-to-thin transition after snapshot, cluster-aligned referenced size, clone creation/provenance, and snapshot listing after source destruction. Later tests cover snapshot attribute persistence across pool export/import, discarded snapshot behavior when clones exist, retry cleanup of pending discarded snapshots, data restore equivalence through snapshot clones, and usage recomputation after destroying snapshots, parents, clones, and clone snapshots.

State/persistence: most state is transient SPDK blobstore state. `test_snapshot_attr` uses `/tmp/disk1.img` and pool export/import to prove blob xattrs persist. Snapshot and clone metadata are stored as blob xattrs; allocation/usage state is derived from cluster ownership and snapshot ancestry.

Dependencies/integration: integrates local Mayastor reactor context, SPDK LVS blobstore, bdev I/O helpers, UUID and timestamp generation, gRPC v1 replica/snapshot builders, NVMe-oF write helpers, and replica comparison utilities.

Risks: long scenario file with shared global `OnceCell<MayastorTest>` means unique pool/device names are important. Several assertions rely on exact cluster sizes and SPDK allocation behavior. Discarded snapshot deletion is subtle because clone count, failed destroy paths, and retry cleanup must agree.

Test signals: passing tests indicate snapshot metadata correctness, list filters, clone provenance, persistent attrs, allocation accounting, discarded-snapshot lifecycle, and snapshot-clone restore data all work across local and exported paths.
