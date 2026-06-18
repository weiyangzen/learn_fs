# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMetadataVersionOutput.java

## Purpose
Validates the `NameNode -metadataVersion` command output for an HA-style name directory configuration, ensuring it prints both stored image layout version and software format version.

## Important APIs, Types, and Functions
- Configures `DFS_NAMESERVICE_ID`, `DFS_HA_NAMENODES_KEY_PREFIX`, `DFS_HA_NAMENODE_ID_KEY`, and nameservice-scoped `DFS_NAMENODE_NAME_DIR_KEY`.
- Uses `MiniDFSCluster.Builder.manageNameDfsDirs(false)`, `checkExitOnShutdown(false)`, and `NameNode.createNameNode`.
- Captures `System.out` with `ByteArrayOutputStream`.
- Compares against `HdfsServerConstants.NAMENODE_LAYOUT_VERSION`.

## Control Flow
- `initConfig` prepares HA-specific NameNode directory keys and unsets the generic name dir.
- Test builds a small cluster, shuts it down without full cleanup, reinitializes config, redirects stdout, invokes `NameNode.createNameNode("-metadataVersion")`, catches expected `ExitUtil` exception, and asserts expected strings are present.
- `tearDown` shuts down any cluster and sleeps briefly.

## State and Persistence Behavior
- Depends on a formatted NameNode storage directory from the mini-cluster run.
- Reads existing metadata version without starting a normal NameNode service.
- Captures process-style exit behavior via `ExitUtil`.

## Dependencies and Integration Points
- Integrates NameNode command-line parsing/startup, HA name-dir resolution, storage metadata, and stdout output.

## Risks and Edge Cases
- Mutates global `System.out`; finally restores it.
- Sleep in teardown indicates sensitivity to shutdown/port cleanup timing.
- Only verifies output contains version substrings, not full command output or exit code object.

## Test Signals
- Focused regression signal for CLI metadata version reporting against HA-scoped storage configuration.
