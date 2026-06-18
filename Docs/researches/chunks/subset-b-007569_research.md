# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testHDFSConf.xml lines 1-6034

## Purpose

This chunk is the opening portion of Hadoop HDFS' XML-driven CLI regression suite. It is consumed by `org.apache.hadoop.cli.TestHDFSCLI`, which creates a `MiniDFSCluster`, substitutes the live NameNode URI for the `NAMENODE` token, runs every `<test>` in `testHDFSConf.xml`, and compares command output against XML-declared comparators.

Lines 1-6034 cover 268 CLI tests. The range starts with the XML header, license, `<configuration>`, `<mode>test</mode>`, and comparator notes, then exercises a broad set of `hadoop fs` filesystem shell behavior: `ls`, `ls -R`, `du`, legacy `dus`, `mv`, `cp`, `rm`, `put`, `copyFromLocal`, `get`, `getmerge`, `cat`, negative `copyToLocal`, `checksum`, and the beginning of `mkdir`. The chunk ends inside the `mkdir: Test for hdfs:// path - creating many directories` test, so that test and later command groups are completed by the next chunk.

The file is not production code, but it is a contract for production CLI behavior. It pins command output formatting, path qualification, glob expansion, recursive traversal, sort order, error text, overwrite behavior, and local/HDFS copy semantics against a real in-process HDFS cluster.

## Important APIs, Types, and Functions

The XML schema used in this range is the CLI test harness schema:

- `<configuration>` wraps suite-wide settings and `<tests>`.
- `<mode>test</mode>` tells the harness to execute commands and compare output. The comment notes `nocompare` as a diagnostic mode that only dumps command output.
- Each `<test>` contains a human-readable `<description>`, a sequence of `<test-commands>`, optional `<cleanup-commands>`, and one or more `<comparators>`.
- `<command>` entries mostly invoke the filesystem shell through `-fs NAMENODE ...`; a few local commands such as `-cat CLITEST_DATA/file` and `rm data` are used after downloads.
- Comparator `<type>` values in this chunk are `RegexpComparator`, `TokenComparator`, `ExactComparator`, and `RegexpAcrossOutputComparator`. `RegexpComparator` dominates because timestamps, user names, hostnames, and port numbers vary across runs.

The main command APIs under test are Hadoop filesystem shell commands rather than Java methods:

- Listing: `-ls`, `-ls -R`, `-ls -r`, `-ls -S`, `-ls -t`, and combinations such as `-ls -S -r`.
- Size/stat: `-du`, `-du -s`, and legacy `-dus`.
- Mutation and copy inside HDFS: `-mv`, `-cp`, `-cp -f`, `-rm`, `-rm -r`, `-touchz`, and `-mkdir`.
- Local-to-HDFS transfer: `-put` and `-copyFromLocal`, including `-f` overwrite cases.
- HDFS-to-local/read transfer: `-get`, `-getmerge`, `-getmerge -nl`, `-cat`, and negative `-copyToLocal`.
- Integrity: `-checksum` on multiple files.

The test harness integration is implemented outside this XML. `TestHDFSCLI` extends `CLITestHelperDFS`, starts an 8-DataNode `MiniDFSCluster`, sets default replication to 1, and records the live default filesystem URI as `namenode`. `expandCommand` replaces `NAMENODE` in XML commands with that URI. `CLITestHelperDFS` uses a DFS-aware parser that recognizes `<dfs-admin-command>` in the full file, while normal `<command>` entries are executed through `CLITestCmd`/`FSCmdExecutor` paths.

## Control Flow and Execution Model

The suite is declarative and sequential. For each `<test>`, the harness runs all `<test-commands>` in order, captures the command output stream, applies every comparator in order, then runs cleanup commands to return HDFS and local scratch state to a known baseline.

