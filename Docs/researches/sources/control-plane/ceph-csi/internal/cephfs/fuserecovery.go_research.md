## sources/control-plane/ceph-csi/internal/cephfs/fuserecovery.go

Purpose: Implements recovery for corrupted or missing Ceph-FUSE stage/publish mounts after node plugin restarts or mount failures.

Important types/functions: `mountState` enum (`msUnknown`, `msNotMounted`, `msMounted`, `msCorrupted`), `String`, `getMountState`, `tryRestoreFuseMountsInNodePublish`, and `tryRestoreFuseMountInNodeStage`.

Control flow: Recovery first classifies stage and target paths using `IsMountPoint` and corrupted mount detection. NodePublish recovery requires a stored `NodeStageMountinfo` record; it rebuilds `VolumeOptions`, selects mounter, remounts staging if needed, and unmounts the publish target so normal publish can continue. NodeStage recovery simply unmounts a corrupted staging target and lets staging proceed.

State and persistence: Reads `NodeStageMountinfo` persisted by `fsutil` during successful FUSE staging. Uses current mount table state and may mutate mounts by unmounting/remounting.

Dependencies and risks: Depends on node server volume option resolution, mounter selection, and saved secrets/capability. If mountinfo is missing, recovery logs and returns nil, leaving normal flow to handle the state. Tests are absent; important scenarios are corrupted stage path, corrupted bind target, missing mountinfo, and non-FUSE volumes.
