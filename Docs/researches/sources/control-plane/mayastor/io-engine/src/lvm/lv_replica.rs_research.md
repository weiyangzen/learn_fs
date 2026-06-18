# sources/control-plane/mayastor/io-engine/src/lvm/lv_replica.rs

## Purpose
This file implements LVM logical volumes as io-engine replicas. It lists and creates LVs through the LVM CLI, imports owned LVs as SPDK AIO bdevs, persists share metadata in LVM tags, supports NVMf share/unshare/update operations, and implements core replica/logical-volume traits.

## Important APIs, types, and functions
`QueryArgs` combines VG and LV filters and can query either regular LVM fields or Mayastor's tag-based LV identity. `LogicalVolume` is deserialized from `lvs` JSON and stores LV/VG identity, size, path, tags, and runtime state. `RunLogicalVolume` mirrors runtime share/name/entity/bdev state derived from tags and SPDK. `BdevOpts` snapshots SPDK bdev URI, share URI, allowed hosts, protocol, and size.

Key methods include `create`, `lookup`, `list`, `fetch`, `import`, `import_bdev`, `export_bdev`, `destroy`, `resize`, `share_nvmf`, `update_share_props`, `unshare`, `set_property`, `dm_suspend`, `dm_resume`, `table`, `bork`, and `unbork`. `LvolPtpl` implements `PtplFileOps` for per-replica NVMf persistence files under the parent VG PTPL path. Trait implementations expose the object through `crate::core::LogicalVolume` and `Share`.

## Control flow
Creation delegates to `VolumeGroup::create_lvoli`, then looks up the LV and treats an existing compatible LV as an import. Listing fetches LVM JSON, imports attributes from tags, then imports every owned LV as an SPDK AIO bdev. `import_bdev` constructs `aio://<lv_path>?uuid=<lv_uuid>`, creates the bdev if missing, applies persisted share/allowed-host state, then stores `BdevOpts`.

Share operations run SPDK work via `spdk_run!`, update the SPDK bdev, then synchronize LVM tags. Unshare can optionally persist `Protocol::Off`. Resize first resizes the LV, then notifies the SPDK bdev block count change and rolls back the LV size if bdev notification fails. Destroy exports/unshares/destroys the bdev before `lvremove` and PTPL cleanup.

## State and persistence behavior
Persistent state lives in LVM tags: Mayastor ownership, replica display name, share protocol, allowed hosts, and entity id. Runtime state mirrors those tags and SPDK bdev state. PTPL files are created for NVMf share persistence and removed on destroy. `tags_dirty` records failed tag updates but there is no visible repair loop in this file.

## Dependencies and integration points
The file depends on LVM command/query/property modules, `VolumeGroup`, `DmSetup`, SPDK bdev APIs, core `Share`/`LogicalVolume`/`UntypedBdev` traits, and pool backend types. It is surfaced through `lvm/mod.rs` factories and replica operations.

## Risks and test signals
The backend relies on LVM stderr strings for `NoSpace` and `Exists` mapping. Tag synchronization can fail after SPDK state changes, leaving runtime and persistent state divergent. `share_nvmf` contains a TODO noting wrong share URI behavior. `list` fails the whole list if any owned LV import fails. Resize rollback is best-effort. Tests should cover idempotent create/import, tag persistence and dirty failure, share/unshare persistence, allowed-host updates, resize rollback, export/destroy ordering, and dmsetup table fault paths.
