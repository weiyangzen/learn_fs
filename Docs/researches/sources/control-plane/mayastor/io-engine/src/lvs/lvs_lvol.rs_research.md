# sources/control-plane/mayastor/io-engine/src/lvs/lvs_lvol.rs

## Purpose
This file implements SPDK lvol replicas as io-engine logical volumes. It wraps `spdk_lvol`, exposes share and logical-volume traits, manages blob xattr properties, handles resize/destroy/wipe operations, and computes space usage including snapshots and clones.

## Important APIs, types, and functions
`PropValue` and `PropName` represent persisted lvol metadata for shared state, allowed hosts, and entity id. `Lvol` wraps `NonNull<spdk_lvol>` and can be constructed from an `UntypedBdev` when the bdev driver is `lvol`. `WIPE_SUPER_LEN` defines the 8 MiB fallback zeroing length when unmap is unavailable. `ResizeCbCtx` bridges resize callback state.

Important methods include `lookup_by_uuid_str`, `wipe_super`, `lvol_cb`, `ptpl`, `blob_xattr`/`get_blob_xattr`, `set_blob_attr`, clone-count helpers, and `lvol_resize_cb`. `LvolPtpl` manages per-replica PTPL files. `LvsLvol` is the lvol-specific trait extending `LogicalVolume + Share` with store/bdev access, metadata get/set/sync, blob iteration, destroy, and resize.

## Control flow
Share implementation delegates to the underlying bdev's NVMf share, then persists `Shared(true)` and allowed hosts into blob xattrs. Unshare delegates to bdev unshare and optionally persists `Shared(false)`. Property updates can set allowed hosts without metadata sync before updating the live bdev.

Destroy unshares without persisting, calls `vbdev_lvol_destroy`, removes PTPL, emits a delete event, and returns the name. `destroy_replica` also destroys a discarded source snapshot when the last clone disappears. Resize calls `vbdev_lvol_resize`, verifies callback success and resulting size, and maps errno. Metadata setters compare existing xattr values, set new xattrs, and sync blob metadata only when changed.

## State and persistence behavior
Persistent state lives in SPDK blob xattrs and PTPL JSON files. Runtime state is derived from live SPDK bdev/lvol structures. Snapshot/clone state is interpreted from xattrs defined in core. Wipe behavior writes zeros to the beginning of the lvol when unmap clearing is not available.

## Dependencies and integration points
It depends on SPDK blob/lvol APIs, core `LogicalVolume`, `Share`, bdev traits, snapshot/clone xattrs, eventing, `Lvs`, `LvsError`, and PTPL helpers. `lvs_store` creates `Lvol`s and `lvol_snapshot` extends them.

## Risks and test signals
The wrapper is pointer-heavy and must run on the correct SPDK reactor lifetime. Property setters ignore writes on snapshots and warn on read-only blobs. `share_uri` appends the lvol uuid as a query parameter, so callers must not double-append. `set_no_sync` compares sorted allowed hosts to avoid unnecessary metadata sync. Tests should cover property get/set/sync, share/unshare persistence, PTPL creation/destruction, wipe fallback, resize callback failure, clone-count behavior, and logical-volume usage accounting.
