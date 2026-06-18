<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/snapshot.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/snapshot.yaml

Purpose: creates a snapshot of the NFS CSI example PVC.
Important APIs/types/functions: `VolumeSnapshot`, snapshot class `csi-nfsplugin-snapclass`, and source PVC `nfs-pvc`.
Control flow: the snapshot controller asks the NFS CSI driver to snapshot the backing volume/export and records readiness on the snapshot object. State spans Kubernetes snapshot resources and backend Ceph snapshot data. Dependencies are snapshot CRDs/controller, NFS snapshot class, a bound PVC, and driver snapshot support. Risks: snapshot consistency depends on active workload writes and backend implementation; delete policy comes from the class. Test signals: `readyToUse` true and `pvc-restore.yaml` can create a PVC from it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/snapshot.yaml -->
