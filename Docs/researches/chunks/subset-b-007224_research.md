# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.5.xml lines 37146-40640

## Research scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.3.5, not Java implementation source. The range starts at the tail of `org.apache.hadoop.service.ServiceStateModel`, covers the public `org.apache.hadoop.service.launcher` package, a broad slice of `org.apache.hadoop.util`, all visible `org.apache.hadoop.util.bloom` entries in this range, and the beginning of `org.apache.hadoop.util.functional`. Conclusions are based on package/class/interface declarations, inheritance, visibility, declared exceptions, fields, method signatures, and embedded Javadocs.

## Purpose

The chunk documents support APIs that sit under Hadoop command-line tools, service launchers, platform integration, diagnostics, serialization-friendly probabilistic data structures, and async/listing utilities. The service launcher layer gives long-running Hadoop services a standard lifecycle and process-exit contract. The utility layer provides classloader isolation, command execution, shutdown hook ordering, reflection-based instantiation, duration logging, checksums, system-resource reporting, CLI `Tool` dispatch, and build-version reporting. The Bloom filter package exposes serializable set-membership filters. The functional package begins a newer set of helpers for executor lifecycle management, future exception unwrapping, filesystem builder option propagation, and `RemoteIterator` composition.

## Important APIs and types

The chunk begins with `ServiceStateModel.checkStateTransition(String, Service.STATE, Service.STATE)`, `isValidStateTransition(Service.STATE, Service.STATE)`, and `toString()`. These APIs guard and describe Hadoop `Service` lifecycle transitions. `isValidStateTransition` explicitly treats `current == proposed` as a non-transition rather than a valid transition check.

`org.apache.hadoop.service.launcher.AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService`. Its protected name constructor delegates service naming to the superclass. The base `bindArgs(Configuration, List)` logs command-line arguments at debug level and returns the original `Configuration`; the base `execute()` returns success code `0`.

`HadoopUncaughtExceptionHandler` implements `Thread.UncaughtExceptionHandler`. It can wrap a delegate handler for "simple" exceptions or run standalone. Its contract is conservative for JVM `Error`: log and exit instead of attempting a clean shutdown when process state may be corrupt. It is intended to be installed as the default uncaught exception handler in main entry points.

`LaunchableService` extends `Service` and adds `bindArgs(Configuration, List)` plus `execute()`. The launcher invokes `bindArgs` before `Service.init(Configuration)`, allowing a service to replace or mutate the configuration before initialization. After `Service.start()`, the launcher calls `execute()`, and that return value becomes the process exit code. Its exception policy distinguishes `ExitUtil.ExitException`, `ExitCodeProvider`, and generic exceptions, mapping the latter two into `ServiceLaunchException` where needed.

`LauncherExitCodes` centralizes process exit constants. The documented groups are Unix success `0`, generic command issues, HTTP-like client/config errors in the 40s, service-side failures in the 50s, and application-specific codes at 60+. Named constants include success/fail, client shutdown, task launch failure, interrupted, command argument error, unauthorized, usage, forbidden, not found, operation not allowed, not acceptable, connectivity problem, bad configuration, exception thrown, unimplemented, service unavailable, unsupported version, service creation failure, and service lifecycle exception.

`ServiceLaunchException` extends `ExitUtil.ExitException` and implements both `ExitCodeProvider` and `LauncherExitCodes`. Constructors accept an exit code plus a cause, message, formatted message, or cause with formatted message. The formatted constructors use English-locale `String.format`, and one constructor treats a trailing throwable in the argument list as the cause.

`ApplicationClassLoader` extends `URLClassLoader` for application isolation. It can be constructed from URL arrays or a classpath string, overrides resource lookup and class loading, and exposes `isSystemClass(String, List)` to decide whether a name should be loaded from the parent/system side. `SYSTEM_CLASSES_DEFAULT` keeps JDK, Hadoop, resource, and selected third-party classes out of the application-first loader path.

`DurationInfo` extends `OperationDuration` and implements `AutoCloseable`. It logs a formatted operation description at info or debug level and logs final duration in `close()`, making it suitable for try-with-resources timing blocks. `OperationDuration` records start and finish clock times, exposes `finished()`, `value()` in milliseconds, `asDuration()`, and static `humanTime(long)` formatting.

`IPList` is a small membership interface with `isIn(String ipAddress)`. `Progressable` exposes `progress()` for long-running Hadoop operations to report liveness to a framework that may otherwise time out work.

`PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`. Each has `getValue()`, `reset()`, `update(byte[], int, int)`, and final single-byte `update(int)`. `PureJavaCrc32` targets the same polynomial as the native `CRC32` while avoiding JNI overhead for small repeated updates. `PureJavaCrc32C` targets the CRC32-C polynomial used by iSCSI and hardware-accelerated on many Intel chipsets.

`ReflectionUtils` provides Hadoop-aware reflection helpers: `setConf(Object, Configuration)` for `Configurable` instances, `newInstance(Class, Configuration)` for configured construction, contention tracing toggles, synchronized thread dump printing, commons-logging and SLF4J thread-stack logging with minimum intervals, typed `getClass(T)`, serialization-based `copy(Configuration, T, T)`, `cloneWritableInto(Writable, Writable)`, and utilities that gather declared fields or methods across superclasses.

`Shell` is an abstract base for platform-aware command execution. It has protected constructors for no throttling, minimum run interval, and optional stderr redirection. Static helpers build OS-specific command arrays for group lookup, group-id lookup, netgroups, permissions, ownership, symlinks, readlink, process liveness, signal/kill, scripts, Hadoop-home qualified binaries, Winutils lookup, bash support, and one-shot `execCommand` calls. Instance methods configure environment and working directory, run commands subject to the interval, expose process/exit/waiting-thread/timeout state, and require subclasses to implement `getExecString()` and `parseExecResult(BufferedReader)`. Public fields document OS booleans, command constants, regexes, timeout and environment behavior, `WINUTILS`, setsid support, and the token separator regex. `isJava7OrAbove()` remains public but is deprecated because Hadoop now assumes Java 7 or later.

`ShutdownHookManager` is a singleton manager for deterministic shutdown hook ordering. It registers one JVM hook and runs registered `Runnable` hooks by priority, with higher priorities first and same-priority hooks unordered. Hooks can be added with just priority or with priority plus timeout/time unit, removed, tested, queried for shutdown-in-progress, or cleared. `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT` document timeout defaults, and the class Javadoc ties default timeout behavior to `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT`.

`StringInterner` provides `strongIntern(String)`, `weakIntern(String)`, and in-place `internStringsInArray(String[])`. The Javadoc says weak interning uses standard `String.intern()` behavior, while strong interning retains a strong representative reference.

`SysInfo` is an abstract plugin for host resource metrics. `newInstance()` returns the default implementation for the detected OS or throws `UnsupportedOperationException`. Abstract methods report virtual and physical memory totals and availability, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, vcores used, network bytes read/written, and storage bytes read/written. Several metrics may return `-1` where unavailable.

`Tool` extends `Configurable` and defines `run(String[] args)`. Its Javadoc establishes the standard Hadoop command-line pattern: `ToolRunner` parses generic options into a `Configuration`, sets the tool's configuration, then leaves application-specific arguments for the tool. `ToolRunner` exposes `run(Configuration, Tool, String[])`, `run(Tool, String[])`, `printGenericCommandUsage(PrintStream)`, and `confirmPrompt(String)`.

`VersionInfo` exposes build metadata: version, Git revision, branch, compile date, build user, repository URL, source checksum, build version, protoc version, and `main(String[])`. Protected instance methods back the public static accessors, with a protected constructor taking a component name.

`org.apache.hadoop.util.bloom.BloomFilter` extends `Filter` with constructors for deserialization and configured vector size/hash count/hash type. It supports `add(Key)`, logical `and`, `or`, `xor`, `not`, `membershipTest(Key)`, `toString()`, `getVectorSize()`, and `Writable` `write(DataOutput)`/`readFields(DataInput)`. It is the standard false-positive/no-false-negative bit-vector filter.

`CountingBloomFilter` is a final `Filter` implementation using counters rather than bits. It adds `delete(Key)` and `approximateCount(Key)`. The approximate count contract is constrained by 4-bit bucket behavior: repeated insertion past 15 can overflow and raise error rates, while delete underflow can introduce false negatives.

`DynamicBloomFilter` extends `Filter` with a row-threshold constructor `(vectorSize, nbHash, hashType, nr)`. It grows by adding rows when the current row reaches the configured key threshold. It supports the same logical operations and `Writable` serialization as the other filters.

`HashFunction` wraps repeated hashing for Bloom filters. Its constructor takes vector size, hash count, and hash type. `hash(Key)` returns an array of positions, and `clear()` resets internal behavior/state.

