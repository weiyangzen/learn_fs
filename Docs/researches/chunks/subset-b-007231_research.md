# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.3.6.xml lines 37160-40994

## Scope

This chunk is a JDiff public API snapshot for Hadoop Common 3.3.6. It covers the tail of `org.apache.hadoop.service.Service`, service lifecycle helper APIs, the service launcher API, a large part of `org.apache.hadoop.util`, the public Bloom filter APIs, and the beginning of `org.apache.hadoop.util.functional`. The file is API metadata rather than implementation source, so the research below records public contracts, stated behavior, integration surfaces, and risks that downstream source or compatibility work must preserve.

## Purpose

The covered API surface provides common infrastructure used across Hadoop components:

- Service lifecycle state modeling and shutdown helpers for Hadoop daemons and managed services.
- Launchable-service contracts and process exit code conventions.
- General utilities for class loading, duration logging, progress callbacks, CRC implementations, reflection, shell command execution, shutdown hooks, string interning, system resource reporting, generic command-line tools, and build version metadata.
- Probabilistic membership structures in `org.apache.hadoop.util.bloom`.
- Functional helpers for executor lifecycle, future exception unwrapping, FSBuilder option propagation, and `RemoteIterator` transformation/cleanup.

## Important APIs and Types

### `org.apache.hadoop.service`

- `Service` tail methods in this chunk expose lifecycle observation: `getLifecycleHistory()` returns a non-null snapshot list of lifecycle events, and `getBlockers()` returns a snapshotted map of blocker name to description for remote dependencies preventing a service from being live. The preceding `waitForServiceToStop(timeout)` contract notes that a timeout of zero means forever and returns whether the service stopped in time.
- `ServiceOperations` is a final static utility. `stop(Service)` is null-tolerant and skips services that are not in a stoppable state, but explicitly checks state before acting and is not thread safe. Three `stopQuietly(...)` overloads catch and log `Exception` at warning level while returning the caught exception, with overloads for no logger, Apache Commons Logging, and SLF4J.
- `ServiceStateChangeListener.stateChanged(Service)` is a callback invoked after the state transition has already happened, on the initiating thread, while the service is still inside a synchronized section. The XML warns that slow callbacks delay state changes and listener re-entry through another thread can deadlock.
- `ServiceStateException` is a `RuntimeException` and `ExitCodeProvider`. It can derive an exit code from a cause, accept an explicit exit code, or fall back to `LauncherExitCodes.EXIT_SERVICE_LIFECYCLE_EXCEPTION`. Static `convert(...)` helpers wrap non-runtime throwables as `ServiceStateException`.
- `ServiceStateModel` models valid `Service.STATE` transitions. It starts in `NOTINITED` by default or a caller-provided state. `enterState(...)` is synchronized and returns the original state; `getState()`, `isInState(...)`, `ensureCurrentState(...)`, `checkStateTransition(...)`, and `isValidStateTransition(...)` provide transition validation. Same-state proposals are considered non-transitions.

### `org.apache.hadoop.service.launcher`

- `LaunchableService` extends `Service` with launcher-managed execution. `bindArgs(Configuration, List)` is called before `init(Configuration)` and may return a replacement configuration, allowing implementations to switch to richer subclasses such as `YarnConfiguration`. `execute()` is called after `Service.start()`; its return value becomes the process exit code. Exceptions are normalized by launcher semantics: `ExitUtil.ExitException` can pass through, `ExitCodeProvider` exceptions become `ServiceLaunchException` with the provider exit code, and other exceptions map to `EXIT_EXCEPTION_THROWN`.
- `AbstractLaunchableService` extends `AbstractService` and implements `LaunchableService`. Its base `bindArgs` logs arguments at debug and returns the same configuration; its base `execute()` returns success (`0`).
- `HadoopUncaughtExceptionHandler` implements `Thread.UncaughtExceptionHandler`. It is intended for installation through `Thread#setDefaultUncaughtExceptionHandler`. The handler logs simple exceptions and continues, but on `Error` it exits rather than attempting a clean shutdown because process state is unknown.
- `LauncherExitCodes` defines public process exit constants. The documented ranges are `0-10` for general command issues, `30-39` for 3xx-like errors considered application failures, `40-49` for client/CLI/config problems, `50-59` for service-side problems, and `60+` for application-specific errors. Constants include success/fail, client shutdown, task launch failure, interrupted, argument/usage/auth/forbidden/not-found errors, configuration conflicts, exception thrown, unimplemented, service unavailable, unsupported version, service creation failure, and service lifecycle exception.
- `ServiceLaunchException` extends `ExitUtil.ExitException` and implements `ExitCodeProvider` and `LauncherExitCodes`. Constructors accept an exit code plus cause, plain message, formatted message, or cause plus formatted message. Formatted constructors use `String.format` in English locale, and the last argument may become the cause when it is a throwable.

