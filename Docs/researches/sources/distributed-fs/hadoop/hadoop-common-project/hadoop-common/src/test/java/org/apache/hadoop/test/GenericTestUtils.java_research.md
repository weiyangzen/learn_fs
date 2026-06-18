# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/GenericTestUtils.java

Purpose: broad shared test utility class for logging, temp paths, exception assertions, waiting, system-error/log capture, Mockito answers, thread leak checks, file diffs, formatted failures, parallel test sizing, and synthetic filesystem trees.

Important APIs/types/functions: log controls `disableLog/setLogLevel/toLevel`, temp helpers `getTestDir/getTempPath`, `assertExceptionContains`, `waitFor`, `SystemErrCapturer`, `LogCapturer`, `DelayAnswer`, `DelegateAnswer`, `SleepAnswer`, regex asserts, thread checks, `assumeInNativeProfile`, `getFilesDiff`, `failf/failif`, `getTestsThreadCount`, `createFiles/createDirsAndFiles`, `buildPaths`, and private async `put`.

Control flow: most helpers are stateless static utilities. `waitFor` polls a supplier until true or timeout and emits thread diagnostics. Capture classes install appenders or replace `System.err` temporarily. Mockito answers block, delegate, or sleep around method calls. File-tree helpers generate paths recursively, then create directories and files asynchronously using a shared blocking thread pool.

State and persistence behavior: static atomic sequence and static executor are process state. Temp/file helpers write under `test.build.data` or `target/test/data`; filesystem tree creation writes through a Hadoop `FileSystem`.

Dependencies and integration points: integrates JUnit assertions/assumptions, Mockito, log4j/SLF4J, Hadoop FS utilities, `DurationInfo`, thread diagnostics, and Hadoop functional future helpers.

Risks and test signals: broad shared surface means regressions affect many tests. Risks include global logging mutation, thread-pool resource use, capture cleanup requirements, and timeout flakiness. Strong utility signals include detailed timeout diagnostics, exact exception text validation, leak checks, and deterministic path naming.
