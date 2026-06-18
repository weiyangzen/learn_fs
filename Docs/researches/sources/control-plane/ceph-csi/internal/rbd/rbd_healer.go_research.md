<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_healer.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_healer.go

## Purpose
`rbd_healer.go` implements a node-side recovery loop for `rbd-nbd` volumes. It reconstructs `NodeStageVolume` requests from Kubernetes `VolumeAttachment` and `PersistentVolume` objects so previously attached NBD devices can be reattached after node-server restart or NBD process loss.

## Important APIs, Types, And Functions
Key functions are `accessModeStrToInt`, `getSecret`, `formatStagingTargetPath`, `NodeServer.callNodeStageVolume`, and `NodeServer.RunVolumeHealer`. `fsTypeBlockName` identifies block-mode PVs.

## Control Flow
`RunVolumeHealer` lists `VolumeAttachment` objects, filters to the current node and driver, loads bound non-deleting PVs, skips non-CSI and non-`rbd-nbd` volumes, rechecks the attachment is still attached, and launches concurrent `callNodeStageVolume` calls. `callNodeStageVolume` derives the Kubernetes 1.24+ staging path using a SHA-256 hash of the volume handle, fetches the node-stage secret, adds `volumeHealerContext=true`, builds a CSI `NodeStageVolumeRequest`, sets block or mount access type, and invokes `NodeStageVolume`. In healer context, `NodeStageVolume` only reattaches using stashed device metadata.

## State And Persistence
The healer relies on Kubernetes API state and existing node-local `image-meta.json` under the hashed staging path. It mutates the PV volume attributes map in place by adding `volumeHealerContext`. No new independent persistent state is introduced.

## Dependencies And Integration Points
It depends on Kubernetes API helpers, CSI protobufs, RBD node staging, secrets, and kubelet staging path conventions. It integrates tightly with `rbd_attach.go` NBD attach support and the stash created by `nodeserver.go`.

## Risks
The staging path format is version-sensitive and currently assumes the hash-based path. `pv.Spec.AccessModes[0]` is accessed without checking length. The unbuffered channel with goroutines is drained after launcher completion starts; this works because receives begin after the launcher loop but can serialize goroutine completion. Mutating `VolumeAttributes` in place can surprise callers if reused. Only `rbd-nbd` volumes are healed.

## Test Signals
There are no direct tests in this subset. Useful tests would mock Kubernetes objects, staging path derivation, missing secrets, access-mode conversion, nil PV/CSI fields, and healer-context `NodeStageVolume` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_healer.go -->
