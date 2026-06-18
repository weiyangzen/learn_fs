# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-driverinfo.yaml

## Purpose
This `CSIDriver` object declares hostpath capabilities for the distributed DaemonSet deployment. It differs from single-node manifests by disabling attach and enabling storage capacity tracking.

## Important APIs, Types, And Functions
The resource is `storage.k8s.io/v1` `CSIDriver` named `hostpath.csi.k8s.io`. It sets persistent and ephemeral lifecycle modes, `podInfoOnMount: true`, `attachRequired: false`, `storageCapacity: true`, and `fsGroupPolicy: File`.

## Control Flow
The distributed deploy script may remove `storageCapacity: true` if the cluster lacks the CSIStorageCapacity API. Kubernetes uses `attachRequired: false` to skip external-attacher flows and uses storage capacity objects during scheduling when enabled.

## State, Persistence, And Dependencies
The object persists in the Kubernetes API. It depends on `storage.k8s.io/v1` support and optionally the CSIStorageCapacity API.

## Integration Points
It aligns with the distributed plugin DaemonSet's `--node-deployment`, `--strict-topology`, and capacity arguments. It also drives the distributed Prow test-driver capability patching.

## Risks
If `storageCapacity: true` remains on unsupported clusters, scheduling/provisioning behavior can fail. `attachRequired: false` must match the absence of attacher sidecar and driver controller publish usage.

## Test Signals
Check the applied CSIDriver after deploy on capacity and non-capacity clusters, verify no VolumeAttachment objects are required, and run topology/capacity e2e cases against fast and slow classes.
