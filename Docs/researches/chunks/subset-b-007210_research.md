# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.3.xml lines 37014-39037

## Scope

This chunk is the final segment of the Hadoop Common 3.3.3 JDiff API snapshot. It begins in the middle of `org.apache.hadoop.util.Shell`, then covers public API entries for shutdown hooks, string interning, system information, Hadoop `Tool` execution, build version metadata, Bloom filter implementations, and the first functional async/iterator helpers. The source is an API-description XML, so the chunk records public/protected signatures, fields, documentation, deprecation status, thrown exceptions, package/class boundaries, and selected type relationships rather than method bodies.

## Purpose

The APIs in this chunk are general support infrastructure used across Hadoop Common and downstream modules:

- `Shell` abstracts platform-specific process execution, command construction, Windows `winutils.exe` discovery, timeout handling, and process cleanup.
- `ShutdownHookManager` centralizes JVM shutdown hook ordering and timeout enforcement.
- `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, and `VersionInfo` provide common CLI, metadata, resource-reporting, and memory-optimization utilities.
- `org.apache.hadoop.util.bloom` provides serializable Bloom filter variants used by Hadoop IO components such as Bloom map files and by modules that need probabilistic membership tests.
- `FutureIO` and `RemoteIterators` in `org.apache.hadoop.util.functional` adapt Java futures and Hadoop `RemoteIterator` APIs to IOException-aware functional workflows.

## Important APIs and Types

### `org.apache.hadoop.util.Shell`

The chunk includes the lower portion of `Shell`:

- Windows binary discovery and validation: `hasWinutilsPath()`, `getWinUtilsPath()`, `getWinUtilsFile()`, public deprecated `WINUTILS`, and Hadoop home constants `SYSPROP_HADOOP_HOME_DIR` and `ENV_HADOOP_HOME`.
- Bash/process support: `checkIsBashSupported()`, `isSetsidAvailable`, OS booleans (`WINDOWS`, `LINUX`, `MAC`, `SOLARIS`, `FREEBSD`, `OTHER`, `PPC_64`), `osType`, and command constants such as `SET_PERMISSION_COMMAND`, `SET_OWNER_COMMAND`, `SET_GROUP_COMMAND`, `LINK_COMMAND`, `READ_LINK_COMMAND`, and `TOKEN_SEPARATOR_REGEX`.
- Execution lifecycle for subclasses: protected `setEnvironment(Map)`, `setWorkingDirectory(File)`, `run()`, abstract `getExecString()`, and abstract `parseExecResult(BufferedReader)`.
- Runtime inspection and cleanup: `getEnvironment(String)`, `getProcess()`, `getExitCode()`, `getWaitingThread()`, `isTimedOut()`, `destroyAllShellProcesses()`, and `getAllShells()`.
- Convenience execution: overloaded static `execCommand(...)` variants with optional environment and timeout.
- Platform-specific safety: `WindowsProcessLaunchLock`, `WINDOWS_MAX_SHELL_LENGTH`, deprecated misspelled `WINDOWS_MAX_SHELL_LENGHT`, and `getMemlockLimit(Long)`.

The implementation behind these declarations keeps a process-wide weak set of active `Shell` instances, starts `ProcessBuilder` commands, drains stdout/stderr in separate flows, destroys timed-out processes through a `TimerTask`, and converts nonzero exits into `ExitCodeException` from the nested class declared earlier in the XML.

### `ShutdownHookManager`

`ShutdownHookManager` is a final singleton. Its visible API in this chunk:

- `get()` returns the singleton.
- `addShutdownHook(Runnable, int)` and `addShutdownHook(Runnable, int, long, TimeUnit)` register hooks with priority and optional timeout.
- `removeShutdownHook(Runnable)`, `hasShutdownHook(Runnable)`, `isShutdownInProgress()`, and `clearShutdownHooks()` manage registrations and state.
- `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` define timeout defaults.

Hook identity is based on the runnable instance. Hooks with higher priority execute first; same-priority ordering is explicitly non-deterministic.

### `StringInterner`

`StringInterner` exposes static helpers:

- `strongIntern(String)` uses a strong Guava interner and retains interned values.
- `weakIntern(String)` delegates to Java string interning and does not add a Hadoop-owned strong reference.
- `internStringsInArray(String[])` mutates an array in place by weak-interning all entries.

Null string inputs return null for individual intern operations.

### `SysInfo`

`SysInfo` is an abstract resource information plugin:

- `newInstance()` chooses an OS-specific implementation, Linux or Windows in the backing code.
- Abstract getters expose total/available virtual and physical memory, processor/core counts, CPU frequency, cumulative CPU time, CPU utilization, vcores used, network bytes read/written, and storage bytes read/written.

Unsupported OS detection raises `UnsupportedOperationException`.

### `Tool` and `ToolRunner`

`Tool` extends Hadoop `Configurable` and defines `int run(String[] args) throws Exception`. It is the stable CLI application contract used by MapReduce and file-system tools.

`ToolRunner` runs a `Tool` after generic Hadoop option parsing:

- `run(Configuration, Tool, String[])` installs/updates the tool configuration through `GenericOptionsParser`, sets CLI caller/audit context in the backing implementation, and invokes `Tool.run()` with remaining arguments.
- `run(Tool, String[])` delegates to the tool's current configuration.
- `printGenericCommandUsage(PrintStream)` delegates generic option help.
- `confirmPrompt(String)` loops on `System.in` until `y/yes` or `n/no`.

### `VersionInfo`

`VersionInfo` reads component version properties and exposes common build metadata:

- Protected constructor and `_getVersion`, `_getRevision`, `_getBranch`, `_getDate`, `_getUser`, `_getUrl`, `_getSrcChecksum`, `_getBuildVersion`, `_getProtocVersion`.
- Static common accessors `getVersion`, `getRevision`, `getBranch`, `getDate`, `getUser`, `getUrl`, `getSrcChecksum`, `getBuildVersion`, `getProtocVersion`.
- `main(String[])` prints human-readable Hadoop build metadata.

The backing class also has a `getCompilePlatform()` API outside this exact JDiff chunk.

### `org.apache.hadoop.util.bloom`

The chunk covers the public Bloom-filter surface:

- `BloomFilter` extends `Filter`; it supports `add`, `membershipTest`, `and`, `or`, `xor`, `not`, `toString`, `getVectorSize`, `write`, and `readFields`.
- `CountingBloomFilter` extends `Filter`; it supports `add`, `delete`, `membershipTest`, `approximateCount`, `and`, `or`, `toString`, `write`, and `readFields`; `not` and `xor` are declared but unsupported by implementation.
- `DynamicBloomFilter` extends `Filter`; it adds new internal Bloom-filter rows when the current row reaches its configured record threshold and supports logical operations, string rendering, and Writable serialization.
- `HashFunction` turns a `Key` into `nbHash` vector positions using a selected `org.apache.hadoop.util.hash.Hash` implementation.
- `RemoveScheme` defines retouched Bloom clearing constants: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`; it tracks false-positive and true-key vectors, accepts false-positive observations, performs `selectiveClearing(Key, short)`, and serializes its extra vectors and ratios.

