# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testHDFSConf.xml lines 11779-17057

## Scope And Purpose

This chunk is a large middle-to-late section of Hadoop HDFS's XML-driven command-line test fixture. It does not define Java implementation classes directly; instead it declares executable CLI scenarios consumed by the HDFS CLI test harness. The visible tests exercise `FsShell` commands through `<command>` entries and `DFSAdmin` commands through `<dfs-admin-command>` entries against a MiniDFSCluster-style `NAMENODE` placeholder, with expected output checked by comparator declarations.

The chunk starts inside a `chmod` test's comparator block, continues through extensive `chmod`, `chown`, and `chgrp` coverage, then shifts into `dfsadmin -help`, quota error handling, service ACL refresh, safemode, report, namespace/edit-log administration, node refresh, metasave, topology reporting, newer file-system shell operations, snapshots, group mapping refresh, quota commands, and the beginning of `setBalancerBandwidth`. The final per-file synthesis should treat this as a declarative specification for CLI-facing HDFS semantics rather than as runtime business logic.

## Test Harness Shape

Each `<test>` block follows the same contract:

- `<description>` names the user-visible behavior under test.
- `<test-commands>` lists ordered shell invocations, using `-fs NAMENODE` to bind the command to the test NameNode.
- `<cleanup-commands>` removes created files or directories, resets safemode, or intentionally leaves no cleanup where the command is read-only or cluster-wide.
- `<comparators>` defines expected output fragments with `RegexpComparator`, `TokenComparator`, `SubstringComparator`, `ExactComparator`, or `RegexpAcrossOutputComparator`.

The file relies on fixture substitutions such as `NAMENODE`, `USERNAME`, and `CLITEST_DATA`. Most `ls` expectations use regexes for dates, times, hostnames, ports, and byte counts so the tests are stable across cluster instances. Empty-output success paths are explicitly represented by `ExactComparator` with an empty `<expected-output>`.

## Permission And Ownership Commands

### `chmod`

The opening portion continues `chmod` coverage for NameNode-qualified paths. It verifies octal and symbolic modes, direct and recursive operation, glob expansion, multiple explicit operands, non-existent paths, and invalid mode parsing.

The key command forms are:

- `-chmod 777`, `-chmod a+rw`, and `-chmod a+rwx` on files and directories.
- Recursive variants such as `-chmod -R 777` and `-chmod -R a+rwx`.
- Globs like `NAMENODE/file*` and `NAMENODE/dir*`.
- Multiple explicit operands such as `NAMENODE/file1 NAMENODE/file2 ...`.

Expected signals are `-ls` or `-ls -R` rows whose permission bits change only on the targeted paths unless recursion is requested. Directory children remain at default permissions when only the parent directory is changed. Error coverage includes missing files with `No such file or directory`, invalid octal value `999`, and invalid symbolic string `rdef`.

### `chown`

The chunk contains a broad `chown` matrix over path syntaxes:

- URI-style `hdfs:///...` paths.
- Absolute paths such as `/file1` and `/dir0`.
- Relative paths such as `file1` and `dir0`.
- NameNode placeholder paths such as `NAMENODE/file1`.

For each path family the fixture covers files, directories, recursive directory changes, non-existent targets, globbed multiple targets, explicit multiple operands, and invalid owner or group values. The normal mutation uses `newowner:newgroup` and verifies that `-ls` output reflects `newowner` and `newgroup` on the intended inode set. Recursive variants update children under the selected directory, while non-recursive directory tests leave descendants owned by the default `USERNAME supergroup`.

Invalid parsing is tested with values containing `%`, for example `%:newgroup` and `newowner:%`, and the expected output names the failed pattern for owner or group. These tests are high-signal for command-line validation before any NameNode metadata mutation is attempted.

### `chgrp`

The `chgrp` tests mirror the `chown` structure for group-only changes. They cover absolute, relative, `hdfs:///`, and `NAMENODE` paths; file and directory targets; recursive and non-recursive directory operations; globbed and explicit multiple operands; non-existent targets; and invalid group names. The normal mutation uses `newgroup` and verifies `-ls` output while preserving the original owner (`USERNAME`).

The important distinction from `chown` is that only the group field changes. The recursive tests prove group metadata is propagated down nested files and directories only when `-R` is present. The invalid group case `-chgrp % ...` expects a parser-level error rather than a filesystem-side failure.

## DFSAdmin Help And Quota Diagnostics

The next section validates `dfsadmin -help` output for:

- `report`
- `safemode`
- `refreshNodes`
- `finalizeUpgrade`
- `metasave`
- `setQuota`
- `clrQuota`
- `setSpaceQuota`
- `clrSpaceQuota`
- `refreshServiceAcl`
- `help`

These tests are not just cosmetic. They lock down command syntax, option names, and operator-facing documentation for storage-type quotas, safemode semantics, host include/exclude refresh, upgrade finalization, and metasave contents. Regex comparators intentionally allow spacing variation but require key phrases and option forms, including `-storageType <storagetype>` and available storage types `DISK`, `SSD`, `ARCHIVE`, and `PROVIDED`.

