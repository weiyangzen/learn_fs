# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testHDFSConf.xml lines 6035-11778

## Purpose

This chunk is a large middle slice of the HDFS CLI golden-output configuration consumed by `org.apache.hadoop.cli.TestHDFSCLI`. It defines XML-driven integration tests for `hdfs dfs`/`FsShell` behavior against a real `MiniDFSCluster`, not unit-test code in Java. The range starts in the tail of `mkdir` coverage and continues through `setrep`, `touchz`, `test`, `stat`, `tail`, `count`, and a large part of `chmod`; it ends before the complete `chmod` matrix for `NAMENODE` paths is finished.

The chunk's main purpose is to pin stable command-line contracts for HDFS path resolution, output formatting, errors, glob expansion, recursive traversal, quota reporting, replication changes, zero-length file creation, metadata reporting, file tailing, namespace counting, and permission mutation. It repeats most behaviors across absolute paths, relative paths under the test user's HDFS home, `hdfs:///` paths, and paths containing the `NAMENODE` placeholder so regressions in URI expansion and displayed path strings are caught.

## Important APIs, Types, and Functions

The XML schema used here is the shared CLI test schema:

- `<test>` groups one scenario with a human-readable `<description>`.
- `<test-commands>` lists ordered shell-style command strings. In this chunk, they are mostly `<command>` entries for `FsShell`; no new Java methods are declared.
- `<cleanup-commands>` removes files and directories created by the test, commonly with `-rm`, `-rm -r`, `-rm -f`, or wildcard cleanup under `/user`, `hdfs:///`, or `NAMENODE/*`.
- `<comparators>` contains one or more expected output checks. This range uses `RegexpComparator`, `TokenComparator`, and `ExactComparator`.
- Placeholders include `NAMENODE`, expanded by `TestHDFSCLI` to the mini cluster's default FS URI; `CLITEST_DATA`, expanded to the test cache data directory; and `USERNAME`, expanded to the local user running the test.

The command surfaces exercised in this chunk are:

- `-mkdir`, including normal creation, multiple-argument creation, duplicate-directory failure, file-vs-directory conflict, missing-parent failure without `-p`, duplicate success with `-p`, and output verification through `-du -s`.
- `-setrep`, including files, directories, legacy `-R`, absolute/relative/URI/default-FS paths, missing paths, too-large replication, zero replication, and non-numeric replication.
- `-touchz`, including zero-length file creation, multiple targets, missing parent behavior, rejection of non-empty existing files, and path display differences.
- `-test`, focused in this range on missing file and directory probes across path forms. Comparators expect the command's boolean false result to produce empty output rather than a text error.
- `-stat`, including file and directory format fields, globbed multiple files, missing-path errors, and `%u/%g` owner/group output for files and directories.
- `-tail`, including file content output, globbed files, missing paths, and directory rejection.
- `-count`, including file/directory counts, wildcard and explicit multi-argument counts, `-q` quota output, storage-type quota setup/clear via `-setSpaceQuota -storageType` and `-clrSpaceQuota -storageType`, human-readable `-h`, and header output with `-v`.
- `-chmod`, including octal and symbolic modes on files and directories, recursive and non-recursive behavior, missing targets, invalid modes, globbed and explicit target lists, and output validation through `-ls`/`-ls -R`.

The Java harness around this XML matters for interpretation. `TestHDFSCLI` sets up a `MiniDFSCluster` with eight DataNodes, sets default replication to `1`, replaces `NAMENODE` in commands and expected output, and executes commands through `CLITestCmdDFS`. `CLITestCmdDFS` delegates normal FS commands to the shared CLI executor and special `dfs-admin-command` entries to `DFSAdmin`; this chunk uses ordinary FS command entries. `FSCmdExecutor` tokenizes each command string, replaces placeholders, runs `ToolRunner.run` on an `FsShell`, and captures both stdout and stderr for comparator matching.

## Control Flow and Execution Model

Each XML `<test>` in this slice executes as an independent scenario:

1. The SAX parser in `CLITestHelper` reads the test description, command list, cleanup command list, and comparator data from `testHDFSConf.xml`.
2. `TestHDFSCLI.setUp()` creates the HDFS mini cluster and configures the default filesystem. Relative paths therefore resolve under `/user/USERNAME` when the user home exists, while `NAMENODE/...` is expanded to the actual cluster URI.
3. The test commands run in order through `FsShell`. Setup operations such as `-mkdir`, `-touchz`, or `-put CLITEST_DATA/data15bytes` create the namespace state needed by the final command under test.
4. The harness captures combined stdout/stderr from all test commands in the scenario.
5. Each comparator is evaluated against the captured output. `RegexpComparator` matches a full line against a regular expression; `TokenComparator` checks token presence in the full output; `ExactComparator` requires the exact output string, used here for a no-output `mkdir -p` success case.
6. Cleanup commands run after the scenario to remove created HDFS state.