### `org.apache.hadoop.util`

- `ApplicationClassLoader` is a `URLClassLoader` for application isolation. It loads application JAR classes before parent classes except for system classes. `isSystemClass(String, List)` uses positive and negative pattern matching: a name is system only if it matches a positive pattern and no negative pattern. `SYSTEM_CLASSES_DEFAULT` keeps JDK classes, Hadoop classes/resources, and selected third-party classes in the parent/system loader.
- `DurationInfo` extends `OperationDuration` and implements `AutoCloseable`. It logs start/final duration messages at info or debug and is designed for try-with-resources. `OperationDuration` records start and finished times, uses `finished()` to update end time, returns `0` from `value()` until finished, formats as minutes:seconds.millis through `humanTime(long)`, and exposes `asDuration()`.
- `IPList.isIn(String)` is a small membership interface for IP address lists.
- `Progressable.progress()` is the long-running operation heartbeat callback. The contract says clients should explicitly report progress to avoid framework timeouts.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum`. Both expose `getValue()`, `reset()`, `update(byte[], int, int)`, and final `update(int)`. `PureJavaCrc32` uses the standard CRC32 polynomial to avoid JNI overhead on many small checksum operations; `PureJavaCrc32C` uses the CRC32-C/iSCSI polynomial.
- `ReflectionUtils` provides configuration injection, object instantiation, thread-stack diagnostics, writable copying, and reflective field/method enumeration. Key methods are `setConf(Object, Configuration)`, `newInstance(Class, Configuration)`, `setContentionTracing(boolean)`, synchronized `printThreadInfo(...)`, Commons Logging and SLF4J `logThreadInfo(...)`, `copy(Configuration, T, T)`, `cloneWritableInto(Writable, Writable)`, and inherited member collection helpers.
- `Shell` is an abstract base for shell command execution with optional minimum rerun interval and optional stderr redirection. Static helpers build OS-specific group, permission, ownership, symlink, readlink, process-liveness, signal, script-extension, and script-run commands. It locates Hadoop home, qualified Hadoop binaries, and Windows `winutils`, checks Windows command length, checks bash support, and exposes static `execCommand(...)` overloads. Subclasses implement `getExecString()` and `parseExecResult(BufferedReader)`. Instance state includes timeout interval, parent-env inheritance, working directory, environment, process, exit code, waiting thread, and timeout flag. Public constants expose OS detection, command names, regexes, Windows process launch lock, and `WINUTILS` location; misspelled `WINDOWS_MAX_SHELL_LENGHT` and direct `WINUTILS` access are deprecated.
- `ShutdownHookManager` is a final singleton that registers one JVM shutdown hook and runs managed hooks in deterministic priority order, higher priority first. It supports registration with default or explicit timeout, removal, presence checks, shutdown-in-progress checks, and clearing all hooks. Default timeout is driven by `CommonConfigurationKeysPublic.SERVICE_SHUTDOWN_TIMEOUT` with documented minimum/default units.
- `StringInterner` provides `strongIntern`, `weakIntern`, and in-place array interning. The doc says weak interning uses standard `String.intern()` behavior in modern JDKs; strong interning retains a strong reference.
- `SysInfo` is an abstract plugin for OS resource information. `newInstance()` chooses the default OS implementation or throws `UnsupportedOperationException`. Abstract metrics include virtual/physical memory totals and availability, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, virtual cores used, network bytes read/written, and storage bytes read/written. Unavailable percentage-style metrics may return `-1`.
- `Tool` extends `Configurable` and standardizes Hadoop command-line applications: `run(String[])` accepts app-specific arguments after generic options are handled. `ToolRunner` parses generic Hadoop options through `GenericOptionsParser`, updates the tool configuration, runs the tool, prints generic usage, and provides `confirmPrompt(String)` that returns true for `y` or `yes`.
- `VersionInfo` exposes build metadata: version, git revision, branch, compile date/user, repository URL, source checksum, build version, protoc version, compile platform, and `main(String[])`. Protected underscore methods back the public static accessors.

### `org.apache.hadoop.util.bloom`

- `BloomFilter` extends `Filter` and exposes default serialization constructor, parameterized constructor `(vectorSize, nbHash, hashType)`, `add(Key)`, set operations `and`, `or`, `xor`, `not`, `membershipTest(Key)`, `getVectorSize()`, string conversion, and `Writable`-style `write/readFields`. It guarantees no false negatives for inserted keys but can return false positives.
- `CountingBloomFilter` is final and extends `Filter`. It supports add, delete, membership test, set-like operations, serialization, and `approximateCount(Key)`. The count API can behave as an approximate key-to-count map, but the doc warns that inserting the same key more than 15 times overflows associated buckets and increases error rates. Deletes can underflow and introduce false negatives.
- `DynamicBloomFilter` extends `Filter` and adds rows of standard Bloom filters as cardinality grows. Constructor parameters add `nr`, the threshold for maximum keys per row. Add inserts into an active row when one has capacity; otherwise it creates a new row. Membership succeeds when all hash positions are set in one row.
- `HashFunction` is final and maps a `Key` to multiple integer positions using a configured maximum value, number of hashes, and hash type. `clear()` is documented as a no-op.
- `RemoveScheme` defines retouched Bloom filter clearing strategies: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` is final, extends `BloomFilter`, and implements `RemoveScheme`. It records known false positives through overloads accepting a single `Key`, `Collection`, `List`, or `Key[]`, then `selectiveClearing(Key, short)` clears bits according to the selected scheme. The design intentionally trades selected false positives for possible false negatives.

