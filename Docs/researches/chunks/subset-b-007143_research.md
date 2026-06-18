# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 36777-40847

Chunk id: `subset-b-007143`
Source: `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml`
Line range: 36777-40847

## Purpose

This chunk is the final public API slice of Hadoop Common 2.10.0's generated JDiff XML. It crosses several packages: web delegation-token authentication, the `org.apache.hadoop.service` lifecycle framework, launchable-service exit contracts, tracing administration RPC metadata, common utility APIs, and the `org.apache.hadoop.util.bloom` filter family. The XML records public/protected API shape, inheritance, method signatures, checked exceptions, deprecation text, and Javadoc, not implementation bodies.

The central themes are reusable infrastructure APIs: HTTP delegation-token acquisition/renewal/cancelation; consistent service state transitions and listener notifications; process-launch error mapping; isolated class loading; checksum, reflection, shell, shutdown, system-info, generic CLI, and version helpers; and serializable Bloom-filter data structures. These APIs are consumed throughout Hadoop daemons, command-line tools, IPC protocols, and clients.

## Important APIs, Types, and Functions

- `DelegationTokenAuthenticatedURL.Token` extends `AuthenticatedURL.Token` and adds `getDelegationToken()` / `setDelegationToken(Token)` for carrying a Hadoop delegation token alongside the HTTP authentication cookie/token.
- `DelegationTokenAuthenticator` implements `Authenticator` and wraps another authenticator with delegation-token operations: `authenticate(URL, AuthenticatedURL.Token)`, `getDelegationToken(...)`, `renewDelegationToken(...)`, and `cancelDelegationToken(...)`. Overloads support a `doAsUser` proxy user.
- `KerberosDelegationTokenAuthenticator` and `PseudoDelegationTokenAuthenticator` specialize `DelegationTokenAuthenticator` for SPNEGO with pseudo-auth fallback and simple/pseudo authentication based on `UserGroupInformation#getCurrentUser()`.
- Delegation token constants include `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`, defining the HTTP query/header/JSON protocol vocabulary.
- `Service` is the lifecycle interface. It extends `Closeable` and defines `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, state/config/name/start-time accessors, failure accessors, `waitForServiceToStop(long)`, lifecycle history, and blocker reporting.
- `AbstractService` is the base implementation for `Service`. It exposes final or protected lifecycle scaffolding around `serviceInit(Configuration)`, `serviceStart()`, and `serviceStop()`, plus `noteFailure(Exception)`, global listeners, lifecycle history, blocker mutation, and failure-state capture.
- `CompositeService` extends `AbstractService` to manage child services with `addService(Service)`, `addIfService(Object)`, `removeService(Service)`, `getServices()`, and lifecycle methods that cascade to children.
- `LifecycleEvent` is a serializable state-transition record with public `time` and `state` fields.
- `LoggingStateChangeListener` implements `ServiceStateChangeListener` and logs state changes through either a supplied SLF4J logger or the class logger.
- `ServiceOperations` provides static cleanup helpers: `stop(Service)` and `stopQuietly(...)` overloads for no-op/null-tolerant shutdown with Commons Logging or SLF4J warning paths.
- `ServiceStateException` is a `RuntimeException` and `ExitCodeProvider` with constructors that derive or override launcher exit codes and static `convert(...)` helpers for wrapping arbitrary `Throwable`s.
- `ServiceStateModel` tracks valid service state transitions with `enterState(STATE)`, `checkStateTransition(...)`, `isValidStateTransition(...)`, `ensureCurrentState(...)`, and `isInState(...)`.
- `LaunchableService` extends `Service` for command-line launched services. `bindArgs(Configuration, List)` can rewrite configuration before init, and `execute()` returns the launched process exit code after start.
- `AbstractLaunchableService` gives default launchable behavior: debug-log arguments, return the provided configuration, and treat `execute()` as success.
- `HadoopUncaughtExceptionHandler` is a JVM default uncaught-exception handler. Its public contract distinguishes standard exceptions from `Error`s, with `Error` causing process shutdown/exit instead of attempting clean recovery.
- `LauncherExitCodes` defines shared integer exit codes for success, generic failure, interrupted execution, argument/config/auth/connectivity problems, service-side failures, unsupported versions, service creation, and lifecycle exceptions.
- `ServiceLaunchException` extends `ExitUtil.ExitException`, implements `ExitCodeProvider` and `LauncherExitCodes`, and supports explicit, cause-based, and formatted exception construction.
- `SpanReceiverInfo`, `SpanReceiverInfoBuilder`, `TraceAdminProtocol`, and `TraceAdminProtocolPB` define tracing administration metadata and RPC contracts for listing, adding, and removing span receivers.
- `ApplicationClassLoader` extends `URLClassLoader` and implements application-first loading except for configured system classes. Constructors accept URL arrays or classpath strings, and `isSystemClass(String, List)` applies positive/negative class/resource patterns.
- `IPList` is a membership predicate for IP address allow/deny style checks.
- `Progressable` is the framework callback for long-running operations to signal liveness and avoid timeouts.
- `PureJavaCrc32` and `PureJavaCrc32C` implement `java.util.zip.Checksum` with pure-Java CRC32 and CRC32C algorithms, exposing `update(...)`, `reset()`, and `getValue()`.
- `ReflectionUtils` provides configuration injection, reflective construction, thread dump logging/printing, Writable copy/clone helpers, and inherited-field/method enumeration.
- `Shell` is an abstract command execution base with OS-specific command builders, Hadoop home/bin resolution, winutils resolution, environment and working-directory setters, throttled `run()`, abstract `getExecString()` / `parseExecResult(BufferedReader)`, process/exit/timeout inspection, static `execCommand(...)` helpers, global shell-process destruction, and memory-lock limit parsing.
- `ShutdownHookManager` is a priority-ordered singleton manager for JVM shutdown hooks, including optional per-hook timeout and default timeout integration with Hadoop common configuration.
- `StringInterner` provides strong and weak string interning and in-place array interning.
- `SysInfo` is an abstract host resource metrics provider with factory `newInstance()` and methods for memory, processor/core count, CPU frequency/time/usage, vcores, network bytes, and storage bytes.
- `Tool` and `ToolRunner` define Hadoop's generic command-line tool contract. `Tool` extends `Configurable`; `ToolRunner` parses generic Hadoop options into a `Configuration`, injects it into the `Tool`, runs custom arguments, prints generic usage, and supports interactive yes/no confirmation.
- `VersionInfo` exposes build metadata: version, revision, branch, date, user, URL, source checksum, build version, protoc version, and `main(String[])`.
- `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` expose probabilistic set-membership filters. All have serialization constructors and `write(DataOutput)` / `readFields(DataInput)`. Common operations include `add(Key)`, `membershipTest(Key)`, boolean filter operations `and`, `or`, `xor`, `not`, and `toString()`.
- `CountingBloomFilter` adds `delete(Key)` and `approximateCount(Key)`.
- `DynamicBloomFilter` adds a constructor parameter `nr`, the threshold for maximum keys per dynamic row.
- `HashFunction` maps a `Key` to multiple integer positions with configured maximum value, number of hash functions, and hash type.
- `RemoveScheme` defines retouched Bloom-filter clearing constants: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` adds false-positive registration overloads for a single `Key`, `Collection`, `List`, and `Key[]`, plus `selectiveClearing(Key, short)`.

