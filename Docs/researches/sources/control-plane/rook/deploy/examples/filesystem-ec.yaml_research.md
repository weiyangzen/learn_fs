<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-ec.yaml -->
# sources/control-plane/rook/deploy/examples/filesystem-ec.yaml

Purpose: creates a CephFS filesystem with replicated metadata/default data and an erasure-coded secondary data pool.
Important APIs/types/functions: `CephFilesystem` `myfs-ec`, metadata pool replication, `dataPools` with replicated and `erasurecoded` pools, `preserveFilesystemOnDelete`, MDS `activeCount`, `activeStandby`, placement anti-affinity, and `CephFilesystemSubVolumeGroup` `myfs-csi` with distributed pinning.
Control flow: Rook reconciles pools and MDS deployments, then creates the CSI subvolume group for dynamic provisioning. State persists in CephFS pools/MDS metadata and Kubernetes CR status. Dependencies are enough OSDs/hosts for EC chunks and replica size, Rook CephFilesystem CRD, and CSI StorageClass using `myfs-ec`. Risks: EC data pool needs bluestore/OSD capacity, `preserveFilesystemOnDelete: true` leaves backend data after CR deletion, and subvolume group references `filesystemName: myfs` while the filesystem CR is `myfs-ec`, which may require user correction. Test signals: CephFilesystem Ready, MDS active/standby pods run, subvolume group ready, and EC StorageClass PVCs bind.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-ec.yaml -->
