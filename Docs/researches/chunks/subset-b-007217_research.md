# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.4.xml lines 37014-39037

## Scope

This chunk is the final portion of the Hadoop Common 3.3.4 JDiff public API XML. It closes the `org.apache.hadoop.util.Shell` class, documents several core utility classes in `org.apache.hadoop.util`, then covers the public Bloom filter API under `org.apache.hadoop.util.bloom` and functional helper APIs under `org.apache.hadoop.util.functional`. The source is an API snapshot rather than executable source, so the research focuses on exposed contracts, state surfaces, expected control flow, integration points, and compatibility risks.

## Purpose

The chunk groups utility APIs used across Hadoop Common:

- `Shell` provides a base abstraction and static helpers for launching native commands, discovering Hadoop home and Windows `winutils`, enforcing timeouts, tracking live shell processes, and exposing OS/platform constants.
- `ShutdownHookManager` gives Hadoop a deterministic, priority-ordered shutdown hook registry with per-hook timeouts instead of relying directly on JVM shutdown hook ordering.
- `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, and `VersionInfo` support common runtime concerns: memory-efficient strings, OS resource metrics, command-line application bootstrapping, generic Hadoop option parsing, and build metadata reporting.
- `org.apache.hadoop.util.bloom` exposes Bloom filter variants for compact set-membership structures, deletion/counting, dynamic growth, retouched false-positive removal, and hash vector generation.
- `FutureIO` and `RemoteIterators` make async IO and `RemoteIterator` composition easier while preserving Hadoop IO exception semantics and optional IO statistics.

## Important APIs, Types, And Functions

### `org.apache.hadoop.util.Shell`

This segment contains the operational tail of `Shell`:

- Windows executable discovery: `hasWinutilsPath()`, `getWinUtilsPath()`, and `getWinUtilsFile()` publish a safer replacement for directly reading the deprecated nullable `WINUTILS` field. `getWinUtilsPath()` converts lookup failure to `RuntimeException`; `getWinUtilsFile()` raises `FileNotFoundException`.
- Shell capability probing: `checkIsBashSupported()` returns whether bash can be used and may raise `InterruptedIOException`.
- Instance setup and execution: protected `setEnvironment(Map)`, `setWorkingDirectory(File)`, `run()`, abstract `getExecString()`, and abstract `parseExecResult(BufferedReader)` define the subclass contract. A subclass provides command arguments and parses stdout; the base class handles launch cadence, timeout behavior, and process state.
- Runtime inspection: `getEnvironment(String)`, `getProcess()`, `getExitCode()`, `getWaitingThread()`, and `isTimedOut()` expose environment lookup and current process lifecycle state.
- Convenience execution: overloaded static `execCommand(...)` methods run a command with optional environment and timeout and return stdout as a `String`.
- Process registry: `destroyAllShellProcesses()` destroys all currently running `Shell` processes in a thread-safe way; `getAllShells()` returns the registered set.
- Native memory helper: `getMemlockLimit(Long ulimit)` computes the datanode memory lock limit capped by the provided `ulimit`.
- Published constants include Hadoop home property/env names, OS booleans and `osType`, Unix command names, Windows process-launch lock, Windows command-line length limit, `ENV_NAME_REGEX`, `TOKEN_SEPARATOR_REGEX`, timeout and environment inheritance fields, deprecated misspelled `WINDOWS_MAX_SHELL_LENGHT`, deprecated nullable `WINUTILS`, and `isSetsidAvailable`.

### `org.apache.hadoop.util.ShutdownHookManager`

`ShutdownHookManager` is a final singleton reached through `get()`. Its registry API is:

- `addShutdownHook(Runnable, int)` and `addShutdownHook(Runnable, int, long, TimeUnit)` register hooks with priority. Higher priority runs earlier; same-priority hooks run in nondeterministic order.
- `removeShutdownHook(Runnable)` and `hasShutdownHook(Runnable)` query and mutate the registry.
- `isShutdownInProgress()` exposes shutdown state.
- `clearShutdownHooks()` removes all registered hooks, mostly useful for tests.
- `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` define timeout policy. The class documentation states default hook timeout comes from `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT` with `SERVICE_SHUTDOWN_TIMEOUT_DEFAULT`.

### `org.apache.hadoop.util.StringInterner`

`StringInterner` exposes `strongIntern(String)`, `weakIntern(String)`, and `internStringsInArray(String[])`. The array method interns in place and returns the same array. Documentation says weak interning uses the standard `String.intern()` behavior from JDK 7 onward, while strong interning retains a strong reference and prevents collection.

### `org.apache.hadoop.util.SysInfo`

`SysInfo` is an abstract plugin interface for OS resource metrics. `newInstance()` chooses the default OS implementation and may throw `UnsupportedOperationException` when the OS cannot be determined. Implementations provide:

- memory totals and availability: virtual and physical memory sizes;
- CPU topology and usage: logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, and vcores used;
- aggregate IO counters: network bytes read/written and storage bytes read/written.

Methods return primitive `long`, `int`, or `float`; CPU usage and vcores may return `-1` when unavailable.

### `org.apache.hadoop.util.Tool` And `ToolRunner`

`Tool` extends `Configurable` and standardizes Hadoop command-line applications through `run(String[] args): int`. The contract expects generic Hadoop options to be delegated to `ToolRunner`, while the tool handles only application-specific arguments.

`ToolRunner` provides:

- `run(Configuration, Tool, String[])`: parses generic options through `GenericOptionsParser`, updates the tool's configuration, and invokes `Tool.run`.
- `run(Tool, String[])`: delegates using the tool's existing configuration.
- `printGenericCommandUsage(PrintStream)`: emits generic option usage.
- `confirmPrompt(String)`: prompts and returns true for case-insensitive `y` or `yes`.

### `org.apache.hadoop.util.VersionInfo`

`VersionInfo` exposes protected instance accessors for component build metadata and public static getters:

- `getVersion()`, `getRevision()`, `getBranch()`, `getDate()`, `getUser()`, `getUrl()`, `getSrcChecksum()`, `getBuildVersion()`, and `getProtocVersion()`;
- `main(String[])` for command-line metadata display.

The class is the public build-info surface for Hadoop components, including Git revision, branch, compile date/user, source checksum, and protobuf compiler version.

### `org.apache.hadoop.util.bloom`

The Bloom package in this chunk contains:

- `BloomFilter extends Filter`: standard Bloom filter with constructors for deserialization and `(vectorSize, nbHash, hashType)`. It supports `add(Key)`, `membershipTest(Key)`, boolean operations `and`, `or`, `xor`, `not`, `getVectorSize()`, `toString()`, and `Writable`-style `write(DataOutput)` / `readFields(DataInput)`.
- `CountingBloomFilter final extends Filter`: counting-vector implementation that supports `add(Key)`, `delete(Key)`, `membershipTest(Key)`, `approximateCount(Key)`, boolean operations, string rendering, and serialization. Counts are limited by small buckets; the docs warn that inserting the same key more than 15 times overflows associated positions and increases error rates.
- `DynamicBloomFilter extends Filter`: matrix/row-based filter that grows by adding rows when the active row reaches threshold `nr`. It supports add, membership test, boolean operations, string rendering, and serialization.
- `HashFunction final`: configured by `maxValue`, `nbHash`, and Hadoop hash type. `hash(Key)` returns multiple integer positions; `clear()` is a no-op.
- `RemoveScheme`: constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` define retouched Bloom filter bit-clearing strategies.
- `RetouchedBloomFilter final extends BloomFilter implements RemoveScheme`: adds false-positive tracking through `addFalsePositive(Key)`, overloads for `Collection`, `List`, and `Key[]`, and `selectiveClearing(Key, short)` to remove selected false positives at the cost of possible false negatives. It also participates in serialization through `write` and `readFields`.

