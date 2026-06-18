# Research: subset-b-007370

This grouped report covers Hadoop common service launching, command/tool helpers, no-op tracing compatibility, and selected utility classes for class loading, concurrency, checksums, disk validation, and configuration parsing. Each file section is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LaunchableService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LaunchableService.java

Purpose: `LaunchableService` is the optional service contract used by `ServiceLauncher` when a Hadoop `Service` wants command-line binding and a foreground execution method rather than only background service threads.

Important APIs and types: it extends `Service` and adds `bindArgs(Configuration, List<String>)` and `execute()`. `bindArgs` receives the launcher's base `Configuration` plus post-launcher arguments, and may return a replacement configuration. `execute` returns the process exit code and may throw `ExitUtil.ExitException`, `ExitCodeProvider` exceptions, or generic exceptions.

Control flow: `ServiceLauncher.coreServiceLaunch` detects this interface before service initialization, calls `bindArgs`, initializes and starts the service, then calls `execute` while the service is started. `execute` completion causes the launcher to stop the service and use the returned integer as the exit status.

State and persistence behavior: the interface itself stores nothing. Implementations can use `bindArgs` to mutate or replace configuration before `init`, so persistent configuration resources must be loaded before returning.

Dependencies and integration points: integrates with `Service`, `Configuration`, `ServiceLauncher`, `ServiceLaunchException`, `LauncherExitCodes`, and Hadoop exit-code conversion.

Risks: implementations that initialize in constructors may run before CLI arguments are bound. Returning null from `bindArgs` preserves the launcher configuration. Throwing generic exceptions loses service-specific exit status unless the exception implements `ExitCodeProvider`.

Test signals: cover bind-before-init ordering, returned replacement configuration, execute return-code propagation, exception conversion, and automatic stop after `execute`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LaunchableService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LauncherArguments.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LauncherArguments.java

Purpose: `LauncherArguments` centralizes the command-line option names and parse-error text shared by the service launcher package.

Important APIs and types: it defines constants for `--conf`, short `conf`, `--hadoopconf`, short `hadoopconf`, and the parse failure prefix `E_PARSE_FAILED`.

Control flow: `ServiceLauncher.createOptions` uses these constants to build Commons CLI options, while parse failures use `E_PARSE_FAILED` in `ServiceLaunchException` messages.

State and persistence behavior: this is a constant-only interface with no runtime state or persistence.

Dependencies and integration points: consumed by `ServiceLauncher` and documented by `LauncherExitCodes`/package docs. The names mirror a subset of Hadoop `GenericOptionsParser` options but are intentionally restricted by `MinimalGenericOptionsParser`.

Risks: changing these strings breaks launcher compatibility and command help. The short option values are identical to long names, so parser behavior depends on Commons CLI accepting that spelling.

Test signals: assert option creation includes the expected names, parse errors include `Failed to parse:`, and usage text remains synchronized with these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LauncherArguments.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LauncherExitCodes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LauncherExitCodes.java

Purpose: `LauncherExitCodes` defines the stable public exit-code vocabulary used by Hadoop service launchers and launchable services.

Important APIs and types: constants include success/failure basics (`EXIT_SUCCESS`, `EXIT_FAIL`), interrupt and shutdown codes, CLI/client errors in the 40s, service/server errors in the 50s, and service creation/lifecycle failures.

Control flow: `ServiceLauncher`, `ServiceLaunchException`, and `LaunchableService` implementations use these codes to convert Java exceptions and lifecycle outcomes into process exit statuses. Some values intentionally resemble HTTP status classes compressed into a byte-sized range.

State and persistence behavior: constant-only interface; no state, persistence, or validation logic.

Dependencies and integration points: public evolving API used by services, CLI callers, tests, and documentation. `ServiceLaunchException` implements this interface for convenient constant access.

Risks: codes are part of CLI compatibility. `EXIT_FAIL` is `-1`, which is meaningful inside Java but may be shell-normalized differently. Application-specific codes are expected at 60+, so new framework codes should avoid that range.

