# sources/control-plane/external-snapshotter/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml

Purpose: CRD for cluster-scoped `VolumeSnapshotContent`, representing the actual CSI snapshot object and binding to a namespaced `VolumeSnapshot`.
Important APIs/types/functions: group `snapshot.storage.k8s.io`, plural `volumesnapshotcontents`, short names `vsc`/`vscs`, served/storage `v1`, deprecated non-served `v1beta1`; required spec fields `deletionPolicy`, `driver`, `source`, and `volumeSnapshotRef`; status subresource enabled.
Control flow: schema validates exactly one of `source.volumeHandle` and `source.snapshotHandle`; `sourceVolumeMode` is immutable/required once set; status exposes creation time, error, readiness, restore size, snapshot handle, and group snapshot handle.
State/persistence: v1 storage with `/status` subresource. v1beta1 schema remains for compatibility metadata but is not served.
Dependencies/integration: snapshot sidecar/controller creates and updates content objects, and consumers must verify bidirectional binding with `VolumeSnapshot`.
Risks/test signals: object reference validation uses CEL fields such as `self.__namespace__`; tests should cover CRD dry-run, source one-of validation, status updates, restore size minimum, and binding security assumptions.
