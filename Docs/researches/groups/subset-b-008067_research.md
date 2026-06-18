# subset-b-008067 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/hdfs/web/WebHdfsConstants.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/hdfs/web/WebHdfsConstants.java

## Purpose
`WebHdfsConstants` centralizes WebHDFS and secure WebHDFS scheme/token identifiers used by the Ozone HttpFS gateway compatibility layer. It is a private utility class, not a runtime service.

## Important APIs, types, and functions
The class exposes `WEBHDFS_SCHEME`, `SWEBHDFS_SCHEME`, `WEBHDFS_TOKEN_KIND`, and `SWEBHDFS_TOKEN_KIND`. The token constants are Hadoop `Text` values matching WebHDFS delegation token kinds.

## Control flow
There is no control flow beyond class initialization of constants. A private constructor prevents instantiation.

## State and persistence behavior
The only state is immutable static constants. No configuration, filesystem, or durable state is read or written.

## Dependencies and integration points
The file depends on Hadoop `Text` and Ozone's private audience annotation. It integrates with code that needs canonical WebHDFS scheme names or token kind comparisons.

## Risks and edge cases
Changing string values would break protocol compatibility with WebHDFS clients or token consumers. The class intentionally mirrors Hadoop naming rather than deriving values dynamically.

## Test signals
There is no direct test in this subset. Coverage is indirect through HttpFS/WebHDFS authentication and client-compatibility paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/hdfs/web/WebHdfsConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/hdfs/web/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/hdfs/web/package-info.java

## Purpose
This package descriptor documents `org.apache.ozone.hdfs.web` as the WebHDFS implementation namespace for the HttpFS gateway code.

## Important APIs, types, and functions
It declares only package-level Javadoc. The concrete type in this package for this subset is `WebHdfsConstants`.

## Control flow
There is no executable behavior.

## State and persistence behavior
No state is stored or persisted.

## Dependencies and integration points
The package is a compatibility-facing namespace for WebHDFS constants and related gateway implementation classes.

## Risks and edge cases
Risk is documentation drift: the package text is generic, so future additions should keep it aligned with actual WebHDFS compatibility behavior.

## Test signals
No direct tests apply; package-info files are validated through compilation and documentation generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/hdfs/web/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/RunnableCallable.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/RunnableCallable.java

## Purpose
`RunnableCallable` adapts a `Runnable` to `Callable<Void>` and a `Callable<?>` to `Runnable`. The scheduler service uses it to expose one scheduling API for both task forms.

## Important APIs, types, and functions
The constructors accept either a `Runnable` or `Callable<?>` and reject nulls through `Check.notNull`. `call()` invokes the wrapped task and returns null. `run()` invokes the wrapped runnable directly or wraps callable exceptions in `RuntimeException`. `toString()` returns the wrapped class simple name.

## Control flow
Each instance has exactly one non-null delegate. Invocation paths branch on whether the runnable field is set; otherwise the callable field is used.

## State and persistence behavior
State is limited to object references. No persistent state or background resource is owned.

## Dependencies and integration points
It depends on `java.util.concurrent.Callable` and the local `Check` utility. `SchedulerService.schedule(Runnable, ...)` wraps runnables with this class before delegating to the callable scheduler.

## Risks and edge cases
The callable-to-runnable path converts checked exceptions into unchecked `RuntimeException`, so callers using `run()` lose checked exception typing. `toString()` assumes anonymous classes still have a useful simple name, which may be empty.

## Test signals
No direct tests in this subset. Scheduler tests or instrumentation counters would expose adapter failures when runnable tasks are scheduled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/RunnableCallable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/XException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/XException.java

## Purpose
`XException` is the shared checked-exception base for the HttpFS support framework. It standardizes error-code enums, templated messages, and cause extraction.

## Important APIs, types, and functions
The public constructor accepts an `XException.ERROR` and varargs parameters. `getError()` returns the code. `ERROR#getTemplate()` supplies a `MessageFormat` template. Private helpers format messages as `ERROR: message` and treat the final vararg as the cause when it is a `Throwable`.

## Control flow
Construction validates the error code, formats the message, detects an optional cause, and delegates to `Exception`. If a code has no template, a positional template is synthesized from the argument count.

## State and persistence behavior
Each exception stores the error enum. There is no persistence beyond standard exception stack traces.

## Dependencies and integration points
`ServerException`, `ServiceException`, and `FileSystemAccessException` use this base. It relies on `MessageFormat`, so placeholders and quoting follow JDK formatting rules.

## Risks and edge cases
If the last message argument is intentionally a `Throwable` value rather than a cause, it will still be installed as the cause. Template/argument mismatches can produce confusing messages.

## Test signals
No direct test in this subset. Error-message assertions in server, filesystem, and Iceberg tests indirectly depend on stable formatting conventions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/XException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/package-info.java

## Purpose
This descriptor marks `org.apache.ozone.lib.lang` as the package for basic language-level helpers used by the HttpFS gateway support framework.

## Important APIs, types, and functions
The package contains `RunnableCallable` and `XException` in this subset.

## Control flow
No executable behavior is present.

## State and persistence behavior
No state is stored.

## Dependencies and integration points
The package feeds service scheduling and typed exception handling across `org.apache.ozone.lib`.

## Risks and edge cases
Only documentation drift is relevant.

## Test signals
Compilation is the primary signal for this descriptor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/BaseService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/BaseService.java

## Purpose
`BaseService` is the convenience superclass for HttpFS services managed by `Server`. It extracts service-scoped configuration and supplies no-op lifecycle defaults.

## Important APIs, types, and functions
`init(Server)` is final and captures the owning server, derives a prefix of `serverPrefix.servicePrefix.`, copies matching resolved configuration entries into an unprefixed `serviceConfig`, and calls abstract `init()`. It also provides `postInit()`, `destroy()`, `getServiceDependencies()`, `serverStatusChange()`, `getServer()`, `getServiceConfig()`, and `getPrefixedName()`.

## Control flow
Service implementations only override protected `init()` and optional lifecycle hooks. Server initialization calls `init(Server)` once, then calls `postInit()` after all services are registered.

## State and persistence behavior
State is in-memory references to service prefix, owner server, and a per-service Hadoop `Configuration`. No durable writes occur.

## Dependencies and integration points
It depends on `ConfigurationUtils.resolve` to expand inline config values before trimming prefixes. Implementations include instrumentation, scheduler, groups, and filesystem access services.

## Risks and edge cases
The final `init(Server)` means subclasses cannot customize prefix extraction. Misconfigured prefixes silently omit properties from `serviceConfig`, leaving defaults active. The raw `Class[]` dependency API lacks type safety.

## Test signals
Indirect signals appear when `Server` initializes configured services and when `FileSystemAccessService`, `SchedulerService`, and `GroupsService` read their scoped settings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/BaseService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/Server.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/Server.java

## Purpose
`Server` is the HttpFS service container. It owns server directories, configuration loading, log4j initialization, service instantiation, dependency ordering checks, status transitions, and shutdown.

## Important APIs, types, and functions
Key configuration names are `services`, `services.ext`, and `startup.status`. Constructors validate absolute home/config/log/temp directories. `init()` verifies directories, loads build metadata, initializes logging and configuration, loads/deduplicates services, initializes and post-initializes them, then sets startup status. `setStatus()` notifies services, `get(Class<T>)` retrieves services, `setService()` programmatically replaces a service, and `destroy()` tears services down in reverse order. `Status` defines `UNDEF`, `BOOTING`, `HALTED`, `ADMIN`, `NORMAL`, `SHUTTING_DOWN`, and `SHUTDOWN`.

## Control flow
Initialization moves from `UNDEF` to `BOOTING`, loads defaults from `name-default.xml`, overlays site config or a supplied config, injects defaults, applies matching system properties, and uses Hadoop `Configuration#getClasses` to instantiate services. Duplicate service interfaces are resolved with last-one-wins semantics. Dependency checks require dependencies to have already initialized.

## State and persistence behavior
The server stores a mutable `Configuration`, lifecycle status, and a `LinkedHashMap<Class, Service>`. It reads XML/properties files and watches external log4j config if present, but does not persist server state itself.