All Bloom classes are serializable through Hadoop `Writable` methods and depend on `Key`, `Filter`, and hash implementations in `org.apache.hadoop.util.hash`.

### `org.apache.hadoop.util.functional.FutureIO`

Visible APIs in this chunk:

- `awaitFuture(Future<T>)` and `awaitFuture(Future<T>, long, TimeUnit)` block for results while converting `InterruptedException` to `InterruptedIOException`, unwrapping nested execution failures, preserving runtime exceptions, and exposing timeout/cancellation separately.
- `raiseInnerCause(ExecutionException)` and `raiseInnerCause(CompletionException)` rethrow the meaningful nested cause.
- `unwrapInnerException(Throwable)` recursively unwraps `IOException`, `UncheckedIOException`, `ExecutionException`, and `CompletionException`, throws nested runtime/errors, or wraps unknown causes in `IOException`.

The backing file also includes additional APIs after this JDiff-visible set, such as option propagation and `CompletableFuture` evaluation helpers.

### `org.apache.hadoop.util.functional.RemoteIterators`

Visible APIs in this chunk adapt `RemoteIterator<T>`:

- Constructors from singleton, Java `Iterator`, `Iterable`, or array.
- Wrappers for mapping, type casting, filtering, and combined close behavior.
- Conversions to `List` or array.
- `foreach(RemoteIterator, ConsumerRaisingIOE)` applies an IOException-aware consumer and returns the processed count.
- `cleanupRemoteIterator(RemoteIterator)` logs `IOStatistics` at debug and closes closeable iterators.

