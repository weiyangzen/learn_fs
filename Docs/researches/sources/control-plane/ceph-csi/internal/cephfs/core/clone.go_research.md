## sources/control-plane/ceph-csi/internal/cephfs/core/clone.go

Purpose: CephFS core clone implementation wrapping go-ceph subvolume snapshot clone APIs and mapping Ceph clone states to internal CSI errors.

Important types/functions: `cephFSCloneState`, `CephFSCloneError`, `ToError`, `GetProgressReport`, `CreateCloneFromSubvolume`, `CleanupSnapshotFromSubvolume`, `CreateCloneFromSnapshot`, and `GetCloneState`.

Control flow: PVC-to-PVC clone creates an intermediate snapshot named after the target clone, clones it to the target subvolume, checks clone state, expands the clone if needed, and deletes the intermediate snapshot. Snapshot restore clones the existing snapshot to the target and expands. Deferred cleanup purges the target and/or snapshot on non-retry errors.

State and persistence: Uses CephFS subvolume snapshots and clone state maintained by the Ceph manager. No local persistence; callers coordinate RADOS journal reservations. Clone progress fields are exposed for `ErrCloneInProgress`.

Dependencies and risks: Depends on `go-ceph/cephfs/admin`, CephFS clone support, internal errors, and logging. Retry errors intentionally avoid destructive cleanup because clone may still progress. A failed delete of the intermediate snapshot can leave cleanup work. `CephFSCloneError` is a sentinel with default state, so state mapping relies on matching enum zero behavior. Unit test covers `ToError` mapping.
