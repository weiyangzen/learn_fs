# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTable.java

## Purpose

`TestRouterMountTable.java` is a broad end-to-end test suite for Router mount-table behavior. It covers read-only mounts, admin path component limits, listing modification times, synthetic mount-point statuses, default namespace disabling, mount permissions, child counts, exception path rewriting, trailing slash listings, file info on ancestor mounts, delete/rename guards around mount points, erasure-coding status, and `getEnclosingRoot`. The source was read as a complete 815-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `StateStoreDFSCluster`, `RouterContext`, `NamenodeContext`, `MountTableResolver`, `MountTableManager`, `RouterClientProtocol`, `ClientProtocol`, `DirectoryListing`, `HdfsFileStatus`, `DistributedFileSystem`, `FsPermission`, `UserGroupInformation`, and mount-table state-store requests. Helpers include `globalSetUp`, `clearMountTable`, `addMountTable`, `updateMountTable`, `getListing`, and `createEntry`.

## Control Flow

Global setup starts a two-namespace state-store cluster with admin/RPC enabled and a maximum mount component length. Each test adds mount-table records via admin API, refreshes the resolver cache, performs router or namenode filesystem operations, and asserts behavior. The suite tests read-only write rejection; add/update validation for overly long path components; root listing modification-time consistency between mount records and actual namespace entries; synthetic mount-point status owner/group behavior when remote `getFileInfo` raises permission errors; listing without a default namespace; permissions from mount records versus remote destinations; multi-destination permission and child aggregation; path rewriting in exceptions; trailing-slash `getListing`; mount-point delete/rename protection; erasure-coded mount status; and enclosing-root resolution before and after adding a mount.

## State and Persistence Behavior

Mount-table entries are persisted through the router admin client and then loaded into `MountTableResolver`. Remote filesystem state is created on `nnFs0` and `nnFs1` and deleted in `finally` blocks. `clearMountTable` removes every mount entry and resets default namespace support after each test. `startTime` is captured to validate modification times generated during the suite.

## Dependencies and Integration Points

The file integrates state-store mount-table protocols, router RPC path resolution, router filesystem behavior, HDFS metadata/status types, HDFS permissions, EC policy state, default namespace fallback, and mount-point guard logic for destructive operations.

## Risks and Edge Cases

This is a high-blast-radius regression suite: it asserts exact exception message fragments, owner/group/mode fallback behavior, ordering-sensitive root listings, and HDFS path rewriting. Some multi-destination permission tests allow either namespace's metadata when destinations differ. The default namespace is toggled inside tests and must be reset to avoid cross-test contamination.

## Test Signals

Strong signals include read-only `IOException`, path component limit failures, listing lengths and modification times, synthetic owner/group values, `FileNotFoundException` with router-visible paths, exact mount permissions when destination is absent, destination permissions when present, child-count aggregation, `AccessControlException` for deleting or renaming mount points, EC status visible through `listStatus`, and correct `getEnclosingRoot` values.
