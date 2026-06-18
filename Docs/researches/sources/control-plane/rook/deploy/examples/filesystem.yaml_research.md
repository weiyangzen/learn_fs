<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem.yaml -->
# sources/control-plane/rook/deploy/examples/filesystem.yaml

Purpose: production-oriented replicated CephFS filesystem example with default CSI subvolume group.
Important APIs/types/functions: `CephFilesystem` `myfs`, replicated metadata/data pools size 3, pool compression parameters, `preserveFilesystemOnDelete: true`, MDS active/standby settings, anti-affinity, priority class, liveness/startup probes, commented mirroring configuration, and `CephFilesystemSubVolumeGroup` `myfs-csi` with distributed pinning.
Control flow: Rook creates pools, deploys MDS pods, manages health/probes, and creates the CSI subvolume group used by CephFS StorageClasses. State persists in CephFS metadata/data pools and CR status. Dependencies are at least three OSD hosts for safe replica size, Rook operator, and CSI StorageClass `storageclass.yaml`. Risks: `preserveFilesystemOnDelete` leaves data after CR deletion, anti-affinity can block scheduling in small clusters, and commented mirroring requires additional peer secrets to activate. Test signals: CephFilesystem Ready, MDS active/standby healthy, subvolume group ready, PVC provisioning works, and pod anti-affinity behaves as intended.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem.yaml -->
