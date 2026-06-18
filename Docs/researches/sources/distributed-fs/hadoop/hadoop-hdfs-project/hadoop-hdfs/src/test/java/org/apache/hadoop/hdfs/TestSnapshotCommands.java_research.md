# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSnapshotCommands.java

Purpose: End-to-end coverage for HDFS snapshot-related DFSAdmin, FsShell, and SnapshotDiff command behavior.

Important APIs and types: `DistributedFileSystem.allowSnapshot`, `deleteSnapshot`, `disallowSnapshot`, `getSnapshotDiffReport`, `DFSTestUtil.DFSAdminRun`, `DFSTestUtil.FsShellRun`, `DFSTestUtil.toolRun`, `SnapshotDiff`, `SnapshotDiffReport`, and `DFS_NAMENODE_SNAPSHOT_MAX_LIMIT`.

Control flow: `@BeforeAll` starts one cluster with max snapshots set to 3. `@BeforeEach` recreates `/sub1`, allows snapshots, and creates child dirs. Tests cover idempotent allow/disallow, snapshot creation and duplicate-name errors, max snapshot limit enforcement, reserved `.snapshot` mkdir behavior, snapshot rename success and failure cases, delete-snapshot errors, blocked deletion of snapshottable dirs with snapshots, fully qualified URI paths ignoring bad defaultFS, and snapshot diff output matching API reports. `testSnapshotDiff` creates enough files to force chunked diff generation.

State and persistence behavior: The tests mutate HDFS namespace snapshots under `/sub1`, `/sub3`, `/Fully/QPath`, and `/snap_dir`. `@AfterEach` deletes snapshots before disallowing snapshot and deleting `/sub1`, but some tests perform their own cleanup for other paths.

Dependencies and integration points: Integrates CLI parsing, admin commands, filesystem snapshots, reserved path names, URI-qualified paths, snapshot diff API/tool parity, and chunked diff report backing storage.

Risks and test signals: Cleanup completeness matters because the cluster is shared across tests. Passing signals command-line snapshot workflows produce expected status codes/messages and consistent API-visible snapshot state.
