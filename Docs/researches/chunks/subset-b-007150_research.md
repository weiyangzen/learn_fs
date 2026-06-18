# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.2.xml lines 36847-41055

## Purpose

This chunk is the tail of the Hadoop Common 2.10.2 JDiff API description. It documents public API signatures and Javadocs, not implementation bodies. The covered surface spans web delegation-token authentication, the service lifecycle framework, service launch exit-code conventions, tracing administration protocols, general utility classes, system process helpers, build metadata, and Bloom filter data structures.

The XML is consumed as generated compatibility/API metadata. Its value is in the stable public contracts: method names, visibility, return types, parameter types, exceptions, fields, inheritance, implemented interfaces, and deprecation state.

## API Inventory

### `org.apache.hadoop.security.token.delegation.web` tail

- The chunk begins inside `DelegationTokenAuthenticatedURL` methods for `getDelegationToken`, `renewDelegationToken`, and `cancelDelegationToken`, plus `openConnection` behavior. These APIs authenticate HTTP/S requests using an `AuthenticatedURL.Token`, optionally prefer a delegation token over the configured `Authenticator`, and support proxy-user execution via `doAs`/`doAsUser`.
- `DelegationTokenAuthenticatedURL.Token` at line 37011 extends `AuthenticatedURL.Token` and stores a Hadoop `org.apache.hadoop.security.token.Token` with `getDelegationToken()` and `setDelegationToken(Token)`.
- `DelegationTokenAuthenticator` at line 37036 wraps an `org.apache.hadoop.security.authentication.client.Authenticator` with delegation-token operations. It implements `Authenticator`, exposes `setConnectionConfigurator`, `authenticate`, token get/renew/cancel overloads, and protocol constants including `OP_PARAM`, `DELEGATION_TOKEN_HEADER`, `DELEGATION_PARAM`, `TOKEN_PARAM`, `RENEWER_PARAM`, `SERVICE_PARAM`, `DELEGATION_TOKEN_JSON`, `DELEGATION_TOKEN_URL_STRING_JSON`, and `RENEW_DELEGATION_TOKEN_JSON`.
- `KerberosDelegationTokenAuthenticator` at line 37238 supplies Kerberos SPNEGO support and defaults to a fallback-capable delegation-token authenticator.
- `PseudoDelegationTokenAuthenticator` at line 37257 supplies Hadoop simple/pseudo authentication support for delegation tokens.

### `org.apache.hadoop.service`

- `AbstractService` at line 37279 is the base implementation for Hadoop services. It owns the lifecycle state machine through `init(Configuration)`, `start()`, `stop()`, `close()`, protected hooks `serviceInit`, `serviceStart`, `serviceStop`, failure recording through `noteFailure(Throwable)`, stop waiting, listener registration, service naming/config/start time, lifecycle history snapshots, and blocker tracking through `putBlocker`, `removeBlocker`, and `getBlockers`.
- `CompositeService` at line 37541 composes child `Service` instances. It offers `getServices()`, `addService(Service)`, `addIfService(Object)`, `removeService(Service)`, and lifecycle hook overrides that initialize, start, and stop children. `STOP_ONLY_STARTED_SERVICES` controls whether shutdown only stops already-started services or attempts broader cleanup.
- `LifecycleEvent` at line 37626 is a serializable event with public `time` and `state` fields describing when a service entered a state.
- `LoggingStateChangeListener` at line 37658 logs lifecycle changes via a supplied or static SLF4J `Logger`.
- `Service` at line 37694 defines the lifecycle contract: `init`, `start`, idempotent/no-op `stop`, `close`, listener registration, state/name/config/start-time accessors, `isInState`, failure accessors, `waitForServiceToStop`, lifecycle history, and blockers. The docs emphasize state transitions and stop semantics.
- `ServiceOperations` at line 37893 contains helper methods to stop services, including quiet variants that catch and return exceptions while optionally logging through Apache Commons Logging or SLF4J.
- `ServiceStateChangeListener` at line 37967 is the callback interface for service state changes.
- `ServiceStateException` at line 37999 is a runtime lifecycle exception with exit-code carrying constructors, `getExitCode()`, and static `convert` helpers to wrap arbitrary exceptions.
- `ServiceStateModel` at line 38086 implements the thread-safe service state model with state queries, `ensureCurrentState`, `enterState`, transition validation, and textual state reporting.

