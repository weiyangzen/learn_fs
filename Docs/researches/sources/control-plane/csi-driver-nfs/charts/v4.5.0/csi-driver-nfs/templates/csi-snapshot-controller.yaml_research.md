# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose

This v4.5.0 template optionally deploys the external snapshot-controller `Deployment` when `.Values.externalSnapshotter.enabled` is true.

## APIs, control flow, and state

The deployment renders replicas, labels, annotations, service account, Linux node selection, priority, tolerations, image, resources, and leader-election arguments from values. v4.5.0 adds `imagePullSecrets` support, allowing private registry credentials to be attached to the snapshot-controller pod. It persists reconciliation state in snapshot objects, their status subresources, events, and leader-election leases.

## Dependencies and integration points

It depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, the snapshot-controller image, and lease permissions in the release namespace. It works with the `csi-snapshotter` sidecar in the NFS controller deployment to implement Kubernetes CSI snapshot workflows.

## Risks and test signals

The controller should not be enabled in clusters that already provide a snapshot-controller unless duplicate reconciliation is intended. Missing CRDs cause startup/readiness failures; `minReadySeconds: 15` is meant to avoid marking it ready too early. Test rendering with image pull secrets, rollout with enabled/disabled CRDs, lease creation, snapshot status reconciliation, and private-registry image pulls.
