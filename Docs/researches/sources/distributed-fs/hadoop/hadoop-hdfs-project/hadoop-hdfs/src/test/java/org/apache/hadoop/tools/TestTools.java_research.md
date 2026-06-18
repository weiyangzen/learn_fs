# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestTools.java

## Purpose
`TestTools` verifies command-line help, invalid-option output, and exit behavior for HDFS administrative tools: `DelegationTokenFetcher`, `JMXGet`, and `DFSAdmin`.

## Important APIs, types, and functions
- `before()` disables JVM exit through `ExitUtil.disableSystemExit()` and prepares an invalid option array.
- `checkOutput(String[], String, PrintStream, Class<?>)` captures either stdout or stderr, invokes the selected tool, and asserts the captured text contains an expected pattern.
- `expectDelegationTokenFetcherExit`, `expectJMXGetExit`, and `expectDfsAdminPrint` wrap tool invocation and expected `ExitException` handling.
- `testDFSAdminInvalidUsageHelp()` iterates many DFSAdmin commands with an extra invalid option and checks return code `-1`.

## Control flow
Individual tests call `checkOutput` with a command class and pattern. For tools that call `System.exit`, the disabled-exit hook throws `ExitException`, which is consumed and reset. DFSAdmin is invoked through `ToolRunner` or direct helper and expected to print usage for invalid combinations.

## State and persistence behavior
The class mutates global `ExitUtil` state and process stdout/stderr during capture. It does not create files or clusters.

## Dependencies and integration points
It integrates HDFS command-line tools, `ToolRunner`, `ExitUtil`, Guava/thirdparty `ByteStreams` and `ImmutableSet`, and Java piped streams.

## Risks and edge cases
Global stdout/stderr redirection and disabled system exit are not parallel-test-safe. Pipe buffer size is fixed at 5 KiB, so unexpectedly large output could block or truncate behavior. Pattern assertions are broad and may miss formatting regressions outside the checked substring.

## Test signals
Passing confirms common HDFS tools emit expected help/error text and handle invalid argument combinations without terminating the test JVM.
