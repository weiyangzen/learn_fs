<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-clone.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-clone.yaml

Purpose: demonstrates Kubernetes PVC cloning for a CephFS volume.
Important APIs/types/functions: `PersistentVolumeClaim`, `dataSource.kind: PersistentVolumeClaim`, source `cephfs-pvc`, `storageClassName: rook-cephfs`, and RWX access mode.
Control flow: the external provisioner detects `dataSource`, calls CSI clone support on the CephFS driver, and creates a new 1Gi PVC initialized from the source volume. State is stored as a new PVC/PV and CephFS subvolume clone. Dependencies are a bound source PVC in the same namespace, CSI clone feature support, and compatible StorageClass/access mode. Risks: source PVC must not be absent or in an incompatible namespace; clone behavior may be snapshot-backed and consume backend metadata. Test signals: clone PVC reaches Bound, contents match the source at clone time, and source/clone diverge independently after writes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-clone.yaml -->