## Dependencies and integration points
It integrates Hadoop configuration, `ConfigRedactor`, log4j/reload4j, `ConfigurationUtils`, `Check`, and all `Service` implementations. `ServerWebApp` binds this lifecycle to servlet context events.

## Risks and edge cases
Service instantiation uses deprecated no-arg reflection and raw class casts. `destroy()` calls `ensureOperational()`, so shutdown from non-operational states can throw. Status-change callback failures destroy the whole server. Missing classpath resources can surface as runtime or server exceptions.

## Test signals
`TestHttpFSMetrics` initializes `HttpFSServerWebApp`, replaces `FileSystemAccess`, and destroys the server, exercising config loading, service wiring, and programmatic replacement indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/Server.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/ServerException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/ServerException.java

## Purpose
`ServerException` is the typed exception for `Server` lifecycle, configuration, service-loading, and servlet authority failures.

## Important APIs, types, and functions
The nested `ERROR` enum defines codes `S01` through `S14`, covering missing directories, invalid files, classpath loading, service interface mismatches, instantiation failures, dependency failures, status-change failures, missing system properties, and initialization failures. Constructors delegate to `XException`.

## Control flow
The class has no runtime logic beyond templated exception construction.

## State and persistence behavior
State is standard exception data plus the inherited error code. No persistence occurs.

## Dependencies and integration points
`Server`, `ServerWebApp`, and `ServiceException` use these errors. Messages rely on `MessageFormat` formatting through `XException`.

## Risks and edge cases
Some templates preserve historical typos, which tests or logs may now depend on. The protected constructor allows subclasses to pass non-`ServerException.ERROR` codes.

## Test signals
Indirectly tested through initialization failures, missing properties, and service replacement paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/ServerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/Service.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/Service.java

## Purpose
`Service` defines the lifecycle contract for components managed by `Server`.

## Important APIs, types, and functions
Implementations provide `init(Server)`, `postInit()`, `destroy()`, `getServiceDependencies()`, `getInterface()`, and `serverStatusChange(oldStatus, newStatus)`.

## Control flow
`Server` constructs services, validates dependencies, calls `init`, registers by interface, calls `postInit`, notifies status changes, and destroys in reverse order.

## State and persistence behavior
The interface owns no state. Implementations may own resources such as schedulers, metrics, or filesystem caches.

## Dependencies and integration points
The `getInterface()` return value is the service key used by `Server#get(Class)`, enabling concrete services to be replaced by extensions.

## Risks and edge cases
Raw `Class[]` and `Class` returns provide little compile-time safety. Incorrect `getInterface()` values can hide services or break dependency lookup.

## Test signals
`TestHttpFSMetrics` exercises service replacement and lookup via the `FileSystemAccess` interface.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/Service.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/ServiceException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/ServiceException.java

## Purpose
`ServiceException` is the checked exception type for failures inside `Service` implementations.

## Important APIs, types, and functions
It extends `ServerException` and accepts any `XException.ERROR` plus formatting parameters.

## Control flow
No additional logic is added over the parent exception construction.

## State and persistence behavior
Only inherited exception state is stored.

## Dependencies and integration points
`BaseService` subclasses throw this type during initialization and post-initialization. `FileSystemAccessService` wraps Hadoop configuration and Kerberos failures with this exception.

## Risks and edge cases
Because it accepts any `XException.ERROR`, service-specific domains can share one exception type but logs must inspect the error code for source context.

## Test signals
Indirect tests are service initialization failures and server boot behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/ServiceException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/package-info.java

## Purpose
This package descriptor labels `org.apache.ozone.lib.server` as the basic server implementation package for the HttpFS support framework.

## Important APIs, types, and functions
The package contains `Server`, `Service`, `BaseService`, and the server/service exception hierarchy.

## Control flow
No executable logic is present.

## State and persistence behavior
No state is stored by this descriptor.

## Dependencies and integration points
The package underpins servlet startup and service wiring for the gateway.

## Risks and edge cases
Documentation should stay aligned with the package's role as an internal service container.

## Test signals
Compilation and documentation generation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/FileSystemAccess.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/FileSystemAccess.java

## Purpose
`FileSystemAccess` defines the service API for authenticated Hadoop `FileSystem` access from HttpFS request handlers.

## Important APIs, types, and functions
`FileSystemExecutor<T>` encapsulates a filesystem operation. `execute(user, conf, executor)` runs managed operations. `createFileSystem(user, conf)` and `releaseFileSystem(fs)` expose unmanaged lifecycle control for streaming responses. `getFileSystemConfiguration()` returns a service-created configuration template.

## Control flow
The interface separates short managed operations from request-spanning filesystem handles that must be released later.

## State and persistence behavior
The interface owns no state. Implementations cache or count filesystem instances.

## Dependencies and integration points
`FileSystemAccessService` implements it. `FileSystemReleaseFilter` releases unmanaged handles after servlet processing.

## Risks and edge cases
Callers using `createFileSystem` must always call `releaseFileSystem`; otherwise cached filesystem counts and resources can leak.

## Test signals
`TestHttpFSMetrics` invokes `execute` with `FSCreate` and `FSAppend` operations through a mocked implementation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/FileSystemAccess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/FileSystemAccessException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/FileSystemAccessException.java

## Purpose
`FileSystemAccessException` reports validation, authentication, configuration, and execution failures from filesystem access.

## Important APIs, types, and functions
The nested `ERROR` enum covers missing service properties, Kerberos failure, executor errors, invalid non-service-created configurations, namenode validation, missing `fs.defaultFS`, health failures, wrapped generic messages, invalid auth mode, missing Hadoop config directory, and config load failures.

## Control flow
The class delegates all formatting and cause handling to `XException`.

## State and persistence behavior
Only exception metadata is stored.

## Dependencies and integration points
`FileSystemAccessService` throws these codes both directly and wrapped in `ServiceException` during service initialization.

## Risks and edge cases
Several error paths wrap broad exceptions, so callers may need to inspect causes for detailed Hadoop failures.

## Test signals
Tests that pass invalid versions/configurations or missing filesystem properties would assert these codes; this subset's metrics test avoids the failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/FileSystemAccessException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Groups.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Groups.java

## Purpose
`Groups` defines the service interface for resolving a user to Hadoop group names.

## Important APIs, types, and functions
It exposes `getGroups(String user)` returning `List<String>` and throwing `IOException`.

## Control flow
No behavior is defined beyond delegation.

## State and persistence behavior
The interface owns no state.

## Dependencies and integration points
`GroupsService` implements it with Hadoop `org.apache.hadoop.security.Groups`. Authentication and proxyuser checks can depend on group resolution.

## Risks and edge cases
Group resolution is environment-sensitive and can block or fail depending on configured mapping providers.

## Test signals
No direct tests in this subset; integration is through HttpFS authentication and proxy user flows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Groups.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Instrumentation.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Instrumentation.java

## Purpose
`Instrumentation` defines the metrics and runtime snapshot API for the HttpFS service framework.

## Important APIs, types, and functions
`Cron` measures operations with `start()` and `stop()`. `Variable<T>` supplies dynamic values. The service API increments counters, records cron timings, adds variables, adds one-second samplers, and returns a grouped snapshot map.

## Control flow
Implementations create cron objects around measured work, register variables/samplers, and expose a live snapshot for JSON rendering or diagnostics.

## State and persistence behavior
The interface defines in-memory metrics only. No durable persistence is implied.

## Dependencies and integration points
`InstrumentationService`, `SchedulerService`, and `FileSystemAccessService` use this API. `JSONProvider` and `JSONMapProvider` can serialize metrics-like maps and JSON-aware values.

## Risks and edge cases
The snapshot is typed as nested wildcard maps, so consumers need runtime knowledge of value types.

## Test signals
`TestHttpFSMetrics` verifies higher-level HttpFS metrics updates for create/append byte counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Instrumentation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Scheduler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Scheduler.java

## Purpose
`Scheduler` defines the background scheduling service API for HttpFS internal jobs.

