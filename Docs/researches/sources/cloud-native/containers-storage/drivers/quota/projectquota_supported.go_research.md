<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota_supported.go -->
# sources/cloud-native/containers-storage/drivers/quota/projectquota_supported.go

## Purpose
This Linux+cgo implementation provides XFS project quota control for graph drivers, mainly overlay on XFS with project quotas enabled.

## Important APIs, Types, And Functions
`Quota` stores byte and inode limits. `Control` tracks the backing block device, next project ID, `targetPath -> projectID` map, and base path. `NewControl`, `SetQuota`, `ClearQuota`, `GetQuota`, and `GetDiskUsage` are the public operations. Internal functions manage project IDs via `FS_IOC_FSGETXATTR`/`FS_IOC_FSSETXATTR`, set quota limits via `quotactl`, create the backing block device node, and scan existing directories for used project IDs.

## Control Flow
`NewControl` reads or generates a base project ID, creates/recreates `backingFsBlockDev`, verifies quota support by setting a zero quota, clears project inheritance from the top-level directory, and scans existing children to seed the map and next ID. `SetQuota` reuses an existing project ID for a target or assigns `nextProjectID` to an empty directory, sets `FS_XFLAG_PROJINHERIT`, records the mapping, increments the counter, and applies block/inode limits. Reads resolve the stored project ID and call `Q_XGETPQUOTA`.

## State And Persistence
Persistent state includes XFS project IDs and inherit flags on directories plus the block-device node under the quota home. In-memory state is `sync.Map` quota assignments and `nextProjectID`. On startup, `findNextProjectID` reconstructs much of the in-memory state from existing directories.

## Dependencies And Integration Points
The file uses cgo Linux quota and fs ioctls, `unix.Syscall6`, `directory.DiskUsage`, logrus, and filesystem stat data. Overlay initializes `Control` only on XFS and calls `SetQuota`, `GetDiskUsage`, and `ClearQuota`.

## Risks And Edge Cases
Project ID generation is inode-derived and reserves ranges of 10,000 IDs per quota home, reducing but not eliminating administrative conflicts. `SetQuota` requires empty target directories because project ID inheritance does not apply retroactively. Missing `backingFsBlockDev` is recreated on quota set, but device changes and copied stores remain operational hazards. Concurrency relies on `sync.Map` but `nextProjectID` increments are not protected by an explicit mutex in this file.

## Test Signals
Coverage depends on quota-capable XFS integration tests. ZFS has quota tests separately; this package has no direct unit test in the listed files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota_supported.go -->
