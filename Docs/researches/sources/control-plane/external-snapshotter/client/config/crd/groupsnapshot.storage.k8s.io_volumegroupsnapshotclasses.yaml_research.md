# sources/control-plane/external-snapshotter/client/config/crd/groupsnapshot.storage.k8s.io_volumegroupsnapshotclasses.yaml

Purpose: CRD for cluster-scoped `VolumeGroupSnapshotClass` in `groupsnapshot.storage.k8s.io`.
Important APIs/types/functions: names plural `volumegroupsnapshotclasses`, short names `vgsclass`/`vgsclasses`, versions `v1`, deprecated `v1beta1`, and storage `v1beta2`. Required fields are `deletionPolicy` and `driver`; optional `parameters` is a string map.
Control flow: declarative schema consumed by Kubernetes apiextensions. Printer columns expose driver, deletion policy, and age.
State/persistence: CRD declares storage version `v1beta2`; all versions are served, with v1beta1 deprecated.
Dependencies/integration: used by snapshot controller/sidecar to select CSI driver parameters and deletion policy for group snapshot contents.
Risks/test signals: v1/v1beta2 add CEL immutability for `deletionPolicy`, `driver`, and `parameters`, while v1beta1 lacks those validations. Tests should cover apply/install, version conversion expectations, and invalid enum values.