## Important APIs, types, and functions
It exposes overloads for scheduling `Callable<?>` and `Runnable` tasks with delay, fixed delay interval, and `TimeUnit`.

## Control flow
Implementations run tasks periodically and decide how to handle failures and server status.

## State and persistence behavior
The interface owns no state. `SchedulerService` owns an executor.

## Dependencies and integration points
`InstrumentationService` uses the scheduler to sample metrics every second. `FileSystemAccessService` uses it to purge idle cached filesystem instances.

## Risks and edge cases
Scheduled tasks should tolerate repeated execution and exceptions because failures are logged and counted by the implementation.

## Test signals
No direct tests in this subset; service boot and filesystem cache purge wiring depend on this API.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/Scheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/hadoop/FileSystemAccessService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/hadoop/FileSystemAccessService.java

## Purpose
`FileSystemAccessService` implements authenticated Hadoop `FileSystem` access for HttpFS. It handles simple or Kerberos login, loads Hadoop configuration, validates target namenodes, creates proxy-user contexts, caches filesystem instances per user, and records instrumentation.

## Important APIs, types, and functions
Config keys include `authentication.type`, Kerberos principal/keytab, filesystem cache purge frequency/timeout, namenode whitelist, and Hadoop config directory. `execute()` validates a service-created configuration and `fs.defaultFS`, runs the executor inside a proxy `UserGroupInformation#doAs`, times the operation, and releases the filesystem. `createFileSystem()` and `releaseFileSystem()` manage unmanaged streaming handles. The nested `CachedFileSystem` tracks a `FileSystem`, active use count, last idle time, and timeout.

## Control flow
Initialization configures Hadoop security, loads `core-site.xml` and `hdfs-site.xml`, forces `fs.hdfs.impl.disable.cache=true`, marks the returned filesystem config with `FileSystemAccessService.created`, clears the server-side umask to `000`, and lowercases the whitelist. Post-init registers unmanaged-FS metrics and schedules periodic purging if timeout is positive.

## State and persistence behavior
State is in-memory: service Hadoop configuration, filesystem template configuration, whitelist, unmanaged count, cache map keyed by short user name, and purge timeout. It reads local Hadoop XML files and uses Hadoop filesystem clients but does not persist service metadata.

## Dependencies and integration points
It depends on Hadoop `Configuration`, `FileSystem`, `UserGroupInformation`, `FsPermission`, `VersionInfo`, `Instrumentation`, and `Scheduler`. It is configured as a default HttpFS service in `httpfs-default.xml` and used by servlet operations and release filters.

## Risks and edge cases
The per-user cache map intentionally retains entries forever; large user cardinality can grow the map. Missing `fs.defaultFS`, non-service-created configs, invalid whitelist authority, Kerberos login failure, or absent Hadoop config directory fail requests or boot. Unmanaged callers must release handles or counts and cached filesystems remain active.

## Test signals
`TestHttpFSMetrics` replaces this service with a subclass that returns a mocked `FileSystem`; its create/append tests verify that `execute()` wraps FS operations and metrics update correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/hadoop/FileSystemAccessService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/hadoop/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/hadoop/package-info.java

## Purpose
This descriptor documents the Hadoop service provider package.

## Important APIs, types, and functions
The package contains `FileSystemAccessService`, the concrete Hadoop-backed implementation of `FileSystemAccess`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The package bridges HttpFS service APIs to Hadoop security and filesystem clients.

## Risks and edge cases
Documentation should remain aligned if additional Hadoop-backed services are added.

## Test signals
Compilation and service integration tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/hadoop/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/instrumentation/InstrumentationService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/instrumentation/InstrumentationService.java

## Purpose
`InstrumentationService` is the in-memory metrics implementation for the HttpFS service framework. It tracks counters, timers, variables, sampled rates, JVM memory variables, environment, and system properties.

## Important APIs, types, and functions
`init()` creates concurrent maps and lock guards, initializes the snapshot map, and registers JVM memory variables. `createCron()`, `incr()`, `addCron()`, `addVariable()`, `addSampler()`, and `getSnapshot()` implement the interface. Nested `Cron` records own and total time, `Timer` keeps a ring buffer of recent cron values and JSON serialization, `VariableHolder` wraps live variables, `Sampler` maintains a rolling sum/rate, and `SamplersRunnable` samples every second.

## Control flow
Post-init obtains `Scheduler` and schedules sampler execution with zero delay and one-second interval when a scheduler is present. Metric containers are lazily created per group/name with `computeIfAbsent` under locks. Timers call `cron.end()` before storing values.

## State and persistence behavior
All state is in-memory and concurrent. Snapshot includes live `System.getenv()` and `System.getProperties()` maps plus dynamic metric structures. No metrics are written to disk.

## Dependencies and integration points
It extends `BaseService`, implements `Instrumentation`, uses the `Scheduler` service, Hadoop `Time`, JSON.simple, and Java concurrent primitives. `SchedulerService` and `FileSystemAccessService` record counters/timers through it.

## Risks and edge cases
`Timer#getValues()` assumes at least one cron has been added; reading a never-used timer could index `-1`. Re-adding a sampler with the same group/name reinitializes the sampler and appends it again to the sampling list. Snapshot exposes mutable live maps to consumers.

## Test signals
Indirect signals include scheduler instrumentation counters and `TestHttpFSMetrics` for higher-level byte and operation metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/instrumentation/InstrumentationService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/instrumentation/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/instrumentation/package-info.java

## Purpose
This package descriptor labels the instrumentation service package.

## Important APIs, types, and functions
The package contains `InstrumentationService`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The package implements the metrics API consumed by other HttpFS services.

## Risks and edge cases
Only documentation drift is relevant.

## Test signals
Compilation and service boot are the applicable signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/instrumentation/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/package-info.java

## Purpose
This descriptor documents the internal service-definition package for HttpFS.

## Important APIs, types, and functions
The package defines `FileSystemAccess`, `Groups`, `Instrumentation`, `Scheduler`, and `FileSystemAccessException`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
These interfaces are the contracts implemented by `org.apache.ozone.lib.service.*` concrete services and retrieved through `Server#get`.

## Risks and edge cases
Interface changes in this package have broad impact on service wiring.

## Test signals
Compilation and service-integration tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/scheduler/SchedulerService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/scheduler/SchedulerService.java

## Purpose
`SchedulerService` implements periodic background task execution for HttpFS services, with instrumentation and server-status gating.

## Important APIs, types, and functions
It reads `scheduler.threads` from service config, creates a `ScheduledThreadPoolExecutor`, and implements both `schedule(Callable, ...)` and `schedule(Runnable, ...)`. The callable scheduler wraps each run with counters for executions, skips, failures, and cron timing. `destroy()` shuts down the executor and waits up to 30 seconds.

## Control flow
If the server is `HALTED`, scheduled work is skipped and a `.skips` counter is incremented. Otherwise it increments `.execs`, starts a cron, invokes `call()`, records failures, and adds timing in a finally block. Scheduling uses fixed delay rather than fixed rate.

## State and persistence behavior
State is the scheduled executor and queued tasks. There is no durable persistence.

## Dependencies and integration points
It extends `BaseService`, depends on `Instrumentation`, wraps runnables with `RunnableCallable`, and is used by instrumentation sampling and filesystem cache purging.

## Risks and edge cases
Scheduling after shutdown throws `IllegalStateException`. A task that blocks can delay its own next run under fixed-delay semantics. Interrupted shutdown logs but does not restore the interrupt flag.

## Test signals
Indirect service boot and filesystem purge behavior depend on this service. Instrumentation counters provide runtime visibility into task execution/failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/scheduler/SchedulerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/scheduler/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/scheduler/package-info.java

## Purpose
This descriptor documents the scheduler service package.

## Important APIs, types, and functions
The package contains `SchedulerService`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The scheduler package supplies background execution for metrics sampling and filesystem cache purging.

## Risks and edge cases
Only documentation drift is relevant.

## Test signals
Compilation and service boot validate the descriptor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/scheduler/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/security/GroupsService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/security/GroupsService.java

## Purpose
`GroupsService` implements the HttpFS `Groups` interface using Hadoop's group-mapping subsystem.

