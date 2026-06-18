# subset-b-007384 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/libwinutils.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/libwinutils.c

Purpose: shared Windows support library for Hadoop `winutils`, covering long-path normalization, file metadata, POSIX-like ACL/mode translation, account/SID lookup, LSA S4U logon helpers, job-object naming/termination, service/RPC security descriptors, token/profile handling, debug/error reporting, and MIDL allocation hooks.

Important APIs/types/functions: `GetFileInformationByName`, `ConvertToLongPath`, `DirectoryCheck`, `SymbolicLinkCheck`, `JunctionPointCheck`, `FindFileOwnerAndPermission`, `ChangeFileModeByMask`, `CreateDirectoryWithMode`, `CreateFileWithMode`, `GetSidFromAcctNameW`, `GetAccntNameFromSid`, `GetLocalGroupsForUser`, `EnablePrivilege`, `RegisterWithLsa`, `CreateLogonTokenForUser`, `LoadUserProfileForLogon`, `ChangeFileOwnerBySid`, `GetSecureJobObjectName`, `KillTask`, `ChownImpl`, `SplitStringIgnoreSpaceW`, `BuildServiceSecurityDescriptor`, `MIDL_user_allocate`, and `MIDL_user_free`. The global `WinMasks` table maps Hadoop's Unix mode bits to Windows access masks.

Control flow: most helpers follow a two-pass Windows API pattern for size discovery, allocation, then retrieval. Permission reads obtain owner/group/DACL security info, use AuthZ access checks for owner/group/world SIDs, then synthesize Unix mode bits. Permission writes convert Unix masks into ordered allow/deny ACEs, build DACLs, attach them to absolute or self-relative security descriptors, and persist through `SetFileSecurity`. Logon helpers register with LSA, resolve Kerberos auth package IDs, issue S4U logons, and manage user profiles.

State and persistence: this file mutates NTFS DACLs/owner/group fields, creates files/directories with explicit security descriptors, enables process token privileges, loads/unloads user profiles, opens or terminates named job objects, and emits diagnostic messages to stderr/debugger. Allocations are split between `LocalAlloc`, CRT `calloc/free`, NetAPI buffers, and LSA-returned buffers, so caller-owned cleanup is part of the API contract.

Dependencies/integration: depends on Win32 security APIs, AuthZ, NetAPI, Secur32/LSA, Userenv, Ntdsapi, service/RPC MIDL conventions, and constants from `winutils.h`. It is consumed by command modules (`ls`, `chmod`, `chown`, `symlink`, `task`, `service`) and forms the privileged bridge used by YARN Windows Secure Container Executor.

Risks and test signals: high risk around Windows privilege availability, ACL ordering semantics, long path prefix handling, mixed allocation families, insufficient-buffer retry logic, and exact POSIX compatibility expectations. Tests should exercise symlink/junction follow behavior, mode round-tripping, owner/group lookup fallback to SID strings, service security descriptor authorization, S4U logon/profile cleanup, and job-object kill semantics under non-admin and LocalSystem contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/libwinutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/ls.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/ls.c

Purpose: implements `winutils ls`, a Windows analogue of `ls -ld` that reports file type, permissions, hardlink count, owner, group, size, timestamp, and input path.

Important APIs/functions: `ParseCommandLine` accepts optional `-L` symlink dereference and `-F` pipe-separated output; `GetMaskString` converts Hadoop Unix mask bits to `drwxrwxrwx` text; `LsPrintLine` formats the output; `Ls` drives validation, long-path conversion, metadata lookup, permission lookup, and output. `LsUsage` prints the help text.

Control flow: command-line parsing defaults to `.` when no path is provided, rejects duplicate or unknown options, rejects paths beginning with invalid characters, converts to long-path form, gets handle metadata via `GetFileInformationByName`, gets owner/group/mode via `FindFileOwnerAndPermission`, then prints using the original path string.

State and persistence: no persistent state is changed. It allocates owner/group/long-path buffers and writes a single formatted line to stdout or diagnostics to stderr.

Dependencies/integration: relies on `libwinutils.c` for path, file info, ACL-to-mode, and error reporting; uses the shared `MONTHS` table and `UX_*` constants from `winutils.h`. Called from `main.c` when command is `ls`.