Test signals: verify launcher exception conversion chooses the documented codes, usage failures produce `EXIT_USAGE`, missing config files produce `EXIT_NOT_FOUND`, and service instantiation failures produce `EXIT_SERVICE_CREATION_FAILURE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LauncherExitCodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceLaunchException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceLaunchException.java

Purpose: `ServiceLaunchException` is the launcher-specific `ExitUtil.ExitException` subclass that carries a process exit code plus an optional formatted message and cause.

Important APIs and types: constructors accept `(exitCode, Throwable)`, `(exitCode, String)`, `(exitCode, format, args...)`, and `(exitCode, cause, format, args...)`. It implements `ExitCodeProvider` and `LauncherExitCodes`.

Control flow: `ServiceLauncher` throws or returns this exception for argument, service creation, lifecycle, and generic execution failures. Formatted constructors use `String.format(Locale.ENGLISH, ...)`; the varargs constructor also treats a trailing `Throwable` as a cause.

State and persistence behavior: stores only the inherited exit code, message, and cause. It has no persistence behavior.

Dependencies and integration points: integrates with `ExitUtil.terminate`, `ExitCodeProvider`, and the launcher exception-conversion path.

Risks: the varargs constructor includes the trailing throwable in format substitution while also installing it as cause, so format strings must account for it. Locale is fixed to English for reproducibility.

Test signals: cover exit-code retention, cause initialization in both cause-taking paths, formatted messages under non-English default locales, and launcher pass-through of existing `ExitException` instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceLaunchException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceLauncher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceLauncher.java

Purpose: `ServiceLauncher<S extends Service>` is the generic Hadoop entry point for constructing, configuring, starting, optionally executing, waiting for, and terminating a `Service` by class name or provided instance.

Important APIs and types: key entry points are `main`, `serviceMain`, `launchServiceAndExit`, `launchService`, `coreServiceLaunch`, `instantiateService`, `extractCommandOptions`, `parseCommandArgs`, `loadConfigurationClasses`, `convertToExitException`, and the protected hooks `createOptions`, `createConfiguration`, `createGenericOptionsParser`, `getClassLoader`, `exit`, `warn`, and `error`. It implements `LauncherExitCodes`, `LauncherArguments`, and `Thread.UncaughtExceptionHandler`.

Control flow: the CLI path registers interrupt/uncaught-exception handling, reflectively loads default configuration classes, builds a base `Configuration`, parses launcher options, verifies `--conf` files, records extra configuration resources/classes, instantiates the service with a no-arg or string constructor, adds a `ServiceShutdownHook`, binds `LaunchableService` arguments before `init`, starts the service, calls `execute` if available, otherwise waits for service stop, unregisters the hook, checks service failure state, converts outcomes to `ExitUtil.ExitException`, logs, flushes streams, and terminates.

State and persistence behavior: mutable launcher state includes the volatile service, configuration, exit code/exception, interrupt escalator, service names, config class/resource lists, and command options. It persists no service data, but it mutates configuration resources and installs process-level interrupt and default uncaught-exception handlers.

Dependencies and integration points: uses Commons CLI, `GenericOptionsParser`, `Configuration`, `Service`, `LaunchableService`, `ServiceShutdownHook`, `InterruptEscalator`, `HadoopUncaughtExceptionHandler`, `CommonAuditContext`, `NetUtils`, `StringUtils`, `ExitUtil`, and SLF4J. Subclasses can customize option sets, configuration construction, class loading, and exit behavior for tests.

Risks: constructor-side service initialization can run before `bindArgs`. The CLI contract assumes argument 0 is the service class. Config classes that are missing are debug-logged and ignored, while wrong subclasses fail. `parseCommandArgs` mutates `confClassnames` after the initial `loadConfigurationClasses` call in `launchServiceAndExit`, so classes added with `--hadoopconf` are recorded but not created in that path until subclasses intervene. Global signal and uncaught-exception handlers affect the whole JVM. Non-launchable services block indefinitely until stopped.

Test signals: cover no-argument usage exit, option parsing and remaining args, missing config file errors, service instantiation constructor fallback, non-service class rejection, bind/init/start/execute/stop order, wait path for non-launchable services, shutdown hook registration/unregistration, failure-state handling, `ExitCodeProvider` conversion, and disabled `System.exit` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceLauncher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceShutdownHook.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceShutdownHook.java

Purpose: `ServiceShutdownHook` adapts a Hadoop `Service` into a JVM shutdown hook that calls `stop()` during process shutdown.

Important APIs and types: constructor stores a `WeakReference<Service>`. `register(int)` adds the hook to `ShutdownHookManager`; `unregister()` removes it; `run()` delegates to `shutdown()`; `shutdown()` stops and clears the service reference and returns whether stop succeeded.

Control flow: registration first unregisters any existing hook registration for the same instance. On shutdown, the service reference is read and cleared under synchronization, then `service.stop()` is invoked outside that synchronized block. Stop failures are logged and swallowed.

State and persistence behavior: state is only the weak service reference. Clearing the reference prevents duplicate stops from the same hook and avoids pinning the service in memory. No durable persistence occurs.

Dependencies and integration points: used by `ServiceLauncher.coreServiceLaunch`; integrates with Hadoop `ShutdownHookManager`, `Service`, and SLF4J.

Risks: weak references mean a service can be garbage-collected before shutdown if nothing else holds it. `unregister()` may see `IllegalStateException` during shutdown and logs at info. Stop exceptions do not affect process exit.

Test signals: cover register/unregister idempotence, weak reference clearing, successful stop return value, exception-swallowing path, and behavior when `ShutdownHookManager` is already shutting down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/ServiceShutdownHook.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/package-info.java

Purpose: this package documentation defines the design contract for launching Hadoop services through `ServiceLauncher`, including normal lifecycle ordering, CLI handling, exit-code policy, and extension points.

Important APIs and types: it documents `ServiceLauncher`, `LaunchableService`, `ServiceLaunchException`, `LauncherExitCodes`, service constructors, configuration loading, shutdown hooks, and the expected `bindArgs`/`execute` lifecycle for launchable services.

Control flow: the documented sequence is class creation, optional `LaunchableService.bindArgs`, service `init`, `start`, optional `execute`, otherwise waiting for service termination, then stop/exit. It also describes how command-line options are stripped before service arguments are passed downstream.

State and persistence behavior: documentation emphasizes configuration as the main state carrier and warns that launchers create base `Configuration` unless subclasses or services replace it. Shutdown state is managed with hooks and exit exceptions rather than persisted records.

Dependencies and integration points: ties the service package to CLI scripts, Hadoop configurations, YARN/HDFS configuration subclasses, `ExitUtil`, and tests that disable JVM termination.

Risks: this file is a behavioral contract; divergence between docs and `ServiceLauncher` can break service authors. The documented ordering makes constructor-side initialization risky because it can happen before CLI binding.

Test signals: compare package examples and stated lifecycle against actual launcher tests, especially argument stripping, configuration class/resource loading, exit status mapping, and launchable versus non-launchable service behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/package-info.java

Purpose: this package-info marks `org.apache.hadoop.service` as a public, evolving API package for Hadoop service lifecycle abstractions.

Important APIs and types: the file itself only carries package annotations, but it applies to the core `Service` package that launchers and service implementations depend on.

Control flow: no executable flow. Its semantic role is API classification for downstream users and compatibility policy.

State and persistence behavior: no state or persistence.

Dependencies and integration points: imports `InterfaceAudience` and `InterfaceStability`, declaring the package public and evolving for tools, daemons, and service launcher code.

Risks: changing annotations changes published compatibility expectations. Package docs are minimal, so detailed behavior must be read from concrete classes and service launcher docs.

Test signals: no runtime tests are needed; API compatibility checks should verify annotations remain intentional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/CommandShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/CommandShell.java

Purpose: `CommandShell` is an abstract base for Hadoop CLI utilities implemented as `Tool`s with optional subcommands and injectable output streams.

Important APIs and types: subclasses implement `getCommandUsage()` and `init(String[])`. The base class exposes `setSubCommand`, `setOut`, `getOut`, `setErr`, `getErr`, `run`, `printShellUsage`, `printException`, and nested abstract `SubCommand` with `validate`, `execute`, and `getUsage`.

Control flow: `run` calls subclass `init`; if initialization fails or no subcommand is selected, it prints usage and returns the init exit code. If a subcommand is selected, it validates and executes it, printing usage and returning 1 on validation failure or any exception.

State and persistence behavior: stores current `PrintStream`s and selected subcommand only. It writes to streams but persists no data.

Dependencies and integration points: extends `Configured`, implements `Tool`, and is intended for command implementations run by `ToolRunner` or Hadoop scripts.

Risks: any exception prints a stack trace by default, which may be too verbose for user-facing commands. `SubCommand` is a non-static inner class, so it holds the enclosing shell. A subcommand can return no status except by throwing.

Test signals: cover init failure, no subcommand usage, validate false path, execute exception path, stream injection, and command-specific usage selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/CommandShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/GetGroupsBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/GetGroupsBase.java

Purpose: `GetGroupsBase` is the common CLI base for Hadoop tools that print group memberships for supplied users through `GetUserMappingsProtocol`.

Important APIs and types: constructors accept a `Configuration` and optional `PrintStream`. Subclasses implement `getProtocolAddress(Configuration)`. `run(String[])` formats output, and `getUgmProtocol()` creates the RPC proxy.

Control flow: if no users are supplied, `run` uses the current UGI username. For each user it obtains a protocol proxy, calls `getGroupsForUser`, appends groups to `username : group...`, and prints one line. `getUgmProtocol` calls `RPC.getProxy` with protocol version, target address, current user, configuration, and socket factory.

State and persistence behavior: stores only the configured output stream through object lifetime. It creates RPC proxies but does not close them in this base method, so subclasses or process lifetime manage proxy cleanup.

Dependencies and integration points: depends on `Configuration`, `Configured`, `Tool`, `RPC`, `NetUtils`, `UserGroupInformation`, and `GetUserMappingsProtocol`. HDFS and MapReduce provide concrete address resolution.

Risks: repeated users reuse no proxy cache in this method. RPC failures abort the whole run. Output has fixed formatting and no escaping for usernames or group names.

Test signals: cover default current user, multiple user formatting, empty group lists, injected output stream, RPC address selection in subclasses, and error propagation on proxy/group lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/GetGroupsBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/GetUserMappingsProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/GetUserMappingsProtocol.java

Purpose: `GetUserMappingsProtocol` is the RPC interface used by NameNode/JobTracker-side services to return group names for a user.

Important APIs and types: it declares `versionID = 1L` and idempotent `String[] getGroupsForUser(String user) throws IOException`.

Control flow: client tools invoke it through Hadoop RPC or the protobuf translator. Implementations map the supplied user string to group names and return them as an array.

State and persistence behavior: interface-only; no state. Implementations may consult UGI/group mapping caches but that is outside this file.

Dependencies and integration points: annotated limited-private for HDFS/MapReduce, evolving stability, and `@Idempotent` for retry semantics. Bridged by `GetUserMappingsProtocolPB` and client/server translators.

Risks: version ID and method signature are wire compatibility. The method is marked idempotent, so implementations must avoid side effects that make retries unsafe.

Test signals: verify protobuf translators preserve order/count, RPC method support metadata, retry behavior, and IOException propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/GetUserMappingsProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/TableListing.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/TableListing.java

Purpose: `TableListing` formats command output as aligned text tables with optional headers, left/right justification, and wrapping of selected columns.

Important APIs and types: `Justification` enum supplies `LEFT` and `RIGHT`. `Builder` supports `addField`, `hideHeaders`, `showHeaders`, `wrapWidth`, and `build`. `TableListing.addRow` appends rows, and `toString` renders the table. Private `Column` tracks row values, max width, wrap mode, and per-row wrapped lines.

Control flow: builders create columns containing header rows. `addRow` validates row length and appends values. `toString` computes total width, shrinks wrappable columns down to a minimum width of 10 until the target wrap width is met or no more shrink is possible, then renders header/data rows, expanding wrapped cells into multiple output lines and padding missing wrapped lines.

State and persistence behavior: table content is kept in memory as column arrays and row strings. `toString` mutates column wrap widths, so repeated rendering after a narrow wrap may preserve narrower internal max widths.

Dependencies and integration points: used by Hadoop command-line tools. It depends on Apache Commons Lang `StringUtils` for padding and Hadoop `StringUtils.wrap` for line wrapping.

Risks: `addRow` throws a generic `RuntimeException` on wrong arity. Wrapping/padding is character-count based and not display-width aware. Long unwrappable columns can exceed requested width. Null cell values become empty strings.

Test signals: cover left/right padding, headers hidden/shown, row arity errors, null cells, wrapping multi-line cells, repeated `toString`, minimum wrap width behavior, and tables with no data rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/TableListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/package-info.java

Purpose: this package-info identifies `org.apache.hadoop.tools` as a package containing Hadoop common command/tool support classes.

Important APIs and types: it has package-level documentation only. Concrete APIs in this package include `CommandShell`, `GetGroupsBase`, `GetUserMappingsProtocol`, and `TableListing`.

Control flow: no executable control flow.

State and persistence behavior: no state or persistence.

Dependencies and integration points: the package integrates common CLI utilities with Hadoop `Tool`, IPC, and command output formatting.

Risks: minimal documentation means package-level intent is inferred from concrete classes. Annotation or package-comment changes can affect generated docs but not runtime.

Test signals: no direct runtime tests; package coverage comes from concrete tool classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolClientSideTranslatorPB.java

Purpose: this client-side translator adapts the protobuf RPC blocking interface to the classic `GetUserMappingsProtocol` Java interface.

Important APIs and types: it implements `ProtocolMetaInterface`, `GetUserMappingsProtocol`, and `Closeable`. It stores a `GetUserMappingsProtocolPB` proxy, uses a null `RpcController`, implements `getGroupsForUser`, `isMethodSupported`, and `close`.

Control flow: `getGroupsForUser` builds `GetGroupsForUserRequestProto` with the user, invokes `rpcProxy.getGroupsForUser` through `ShadedProtobufHelper.ipc` to convert service exceptions, then converts the response group list to a `String[]`. `close` stops the RPC proxy.

State and persistence behavior: persistent state is only the RPC proxy reference. No data is cached.

Dependencies and integration points: integrates Hadoop RPC, protobuf-generated request/response classes, `RpcClientUtil`, protocol version lookup, and `GetUserMappingsProtocolPB`.

Risks: a null controller is intentional but assumes server-side code ignores it. Array sizing uses `resp.getGroupsCount()`, preserving list size. Callers must close the translator or proxy resources remain open.

Test signals: cover request user propagation, group order preservation, service exception conversion to IOException, `RPC.stopProxy` on close, and `isMethodSupported` using the PB protocol/version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolPB.java

Purpose: `GetUserMappingsProtocolPB` is the protobuf RPC wire interface for user-to-group mapping lookups.

Important APIs and types: it extends the generated `GetUserMappingsProtocolService.BlockingInterface` and carries `@KerberosInfo`, `@ProtocolInfo`, audience, and stability annotations.

Control flow: no implementation flow. Hadoop RPC uses the annotations to bind protocol name `org.apache.hadoop.tools.GetUserMappingsProtocol`, version 1, and server principal configuration.

State and persistence behavior: interface-only; no state or persistence.

Dependencies and integration points: connects protobuf service generation to Hadoop IPC security and protocol metadata. Used by both client and server translators.

Risks: protocol name/version and Kerberos principal key are wire/security compatibility points. Changes must be coordinated with clients and servers.

Test signals: verify RPC registration metadata, KerberosInfo principal lookup, and translator compatibility with the generated blocking interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolServerSideTranslatorPB.java

Purpose: this server-side translator adapts a classic `GetUserMappingsProtocol` implementation to the protobuf blocking RPC service.

Important APIs and types: it implements `GetUserMappingsProtocolPB`, stores a `GetUserMappingsProtocol` delegate, and implements protobuf `getGroupsForUser`.

Control flow: on RPC, it extracts the user from `GetGroupsForUserRequestProto`, calls the delegate, wraps any `IOException` in `ServiceException`, builds `GetGroupsForUserResponseProto`, and adds each returned group in order.

State and persistence behavior: state is only the delegate reference. No caching or persistence.

Dependencies and integration points: used by Hadoop IPC servers for HDFS/MapReduce group-mapping endpoints. Depends on generated protobuf request/response types and shaded protobuf `ServiceException`.

Risks: null delegate results or null group entries are not guarded. IOException is the only checked exception converted explicitly. Group order is preserved and may be significant to clients.

Test signals: cover user extraction, group order/count, empty groups, IOException-to-ServiceException conversion, and malformed/null delegate behavior if construction is not controlled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tools/protocolPB/GetUserMappingsProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/NullTraceScope.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/NullTraceScope.java

Purpose: `NullTraceScope` is the singleton no-op trace scope returned when tracing APIs are retained but no real tracer is active.

Important APIs and types: it extends `TraceScope`, exposes `INSTANCE`, and calls the parent constructor with null span.

Control flow: no additional flow beyond `TraceScope` methods. Closing the null scope is safe because the parent checks for a null span before closing.

State and persistence behavior: singleton object with inherited null `span`; no persistence.

Dependencies and integration points: returned by `Tracer.newScope` and `Tracer.activateSpan` in this no-op tracing layer.

Risks: callers expecting non-null spans from `span()` or `getSpan()` must handle null. The public constructor permits extra null scopes, though the singleton is intended.

Test signals: verify singleton reuse, close no-op behavior, and null span exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/NullTraceScope.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/Span.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/Span.java

Purpose: `Span` is a no-op compatibility wrapper preserving old Hadoop tracing call sites after HTrace removal.

Important APIs and types: methods include `addKVAnnotation`, `addTimelineAnnotation`, `getContext`, `finish`, and `close`. Annotation methods return `this`; context returns null; close/finish do nothing.

Control flow: all calls are local no-ops and never emit tracing data.

State and persistence behavior: no fields and no persistence.

Dependencies and integration points: implements `Closeable`; returned by `Tracer.newSpan`; used by `TraceScope`.

Risks: silent no-op behavior can hide assumptions in call sites that expect real trace propagation or non-null contexts. Because methods return self, fluent call chains still compile but record nothing.

Test signals: verify no exceptions from annotations/finish/close, fluent self return, and null context behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/Span.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/SpanContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/SpanContext.java

Purpose: `SpanContext` is a no-op wrapper class retained to avoid exposing OpenTracing/OpenTelemetry context types directly through Hadoop APIs.

Important APIs and types: it implements `Closeable`, has a public constructor, and `close()` is a no-op.

Control flow: no runtime flow beyond no-op close.

State and persistence behavior: no fields, serialization, or propagation data.

Dependencies and integration points: accepted by `Tracer.newSpan` and `Tracer.newScope`, and referenced by `TraceUtils` conversion methods.

Risks: `TraceUtils` conversion methods currently return null, so this class does not carry distributed trace state. Callers must tolerate empty contexts.

Test signals: verify construction and close are harmless, and context-consuming APIs accept instances without producing real tracing effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/SpanContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceConfiguration.java

Purpose: `TraceConfiguration` is a placeholder configuration wrapper for the no-op tracing layer.

Important APIs and types: only a public constructor is defined.

Control flow: no executable behavior.

State and persistence behavior: no fields or persistence.

Dependencies and integration points: accepted by `Tracer.Builder.conf`; returned conceptually by `TraceUtils.wrapHadoopConf`, though that method currently returns null.

Risks: code assuming trace configuration data is available will not work with this placeholder. The type exists mainly for source compatibility.

Test signals: verify builder accepts null or placeholder configurations without changing no-op tracer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceScope.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceScope.java

Purpose: `TraceScope` is the closeable scope wrapper around a `Span`, preserved for try-with-resources tracing call sites.

Important APIs and types: constructor stores a `Span`. Methods include overloaded `addKVAnnotation`, `addTimelineAnnotation`, `span`, `getSpan`, `reattach`, `detach`, and `close`.

Control flow: annotation, attach, and detach methods are no-ops. `close` closes the wrapped span when non-null.

State and persistence behavior: stores one package-visible `Span` reference. No durable state is written.

Dependencies and integration points: used by `Tracer`, `NullTraceScope`, and code that scopes trace spans around operations.

Risks: a non-null span is closed on scope close, but no finish semantics are enforced beyond whatever `Span.close` does, currently no-op. Null spans are common via `NullTraceScope`.

Test signals: cover null and non-null span close behavior, getter aliases, and no-op annotations with string and number values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceScope.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceUtils.java

Purpose: `TraceUtils` keeps old Hadoop tracing utility entry points while tracing is disabled/no-op in this source tree.

Important APIs and types: it defines `DEFAULT_HADOOP_TRACE_PREFIX` and static methods `wrapHadoopConf`, `createAndRegisterTracer`, `byteStringToSpanContext`, and `spanContextToByteString`.

Control flow: all methods currently return null and perform no registration, wrapping, serialization, or deserialization.

State and persistence behavior: no state is stored. No trace configuration or span context is persisted into protobuf bytes.

Dependencies and integration points: imports Hadoop `Configuration`, shaded protobuf `ByteString`, `TraceConfiguration`, `Tracer`, and `SpanContext`. Call sites retain compatibility but must handle nulls.

Risks: returning null from conversion and tracer creation is a sharp edge for callers that do not expect tracing to be removed. This differs from `Tracer.Builder.build`, which returns a no-op tracer.

Test signals: cover null-return compatibility, callers' null guards, and behavior of code paths that formerly expected serialized span contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/Tracer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/Tracer.java

Purpose: `Tracer` is Hadoop's no-op tracer facade retained after HTrace removal so existing tracing call sites keep compiling.

Important APIs and types: constructor stores a name and `NullTraceScope`. Static methods include `curThreadTracer` and `getCurrentSpan`; instance methods include `newScope`, `newSpan`, `activateSpan`, `close`, and `getName`. Nested `Builder` accepts a name, optional `TraceConfiguration`, and builds a singleton no-op tracer.

Control flow: `newScope` and `activateSpan` return the shared null scope; `newSpan` returns a new no-op `Span`; `getCurrentSpan` and `curThreadTracer` return null in the outer static API. Builder caches one static `Tracer` for all names after the first build.

State and persistence behavior: instance state is name and null scope. Builder has static singleton state. No trace spans are exported or persisted.

Dependencies and integration points: used throughout Hadoop where trace scopes are created around IO/RPC operations. Constant `SPAN_RECEIVER_CLASSES_KEY` preserves config-key compatibility.

Risks: outer `globalTracer` is a separate static field initialized null while `Builder.globalTracer` may hold the singleton, so `curThreadTracer()` still returns null even after builder construction. Later builder names are ignored after the first build.

Test signals: cover builder singleton behavior, name retention for first build, null current tracer/span, null-scope return values, no-op close, and compatibility with try-with-resources scopes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/Tracer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ApplicationClassLoader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ApplicationClassLoader.java

Purpose: `ApplicationClassLoader` is a child-first `URLClassLoader` for isolating application classes while delegating configured system classes/resources to the parent loader.

Important APIs and types: constructors accept URL arrays or a classpath string, parent classloader, and system class patterns. Static `constructUrlsFromClasspath` expands existing entries and wildcard jar directories. `getResource`, `loadClass`, and `isSystemClass` implement resource/class selection.

Control flow: static initialization loads `org.apache.hadoop.application-classloader.properties` and `system.classes.default`. For non-system classes/resources, lookup tries this loader first, then parent. For system classes it delegates directly. `isSystemClass` normalizes slashes, strips leading dots, applies ordered positive and negative prefixes, and treats exact class, package suffix dot, and nested class `$` as matches.

State and persistence behavior: stores parent and system class list; no persistence beyond loaded URLs. Static failure to load defaults throws `ExceptionInInitializerError`.

Dependencies and integration points: uses `FileUtil.getJarsInDirectory`, `Path`, Hadoop `StringUtils`, Java `URLClassLoader`, and YARN/application isolation code.

Risks: child-first loading can create incompatible duplicate classes if system patterns are wrong. Missing properties file prevents class initialization. Classpath wildcard entries only include jars present at construction time. Negative system-class rules override positives.

Test signals: cover default property loading, null parent rejection, wildcard jar expansion, nonexistent classpath elements, resource leading slash handling, system class include/exclude rules, nested classes, and parent fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ApplicationClassLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/AsyncDiskService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/AsyncDiskService.java

Purpose: `AsyncDiskService` manages one thread pool per storage volume for asynchronous disk work such as background deletion.

Important APIs and types: constructor accepts volume roots. `execute(root, task)` submits to a root-specific executor. `shutdown`, `awaitTermination`, and `shutdownNow` manage all executors.

Control flow: construction creates a `ThreadPoolExecutor` per volume with core size 1, max 4, unbounded queue, 60-second keepalive, core thread timeout, and `SubjectInheritingThread`s in a shared thread group. `execute` synchronizes lookup and submission. Graceful shutdown iterates all executors; `awaitTermination` shares a total deadline across them; `shutdownNow` aggregates pending tasks.

State and persistence behavior: in-memory map from root string to executor plus thread factory/group. No disk state is modified directly by this class; tasks perform the actual IO.

Dependencies and integration points: used by HDFS/MapReduce disk cleanup code; depends on `SubjectInheritingThread`, `Time`, Java executors, and SLF4J.

Risks: unbounded queues can grow under heavy deletion backlogs. Unknown roots throw `RuntimeException`. Methods are synchronized, so a long `awaitTermination` blocks submissions/shutdown calls. Duplicate volume strings replace prior executor in the map.

Test signals: cover per-volume routing, unknown root failure, task execution, graceful timeout, immediate shutdown returning pending tasks, subject inheritance, duplicate volume behavior, and core-thread timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/AsyncDiskService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/AutoCloseableLock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/AutoCloseableLock.java

Purpose: `AutoCloseableLock` wraps a `Lock` so callers can acquire it and release it via try-with-resources.

Important APIs and types: constructors wrap a new `ReentrantLock` or supplied `Lock`. Methods are `acquire`, `release`, `close`, `tryLock`, package-visible/testing `isLocked`, and `newCondition`.

Control flow: `acquire` calls `lock.lock()` and returns `this`; `close` delegates to `release`; `tryLock` returns immediately with lock outcome. `isLocked` only works for `ReentrantLock`, otherwise throws `UnsupportedOperationException`.

State and persistence behavior: stores one lock reference; no persistence.

Dependencies and integration points: integrates with Java `Lock`, `Condition`, and resource-scoped synchronization patterns across Hadoop code.

Risks: callers must only use try-with-resources after a successful `acquire` or `tryLock` that actually acquired the lock. `close` can throw `IllegalMonitorStateException` if the current thread does not hold it. Fairness depends on supplied lock.

Test signals: cover acquire/release with try-with-resources, reentrant acquire, tryLock success/failure, condition creation, `isLocked` for default lock, and unsupported `isLocked` for non-reentrant locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/AutoCloseableLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/BasicDiskValidator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/BasicDiskValidator.java

Purpose: `BasicDiskValidator` is the simplest `DiskValidator` implementation; it verifies that a directory exists and has required read/write/execute access.

Important APIs and types: constant `NAME = "basic"` identifies it in `DiskValidatorFactory`. It implements `checkStatus(File)` by delegating to `DiskChecker.checkDir`.

Control flow: validation is a single call into `DiskChecker`, which may create missing directories and then verify access through file methods.

State and persistence behavior: stateless validator. Side effects come from `DiskChecker.checkDir`, which can create directories.

Dependencies and integration points: registered by name in `DiskValidatorFactory`; used by components that need a low-cost disk health check without write/sync probing.

Risks: it does not perform actual write/sync IO, so it may miss deeper disk/controller failures. Directory creation as part of validation is a side effect.

Test signals: cover valid existing directory, missing directory creation, non-directory path, permission/access failures, and factory lookup by `basic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/BasicDiskValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/BlockingThreadPoolExecutorService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/BlockingThreadPoolExecutorService.java