## Control Flow

The delegation-token web flow is represented as an authenticated HTTP sequence. A `DelegationTokenAuthenticatedURL.Token` can hold both normal HTTP authentication state and a Hadoop delegation token. `DelegationTokenAuthenticator.authenticate()` authenticates a URL using the configured authenticator. `getDelegationToken()` and `renewDelegationToken()` require normal authentication and talk to HTTP/S endpoints using the delegation-token operation parameters and JSON fields. `cancelDelegationToken()` explicitly does not require authentication by the configured authenticator, so the token itself and endpoint authorization are the effective control inputs. The Kerberos authenticator can fall back to pseudo authentication when a server does not trigger SPNEGO.

The service lifecycle flow is the public contract for daemon components. A `Service` starts in `NOTINITED`, moves through `init(Configuration)` to `INITED`, then through `start()` to `STARTED`, and eventually through `stop()`/`close()` to `STOPPED`. `AbstractService` wraps these transitions, records lifecycle events, calls implementation hooks exactly once, notifies listeners, captures the first failure, and exposes `waitForServiceToStop(long)` for coordination. `ServiceStateModel` enforces valid transitions, and `ServiceStateException` converts failures into runtime exceptions with launcher-compatible exit codes. `CompositeService` adds parent/child orchestration by initializing, starting, and stopping managed child services around the parent lifecycle.

