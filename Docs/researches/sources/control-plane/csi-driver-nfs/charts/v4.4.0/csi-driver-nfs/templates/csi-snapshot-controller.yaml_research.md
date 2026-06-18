# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose

This template optionally deploys the Kubernetes CSI external snapshot-controller when `.Values.externalSnapshotter.enabled` is true. The controller reconciles `VolumeSnapshot` and `VolumeSnapshotContent` objects independently from the NFS CSI driver pods.

## APIs, control flow, and state

When enabled, Helm renders an `apps/v1` `Deployment` named from `.Values.externalSnapshotter.name`. It uses one or more replicas, rolling update with `maxSurge: 0`, `minReadySeconds: 15`, Linux node selection, a release-namespace service account, optional labels/annotations, controller tolerations, and the configured snapshot-controller image. The container starts with `--leader-election=true` and `--leader-election-namespace={{ .Release.Namespace }}`. Runtime state is stored in snapshot API resources, status subresources, events, and leader-election leases.

## Dependencies and integration points

The deployment depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, the `snapshot.storage.k8s.io` API group, and controller leader-election permissions in the release namespace. It complements the `csi-snapshotter` sidecar running inside the NFS controller deployment.

## Risks and test signals

In v4.4.0 this deployment does not template `imagePullSecrets`, so private registries require separate handling or later chart behavior. Enabling it in clusters that already install a platform snapshot-controller can create duplicate controllers. Test with `helm template` enabled/disabled, `kubectl rollout status`, lease creation, snapshot status updates, and failure behavior when CRDs are missing; `minReadySeconds` is intended to cover startup failures when v1 CRDs are unavailable.