### `org.apache.hadoop.util.functional`

- `CloseableTaskPoolSubmitter` implements `TaskPool.Submitter` and `Closeable` around a non-null `ExecutorService`. `submit(Runnable)` delegates to the pool, `getPool()` exposes it, and `close()` shuts it down.
- `FutureIO` is a final static utility for asynchronous IO. `awaitFuture(Future)` and timed `awaitFuture(Future, long, TimeUnit)` return the result or extract and rethrow nested IO/runtime failures, mapping interruption to `InterruptedIOException` and timed waits to `TimeoutException`. `raiseInnerCause(...)` overloads handle `ExecutionException` and `CompletionException`. `unwrapInnerException(Throwable)` recursively unwraps `UncheckedIOException`, execution/completion wrappers, runtime exceptions, and errors, returning or wrapping an `IOException` while rethrowing runtime/errors. `propagateOptions(...)` copies configuration entries with optional/mandatory prefixes into an `FSBuilder`, converting stripped prefix suffixes into builder options; examples include `fs.example.s3a.option` to `s3a.option` and `fs.example.something` to `something`. `eval(CallableRaisingIOE)` evaluates in the current thread and returns a `CompletableFuture`, converting IOExceptions to runtime failures.
- `RemoteIterators` is a final helper set for `RemoteIterator` composition. It creates remote iterators from singleton, `Iterator`, `Iterable`, and arrays; maps, type-casts, filters, adds close handling, adds halt predicates, creates numeric ranges `[start, excludedFinish)`, materializes to list/array, applies a consumer with `foreach`, and performs cleanup. The APIs preserve or pass through `IOStatisticsSource` where possible and can log IO statistics at debug with zero cost when debug logging is disabled. Cleanup closes closeable iterators and logs statistics when appropriate.

