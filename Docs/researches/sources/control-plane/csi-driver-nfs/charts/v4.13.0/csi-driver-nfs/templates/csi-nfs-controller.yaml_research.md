# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This 4.13.0 Deployment template runs the CSI NFS controller and updated sidecars for provisioning, resizing, snapshotting, and health.

## APIs, Control Flow, and State
The Deployment structure matches 4.12.x but includes important argument changes. `csi-provisioner` now passes `--feature-gates=HonorPVReclaimPolicy=true,VolumeAttributesClass=false`; `csi-resizer` passes `-feature-gates=VolumeAttributesClass=false`; the privileged `nfs` container adds `--enable-snapshot-compression={{ .Values.controller.enableSnapshotCompression }}`. Image references also support repositories beginning with `/` by prefixing `image.baseRepo`, which is used by new sidecar defaults.

## Dependencies and Integration Points
It depends on `values.yaml` for upgraded sidecar images, `controller.enableSnapshotCompression`, RBAC, snapshot CRDs, StorageClass values, and kubelet host paths. The CSI socket remains an `emptyDir` shared among sidecars and the NFS container.

## Risks and Test Signals
Disabling `VolumeAttributesClass` is explicit compatibility behavior for newer sidecars and should be tested during Kubernetes upgrades. Snapshot compression changes snapshot artifact behavior and restore expectations. Test Helm rendering, sidecar startup with feature gates, PVC provisioning, resizing, compressed and uncompressed snapshots, and liveness probes.
