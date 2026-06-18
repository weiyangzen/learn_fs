## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-driverinfo.yaml

Purpose: Registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`. This tells core storage controllers and kubelet that the driver does not require attach/detach operations and supports persistent volumes.

Important APIs and types: The manifest uses `CSIDriver.spec.attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`. `attachRequired: false` is important for NFS because the driver exposes network filesystems and does not need a `VolumeAttachment` object. `fsGroupPolicy: File` declares that Kubernetes may apply filesystem ownership changes for mounted volumes when a pod requests an `fsGroup`.

Control flow: The object is read by Kubernetes storage control loops and kubelet during CSI volume lifecycle operations. PVCs provisioned by the `nfs.csi.k8s.io` provisioner bind to PVs using this driver name; kubelet later consults the `CSIDriver` object while deciding whether to wait for attachment and how to handle ownership policy.

State and persistence behavior: The object is cluster-scoped persistent Kubernetes configuration. It does not create pods or local files. Changes to `attachRequired`, lifecycle modes, or `fsGroupPolicy` alter future scheduling and mount behavior for NFS CSI volumes and should be treated as driver contract changes.

Dependencies and integration points: Integrates with the node plugin registered by `csi-nfs-node.yaml`, the controller plugin in `csi-nfs-controller.yaml`, and storage objects that use provisioner/driver `nfs.csi.k8s.io`, including `StorageClass` and `VolumeSnapshotClass` manifests. Requires the `storage.k8s.io/v1` API, which is present on supported Kubernetes versions for this driver family.

Risks: If this object is missing, kubelet may assume default CSI behavior and attachment semantics that are wrong for NFS. If `fsGroupPolicy` is changed, pods relying on group ownership propagation can see permission changes. `volumeLifecycleModes` excludes `Ephemeral`; inline CSI ephemeral examples need a different driver declaration if enabled elsewhere.

Test signals: After apply, `kubectl get csidriver nfs.csi.k8s.io -o yaml` should show `attachRequired: false` and `fsGroupPolicy: File`. Provision a PVC with the NFS `StorageClass`, schedule a pod with and without `fsGroup`, and verify no `VolumeAttachment` is required. Confirm kubelet node-driver registration reports the same driver name.