Quota diagnostics then exercise negative and boundary cases:

- `-setQuota` on a file returns "Is not a directory".
- `-setSpaceQuota` on a missing directory returns a directory-not-found message.
- Exceeding a namespace quota by creating another entry under `/test` reports the namespace quota breach.
- `-setQuota 0` is rejected as an invalid quota value.
- `-setSpaceQuota a5` is rejected as an invalid quota string.
- `-clrQuota` on a missing path reports a missing directory.
- Globbed `-setSpaceQuota 1k /dir*` and `-setQuota 1 /dir*` apply limits to several directories, then subsequent `put` or `mkdir` operations prove the limits are enforced.

One detail matters for state management: several quota error tests intentionally reuse `/test` across adjacent tests, with comments in cleanup sections stating that the same directory is carried forward. This makes ordering relevant in this part of the fixture.

## DFSAdmin Operational Commands

### Service ACL Refresh

`-refreshServiceAcl` is tested for the success path with output `Refresh service acl successful`. A denied-user variant using `-Dhadoop.job.ugi=blah,blah` is present but commented out inside XML comments. The final report should preserve that it is fixture context only, not an active test in this chunk.

### Safemode

The safemode tests cover:

- `-safemode enter` when safemode is off.
- Re-entering safemode when it is already on.
- `-safemode forceExit`.
- `-safemode leave` from both on and off states.
- `-safemode get` from both off and on states.
- `-safemode wait` when off.
- `-safemode wait &` while on, followed by `leave` to release the wait.

Expected outputs are token checks for `Safe mode is ON` or `Safe mode is OFF`. Cleanup commonly leaves safemode off, which is important because later tests perform metadata mutations and namespace saves.

### Cluster Reports And Node Operations

`-report` validates the operator report format: configured capacity, present capacity, DFS remaining and used, DFS used percentage, live datanode count, datanode name and hostname, decommission status, non-DFS used, remaining percentage, last contact timestamp, and block counts. `-refreshNodes` is followed by another `-report`, proving the include/exclude refresh command returns the cluster to a reportable state.

`-printTopology` expects a specific rack topology across `/rack1` through `/rack4`, with localhost datanodes in service. The XML comment notes that the MiniDFSCluster launched by `CLITestHelper` is configured to match this output. This is a tight integration point with the test harness's datanode topology setup.

### Namespace, Edit Log, Metasave, And Balancer Controls

`-saveNamespace` is tested in two modes: it succeeds only after `-safemode enter`, and it returns a safe-mode-required message when safemode is off. `-rollEdits` expects a new edit-log segment txid. `-metasave metafile` expects creation of a metasave file in the NameNode log directory.

The chunk also includes `-setBalancerBandwidth 104857600` at the end, but the line range stops inside that test before its comparator is complete. Research for this chunk can identify the command under test, but the expected output must be completed by the next chunk.

## File System Shell Operations

After the DFSAdmin block, the fixture tests several `FsShell` data and directory operations under `/user/USERNAME/dir1`:

- `appendToFile` creates an empty file, appends `CLITEST_DATA/data15bytes`, then reads it with `-cat` and expects the fixture content prefix `12345678901234`.
- `text` uploads the same data with `-put` and reads it through `-text`.
- `rmdir` removes an empty directory and expects a subsequent parent listing to be empty.
- `rmdir --ignore-fail-on-non-empty` attempts to remove a non-empty directory, suppresses the failure, and verifies the directory still exists.
- `df` checks that the filesystem usage header is printed.
- `expunge` expects empty output.

These tests validate command behavior against HDFS rather than local filesystem semantics, including HDFS path qualification, trash expunge behavior, and directory removal rules.

## Snapshot Commands

Snapshot coverage uses `/user/USERNAME/dir1` as the snapshot root and combines `DFSAdmin` snapshot allowance with `FsShell` snapshot lifecycle commands:

- `-allowSnapshot` succeeds on the directory.
- `-disallowSnapshot` succeeds after allow.
- `-createSnapshot /user/USERNAME/dir1 snapshot1` returns the `.snapshot/snapshot1` path.
- `-renameSnapshot ... snapshot1 snapshot2` is followed by `-ls` of `.snapshot` and expects the renamed snapshot directory.
- `-deleteSnapshot ... snapshot1` is followed by `-ls` of `.snapshot` and expects empty output.

Cleanup disallows snapshots where needed and removes `/user/USERNAME`. These tests are important because snapshot state is NameNode metadata, not ordinary files; failure to clean it can block directory deletion or affect later tests.

## Group Mapping And Quota Success Paths

The final complete DFSAdmin tests in the chunk validate:

- `-refreshUserToGroupsMappings`
- `-refreshSuperUserGroupsConfiguration`
- `-setQuota 3 /user/USERNAME/dir1` followed by `-count -q` showing quota `3`
- `-clrQuota` followed by `-count -q` showing `none`
- `-setSpaceQuota 1G` returning no output

