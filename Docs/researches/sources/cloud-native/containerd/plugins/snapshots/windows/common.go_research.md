<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/common.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/common.go

## Purpose
Provides shared Windows snapshotter infrastructure for metadata, common snapshot APIs, removal preparation, UVM scratch creation, scratch disk copying, and scratch size label parsing.

## Important APIs, Types, And Functions
`windowsBaseSnapshotter` holds root, metastore, and hcsshim driver info. Common methods are `newBaseSnapshotter`, `getSnapshotDir`, `parentIDsToParentPaths`, `Stat`, `Update`, `Usage`, `Walk`, `preRemove`, and `Close`. Helpers are `createUVMScratchLayer`, `copyScratchDisk`, and `getRequestedScratchSize`.

## Control Flow
Base initialization creates root, `metadata.db`, and `snapshots/`. `preRemove` removes metadata in a transaction, renames the snapshot directory to `rm-<id>`, and if permission is denied attempts HCS layer deactivation before retrying. UVM scratch creation locates the base layer `UtilityVM/SystemTemplate.vhdx`, creates a `vm` subdir, and copies it to `vm/sandbox.vhdx`.

## State And Persistence
Shared state is `metadata.db`, `snapshots/<id>` directories, renamed `rm-<id>` directories, and copied scratch VHDX files. Active usage scans snapshot directories; committed usage comes from metadata unless specialized snapshotters add layer-specific usage.

## Dependencies And Integration Points
Uses hcsshim driver info and layer deactivation, containerd snapshot storage, continuity disk usage, and labels defined in Windows snapshotter files.

## Risks And Edge Cases
Rename rollback failure can leave inconsistent state. Permission-denied removal recovery is best-effort. Scratch size labels support both deprecated GB and newer byte labels, preferring bytes; invalid values fail snapshot creation.

## Test Signals
Exercised indirectly by WCOW, CimFS, and block-CIM snapshotters plus Windows snapshotter suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/common.go -->