## Important APIs, types, and functions
`init()` copies service-scoped configuration into a Hadoop `Configuration` and constructs `org.apache.hadoop.security.Groups`. `getInterface()` returns `Groups.class`. `getGroups(user)` delegates to Hadoop.

## Control flow
Initialization occurs during server boot. Requests later call `getGroups`, which may use Hadoop's configured cache and mapping provider.

## State and persistence behavior
State is one Hadoop `Groups` instance and its internal caches. No explicit persistence occurs.

## Dependencies and integration points
It extends `BaseService`, uses `ConfigurationUtils.copy`, and integrates with authentication/proxyuser paths that need group membership.

## Risks and edge cases
Behavior depends on Hadoop group mapping configuration and host environment. IO failures propagate to callers.

## Test signals
No direct tests in this subset; authentication integration tests would expose mapping failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/security/GroupsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/security/package-info.java

## Purpose
This package descriptor documents the security service implementation package.

## Important APIs, types, and functions
The package contains `GroupsService`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The package bridges HttpFS security contracts to Hadoop security utilities.

## Risks and edge cases
Documentation should remain aligned if additional security services are added.

## Test signals
Compilation and service boot are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/FileSystemReleaseFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/FileSystemReleaseFilter.java

## Purpose
`FileSystemReleaseFilter` guarantees that request-scoped unmanaged `FileSystem` instances are returned to `FileSystemAccess` after servlet processing, especially for streaming responses.

## Important APIs, types, and functions
It implements `Filter`, keeps a static thread-local `FileSystem`, exposes `setFileSystem(fs)`, and requires subclasses to implement `getFileSystemAccess()`.

## Control flow
`doFilter()` delegates to the chain in a try block, then in finally checks the thread-local, removes it, and calls `releaseFileSystem(fs)`.

## State and persistence behavior
State is a per-thread filesystem reference. No durable state is written.

## Dependencies and integration points
`HttpFSReleaseFilter` is the concrete gateway subclass. `FileSystemAccessService.createFileSystem` increments unmanaged count, and this filter should call release at request completion.

## Risks and edge cases
If streaming occurs on a different thread than the request filter thread, the thread-local release mechanism can miss the handle. If release throws, it propagates from the finally block.

## Test signals
No direct tests in this subset. Streaming read tests and unmanaged filesystem counters would reveal leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/FileSystemReleaseFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/HostnameFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/HostnameFilter.java

## Purpose
`HostnameFilter` resolves the remote client address to a canonical hostname and exposes it to downstream request processing through a thread-local.

## Important APIs, types, and functions
`doFilter()` reads `ServletRequest#getRemoteAddr`, resolves with `InetAddress.getByName(...).getCanonicalHostName()`, stores the result in `HOSTNAME_TL`, invokes the chain, and clears the thread-local. `get()` returns the current hostname.

## Control flow
Null or unresolvable remote addresses are logged and represented as `"???"`. Cleanup always runs in finally.

## State and persistence behavior
Only per-thread request context is stored. No persistence occurs.

## Dependencies and integration points
`MDCFilter` reads this thread-local to put `hostname` into SLF4J MDC. Both web descriptors map this filter to all requests.

## Risks and edge cases
Reverse DNS can add latency. The filter order in both web descriptors maps `MDCFilter` before `hostnameFilter`, so MDC will not see a hostname unless the container applies an ordering different from declaration order or mapping order is changed.

## Test signals
No direct tests in this subset. Request logging output would expose missing hostname MDC.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/HostnameFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/MDCFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/MDCFilter.java

## Purpose
`MDCFilter` enriches request logs by populating SLF4J MDC with request context.

## Important APIs, types, and functions
`doFilter()` clears MDC, reads `HostnameFilter.get()`, principal name, HTTP method, and path info, puts available values under `hostname`, `user`, `method`, and `path`, delegates to the chain, and clears MDC in finally.

## Control flow
The filter assumes the request is an `HttpServletRequest`. Null principal and path are tolerated.

## State and persistence behavior
State is MDC thread-local context for the current request only.

## Dependencies and integration points
It integrates servlet filters with SLF4J/reload4j log patterns. Web descriptors map it to all requests.

## Risks and edge cases
If it runs before `HostnameFilter`, hostname will be absent. Non-HTTP servlet requests would cause a class cast failure. Clearing MDC can remove context set by upstream filters.

## Test signals
No direct tests in this subset; log formatting and request traces are runtime signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/MDCFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/ServerWebApp.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/ServerWebApp.java

## Purpose
`ServerWebApp` binds the `Server` lifecycle to a servlet container. It resolves directories and HTTP authority from system properties and starts/stops the server from servlet context events.

## Important APIs, types, and functions
The constructor reads `name.home.dir`, optional config/log/temp dir properties, and calls the `Server` constructor. `contextInitialized()` calls `init()` and wraps `ServerException` as `RuntimeException`. `contextDestroyed()` calls `destroy()`. `getAuthority()` lazily resolves `name.http.hostname` and `name.http.port`.

## Control flow
Directory resolution happens during construction. Servlet startup calls server initialization. Authority resolution is synchronized and cached after the first call.

## State and persistence behavior
State is the inherited server state and cached `InetSocketAddress`. It reads system properties but does not persist data.

## Dependencies and integration points
`HttpFSServerWebApp` subclasses this type and is configured as the listener in both web descriptors. The server process launcher must set system properties such as `httpfs.home.dir`.

## Risks and edge cases
Missing `home.dir`, `http.hostname`, or `http.port` properties fail early. `HOME_DIR_TL` exists but has no setter in this file, so normal resolution relies on system properties. Invalid hostnames or non-numeric ports fail authority resolution.

## Test signals
`TestHttpFSMetrics` sets `httpfs.home.dir`, creates `HttpFSServerWebApp`, initializes it, replaces a service, and destroys it, exercising this lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/ServerWebApp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/package-info.java

## Purpose
This descriptor documents the servlet implementation details package.

## Important APIs, types, and functions
The package contains request filters and `ServerWebApp`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The package connects servlet containers to HttpFS server lifecycle, request logging, hostname context, and filesystem release.

## Risks and edge cases
Servlet filter ordering and lifecycle expectations are the main package-level concern.

## Test signals
Compilation and web descriptor integration validate the package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/Check.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/Check.java

## Purpose
`Check` provides small argument precondition helpers used throughout the HttpFS support framework.

## Important APIs, types, and functions
`notNull(obj, name)` rejects null values and returns the object. `notEmpty(str, name)` rejects null and empty strings and returns the string.

## Control flow
Each method throws `IllegalArgumentException` with a simple message on validation failure.

## State and persistence behavior
The utility has no state and a private constructor.

## Dependencies and integration points
It is used by `Server`, `BaseService`, `RunnableCallable`, `XException`, `ConfigurationUtils`, `FileSystemAccessService`, and `SchedulerService`.

## Risks and edge cases
`notEmpty` does not trim or reject whitespace-only strings. Callers needing non-blank semantics must add their own checks.

## Test signals
Indirect tests assert null/empty handling in service and rewrite code paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/Check.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/ConfigurationUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/ConfigurationUtils.java

## Purpose
`ConfigurationUtils` wraps common Hadoop `Configuration` copy, default injection, resolution, and XML loading operations used by the server framework.

## Important APIs, types, and functions
`copy(source, target)` overwrites target entries with all source entries. `injectDefaults(source, target)` sets only missing target keys. `resolve(conf)` creates a new configuration with values resolved through `conf.get(key)`. `load(conf, inputStream)` delegates to `Configuration#addResource`.

## Control flow
All methods validate required arguments. Iteration uses Hadoop `Configuration`'s entry iterator.

## State and persistence behavior
No static state exists. Methods mutate provided target configurations and read input streams via Hadoop configuration parsing.

## Dependencies and integration points
`Server` uses this class for default/site config merging. `BaseService` uses `resolve` before trimming service prefixes. `GroupsService` and `FileSystemAccessService` use it to copy scoped config.

## Risks and edge cases
`copy` and `injectDefaults` iterate effective configuration entries, which may include defaults depending on the source. `resolve` materializes substituted values, which is useful for services but can obscure original variable references.

