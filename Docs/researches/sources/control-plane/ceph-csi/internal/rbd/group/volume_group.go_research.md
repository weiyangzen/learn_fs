# sources/control-plane/ceph-csi/internal/rbd/group/volume_group.go

## Purpose
Implements the `types.VolumeGroup` abstraction backed by librbd groups and RADOS journal mappings, including group creation/deletion, volume membership management, CSI-Addons conversion, and group-consistent snapshot creation.

## Important APIs, Types, And Functions
`volumeGroup` embeds `commonVolumeGroup` and tracks member volumes plus owned volume handles. `GetVolumeGroup` resolves an existing group and its member volumes from journal mappings. Methods include `ToCSI`, `Destroy`, `Create`, `Delete`, `AddVolume`, `RemoveVolume`, `ListVolumes`, and `CreateSnapshots`.

## Control Flow
Lookup initializes common group state, loads journal attributes, resolves member volume IDs, and arranges cleanup ownership. Create calls `librbd.GroupCreate`, tolerating existing groups. Delete calls `librbd.GroupRemove`, tolerating missing groups, then removes the journal reservation. Add/remove operations update librbd membership first and then update the journal volume map. `CreateSnapshots` creates a temporary librbd group snapshot, reads group snapshot info, removes the temporary group snapshot on exit, matches returned snapshot entries to known volumes by image name, and creates CSI snapshot images from librbd snapshot IDs.

## State And Persistence
Persistent state includes the librbd group, image membership, snapshot images created from group snapshots, and RADOS journal reservation/membership mapping. The temporary librbd group snapshot is deliberately removed after per-volume snapshot images are created.

## Dependencies And Integration Points
Depends on go-ceph rados/librbd, CSI and CSI-Addons volume group protobufs, common group utilities, `types.Volume`, and journal mappings. It is used by `manager.go` and the controller group snapshot RPC path.

## Risks And Test Signals
Risks include split-brain between librbd membership and journal mapping, non-deterministic snapshot ordering from librbd info, partial snapshot creation cleanup, name-based matching between group snapshot entries and volumes, and tolerating `ErrExist`/`ErrNotFound` in ways that may mask stale state. No direct tests exist in this subset.