Backing implementations preserve `IOStatisticsSource` where possible and close wrapped iterators when exhausted or on cleanup.

## Control Flow

`Shell.run()` is interval-gated: if the last execution is too recent, it returns without launching. Otherwise it constructs the command from `getExecString()`, applies the configured environment and working directory, launches through `ProcessBuilder`, starts timeout handling if configured, drains stderr concurrently, lets `parseExecResult()` process stdout, waits for the process, records the exit code, and tears down streams/process references in `finally`. Static `execCommand()` uses a `ShellCommandExecutor` wrapper for simple commands.

`ShutdownHookManager` registers one JVM hook at class initialization. During JVM shutdown, it flips an atomic shutdown flag, sorts registered hooks by descending priority, submits each hook to a single-thread executor, waits for the hook-specific timeout, cancels timed-out hooks, logs failures, then shuts down the executor with a configured timeout.

`ToolRunner.run()` normalizes the configuration, parses generic Hadoop command-line options, sets the mutated configuration back onto the `Tool`, and calls the tool with only remaining application arguments.

Bloom filter control flow is hash-first: each added or queried `Key` is converted to one or more vector positions by `HashFunction.hash(Key)`. Standard Bloom operations mutate `BitSet` state; counting filters mutate 4-bit counters packed into `long[]`; dynamic filters route inserts to the active row or append a new row; retouched filters choose a bit-clearing index using the selected removal scheme and update the true-key/false-positive tracking vectors.

`FutureIO.awaitFuture()` is a blocking boundary around asynchronous code: it calls `Future.get`, translates interruption, preserves cancellation, and unwraps asynchronous failure wrappers to match Hadoop's IOException-centric APIs.

`RemoteIterators` builds lazy wrapper chains. Filtering can advance the source in `hasNext()`; mapping applies during `next()`. `foreach()` guarantees cleanup in a `finally` block but intentionally does not hide IOExceptions from the source or consumer.

## State and Persistence Behavior

- `Shell` maintains static OS detection state, cached Hadoop home/winutils resolution results, and a synchronized weak map of active shell instances. Per-instance state includes timeout interval, inherit-parent-env flag, environment map, working directory, current process, exit code, waiting thread, completed flag, and timed-out flag. Shell state is runtime-only, not persisted.
- `ShutdownHookManager` stores hook entries in a synchronized set and shutdown progress in an `AtomicBoolean`. It is process-global runtime state.
- `StringInterner` strong interning retains process-lifetime references; weak interning uses the JVM string pool.
- `VersionInfo` loads properties from classpath resources into a `Properties` object and exposes them as static common metadata. Missing keys resolve to `"Unknown"`.
- Bloom filters persist through `Writable.write/readFields`. `Filter` writes a negative version marker, hash count, hash type, and vector size while retaining compatibility with an older unversioned format. Subclasses append their bit vectors, packed counters, dynamic row arrays, or retouched tracking vectors.
- `FutureIO` and `RemoteIterators` are stateless utility classes, but iterator wrappers carry lazy cursor, cached next-value, close state, or underlying iterator references.

## Dependencies and Integration Points

- `Shell` integrates with the host OS, `ProcessBuilder`, Hadoop home layout, `winutils.exe`, shell tools such as `bash`/`setsid`, `Time.monotonicNow`, `SubjectInheritingThread`, SLF4J, and Windows process serialization.
- `ShutdownHookManager` depends on JVM shutdown hooks, Hadoop `Configuration`, `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT`, `HadoopExecutors`, Guava `ThreadFactoryBuilder`, `SubjectInheritingThread`, and SLF4J.
- `ToolRunner` depends on `Configuration`, `GenericOptionsParser`, `CallerContext`, and `CommonAuditContext`; it is used broadly by Hadoop CLIs and tests.
- Bloom filters depend on `Writable`, `DataInput/DataOutput`, `Key`, `HashFunction`, and hash implementations. `BloomMapFile` tests and IO code are downstream integration signals.
- `FutureIO` integrates Java `Future`, `CompletableFuture`, `ExecutionException`, `CompletionException`, Hadoop filesystem builder APIs outside this chunk, and IOException-oriented contract tests.
- `RemoteIterators` integrates Hadoop `RemoteIterator`, `IOStatisticsSource`, `IOStatistics` logging/support, `Closeable`, and IOException-aware functional interfaces.