### `org.apache.hadoop.util.functional.FutureIO`

`FutureIO` is a final static helper class for waiting on asynchronous IO while preserving checked `IOException` behavior:

- `awaitFuture(Future<T>)` and `awaitFuture(Future<T>, long, TimeUnit)` wait for completion, extract exceptions from the future, and rethrow nested `IOException`, `RuntimeException`, `InterruptedIOException`, or `TimeoutException` as appropriate.
- `raiseInnerCause(ExecutionException)` and `raiseInnerCause(CompletionException)` always throw the inner cause as an `IOException`, runtime exception, or wrapped `IOException`.
- `unwrapInnerException(Throwable)` recursively unwraps `IOException`, `UncheckedIOException`, `ExecutionException`, and `CompletionException`; it throws runtime exceptions and errors directly, and wraps other causes in `IOException`.

### `org.apache.hadoop.util.functional.RemoteIterators`

`RemoteIterators` is a final static helper class for building and composing Hadoop `RemoteIterator` instances:

- factories: `remoteIteratorFromSingleton(T)`, `remoteIteratorFromIterator(Iterator<T>)`, `remoteIteratorFromIterable(Iterable<T>)`, and `remoteIteratorFromArray(T[])`;
- transforms: `mappingRemoteIterator(RemoteIterator<S>, FunctionRaisingIOE<S,T>)`, `typeCastingRemoteIterator(RemoteIterator<S>)`, and `filteringRemoteIterator(RemoteIterator<S>, FunctionRaisingIOE<S,Boolean>)`;
- lifecycle composition: `closingRemoteIterator(RemoteIterator<S>, Closeable)` forwards close behavior to wrapped iterators and an additional closeable;
- materialization and consumption: `toList(RemoteIterator<T>)`, `toArray(RemoteIterator<T>, T[])`, `foreach(RemoteIterator<T>, ConsumerRaisingIOE<T>)`, and `cleanupRemoteIterator(RemoteIterator<T>)`.