Risks and test signals: exact output spacing and `-F` separator format are compatibility-sensitive. Tests should include regular files, directories, symlinks with and without `-L`, invalid duplicate options, invalid path strings, and ownership or ACL cases that affect the rendered mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/ls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/main.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/main.c

Purpose: top-level Unicode entry point for `winutils.exe`, dispatching subcommands and installing an unhandled structured-exception handler.

Important APIs/functions: `wmain` selects `ls`, `chmod`, `chown`, `groups`, `hardlink`, `symlink`, `readlink`, `task`, `systeminfo`, `service`, or `help`; `WinutilsSehUnhandled` logs and exits on unhandled SEH exceptions; `Usage` aggregates subcommand usage text.

Control flow: arguments with fewer than two elements print usage and fail. Recognized subcommands call their implementation with `argc - 1` and `argv + 1`, so each command sees its own name at `argv[0]`. `help` returns success; unknown commands return failure after printing usage.

State and persistence: no durable state is changed directly, but it installs a process-wide exception filter and can route into commands that mutate files, jobs, services, or security descriptors.

Dependencies/integration: includes `winutils.h` and assumes all command usage/entry functions are linked. It is the shared contract used by Hadoop Java code and tests invoking `winutils`.

Risks and test signals: dispatch depends on exact wide-string command names. Tests should confirm exit codes for no args, help, unknown commands, and that each subcommand receives argv layout expected by its parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/readlink.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/readlink.c

Purpose: implements `winutils readlink`, printing the target print-name of a Windows symbolic link with Unix-like success/failure behavior.

Important APIs/types/functions: local `REPARSE_DATA_BUFFER` definition avoids a WDK dependency; `Readlink` opens the reparse point with `FILE_FLAG_OPEN_REPARSE_POINT`, calls `FSCTL_GET_REPARSE_POINT`, validates `IO_REPARSE_TAG_SYMLINK`, extracts `PrintNameOffset`/`PrintNameLength`, null-terminates, and prints; `ReadlinkUsage` documents no-option behavior.

Control flow: only `argc == 2` is accepted. The link path is converted to long-path form, opened with backup semantics, then queried in a growing buffer loop on `ERROR_INSUFFICIENT_BUFFER` or `ERROR_MORE_DATA`. Non-symlink reparse points and all API errors fall through cleanup and return failure without detailed stderr messages.

State and persistence: read-only except for stdout. It allocates a long path, a reparse buffer, and a copied print-name buffer.

Dependencies/integration: depends on `ConvertToLongPath`, Win32 file/device APIs, and `winutils.h`; dispatched by `main.c`; pairs with `symlink.c` for link creation.

Risks and test signals: buffer length is in bytes while the terminator index is in WCHARs, so tests should include long Unicode targets. Test regular files, junctions, missing links, directory symlinks, and exact no-newline stdout formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/readlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/service.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/service.c

Purpose: implements the NodeManager Windows Secure Container Executor helper service, exposing privileged local RPC operations for process creation, file creation, deletion, chmod/chown, mkdir, move/copy, and task kill under constrained authorization.

Important APIs/functions: service lifecycle functions `RunService`, `SvcMain`, `SvcInit`, `SvcCtrlHandler`, `SvcShutdown`, `ReportSvcStatus`; security/config functions `ValidateConfigurationFile`, `AuthInit`, `InitLocalDirs`, `InitJobName`, `ValidateLocalPath`, `RpcAuthorizeCallback`; RPC functions `WinutilsCreateProcessAsUser`, `WinutilsCreateFile`, `WinutilsKillTask`, `WinutilsDeletePath`, `WinutilsMkDir`, `WinutilsChown`, `WinutilsChmod`, and `WinutilsMoveFile`.

Control flow: startup registers with SCM/event log, enables impersonation privileges, creates a stop event, validates that the WSCE config file is writable only by LocalSystem/Administrators, builds an allowed-caller security descriptor from config, loads local directories and optional job name, then starts a local-only RPC server with an AuthZ callback. RPC methods validate local paths, perform requested Win32 operations, duplicate handles back into the NodeManager process when needed, and log through Event Log/debug messages.