## Test signals
Service boot and configuration-based behavior provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/ConfigurationUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/package-info.java

## Purpose
This descriptor labels the utility package.

## Important APIs, types, and functions
The package contains `Check` and `ConfigurationUtils`.

## Control flow
No executable behavior is present.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The utilities support configuration and validation across the server framework.

## Risks and edge cases
Utility behavior is broad-impact despite the small package size.

## Test signals
Compilation and indirect service initialization tests validate usage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/BooleanParam.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/BooleanParam.java

## Purpose
`BooleanParam` is a typed JAX-RS query parameter base for boolean values.

## Important APIs, types, and functions
It extends `Param<Boolean>`, parses case-insensitive `"true"` and `"false"`, and reports its domain as `"a boolean"`.

## Control flow
Invalid non-boolean strings throw `IllegalArgumentException`, which `Param.parseParam` wraps into a parameter-specific error message.

## State and persistence behavior
State is the inherited current value and parameter name.

## Dependencies and integration points
Concrete HttpFS parameter classes subclass it and are instantiated by `ParametersProvider`.

## Risks and edge cases
Only literal true/false values are accepted; numeric or yes/no aliases are rejected.

## Test signals
No direct tests here; request parameter parsing tests would verify invalid input mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/BooleanParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/EnumParam.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/EnumParam.java

## Purpose
`EnumParam` is a typed parameter base for single enum-valued request parameters.

## Important APIs, types, and functions
It stores the enum class, uppercases input with Hadoop `StringUtils`, resolves via `Enum.valueOf`, and formats the allowed domain as comma-joined enum constants.

## Control flow
Parsing is case-insensitive for ASCII-style enum names because input is uppercased before lookup.

## State and persistence behavior
State is the inherited value and the enum class reference.

## Dependencies and integration points
Used by concrete HttpFS parameter classes and `ParametersProvider`.

## Risks and edge cases
Enum names must match uppercased input exactly. Locale/format expectations are inherited from Hadoop `StringUtils.toUpperCase`.

## Test signals
Parameter-provider tests and WebHDFS operation parsing exercise this behavior indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/EnumParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/EnumSetParam.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/EnumSetParam.java

## Purpose
`EnumSetParam` parses comma-separated enum sets for request parameters.

## Important APIs, types, and functions
It extends `Param<EnumSet<E>>`, splits non-empty strings by comma, trims each token, uppercases it, and adds enum constants to an `EnumSet`. Static `toString(EnumSet)` serializes sets as comma-separated enum names. `toString()` returns `name=valueList`.

## Control flow
An empty string parses to an empty enum set rather than the default.

## State and persistence behavior
State is the inherited current enum set and enum class.

## Dependencies and integration points
Concrete WebHDFS parameters use it for options such as flag sets. `ParametersProvider` handles multi-value query parameters separately from comma-separated values.

## Risks and edge cases
Duplicate enum tokens collapse naturally in the set. Invalid tokens fail the entire parse. Serialized order follows enum declaration order.

## Test signals
No direct tests in this subset; operation parameter parsing would expose failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/EnumSetParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ExceptionProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ExceptionProvider.java

## Purpose
`ExceptionProvider` is the default JAX-RS exception mapper for HttpFS support classes.

## Important APIs, types, and functions
It implements `ExceptionMapper<Throwable>`. `toResponse()` maps all throwables to HTTP `BAD_REQUEST` using `HttpExceptionUtils.createJerseyExceptionResponse`. Protected helpers create responses, extract first-line messages, and log at debug level.

## Control flow
Subclasses can override status selection or logging. The base class always returns a Jersey exception response with status 400.

## State and persistence behavior
No mutable state is stored.

## Dependencies and integration points
Jersey discovers providers from `org.apache.ozone.lib.wsrs` as configured in web.xml. HttpFS-specific exception providers may extend or coexist with this mapper.

## Risks and edge cases
Mapping every throwable to bad request can hide server-side failures unless overridden. Debug-only logging may make production diagnostics depend on response bodies.

## Test signals
REST error response tests would exercise this mapper; none are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ExceptionProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/InputStreamEntity.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/InputStreamEntity.java

## Purpose
`InputStreamEntity` streams an input stream to a JAX-RS response while honoring offset/length and updating HttpFS bytes-read metrics.

## Important APIs, types, and functions
The constructor stores `InputStream`, offset, and length. `write(OutputStream)` skips the offset with `IOUtils.skipFully`, copies all remaining bytes when `len == -1` or exactly `len` bytes otherwise via `FSOperations.copyBytes`, then increments `HttpFSServerMetrics` bytes-read when metrics are available.

## Control flow
The stream copy is synchronous inside Jersey's `StreamingOutput` callback. Metrics are updated after copy completion.

## State and persistence behavior
State is the stream and range parameters. It does not close the input stream directly in this file; stream lifecycle is owned by callers/filters.

## Dependencies and integration points
It integrates Hadoop IO utilities, HttpFS copy buffer logic, `HttpFSServerWebApp`, and metrics. It is used for read/open-style responses.

## Risks and edge cases
Invalid offsets can fail during skip. If copy fails, metrics are not incremented. The filesystem backing the stream must remain open until streaming completes, which is why release filters are important.

## Test signals
Read metrics tests would validate `incrBytesRead`; this subset's metrics test covers write metrics through create/append.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/InputStreamEntity.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/IntegerParam.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/IntegerParam.java

## Purpose
`IntegerParam` is a typed request parameter base for integer values.

## Important APIs, types, and functions
It extends `Param<Integer>`, parses with `Integer.parseInt`, and reports its domain as `"an integer"`.

## Control flow
Parsing errors propagate to `Param.parseParam` and become parameter-specific `IllegalArgumentException`s.

## State and persistence behavior
State is inherited parameter name and value.

## Dependencies and integration points
Concrete HttpFS parameter classes use it for numeric query parameters.

## Risks and edge cases
Only base-10 signed Java integer syntax is accepted. Overflow is rejected by `Integer.parseInt`.

## Test signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/IntegerParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/JSONMapProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/JSONMapProvider.java

## Purpose
`JSONMapProvider` is a Jersey message-body writer for serializing Java `Map` responses as UTF-8 JSON.

## Important APIs, types, and functions
It is annotated with `@Provider` and produces `application/json; charset=utf-8`. `isWriteable()` accepts `Map` subclasses, `getSize()` returns `-1`, and `writeTo()` writes with JSON.simple `JSONObject.writeJSONString`, appends a line separator, and flushes.

## Control flow
Serialization is one-pass to the response output stream through an UTF-8 writer.

## State and persistence behavior
No mutable state exists beyond the static line separator.

## Dependencies and integration points
Jersey loads it from the `org.apache.ozone.lib.wsrs` provider package in both web descriptors. It can serialize instrumentation snapshots and REST response maps.

## Risks and edge cases
Map contents must be JSON.simple-compatible. It does not set response headers beyond provider annotations.

## Test signals
REST response tests would validate JSON output; none are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/JSONMapProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/JSONProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/JSONProvider.java

## Purpose
`JSONProvider` is a Jersey message-body writer for objects implementing JSON.simple `JSONStreamAware`.

## Important APIs, types, and functions
The provider produces UTF-8 JSON. `isWriteable()` accepts `JSONStreamAware`, `getSize()` returns `-1`, and `writeTo()` invokes `writeJSONString`, writes a line separator, and flushes.

## Control flow
Serialization delegates to the object, allowing timers, variables, and samplers to stream their own JSON.

## State and persistence behavior
No mutable state is stored.

## Dependencies and integration points
It integrates with `InstrumentationService.Timer`, `VariableHolder`, and `Sampler`, which implement `JSONStreamAware`.

## Risks and edge cases
Any exception in the object's JSON writer propagates as an IO/JAX-RS failure. Objects control their own JSON shape.

## Test signals
REST or instrumentation endpoint tests would validate behavior; none are included here.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/JSONProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/LongParam.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/LongParam.java

## Purpose
`LongParam` is a typed parameter base for long integer values.