Launchable services add a command-line control path. A service launcher calls `bindArgs(Configuration, List)` before `init`, so a service can replace or augment configuration after launcher-specific arguments have been stripped. After `start()`, the launcher calls `execute()` and uses its return value as the process exit code. Exceptions from `execute()` are classified: explicit `ExitUtil.ExitException`s propagate, `ExitCodeProvider` exceptions become `ServiceLaunchException`s with their code, and other exceptions become `EXIT_EXCEPTION_THROWN`.

The tracing protocol flow is administrative RPC: clients list currently active span receivers, add a receiver from a `SpanReceiverInfo` built by `SpanReceiverInfoBuilder`, or remove a receiver by ID. The PB interface binds this API to the generated blocking protobuf service and Hadoop `VersionedProtocol`.

Utility APIs provide several independent flows. `ApplicationClassLoader` attempts application class/resource loading before parent delegation unless `isSystemClass()` says a class/resource belongs to JDK, Hadoop, or configured system namespaces. `ReflectionUtils.newInstance()` creates objects and injects `Configuration` when appropriate, while `copy()` / `cloneWritableInto()` use Writable serialization as the copy path. `Shell.run()` gates actual process execution by the configured minimum interval, builds the command via `getExecString()`, captures/feeds output to `parseExecResult()`, tracks process/exit/timeout state, and supports static one-shot command execution. `ShutdownHookManager` registers one JVM hook and then runs registered hooks in descending priority with configured timeout handling.

The generic CLI flow is `ToolRunner.run(conf, tool, args)`: parse generic Hadoop options, update the configuration, set it into the `Tool`, then invoke `Tool.run(String[])` with application-specific arguments. `ToolRunner.run(tool, args)` reuses the tool's existing configuration. `confirmPrompt()` is the interactive branch for user confirmation.

Bloom-filter flow is probabilistic and serializable. Construction fixes vector size, hash count, and hash implementation. `HashFunction.hash(Key)` maps each key to several vector positions. `add(Key)` mutates the underlying vector/matrix/counter structure, `membershipTest(Key)` checks all derived positions, boolean operations combine compatible filters, and `write`/`readFields` persist/restore filter state. `CountingBloomFilter.delete()` decrements counters and `approximateCount()` reports the minimum/derived count for a key. `DynamicBloomFilter.add()` targets an active row until the `nr` threshold is reached, then grows by adding a row. `RetouchedBloomFilter` collects known false positives and `selectiveClearing()` clears selected bits according to the chosen `RemoveScheme`.

## State and Persistence Behavior