Purpose: `BlockingThreadPoolExecutorService` is a bounded executor wrapper that blocks task submission through `SemaphoredDelegatingExecutor` when active plus queued tasks reach a configured limit.

Important APIs and types: static `newInstance`, `newDaemonThreadFactory`, package-visible `getNamedThreadFactory`, testing `getActiveCount`, and `toString`. It wraps a fixed-size `ThreadPoolExecutor`.

Control flow: `newInstance` creates a queue sized `waitingTasks + activeTasks`, a fixed active-thread executor, daemon `SubjectInheritingThread`s, core timeout, and a rejection handler that logs unexpected rejections. The superclass controls permit acquisition/release around submissions.

State and persistence behavior: stores the delegate executor and inherited semaphore state. No persistence.

Dependencies and integration points: depends on Java executor primitives, Hadoop `SubjectInheritingThread`, and `SemaphoredDelegatingExecutor`. Used where Hadoop needs backpressure rather than unlimited queued work.

Risks: rejected executions are logged but not rethrown by the handler, though the semaphore should prevent them. Daemon threads will not keep the JVM alive. Misconfigured zero/negative counts are not validated here unless superclass/executor rejects them.

Test signals: cover blocking at permit limit, permit release on completion/failure, thread naming/daemon priority, queue sizing, timeout of idle core threads, and `toString` active count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/BlockingThreadPoolExecutorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CacheableIPList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CacheableIPList.java