## Control Flow and State Behavior

- Service startup/execution flow is: launcher creates or configures a `LaunchableService`, calls `bindArgs(...)`, passes any returned configuration to `init(...)`, calls `start()`, invokes `execute()`, and maps the return value or thrown exception to a process exit code. Service lifecycle state transitions are guarded by `ServiceStateModel`, with synchronized transition entry and separate validation helpers.
- Service stop helpers are intentionally conservative: null services and already non-stoppable services are ignored. Quiet stop helpers catch only `Exception`, not arbitrary `Throwable`, and are intended for cleanup paths.
- State change listeners execute synchronously inside service state-change locking. This makes callbacks part of the state transition critical path.
- `Shell.run()` control flow is interval-gated. It executes only when the minimum interval has elapsed, then spawns a process from subclass-provided command strings, lets subclasses parse stdout, records exit/timeout state, and supports static global destruction of currently running shell processes.
- `ShutdownHookManager` serializes Hadoop shutdown through one JVM hook. Managed hooks are ordered by priority, with same-priority hooks nondeterministic and timeout enforcement for long-running hooks.
- Bloom filter state is in-memory probabilistic state with `Writable`-style binary serialization. Standard Bloom filters are monotonic unless bitwise operations are applied; counting filters mutate counters on add/delete; dynamic filters append rows as thresholds are reached; retouched filters mutate bits to suppress known false positives.
- `FutureIO` normalizes async control flow by moving checked `IOException` semantics through future/execution wrappers. `RemoteIterators` composes lazy iteration; filtering may happen in `hasNext()` or lazily in `next()` if `hasNext()` is not called.

## Persistence and Compatibility Notes

- This XML is generated public API metadata. It is a compatibility baseline: public names, signatures, visibility, deprecation state, inheritance, exceptions, and documentation are the durable facts.
- `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` expose `write(DataOutput)` and `readFields(DataInput)`, so serialized wire/storage compatibility depends on preserving vector sizes, hash counts/types, counter encodings, dynamic rows, and false-positive metadata layouts in implementation code.
- `VersionInfo` values come from build-time metadata resources/properties rather than runtime mutable state.
- `Service.getLifecycleHistory()` and `getBlockers()` promise snapshots. Implementations should avoid exposing mutable live internal collections.
- `Shell` exposes several public constants and deprecated fields that remain part of binary/source compatibility. The misspelled `WINDOWS_MAX_SHELL_LENGHT` and nullable `WINUTILS` cannot simply be removed without API breakage.

## Dependencies and Integration Points

- Service APIs integrate with `org.apache.hadoop.conf.Configuration`, `AbstractService`, `ExitCodeProvider`, `ExitUtil.ExitException`, `LauncherExitCodes`, Commons Logging, SLF4J, and the general Hadoop shutdown/launcher ecosystem.
- Tool APIs integrate with `Configurable`, `Configured`, `GenericOptionsParser`, command manual generic options, and MapReduce-style jobs in downstream applications.
- `Shell` integrates deeply with OS-specific facilities: Unix commands (`groups`, `id`, `chmod`, `chown`, `ln`, `readlink`, `kill`), Windows command length and `winutils`, script extension/interpreter selection, environment variables, process handles, and Hadoop home/bin discovery.
- `ShutdownHookManager` depends on `CommonConfigurationKeysPublic` shutdown timeout configuration.
- Reflection utilities depend on Hadoop `Writable` serialization and `Configuration` injection patterns.
- Bloom filters depend on `Key`, `Filter`, and `org.apache.hadoop.util.hash.Hash`.
- Functional utilities integrate with `ExecutorService`, `Future`, `CompletableFuture`, `ExecutionException`, `CompletionException`, `UncheckedIOException`, `FSBuilder`, `Configuration`, `RemoteIterator`, `IOStatisticsSource`, and Hadoop IO-statistics logging conventions.