## Important APIs, types, and functions
It extends `Param<Long>`, parses with `Long.parseLong`, and reports its domain as `"a long"`.

## Control flow
Invalid or overflowing values are converted to parameter-specific `IllegalArgumentException`s by `Param`.

## State and persistence behavior
State is inherited parameter name and value.

## Dependencies and integration points
Concrete HttpFS parameters use it for lengths, offsets, block sizes, or timestamps.

## Risks and edge cases
Only signed base-10 Java long syntax is accepted.

## Test signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/LongParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/Param.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/Param.java

## Purpose
`Param<T>` is the generic base class for typed JAX-RS query parameters in HttpFS.

## Important APIs, types, and functions
It stores the query parameter name and current value. `parseParam(str)` parses only non-blank input using subclass `parse`, keeps the existing default for blank input, and formats invalid-value errors with `getDomain()`. `value()` returns the parsed/default value.

## Control flow
Subclasses define both domain text and parsing. The base parser catches any exception and throws a new `IllegalArgumentException`.

## State and persistence behavior
Each parameter instance is mutable: parsing updates `value`. No persistence occurs.

## Dependencies and integration points
`ParametersProvider` instantiates concrete `Param` classes per request and stores them in `Parameters`.

## Risks and edge cases
Mutable parameter instances require fresh objects for multi-value parameters; `ParametersProvider` explicitly creates a new one after each parsed value. Blank values keep defaults, which may differ from explicit empty semantics in subclasses such as `StringParam`.

## Test signals
Parameter parsing tests and WebHDFS request validation are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/Param.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/Parameters.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/Parameters.java

## Purpose
`Parameters` is the parsed request-parameter container produced by `ParametersProvider`.

## Important APIs, types, and functions
The constructor accepts a map from parameter name to a list of `Param<?>`. `get(name, klass)` returns the first value cast through the requested parameter class. `getValues(name, klass)` returns all non-null values for repeated parameters.

## Control flow
Lookup is name-based. Missing or empty parameter lists return null or an empty list.

## State and persistence behavior
State is the parsed parameter map for one request. No persistence occurs.

## Dependencies and integration points
HttpFS REST resources use this class to retrieve typed query parameter values after provider parsing.

## Risks and edge cases
The `klass` argument is not actively checked against stored instances beyond unchecked casts. Supplying the wrong class can cause runtime `ClassCastException`.

## Test signals
REST operation tests would verify required/default/multi-value parameter behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/Parameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ParametersProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ParametersProvider.java

## Purpose
`ParametersProvider` parses servlet request query parameters according to an operation-specific parameter definition map.

## Important APIs, types, and functions
The constructor receives the driver parameter name, enum class for operations, and a map from operation enum to parameter classes. `get(HttpServletRequest)` reads the driver parameter, resolves the enum, validates support, instantiates each expected `Param` class with a default constructor, parses all supplied values, and returns a `Parameters` container.

## Control flow
Parsing is operation-driven. For each declared parameter, absent values produce one default parameter instance; present repeated values produce one parsed instance per value.

## State and persistence behavior
Provider state is immutable definition data. Request parsing creates transient maps and parameter objects.

## Dependencies and integration points
HttpFS parameter providers use it to enforce supported operations and typed query parameters before resource handlers execute.

## Risks and edge cases
`queryString.get(driverParam)[0]` can throw if the driver parameter is absent because the null check occurs after indexing. Parameter classes must have public no-arg constructors. All request parameter values are trusted as arrays from the servlet API.

## Test signals
Invalid/missing operation and bad-parameter REST tests should cover this behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ParametersProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ShortParam.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ShortParam.java

## Purpose
`ShortParam` is a typed parameter base for short integer values, with optional radix support.

## Important APIs, types, and functions
Constructors accept parameter name, default value, and optional radix defaulting to 10. `parse` uses `Short.parseShort(str, radix)`. `getDomain()` returns `"a short"`.

## Control flow
Invalid syntax or overflow is handled by the base `Param` error wrapper.

## State and persistence behavior
State includes inherited name/value and the configured radix.

## Dependencies and integration points
Concrete permission-like or short-valued HttpFS parameters can use it.

## Risks and edge cases
Domain text does not mention non-decimal radix, so error messages may be vague for octal/hex subclasses.

## Test signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/ShortParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/StringParam.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/StringParam.java

## Purpose
`StringParam` is a typed parameter base for string values, optionally constrained by a regex pattern.

## Important APIs, types, and functions
Constructors accept name, default value, and optional `Pattern`. The pattern constructor calls `parseParam(defaultValue)` to validate/default-normalize. `parseParam` trims non-null input and parses only non-empty strings. `parse` enforces the pattern when present and returns the string. `getDomain()` returns either `"a string"` or the regex.

## Control flow
Unlike base `Param`, this parser treats empty and null strings as "keep current value" after trimming.

## State and persistence behavior
State is inherited name/value plus the optional compiled pattern.

## Dependencies and integration points
Concrete HttpFS path/user/query parameters subclass it.

## Risks and edge cases
Default values are validated at construction. Whitespace is trimmed, so significant leading/trailing spaces cannot be represented.

## Test signals
REST parameter parsing tests would cover regex failures and default handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/StringParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/package-info.java

## Purpose
This descriptor documents the JAX-RS support package.

## Important APIs, types, and functions
The package provides typed query parameters, request parameter containers/providers, JSON message writers, streaming entities, and exception mapping.

## Control flow
No executable behavior is present in the descriptor.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
Both web descriptors register this package with Jersey provider scanning alongside HttpFS server resources.

## Risks and edge cases
Changes here affect REST request parsing and response serialization across the gateway.

## Test signals
REST integration tests and Jersey provider discovery validate this package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/wsrs/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/resources/httpfs-default.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/resources/httpfs-default.xml

## Purpose
`httpfs-default.xml` is the default HttpFS gateway configuration loaded from the classpath by `Server`. It defines HTTP binding defaults, service classes, authentication defaults, delegation token settings, filesystem access settings, and access mode.

## Important APIs, types, and functions
Key properties include `httpfs.http.port=14000`, `httpfs.http.hostname=0.0.0.0`, admin ACLs, SSL toggle, Hadoop HTTP thread/header/temp settings, `httpfs.buffer.size`, `httpfs.services`, Kerberos realm/host interpolation, Hadoop HTTP authentication settings, proxyuser examples, delegation token intervals, `httpfs.hadoop.authentication.*`, filesystem cache purge frequency/timeout, and `httpfs.access.mode`.

## Control flow
During server initialization, this file is loaded as defaults and site configuration or system properties overlay it. The `httpfs.services` list controls service startup order: instrumentation, scheduler, groups, then filesystem access.

## State and persistence behavior
The file is static configuration. It does not store runtime state but supplies defaults for in-memory server/service configuration.

## Dependencies and integration points
It references classes in this subset and Hadoop HTTP authentication keys. `FileSystemAccessService` consumes the `httpfs.hadoop.*` scoped keys after `BaseService` trims prefixes.

## Risks and edge cases
Defaults use simple authentication and local keytab/principal placeholders, so production deployments must override security settings. The access-mode description contains a `FORBIDDED` typo but behavior is implemented elsewhere. Service order matters because dependencies require instrumentation and scheduler before filesystem access.

## Test signals
`TestHttpFSMetrics` initializes `HttpFSServerWebApp`, causing this default config to load and services to start from the configured service list.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/resources/httpfs-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/resources/webapps/webhdfs/WEB-INF/web.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/resources/webapps/webhdfs/WEB-INF/web.xml

## Purpose
This web descriptor configures the `webhdfs` webapp variant of the HttpFS gateway.

## Important APIs, types, and functions
It registers `HttpFSServerWebApp` as a listener, a Jersey `ServletContainer` scanning `org.apache.ozone.fs.http.server,org.apache.ozone.lib.wsrs`, maps the servlet to `/webhdfs/*`, and configures auth, MDC, hostname, upload content-type, and filesystem release filters.

## Control flow
Servlet context startup initializes the server. All requests pass through the mapped filters and then reach Jersey resources under `/webhdfs/*`.

