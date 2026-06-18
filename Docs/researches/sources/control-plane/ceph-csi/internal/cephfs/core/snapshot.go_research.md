## sources/control-plane/ceph-csi/internal/cephfs/core/snapshot.go

Purpose: CephFS subvolume snapshot client abstraction for create, delete, inspect, clone, and metadata operations.

Important types/functions: `SnapshotClient`, `snapshotClient`, `Snapshot`, `SnapshotInfo`, `NewSnapshot`, `CreateSnapshot`, `DeleteSnapshot`, `GetSnapshotInfo`, and `CloneSnapshot`.

Control flow: Methods obtain FSAdmin from the cluster connection and call go-ceph subvolume snapshot APIs. `GetSnapshotInfo` maps missing snapshots to `ErrSnapNotFound` and extracts creation time and pending-clone status. `CloneSnapshot` builds `admin.CloneOptions`, including target group and optional pool layout, then invokes `CloneSubVolumeSnapshot`.

State and persistence: Writes CephFS subvolume snapshots and clone jobs; snapshot metadata methods are defined in `snapshot_metadata.go`. CSI journals are handled by callers.

Dependencies and risks: Depends on go-ceph admin and rados errors. Force deletion is used for snapshots. `CreationTime` field in `SnapshotInfo` is present but populated by higher-level controller after converting `CreatedAt`. Tests are indirect; integration should cover pending clones, missing parent, pool layout, and delete failures.
