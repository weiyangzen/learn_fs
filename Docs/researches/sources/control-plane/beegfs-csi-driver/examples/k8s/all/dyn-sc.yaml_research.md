<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-sc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-sc.yaml

Purpose: StorageClass for dynamically provisioning BeeGFS volumes in the combined examples.

Important APIs and flow: `provisioner: beegfs.csi.netapp.com` passes `sysMgmtdHost` and `volDirBasePath` parameters to the CSI driver. Optional stripe pattern and permissions parameters are documented as string values. `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and `allowVolumeExpansion: true` control Kubernetes lifecycle.

State and persistence: creates/deletes BeeGFS directories through dynamic provisioning and supports expansion operations through the CSI driver.

Dependencies and integration points: depends on an actual BeeGFS management host, unique cluster-specific base path, and CSI provisioner sidecar.

Risks and test signals: leaving `localhost` or `k8s/name/dyn` unchanged can collide or fail. Test by PVC bind, directory creation, deletion cleanup, and expansion.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-sc.yaml -->
