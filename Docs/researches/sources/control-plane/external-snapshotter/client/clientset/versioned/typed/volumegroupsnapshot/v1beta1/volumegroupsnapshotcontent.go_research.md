# sources/control-plane/external-snapshotter/client/clientset/versioned/typed/volumegroupsnapshot/v1beta1/volumegroupsnapshotcontent.go

Purpose: real typed client for cluster-scoped v1beta1 `VolumeGroupSnapshotContent`.
Important APIs/types/functions: content getter/interface with `UpdateStatus`, `volumeGroupSnapshotContents`, `newVolumeGroupSnapshotContents`.
Control flow: wraps generic list client for root-scope `volumegroupsnapshotcontents`; operations encode options with generated scheme and decode v1beta1 objects.
State/persistence: remote Kubernetes API server state only.
Dependencies/integration: controller reconciliation uses content status as the authoritative on-disk group snapshot state.
Risks/test signals: tests should cover status update/patch paths, root scope, and versioned object decoding.
