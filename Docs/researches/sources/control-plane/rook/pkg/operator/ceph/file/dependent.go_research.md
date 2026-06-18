# sources/control-plane/rook/pkg/operator/ceph/file/dependent.go

## Purpose
This file implements deletion dependency detection for `CephFilesystem`. Since ordinary CephFS usage does not create RBD images, the operator blocks filesystem deletion by checking for CephFS subvolume groups containing subvolumes and `CephFilesystemSubVolumeGroup` CRs that reference the filesystem.

## Important APIs, Types, and Functions
The exported variable `CephFilesystemDependents` points to `cephFilesystemDependents` and is overridable for unit tests. `filesystemExists` wraps `cephclient.GetFilesystem` and treats Ceph `ENOENT` as safe absence. `subvolumeGroupDependents` calls `ListSubvolumeGroups` and `ListSubvolumesInGroup`, adds the explicit no-group case, ignores internal groups via `ignoreSVG`, and reports non-empty groups through a `dependents.DependentList`.

## Control Flow, State, and Persistence
`cephFilesystemDependents` creates an empty dependency list, checks whether the Ceph filesystem exists, and only queries Ceph subvolume groups when it does. It then lists Kubernetes `CephFilesystemSubVolumeGroup` resources in the namespace and adds those whose `Spec.FilesystemName` matches the filesystem. It returns aggregated errors from subvolume listing, but a filesystem-existence error is swallowed and returns an empty list.

## Dependencies and Integration Points
The logic integrates Ceph CLI-backed client calls, the Rook typed clientset, operator deletion reporting, and the common `dependents` utility. The dependent type string is written for user-facing deletion-block reports. Ignored Ceph group names include `_nogroup`, `_index`, `_legacy`, and `_deleting`, with a separate explicit no-group check represented as `<no group>`.

## Risks
Swallowing unexpected `filesystemExists` errors allows deletion to proceed without dependency checks if Ceph existence cannot be determined. Listing every subvolume in every non-ignored group can time out on large filesystems; the aggregate error message acknowledges this. Ignored internal groups could contain manually created data, but the code intentionally treats that as rare to avoid false deletion blocks from Ceph internals.

## Test Signals
Important signals are empty results for missing filesystem, detection of matching `CephFilesystemSubVolumeGroup` CRs, ignoring wrong-filesystem CRs, detection of non-empty Ceph subvolume groups, aggregation of list-subvolume errors, ignoring internal groups, and reporting subvolumes not in any group as `<no group>`.
