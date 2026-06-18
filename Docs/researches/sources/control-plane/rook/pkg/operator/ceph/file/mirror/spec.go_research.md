<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec.go

## Purpose
This file builds the Kubernetes Deployment and containers for the CephFS mirror daemon. It translates `CephFilesystemMirror` placement, labels, annotations, resources, priority, networking, and cluster image settings into a one-replica Deployment running `cephfs-mirror`.

## Important APIs and control flow
`makeDeployment` creates a pod template with a chown init container, the `fs-mirror` daemon container, daemon volumes, service account, host network or Multus settings, tolerations, placement, and optional log collector sidecar. It sets selector labels with `controller.CephDaemonAppLabels`, applies CR annotations/labels to the pod template and Deployment, and adds Rook/Ceph version labels. `makeChownInitContainer` delegates to `controller.ChownCephDataDirsInitContainer`. `makeFsMirroringDaemonContainer` runs `cephfs-mirror --foreground --name=client.fs-mirror` with daemon flags, env vars, resource requirements, default security context, and daemon volume mounts.

## State and persistence
The Deployment is the durable Kubernetes object. The daemon data path uses `controller.DaemonVolumes` and a dataless data path map supplied by `mirror.go`, so this spec primarily persists configuration through pod template fields and annotations. CR annotations and labels are copied to Kubernetes objects.

## Dependencies and integration points
The file is tightly coupled to Rook Ceph daemon helpers for command flags, security context, labels, volumes, version labels, log collection, and Multus attachment. It also depends on the Ceph cluster spec for image, data directory, network mode, and log collector settings.

## Risks and test signals
Selector and label changes can trigger immutable-field update problems handled by `mirror.go`. The daemon lacks a liveness probe, with a TODO noting that health checking remains incomplete. `spec_test.go` validates volume counts, service account, labels, resources, priority class, and standard pod-template expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec.go -->
