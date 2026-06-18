# sources/control-plane/external-snapshotter/client/clientset/versioned/typed/volumegroupsnapshot/v1beta1/fake/fake_volumegroupsnapshotclass.go

Purpose: fake cluster-scoped v1beta1 `VolumeGroupSnapshotClass` client.
Important APIs/types/functions: `fakeVolumeGroupSnapshotClasses`, constructor `newFakeVolumeGroupSnapshotClasses`, resource `volumegroupsnapshotclasses`, kind `VolumeGroupSnapshotClass`.
Control flow: delegates all operations to `gentype.NewFakeClientWithList` with empty namespace and type-specific list conversion callbacks.
State/persistence: in-memory only.
Dependencies/integration: exposed by `FakeGroupsnapshotV1beta1.VolumeGroupSnapshotClasses`.
Risks/test signals: CRD-level deprecation and validation are not simulated. Tests should confirm root-scope fake actions and list filtering.