These complement the earlier negative quota tests by checking the normal administrative path and observable `count -q` state.

## State And Persistence Behavior

Most tests create ephemeral paths and remove them in cleanup, but the state being changed is real HDFS NameNode metadata in the test cluster:

- Permission bits, owner, and group are persisted on inodes and observed through `-ls` output.
- Recursive metadata changes mutate directory descendants; non-recursive changes intentionally leave children untouched.
- Quotas persist on directories and are later observed through namespace or disk-space quota enforcement.
- Safemode is global NameNode state and is explicitly reset to off after tests that turn it on.
- `saveNamespace` persists the namespace image and is intentionally gated by safemode.
- `rollEdits` changes edit-log segment state and returns the starting transaction id for the new segment.
- Snapshot allow/disallow and snapshot create/rename/delete mutate NameNode snapshot metadata under `.snapshot`.
- `refreshNodes`, group mapping refresh, superuser group refresh, service ACL refresh, and balancer bandwidth are cluster-wide administrative changes.
- `metasave` writes a file under the NameNode log directory, and this test intentionally does not clean it up.

The quota error tests around `/test` deliberately share state across adjacent tests. That makes this part of `testHDFSConf.xml` less isolated than the repeated create-cleanup patterns in the permission tests.

## Dependencies And Integration Points

This chunk depends on the Hadoop CLI test framework that parses `testHDFSConf.xml` and dispatches XML elements to command implementations. The main runtime integration points are:

- `FsShell` commands such as `mkdir`, `touchz`, `chmod`, `chown`, `chgrp`, `ls`, `rm`, `put`, `cat`, `text`, `appendToFile`, `rmdir`, `df`, `expunge`, `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- `DFSAdmin` commands such as `help`, `setQuota`, `clrQuota`, `setSpaceQuota`, `clrSpaceQuota`, `refreshServiceAcl`, `safemode`, `report`, `saveNamespace`, `rollEdits`, `refreshNodes`, `metasave`, `printTopology`, `allowSnapshot`, `disallowSnapshot`, group mapping refreshes, and `setBalancerBandwidth`.
- The MiniDFSCluster and `CLITestHelper` setup, including NameNode URI substitution, username substitution, test data files, rack topology, live datanodes, and default owner/group values.
- HDFS NameNode internals for permissions, ownership, quotas, safemode, snapshots, namespace image saving, edit-log rolling, datanode reports, host refresh, and topology reporting.
- Output comparator classes, including line-local regex/token comparators and `RegexpAcrossOutputComparator` for multi-line topology output.

## Risks And Edge Cases Captured

This fixture protects several CLI-facing compatibility risks:

- Parser regressions in symbolic/octal modes, owner/group syntax, glob expansion, relative versus absolute paths, URI paths, and `NAMENODE` placeholder paths.
- Accidental recursive metadata mutation when `-R` is absent, or missing recursive propagation when `-R` is present.
- Incorrect `ls` formatting for permissions, owner/group fields, replication columns, dates, and URI/path rendering.
- Missing or changed operator help text for DFSAdmin commands.
- Quota validation regressions, including invalid numbers, invalid units, file-versus-directory handling, globbed quota application, and enforcement error text.
- Safemode state leakage that would break later mutating tests or make `saveNamespace` assertions unreliable.
- Cluster report format drift, especially datanode capacity and liveness fields used by operators and scripts.
- Topology output drift from MiniDFSCluster rack setup or `printTopology` formatting.
- Snapshot lifecycle bugs where allow/disallow state or renamed/deleted snapshots remain visible.
- State leakage from intentionally shared `/test` quota tests and no-cleanup admin commands like `metasave` and `rollEdits`.

## Test Signals

The strongest pass/fail signals in this chunk are output comparisons after commands that mutate HDFS state:

- `-ls` and `-ls -R` regex rows prove permission, owner, and group metadata changed on exactly the expected paths.
- Missing-path and invalid-syntax commands prove CLI validation and NameNode error propagation through exact error text.
- Empty `ExactComparator` entries prove successful quiet commands such as `setSpaceQuota`, `expunge`, and quota clear in selected scenarios.
- `-count -q` proves quota state after `setQuota` and `clrQuota`.
- Subsequent `put` and `mkdir` failures prove disk-space and namespace quota enforcement.
- Safemode token checks prove global state transitions.
- `report` and `refreshNodes` comparators prove datanode report fields and liveness output.
- `saveNamespace`, `rollEdits`, and `metasave` regexes prove administrative side effects reached the NameNode.
- Snapshot `ls` and command-message checks prove snapshot metadata visibility and cleanup.

Because the source is XML test data, code changes elsewhere may break this chunk by changing command output strings, formatting, or validation order even when core HDFS state transitions still succeed. Any implementation change touching these commands should run the CLI test harness that consumes `testHDFSConf.xml`, not just unit tests around the underlying Java APIs.
