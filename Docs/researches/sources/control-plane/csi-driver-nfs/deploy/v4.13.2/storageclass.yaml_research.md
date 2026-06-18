## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/storageclass.yaml

Purpose: Provides an example dynamic-provisioning `StorageClass` named `nfs-csi` for the NFS CSI driver. It points the driver at a sample NFS server DNS name and share path and enables volume expansion.

Important APIs and types: The resource is `storage.k8s.io/v1`, kind `StorageClass`, with `provisioner: nfs.csi.k8s.io`. Parameters set `server: nfs-server.default.svc.cluster.local` and `share: /`. `reclaimPolicy: Delete` deletes the PV object and asks the driver to clean up provisioned storage on PVC removal. `volumeBindingMode: Immediate` provisions as soon as the PVC is created. `allowVolumeExpansion: true` enables PVC resize handling. `mountOptions` sets `nfsvers=4.1`. Commented parameters show optional provisioner secret fields for DeleteVolume mount options.

Control flow: A PVC referencing `storageClassName: nfs-csi` triggers the external provisioner in the controller deployment. The provisioner calls the NFS CSI driver over the controller socket with the StorageClass parameters, and the driver creates a backing directory under the configured NFS share. Node-stage/publish later mounts that export with the configured mount options.

State and persistence behavior: The StorageClass is persistent cluster policy. It does not hold per-volume state, but its parameters are copied into provisioning decisions and influence PV attributes. The backing NFS server/share must exist independently. `reclaimPolicy: Delete` can remove dynamically provisioned subdirectories when claims are deleted, depending on driver implementation and mount-secret configuration.

Dependencies and integration points: Requires the controller deployment with `csi-provisioner`, the NFS driver container, the RBAC rules for PV/PVC/StorageClass/events/secrets, and a resolvable/reachable NFS server from controller and node pods. It integrates with `csi-nfs-driverinfo.yaml` through the same driver name.

Risks: The bundled server value is an example and will fail unless that service exists. `Immediate` binding can provision before a consuming pod's node placement is known. `reclaimPolicy: Delete` is potentially destructive. NFS version mismatch, firewall rules, DNS failures, or missing kernel NFS client support on nodes will surface as mount/provisioning failures. Secrets for DeleteVolume mount options are commented out, so environments needing special mount options must enable and grant them explicitly.

Test signals: Apply with a real NFS server/share, create a PVC using `nfs-csi`, and verify PV creation, events, and the provisioned directory. Mount from a pod, write/read data, resize the PVC, and delete it to confirm reclaim behavior. Negative tests should cover bad server DNS, inaccessible share, unsupported `nfsvers`, and missing optional secrets.
