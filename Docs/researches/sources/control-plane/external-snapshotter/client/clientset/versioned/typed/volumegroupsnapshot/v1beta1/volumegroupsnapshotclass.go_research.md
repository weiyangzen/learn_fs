# sources/control-plane/external-snapshotter/client/clientset/versioned/typed/volumegroupsnapshot/v1beta1/volumegroupsnapshotclass.go

Purpose: real typed client for cluster-scoped v1beta1 `VolumeGroupSnapshotClass`.
Important APIs/types/functions: class getter/interface and `volumeGroupSnapshotClasses` wrapping `gentype.ClientWithList`.
Control flow: constructor uses empty namespace and resource `volumegroupsnapshotclasses`; generic methods issue root-scope REST calls.
State/persistence: API server persistence only.
Dependencies/integration: used by beta controllers/tools that create or inspect group snapshot classes.
Risks/test signals: validate root-scope request paths and versioned GVR; schema immutability is server-side.
