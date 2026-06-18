# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testHDFSConf.xml lines 17058-17661

## Scope

This chunk is the final section of the HDFS CLI XML test configuration consumed by `org.apache.hadoop.cli.TestHDFSCLI`. It starts at the expected output for the previous `-setBalancerBandwidth` case, then covers `dfsadmin -finalizeUpgrade`, negative `-moveFromLocal` destination/source handling, safemode rejection for mutating permission/quota operations, `-find` traversal and matching behavior, and two `-truncate -w` scenarios. The range ends by closing the `<tests>` and `<configuration>` elements for `testHDFSConf.xml`.

`TestHDFSCLI` runs these tests against a `MiniDFSCluster` with eight datanodes and replication forced to 1. `NAMENODE` is expanded to the cluster URI, `USERNAME` to the current process user, and `CLITEST_DATA` to the test-resource data directory. Normal `<command>` elements execute through the filesystem shell, while `<dfs-admin-command>` elements are recognized by `CLITestHelperDFS` and routed through `DFSAdmin`.

## Purpose

The chunk protects command-line compatibility at the HDFS integration boundary. It records exact user-visible messages for administrative operations and shell commands, verifies URI normalization for HDFS destinations, confirms that safemode blocks namespace metadata mutations, checks deterministic `find` output ordering and expression behavior, and verifies that HDFS truncation waits for block recovery before subsequent reads.

The `finalizeUpgrade` test asserts that `hdfs dfsadmin -finalizeUpgrade` reaches `DFSAdmin.finalizeUpgrade()` and prints `Finalize upgrade successful` for the non-HA mini-cluster path.

The `moveFromLocal` tests focus on failure semantics rather than successful moves. They cover missing local sources, multiple-source moves into an existing file, multiple-source moves into a missing destination directory, and three destination spellings: plain HDFS paths, `hdfs:///...` paths, and explicit `NAMENODE/...` URI paths. These tests keep the shell's diagnostic prefix and rendered destination string stable.

The safemode tests verify that `-chmod`, `-chown`, `-chgrp`, `-setQuota`, `-clrQuota`, `-setSpaceQuota`, and `-clrSpaceQuota` cannot mutate HDFS while the NameNode is in safemode. Each case creates `/test` or `/test/file1`, enters safemode via dfsadmin, executes the mutating command, then leaves safemode during cleanup so later cases can proceed.

The `find` tests build a small directory tree under `/findtest` or relative `findtest`, with a mix of directories and files copied from `data60bytes`, `data120bytes`, and `data1k`. They assert default expression behavior, explicit `-print`, relative-path output, current-working-directory output when no path is supplied, `-name item*a`, and case-insensitive `-iname ITEM*a`.

The final `truncate` tests exercise `-truncate -w`: truncating a 120-byte file to 5 bytes and reading back `12345`, and attempting to truncate a 15-byte file to 50 bytes while verifying the file content remains the original `data15bytes` prefix expected by the comparator.

## Important APIs, Commands, and Types

`TestHDFSCLI` is the top-level JUnit harness. It initializes `MiniDFSCluster`, records the default HDFS URI as `namenode`, expands placeholders, and delegates command execution to each parsed `CLICommand`.

`CLITestHelperDFS.TestConfigFileParserDFS` extends the generic CLI XML parser by treating `dfs-admin-command` as a `CLITestCmdDFS` backed by `CLICommandDFSAdmin`. This distinction matters in this chunk because `-finalizeUpgrade`, `-safemode`, and quota commands are `DFSAdmin` operations, not ordinary `FsShell` commands.

`DFSAdmin.finalizeUpgrade()` obtains a `DistributedFileSystem`, handles HA logical URIs by iterating all NameNodes, and in the non-HA path calls `dfs.finalizeUpgrade()` before printing `Finalize upgrade successful`.

`DFSAdmin.setSafeMode(...)` maps `enter`, `leave`, `get`, `wait`, and `forceExit` arguments to `HdfsConstants.SafeModeAction` values and prints the resulting safemode state. The XML uses `enter` before each prohibited mutation and `leave` in cleanup.

`DFSAdmin.SetQuotaCommand`, `ClearQuotaCommand`, `SetSpaceQuotaCommand`, and `ClearSpaceQuotaCommand` are `DFSAdminCommand` subclasses. They parse path arguments with `CommandFormat`, resolve each `PathData` to a `DistributedFileSystem`, and call `setQuota(...)` or `setQuotaByStorageType(...)` with `HdfsConstants.QUOTA_DONT_SET` and `HdfsConstants.QUOTA_RESET` sentinels as appropriate.

