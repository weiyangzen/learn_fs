# sources/control-plane/external-snapshotter/client/config/crd/groupsnapshot.storage.k8s.io_volumegroupsnapshotcontents.yaml

Purpose: CRD for cluster-scoped `VolumeGroupSnapshotContent`, representing the storage-system group snapshot and per-volume snapshot handles.
Important APIs/types/functions: names plural `volumegroupsnapshotcontents`, short names `vgsc`/`vgscs`, versions `v1`, deprecated `v1beta1`, storage `v1beta2`; required spec fields include `deletionPolicy`, `driver`, `source`, and `volumeGroupSnapshotRef`; status subresource is enabled.
Control flow: schema validates dynamic vs pre-provisioned sources: exactly one of `volumeHandles` or `groupSnapshotHandles`; group handles require a group handle and snapshot handle list. Status carries readiness, creation time, error, group handle, and per-volume snapshot info/pairs depending on version.
State/persistence: storage version is v1beta2; status is persisted separately through `/status`.
Dependencies/integration: consumed by group snapshot controller/sidecar and bound to namespaced `VolumeGroupSnapshot` through `volumeGroupSnapshotRef`.
Risks/test signals: CEL references `self.__namespace__` for object references and must be verified against Kubernetes CRD validation behavior. Tests should cover install, status updates, immutable fields, one-of source validation, and version differences between `volumeSnapshotHandlePairList` and `volumeSnapshotInfoList`.