Purpose: `CacheableIPList` wraps a `FileBasedIPList` and reloads it on demand when a cache timeout expires or refresh is requested.

Important APIs and types: constructor accepts the file-backed list and timeout. `refresh()` forces expiration. `isIn(String)` checks membership and reloads if needed.

Control flow: cache expiry timestamp is volatile. `isIn` uses double-checked locking: if expiry is non-negative and in the past, it synchronizes and reloads via `ipList.reload()`, then delegates membership to the current list.

State and persistence behavior: stores timeout, volatile expiry time, and volatile current `FileBasedIPList`. Negative timeout disables automatic expiry. No writes to the backing file occur.

Dependencies and integration points: implements `IPList`; used by `CombinedIPList` and `CombinedIPWhiteList` for variable blacklist/whitelist files.

Risks: `refresh()` only sets expiry to zero; the next `isIn` performs reload. Reload failures depend on `FileBasedIPList.reload` behavior. System clock changes affect expiry.

Test signals: cover negative timeout no-reload, positive timeout reload, manual refresh, concurrent reload single execution, and membership delegation after file changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CacheableIPList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ChunkedArrayList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ChunkedArrayList.java

Purpose: `ChunkedArrayList<T>` is a memory-fragmentation-friendly list for large append-heavy collections, storing elements across multiple growing chunks rather than one contiguous array.

