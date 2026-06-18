<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShell.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShell.java

## Purpose
`TestDFSShell` is the broad integration regression suite for HDFS-facing `FsShell` and related command behavior. It exercises shell commands against a shared `MiniDFSCluster` with permissions, xattrs, ACLs, snapshots, access-time precision, and small block sizes enabled. It also starts isolated clusters for scenarios that need special topology or configuration, such as corrupt replicas, low replication minimums, trash policy precedence, URI movement, and append-to-EC behavior.

## Important APIs, Types, and Helpers
- `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, and `FsShell` provide the main in-process HDFS command surface.
- Static helpers `writeFile`, `writeByte`, `mkdir`, `rmr`, `createLocalFile`, `createLocalFileWithRandomData`, `createTree`, `runCmd`, `runCount`, `confirmPermissionChange`, and `confirmOwner` keep command setup and assertions reusable.
- `getMaterializedReplicas` and `corrupt` inspect block reports and corrupt materialized replicas for checksum and `-get -ignoreCrc` coverage.
- XAttr constants `raw.a1`, `trusted.a1`, `user.a1` and their byte values are reused by copy-preserve and xattr permission tests.
- `TestGetRunner` abstracts repeated `-get` invocations with different expected exit codes and options.

## Control Flow and Coverage
The class uses `@BeforeAll` to create a two-datanode shared cluster and `@AfterAll` to shut it down. Tests then build filesystem state, invoke shell commands with `shell.run` or `ToolRunner.run`, capture `System.out` or `System.err` when output content matters, and assert both exit codes and filesystem side effects.

Major command groups covered:
- File creation, copying, and deletion: zero-size local/HDFS copy, recursive delete, `-put`, `-copyToLocal`, `-cp`, `-mv`, `-copyFromLocal`, force overwrite, permission-denied local source handling, and URI-qualified paths across multiple clusters.
- Listing and content display: `-ls`, `-lsr`, `-cat`, `-head`, `-tail`, `-tail -f`, `-text` with gzip, deflate, bzip2, sequence files, and plain text.
- Accounting and stats: `-du`, `-du -s`, `-du -x`, `-count`, snapshot-aware count and disk usage, `FileSystem#getUsed`, and `-stat` formatting tokens.
- Permissions and ownership: local and HDFS `-chmod`, sticky bit variants, recursive mode changes, `-chown`, `-chgrp`, owner/group name character handling, and `-test -e/-d/-z/-f/-s/-r/-w`.
- Preservation semantics: `-cp -p`, `-ptop`, `-ptopx`, `-ptopa`, `-ptoa`, directory attribute preservation, ACL preservation, sticky bit preservation, vanilla xattrs, trusted xattrs, and raw xattrs under `/.reserved/raw`.
- Data integrity and append: `-checksum -v`, corrupt-replica `-get` behavior with and without `-ignoreCrc`, `-appendToFile`, invalid append arguments, and `-appendToFile -n` for replicated and EC files.
- Extended attributes: `-setfattr`, `-getfattr`, case sensitivity, permission checks across users, trusted namespace privilege checks, missing xattr errors, and path access failures.
- Trash: client and server `fs.trash.interval` precedence, including disabled default behavior.
- Reserved paths: visibility and rejection behavior for `/.reserved`, raw path restrictions, mkdir/delete/copy/chmod/chown/symlink/snapshot operations on reserved names.

## State and Persistence Behavior
The suite mutates both shared HDFS namespace state and local test files under `TEST_ROOT_DIR`. Most tests create unique top-level directories or append a `counter` suffix; some reuse names and explicitly delete on exit. Snapshot tests persist historical content after live deletions and verify `-du`/`-count` with and without snapshot inclusion. Trash tests verify whether deleted files move under the current trash directory based on server/client configuration. Copy-preserve tests persist metadata and then compare ownership, permissions, ACLs, xattrs, raw xattrs, times, block counts, and replication.

Some tests temporarily replace global streams (`System.out`/`System.err`) and restore them in `finally`; failures before restoration could pollute later tests. Several isolated clusters persist storage while shut down and restarted to validate corrupted replica reads.

## Dependencies and Integration Points
The file integrates with HDFS shell commands, HDFS NameNode/DataNode services, `FSDirectory` reserved-name handling, ACL and xattr subsystems, checksum verification, snapshots, trash, block reports, block replica materialization, EC append policy, and local filesystem copy behavior. It also uses `UserGroupInformation.doAs` to exercise authorization paths and `SubjectInheritingThread` for `-tail -f`.

## Risks and Edge Cases
- Tests depend heavily on wall-clock timestamps, access-time precision, and `Thread.sleep`; timing changes can introduce flakes.
- Shared cluster state means path reuse or missing cleanup can create cross-test coupling.
- Capturing global stdout/stderr is process-wide and unsafe under parallel test execution.
- Reserved path and raw xattr checks are sensitive to path normalization and `/.reserved/raw` detection for relative paths.
- Corruption and restart tests assume replica materialization behavior and platform file-lock behavior.
- Append and EC tests are long-running and topology-sensitive.

## Test Signals
Strong signals include command exit-code assertions, output substring checks, direct filesystem metadata comparisons, corruption readback checks, ACL/xattr equality checks, and verification that failures produce user-facing messages rather than stack traces. The suite is especially useful for catching behavioral regressions in user-visible shell semantics rather than isolated method-level defects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShell.java -->