## State and persistence behavior
The descriptor is deployment metadata only. Runtime state is owned by the listener, filters, and servlet.

## Dependencies and integration points
It wires classes from the HttpFS server package and support classes in this subset. It is distinct from the main webapp descriptor mainly by URL pattern.

## Risks and edge cases
Filter mapping order places `MDCFilter` before `hostnameFilter`, so MDC may not include hostname. Mapping filters to `*` rather than a slash pattern follows the existing descriptor style but should be validated with the target servlet container.

## Test signals
Webapp integration tests or container startup validate descriptor correctness; this subset has no direct descriptor test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/resources/webapps/webhdfs/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/sbin/httpfs.sh -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/sbin/httpfs.sh

## Purpose
`httpfs.sh` is a deprecated compatibility launcher for the HttpFS server. It forwards commands to `hdfs`.

## Important APIs, types, and functions
`print_usage` emits `run|start|status|stop` usage. The script maps `run` to `hdfs httpfs` and `start|stop|status` to `hdfs --daemon <command> httpfs`. It locates `hdfs` under `$HADOOP_HOME/bin` or relative `../bin`.

## Control flow
The script prints a deprecation warning, validates arguments, translates the subcommand, resolves the binary directory, and `exec`s `hdfs` with translated arguments.

## State and persistence behavior
It does not persist state. Daemon state is managed by the delegated `hdfs` command.

## Dependencies and integration points
It depends on Bash and a Hadoop installation layout. It preserves older operational entrypoints while directing users to `hdfs [--daemon ...] httpfs`.

## Risks and edge cases
If neither `$HADOOP_HOME/bin/hdfs` nor relative `../bin/hdfs` exists, exec fails. Unknown commands exit 1. Zero arguments print usage and exit with the shell default success status from `exit`.

## Test signals
Shell command tests would verify argument translation and deprecation output; none are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/sbin/httpfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/webapp/WEB-INF/web.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/webapp/WEB-INF/web.xml

## Purpose
This is the main HttpFS webapp descriptor, wiring server startup, Jersey resources, and request filters.

## Important APIs, types, and functions
It registers `HttpFSServerWebApp`, Jersey `ServletContainer` scanning `org.apache.ozone.fs.http.server,org.apache.ozone.lib.wsrs`, maps the servlet to `/*`, and maps authentication, MDC, hostname, upload content-type, and filesystem release filters to all requests.

## Control flow
The listener initializes/destroys the server with the servlet context. Requests pass through filters before Jersey dispatch.

## State and persistence behavior
The file is static deployment metadata only.

## Dependencies and integration points
It binds web container configuration to the service framework and REST provider packages. Compared with `resources/webapps/webhdfs/WEB-INF/web.xml`, this variant exposes the Jersey servlet at the app root.

## Risks and edge cases
The same filter-order concern exists: MDC is configured before hostname. Root mapping means static or auxiliary paths in the same webapp may also hit Jersey unless separately handled.

## Test signals
Container integration and REST endpoint tests validate this descriptor; no direct test is present here.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/webapp/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/test/java/org/apache/ozone/fs/http/server/metrics/TestHttpFSMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/test/java/org/apache/ozone/fs/http/server/metrics/TestHttpFSMetrics.java

## Purpose
`TestHttpFSMetrics` verifies that HttpFS create and append operations increment operation counters and written-byte metrics.

## Important APIs, types, and functions
The suite uses `HttpFSServerWebApp`, `HttpFSServerMetrics`, `FileSystemAccess`, `FileSystemAccessService`, `FSOperations.FSCreate`, and `FSOperations.FSAppend`. `MockFileSystemAccessService` overrides `createFileSystem` and `closeFileSystem` to use a mocked Hadoop `FileSystem`.

## Control flow
`@BeforeAll` creates temp home/log/conf/temp directories and sets `httpfs.home.dir`. `@BeforeEach` creates a service-created `Configuration`, initializes the web app, replaces filesystem access with the mock service, obtains metrics, and creates a test UGI. Tests stub `mockFs.create` or `mockFs.append`, execute the corresponding FS operation through `fsAccess.execute`, and assert metric increments.

## State and persistence behavior
The server lifecycle and metrics are in-memory. Temporary directories satisfy server directory validation. No real filesystem data is written because the Hadoop filesystem is mocked.

## Dependencies and integration points
This test covers the integration between server boot, service replacement, filesystem execution, FS operation implementations, and metrics counters.

## Risks and edge cases
Static mocks are shared across tests; stubbing interactions must remain isolated. The test shuts metrics down and destroys the singleton web app after each test.

## Test signals
Signals are exact increments: create/append operation counters increase by one and bytes-written increases by four for the `"test"` input.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/test/java/org/apache/ozone/fs/http/server/metrics/TestHttpFSMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/iceberg/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclude file is present for the Ozone Iceberg module.

## Important APIs, types, and functions
It declares an empty `<FindBugsFilter>` root, meaning no module-specific suppressions are currently configured.

## Control flow
No executable behavior is present.

## State and persistence behavior
The file is static build configuration.

## Dependencies and integration points
`iceberg/pom.xml` references this file from the `spotbugs-maven-plugin` configuration.

## Risks and edge cases
An empty filter is useful as a stable plugin path but can hide the fact that no suppressions exist. Future suppressions should be tightly scoped.

## Test signals
SpotBugs execution validates XML parsing and absence/presence of suppressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/iceberg/pom.xml

## Purpose
This Maven POM defines the `ozone-iceberg` module, which packages Apache Ozone integration utilities for Iceberg tables.

## Important APIs, types, and functions
The module inherits from the Ozone parent, packages a jar, and overrides `maven.compiler.release` to 11 because Iceberg 1.10+ uses Java 11 bytecode. Dependencies include Picocli, Avro, Hadoop common, Iceberg API/core/ORC/Parquet, Ozone CLI/common/filesystem artifacts, Parquet column, SLF4J, Hadoop MapReduce runtime, and reload4j runtime.

## Control flow
Build-time behavior disables annotation processing with `maven-compiler-plugin` and configures SpotBugs with the module exclude filter, forked execution, and 2048 MB heap.

## State and persistence behavior
The POM is build metadata. It does not store runtime state.

## Dependencies and integration points
The dependency set supports `IcebergCommand`, `RewriteTablePathCommand`, metadata rewriting, manifest IO, position-delete readers/writers, and Ozone filesystem access at runtime.

## Risks and edge cases
The POM contains many exclusions to avoid dependency conflicts, especially HTTP client, checker, roaring bitmap, Jersey, JAXB, YARN, Avro duplication, and Jetty websocket artifacts. Version drift with Iceberg, Avro, ORC, Parquet, or Hadoop can break binary compatibility.

## Test signals
Module compilation and `TestRewriteTablePathOzoneAction` are the primary signals. SpotBugs uses the empty exclude file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/IcebergCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/IcebergCommand.java

## Purpose
`IcebergCommand` is the Picocli root command for Ozone Iceberg table utilities.

## Important APIs, types, and functions
The `@Command` annotation names the command `ozone iceberg`, adds alias `iceberg`, uses `HddsVersionProvider`, enables standard help options, and registers `RewriteTablePathCommand` as a subcommand. `main` runs the command through `GenericCli`.

## Control flow
Picocli dispatches subcommands; this class only boots the CLI.

## State and persistence behavior
No runtime state is stored by this class.

## Dependencies and integration points
It extends HDDS `GenericCli`, so it inherits Ozone configuration and command execution behavior. Tests execute `new IcebergCommand().getCmd().execute(...)`.

## Risks and edge cases
Command naming and aliases must remain stable for users and scripts. Adding subcommands requires updating the annotation.

## Test signals
`TestRewriteTablePathOzoneAction` uses this command to run the `rewrite-path` subcommand and assert exit code/output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/IcebergCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathCommand.java

## Purpose
`RewriteTablePathCommand` is the CLI front end for rewriting Iceberg table paths during Ozone-backed table migration.

