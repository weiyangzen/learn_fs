# sources/control-plane/rook/deploy/examples/subvolumegroup.yaml

Purpose: creates a CephFS subvolume group for organizing CephFS CSI subvolumes.

Important APIs/types/functions: `CephFilesystemSubVolumeGroup/group-a`, `filesystemName`, and `pinning` configuration.

Control flow: Rook reconciles the CR by creating the named subvolume group in the target CephFS filesystem.

State and persistence: group metadata persists in CephFS; Kubernetes stores desired pinning policy.

Dependencies/integration: requires an existing `CephFilesystem`.

Risks: wrong filesystem name leaves the CR pending; pinning settings affect data placement.

Test signals: `ceph fs subvolumegroup ls <fs>` includes the group and CSI volumes can target it.
