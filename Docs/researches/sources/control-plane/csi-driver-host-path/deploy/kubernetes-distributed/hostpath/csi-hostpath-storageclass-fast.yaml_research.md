# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-storageclass-fast.yaml

## Purpose
This StorageClass selects the distributed hostpath driver's `fast` simulated capacity pool. It is used for topology-aware provisioning in the DaemonSet deployment.

## Important APIs, Types, And Functions
The resource is `storage.k8s.io/v1` `StorageClass` named `csi-hostpath-fast`. It uses provisioner `hostpath.csi.k8s.io`, `volumeBindingMode: WaitForFirstConsumer`, and parameter `kind: fast`.

## Control Flow
PVCs referencing this class remain unbound until a consuming pod is scheduled. The node-local provisioner then sends `CreateVolume` with `parameters.kind=fast`, and the driver checks remaining configured capacity for that kind.

## State, Persistence, And Dependencies
The class persists in Kubernetes. Actual volume state is in the driver state JSON and node hostPath data directory. It depends on distributed plugin capacity flags defining `fast`.

## Integration Points
It integrates with the distributed DaemonSet's `--capacity=fast=...` settings, CSIStorageCapacity publication, generic ephemeral example for fast class, and Prow test-driver `FromExistingClassName: csi-hostpath-fast`.

## Risks
If the driver capacity map lacks `fast`, provisioning fails with invalid or exhausted capacity. `WaitForFirstConsumer` requires a consumer pod; PVC-only tests expecting immediate binding need different configuration.

## Test Signals
Create a PVC and pod with this class, verify late binding on a node with capacity, and confirm `GetCapacity` decreases by requested volume size for `fast`.