The command families have intentionally repetitive control-flow patterns. `mkdir` scenarios create directories, call `-du -s` when success needs proof, and clean with `-rm` or `-rm -r`. `setrep` scenarios first create files or directories with `-touchz`, run `-setrep`, and assert either "Replication 2 set" lines for every affected file or exact validation errors for missing paths and invalid factors. `touchz` scenarios verify zero-byte status through `-du`; when an existing non-empty file is created with `-put`, the command must fail with "Not a zero-length file".

`stat`, `tail`, and `count` tests use a setup-command/final-read-command pattern. `stat` asserts formatted metadata and owner/group fields while tolerating dates and host-specific URI authority with regexes. `tail` writes or copies fixture data, then checks tail output or error text for missing paths and directories. `count` constructs small file/directory trees and checks count columns for directory count, file count, content size, path, and quota values; the `-q`, `-h`, and `-v` variants widen the expected column contract.

The `chmod` portion is the broadest. It builds files and nested directories, applies either octal mode such as `777` or symbolic mode such as `a+rwx`/`a+rw`, then runs `-ls` or `-ls -R` to assert POSIX mode strings. Non-recursive directory tests deliberately show that only the targeted directory changes while child files keep default `-rw-r--r--`. Recursive tests assert that files and nested directories under every targeted path receive the new permissions. Multi-target cases cover both shell glob expansion inside `FsShell` and explicit argument lists.

## State and Persistence Behavior

The XML file itself is static test data, but the scenarios mutate a live HDFS namespace in the `MiniDFSCluster`. The persisted and transient state under test includes:

- Directory inodes created by `-mkdir`, including parent creation through `-p` and error behavior when a parent is absent.
- File inodes and block metadata created by `-touchz` and `-put`. Zero-length files have no content bytes and produce `du`/`count` size zero; fixture files such as `data15bytes` and `data30bytes` exercise non-zero length.
- Replication metadata changed by `-setrep`. The tests assert command output and validation behavior rather than waiting for physical replica placement, which is appropriate because many files are zero-length.
- Permission bits changed by `-chmod`, then observed through directory listings. These permissions are namespace metadata persisted through NameNode edit-log operations in the mini cluster.
- Namespace count and quota state observed by `-count`. Storage-type quota cases set and clear `DISK` quotas and verify quota columns, so they depend on NameNode quota metadata as well as count formatting.
- User and group ownership displayed by `-stat` and `-ls`. Expected outputs substitute `USERNAME` and assume the test cluster's default group string `supergroup`.

Cleanup is part of the state model. Many tests remove `/user`, `hdfs:///user`, `hdfs:///*`, or `NAMENODE/*` to reset shared namespace roots. Because failures can leave partially created state, the cleanup commands are usually broad enough to remove entire test subtrees. A few cleanup commands intentionally use non-recursive `-rm` for files or empty directories; if a scenario changes shape, cleanup may need to be adjusted.

## Dependencies and Integration Points

This chunk integrates these layers:

- `TestHDFSCLI` supplies the cluster, default filesystem URI, replication default, placeholder expansion, and test lifecycle.
- `CLITestHelper` and `CLITestHelperDFS` parse `testHDFSConf.xml`, expand `CLITEST_DATA`/`USERNAME`, dispatch commands, and evaluate comparators.
- `CLITestCmdDFS`, `CommandExecutor`, and `FSCmdExecutor` translate XML command strings into `FsShell` arguments and capture output.
- Hadoop common comparator classes (`RegexpComparator`, `TokenComparator`, `ExactComparator`) define how exact the golden checks are.
- `FsShell` command implementations behind `-mkdir`, `-setrep`, `-touchz`, `-test`, `-stat`, `-tail`, `-count`, and `-chmod` provide the user-visible command behavior.
- HDFS client and NameNode internals provide path qualification, glob expansion, metadata mutation, quota accounting, permission display, owner/group display, and error propagation.
- Fixture data under `CLITEST_DATA`, especially small files like `data15bytes` and larger content used by `tail`, is required for non-empty-file and content-output cases.

