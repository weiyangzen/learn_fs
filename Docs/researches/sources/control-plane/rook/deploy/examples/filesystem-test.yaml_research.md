<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-test.yaml -->
# sources/control-plane/rook/deploy/examples/filesystem-test.yaml

Purpose: single-OSD CephFS example for non-production testing.
Important APIs/types/functions: `CephFilesystem` `myfs`, metadata/data pools with replica size 1 and `requireSafeReplicaSize: false`, `preserveFilesystemOnDelete: false`, MDS `activeStandby: false`, and `CephFilesystemSubVolumeGroup` `myfs-csi`.
Control flow: Rook creates a low-redundancy filesystem and default CSI subvolume group suitable for small test clusters. State persists in CephFS pools and Kubernetes CRs, but filesystem deletion does not preserve data. Dependencies are Rook CephFilesystem CRD and at least one OSD. Risks: explicit data-loss exposure with replica 1, no standby MDS, and delete removes filesystem data. Test signals: CephFilesystem Ready on a single OSD, subvolume group ready, and `rook-cephfs` PVCs bind in test clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-test.yaml -->