### `org.apache.hadoop.service.launcher`

- `AbstractLaunchableService` at line 38202 extends `AbstractService` and implements `LaunchableService`, giving services a command-line binding phase (`bindArgs(Configuration, List<String>)`) and an `execute()` method that returns a process-style exit code.
- `HadoopUncaughtExceptionHandler` at line 38246 logs uncaught exceptions and can delegate to another `Thread.UncaughtExceptionHandler`.
- `LaunchableService` at line 38296 declares command-line argument propagation and post-start service execution.
- `LauncherExitCodes` at line 38376 centralizes stable numeric exit-code constants for success, generic failure, client shutdown, task launch failure, interruption, command-line errors, unauthorized/forbidden/not-found HTTP-style failures, connectivity and configuration problems, thrown exceptions, unimplemented features, service unavailable, unsupported version, service creation failure, and lifecycle exceptions.
- `ServiceLaunchException` at line 38599 wraps launch failures with explicit exit codes and supports cause, plain message, and formatted-message constructors.

### Empty or marker packages

- `org.apache.hadoop.tools` at line 38652 and `org.apache.hadoop.tools.protocolPB` at line 38654 are present as package entries without classes in this chunk.
- `org.apache.hadoop.util.curator` at line 41050 and `org.apache.hadoop.util.hash` at line 41052 are also package markers here.

### `org.apache.hadoop.tracing`

- `SpanReceiverInfo` at line 38657 exposes span receiver identity through `getId()` and implementation class through `getClassName()`.
- `SpanReceiverInfoBuilder` at line 38674 constructs receiver descriptors with a class name and configuration pairs, then emits `SpanReceiverInfo` through `build()`.
- `TraceAdminProtocol` at line 38697 is a versioned RPC protocol (`versionID`) for listing, adding, and removing span receivers. It throws `IOException` for remote/admin failures.
- `TraceAdminProtocolPB` at line 38750 is the protobuf service interface bridge for tracing administration.

### `org.apache.hadoop.util`

- `ApplicationClassLoader` at line 38760 is a `URLClassLoader` used for application isolation. It accepts URL arrays or classpath strings plus parent and system-class patterns, overrides `getResource` and `loadClass`, and exposes static `isSystemClass(String, List<String>)` plus `SYSTEM_CLASSES_DEFAULT`.
- `IPList` at line 38829 is a simple membership predicate for IP address strings.
- `Progressable` at line 38846 defines the `progress()` callback used by long-running Hadoop operations to report liveness to the framework.
- `PureJavaCrc32` at line 38869 and `PureJavaCrc32C` at line 38920 implement `java.util.zip.Checksum` with `getValue`, `reset`, and byte/byte-array `update` methods. CRC32C uses the Castagnoli polynomial.
- `ReflectionUtils` at line 38964 provides configuration injection (`setConf`), cached reflective construction (`newInstance`), contention/thread diagnostics, type extraction, writable deep copy through serialization, cloning into an existing writable, and inherited field/method enumeration.
- `Shell` at line 39108 is the central process-execution abstraction. It covers OS detection flags, command construction for groups, permissions, ownership, symlinks, process checks, signals, script execution, Hadoop home and winutils lookup, environment and working-directory control, timeout-aware `run()`, `getExecString`, result parsing, subprocess state, static `execCommand` overloads, process cleanup, active-shell tracking, and memlock-limit discovery.
- `ShutdownHookManager` at line 39820 manages prioritized shutdown hooks, optional per-hook timeouts, hook removal and existence checks, shutdown-progress status, and test/reset support through `clearShutdownHooks`. It exposes `TIMEOUT_MINIMUM` and `TIME_UNIT_DEFAULT`.
- `StringInterner` at line 39948 exposes strong and weak string interning plus in-place interning of string arrays.
- `SysInfo` at line 40004 is an abstract resource-information plugin with a factory `newInstance()` and methods for total/available virtual and physical memory, processor/core counts, CPU frequency, cumulative CPU time, CPU usage percentage, vcores used, network byte counters, and storage byte counters.
- `Tool` at line 40168 is the generic Hadoop command-line interface with `run(String[])`.
- `ToolRunner` at line 40241 runs `Tool` instances with generic option parsing, with overloads for supplied `Configuration`, generic-command usage printing, and interactive confirmation prompting.
- `VersionInfo` at line 40328 reads component build metadata. Instance underscore methods and static methods return version, revision, branch, build date, build user, source URL, source checksum, combined build version, protoc version, and `main` prints this metadata.

