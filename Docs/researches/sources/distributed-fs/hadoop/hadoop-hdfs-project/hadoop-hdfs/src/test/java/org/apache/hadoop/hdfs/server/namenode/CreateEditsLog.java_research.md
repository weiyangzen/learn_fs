# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/CreateEditsLog.java

## Purpose
`CreateEditsLog` is a test utility executable that synthesizes a NameNode edit log containing many file-create operations. The generated edits can be copied into a NameNode storage directory and paired with simulated DataNode blocks for scale or compatibility testing.

## Important APIs, Types, and Functions
- Constants: `BASE_PATH`, default `EDITS_DIR`, mutable `edits_dir`, and `BLOCK_GENERATION_STAMP`.
- `addFiles(...)` logs a base directory, creates reusable `BlockInfoContiguous` entries, assigns sequential block IDs, logs per-file subdirectories, open-file operations, close-file operations, and periodic `logSync`.
- `usage`, `printUsageExit()`, and `printUsageExit(String)` print CLI help and terminate with `System.exit(-1)`.
- `main(String[])` parses `-f numFiles startingBlockId numBlocksPerFile`, `-l blockSize`, `-r replication`, and `-d editsLogDirectory`, creates `current/`, opens a standalone edit log via `FSImageTestUtil.createStandaloneEditLog`, writes file operations, syncs, and closes.

## Control Flow and Behavior
The CLI validates required arguments, creates the edits directory and `current` subdirectory if needed, disables fsync for testing through `EditLogFileOutputStream.setShouldSkipFsyncForTesting(true)`, and opens an `FSEditLog` for the current layout version. `addFiles` first logs `BASE_PATH`, then for each file assigns a range of block IDs, creates an under-construction inode for `logOpenFile`, logs a completed inode with blocks through `logCloseFile`, creates a new subdirectory every `FileNameGenerator.getFilesPerDirectory()` files, and syncs every 2000 block IDs.

## State and Persistence
This utility writes real edit-log files under `edits_dir/current`. It mutates static `edits_dir`, toggles the static test fsync skip flag, and advances synthetic inode IDs and block IDs. File names encode block ID ranges so multiple non-overlapping generated logs can be combined conceptually. It does not create block files; it only creates namespace edit-log state.

## Dependencies and Integration Points
The utility depends on `FSEditLog`, `EditLogFileOutputStream`, `NameNodeLayoutVersion`, `FSImageTestUtil`, `INodeDirectory`, `INodeFile`, `INodeId`, `BlockInfoContiguous`, `FileNameGenerator`, and HDFS storage constants. It is related to DataNode simulation utilities that inject matching blocks.

## Risks and Edge Cases
- Argument parsing contains a risky condition `args[i].equals("-r") || args[i+1].startsWith("-")`; when `i` is the last index and not `-r`, this can access past the end.
- CLI errors call `System.exit`, making direct unit testing awkward.
- The generated edit log is tightly coupled to internal NameNode layout and inode/block constructors.
- `mkdir()` is used only one level at a time; parent path failures are not recovered.
- Fsync skipping is static and can affect later code in the same JVM if reused.

## Test Signals
There are no JUnit tests in this file. Operational signals are successful process exit, existence of non-empty edit-log files under `current/`, printed file/block counts, and later NameNode startup or edit-log loading with the generated operations.
