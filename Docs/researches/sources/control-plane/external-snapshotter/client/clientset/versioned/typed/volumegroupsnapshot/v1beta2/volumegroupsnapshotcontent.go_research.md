# sources/control-plane/external-snapshotter/client/clientset/versioned/typed/volumegroupsnapshot/v1beta2/volumegroupsnapshotcontent.go

Purpose: real typed client for cluster-scoped v1beta2 `VolumeGroupSnapshotContent`.
Important APIs/types/functions: content interface includes `UpdateStatus`; concrete client embeds generic list client for v1beta2 content types.
Control flow: `newVolumeGroupSnapshotContents` creates root-scope client for `volumegroupsnapshotcontents`; generic methods perform REST CRUD/list/watch/patch/status.
State/persistence: remote API server content and status storage.
Dependencies/integration: v1beta2 status includes per-volume snapshot information used by snapshot sidecars/controllers.
Risks/test signals: tests should cover status subresource updates and object decoding for `volumeSnapshotInfoList`; validation remains server-side.
