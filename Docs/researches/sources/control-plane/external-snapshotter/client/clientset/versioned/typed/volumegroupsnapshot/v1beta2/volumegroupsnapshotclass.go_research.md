# sources/control-plane/external-snapshotter/client/clientset/versioned/typed/volumegroupsnapshot/v1beta2/volumegroupsnapshotclass.go

Purpose: real typed client for cluster-scoped v1beta2 `VolumeGroupSnapshotClass`.
Important APIs/types/functions: getter/interface and `volumeGroupSnapshotClasses` generic list client.
Control flow: constructor uses resource `volumegroupsnapshotclasses`, empty namespace, v1beta2 factories, and generated parameter codec.
State/persistence: API server persists classes.
Dependencies/integration: class selection for group snapshot provisioning.
Risks/test signals: tests should assert root-scope calls and version; server-side CEL validates immutable class fields.