## Risks and Edge Cases

- Listener deadlocks are a first-class risk: `ServiceStateChangeListener` runs while the service is synchronized, so callbacks must avoid slow work and re-entrant service calls through other threads.
- `ServiceOperations.stop(Service)` is not thread safe because it checks state before operating. Concurrent lifecycle changes can race with the stop decision.
- Quiet stop catches `Exception` but not `Throwable`; cleanup paths can still be interrupted by `Error`.
- Launcher exit code behavior is observable process API. Incorrect exception mapping can break scripts and service managers that key off numeric exit codes.
- `HadoopUncaughtExceptionHandler` exits on `Error`; tests and embedding environments must account for process termination behavior.
- `ApplicationClassLoader` system-class pattern errors can either leak Hadoop classes into isolated apps or accidentally shadow core/system classes.
- `Shell` has OS-dependent behavior and external binary dependencies. Windows command length validation, `winutils` discovery, `setsid` availability, environment inheritance, timeout handling, process cleanup, and shell output parsing are all platform-sensitive.
- `ShutdownHookManager` same-priority order is nondeterministic. Hooks should not depend on ordering unless priorities differ.
- `OperationDuration.value()` returns zero until `finished()` is called; callers that expect live elapsed time can misreport.
- `CountingBloomFilter` overflows after repeated inserts of the same key beyond the documented counter capacity and deletes can underflow, increasing false positives or causing false negatives.
- `RetouchedBloomFilter` explicitly accepts false negatives as the cost of selective false-positive removal; callers needing strict no-false-negative semantics should not substitute it for standard `BloomFilter`.
- `FutureIO.unwrapInnerException(...)` rethrows runtime exceptions and errors. Callers expecting only `IOException` from all async failures must handle those paths separately.
- `RemoteIterators.foreach(...)` does not close the iterator afterward. Callers must invoke cleanup or use closeable wrapping when iterators hold remote connections/file handles.

## Test Signals

- Service lifecycle tests should cover valid and invalid `ServiceStateModel` transitions, same-state non-transitions, `ensureCurrentState` failures, snapshot immutability/non-nullness for lifecycle history/blockers, listener invocation ordering, and deadlock-avoidance expectations.
- Stop helper tests should cover null services, services in non-stoppable states, exception-return behavior from `stopQuietly`, and logging overloads for Commons Logging and SLF4J.
- Launcher tests should exercise `bindArgs` configuration replacement before init, `execute` return-code propagation, exception-to-exit-code mapping for `ExitException`, `ExitCodeProvider`, generic exceptions, and formatted `ServiceLaunchException` causes.
- Utility tests should validate `ApplicationClassLoader.isSystemClass` positive/negative pattern behavior, duration formatting and close-time logging, progress callback use in long-running operations, CRC32/CRC32C compatibility with known vectors, reflection copy/config injection, and `VersionInfo` metadata reads.
- Shell tests need OS-specific coverage for command construction, script extension selection, Hadoop home/bin discovery, Windows path/length/winutils behavior, timeout state, process cleanup, environment/working-directory propagation, and parsing failures.
- Shutdown hook tests should verify priority ordering, same-priority nondeterminism tolerance, explicit/default timeout handling, removal, `hasShutdownHook`, and shutdown-in-progress state.
- Bloom filter tests should round-trip serialization, verify no false negatives for standard Bloom inserts, confirm expected false-positive behavior statistically, cover counting add/delete/approximate count with overflow/underflow boundaries, dynamic row growth at `nr`, hash position bounds, and retouched selective-clearing tradeoffs.
- Functional tests should cover future success, interruption, timeout, nested `ExecutionException`/`CompletionException`/`UncheckedIOException` unwrapping, runtime/error propagation, FSBuilder optional/mandatory option propagation and suffix conversion, iterator mapping/filtering/lazy behavior, close passthrough, halt predicate termination, range boundaries, `toList`/`toArray`, `foreach` count return, and IO-statistics logging only when debug is enabled.