Important APIs and types: constructors configure initial and maximum chunk size. Implemented operations include `add`, `get`, `iterator`, `clear`, `isEmpty`, `size`, and testing accessors `getNumChunks`/`getMaxChunkSize`.

Control flow: first add allocates the initial chunk. When the current chunk reaches capacity, a new chunk is allocated at 1.5x previous capacity capped by `maxChunkSize`. Iteration concatenates chunk iterators and decrements total size on iterator removal. `get` scans chunks linearly until the index falls inside one.

State and persistence behavior: in-memory chunks, cached last chunk/capacity, and total size. `clear` drops all chunk references.

Dependencies and integration points: uses Hadoop shaded/third-party Guava-style `Lists`/`Iterables` helpers and `Preconditions`. Intended for internal Hadoop large-list workloads.

Risks: random access is O(number of chunks). Only a subset of `List` operations is efficient/supported. Iterator removal updates size but may leave `lastChunk` capacity assumptions if removing from the last chunk through concatenated iterator.

Test signals: cover chunk growth, max chunk cap, `Integer.MAX_VALUE` guard, iteration order, iterator remove size accounting, clear reset, negative/out-of-range get, and constructor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ChunkedArrayList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ClassUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ClassUtil.java

Purpose: `ClassUtil` locates the jar or class-file resource that contains a given Java class.

Important APIs and types: `findContainingJar(Class<?>)`, `findClassLocation(Class<?>)`, and private `findContainingResource(ClassLoader, String, String)`.

Control flow: it converts the class name to a `.class` resource path, enumerates all matching resources from the classloader, picks the first with the requested protocol (`jar` or `file`), strips a leading `file:` and any `!` suffix, URL-decodes as UTF-8, and returns the path.

State and persistence behavior: stateless utility; no persistence.

Dependencies and integration points: used by diagnostics and classpath reporting code. Depends on Java `ClassLoader.getResources`, `URLDecoder`, and Hadoop audience annotations.

Risks: returns the first matching resource with the protocol, which may not be the actual class loaded if classpath contains duplicates. Throws `RuntimeException` on IO enumeration failure. Path handling is URL/protocol-specific.

Test signals: cover jar resource paths, exploded class directories, URL-encoded spaces, duplicate resources, classes loaded by null/bootstrap-like loaders if applicable, and no-match null returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ClassUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Classpath.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Classpath.java

