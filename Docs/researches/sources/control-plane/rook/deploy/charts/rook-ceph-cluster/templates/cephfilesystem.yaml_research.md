## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephfilesystem.yaml

Purpose: renders CephFS resources and optional CephFS StorageClasses from `.Values.cephFileSystems`.

Important template behavior: for each filesystem it creates a `CephFilesystemSubVolumeGroup` named `<filesystem>-csi` with filesystemName and default distributed pinning, then creates the `CephFilesystem` CR from raw `spec`. If `storageClass.enabled`, it creates a CephFS CSI StorageClass with provisioner from `csiDriverNamePrefix` or `operatorNamespace`, fsName, pool name defaulting to `<fs>-data0`, clusterID, templated user parameters, reclaim policy, expansion, binding mode, and mount options.

Control flow: range with StorageClass conditional and optional fields. A YAML document separator is emitted before the conditional StorageClass, which should be checked in disabled cases for clean rendering.

State and persistence: creates CephFS metadata/data pools and MDS daemons through Rook, a subvolume group, and optional cluster-scoped StorageClass. StorageClass choices persist into PVC provisioning.

Dependencies and integration points: relies on CephFilesystem and CephFilesystemSubVolumeGroup CRDs plus CephFS CSI driver. Risks: pool name must correspond to a real filesystem data pool; default StorageClass toggles can affect cluster-wide PVC binding; `tpl` parameters may render invalid values. Tests should include enabled/disabled storage class renders and non-default pool values.