`MoveCommands.MoveFromLocal` is registered as `-moveFromLocal`. It extends `CopyCommands.CopyFromLocal`, rejects the unimplemented `-t` option, avoids merging existing directories during move-specific path processing, and deletes each source in `postProcessPath` only after a copy succeeds. The tests in this chunk rely on copy-path validation failing before deletion for missing sources and invalid destinations.

`FsShellPermissions.Chmod`, `Chown`, and `Chgrp` implement `-chmod`, `-chown`, and `-chgrp`. They parse mode or owner/group options and eventually call `FileSystem.setPermission(...)` or `FileSystem.setOwner(...)`, which route to HDFS NameNode RPCs in these tests.

`Find` is the `-find` implementation under `org.apache.hadoop.fs.shell.find`. It registers the `And`, `Print`, and `Name` expressions; defaults to the current directory when no path is supplied; defaults to `-print` when no expression is supplied; injects `-print` when an expression has no explicit action; and recursively applies the root expression to each `PathData`.

`Truncate` is the `-truncate` filesystem shell command. It parses `[-w] <length> <path> ...`, rejects negative sizes and directories, calls `FileSystem.truncate`, records paths needing recovery when `truncate` returns false, and waits until each file status length reaches the target length when `-w` is present. It also rejects requests to truncate to a larger length than the current file size.

`FSNamesystem` is the NameNode implementation behind the visible safemode failures. `setPermission`, `setOwner`, and `setQuota` all call `checkNameNodeSafeMode(...)` while holding write locks before editing namespace metadata; their message prefixes become the expected XML output. `finalizeUpgrade` checks superuser privileges, coordinates with checkpoint locking, and calls `FSImage.finalizeUpgrade(...)`.

## Control Flow

For each `<test>`, the CLI harness runs the listed setup/test commands in order, captures stdout/stderr, runs cleanup commands, then evaluates the configured comparator list. `TokenComparator` stabilizes tokenized diagnostic output, `SubstringComparator` accepts any captured output containing the required message, `RegexpComparator` matches regular expressions, and `RegexpAcrossOutputComparator` is used when exact multi-line command output must be matched as one stream.

The `finalizeUpgrade` flow is direct: XML command -> `CLICommandDFSAdmin` -> `DFSAdmin.finalizeUpgrade()` -> `DistributedFileSystem.finalizeUpgrade()` -> NameNode `FSNamesystem.finalizeUpgrade()` -> success text. Because the test cluster is not configured through an HA logical URI, the expected text is the single-NameNode message rather than the per-address HA variant.

The `moveFromLocal` flow first creates local-ish test inputs using shell `-cp CLITEST_DATA/... data...` where needed, then calls `-moveFromLocal` with one or more sources and a destination. Multi-source cases depend on the copy command's destination validation: the destination must be an existing directory, so an existing file produces `Is not a directory` and a missing final directory produces `No such file or directory`. The explicit `NAMENODE/...` cases show that diagnostics render the fully qualified `hdfs://host:port/...` URI after path resolution.

The safemode flow deliberately performs a successful namespace write before entering safemode, then a prohibited write while safemode is on. Permission operations reach `FSNamesystem.setPermission` or `setOwner`, which fail with `Cannot set permission for /test/file1. Name node is in safe mode.` or `Cannot set owner for /test/file1. Name node is in safe mode.` Quota operations reach `FSNamesystem.setQuota`, whose operation name is reflected by dfsadmin as `setQuota`, `clrQuota`, `setSpaceQuota`, or `clrSpaceQuota` before the common `Cannot set quota on /test. Name node is in safe mode.` body.

The `find` flow parses initial path operands until the first expression token beginning with `-`. If no path remains, it searches `.`. If no expression remains, `parseExpression` returns `Print`; if a matcher such as `-name` or `-iname` is supplied without an action, `processOptions` builds an `And` expression combining `Print` with the matcher. Recursive traversal visits the root path before descendants, and the expected outputs assert that child listing order is deterministic for this test tree.

The `truncate` flow with `-w` calls `FileSystem.truncate` and either prints success immediately or waits for block recovery until `PathData.refreshStatus()` reports the requested length. The first case then reads the file to prove data was shortened to five bytes. The second case tries to enlarge a file; `Truncate.processPath` rejects this before calling HDFS truncate, and the following `-cat` proves the original file content is still present.

## State and Persistence Behavior

The XML itself does not persist production state, but the tests create and remove HDFS namespace entries. The main temporary roots are `/user/USERNAME`, `/test`, `/findtest`, `/donotfind`, relative `donotfind`, and relative `findtest`. Cleanup commands remove these roots to keep later tests independent.

`-finalizeUpgrade` is a persistent administrative operation in a real cluster: it finalizes storage upgrade state through the NameNode image. In this mini-cluster test it mainly validates the CLI/RPC success path and message, but the command is still stateful and requires superuser privilege.

