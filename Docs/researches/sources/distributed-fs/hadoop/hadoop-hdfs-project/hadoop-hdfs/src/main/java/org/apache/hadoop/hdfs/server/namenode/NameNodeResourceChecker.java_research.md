# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeResourceChecker.java

## Purpose
`NameNodeResourceChecker` builds the set of local volumes whose free disk space must be checked before the NameNode continues writing edits. It covers local edits dirs and configured extra checked volumes, classifies required versus redundant volumes, and delegates policy evaluation to `NameNodeResourcePolicy`.

## Important APIs and Types
- Constructor `NameNodeResourceChecker(Configuration)` reads reserved bytes, checked volume config, local edits dirs, required edits dirs, and minimum redundant volume count.
- Inner `CheckedVolume` implements `CheckableNameNodeResource` using Hadoop `DF` to check available bytes on a filesystem.
- `hasAvailableDiskSpace()` returns the resource policy result.
- Testing hooks include `getVolumesLowOnSpace`, `setVolumes`, and `setMinimumReduntdantVolumes`.

## Control Flow
Construction resolves extra checked volumes from `dfs.namenode.checked.volumes`, filters namespace edits dirs to local `file` URIs, adds each edits dir with required status based on `FSNamesystem.getRequiredNamespaceEditsDirs`, adds extra dirs as required, and stores the minimum redundant volume threshold. `addDirToCheck` requires the directory to exist, collapses multiple directories on the same filesystem to one `CheckedVolume`, and upgrades an existing redundant volume to required if necessary.

## State and Persistence Behavior
All state is runtime-only: `duReserved`, `volumes`, and `minimumRedundantVolumes`. It does not modify disk. `CheckedVolume.isResourceAvailable` reads current filesystem free space and compares it with reserved bytes, logging warnings for low space.

## Dependencies and Integration Points
It depends on `FSNamesystem` for namespace edits dir config, `NNStorage.LOCAL_URI_SCHEME`, `Util.stringCollectionAsURIs`, Hadoop `DF`, DFS config keys, and `NameNodeResourcePolicy`. `FSNamesystem` resource monitoring and `NameNode.monitorHealth` use this path to enter safe mode or fail HA health checks when resources are exhausted.

## Risks and Edge Cases
- Missing checked directories cause constructor failure.
- Only local edits dirs are checked here; remote/shared journal health is handled elsewhere.
- Multiple configured dirs on the same filesystem collapse to one resource, which is correct for disk-space accounting but can surprise config audits.
- `getVolumesLowOnSpace` currently returns all volume names after invoking debug logging; despite its name, it does not filter by availability in this implementation.
- The testing method name `setMinimumReduntdantVolumes` contains a typo.

## Test Signals
`TestNameNodeResourceChecker` covers constructor behavior, required/redundant volume policy, monitor integration with safe mode, and mock resource checkers. Metrics tests also exercise low-resource reporting through NameNode state.
