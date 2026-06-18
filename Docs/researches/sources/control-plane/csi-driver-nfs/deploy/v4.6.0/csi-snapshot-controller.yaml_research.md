# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-snapshot-controller.yaml

## Purpose
This manifest deploys the v4.6.0 external snapshot controller. It updates the controller image to v6.3.3 and adds capability dropping for the container.

## Important APIs, Types, and Functions
The `Deployment` is `snapshot-controller` in `kube-system`, two replicas, `minReadySeconds: 15`, `maxSurge: 0`, `maxUnavailable: 1`, Linux node selector, control-plane tolerations, and `system-cluster-critical` priority. The container runs `snapshot-controller:v6.3.3`, `--v=2`, and leader election in `kube-system`, with `securityContext.capabilities.drop: [ALL]`.

## Control Flow, State, and Persistence
The elected controller replica reconciles snapshot CRDs, updates status and events, and uses a coordination lease. The standby replica provides failover while rolling updates preserve one available controller. Persistent state is entirely Kubernetes API state.

## Dependencies and Integration Points
It depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, and the NFS controller's `csi-snapshotter:v6.3.3`. It also relies on the CRDs being present long enough for readiness because the deployment comments document startup failure when v1 CRDs are missing.

## Risks and Test Signals
Risks include image/CRD skew, missing status verbs, capability drop incompatibility if the image expected extra Linux capabilities, and leader-election namespace errors. Test signals are ready replicas, one leader lease, snapshot status updates, no forbidden errors, and clean upgrade from v6.3.1.