- This source is generated API XML; it records public contracts, not private fields or storage layouts. State behavior below is inferred from signatures and Javadoc in this chunk.
- Delegation token state is stored client-side in `DelegationTokenAuthenticatedURL.Token` and server-side through HTTP/S delegation-token endpoints. Operation names, token values, renewers, services, and JSON fields are serialized through query parameters, headers, and JSON responses.
- `AuthenticatedURL` instances are documented as not thread-safe, and the delegation-token URL subclass inherits that constraint.
- `AbstractService` maintains service name, configuration, current state, start time, lifecycle history, failure cause, failure state, listeners, global listeners, and blocker map. Some getters are synchronized in the API (`getFailureCause`, `getFailureState`, `getLifecycleHistory`), while lifecycle hooks are documented as protected from re-entrancy by the wrapper methods.
- `LifecycleEvent` is explicitly `Serializable` and stores local transition time plus entered state, making lifecycle history snapshot-friendly.
- `CompositeService` owns an in-memory list of child `Service`s. `getServices()` returns a cloned snapshot so concurrent additions are not observed by that call.
- `ServiceStateModel.enterState()` is synchronized and returns the original state, making it the visible state-transition mutation point in the public API.
- `LauncherExitCodes` and `ServiceLaunchException` define process-exit state rather than persisted state; the exception carries an exit code used by launchers.
- `SpanReceiverInfoBuilder` accumulates receiver class name and configuration key/value pairs before producing an immutable-ish `SpanReceiverInfo` for RPC transport.
- `ApplicationClassLoader` persists classpath and system-class pattern configuration in memory for the lifetime of the loader.
- `Shell` stores process execution state: timeout interval, parent-environment inheritance flag, environment map, working directory, current `Process`, exit code, waiting thread, timeout flag, and a static set of live shell instances available through `getAllShells()` / `destroyAllShellProcesses()`.
- `Shell` resolves Hadoop home and qualified binary paths from system property `hadoop.home.dir`, `HADOOP_HOME`, platform-specific bin paths, and `winutils`; callers are warned to cache qualified binary results because path existence is checked.
- `ShutdownHookManager` is a singleton in-memory registry of `Runnable` hooks with priority and optional timeout. Hook execution order is deterministic by priority, but hooks with the same priority are non-deterministic.
- `StringInterner.strongIntern()` deliberately retains a strong reference; `weakIntern()` uses weak/interner behavior that avoids preventing GC.
- `VersionInfo` exposes build-time metadata, likely loaded from component-specific build properties through the protected constructor's component argument.
- Bloom filters persist their probabilistic vector/counter/matrix state through `DataOutput` and `DataInput`. Default constructors are explicitly for `readFields()`. Counting filters store small counters, dynamic filters store multiple Bloom rows and occupancy thresholds, and retouched filters store base Bloom data plus false-positive clearing metadata as implemented by the concrete class.

## Dependencies and Integration Points

- Security/authentication: `AuthenticatedURL`, `AuthenticatedURL.Token`, `Authenticator`, `ConnectionConfigurator`, `AuthenticationException`, `UserGroupInformation`, and `org.apache.hadoop.security.token.Token`.
- HTTP delegation-token protocol: HTTP/S URLs, query parameters, headers, JSON response names, renewer/service fields, and optional `doAsUser` proxy-user semantics.
- Configuration and lifecycle: `org.apache.hadoop.conf.Configuration`, service state enum `Service.STATE`, `Closeable`, listeners, SLF4J, Commons Logging, and Hadoop `ExitCodeProvider` / `ExitUtil`.
- Launching: daemon main methods, service launchers, JVM uncaught exception handling, process exit codes, command-line argument lists, and shutdown policy.
- Tracing and IPC: span receiver metadata, Hadoop tracing protobuf service `TraceAdminPB.TraceAdminService.BlockingInterface`, `VersionedProtocol`, and `IOException` for RPC failures.
- Class loading: `URLClassLoader`, classpath strings, `MalformedURLException`, parent classloader delegation, and system class pattern configuration.
- OS and process utilities: Java `Process`, command arrays, environment maps, working directories, Unix command names, Windows `winutils`, command-line length limits, script extension selection, `kill -0`/signal equivalents, `bash` detection, and memory-lock/ulimit parsing.
- Checksums and serialization: `java.util.zip.Checksum`, byte-array update APIs, Hadoop `Writable`, `DataInput`, `DataOutput`, and in-memory serialization buffers.
- Diagnostics: thread dumps through `ThreadMXBean`-style mechanisms behind `ReflectionUtils`, loggers, and throttled stack logging intervals.
- Resource monitoring: OS-specific `SysInfo` implementations for memory, CPU, network, and storage counters.
- Generic command-line tools: `Configurable`, `GenericOptionsParser`, Hadoop common generic options, `PrintStream`, and interactive stdin responses.
- Bloom filters: `org.apache.hadoop.util.bloom.Key`, `Filter`, `BloomFilter`, `HashFunction`, `org.apache.hadoop.util.hash.Hash`, and probabilistic filter theory referenced by the public docs.

## Risks and Edge Cases