Most tests build a small namespace fixture, execute the command under inspection, and clean up that fixture. For example, `ls` tests create files with `-touchz` or directories with `-mkdir`, list them by absolute path, relative path, glob, `hdfs:///` URI, and `NAMENODE/...` URI, then remove the created paths. The recursive `ls -R` tests construct nested directories and files before asserting all expected descendants. Transfer tests stage known local fixtures from `CLITEST_DATA` into HDFS and validate resulting sizes or content.

The chunk deliberately repeats equivalent scenarios across path syntaxes. Many command families have three variants: unqualified absolute/relative HDFS paths, `hdfs:///` scheme-qualified paths, and `NAMENODE/...` paths that are expanded to the real NameNode authority. This ensures the filesystem shell reports paths consistently while still accepting URI-qualified inputs.

Negative tests are first-class control-flow signals. Missing inputs, directory/file mismatches, existing destinations, multiple sources to non-directories, and non-existent target directories are expected to produce stable error messages such as `No such file or directory`, `Is a directory`, `Is not a directory`, or `File exists`. Tests for quoted globbing verify escaped `*` behavior separately from normal glob expansion.

Some tests are marked as tied in descriptions because the second test depends on state from the previous one before cleanup. In this chunk, tied `mv` cases validate both the move result and the source disappearance/destination presence after the earlier command.

## State and Persistence Behavior

The persistent state under test is HDFS namespace metadata and file block/checksum metadata in the `MiniDFSCluster`. Commands mutate directories, zero-byte files, copied data files, block checksums, and local scratch output. The suite relies on cleanup commands such as `-rm -r /user`, `-rm -r hdfs:///*`, `-rm NAMENODE/file*`, and removal of local `CLITEST_DATA/file` outputs to avoid cross-test contamination.

Listing tests assert persisted namespace attributes: permission strings, replication count, owner placeholder `USERNAME`, group `supergroup`, size, timestamp shape, and displayed path. Recursive listing tests persist multi-level trees and assert traversal output. Sorted listing tests persist multiple files with specific names, sizes, or modification order to validate default, reverse, size, and time ordering.

Size tests persist local fixture content in HDFS and assert byte-size accounting. `du` and `dus` cases cover files, directories, globs, and URI-qualified paths. Directory size expectations account for the specific fixture files copied from `CLITEST_DATA`.

Move and copy tests persist both source and destination state. `mv` cases assert that renames and directory moves remove the source path and create the expected destination path. `cp` cases assert that copies preserve the source and create destination files or subtrees, including directory-to-directory and multiple-directory copies.

Transfer tests exercise the boundary between local test resources and HDFS state. `put` and `copyFromLocal` persist local fixture data into HDFS; `getmerge` pulls HDFS files back to a local file and then validates local content with `-cat`. The `cat` tests read persisted HDFS bytes directly and use known fixture content beginning with `12345678901234`.

`checksum` tests assert deterministic HDFS checksum output for four fixture files. The expected algorithm string is `MD5-of-0MD5-of-512CRC32C`, and the tests pin the hash for `data15bytes`, `data30bytes`, `data60bytes`, and `data120bytes`.

## Dependencies and Integration Points

This XML depends on the Hadoop CLI test framework in `hadoop-common` and HDFS-specific extensions in `hadoop-hdfs`:

- `TestHDFSCLI` supplies the HDFS cluster, NameNode URI substitution, replication setting, rack/host topology setup for the broader file, and JUnit entrypoint.
- `CLITestHelper` and `CLITestHelperDFS` parse the XML, construct command/comparator objects, expand variables such as `USERNAME`, `NAMENODE`, and `CLITEST_DATA`, execute commands, and run cleanup.
- `CLITestCmdDFS`, `FSCmdExecutor`, and the standard filesystem shell route XML command strings to the same command implementations users invoke from the shell.
- `MiniDFSCluster` and `DistributedFileSystem` provide a real NameNode/DataNode environment rather than a mocked filesystem.
- Local fixture files under `CLITEST_DATA`, especially `data15bytes`, `data30bytes`, `data60bytes`, and `data120bytes`, provide deterministic sizes, contents, and checksums.