The class is intended to preserve IOStatisticsSource passthrough and log IO statistics at DEBUG during `foreach` or cleanup when available.

## Control Flow

`Shell` subclasses follow a template-method pattern: configure environment and working directory, call protected `run()`, let the subclass provide the command vector through `getExecString()`, then parse process output through `parseExecResult(BufferedReader)`. Static `execCommand` wraps this pattern for simple one-shot commands. Timeout flow is visible through `timeOutInterval`, `isTimedOut()`, exit-code inspection, and `getWaitingThread()`. Global shutdown or cleanup can call `destroyAllShellProcesses()` to terminate all registered shells.

`ShutdownHookManager` centralizes JVM shutdown handling. Instead of registering many independent JVM hooks, Hadoop registers one manager hook, sorts registered runnables by priority, and runs higher-priority hooks first. A hook registered with an explicit timeout uses its own timeout; otherwise timeout configuration is read from `core-site.xml`. Same-priority ordering remains nondeterministic.

`ToolRunner` control flow is generic-option parse, configuration mutation, and `Tool.run` invocation. The two `run` overloads differ only in where the initial `Configuration` comes from. `confirmPrompt` is synchronous stdin/stdout interaction with a narrow yes condition.

Bloom filter control flow is hash-driven: `HashFunction.hash(Key)` maps a key to positions; `add` mutates vectors/counters/rows; `membershipTest` checks positions; boolean operations combine compatible filters. `CountingBloomFilter.delete` decrements counters only for present keys by contract. `DynamicBloomFilter.add` inserts into an active row or creates a new row once the row threshold is met. `RetouchedBloomFilter` first records known false positives, then `selectiveClearing` chooses bits to reset based on a `RemoveScheme`.

