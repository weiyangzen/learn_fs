# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-resizer.yaml

## Purpose
This manifest runs the external CSI resizer as a separate StatefulSet for controller expansion testing. It watches PVC resize requests and calls the driver's `ControllerExpandVolume` RPC through the shared CSI socket.

## Important APIs, Types, And Functions
The resource is `StatefulSet` `csi-hostpath-resizer`, service account `csi-resizer`, image `registry.k8s.io/sig-storage/csi-resizer:v1.13.1`, arguments `-v=5` and `-csi-address=/csi/csi.sock`, and a privileged container with `/csi` mounted from `/var/lib/kubelet/plugins/csi-hostpath`.

## Control Flow
The pod is colocated with the hostpath plugin via required pod affinity. The resizer observes PVC capacity changes, sends CSI expansion calls, and lets kubelet perform node-side expansion when required by the driver response.

## State, Persistence, And Dependencies
Resize state is reflected in Kubernetes PVC/PV status and in the driver state JSON where volume size is updated. The manifest depends on external-resizer RBAC and socket availability.

## Integration Points
It is used with StorageClasses that set `allowVolumeExpansion: true` and with the driver's controller/node expansion capability flags. Deploy image substitution can alter the sidecar version.

## Risks
The container is privileged for socket access. If controller or node expansion flags are disabled in the driver, the sidecar observes unsupported RPCs. Driver expansion updates metadata but does not grow a real filesystem, because this is an e2e test driver.

## Test Signals
Expansion e2e should show the PVC size increasing, `ControllerExpandVolume` and `NodeExpandVolume` calls in driver logs, and failure for requests above configured maximum sizes.