Purpose: `Classpath` is the Java implementation behind `hadoop classpath` advanced modes, printing an expanded classpath or writing it into a manifest jar.

Important APIs and types: `main(String[])` parses `--glob`, `--jar <path>`, `-h`, and `--help`. Private `terminate` prints to stderr and calls `ExitUtil.terminate`.

Control flow: no args/help prints usage. `CommandFormat` parses options. `--glob` prints `java.class.path`. `--jar` validates an output path, creates a temporary manifest jar with `FileUtil.createJarWithClassPath`, and replaces the requested output path with that jar.

State and persistence behavior: reads the `java.class.path` system property and current working directory. `--jar` writes/replaces a jar file; `--glob` only writes stdout.

Dependencies and integration points: integrates Hadoop shell scripts with `FileUtil`, `Path`, `CommandFormat`, environment variables, and `ExitUtil`.

Risks: `--jar` performs filesystem replacement and may overwrite the target. Unknown options terminate. The classpath is whatever the JVM process already received; shell-side wildcard expansion may already have occurred.

Test signals: cover help/no-arg output, unknown option exit, `--glob` output, missing/empty `--jar` target, manifest jar creation, replace failures, and disabled system-exit handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Classpath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CleanerUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CleanerUtil.java

Purpose: `CleanerUtil` provides an internal, version-adaptive hack for forcibly unmapping direct/mapped `ByteBuffer`s on Java 8 and Java 9+.

Important APIs and types: public constants `UNMAP_SUPPORTED` and `UNMAP_NOT_SUPPORTED_REASON`, `getCleaner()`, and functional interface `BufferCleaner.freeBuffer(ByteBuffer)`.

Control flow: static initialization runs privileged `unmapHackImpl`. It first tries Java 9+ `sun.misc.Unsafe.invokeCleaner(ByteBuffer)`, binding the unsafe singleton. If that fails, it tries Java 8 `DirectByteBuffer.cleaner().clean()` via `MethodHandle`s. The produced cleaner validates the buffer is direct and of the expected implementation class, invokes the unmapper under privilege, and wraps failures in `IOException`.

State and persistence behavior: stores one static cleaner or a static reason string. No persistence.

Dependencies and integration points: used by local filesystem/mmap code that needs deterministic unmap. Depends on private JDK APIs, `MethodHandles`, reflection, and security permissions.

Risks: highly JVM/security-manager dependent. Strong encapsulation can disable it. Passing non-direct or unsupported direct buffer subclasses throws `IllegalArgumentException`. Static initialization records support once for the process.

Test signals: cover supported and unsupported platforms, security-denied reason text, non-direct buffer rejection, wrong direct buffer implementation rejection, successful free path, and IOException wrapping from method-handle failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CleanerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CloseableReferenceCount.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CloseableReferenceCount.java

Purpose: `CloseableReferenceCount` tracks references to a closeable resource and prevents new references after closure.

Important APIs and types: methods are `reference`, `unreference`, `unreferenceCheckClosed`, `isOpen`, `setClosed`, and `getReferenceCount`. State is encoded in an `AtomicInteger` with bit 30 as closed and low bits as count.

Control flow: `reference` increments first, then rolls back and throws `ClosedChannelException` if closed. `unreference` decrements and returns true only when status equals closed-with-zero-references. `setClosed` CASes in the closed bit and returns the current count, or throws if already closed.

State and persistence behavior: all state is in one atomic integer. No persistence.

Dependencies and integration points: used by closeable channel/socket-like resources needing concurrent acquisition and asynchronous close detection.

Risks: reference count overflow is not guarded except by the closed bit layout. `unreferenceCheckClosed` can throw `AsynchronousCloseException` after decrementing. Calling unreference at zero triggers a precondition failure after underflow sentinel.

Test signals: cover open reference/unreference, close with outstanding refs, no-new-ref after close, closed-and-zero return value, double close, underflow failure, and concurrent race between reference and close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CloseableReferenceCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CombinedIPList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CombinedIPList.java

Purpose: `CombinedIPList` combines fixed and optional cache-refreshable variable IP/subnet blacklist files behind one `IPList`.

Important APIs and types: constructor accepts fixed file path, variable file path, and cache expiry seconds. `isIn(String)` checks membership across the configured lists.

Control flow: construction always creates a `FileBasedIPList` for the fixed file. If a variable file is supplied, it wraps another `FileBasedIPList` in `CacheableIPList`. `isIn` rejects null input, then returns true on the first list that contains the address.

State and persistence behavior: stores an array of IP list delegates. It reads list files through delegates and may reload variable lists; no writes.

Dependencies and integration points: used by access-control or network filtering components; depends on `FileBasedIPList`, `CacheableIPList`, and `IPList`.

Risks: null fixed file behavior depends on `FileBasedIPList`. Cache expiry parameter name says seconds but `CacheableIPList` treats it as a raw millisecond timeout, so callers must align units. Null IP input throws.

Test signals: cover fixed-only membership, fixed plus variable membership, null variable file, null input failure, cache refresh, and first-match behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CombinedIPList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CombinedIPWhiteList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CombinedIPWhiteList.java

Purpose: `CombinedIPWhiteList` combines fixed and optional variable whitelist files, always allowing localhost.

Important APIs and types: constructor mirrors `CombinedIPList`; `isIn(String)` checks whitelist membership and treats `127.0.0.1` specially.

Control flow: it builds fixed and optional cacheable variable delegates. `isIn` rejects null input, returns true for localhost, then tests each delegate until one contains the address.

State and persistence behavior: stores delegate IP lists and reads/reloads files through them. No writes.

Dependencies and integration points: used by network allow-list checks; depends on `FileBasedIPList`, `CacheableIPList`, and `IPList`.

Risks: localhost bypass is unconditional and only covers IPv4 loopback string, not `::1`. Cache expiry unit naming has the same risk as `CombinedIPList`. Null input throws.

Test signals: cover localhost acceptance, fixed/variable matches, nonmatches, null input failure, null variable file, and cache refresh behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CombinedIPWhiteList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ComparableVersion.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ComparableVersion.java

Purpose: `ComparableVersion` is Hadoop's copy of Maven's generic version comparator, supporting numeric parts, string qualifiers, dot/dash separators, and canonical equality.

Important APIs and types: public constructor, `parseVersion`, `compareTo`, `toString`, `equals`, and `hashCode`. Internal `Item` implementations are `IntegerItem`, `StringItem`, and recursive `ListItem`.

Control flow: parsing lowercases the version, splits on dots, dashes, and digit/letter transitions, creates integer or string items, creates nested list items for numeric dash segments, normalizes trailing null items, and stores a canonical list string. Comparison delegates recursively: integers compare numerically with `BigInteger`, known qualifiers order as alpha, beta, milestone, rc, snapshot, release, sp, and unknown qualifiers sort after known ones lexically.

State and persistence behavior: stores original value, canonical string, and parsed item tree. No persistence.

Dependencies and integration points: used wherever Hadoop needs Maven-like version ordering. Depends on Hadoop `StringUtils.toLowerCase` and Java `BigInteger`.

Risks: behavior is compatibility-sensitive with Maven semantics. Empty or malformed numeric segments may throw through `BigInteger`. Equality is canonical, so different strings like `1.0` and `1` can be equal.

Test signals: cover numeric ordering, qualifier aliases (`ga`, `final`, `cr`), short qualifiers (`a1`, `b1`, `m1`), dash versus dot precedence, unknown qualifiers, canonical equality/hash, huge numeric segments, and case-insensitivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ComparableVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ConfTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ConfTest.java