`moveFromLocal` is stateful in two filesystems: it copies from local filesystem paths into HDFS and then removes the local source after successful copy. The negative cases in this chunk are important because a failed copy/destination validation must not delete sources.

Safemode is cluster-global NameNode state. Each safemode test enters it and must leave it in cleanup, otherwise subsequent tests would fail unexpectedly. Permission and quota operations would normally write edit-log records, but these cases are expected to fail before namespace mutation and edit-log sync.

`find` creates no new state after setup; it reads directory listings and file status metadata. Its output depends on path spelling, current working directory handling, expression parsing, recursion depth, and directory listing order.

`truncate` mutates block and inode length state when the requested length is valid. With `-w`, command completion is coupled to block recovery visibility. The failed enlargement case should leave the file unchanged and must not emit a misleading successful truncate.

## Dependencies and Integration Points

These tests integrate the XML CLI framework, `FsShell`, `DFSAdmin`, `MiniDFSCluster`, HDFS RPCs, `DistributedFileSystem`, NameNode safemode and quota code, shell path resolution through `PathData`, and comparator classes from the generic Hadoop CLI test framework.

The test data files `data15bytes`, `data30bytes`, `data60bytes`, `data120bytes`, and `data1k` under HDFS test resources are part of the contract. Their contents and sizes drive the copy, find, and truncate assertions.

The destination path variants exercise URI handling across plain absolute HDFS paths, scheme-only `hdfs:///...` paths, and fully expanded `NAMENODE/...` paths. This crosses `Path`, `FileSystem` resolution, shell display formatting, and HDFS default-URI behavior.

Safemode rejection messages depend on the integration between `FsShellPermissions`, `DFSAdmin` quota commands, HDFS client RPCs, `NameNodeRpcServer`, `FSNamesystem.checkNameNodeSafeMode`, and the command-layer exception formatting that prefixes messages with the invoked shell command.

`find` depends on the expression factory under `org.apache.hadoop.fs.shell.find`, recursive `FsCommand` traversal, `PathData` status refresh, and output streams supplied by the shell command context.

## Risks and Compatibility Notes

Many assertions in this chunk are intentionally user-facing and brittle. Changing command prefixes, quote style, URI rendering, capitalization, or safemode exception wording can break these tests even when the underlying operation still fails correctly.

The `moveFromLocal` tests are sensitive to whether setup paths are local or HDFS-resolved by the shell. Reworking `CopyFromLocal`, destination validation, or post-copy source deletion can introduce data-loss regressions if failures begin deleting sources or if multi-source destinations are no longer checked before copy.

The `NAMENODE` destination tests use a regular expression for host and port because the mini-cluster endpoint is dynamic. Any change in URI canonicalization, host formatting, IPv6 rendering, or default-port display can require comparator updates.

Safemode cleanup is critical. If a test fails before cleanup or if `-safemode leave` behavior changes, later tests may see unrelated failures. These cases also assume the NameNode rejects chmod/chown/chgrp/quota changes before editing metadata; moving the safemode check later would risk partial state changes.

The `find` expected output encodes preorder traversal and sorted child order for the constructed tree. Changes to listing sort order, default action injection, relative path rendering, or expression matching semantics for `-name` and `-iname` will be visible.

The second truncate test documents that enlarge requests are rejected and data remains unchanged. If the command changes to allow sparse extension or zero-fill extension, this test's expected behavior would need intentional migration.

Because the chunk ends the XML document, malformed edits here can invalidate the entire `testHDFSConf.xml` suite. The empty cleanup command in the `finalizeUpgrade` case is also part of the parsed structure and should be preserved unless the harness behavior is changed deliberately.

## Test Signals

The direct signal for this chunk is `TestHDFSCLI.testAll`, which loads `testHDFSConf.xml`, expands placeholders, and executes every listed CLI case against a live `MiniDFSCluster`.

Expected comparator signals in this range include:

- `Finalize upgrade successful` for `dfsadmin -finalizeUpgrade`.
- `moveFromLocal: ... No such file or directory` for missing sources or missing multi-source destination directories.
- `moveFromLocal: ... Is not a directory` for multi-source moves targeting an existing file.
- Safemode rejection substrings for permission, owner, and quota mutations.
- Exact multi-line `find` output for absolute paths, relative paths, current directory defaulting, `-name`, and `-iname`.
- `12345` after truncating `data120bytes` to 5 bytes with `-w`.
- The original `data15bytes` content prefix after a rejected truncate-to-larger-size request.

Useful adjacent validation would include focused unit tests for `MoveFromLocal` source deletion on failure, `Find` expression parsing/default action behavior, and `Truncate` enlargement rejection, but this XML chunk is specifically an integration-level CLI contract test.