`FutureIO` control flow is exception normalization around `Future.get()`: interruption becomes `InterruptedIOException`, timeout remains `TimeoutException`, nested checked IO failures are surfaced as `IOException`, unchecked failures remain unchecked, and arbitrary checked causes are wrapped. `RemoteIterators` builds lazy wrappers: mapping/filtering happen during iteration, filtering may advance in `hasNext()`, materialization consumes the source, and cleanup optionally closes and logs statistics.

## State And Persistence Behavior

`Shell` has both per-instance mutable state and process-wide static state. Per-instance state includes environment, working directory, current `Process`, exit code, waiting thread, timeout flag/interval, and whether to inherit parent environment. Static state includes OS detection constants, `WINUTILS`, `isSetsidAvailable`, command constants, and a registry of live shells. `WINUTILS` is deprecated because null handling leaked into callers; the exception-raising getters are the stable contract.

`ShutdownHookManager` persists hook registrations in memory only for the JVM lifetime. It tracks shutdown-in-progress state and hook metadata including priority and timeout. `clearShutdownHooks()` can erase this state, which is valuable in tests but risky in shared runtime code.

`StringInterner` stores interned strings either strongly or weakly depending on method, affecting heap retention. `internStringsInArray` mutates the caller's array in place.

`SysInfo` exposes live OS counters. Values are observational and may be unavailable, platform-specific, cumulative, or sampled.

`VersionInfo` reads build metadata generated at build time and exposes it as immutable strings at runtime.

Bloom filters are persistent Hadoop data structures through `write(DataOutput)` and `readFields(DataInput)`. Default constructors exist specifically for deserialization. Persistent state includes vector size, hash count/type, bit vectors, counter vectors, dynamic rows and thresholds, and retouched false-positive metadata. Compatibility depends on serialized field order in the implementation, not visible in this JDiff snapshot.

`FutureIO` is stateless. `RemoteIterators` wrappers hold references to source iterators, mapping/filter functions, optional cached next elements, closeables, and possibly IO statistics sources; they are lazy and stateful across iteration.

## Dependencies And Integration Points

Key dependencies surfaced in this chunk:

- Java platform APIs: `Process`, `Thread`, `File`, `BufferedReader`, `DataInput`, `DataOutput`, `IOException`, `FileNotFoundException`, `InterruptedIOException`, `UncheckedIOException`, `ExecutionException`, `CompletionException`, `Future`, `TimeoutException`, `TimeUnit`, `Iterator`, `Iterable`, `Collection`, `List`, `Closeable`, and `PrintStream`.
- Hadoop configuration and CLI: `org.apache.hadoop.conf.Configurable`, `Configuration`, `GenericOptionsParser`, `CommonConfigurationKeysPublic`, and the generic options command manual.
- Hadoop filesystem iteration: `org.apache.hadoop.fs.RemoteIterator`, IO statistics source behavior, and functional interfaces `FunctionRaisingIOE` and `ConsumerRaisingIOE`.
- Hadoop hashing and serialization: `org.apache.hadoop.util.hash.Hash`, Bloom `Key`, base `Filter`, and Writable-style binary IO through `DataInput`/`DataOutput`.
- Logging: `Shell.LOG` and `RemoteIterators` DEBUG logging for IO statistics.
- Native/platform integration: OS detection, Unix commands such as permission/owner/group/link/readlink, Windows `winutils`, bash probing, `setsid`, Windows process launch locking, and command-line length limits.

These APIs are broad integration points. `Tool`/`ToolRunner` are a stable entry path for Hadoop command-line applications. `RemoteIterators` is especially relevant to object-store filesystems and listings, where lazy remote enumeration, closeable resources, and IO statistics are operationally important.

## Risks And Edge Cases