- Because this is JDiff XML, it cannot show private synchronization, validation, serialization format details, or actual exception paths. Final whole-file research should treat implementation details as unresolved unless covered in source `.java` chunks.
- `AuthenticatedURL` instances are explicitly not thread-safe. Reusing a `DelegationTokenAuthenticatedURL` or its token across threads can corrupt or expose authentication state.
- Delegation token cancelation is documented as not requiring configured authenticator authentication. Endpoint authorization and token secrecy are therefore critical, especially with `doAsUser`.
- Proxy-user overloads (`doAsUser`) can create security regressions if endpoint implementations fail to enforce proxy-user ACLs consistently for get, renew, and cancel.
- Pseudo delegation-token authentication trusts the current user value, so deployment context and transport security determine whether this is acceptable.
- Service listener callbacks are invoked after state change but while the service is in a synchronized section. The docs warn that long-lived listener work delays transitions and listener-created threads calling back into the service can deadlock.
- `Service.stop()` is required to work from partially initialized states. Implementations that assume all fields are initialized can fail during cleanup after `init()` or `start()` failures.
- `ServiceOperations.stop(Service)` is explicitly not thread-safe because it checks state before the operation starts.
- Lifecycle failure state captures the first failure. Later failures during stop may be logged but can be hidden from callers using only `getFailureCause()`.
- `CompositeService` shutdown policy can stop all children or only started children. Child services with fragile `stop()` implementations may behave differently depending on `STOP_ONLY_STARTED_SERVICES`.
- `HadoopUncaughtExceptionHandler` exits on `Error`, reflecting that the process may be unsafe. Tests must avoid masking `Error` paths as recoverable.
- `LauncherExitCodes` deliberately compress HTTP-like error categories into one-byte-ish command exit codes. Callers should not confuse them with actual HTTP status codes.
- `ApplicationClassLoader.isSystemClass()` depends on positive and negative pattern matching. A bad pattern can leak classes into the parent loader or shadow Hadoop/JDK classes, producing linkage conflicts.
- `ReflectionUtils.copy()` destroys/reuses `dst` through serialization. Mutable Writables with transient fields or incompatible serialization versions can lose state.
- `ReflectionUtils` field/method enumeration across superclasses can surface private or synthetic members depending on implementation details; callers need filtering.
- `Shell.checkWindowsCommandLineLength()` expects command parts already include delimiters; callers that omit delimiter lengths may undercount.
- `Shell.WINUTILS` is deprecated because it can be null. Callers should use exception-raising getters to avoid latent null handling bugs.
- `Shell.destroyAllShellProcesses()` is global to all tracked shell instances and can interfere with unrelated in-flight shell commands in the same JVM.
- `Shell` command builders expose OS-specific behavior for groups, permissions, symlinks, signals, and environment-variable syntax; tests must not assume Unix semantics on Windows.
- `ShutdownHookManager` hooks with equal priority run in non-deterministic order. Hook code must not depend on ordering unless priorities differ.
- Shutdown hook timeouts can terminate hooks before cleanup is complete; hooks need idempotent recovery on the next process start.
- `StringInterner.strongIntern()` can retain unbounded distinct values for the life of the JVM.
- `SysInfo.newInstance()` can throw `UnsupportedOperationException` when OS detection fails; resource-monitoring callers need fallback behavior.
- `ToolRunner.confirmPrompt()` parses only yes/y case-insensitively per docs; automation should avoid relying on locale-specific or default-yes behavior.
- Bloom filters intentionally permit false positives. Counting Bloom filters warn that inserting the same key more than 15 times can overflow buckets and materially increase error rate.
- Counting Bloom filter deletes can underflow after deleting keys that were not actually present or after hash collisions, and `approximateCount()` may become lower than the real count with false-negative probability.
- Retouched Bloom filters remove selected false positives at the cost of introducing false negatives, changing the usual Bloom filter no-false-negative guarantee.
- Dynamic Bloom filter growth depends on the `nr` row threshold. Bad sizing can increase memory use or false-positive behavior across rows.

## Test Signals

