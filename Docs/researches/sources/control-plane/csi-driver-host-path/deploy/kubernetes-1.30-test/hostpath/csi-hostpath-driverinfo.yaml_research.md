# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-driverinfo.yaml

## Purpose
This `CSIDriver` object declares the hostpath CSI driver's cluster-facing capabilities for the single-node Kubernetes 1.30 deployments. It tells Kubernetes that the driver supports persistent volumes and inline ephemeral volumes and that pod information is required on mount.

## Important APIs, Types, And Functions
The resource is `storage.k8s.io/v1`, kind `CSIDriver`, named `hostpath.csi.k8s.io`. The key spec fields are `volumeLifecycleModes: [Persistent, Ephemeral]`, `podInfoOnMount: true`, and `fsGroupPolicy: File`.

## Control Flow
The deploy script applies this resource with common labels. Kubernetes consults it during volume admission and kubelet CSI calls. `podInfoOnMount` enables kubelet to pass the `csi.storage.k8s.io/ephemeral` context entry that the node server uses to identify inline ephemeral volumes.

## State, Persistence, And Dependencies
The resource persists in the Kubernetes API. It has no local storage state and depends on the cluster supporting `storage.k8s.io/v1` CSIDriver objects.

## Integration Points
It integrates with the node server's ephemeral handling, fsGroup behavior in kubelet, and the destroy script's label-based cleanup. The driver name must match the plugin `--drivername`, StorageClass provisioner, and snapshot classes.

## Risks
A mismatch in driver name breaks all Kubernetes-to-CSI routing. Enabling ephemeral lifecycle requires the node server to handle ephemeral create/delete correctly. `fsGroupPolicy: File` allows kubelet ownership changes and can alter test volume contents or permissions.

## Test Signals
Check that `kubectl get csidriver hostpath.csi.k8s.io` shows both lifecycle modes, inline volume examples reach `NodePublishVolume` with ephemeral context, and fsGroup-related storage e2e tests behave as expected.