State and persistence: global service handles, event log handle, `pAllowedSD`, local-dir arrays, job name, and listener state persist for service lifetime. RPC operations mutate local files/directories, ACLs, ownership, process/job objects, and duplicated handles in the NodeManager process.

Dependencies/integration: depends on generated `hadoopwinutilsvc_h.h`, RPC runtime, AuthZ, service control manager, `libwinutils.c`, and WSCE XML config properties. It is the privileged peer of YARN NodeManager on Windows.

Risks and test signals: local path validation is prefix-based and path-normalization-sensitive; service auth depends on config ACL integrity; duplicate-handle cleanup is complex; process command-line construction has quoting and size limits. Tests should cover config ACL rejection, allowed/denied caller SIDs, local-dir escape attempts, handle transfer cleanup on mid-flight errors, and local-only RPC binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/symlink.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/symlink.c

Purpose: implements `winutils symlink`, creating Windows symbolic links while enforcing Hadoop-specific path and privilege checks.

Important APIs/functions: `Symlink` converts link and target to long paths, rejects forward-slash separated paths, enables `SeCreateSymbolicLinkPrivilege`, checks target directory status with `DirectoryCheck`, then calls `CreateSymbolicLinkW`; `SymlinkUsage` documents return code `2` for missing privilege.

Control flow: accepts exactly link name and target. Any conversion or validation failure exits through cleanup. Directory targets set `SYMBOLIC_LINK_FLAG_DIRECTORY`; file targets use zero flags.

State and persistence: creates a filesystem symlink and writes diagnostics. It does not change ACLs directly but depends on token privilege adjustment.

Dependencies/integration: depends on `ConvertToLongPath`, `EnablePrivilege`, `DirectoryCheck`, and `ReportErrorCode` from the shared library; dispatched by `main.c`; output is consumed by Hadoop tests and Windows filesystem integrations.

Risks and test signals: symlink privilege differs by Windows policy and developer mode; rejecting `/` paths prevents unusable links but may surprise callers. Tests should cover no privilege, file target, directory target, forward-slash rejection, missing target directory check errors, and exact return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/systeminfo.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/systeminfo.c

Purpose: implements `winutils systeminfo`, producing a comma-separated resource snapshot for memory, CPU, disk, and network counters.

Important APIs/functions: `SystemInfo` gathers `GetPerformanceInfo`, `GetSystemInfo`, `GetSystemTimes`, `CallNtPowerInformation`, and aggregate PDH counters; `GetDiskAndNetwork` opens a PDH query and reads wildcard network/disk counters; `ReadTotalCounter` sums raw counter array values unless `_Total` is present; `SystemInfoUsage` documents output order.

Control flow: memory and CPU totals are collected first; processor power information supplies max MHz; disk/network counters are added, collected, and read; stdout receives one CSV row of sizes, counts, CPU time, and IO totals. Any failure reports to stderr and exits failure.

State and persistence: read-only system inspection, with temporary PDH query handles and allocated buffers.

Dependencies/integration: uses PSAPI, PowrProf, PDH, `winutils.h`, and Windows performance counter names. Called from `main.c` and likely consumed by process/resource monitors.

Risks and test signals: localized or missing PDH counter names, unavailable power APIs, counter wildcard behavior, and `_Total` handling can vary by Windows version. Tests should verify CSV field count/types, graceful PDH failure, and non-negative resource values on supported Windows hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/systeminfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/task.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/task.c

Purpose: implements `winutils task`, managing Hadoop task processes through Windows job objects, optional memory/CPU limits, S4U user impersonation, job liveness, kill, and process resource listing.

Important APIs/functions: command parsing uses `TaskCommandOption` and `ParseCommandLine`; security functions include `BuildImpersonateSecurityDescriptor`, `ValidateImpersonateAccessCheck`, and `AddNodeManagerAndUserACEsToObject`; process functions include `CreateTaskImpl`, `CreateTask`, `CreateTaskAsUser`, `IsTaskAlive`, `PrintTaskProcessList`, and `Task`.

