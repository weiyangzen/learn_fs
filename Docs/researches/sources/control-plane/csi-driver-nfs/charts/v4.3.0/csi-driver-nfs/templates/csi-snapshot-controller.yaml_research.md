# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This template optionally deploys the v4.3.0 external snapshot controller.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` when `externalSnapshotter.enabled` is true. It uses configurable name, labels, annotations, replica count, image, pull policy, and controller tolerations, but hard-codes a small resource profile and does not expose image pull secrets in this version.

## Control Flow, State, and Persistence
The Deployment uses `minReadySeconds: 15`, rolling updates with no surge, Linux node selection, cluster-critical priority, and leader election in the release namespace. It writes status to snapshot API objects and uses namespace leases for leader state.

## Dependencies and Integration Points
It depends on v4.3.0 snapshot CRDs and `rbac-snapshot-controller.yaml`. It works with the controller Deployment's optional `csi-snapshotter` sidecar.

## Risks and Test Signals
Risks include duplicate cluster snapshot controllers, fixed resources, no imagePullSecrets support, and no affinity support in this version. Signals are snapshot controller rollout, lease creation, no CRD discovery crash, and successful VolumeSnapshot binding.