### `org.apache.hadoop.util.bloom`

- `BloomFilter` at line 40480 is the base probabilistic set-membership filter with default serialization constructor, parameterized constructor (`vectorSize`, `nbHash`, `hashType`), `add`, boolean operations `and`/`or`/`xor`/`not`, `membershipTest`, `getVectorSize`, `toString`, and `Writable`-style `write`/`readFields`.
- `CountingBloomFilter` at line 40587 extends `Filter` and supports additions, `delete`, boolean operations, membership testing, approximate counting, string conversion, and serialization. The docs warn that counters overflow after repeated inserts of the same key, especially beyond 15, increasing error rates and possibly causing false negatives after underflow.
- `DynamicBloomFilter` at line 40717 extends `Filter` and grows by rows when active Bloom filter capacity is exhausted. It supports additions, boolean operations, membership testing, string conversion, and serialization; constructor parameter `nr` is the per-row threshold.
- `HashFunction` at line 40832 maps a `Key` to multiple hash values bounded by `maxValue`, `nbHash`, and `hashType`; `clear()` is a no-op.
- `RemoveScheme` at line 40876 defines retouched Bloom filter selective-clearing strategies: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` at line 40932 extends `BloomFilter` and implements `RemoveScheme`. It tracks false-positive keys through overloads accepting one `Key`, a `Collection`, a `List`, or a `Key[]`; `selectiveClearing(Key, short)` removes selected false positives at the cost of possible false negatives; serialization is exposed through `write` and `readFields`.

## Control Flow and State

The XML records API control flow at the contract level. Delegation-token operations flow from URL/token inputs to HTTP/S endpoints and either return an authenticated `HttpURLConnection`, a delegation token, a renewal timestamp, or no value for cancellation. Authentication exceptions and IO failures are part of the method contract, and cancellation explicitly avoids requiring configured-authenticator authentication.

Service lifecycle APIs expose a clear state progression: `NOTINITED` to initialized, started, and stopped states, with `AbstractService` coordinating public lifecycle methods, protected subclass hooks, failure state capture, lifecycle event history, blockers, and listener notifications. `CompositeService` layers child-service sequencing on top of this state model. Launcher APIs build on that lifecycle by binding arguments, starting the service, executing it, and returning standardized exit codes.

Utility classes split between stateless helpers (`ToolRunner`, `StringInterner`, `ReflectionUtils` static methods), stateful process runners (`Shell` instances keep environment, working directory, subprocess, exit code, timeout status, and waiting thread), global singletons/registries (`ShutdownHookManager`, static Shell process tracking), and serializable/filter state (`BloomFilter` variants and lifecycle events).

## Persistence and Serialization

Several types advertise persistence through constructors intended for deserialization and `Writable`-style methods. Bloom filter variants provide zero-argument constructors for `readFields`, then persist their internal bit/counter/filter-row state through `write(DataOutput)` and `readFields(DataInput)`. `LifecycleEvent` is serializable and stores timestamp and state. `ReflectionUtils.copy` and `cloneWritableInto` use Hadoop serialization for object copying.

`VersionInfo` persists no runtime state of its own in this API surface; it exposes build-time metadata embedded in component properties. `DelegationTokenAuthenticatedURL.Token` holds delegation-token state client-side. `Shell` manages runtime process state rather than durable persistence.

## Dependencies and Integration Points

- Authentication APIs integrate with `AuthenticatedURL`, `Authenticator`, `ConnectionConfigurator`, `AuthenticationException`, `HttpURLConnection`, Hadoop `Token`, and server-side delegation-token endpoints that understand the documented operation, token, renewer, service, and JSON field constants.
- Service APIs integrate with `Configuration`, listener callbacks, SLF4J/Commons Logging, Java `Closeable`, runtime exceptions carrying launcher exit codes, and downstream Hadoop daemons that subclass `AbstractService` or aggregate `CompositeService`.
- Launcher APIs connect service lifecycle with command-line processing and process exit-code semantics.
- Tracing admin APIs integrate with Hadoop RPC/protobuf bindings and trace span receiver implementations.
- `ApplicationClassLoader` integrates with Java class/resource loading and classpath isolation rules.
- `Shell` integrates heavily with OS-specific command lines, Hadoop home discovery, Windows `winutils`, process signaling, environment variables, and timeout management.
- `SysInfo` is a plugin seam for OS resource discovery.
- Bloom filters depend on `org.apache.hadoop.util.bloom.Key`, `Filter`, Hadoop hash implementations, and Java data streams.

## Risks and Edge Cases

- Delegation-token APIs carry security-sensitive `doAs` behavior. Callers must ensure proxy-user authorization is enforced server-side and that cancellation semantics without configured-authenticator authentication cannot be abused with leaked tokens.
- `AuthenticatedURL` instances are documented as not thread-safe; reusing token/authenticator state across threads can corrupt authentication flow or leak credentials.
- Service lifecycle transitions must be idempotent where documented, especially `stop()`. Invalid transitions raise `ServiceStateException`, and failure recording must preserve the first relevant cause/state for diagnostics.
- `CompositeService` shutdown policy affects cleanup during partial startup. Stopping only started services avoids unnecessary hooks but may skip cleanup in initialized children if they allocated resources before start.
- `Shell` has platform-specific behavior and Windows command-line length limits. Environment inheritance, timeout cleanup, process killing, symlink commands, and `winutils` discovery are common portability failure points.
- `ShutdownHookManager` is global process state. Priority ordering, timeout enforcement, and shutdown-in-progress behavior can introduce nondeterminism in tests unless hooks are cleared.
- Bloom filters are probabilistic. Counting filters can overflow counters and produce higher false-positive rates or false negatives after deletes/underflow. Retouched filters intentionally trade selected false positives for possible false negatives.
- This is generated JDiff XML. A mismatch between XML and actual source/bytecode would mislead downstream API compatibility analysis, so research consumers should treat it as public-contract evidence rather than implementation proof.

## Test Signals

- API compatibility tests should verify that all documented classes, interfaces, constructors, methods, fields, inheritance, and checked exceptions remain stable for Hadoop Common 2.10.2.
- Delegation-token tests should cover token precedence over authenticators, `doAsUser` overloads, token get/renew/cancel endpoint parameters, cancellation without configured-authenticator authentication, HTTP/S restriction handling, and IO/authentication exception propagation.
- Service lifecycle tests should cover legal and illegal transitions, idempotent stop/close behavior, listener notification order, lifecycle history snapshots, failure cause/state recording, blocker map mutation, `waitForServiceToStop`, and composite child init/start/stop ordering including partial failures.
- Launcher tests should assert exit-code constants and `ServiceLaunchException` exit-code preservation, including formatted messages and wrapped causes.
- Tracing tests should exercise list/add/remove span receiver protocol calls and protobuf bridge compatibility.
- Utility tests should cover classloader parent/system-class decisions, CRC32/CRC32C known vectors, reflective construction with configuration injection, writable copy/clone behavior, shell command construction across OS families, timeout cleanup, shutdown-hook ordering/removal, string interning identity behavior, sysinfo unavailable-value conventions, and `ToolRunner` generic option parsing.
- Bloom filter tests should verify serialization round trips, membership semantics, boolean operations with compatible filters, counter overflow/underflow behavior, dynamic row growth at `nr`, retouched selective-clearing schemes, and hash-value bounds.
