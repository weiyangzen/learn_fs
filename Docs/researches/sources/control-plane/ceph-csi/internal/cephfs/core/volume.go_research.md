## sources/control-plane/ceph-csi/internal/cephfs/core/volume.go

Purpose: Core CephFS subvolume client and data model used by controller and node paths.

Important types/functions: `Subvolume`, `SubVolumeClient`, `subVolumeClient`, `SubVolume`, `NewSubVolume`, `GetVolumeRootPathCephDeprecated`, `GetVolumeRootPathCeph`, `GetSubVolumeInfo`, `CreateVolume`, `ExpandVolume`, `ResizeVolume`, `PurgeVolume`, and `checkSubvolumeHasFeature`. It also defines cluster-level support cache types shared with metadata.

Control flow: Create uses FSAdmin `CreateSubVolume` with size and optional pool layout. Info reads subvolume details and normalizes quota/features. Expand compares requested/current quota and calls resize. Purge removes the subvolume with force and optionally retains snapshots if the subvolume supports `snapshot-retention`.

State and persistence: Directly creates, resizes, queries, and removes CephFS subvolumes. `clusterAdditionalInfo` is in-memory feature support state. Callers handle journals and CSI ID generation.

Dependencies and risks: Depends on go-ceph FSAdmin, rados error mapping, and internal util/log packages. `ExpandVolume` compares `s.Size` against current quota but logs `bytesQuota`, so caller consistency matters. Infinite or nil quotas are tolerated only in specific states. Tests in this subset do not directly cover create/resize/purge; integration should exercise not-found, invalid-command, snapshot-retained, and volume-has-snapshots cases.