The repeated path forms are an important integration point. Absolute paths test normal HDFS namespace roots; relative paths test user-home resolution; `hdfs:///` tests scheme-only URI handling against the default authority; and `NAMENODE/...` tests fully qualified URI handling and output rendering after placeholder substitution.

## Risks and Edge Cases

- This chunk begins and ends inside larger command families. The preceding lines contain earlier `mkdir` tests, and later lines continue `chmod` coverage for `NAMENODE` paths, so a final per-file report must merge adjacent chunks before claiming complete command coverage.
- Comparator strictness is uneven by design. `TokenComparator` tolerates extra output as long as tokens appear, while `RegexpComparator` matches full lines and can be sensitive to punctuation, quoting, authority rendering, and spacing. `ExactComparator` is used where no output is expected.
- Many expected lines encode current CLI wording, including backticks around paths, "No such file or directory", "Is not a directory", "Not a zero-length file", and chmod parser errors. Small user-facing message changes will break these tests even if underlying filesystem behavior is correct.
- URI display is fragile. Some `NAMENODE` expected outputs match `hdfs://\w+[-.a-z0-9]*:[0-9]+/...`, while `hdfs:///` cases expect the scheme-only form to survive in output. Changes to path qualification or error reporting can affect only one path family.
- Relative-path tests depend on user home creation. Many scenarios run `-mkdir -p dir` only to ensure `/user/USERNAME` exists before operating on `file0` or `dir0`; removing those setup commands changes failure modes.
- The `-setrep` tests assert immediate command output, not eventual replication convergence. That makes them stable for zero-length files but does not prove DataNode replica placement.
- The `-touchz` tests distinguish a missing parent from a pre-existing non-empty file. Both cases exercise error text, so changes in `FsShell` exception wrapping can cause regressions.
- `-stat` and `-ls` regexes intentionally abstract timestamps but still depend on default permissions, owner, group, replication, and format-column order.
- `-tail` content checks can be sensitive to fixture contents and newline handling because output is captured through combined stdout/stderr.
- `-count -q` output has wide column formatting and quota sentinel values. Changes in spacing, human-readable units, header labels, or storage-type quota display can break many rows.
- `chmod` recursive tests are high blast-radius because they assert every descendant path. Recursive traversal order is not the main assertion, but every expected line must be present with the correct mode string.
- Cleanup commands sometimes delete broad roots such as `/user` or `hdfs:///*`. These tests assume isolation in a fresh mini cluster and would be unsafe against a shared or non-test filesystem.

## Test Signals

Strong signals in this chunk include:

- `mkdir` proves directory creation across `hdfs:///` and fully qualified `NAMENODE` paths, duplicate-name errors, file conflict errors, missing-parent errors without `-p`, and idempotent success with `-p`.
- `setrep` proves successful replication metadata changes for files and directories across all path forms, recursive directory output per file, legacy `-R` acceptance for files, missing-path diagnostics, and validation for too-large, zero, and non-integer replication factors.
- `touchz` proves zero-length file creation and reporting, multi-target creation, missing parent diagnostics, and rejection of touching an existing non-zero file.
- `test` proves false existence checks on missing files/directories do not emit text in this harness's expected-output contract.
- `stat` proves metadata formatting for file/directory types, globbed paths, missing-path diagnostics, and `%u:%g` owner/group rendering for both files and directories.
- `tail` proves data reads for absolute, relative, `hdfs:///`, and `NAMENODE` paths; globbed tailing; missing-path errors; and directory rejection.
- `count` proves namespace accounting for files, directories, multiple targets, globs, quota columns, storage-type quota set/clear behavior, human-readable formatting, and verbose headers.
- `chmod` proves octal and symbolic permission parsing, file and directory metadata mutation, non-recursive vs recursive semantics, globbed and explicit multi-target behavior, invalid-mode diagnostics, and URI-qualified path handling.

To validate this XML range directly, run the `TestHDFSCLI` test class in the Hadoop build after the resource file is staged into the test cache. The most relevant failure evidence is the harness's detailed report: test description, expanded commands, cleanup commands, comparator type, expected output after placeholder expansion, and actual combined command output.

## Chunk Boundary Notes

Lines 6035-11778 start after the first commands of a `mkdir` test for `hdfs:///dir*`, then cover complete `mkdir` tail scenarios, all `setrep`, `touchz`, `test`, `stat`, `tail`, and `count` scenarios in this part of the file, and most of the `chmod` matrix through the start of `NAMENODE` recursive directory chmod coverage. The subsequent chunk is needed to finish the `chmod` family and any later CLI sections in `testHDFSConf.xml`.