Control flow: `task create` creates a job object, sets kill-on-close and optional limits, assigns current process, sets `JVM_PID`, starts the child command, waits for exit, then terminates the job with the child exit code. `createAsUser` enables privileges, registers with LSA, creates an S4U token, loads profile, writes the pid file, then delegates to `CreateTaskImpl`. Status commands open plain or `Global\` job objects for query/kill/list.

State and persistence: creates named job objects, mutates kernel object DACLs, writes pid files, loads user profiles, sets an environment variable, starts and kills processes, and prints status/resource rows.

Dependencies/integration: depends on `libwinutils.c` for privileges, LSA, profile, config, job name, kill, SID lookup, and service security descriptors. It is launched directly from CLI and indirectly by `service.c` for secure container execution.

Risks and test signals: command-line concatenation for `createAsUser` is quote-sensitive; CPU limiting is conditional on Windows version macros; job object handle lifetime intentionally kills child trees; impersonation authorization depends on WSCE config. Tests should cover parser options, memory limit application, job alive false/true, kill idempotence, process list formatting, pid-file content, and denied impersonation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/site/site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/site/site.xml

Purpose: Maven site descriptor for the Hadoop Common module.

Important elements: `<project name="Apache Hadoop ${project.version}">`, a `maven-stylus-skin` skin with version property `${maven-stylus-skin.version}`, and a body link to the Apache Hadoop website.

Control flow: declarative XML consumed by Maven Site tooling; no executable code.

State and persistence: affects generated site rendering rather than runtime state.

Dependencies/integration: depends on Maven site plugin conventions and project properties. It integrates the module documentation into the larger Hadoop website style.

Risks and test signals: broken skin artifact/version properties or stale HTTP links can break site generation. Test signal is successful Maven site rendering with expected project name and navigation link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/site/site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/CLITestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/CLITestHelper.java

Purpose: reusable JUnit CLI test harness that reads XML test definitions, expands placeholders, executes commands, applies comparators, records results, and logs a detailed pass/fail summary.

Important APIs/classes: constants `TESTMODE_TEST`, `TESTMODE_NOCOMPARE`, `TEST_CACHE_DATA_DIR`; lifecycle `setUp`, `tearDown`; parser factory `getConfigParser`; command expansion `expandCommand`; runner `testAll`; abstract `execute`; inner SAX `TestConfigFileParser`.

Control flow: setup parses `testConf.xml` from the test cache and creates a security-enabled `Configuration`. `testAll` iterates parsed tests, executes all test commands, applies dynamic comparator classes by name, checks optional expected exit code, stores actual output/result data, then runs cleanup commands. Tear down logs details and asserts global success.

State and persistence: keeps parsed tests, comparator data, Hadoop configuration, data-dir URI, username placeholder, and mutable test mode in instance fields. It redirects no global streams itself, but `CommandExecutor` does during execution.

Dependencies/integration: uses secure SAX parsing through `XMLUtils`, JUnit 5 assertions, `Shell.WINDOWS` filtering, `FsShell` command types through utility classes, and comparator classes in `org.apache.hadoop.cli.util`.

Risks and test signals: comparator class loading via string is fragile; `username` is never initialized here while expansion replaces `USERNAME`; only the last command result in a multi-command test is compared; XML character accumulation preserves whitespace. Tests should validate parser behavior, Windows-only filtering, nocompare mode, cleanup execution after failures, and exact summary assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/CLITestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/TestCLI.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/TestCLI.java

Purpose: concrete JUnit test class binding `CLITestHelper` to the standard Hadoop Common CLI test config.

Important APIs/functions: overrides `setUp`, `tearDown`, `execute`, `getTestFile`, and `testAll`; `execute` resolves a `CLICommand` executor with empty namenode tag and the helper configuration.

Control flow: JUnit invokes setup, inherited `testAll`, and teardown. Test commands come from `testConf.xml`; each command uses `cmd.getExecutor("", conf).executeCommand(cmd.getCmd())`.

State and persistence: inherits all mutable harness state from `CLITestHelper`.

Dependencies/integration: integrates the generic CLI harness with `FsShell` command execution via `CLITestCmd`/`FSCmdExecutor`.

Risks and test signals: an empty namenode replacement means tests must not require a concrete `NAMENODE` unless the command executor handles it. Passing signal is successful execution of all XML-defined Common CLI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/TestCLI.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommand.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommand.java

Purpose: interface abstracting one parsed CLI test command and its executor factory.

Important APIs: `getExecutor(String tag, Configuration conf)`, `getType()`, `getCmd()`, and `toString()`.

Control flow: implemented by `CLITestCmd`; the harness calls `getExecutor` during test execution, then passes `getCmd` to the executor.

State and persistence: no state in the interface; implementers carry command text and type.

Dependencies/integration: depends on Hadoop `Configuration` and `CommandExecutor`. Enables upstream projects to add new command types without changing the harness.

Risks and test signals: type dispatch is runtime-only, so unknown implementations fail during execution. Tests should verify each supported `CLICommandTypes` has an executor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommandFS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommandFS.java

Purpose: marker class identifying filesystem shell commands in the CLI test harness.

Important APIs/types: implements `CLICommandTypes` without additional fields or methods.

Control flow: `CLITestCmd.getExecutor` checks `getType() instanceof CLICommandFS` and returns an `FSCmdExecutor`.

State and persistence: stateless marker.

Dependencies/integration: integrates XML `<command>` elements with `FsShell` execution in Hadoop Common tests.

Risks and test signals: behavior depends on `instanceof` rather than enum identity, so subclassing would also route to `FSCmdExecutor`. Tests should confirm parser-created commands use this type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommandFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommandTypes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommandTypes.java

Purpose: marker interface for categorizing CLI test command families.

Important APIs/types: empty interface implemented by `CLICommandFS`; intended for additional upstream command type markers.

Control flow: used by `CLICommand.getType` and runtime executor selection in `CLITestCmd`.

State and persistence: no state.

Dependencies/integration: part of the CLI test utility extension point.

Risks and test signals: no compile-time mapping enforces that each type has an executor. Tests should include failure behavior for unknown command types if new types are introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommandTypes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLITestCmd.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLITestCmd.java

Purpose: concrete immutable CLI command record used by the XML parser and test runner.

Important APIs/fields: final `CLICommandTypes type`, final `String cmd`; constructor; `getExecutor`, `getType`, `getCmd`, and `toString`.

Control flow: for `CLICommandFS`, `getExecutor` creates a new `FsShell(conf)` wrapped in `FSCmdExecutor`; unknown command types throw `IllegalArgumentException`.

State and persistence: stores command text and marker type for one parsed test command.

Dependencies/integration: depends on Hadoop `Configuration`, `FsShell`, and `FSCmdExecutor`; constructed by `CLITestHelper.TestConfigFileParser`.

Risks and test signals: each call creates a new `FsShell`, so tests should not assume shell state persists across commands unless Hadoop config/filesystem state carries it. Test unknown type exceptions and string preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLITestCmd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLITestData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLITestData.java

Purpose: mutable data holder for one XML-defined CLI test case.

Important APIs/fields: `testDesc`, `testCommands`, `cleanupCommands`, `comparatorData`, `testResult`, with simple getters and setters.

Control flow: populated by `CLITestHelper.TestConfigFileParser`, consumed and mutated by `CLITestHelper.testAll`, and read by `displayResults`.

State and persistence: stores in-memory parsed test state and execution outcome only.

Dependencies/integration: depends on `CLICommand`, `ComparatorData`, and Java `ArrayList`.

Risks and test signals: lists may remain null if XML omits sections, causing runner/display failures. Parser tests should verify all required sections initialize lists and result defaults are understood.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLITestData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CommandExecutor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CommandExecutor.java

Purpose: abstract command execution wrapper that tokenizes command strings, expands placeholders, captures stdout/stderr, and returns a result object.

Important APIs/classes: `getCommandAsArgs`, `executeCommand`, abstract `execute`, and nested immutable `Result` with output, exit code, exception, and executed command.

Control flow: `getCommandAsArgs` regex-tokenizes single-quoted, double-quoted, or non-space arguments, replaces `NAMENODE`, `CLITEST_DATA`, and `USERNAME`, then returns a string array. `executeCommand` redirects `System.out` and `System.err` to a buffer, calls subclass `execute`, captures exceptions as exit code `-1`, and restores streams in `finally`.

State and persistence: temporarily mutates JVM-global stdout/stderr, so parallel tests can interfere. No durable state.

Dependencies/integration: used by `FSCmdExecutor`; depends on `CLITestHelper.TEST_CACHE_DATA_DIR` and Java regex/IO APIs.

Risks and test signals: tokenization is shell-like but incomplete for escapes; `replaceAll` treats placeholders as regex; global stream redirection is not thread-safe. Tests should cover quoting, spaces in test data path, exception capture, and stream restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CommandExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ComparatorBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ComparatorBase.java

Purpose: abstract base class for CLI output comparators.

Important APIs: no-op constructor and abstract `compare(String actual, String expected)`.

Control flow: instantiated reflectively by `CLITestHelper.compareTestOutput`; subclasses implement exact, line, regexp, substring, token, or cross-output matching.

State and persistence: stateless by contract.

Dependencies/integration: comparator class names are specified in XML and resolved under `org.apache.hadoop.cli.util`.

Risks and test signals: base documentation says null inputs should return false, but several subclasses do not null-check. Tests should include comparator null-handling or document that XML/runtime never passes null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ComparatorBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ComparatorData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ComparatorData.java

Purpose: mutable data holder for one expected CLI validation and its actual result.

Important APIs/fields: `expectedOutput`, `actualOutput`, `testResult`, `exitCode`, `comparatorType`, with getters and setters.

Control flow: parser fills comparator type, expected output, and optional expected exit code; runner updates actual output, actual exit code, and boolean result after command execution.

State and persistence: in-memory test state only.

Dependencies/integration: consumed by `CLITestHelper.compareTestOutput`, `compareTextExitCode`, and result display.

Risks and test signals: `exitCode` is overwritten with actual exit code after comparison, so post-run display cannot directly show expected exit code. Tests should verify failure diagnostics remain useful and initial default `-1` means no exit-code check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ComparatorData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ExactComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ExactComparator.java

Purpose: comparator requiring complete actual output equality with expected output.

Important APIs: overrides `compare` as `actual.equals(expected)`.

Control flow: reflectively loaded by comparator type `ExactComparator`; returns true only for identical strings including whitespace and line endings.

State and persistence: stateless.

Dependencies/integration: used by XML CLI tests through `CLITestHelper`.

Risks and test signals: no null checks despite base contract; platform line endings and trailing output make this brittle. Tests should include exact whitespace cases and avoid null actual/expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ExactComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ExactLineComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ExactLineComparator.java

Purpose: comparator that passes when any actual output line exactly equals expected.

Important APIs: `compare` tokenizes actual output on `\n` and `\r` via `StringTokenizer` and checks line equality.

Control flow: scans until a match is found or tokens are exhausted.

State and persistence: stateless.

Dependencies/integration: reflectively used by CLI XML tests.

Risks and test signals: `StringTokenizer` drops empty lines and treats CR/LF as delimiters rather than preserving line endings. Tests should include multi-line output, empty-line expectations, and Windows CRLF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/ExactLineComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/FSCmdExecutor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/FSCmdExecutor.java

Purpose: executes parsed CLI commands through Hadoop `FsShell`.

Important APIs/fields: `namenode`, `FsShell shell`, constructor, and `execute`.

Control flow: `execute` tokenizes command text using inherited `getCommandAsArgs(cmd, "NAMENODE", namenode)` and invokes `ToolRunner.run(shell, args)`.

State and persistence: holds the shell instance and namenode replacement for the executor instance. Filesystem mutations are performed by the invoked `FsShell` commands.

Dependencies/integration: created by `CLITestCmd` for `CLICommandFS`; depends on Hadoop `FsShell` and `ToolRunner`.

Risks and test signals: shell reuse within an executor may carry configuration but not across command objects; placeholder substitution must produce valid FsShell arguments. Tests should verify quoted arguments and expected exit codes for representative FsShell commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/FSCmdExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/RegexpAcrossOutputComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/RegexpAcrossOutputComparator.java

Purpose: comparator that searches a regular expression across the entire command output, including multi-line spans.

Important APIs: `compare` normalizes carriage returns on Windows, compiles expected as a regex, and calls `matcher(actual).find()`.

Control flow: unlike `RegexpComparator`, does not tokenize by line and uses substring regex search rather than full-line match.

State and persistence: stateless.

Dependencies/integration: depends on `Shell.WINDOWS` and Java regex; reflectively loaded by CLI tests.

Risks and test signals: regex syntax errors propagate to the harness as comparator instantiation/use failures; no DOTALL flag is set unless the pattern requests it. Tests should cover CRLF normalization and true multi-line patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/RegexpAcrossOutputComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/RegexpComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/RegexpComparator.java

Purpose: line-oriented regular expression comparator for CLI output.

Important APIs: `compare` compiles expected as a `Pattern`, tokenizes actual output on CR/LF, and uses `Matcher.matches()` against each line.

Control flow: succeeds only when a whole line matches the regex. It stops scanning after the first match.

State and persistence: stateless.

Dependencies/integration: reflectively loaded by the CLI harness.

Risks and test signals: `matches()` requires full-line match, unlike a substring search; empty lines are ignored by `StringTokenizer`. Tests should distinguish full-line regex from contains-style expectations and cover CRLF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/RegexpComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/SubstringComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/SubstringComparator.java

Purpose: comparator that passes when expected appears anywhere in actual output.

Important APIs: `compare` uses `actual.indexOf(expected)`.

Control flow: returns false for `-1`, true otherwise.

State and persistence: stateless.

Dependencies/integration: reflectively loaded by CLI XML tests.

Risks and test signals: no null handling and no normalization; case-sensitive and whitespace-sensitive. Tests should include expected substrings with path separators and platform line endings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/SubstringComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/TokenComparator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/TokenComparator.java

Purpose: comparator that treats expected as a comma/newline/CR-delimited token list and requires every token to occur in actual output.

Important APIs: `compare` tokenizes expected with delimiters `,\n\r` and checks `actual.indexOf(token)`.

Control flow: initializes success true and ANDs each token presence result. If expected has no tokens, it returns true.

State and persistence: stateless.

Dependencies/integration: reflectively used by CLI tests for unordered or partial output checks.

Risks and test signals: token matching is substring-based, not word-boundary or normalized; empty expected can pass vacuously. Tests should cover missing token failure, duplicate tokens, and tokens containing spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/TokenComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestCommonConfigurationFields.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestCommonConfigurationFields.java

Purpose: configuration parity test ensuring properties declared in Hadoop Common-related configuration key classes are represented in `core-default.xml`, while allowing a curated set of XML-only or externally-owned keys.

Important APIs/classes: extends `TestConfigurationFieldsBase` and overrides `initializeMemberVariables`. Sets `xmlFilename`, `configurationClasses`, skip sets, and error modes. Configuration classes include `CommonConfigurationKeys`, `CommonConfigurationKeysPublic`, `LocalConfigKeys`, `FtpConfigKeys`, `SshFenceByTcpPort`, `LdapGroupsMapping`, `ZKFailoverController`, `SSLFactory`, `CompositeGroupsMapping`, `CodecUtil`, and `RuleBasedLdapGroupsMapping`.

Control flow: initialization chooses `core-default.xml`, enables `errorIfMissingConfigProps`, disables `errorIfMissingXmlProps`, then populates exact-property and prefix skip sets for FTP, S3A, O3, Azure/ABFS/WASB, ADL, GS, viewfs overload schemes, call queues, deprecated properties, HTTP/security/tracing/registry/private keys, and other keys owned outside the listed classes.

State and persistence: mutates inherited test configuration fields and skip sets only.

Dependencies/integration: relies on the base class to reflect constants from configuration classes and compare against XML. It guards consistency between runtime config key constants and shipped defaults.

Risks and test signals: skip lists can mask real drift if overused, while missing new classes can produce false XML-only gaps because `errorIfMissingXmlProps` is false. Tests should fail when a key constant in the listed classes lacks `core-default.xml` coverage, and maintainers should update skip reasons when moving keys between modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestCommonConfigurationFields.java -->
