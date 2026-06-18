# sources/control-plane/mayastor/io-engine/src/lvs/lvol_snapshot.rs

## Purpose
This file implements snapshot and clone operations for SPDK lvol replicas. It prepares blob xattrs, calls SPDK snapshot/clone APIs, lists snapshot descriptors, handles discarded snapshots, and calculates snapshot usage for clone chains.

## Important APIs, types, and functions
`LvolSnapshotOps` defines the common local/remote snapshot interface. It includes create/destroy/list/clone methods plus lower-level xattr preparation and SPDK callback helpers. `LvolResult` aliases `Result<*mut spdk_lvol, Errno>`. `LvolSnapshotDescriptor` pairs a snapshot `Lvol` with `SnapshotInfo` and converts into `SnapshotDescriptor`. `LvolSnapshotIter` follows parent blobs to enumerate snapshot ancestors.

The `impl LvolSnapshotOps for Lvol` implements `prepare_snapshot_xattrs`, `create_snapshot_inner`, `do_create_snapshot`, `prepare_clone_xattrs`, `create_clone_inner`, `do_create_clone`, descriptor builders, `create_snapshot`, `destroy_snapshot`, list methods, `create_clone`, clone listing, pending discarded snapshot cleanup, and clone-source snapshot usage calculation.

## Control flow
Snapshot creation validates required `SnapshotParams`, builds SPDK xattr descriptors backed by live `CString` storage, calls `vbdev_lvol_create_snapshot_ext`, waits on a oneshot callback, emits an event, and returns `Lvol`. Clone creation mirrors that flow with clone xattrs and `vbdev_lvol_create_clone_ext`. Destroy either destroys immediately when no clones exist or marks `DiscardedSnapshot=true` in metadata. Import cleanup later destroys discarded snapshots with no clones. Listing scans lvol bdevs, filters snapshots/clones by xattrs, and builds descriptors.

## State and persistence behavior
Snapshot and clone identity is persisted in SPDK blob xattrs: transaction id, entity id, parent id, snapshot uuid, creation time, discarded marker, source uuid, clone uuid, and clone creation time. Destroy may leave a discarded snapshot until dependent clones are removed.

## Dependencies and integration points
It depends on SPDK lvol snapshot/clone APIs, `SnapshotParams`, `CloneParams`, `SnapshotXattrs`, `CloneXattrs`, eventing, `LvsLvol`, and `UntypedBdev` iteration. `Lvs::import_from_args_` calls pending discarded snapshot cleanup after pool import.

## Risks and test signals
Required parameter validation is manual; missing values return configuration errors. Raw xattr descriptor pointers rely on local `CString` lifetimes until SPDK call submission. Global `Lvol::lookup_by_uuid_str` is used in parent iteration with a TODO to search only the owning store. Listing all snapshots scans all bdevs, which can be expensive and cross-pool if filters fail. Tests should cover xattr validation, create/clone callback errno mapping, descriptor validity with missing xattrs, discarded snapshot lifecycle, clone list accuracy, and usage accounting in clone chains.
