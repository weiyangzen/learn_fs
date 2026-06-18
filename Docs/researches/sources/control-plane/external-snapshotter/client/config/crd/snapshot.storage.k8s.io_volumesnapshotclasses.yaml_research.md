# sources/control-plane/external-snapshotter/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml

Purpose: CRD for cluster-scoped GA `VolumeSnapshotClass`.
Important APIs/types/functions: group `snapshot.storage.k8s.io`, plural `volumesnapshotclasses`, short names `vsclass`/`vsclasses`, served/storage `v1`, deprecated non-served `v1beta1`; required `deletionPolicy` and `driver`; optional opaque `parameters`.
Control flow: Kubernetes apiextensions uses the schema for validation and printer columns for driver, deletion policy, and age.
State/persistence: v1 is the only served storage version in this manifest; v1beta1 remains non-served/non-storage with deprecation warning text.
Dependencies/integration: snapshot controller reads class policy/parameters when provisioning `VolumeSnapshotContent`.
Risks/test signals: this snapshot class CRD lacks the CEL immutability present in newer group snapshot class schema, so immutability may rely on controller/admission elsewhere. Tests should cover CRD install, enum validation, deprecated version availability expectations, and class selection.
