# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-snapshot-controller.yaml

## Purpose
This manifest deploys the external CSI snapshot controller used by the v4.4.0 bundle. It reconciles `VolumeSnapshot` and `VolumeSnapshotContent` objects independently of the NFS CSI driver pods.

## Important APIs, Types, and Functions
The object is an `apps/v1` `Deployment` named `snapshot-controller` in `kube-system` with two replicas, `minReadySeconds: 15`, rolling update `maxSurge: 0`, and `maxUnavailable: 1`. It runs `registry.k8s.io/sig-storage/snapshot-controller:v6.2.2` with `--leader-election=true`, `--leader-election-namespace=kube-system`, and verbosity 2.

## Control Flow, State, and Persistence
Kubernetes schedules two Linux controller pods with control-plane tolerations and `system-cluster-critical` priority. Only the elected replica actively reconciles snapshot API objects; the second replica provides failover. It waits for v1 snapshot CRDs before readiness and persists state by updating snapshot custom resources and events.

## Dependencies and Integration Points
It depends on snapshot CRDs from `crd-csi-snapshot.yaml` and permissions from `rbac-snapshot-controller.yaml`. It integrates with the NFS controller's `csi-snapshotter` sidecar, which talks to the CSI driver, while this controller owns the Kubernetes-level snapshot binding loop.

## Risks and Test Signals
Risks include deploying the controller before CRDs, insufficient RBAC for status updates, mismatched controller/CRD versions, and leader-election lease conflicts in `kube-system`. Test signals are two available replicas, one active leader lease, no CRD discovery crash loops, status updates on `VolumeSnapshot`, and successful snapshot deletion according to `deletionPolicy`.