- `Shell.WINUTILS` remains public but deprecated and nullable. Callers that still read it directly risk null failures and weaker diagnostics.
- Native command execution is platform-sensitive. Windows command length, bash availability, `setsid`, environment variable validation, working directory existence, and Hadoop home discovery are all likely failure points.
- `destroyAllShellProcesses()` is process-wide. It is useful for shutdown/test cleanup but can terminate unrelated active shell operations in the same JVM.
- `ShutdownHookManager` same-priority hook ordering is nondeterministic. Hooks with dependencies need explicit priority separation.
- Shutdown hook timeouts can terminate unfinished cleanup. Very short explicit timeouts or misconfigured service shutdown timeout may leave resources unflushed.
- `StringInterner.strongIntern` can create unbounded retention if applied to high-cardinality strings.
- `SysInfo` is abstract and platform-backed; metric semantics can differ by OS and unsupported metrics may return `-1` or throw during instance selection.
- `ToolRunner.confirmPrompt` is interactive and unsuitable for non-interactive daemons unless guarded.
- Bloom filters are probabilistic. Standard Bloom filters allow false positives; counting filters can overflow after repeated adds and can underflow after deletes, introducing inaccurate counts or false negatives; retouched filters intentionally trade selected false positives for possible false negatives.
- Boolean operations on Bloom filters are only meaningful for compatible vector sizes, hash counts, and hash types. The JDiff contract does not show validation behavior, so implementation tests should cover incompatible filters.
- `FutureIO.unwrapInnerException` intentionally rethrows runtime exceptions and errors. Callers expecting all failures as `IOException` must account for unchecked propagation.
- `RemoteIterators.filteringRemoteIterator` may perform filtering work in `hasNext()`, which can surface IO failures or advance remote state earlier than callers expect. Materializing with `toList`/`toArray` can consume large remote listings into memory.
- `RemoteIterators.cleanupRemoteIterator` depends on closeable support and DEBUG logging; missing cleanup can leak network connections, file handles, or listing resources.

## Test Signals

Useful tests and validation signals for code touching APIs in this chunk:

- `Shell`: tests for `winutils` discovery on Windows and non-Windows, exception behavior of `getWinUtilsPath()`/`getWinUtilsFile()`, command timeout and `isTimedOut()`, environment propagation, working directory propagation, exit-code capture, process registry cleanup, and concurrent `destroyAllShellProcesses()`.
- `ShutdownHookManager`: ordering by priority, nondeterministic same-priority tolerance, explicit and default timeout handling, removal/query semantics, shutdown-in-progress state, and `clearShutdownHooks()` isolation across tests.
- `StringInterner`: identity reuse for equal strings, in-place array mutation, null behavior if supported by implementation, and memory-retention expectations for strong versus weak paths.
- `SysInfo`: platform-specific implementations should be tested for units, unavailable metric sentinels, monotonic cumulative CPU time, and supported OS selection in `newInstance()`.
- `ToolRunner`: generic option parsing should mutate the tool configuration while preserving application args; exit code from `Tool.run` should pass through; usage printing and prompt parsing should be covered.
- `VersionInfo`: generated build metadata resource loading, static getter consistency, and CLI output from `main`.
- Bloom filters: add/membership semantics, expected false-positive/no-false-negative properties for standard Bloom filters, counting add/delete/approximate count including overflow and underflow cases, dynamic row expansion at threshold `nr`, retouched selective clearing for each `RemoveScheme`, boolean operations, `toString`, and round-trip `write`/`readFields` compatibility.
- `FutureIO`: completed future result propagation, interrupted waits, timeout waits, unwrapping of `IOException`, `UncheckedIOException`, `ExecutionException`, `CompletionException`, runtime exceptions, errors, and arbitrary checked exceptions.
- `RemoteIterators`: singleton/array/iterator/iterable factories, lazy mapping and filtering with IO-raising functions, type casting behavior, close propagation through nested wrappers, `toList`/`toArray` materialization, `foreach` count return, consumer failure propagation, cleanup idempotence, and IOStatistics logging when DEBUG is enabled.
