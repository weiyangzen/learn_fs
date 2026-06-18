<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/crd-csi-snapshot.yaml

## Purpose
Installs the snapshot API CRDs used by the v4.9.0 deployment set. This file is equivalent to the v4.8.0 CRD manifest and defines `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass`.

## Important APIs, Types, and Functions
The CRDs are `apiextensions.k8s.io/v1` resources in API group `snapshot.storage.k8s.io`, with OpenAPI schemas, printer columns, served/storage v1 versions, deprecated v1beta1 compatibility blocks, and `status` subresources. The schemas validate snapshot sources, content references, deletion policies, driver names, restore sizes, readiness, errors, and snapshot handles.

## Control Flow, State, and Persistence
The API server stores snapshot desired state and status. Users create snapshot requests/classes, the snapshot-controller binds snapshots to contents, and CSI snapshotter sidecars update physical snapshot status through the API. The CRD schemas are the durable contract for these objects.

## Dependencies and Integration Points
They integrate with snapshot-controller v8.0.1, CSI snapshotter v8.0.1, Kubernetes CRD discovery/admission, and driver-specific snapshot implementations such as NFS tar archive snapshots.

## Risks and Test Signals
Risks include CRD/controller version skew, deprecated v1beta1 clients, validation incompatibilities, and missing status RBAC. Signals are established CRDs, discovery of `snapshot.storage.k8s.io/v1`, accepted snapshot classes, and snapshots with status fields updated by controllers.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/crd-csi-snapshot.yaml -->