The test content integrates with production command behavior in `FsShell` and HDFS clients. It covers `Path` parsing, working-directory handling for relative paths, glob expansion, URI qualification, error reporting, overwrite checks, recursive traversal, deletion semantics, local filesystem interop, and checksum formatting.

## Risks and Edge Cases

- Output formatting is brittle by design. Permission bits, replication, owner/group placeholders, timestamp format, path qualification, and error prefixes are all asserted textually. Any production change to CLI output may require careful test migration.
- The suite relies heavily on cleanup. A failed cleanup can leave `/user`, root-level files, `hdfs:///*`, or local `CLITEST_DATA/file` artifacts that affect later tests.
- Glob behavior is a major risk area. Normal globs, quoted/escaped globs, whitespace-containing paths, and `NAMENODE` URI globs are all covered because shell parsing and Hadoop `PathData` expansion can differ subtly.
- Relative paths depend on the test user's HDFS home directory. Many cleanup commands remove `/user`, so changes to working-directory creation or home-directory behavior can break unrelated-looking relative-path cases.
- Several cleanup commands in this chunk contain apparent typos or malformed XML-adjacent text, such as `NAMNEODE` in some `cp` cleanups and stray colons after `</cleanup-commands>`. The current parser/test flow evidently tolerates the file, but these are hazards when editing or splitting tests.
- Legacy `dus` coverage remains in this chunk. If the command is removed or fully aliased to `du -s`, expected output and command availability need coordinated updates.
- The tests assert specific checksum algorithm labels and hash values. Changes to default checksum type, bytes-per-checksum, fixture content, or output escaping will break these assertions.
- The line-range boundary is in the middle of a `mkdir` test at line 6034. Research and reconciliation must treat this chunk as partial for `mkdir`; the following chunk owns the remainder of that test and later command groups.

## Test Signals

Strong pass signals from this chunk include:

- `ls` correctly handles files, directories, recursive output, sorted output, absolute and relative paths, `hdfs:///` paths, NameNode-qualified paths, whitespace in names, missing paths, and escaped glob patterns.
- `du` and `dus` report expected file and directory byte totals for single paths, globs, recursive directory fixtures, and URI-qualified inputs.
- `mv` and `cp` preserve the intended source/destination semantics across file-to-file, file-to-directory, directory-to-directory, multiple-source, globbed, overwrite, missing-source, and bad-destination cases.
- `rm` and `rm -r` distinguish files from directories, handle globbed deletions, report missing paths correctly, and work across normal, `hdfs:///`, and NameNode-qualified paths.
- `put` and `copyFromLocal` correctly upload local fixture files, reject missing local inputs, reject multiple sources to files or missing directories, and honor `-f` overwrites.
- `get` negative cases and `getmerge` positive cases validate HDFS-to-local transfer error handling, concatenation order, and optional newline insertion.
- `cat` returns fixture content for files and multiple-file inputs while rejecting missing files and directories with stable error text.
- `copyToLocal` missing-source cases consistently report `No such file or directory`.
- `checksum` emits the expected CRC32C/MD5 checksum lines for all four fixture files.
- Initial `mkdir` tests validate directory creation, multi-directory creation, existing-directory errors, file-vs-directory errors, and the start of `hdfs:///` mkdir coverage.

## Chunk Boundary Notes

Lines 1-6034 start at the beginning of `testHDFSConf.xml` and include complete sections for `ls`, `ls -R`, `du`, `dus`, `mv`, `cp`, `rm`, `put`, `copyFromLocal`, `get`, `getmerge`, `cat`, negative `copyToLocal`, `checksum`, and the beginning of `mkdir`. The final visible line is the first command of `mkdir: Test for hdfs:// path - creating many directories`, so downstream merge work should combine this with the next chunk before drawing complete conclusions about `mkdir` and all later tests in the XML file.
