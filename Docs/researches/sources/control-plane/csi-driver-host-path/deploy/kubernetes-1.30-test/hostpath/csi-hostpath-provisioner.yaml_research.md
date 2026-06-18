# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-provisioner.yaml

## Purpose
This manifest runs the external CSI provisioner as a separate one-replica StatefulSet in the Kubernetes 1.30 test deployment. It handles PVC-driven `CreateVolume` and `DeleteVolume` workflows against the hostpath driver socket.

## Important APIs, Types, And Functions
The resource is `apps/v1` `StatefulSet` `csi-hostpath-provisioner`, service account `csi-provisioner`, image `registry.k8s.io/sig-storage/csi-provisioner:v5.2.0`, arguments `-v=5`, `--csi-address=/csi/csi.sock`, and `--feature-gates=Topology=true`. It mounts `/var/lib/kubelet/plugins/csi-hostpath` at `/csi` and runs privileged for SELinux socket access.

## Control Flow
Pod affinity colocates the provisioner with the hostpath plugin. Once running, it watches PVC/PV objects and calls the driver's controller service over `/csi/csi.sock`, using topology support so created volumes advertise the hostpath node topology when enabled.

## State, Persistence, And Dependencies
The provisioner stores state in Kubernetes PV/PVC objects and uses the driver state store indirectly through CSI calls. It depends on provisioner RBAC fetched by the deploy script and on the driver socket hostPath.

## Integration Points
It integrates with StorageClasses using provisioner `hostpath.csi.k8s.io`, test-driver topology capabilities, and optional deploy-script insertion of `--prevent-volume-mode-conversion=true` for volume mode conversion tests.

## Risks
If the provisioner lands on a different node than the plugin, the socket path will not be usable. Topology feature-gate mismatches can affect binding. RBAC/image version skew is a common failure mode when tags are overridden.

## Test Signals
PVC creation should produce PVs, `CreateVolume` calls should appear in driver logs, topology-aware tests should bind to the driver node, and volume mode conversion tests should show the optional flag when enabled.