## Important APIs, types, and functions
Required options are `--table-location`, `--source-prefix`, and `--target-prefix`. Optional flags include `--staging`, `--start-version`, `--end-version`, and `--threads` defaulting to 10. `call()` loads the table with `HadoopTables(getOzoneConf())`, creates `RewriteTablePathOzoneAction`, applies options, executes, and prints the latest version, staging location, and file-list location.

## Control flow
The command prints progress, loads the Iceberg table, configures the action fluently, executes it, and returns null on success.

## State and persistence behavior
State is Picocli-populated option fields. The command itself does not write files, but the action writes staged metadata/manifests and file-list output.

## Dependencies and integration points
It extends `AbstractSubcommand` for output/configuration and uses Iceberg `HadoopTables` and `RewriteTablePath`.

## Risks and edge cases
The help text says zero threads uses default 10, but the command passes zero through to the action; the action creates a fixed thread pool with the provided value, so zero would fail. Input strings are trimmed only for table loading, not prefixes.

## Test signals
`TestRewriteTablePathOzoneAction` invokes this command and asserts output contains startup, loaded table, staging, and file-list lines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathOzoneAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathOzoneAction.java

## Purpose
`RewriteTablePathOzoneAction` implements Iceberg's `RewriteTablePath` for Ozone-backed tables. It stages rewritten metadata JSON files, manifest lists, manifests, and position delete files while producing a CSV copy plan from staged paths to target paths.

## Important APIs, types, and functions
Fluent methods set source/target prefixes, start/end metadata versions, and staging location. `execute()` validates inputs, creates a fixed thread pool, runs `rebuildMetadata()`, and shuts down the pool. Major helpers include `validateVersion`, `rewriteVersionFiles`, `manifestsToRewrite`, `rewriteManifestLists`, `rewriteManifests`, `rewritePositionDeletes`, `positionDeletesReader`, and `positionDeletesWriter`.

## Control flow
Execution validates non-empty distinct prefixes, resolves end version to current metadata when omitted, validates optional start/end file names against current metadata logs and file existence, and defaults staging under the current metadata directory. It rewrites version metadata first using Iceberg `RewriteTablePathUtil.replacePaths`, computes delta snapshots, collects manifests from valid snapshots in bounded parallel batches, rewrites manifest lists and manifests, then rewrites referenced position-delete files.

## State and persistence behavior
State includes configured prefixes, version paths, staging dir, thread count, executor, and table reference. Persistent side effects are staged rewritten files and a `file-list` CSV in staging. The table is not committed by this action; the copy plan instructs a follow-up copy from staging to target.

## Dependencies and integration points
It depends heavily on Iceberg metadata, manifests, table operations, Avro/Parquet/ORC readers and writers, `RewriteTablePathUtil`, and `FileIO`. It integrates with `RewriteTablePathCommand` and Ozone/Hadoop table loading.

## Risks and edge cases
Partition statistics files are explicitly unsupported. Position delete rewriting can change file size after manifests have already been rewritten; the code documents this as a known Iceberg limitation that can affect catalogs using manifest file sizes. Thread count is not normalized, so zero or negative values can fail. Missing manifest lists produce a wrapped runtime failure advising an earlier version.

## Test signals
`TestRewriteTablePathOzoneAction` covers full and bounded version rewrites, default staging, missing/unknown/deleted versions, stats-file copy-plan validation, partition-stat rejection, missing manifest-list errors, unsupported formats, and AVRO/ORC/PARQUET position-delete round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathOzoneAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathOzoneUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathOzoneUtils.java

## Purpose
`RewriteTablePathOzoneUtils` contains helper functions for the Ozone Iceberg rewrite action.

## Important APIs, types, and functions
`statsFileCopyPlan` pairs before/after `StatisticsFile` paths after validating equal count and size. `fileExist` handles blank/null paths and delegates to Iceberg `FileIO`. `getMetadataLocation` derives the metadata directory from current metadata file location. `checkNonNullNonEmpty` enforces non-null/non-blank strings. `saveFileList` writes copy pairs to `stagingDir + "file-list"`. `writeAsCsv` writes UTF-8 comma-separated pairs. `snapshotSet` returns metadata snapshots or an empty set.

## Control flow
The utility methods are stateless and fail fast on invalid invariants. CSV writing wraps IO failures as Iceberg `RuntimeIOException`.

## State and persistence behavior
Only `saveFileList`/`writeAsCsv` persist data, creating or overwriting the file-list output through Iceberg `OutputFile`.

## Dependencies and integration points
The action uses these helpers for validation, staging defaults, statistics copy planning, and final copy-plan persistence.

## Risks and edge cases
CSV output does not escape commas in paths. `getMetadataLocation` requires a file separator in metadata file location. Stats-file pairing is positional and assumes Iceberg preserves list order after path replacement.

## Test signals
Tests cover empty stats, mismatched count, mismatched size, valid path pairs, default staging metadata location, and file-list parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathOzoneUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/package-info.java

## Purpose
This package descriptor documents Apache Ozone integration with Apache Iceberg.

## Important APIs, types, and functions
The package contains the CLI root command, rewrite-path subcommand, Ozone rewrite action, and helper utilities.

## Control flow
No executable behavior is present in the descriptor.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The package bridges Ozone CLI/configuration with Iceberg table metadata and file IO.

## Risks and edge cases
Package-level compatibility depends on Iceberg APIs and Ozone filesystem dependencies declared by the module POM.

## Test signals
Compilation and `TestRewriteTablePathOzoneAction` validate the package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/test/java/org/apache/hadoop/ozone/iceberg/TestRewriteTablePathOzoneAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/test/java/org/apache/hadoop/ozone/iceberg/TestRewriteTablePathOzoneAction.java

## Purpose
`TestRewriteTablePathOzoneAction` validates the Iceberg path-rewrite CLI and action across full-table rewrites, version windows, validation failures, statistics handling, manifest-list failures, and position-delete IO formats.

## Important APIs, types, and functions
The suite uses `IcebergCommand`, `RewriteTablePathOzoneAction`, `RewriteTablePathOzoneUtils`, Iceberg `HadoopTables`, `TableMetadata`, `StaticTableOperations`, manifest readers, `DataFiles`, position delete writers/readers, and `RewriteTablePathUtil`. Helpers create a local table, read the generated CSV file-list, and assert internal paths in staged metadata and manifests.

## Control flow
Setup creates a temporary file-backed Iceberg table with four append commits and two row-delta commits containing position-delete files, then captures stdout/stderr. CLI tests run `rewrite-path` with source/target/staging and optional start/end/thread flags. Assertion helpers inspect staged metadata JSON, manifest lists, manifests, and staged delete files to verify paths now start with the target prefix while preserving expected file names.

## State and persistence behavior
Tests create real local Iceberg metadata, data-file metadata entries, delete files, staged rewritten artifacts, and file-list CSVs under JUnit temp directories. Table data files are represented by metadata entries except position delete files, which are physically written.

## Dependencies and integration points
The tests exercise Picocli command dispatch, Ozone configuration, Iceberg metadata operations, manifest AVRO IO, Parquet position delete IO, ORC/AVRO/PARQUET delete reader/writer round trips, and action error handling.

## Risks and edge cases
Covered risks include missing prefixes, identical source/target, unknown or deleted start/end metadata versions, unsupported partition statistics, missing manifest lists, unsupported file formats, and internal path rewrite completeness. The suite also documents the generated staging location contract.

## Test signals
Strong signals are exact copy-plan target sets, target-prefix assertions inside every staged artifact type, expected exception messages, successful command exit code, and position-delete row round-trip checks for supported formats.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/test/java/org/apache/hadoop/ozone/iceberg/TestRewriteTablePathOzoneAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclude file is present for the Ozone Insight module.

## Important APIs, types, and functions
It contains an empty `<FindBugsFilter>` root and no suppression matches.

## Control flow
No executable behavior is present.

## State and persistence behavior
The file is static build configuration.

## Dependencies and integration points
The corresponding module build can reference this file as its SpotBugs exclude filter.

## Risks and edge cases
An empty filter has no suppressive effect but provides a stable path for future scoped exclusions.

## Test signals
SpotBugs execution or XML validation confirms the file is well-formed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/dev-support/findbugsExcludeFile.xml -->