## Risks and Edge Cases

- `Shell` has strong platform coupling. Hadoop home/winutils are cached at class initialization, so environment/property changes after class load do not affect lookup. Process timeout uses `Process.destroy()` and a timer; subprocess trees or platform-specific process behavior may survive. `getWinUtilsPath()` throws `RuntimeException` on unresolved paths, whereas `getWinUtilsFile()` throws checked `FileNotFoundException`.
- `Shell.destroyAllShellProcesses()` iterates a global weak set and destroys current processes; callers must understand it is process-wide.
- Shutdown hooks with equal priority run in unspecified order; long-running hooks are cancelled but cancellation depends on interrupt responsiveness. Adding/removing hooks during shutdown raises `IllegalStateException`.
- Strong string interning can grow memory permanently for unbounded inputs.
- `SysInfo.newInstance()` only supports the OSes implemented by Hadoop; unsupported OSes fail at runtime.
- `ToolRunner.confirmPrompt()` blocks on standard input and writes prompts to stderr, making it unsuitable for noninteractive paths unless guarded.
- Bloom filters are mutable and not generally thread-safe. Counting filters saturate 4-bit counters at 15, so repeated insertions can distort `approximateCount()` and deletes. Dynamic filters require compatible matrix length and threshold for logical operations. Retouched Bloom filters intentionally trade selected false-positive removal for false negatives, and `RANDOM` clearing depends on an unseeded `Random`.
- `HashFunction.hash()` rejects null/empty key byte arrays and uses absolute modulo; extreme hash values should be considered in tests because `Math.abs(Integer.MIN_VALUE)` remains negative in Java.
- `FutureIO.awaitFuture()` blocks; cancellation is deliberately not converted to IOException. Callers that expect all failures as IOExceptions must handle `CancellationException`, runtime exceptions, and errors separately.
- `RemoteIterators.filteringRemoteIterator()` may perform source IO in `hasNext()`, which can surprise callers that assume `hasNext()` is cheap. `foreach()` closes/cleans up the iterator after iteration, so callers should not reuse it.

## Test Signals

Relevant tests and downstream signals in the tree include:

- `src/test/java/org/apache/hadoop/util/TestShell.java` and `TestWinUtils.java` for shell execution, timeout/platform behavior, Hadoop home, and winutils lookup.
- `src/test/java/org/apache/hadoop/util/TestShutdownHookManager.java` for ordering, registration, timeout, and shutdown-state behavior.
- `src/test/java/org/apache/hadoop/util/TestStringInterner.java` for null handling and strong/weak interning behavior.
- `src/test/java/org/apache/hadoop/util/TestSysInfoLinux.java` and `TestSysInfoWindows.java` for OS-specific `SysInfo` parsing.
- ToolRunner integration appears in CLI tests such as `TestFindClass`, filesystem shell tests, RPC benchmark tests, and tool-based load generator tests.
- `src/test/java/org/apache/hadoop/util/bloom/TestBloomFilters.java` and `BloomFilterCommonTester.java` cover Bloom membership, add, exception behavior, serialization/deserialization, logical operations, dynamic rows, counting approximate counts/deletes, retouched selective clearing, and large vector serialization.
- `src/test/java/org/apache/hadoop/io/TestBloomMapFile.java` is an integration signal for Bloom filters in Hadoop IO.
- `src/test/java/org/apache/hadoop/fs/impl/TestFutureIO.java`, filesystem contract tests, and statistics duration tests exercise `FutureIO.awaitFuture`, exception extraction, timeouts, and async filesystem flows.
- `src/test/java/org/apache/hadoop/util/functional/TestRemoteIterators.java` covers iterator creation, mapping/filtering, closing, statistics passthrough, haltable iteration, and list/array/foreach conversions.

## Chunk Notes for Reconciliation

This document intentionally describes only `Apache_Hadoop_Common_3.3.3.xml` lines 37014-39037. Earlier methods and nested classes of `Shell`, the abstract `Filter` base class, `Key`, hash package classes, and later functional helpers may be covered by adjacent chunks or by final merge reconciliation. No final per-source report was written here.