- Delegation-token tests should cover SPNEGO success, pseudo fallback, unsupported non-HTTP/S URLs, get/renew/cancel with and without `doAsUser`, renewal return time parsing, token storage in `DelegationTokenAuthenticatedURL.Token`, unauthenticated cancel behavior, and `ConnectionConfigurator` propagation.
- Authentication concurrency tests should verify that callers do not share non-thread-safe `AuthenticatedURL` instances across threads or that wrapper code serializes access.
- Service lifecycle tests should cover legal transitions, illegal transition exceptions, null configuration rejection, hook invocation exactly once, failure capture during `serviceInit`/`serviceStart`, stop after partial init, idempotent stop, `close()` delegating to `stop()`, lifecycle history snapshots, blocker add/remove/snapshot behavior, and `waitForServiceToStop(0)` semantics.
- Listener tests should cover local and global listeners, duplicate registration no-op behavior, unregister return values, listener callback order assumptions, and deadlock avoidance when listeners call service APIs.
- Composite service tests should validate child init/start/stop order, failure cleanup, `addIfService()` for non-service objects, `getServices()` snapshot behavior, and `STOP_ONLY_STARTED_SERVICES` policy differences.
- Service exception tests should cover exit-code derivation from nested `ExitCodeProvider`, explicit exit-code constructors, `convert(Throwable)`, and `convert(String, Throwable)` preserving runtime exceptions.
- Launcher tests should cover `bindArgs()` replacing configuration, `execute()` return-code propagation, wrapping of `ExitUtil.ExitException`, `ExitCodeProvider`, and generic exceptions into `ServiceLaunchException`, and uncaught-handler behavior for `Exception` versus `Error`.
- Trace admin tests should cover adding receivers with configuration pairs, listing receiver IDs/classes, removing missing and existing IDs, `IOException` propagation, and PB protocol version compatibility.
- Application classloader tests should cover application-first class loading, resource lookup, positive/negative system-class patterns, parent fallback, malformed classpath strings, and default system classes for Hadoop/JDK resources.
- CRC tests should compare `PureJavaCrc32` with `java.util.zip.CRC32`, compare `PureJavaCrc32C` with known CRC32C vectors, test byte-by-byte versus array updates, reset behavior, offset/length bounds, and many-small-update performance assumptions.
- Reflection tests should cover `Configurable` injection, constructor caching if implemented, Writable copy of mutable objects, thread info logging throttling, inherited fields/methods inclusion, and behavior with abstract classes or inaccessible constructors.
- Shell tests should cover every OS command builder on supported platforms, Windows command length counting, Hadoop home resolution from system property and environment, missing `winutils`, script extension/run command selection, interval-throttled reruns, timeout marking, process destruction, environment/working-directory injection, and global `destroyAllShellProcesses()` isolation.
- Shutdown hook tests should cover priority ordering, same-priority non-determinism tolerance, timeout minimum/defaults, removal/has checks, clear behavior, and `isShutdownInProgress()` during hook execution.
- String interner tests should cover null or empty strings if allowed by implementation, object identity after strong/weak interning, in-place array mutation, and memory retention expectations for high-cardinality input.
- SysInfo tests should cover OS factory selection, unsupported OS failure, unavailable metrics returning documented sentinel values, monotonic cumulative CPU time, and network/storage counter aggregation.
- ToolRunner tests should cover generic option parsing into `Configuration`, preserving application-specific args, null configuration handling, `printGenericCommandUsage()`, exit-code propagation from `Tool.run`, and prompt parsing for yes/no variants.
- VersionInfo tests should cover each static getter, missing build-property fallback behavior, build-version string composition, protoc version reporting, and `main()` output stability.
- Bloom filter tests should cover add/membership, expected false-positive rate bounds, boolean operations with compatible and incompatible filters, serialization round trips, `getVectorSize()`, counting add/delete/approximate count including overflow/underflow scenarios, dynamic row growth at the `nr` threshold, `HashFunction` range bounds and hash count, retouched false-positive registration overloads, each `RemoveScheme`, and selective clearing's introduction of false negatives.

## Cross-Chunk Notes

This chunk begins inside the tail of `DelegationTokenAuthenticatedURL` documentation from the preceding lines and then covers the nested token class and following packages through the end of the JDiff API document. Whole-file synthesis should connect the partial delegation-token URL methods from the previous chunk with the authenticator/token contracts here. It should also treat all implementation internals as external to this XML unless corroborated by corresponding Hadoop Java source research.