Purpose: `ConfTest` is the `hadoop conftest` validator for Hadoop XML configuration files, checking structural correctness and duplicate properties.

Important APIs and types: `checkConf(InputStream)` returns validation errors. `main` parses `-conffile`, `-h`, and `--help`. Private `parseConf` uses StAX. Package-private `NodeInfo` records property attributes/elements and duplicate QName data.

Control flow: `main` first uses `GenericOptionsParser`, then Commons CLI for specific options. It selects explicit files/directories or `${HADOOP_CONF_DIR}` XML files, validates each, prints valid/errors, and exits nonzero if any invalid. `checkConf` parses top-level `<configuration>`, validates direct children are `<property>`, requires `<name>` and `<value>`, detects empty names and duplicate property names, and flags duplicated child elements except `<source>`.

State and persistence behavior: reads XML files and environment variables; writes stdout/stderr only. `NodeInfo` stores parse state in memory.

Dependencies and integration points: depends on StAX, Commons CLI, `GenericOptionsParser`, Hadoop `StringUtils`, and shell command integration.

Risks: `-h/--help` option is declared with `hasArg`, which can make help parsing unintuitive. The parser tracks first text for elements and may not fully model complex XML. `terminate` calls `System.exit` directly rather than `ExitUtil`.

Test signals: cover valid config, wrong root, non-property children, missing/empty name, missing value, duplicate names, duplicate child elements, allowed duplicate source, directory selection, missing `HADOOP_CONF_DIR`, and CLI parse errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ConfTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ConfigurationHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ConfigurationHelper.java

Purpose: `ConfigurationHelper` provides private advanced parsing helpers for configuration enum values beyond the base `Configuration` API.

Important APIs and types: `parseEnumSet`, `mapEnumNamesToValues`, and `resolveEnum`. It defines an error string for case-insensitive enum name collisions.

Control flow: `parseEnumSet` builds a lowercase mapping of enum names, splits a comma-separated value string, treats `*` as all values, adds known values, ignores or rejects unknowns based on `ignoreUnknown`, and returns a mutable `EnumSet`. `mapEnumNamesToValues` detects duplicate lowercase names. `resolveEnum` reads a trimmed configuration value, maps case-insensitively, or calls a fallback function with the raw trimmed value.

State and persistence behavior: stateless; reads from supplied `Configuration`.

Dependencies and integration points: used by private Hadoop code for capability and option parsing; depends on Java `EnumSet`, streams, functions, and Hadoop `StringUtils`.

Risks: duplicate enum names differing only by case fail. `*` plus unknowns can still reject if `ignoreUnknown` is false. Fallback functions must handle empty strings.

Test signals: cover case-insensitive matches, wildcard all, unknown ignored/rejected, duplicate lowercase enum values, prefix mapping, fallback invocation, and empty/null-like config values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ConfigurationHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CpuTimeTracker.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CpuTimeTracker.java

Purpose: `CpuTimeTracker` converts cumulative CPU jiffies into a CPU usage percentage sampled over wall-clock time.

Important APIs and types: constructor takes jiffy length in milliseconds. Methods include `getCpuTrackerUsagePercent`, `getCumulativeCpuTime`, `updateElapsedJiffies`, and `toString`.

Control flow: `updateElapsedJiffies` multiplies elapsed jiffies by jiffy length, monotonically advances cumulative CPU time, and records sample time. `getCpuTrackerUsagePercent` computes CPU delta divided by elapsed sample time times 100 when enough time has passed, updates last-sample fields, and returns the cached usage otherwise.

State and persistence behavior: stores sample time, last sample time, cumulative and last cumulative CPU time as `BigInteger`, jiffy length, and cached usage. No persistence.

Dependencies and integration points: used by process/resource monitoring code reading OS counters.

Risks: cumulative CPU time is monotonic even if input counter decreases, which hides counter resets. Usage can exceed 100% for multi-core processes. The misspelled `Cummulative` text appears in `toString` compatibility.

Test signals: cover first sample behavior, minimum interval gating, monotonic cumulative handling, decreasing jiffy input, multi-core percentages, big jiffy values, and string diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CpuTimeTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CrcComposer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CrcComposer.java

Purpose: `CrcComposer` composes multiple per-chunk CRC values into one or more CRCs representing concatenated data ranges, with optional stripe boundaries.

Important APIs and types: factories `newCrcComposer` and `newStripedCrcComposer`; update overloads for byte arrays, `DataInputStream`, and single CRC integers; `digest()` returns composed CRC bytes.

Control flow: construction selects the CRC polynomial mod function from `DataChecksum.Type`, precomputes a monomial for the hint length, and initializes stripe state. Updates read big-endian CRCs, compose with either the precomputed hint monomial or a freshly computed monomial, advance current stripe position, flush to `digestOut` at exact stripe boundaries, and reject stripe overrun. `digest` flushes any partial stripe and resets output/current state.

State and persistence behavior: mutable current composite CRC, current stripe position, digest output buffer, fixed type/length hints. No persistence.

Dependencies and integration points: used by HDFS checksum combination paths; depends on `DataChecksum`, `CrcUtil`, and CRC implementations' `mod` functions.

Risks: only CRC32/CRC32C types are valid. Input byte lengths must be multiples of 4. Stripe length must align with update byte counts or an exception is thrown. Calling `digest` resets accumulated output.

Test signals: cover single and multiple CRC composition, hint and non-hint lengths, byte-array/DataInputStream inputs, striped exact/partial boundaries, overrun exception, invalid byte length, and digest reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CrcComposer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CrcUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CrcUtil.java

Purpose: `CrcUtil` implements low-level CRC arithmetic and formatting helpers for composing CRC32/CRC32C values.

Important APIs and types: constants include multiplicative identity and CRC polynomials. Methods include package-private `multiplyMod`, public `getMonomial`, `composeWithMonomial`, `compose`, `intToBytes`, `writeInt`, `readInt`, `toSingleCrcString`, and `toMultiCrcString`.

Control flow: `getMonomial` computes `x^(lengthBytes*8)` under the provided polynomial mod function using exponentiation by squaring. `compose` derives a monomial for the second data length and XORs it with the second CRC after modular multiplication. Byte helpers read/write big-endian ints and formatting helpers validate CRC byte counts.

State and persistence behavior: stateless utility.

Dependencies and integration points: used by `CrcComposer` and checksum debug paths; relies on mod functions from `PureJavaCrc32`/`PureJavaCrc32C` via callers.

Risks: CRC arithmetic is bit-order sensitive; constants are reversed-polynomial forms. `writeInt`/`readInt` only check upper bounds, not negative offsets. Formatting helpers throw for invalid byte lengths.

Test signals: cover monomial identity and negative length, known CRC composition vectors for CRC32 and CRC32C, big-endian read/write bounds, single/multiple CRC formatting, and multiply modular arithmetic against reference implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CrcUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Daemon.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Daemon.java

Purpose: `Daemon` is a `Thread` subclass that is always daemonized and preserves JAAS `Subject` behavior on platforms where subjects are not inherited by threads.

Important APIs and types: constructors accept no runnable, runnable, or thread group plus runnable. `start` captures subject when needed, final `run` executes `work` under that subject, `work` runs the configured runnable, `getRunnable` exposes it, and nested `DaemonFactory` is a `ThreadFactory`.

Control flow: an instance initializer calls `setDaemon(true)`. `start` stores the current subject if thread inheritance is disabled. `run` either wraps `work` in `SubjectUtil.doAs` or invokes it directly.

State and persistence behavior: stores `startSubject` and `runnable`; no persistence.