`RemoveScheme` defines retouched Bloom filter clearing strategies: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`. `RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`; it can record false positives through overloads accepting `Key`, `Collection<Key>`, `List<Key>`, or `Key[]`, then run `selectiveClearing(Key, short)` according to a remove scheme. It also serializes/deserializes its additional retouched-filter state.

`CloseableTaskPoolSubmitter` implements `TaskPool.Submitter` and `Closeable`. It wraps a non-null `ExecutorService`, exposes `getPool()`, submits `Runnable` tasks as `Future`, and shuts the pool down in `close()`.

`FutureIO` is a final utility class for integrating `Future`/`CompletableFuture` work with IOException-oriented Hadoop APIs. `awaitFuture(Future)` and the timeout overload evaluate a future and extract nested failures. `raiseInnerCause(ExecutionException)` and `raiseInnerCause(CompletionException)` always rethrow as the inner `IOException`, inner `RuntimeException`, or an `IOException` wrapper. `unwrapInnerException(Throwable)` recursively handles `IOException`, `UncheckedIOException`, `ExecutionException`, `CompletionException`, `RuntimeException`, and `Error`. `propagateOptions(FSBuilder, Configuration, optionalPrefix, mandatoryPrefix)` and its single-prefix overload map configuration keys into optional or mandatory builder options. `eval(CallableRaisingIOE)` evaluates in the current thread, converting IOExceptions to runtime failures inside a completed/failing `CompletableFuture`.

`RemoteIterators` is a final utility class for `org.apache.hadoop.fs.RemoteIterator` composition. It creates remote iterators from singletons, Java iterators, iterables, and arrays; maps items with `FunctionRaisingIOE`; performs type-casting wrappers; filters lazily; wraps close behavior; materializes to lists or arrays; applies a `ConsumerRaisingIOE` to each element while returning the count; and cleans up iterators. Its Javadoc emphasizes IOStatistics passthrough and debug-only statistics logging, plus close passthrough for iterators that hold remote resources.

The `org.apache.hadoop.tools`, `org.apache.hadoop.tools.protocolPB`, `org.apache.hadoop.tracing`, `org.apache.hadoop.util.curator`, and `org.apache.hadoop.util.hash` package elements in this range are empty placeholders in the JDiff output.

## Control flow and behavior

Service launch flow is explicit. A launcher creates or receives a service, passes command-line tail arguments into `LaunchableService.bindArgs`, initializes the service with the resulting non-null configuration, starts it through the normal `Service` lifecycle, then calls `execute()`. Exceptions from `execute()` are converted into process semantics: existing `ExitException` instances propagate, `ExitCodeProvider` exceptions are wrapped with their own exit code, and other exceptions become `ServiceLaunchException` with `EXIT_EXCEPTION_THROWN`.

Lifecycle state control is guarded by `ServiceStateModel`: callers can check proposed transitions before mutating service state, and invalid transitions are converted from boolean checks into thrown exceptions by `checkStateTransition`.

Command execution through `Shell` follows a template-method pattern. Subclasses describe commands through `getExecString()` and parse stdout through `parseExecResult(BufferedReader)`. The base class decides whether a run is needed based on the minimum interval, constructs and starts a process, merges stderr if configured, tracks the process and waiting thread, records exit code/timeout state, and exposes platform-specific command builders for common Hadoop needs.

Tool execution flows through `ToolRunner`: generic Hadoop options are parsed into the configuration before `Tool.run(String[])` sees the remaining command-specific arguments. This keeps tool implementations focused on application options while preserving standard `-conf`, `-D`, filesystem, jobtracker, and related generic behavior.

Shutdown behavior is centralized in `ShutdownHookManager`. Instead of relying on JVM hook ordering, Hadoop components register hooks with numeric priorities and optional timeouts. During JVM shutdown, the manager runs hooks in priority order, enforcing configured/default time budgets.

Bloom filter behavior is hash-driven. `HashFunction.hash(Key)` calculates vector positions; filters mutate bit vectors, counter vectors, or dynamic rows on `add`; membership checks require all associated positions to be present/non-zero. Logical operations combine compatible filters. Retouched filters collect known false positives and selectively clear positions, accepting a trade-off between reducing false positives and possibly introducing false negatives.

Future and iterator utilities make asynchronous and remote-listing code fit Hadoop's checked-exception style. `FutureIO.awaitFuture` blocks until success/failure/timeout and unwraps nested IO-related causes. `RemoteIterators` adapters defer mapping and filtering to `hasNext()`/`next()` time, propagate `IOException`, and optionally preserve close/statistics behavior through wrapper chains.

## State and persistence behavior

Most state in this chunk is process-local support state rather than distributed filesystem data. Service launch classes manage lifecycle state through `Service` and convert exceptions to process exit status. `HadoopUncaughtExceptionHandler` affects JVM-global uncaught-exception behavior when installed.

`ApplicationClassLoader` maintains classpath URLs and parent/system-class policy. This state influences class identity and resource resolution for the lifetime of the classloader, which is significant in long-running daemons or application containers.

`OperationDuration` stores start and finish timestamps; `DurationInfo` adds log text and log-level behavior. `Shell` stores environment overrides, working directory, current `Process`, timeout flag, exit code, waiting thread, minimum run interval, and whether parent environment is inherited. `ShutdownHookManager` holds a registry of hooks, priorities, and per-hook timeout metadata until shutdown or explicit removal/clear.

`StringInterner` state differs by mode: strong interning retains representatives and can grow memory usage, while weak/standard interning depends on JVM intern table behavior. `ReflectionUtils` may cache constructor/reflection data in implementation, although this XML chunk only exposes the API.

The Bloom filters explicitly persist through Hadoop `Writable` methods. `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` expose zero-argument constructors for `readFields` and serialize their filter vectors/counters/rows and parameters to `DataOutput`. Their state is probabilistic and lossy by design: serialized filters preserve the membership approximation, not the original set.

`FutureIO` and `RemoteIterators` are stateless utility classes from the public API perspective. `CloseableTaskPoolSubmitter` owns an `ExecutorService` lifecycle and can stop accepting/running tasks when `close()` shuts the pool down.

`VersionInfo` reads build-time metadata packaged with Hadoop components. `SysInfo` implementations surface operating-system counters that are external and time-varying rather than persisted by Hadoop.

## Dependencies and integration points

The service launcher APIs integrate with `org.apache.hadoop.service.Service`, `AbstractService`, `Configuration`, `ExitUtil.ExitException`, `ExitCodeProvider`, and process exit handling. They are intended for command-line entry points and service daemons.

The utility layer depends on core Java APIs including `URLClassLoader`, `MalformedURLException`, `Logger`/SLF4J, commons logging, `AutoCloseable`, `Checksum`, `ThreadMXBean`-style diagnostics by implication, `PrintStream`, `Process`, `File`, `BufferedReader`, `TimeUnit`, `Duration`, `DataInput`, `DataOutput`, `IOException`, and `InterruptedIOException`. Hadoop-specific dependencies include `Configuration`, `Configurable`, `Writable`, `GenericOptionsParser`, `CommonConfigurationKeysPublic`, and filesystem-oriented callers that rely on shell commands for permissions, ownership, symlinks, and platform utilities such as `winutils`.

`Shell` is deeply platform-integrated. It depends on OS detection booleans and command formats for Unix-like systems, Windows, Solaris, macOS, FreeBSD, Linux, PowerPC 64-bit, setsid availability, environment variable syntax, Hadoop home resolution, and Windows command length limits.

`Tool`/`ToolRunner` are integration points for nearly every Hadoop CLI application. They bridge generic Hadoop options, user configuration resources, and application-specific command parsing.

Bloom filters depend on `org.apache.hadoop.util.bloom.Filter`, `Key`, `org.apache.hadoop.util.hash.Hash` hash types, `Writable` serialization, and Java collection types for false-positive lists. They can be used by distributed cache, web cache, network, or filesystem metadata code that needs compact approximate membership.

The functional helpers integrate with `ExecutorService`, `Future`, `CompletableFuture`, `ExecutionException`, `CompletionException`, `TimeoutException`, `UncheckedIOException`, Hadoop `FSBuilder`, `Configuration`, `RemoteIterator`, `IOStatisticsSource` by documentation, and Hadoop functional interfaces such as `CallableRaisingIOE`, `FunctionRaisingIOE`, and `ConsumerRaisingIOE`.

## Risks and edge cases

Service lifecycle code must treat same-state proposals carefully: `isValidStateTransition` does not validate `current == proposed`, so callers need a separate idempotence policy if repeated lifecycle calls are allowed. Incorrect exception mapping in a launcher can hide meaningful application exit codes.

`HadoopUncaughtExceptionHandler` intentionally exits on `Error`. Tests and embedding environments must not install it casually where process termination is unacceptable.

`LaunchableService.bindArgs` can replace the configuration before initialization. Implementations that return `null`, mutate shared configurations unexpectedly, or forget to instantiate a needed subclass such as a YARN-specific configuration can fail later during `init`.

Exit codes are a public compatibility surface. Reusing HTTP-like values inconsistently, or returning codes outside the documented single-byte-friendly ranges, can break scripts and service managers.

Application classloader isolation is sensitive to `SYSTEM_CLASSES_DEFAULT` and `isSystemClass` pattern ordering. Loading Hadoop or dependency classes on the wrong side can produce class identity conflicts, linkage errors, or resource shadowing.

`Shell` APIs are inherently platform fragile. Windows command-line length, `winutils` discovery, bash availability, setsid support, command quoting, inherited environment, and non-sorted or locale-specific command output can all affect behavior. Long-running or timed-out processes must be destroyed and not left tracked in `getAllShells()`.

`ShutdownHookManager` hooks with the same priority run in nondeterministic order. Hooks must tolerate partial shutdown, timeout termination, and dependencies already being stopped. Clearing hooks is dangerous outside tests.

Strong string interning can retain unbounded input. Code should avoid strong-interning high-cardinality or user-controlled strings.

`ReflectionUtils.copy` and `cloneWritableInto` rely on correct `Writable` serialization. Broken `write`/`readFields` implementations can corrupt destination objects, and reflection-based construction may fail for missing no-argument constructors or inaccessible classes.

CRC implementations must exactly match expected polynomials and byte ordering. Any optimization or substitution needs cross-checks against `java.util.zip.CRC32` and known CRC32-C vectors.

`SysInfo` metrics may be unavailable, OS-specific, or sampled at different times. Callers must handle `-1`, unsupported OS exceptions, and counter wrap/reset behavior.

Counting Bloom filters can overflow counters above 15 repeated inserts and underflow after deletes, increasing false positives or introducing false negatives. Dynamic filters must only combine compatible layouts. Retouched filters deliberately allow false negatives after selective clearing, which violates the standard Bloom filter guarantee.

`FutureIO.unwrapInnerException` rethrows `RuntimeException` and `Error` immediately. Callers expecting only `IOException` must account for unchecked propagation. Timeout handling in `awaitFuture` does not imply cancellation unless callers do it separately.

`RemoteIterators.foreach` explicitly does not close the iterator afterwards. Callers must invoke `cleanupRemoteIterator` or use close-aware wrappers when remote listings hold connections or file handles. Filtering in `hasNext()` can perform remote IO earlier than callers expect.

## Test signals

Useful test coverage for code using or changing these APIs should include:

- Service lifecycle tests for valid and invalid `Service.STATE` transitions, same-state idempotence behavior, `checkStateTransition` exception text, and launch flow order: `bindArgs`, `init`, `start`, `execute`.
- Launcher exception tests covering raw `ExitUtil.ExitException`, arbitrary `ExitCodeProvider`, generic checked exceptions, runtime exceptions, formatted `ServiceLaunchException` constructors, and expected process exit codes.
- Uncaught exception handler tests that distinguish ordinary exceptions from `Error` without terminating the test JVM directly, using injectable or intercepted exit behavior.
- Classloader tests for application-first loading, parent/system-class delegation, negative and positive system class patterns, resource lookup, malformed classpath entries, and dependency shadowing.
- Duration/logging tests for `OperationDuration.finished()`, `value()`, `asDuration()`, `humanTime()`, and `DurationInfo.close()` at info versus debug.
- Checksum tests using known CRC32 and CRC32-C vectors, byte-array offsets, single-byte updates, reset behavior, and comparison with JDK CRC32 where applicable.
- Reflection tests for `newInstance` with `Configurable` classes, constructor caching behavior, thread dump throttling, serialization copy compatibility, and inherited field/method discovery.
- Shell tests across mocked or isolated OS modes for command construction, Windows command length rejection, script extension selection, Hadoop-home/bin qualification, winutils absence, environment and working-directory propagation, timeout handling, process cleanup, and static `execCommand` error propagation.
- Shutdown hook tests for priority ordering, equal-priority nondeterminism tolerance, hook removal, timeout enforcement, shutdown-in-progress reporting, and test-only clearing.
- ToolRunner tests for generic option parsing, configuration injection, null configuration behavior, usage printing, prompt yes/no parsing, and preservation of application-specific arguments.
- VersionInfo tests that packaged build metadata is readable and `main` prints fields without null-sensitive failures.
- Bloom filter tests for serialization round trips, membership false-positive/no-false-negative expectations for standard filters, logical operation compatibility checks, counting delete and approximate count behavior, overflow/underflow edges, dynamic row growth, and retouched selective-clearing schemes.
- FutureIO tests for successful futures, interrupted futures mapped to `InterruptedIOException`, nested `ExecutionException`/`CompletionException`/`UncheckedIOException` unwrapping, runtime/error propagation, timeout behavior, and `FSBuilder` optional versus mandatory option propagation from configuration prefixes.
- RemoteIterators tests for singleton/iterator/iterable/array adapters, lazy mapping/filtering, IOException propagation from source and callbacks, close passthrough, `toList`/`toArray` materialization, returned count from `foreach`, debug-only IOStatistics paths, and explicit cleanup of closeable remote iterators.
