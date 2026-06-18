<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/ge-sc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/ge-sc.yaml

Purpose: StorageClass for Kubernetes generic ephemeral BeeGFS volumes in the combined examples.

Important APIs and flow: mirrors the dynamic StorageClass but uses `volDirBasePath: k8s/name/ge` and `allowVolumeExpansion: false`, appropriate for ephemeral claim templates. The provisioner is `beegfs.csi.netapp.com`.

State and persistence: creates BeeGFS-backed volumes for Pod-scoped PVCs and deletes them with the owning Pod/PVC lifecycle under `reclaimPolicy: Delete`.

Dependencies and integration points: used by `all-app.yaml` embedded `volumeClaimTemplate`, CSI provisioner, and BeeGFS management service.

Risks and test signals: generic ephemeral support depends on the Kubernetes version and feature availability. Unique base paths avoid cross-cluster collisions. Test Pod creation and cleanup of generated PVC/PV/volume directory.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/ge-sc.yaml -->