Dependencies and integration points: used by executor factories and background Hadoop threads; integrates with `SubjectUtil` and JAAS `Subject`.

Risks: `run` and `start` are final, so subclasses must override `work` only. Runnable constructor names the thread using `runnable.toString()`, which may be unstable or verbose. Daemon threads do not keep JVM alive.

Test signals: cover daemon flag, runnable execution, work override, subject capture path, factory-created threads, thread group constructor, and name assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Daemon.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DataChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DataChecksum.java

Purpose: `DataChecksum` wraps chunked checksum algorithms used in DFS data transfer, including header serialization, checksum calculation, and verification.

Important APIs and types: checksum IDs/types include NULL, CRC32, CRC32C, DEFAULT, and MIXED. Factories create instances from type/bytes-per-checksum, byte headers, or `DataInputStream`. Core methods include `writeHeader`, `getHeader`, `writeValue`, `compare`, `update`, `reset`, `verifyChunkedSums`, `calculateChunkedSums`, `equals`, `hashCode`, and nested `ChecksumNull`.

Control flow: factories reject nonpositive bytes-per-checksum and unsupported DEFAULT/MIXED creation. Headers are one type byte plus big-endian bytes-per-checksum. Chunk verification dispatches to native CRC when available and direct/array inputs permit, otherwise computes per chunk, compares stored big-endian ints, throws `ChecksumException` with file position on mismatch, and restores buffer marks/positions. Calculation similarly dispatches native or loops over chunks.

State and persistence behavior: stores checksum type, underlying `Checksum`, bytes-per-checksum, and current bytes in sum. Header and checksum bytes are serialized to streams/buffers; no independent persistence.

Dependencies and integration points: central to HDFS block IO; depends on `CRC32`, `CRC32C`, `NativeCrc32`, `PureJavaCrc32`, `ChecksumException`, and `CrcComposer` mod functions.

Risks: byte order and ByteBuffer mark/position preservation are critical. `newDataChecksum(byte[], offset)` assumes header size availability and maps invalid type to `InvalidChecksumSizeException`. Shared instance use is not thread-safe because `summer` and `inSum` mutate.

Test signals: cover header round trips, invalid type/size, NULL checksum no-op, CRC32/CRC32C known vectors, byte-array and direct-buffer calculate/verify, native and pure-Java paths, mismatch positions including partial chunks, buffer position restoration, equals/hashCode, and current byte count reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DataChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DirectBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DirectBufferPool.java

Purpose: `DirectBufferPool` reuses direct `ByteBuffer`s by exact capacity to reduce native-memory churn.

Important APIs and types: `getBuffer(int)` obtains a direct buffer, `returnBuffer(ByteBuffer)` clears and stores it, and testing `countBuffersOfSize(int)` reports queue length.

Control flow: buffers are grouped by capacity in a concurrent map. `getBuffer` polls weak references until it finds a live buffer or allocates a new direct buffer. `returnBuffer` clears the buffer, creates or reuses the capacity queue, and enqueues a weak reference.

State and persistence behavior: in-memory concurrent map from size to queues of weak references. Weak values allow GC to reclaim returned direct buffers.

Dependencies and integration points: used by HDFS/MapReduce IO code that repeatedly allocates same-sized direct buffers.

Risks: pooling is exact-size only; larger buffers are never reused for smaller requests. Queues may accumulate cleared weak references until polled. Returning a heap buffer is not rejected and could later return a non-direct buffer despite class purpose.

Test signals: cover allocate/reuse same size, distinct sizes, returned buffer clear state, weak-reference cleanup, concurrent put/get, count accessor, and behavior with heap buffers if callers misuse it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DirectBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskChecker.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskChecker.java

Purpose: `DiskChecker` provides filesystem and disk-health checks for local directories, including optional write/sync/delete probing.

Important APIs and types: exceptions `DiskErrorException` and `DiskOutOfSpaceException`; `checkDir` and `checkDirWithDiskIo` overloads for `File` and `LocalFileSystem`/`Path`; permission-aware `mkdirsWithExistsAndPermissionCheck`; testing hooks `getFileNameForDiskIoCheck`, `replaceFileOutputStreamProvider`, and `getFileOutputStreamProvider`.

Control flow: `checkDirInternal` creates missing directories with race-tolerant `mkdirsWithExistsCheck`, verifies directory/read/write/execute with `FileUtil`, and optional `doDiskIo` writes one byte to a generated file, syncs, closes, deletes, and retries up to three filenames before declaring failure. LocalFS overload also sets expected permissions when newly created or mismatched.

State and persistence behavior: static atomic `FileIoProvider` supports tests. Disk IO checks create temporary files named `DiskChecker.OK_TO_DELETE_.NNN` or random UUID and delete them. Directory checks may create directories and set permissions.

Dependencies and integration points: used by disk validators and Hadoop daemons checking storage directories; depends on `LocalFileSystem`, `FsPermission`, `FileUtil`, `FileUtils`, and `IOUtils`.

Risks: validation has side effects on directories and permissions. File-method access checks may not capture all ACL/security behavior. Disk IO retry can leave files only if cleanup fails. Atomic provider replacement must be restored by tests.

Test signals: cover directory creation races, non-directory and access failures, LocalFS permission setting, disk IO success/failure/retry, cleanup on exceptions, deterministic/random probe filenames, provider replacement, and delete failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskValidator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskValidator.java

Purpose: `DiskValidator` is the pluggable interface for checking whether a local disk directory is usable.

Important APIs and types: single method `checkStatus(File dir) throws DiskErrorException`.

Control flow: implementations perform whatever validation they need and throw on failure. `BasicDiskValidator` performs access checks; `ReadWriteDiskValidator` is also supported by the factory outside this item.

State and persistence behavior: interface-only. Implementations may create directories or write probe files depending on validation strategy.

Dependencies and integration points: used by `DiskValidatorFactory` and storage-directory checking components. It depends on `DiskChecker.DiskErrorException`.

Risks: implementations can have side effects, so callers must understand the chosen validator. Failure classification is coarse through `DiskErrorException`.

Test signals: verify factory-created implementations respect this contract and callers handle thrown `DiskErrorException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskValidatorFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskValidatorFactory.java

Purpose: `DiskValidatorFactory` returns singleton validator instances by class or configured validator name.

Important APIs and types: static concurrent `INSTANCES` cache, `getInstance(Class<? extends DiskValidator>)`, and `getInstance(String)`. Recognized names include `BasicDiskValidator.NAME` and `ReadWriteDiskValidator.NAME`; other strings are loaded as class names.

Control flow: class lookup first checks the cache, otherwise creates an instance with `ReflectionUtils.newInstance`, inserts with `putIfAbsent`, and returns the existing racing instance if any. String lookup maps known aliases or loads a class with `Class.forName`, wrapping class-not-found in `DiskErrorException`.

State and persistence behavior: process-global singleton cache keyed by validator class. No persistence.

Dependencies and integration points: used by configuration-driven disk checking; depends on `ReflectionUtils`, `BasicDiskValidator`, `ReadWriteDiskValidator`, and `DiskChecker.DiskErrorException`.

Risks: custom class strings are unchecked until cast/instantiation, so non-validator classes can fail at runtime. `containsKey` plus `get` is harmless but non-atomic and followed by `putIfAbsent`. Singleton validators must be stateless or thread-safe.

Test signals: cover alias lookup, custom class lookup, class-not-found wrapping, singleton reuse, concurrent get races, non-validator class failure, and cache visibility for tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskValidatorFactory.java -->
