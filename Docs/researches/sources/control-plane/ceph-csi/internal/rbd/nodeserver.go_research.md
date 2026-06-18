<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/nodeserver.go -->
# sources/control-plane/ceph-csi/internal/rbd/nodeserver.go

## Purpose
`nodeserver.go` implements the CSI node-side lifecycle for RBD volumes: staging, publishing, unpublishing, unstaging, node expansion, node capabilities, volume stats, filesystem formatting, block and file encryption activation, cgroup QoS application, and node-local recovery hooks.

## Important APIs, Types, And Functions
`NodeServer` embeds `csicommon.DefaultNodeServer`, keeps per-volume and per-target `VolumeLocks`, and caches feature probes for ext4 prezeroed and xfs reflink support. `stageTransaction` records rollback state for stage failures. Main CSI entry points are `NodeStageVolume`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeUnstageVolume`, `NodeExpandVolume`, `NodeGetCapabilities`, and `NodeGetVolumeStats`.

Important helpers include `populateRbdVol`, `initStaticVol`, `initDynamicVol`, `stageTransaction`, `undoStagingTransaction`, `mountVolumeToStagePath`, `mountVolume`, `createStageMountPoint`, `createTargetMountPath`, `resizeNodeStagePath`, `processEncryptedDevice`, `getNodePublishCredentials`, `applyCgroupQoSIfConfigured`, `setUserIdMapping`, `setClientAddress`, and `getMkfsArgs`.

## Control Flow
`NodeStageVolume` validates the request, builds credentials, locks the volume ID, checks idempotent staging unless the request is a healer context, resolves static or dynamic RBD volume metadata, sets network namespace state, writes image metadata into the staging parent, then calls `stageTransaction`. The transaction flattens unsupported clone/deep-flatten chains if needed, maps the image, opens encryption when configured, creates the stage file or directory, mounts or bind-mounts the device, unlocks fscrypt directories, and optionally resizes.

`NodePublishVolume` validates the request and service-account restrictions, locks the target path and pod UID, creates the target path, bind-mounts the staged path to the pod path, and applies cgroup v2 QoS after mount. `NodeUnpublishVolume` unmounts and removes the target path. `NodeUnstageVolume` unmounts the staging path, removes it, reads `image-meta.json`, unmaps by image spec or device, and deletes the stash. `NodeExpandVolume` finds the staging path, reads stash metadata, locates the mapped RBD device, resizes encrypted mappings, and performs filesystem resize for non-block volumes.

## State And Persistence
Node-local persistent state is the staging directory and `image-meta.json` stash written by `stashRBDImageMetadata` and updated with the mapped device. Cluster state is touched through RBD image metadata keys for client address and user ID mapping. Runtime state includes per-volume locks, kernel feature probe caches, temporary mkfs probe files, and live device mappings. The code intentionally keeps static volumes out of some metadata writes.

## Dependencies And Integration Points
This file depends on CSI protobufs, Kubernetes mount utilities, Ceph RBD helpers in this package, `util` credential/config helpers, fscrypt, encryption helpers, Kubernetes secrets, RBD net namespace configuration, and cgroup QoS handlers. It integrates with kubelet CSI stage/publish paths, VolumeAttachment healer flow, Ceph fencing metadata, RBD NBD/krbd mapping, and VolumeAttributesClass-style QoS.

## Risks
The staging transaction spans local files, mounts, encrypted mapper devices, RBD mappings, and cluster metadata, so rollback ordering is critical. `cleanupRBDImageMetadataStash` treats missing stash as an error in rollback paths. QoS during publish is deliberately best-effort for missing credentials or volume initialization, but actual cgroup write errors are logged and returned only from the helper. `createDiff`-style resize paths depend on stash accuracy. `processEncryptedDevice` rejects unexpected pre-existing formats, protecting data but making migration/static cases sensitive. `mountVolumeToStagePath` trusts custom `mkfsOptions` from volume context.

## Test Signals
Existing tests cover `getStagingTargetPath`, boolean option parsing, read-affinity map option appending, and read-affinity config selection. Missing direct coverage includes full stage rollback, stash cleanup errors, encrypted stage/unstage, node publish credential fallback, cgroup QoS behavior, and node expansion against stale or missing mappings.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/nodeserver.go -->
