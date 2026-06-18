# sources/control-plane/external-snapshotter/client/config/crd/groupsnapshot.storage.k8s.io_volumegroupsnapshots.yaml

Purpose: CRD for namespaced `VolumeGroupSnapshot`, the user-facing request to create a group snapshot from selected PVCs or bind a pre-existing content.
Important APIs/types/functions: names plural `volumegroupsnapshots`, short name `vgs`, versions `v1`, deprecated `v1beta1`, storage `v1beta2`; required top-level `spec`; status subresource enabled.
Control flow: schema requires `spec.source` and validates exactly one of `selector` or `volumeGroupSnapshotContentName`; class name may be absent for defaulting but cannot be empty when set. Status exposes bound content name, creation time, error, and `readyToUse`.
State/persistence: namespaced CRD stored as v1beta2; status persisted through `/status`.
Dependencies/integration: controllers watch these objects, create/bind `VolumeGroupSnapshotContent`, and update status. Consumers must verify bidirectional binding before use.
Risks/test signals: selector/content source immutability and bound content immutability differ across versions. Tests should cover CRD install, status subresource RBAC, one-of validation, empty class rejection, and binding security checks.
