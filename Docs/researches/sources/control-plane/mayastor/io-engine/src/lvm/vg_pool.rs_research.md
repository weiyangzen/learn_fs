# sources/control-plane/mayastor/io-engine/src/lvm/vg_pool.rs

## Purpose
This file implements LVM volume groups as io-engine pools. It creates/imports VGs, lists and filters VG metadata, creates logical-volume replicas, exports/destroys pools, and manages VG-level PTPL directory cleanup.

## Important APIs, types, and functions
`QueryArgs` wraps common query arguments and renders VG-specific `--select` expressions for name, uuid, and tags. `VolumeGroup` deserializes `vgs` JSON fields: name, uuid, size, free, tags, and physical disks. Important methods include `lookup`, `list`, `create`, `import`, `import_inner`, `create_lvol`, `list_lvs`, `list_foreign_lvs`, `destroy`, `purge`, `destroy_`, `export`, `export_all`, and `create_lvoli`. `VgPtpl` implements pool PTPL subpath handling under `pool/vg/<name>`.

## Control flow
Create first checks whether a VG with the requested name exists. Existing VGs go through import validation. Missing VGs run `pvcreate` on disks, then `vgcreate` with optional Mayastor tag, with special stale `/dev/<name>` dm cleanup on a known error. Import validates that users did not provide a VG uuid, verifies disk list equality, and adds or removes the Mayastor ownership tag depending on `no_spdk`. Destroy exports owned LVs first, then removes VG/PVs unless foreign LVs remain or purge is requested.

`create_lvoli` rejects thin provisioning, creates an LV using the replica uuid as LV name, adds metadata tags, maps known stderr text to `NoSpace`/`Exists`, and logs success.

## State and persistence behavior
Persistent state is host LVM metadata: PV labels, VG metadata, ownership tags, and LV tags. Export removes Mayastor tags and unloads bdevs but leaves VG/LV data. Destroy removes VG/PV metadata and PTPL directories if safe.

## Dependencies and integration points
It depends on `LvmCmd`, deserializer helpers, `Property`, `DmSetup`, `LogicalVolume`, `PoolArgs`, and `PtplFileOps`. `lvm/mod.rs` exposes it as `PoolOps`/`IPoolProps`.

## Risks and test signals
Disk comparison is order-sensitive, which may reject semantically identical VG disk sets. Create/import behavior changes with `no_spdk`, so ownership tags can be removed intentionally. Destroy leaves pools with foreign LVs, which is safe but can surprise callers. Stderr-prefix matching is brittle. Tests should cover create/import/no_spdk flows, disk mismatch, foreign LV retention, purge, stale dm cleanup, LV creation error mapping, and query validation.
