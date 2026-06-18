# sources/control-plane/ceph-csi/internal/rbd/group.go

## Purpose
Adapts `rbdVolume` to the volume-group interfaces used by the RBD group package and CSI-Addons volume-group workflows.

## Important APIs, Types, And Functions
`(*rbdVolume).AddToGroup` validates current group membership and calls `librbd.GroupImageAdd`. `RemoveFromGroup` calls `librbd.GroupImageRemove`. `GetVolumeGroupID` reads librbd group information for an image and asks a resolver to construct a CSI volume-group ID.

## Control Flow
Add opens the image, reads its current group, rejects membership in a different group, then adds the image to the requested group using the group IO context and image IO context. Removal resolves the group name and IO context, then removes the image. ID lookup opens the image, reads group info, returns `ErrGroupNotFound` if none is set, otherwise resolves the backend pool/name into a CSI handle.

## State And Persistence
These methods mutate or read librbd group membership. They do not directly write the RADOS journal; higher-level `group/volume_group.go` updates journal volume maps after successful membership changes.

## Dependencies And Integration Points
Depends on go-ceph/librbd, RBD image open helpers, `types.VolumeGroup`, `types.VolumeGroupResolver`, and group errors. It is called by the `internal/rbd/group` package when creating/removing groups and by manager comparison logic.

## Risks And Test Signals
Risks include inconsistent state if librbd membership succeeds but journal updates fail, or if image group info is stale during concurrent group operations. There are no direct unit tests for these methods; behavior is best covered by group snapshot and CSI-Addons integration tests.
