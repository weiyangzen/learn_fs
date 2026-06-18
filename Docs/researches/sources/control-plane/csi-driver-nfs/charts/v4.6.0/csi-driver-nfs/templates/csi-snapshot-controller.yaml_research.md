# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose

This v4.6.0 template optionally deploys the external snapshot-controller that reconciles Kubernetes `VolumeSnapshot` APIs.

## APIs, control flow, and state

It renders only when `.Values.externalSnapshotter.enabled` is true. The deployment includes configurable replicas, labels, annotations, image pull secrets, Linux node selection, priority, tolerations, resources, and leader-election arguments. v4.6.0 adds slash-prefixed repository support using `.Values.image.baseRepo` and adds a container security context that drops all capabilities. The controller persists reconciliation state through snapshot resources, status subresources, events, and leader-election leases.

## Dependencies and integration points

The deployment depends on snapshot CRDs, snapshot-controller RBAC, the configured image, and a compatible Kubernetes snapshot API. It complements the `csi-snapshotter` sidecar in the NFS CSI controller deployment.

## Risks and test signals

The external controller should not duplicate a cluster-provided snapshot-controller. Base-repo image composition can render invalid images if values are inconsistent. Test enabled/disabled rendering, private image pull secrets, slash-prefixed image repositories, capability-restricted runtime, leader-election lease updates, and end-to-end snapshot reconciliation.
