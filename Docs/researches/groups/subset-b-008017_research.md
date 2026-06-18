# Research Group: subset-b-008017

This grouped report covers the requested Apache Ozone HDDS event, HTTP, upgrade, and utility source files. Each section is source-tree aligned and delimited for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventExecutorMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventExecutorMetrics.java

Purpose: `EventExecutorMetrics` is the Hadoop Metrics2 source used by event executors in `org.apache.hadoop.hdds.server.events`. It records executor lifecycle counters for queued, scheduled, successful, failed, dropped, long-running, and long-queue-wait events.

Important APIs/types/functions: the constructor accepts a metrics source `name` and `description`, creates a `MetricsRegistry`, and calls `init()`. `init()` registers this instance with `DefaultMetricsSystem`; `unregister()` removes the source. `getMetrics()` snapshots the registry into a `MetricsRecordBuilder`. Public increment methods mutate the `MutableCounterLong` fields, and getters expose counter values to executor implementations and tests.

Control flow: executors create one metrics object when they are constructed, increment counters around enqueue/schedule/handler execution, and unregister during close. Metrics fields are injected by the Metrics2 annotation machinery when the source is registered.

State and persistence: all state is in-process Metrics2 counter state; there is no durable persistence. Source names must remain unique in the default metrics system or registration/unregistration collisions can occur.

Dependencies/integration: used by `SingleThreadExecutor` and `FixedThreadPoolWithAffinityExecutor`; exposed through Hadoop Metrics2 and consumed by Prometheus export via the HTTP metrics sink path. It depends on `DefaultMetricsSystem`, `MetricsRegistry`, `MetricsSource`, and `MutableCounterLong`.

Risks: duplicate registrations with the same source name may overwrite or fail depending on Metrics2 behavior. `incrementDropped(int)` accepts any integer, so callers should pass non-negative drop counts. Metrics fields are package-initialized by Metrics2 registration, so using an unregistered object in isolation would leave counters unset.

Test signals: event queue tests assert executor counters indirectly through executor APIs; `FixedThreadPoolWithAffinityExecutor` tests cover dropped/queued/scheduled semantics. Metrics correctness is also visible through integration with the HTTP Prometheus metrics path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventExecutorMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventHandler.java

Purpose: `EventHandler<PAYLOAD>` is the functional callback contract for consumers of `EventQueue` events. It lets event processors react to a typed payload and optionally publish follow-on events through the supplied `EventPublisher`.

Important APIs/types/functions: the sole method is `onMessage(PAYLOAD payload, EventPublisher publisher)`. The interface is annotated with `@FunctionalInterface`, so handlers can be lambdas, method references, or concrete classes.

Control flow: `EventQueue.fireEvent()` finds registered handlers and passes each handler to an `EventExecutor`. The executor controls threading and calls `onMessage`; handlers can invoke `publisher.fireEvent()` to build event chains.

State and persistence: the interface stores no state. Implementations may hold component state, and their thread-safety expectations depend on the executor. The Javadoc says event executors should guarantee a handler implementation is called from one thread, but custom executors must preserve that expectation themselves.

Dependencies/integration: implemented broadly across SCM, Recon, container, and safe-mode code paths. Integrates with `EventPublisher`, `EventExecutor`, `SingleThreadExecutor`, and `FixedThreadPoolWithAffinityExecutor`.

Risks: handler exceptions are caught and counted by executor implementations, but caller-visible failure propagation is intentionally absent. Handlers that publish recursive events can create long asynchronous chains, so tests use `EventQueue.processAll()` to drain them.

Test signals: `TestEventQueue`, `TestEventQueueChain`, and many SCM/Recon tests register lambdas or handler classes and verify asynchronous dispatch, chained events, and executor isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventPublisher.java

Purpose: `EventPublisher` is the producer-facing event bus contract. It abstracts publication so event handlers and components can emit typed events without depending directly on `EventQueue`.

Important APIs/types/functions: `fireEvent(EVENT_TYPE event, PAYLOAD payload)` is generic over payload and event type where `EVENT_TYPE extends Event<PAYLOAD>`. This keeps event identifiers and payload classes paired at compile time.

Control flow: `EventQueue` implements this interface. Handler code receives an `EventPublisher` and can publish additional events, creating asynchronous event chains. Other components may mock this interface in tests when only publication side effects matter.

State and persistence: the interface has no state or persistence. Implementations define queueing, threading, and failure behavior.

Dependencies/integration: consumed by `EventHandler`, `EventWatcher`, SCM handlers, container command handlers, and tests. The main implementation is `EventQueue`.

Risks: because publication is asynchronous in `EventQueue`, callers cannot infer completion from a return. Type safety only applies at compile time; raw types in `EventQueue` internals mean mismatched custom registrations can still cause runtime issues.

Test signals: mocked or real `EventPublisher` instances appear in SCM and container tests; `TestEventQueueChain` verifies follow-on publication from handlers through this contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventPublisher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventQueue.java

Purpose: `EventQueue` is HDDS/Ozone's simple asynchronous event bus. It maps `Event` identifiers to one or more `(EventExecutor, EventHandler)` registrations and routes published payloads to the matching handlers.

Important APIs/types/functions: constructors optionally accept a thread-name prefix. `addHandler(event, handler)` creates a `SingleThreadExecutor`; `addHandler(event, executor, handler)` installs a caller-provided executor after validating its name. `fireEvent()` publishes payloads. `processAll(timeout)` is a testing-only drain helper. `close()` stops the queue and closes all distinct executors. `setSilent()` suppresses warnings for unhandled events. `getExecutorName()` derives executor names from event and handler names.

Control flow: handlers are stored in `Map<Event, Map<EventExecutor, List<EventHandler>>>`. On publication, the queue increments event counters, finds the executor map for the event, logs payload details at trace/debug levels, and invokes `executor.onMessage(handler, payload, this)` for each handler. `processAll()` repeatedly inspects each executor's queued/successful/failed counters until all executors appear idle or timeout expires.

State and persistence: state is fully in-memory and guarded only by coarse lifecycle flags; registration and publication are not backed by durable storage. `isRunning` prevents new registrations and publications after `close()`.

Dependencies/integration: depends on Jackson for trace serialization, protobuf support for `Message`, Hadoop `Time`, Guava preconditions, and SCM network classes for a mixin that avoids circular `DatanodeDetails` parent serialization. It is the common publisher used by SCM, Recon, safe mode rules, node/container/pipeline handlers, and tests.

Risks: raw collection usage weakens type safety at dispatch. `payload.getClass()` is used for debug logging, so a null payload can fail when debug is enabled. Executor names are strict; custom executors must match `EventQueue.getExecutorName(event, handler)`. The testing drain method is eventually consistent and not safe for production synchronization.

Test signals: `TestEventQueue` covers handler registration, fixed-pool executor dispatch, metrics, and queue processing. `TestEventQueueChain` covers handler-emitted follow-on events. Many SCM/Recon integration tests call `processAll()` to drain event side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventWatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventWatcher.java

Purpose: `EventWatcher` tracks started events and invokes timeout or completion callbacks based on a lease. It is designed for retry/resend workflows where an initiating payload should be followed by a completion payload before a timeout.

Important APIs/types/functions: constructor takes a watcher name, start event, completion event, and `LeaseManager<Long>`. `start(EventQueue)` registers internal handlers for both events and registers `EventWatcherMetrics`. `contains()`, `remove()`, and `getTimeoutEvents(predicate)` expose tracked payload state. Subclasses implement `onTimeout()` and `onFinished()`.

Control flow: start-event handling stores the payload by id, tracks start time, and acquires a lease whose callback calls `handleTimeout()`. Completion handling releases the lease, removes the tracked payload, updates completion metrics, and calls `onFinished()`. Timeout handling removes state, increments timeout metrics, and calls `onTimeout()`.

State and persistence: tracked payloads are in `ConcurrentHashMap`, `HashSet`, and `HashMap`; mutation methods are synchronized around the multi-structure invariants. There is no persistence. Identity is the payload's `getId()` from `IdentifiableEventPayload`.

Dependencies/integration: depends on `LeaseManager` and Ozone lease exceptions, `EventQueue`, `EventPublisher`, and Hadoop Metrics2. Subclasses are used where SCM needs to monitor asynchronous operations.

Risks: duplicate start ids do not reset the lease; a repeated start overwrites map/time state but `LeaseAlreadyExistException` is ignored, which can surprise callers expecting timeout extension. `handleTimeout()` removes by id then calls `payload.getId()` indirectly through removal state; a missing payload would risk null handling. Metrics source names must be unique per watcher.

Test signals: `TestEventWatcher` covers timeout firing, completion cancellation, removal, timeout-event filtering, and metrics increments for tracked, completed, timed-out, and completion-time state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventWatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventWatcherMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventWatcherMetrics.java

Purpose: `EventWatcherMetrics` is the metrics bean registered by `EventWatcher`. It records how many events are tracked, completed, timed out, and the completion-time rate distribution.

Important APIs/types/functions: `incrementTrackedEvents()`, `incrementTimedOutEvents()`, `incrementCompletedEvents()`, and `updateFinishingTime(duration)` mutate `MutableCounterLong` and `MutableRate` fields. Package-private getters expose metric objects to tests.

Control flow: `EventWatcher.start()` registers this object with the default Metrics2 system. `EventWatcher` updates counters in start, completion, and timeout paths.

State and persistence: state is in memory inside Metrics2 mutable metric objects. There is no explicit unregister method in this class; lifecycle is managed by the registering watcher and metrics system.

Dependencies/integration: depends on Hadoop Metrics2 annotations and mutable metric types. Integrated only through `EventWatcher`.

Risks: fields rely on Metrics2 injection after registration. Instantiating and using the class outside Metrics2 registration may leave fields null. Reusing names across watchers can create metrics-source conflicts at registration time.

Test signals: `TestEventWatcher` obtains metrics via a visible-for-testing watcher accessor and asserts counter/rate behavior after timeout and completion scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventWatcherMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/FixedThreadPoolWithAffinityExecutor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/FixedThreadPoolWithAffinityExecutor.java

Purpose: `FixedThreadPoolWithAffinityExecutor` is an `EventExecutor` for high-volume events where payloads should be partitioned across fixed queues while preserving affinity by `hashCode()`. It is used for report-processing paths such as container reports.

Important APIs/types/functions: the constructor receives a name, event handler, shared work queues, publisher, payload class, executor list, and class-to-executor map. `initializeExecutorPool()` creates one single-thread `ThreadPoolExecutor` per queue. `onMessage()` hashes the payload to a queue and increments metrics. `ContainerReportProcessTask` drains queues and calls the appropriate executor's handler. `IQueueMetrics` lets custom queues report dropped items.

Control flow: construction registers this executor under `clazz.getName()` and starts a queue-draining task on each thread pool if not already active. `onMessage()` enqueues payloads by `Math.floorMod(message.hashCode(), workQueues.size())`. Worker tasks poll queues, find the executor by payload runtime class, inspect `IEventInfo` for creation time/id, update scheduled/done/failed/long-wait/long-execution counters, and log slow events.

State and persistence: in-memory queues, thread pools, an `AtomicBoolean isRunning`, and Metrics2 counters. No durable state. `close()` flips running false, shuts down executors, clears the shared executor map, and unregisters metrics.

Dependencies/integration: depends on `EventExecutor`, `EventHandler`, `EventPublisher`, `IEventInfo`, Metrics2, Guava thread factories, Hadoop `Time`, and SCM event threshold defaults. Used by SCM report-processing tests and integration paths.

Risks: unchecked casts from `P` to `Q` and raw executor-map typing require payload class discipline. `queue.add()` can throw if a bounded queue is full unless the queue handles drops internally. Affinity depends on stable, well-distributed `hashCode()`. Clearing a shared executor map on close can affect other executors if they share it.

Test signals: `TestEventQueue` exercises fixed-pool dispatch, affinity queues, and drop metrics; SCM integration tests instantiate it for container and incremental report handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/FixedThreadPoolWithAffinityExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/IEventInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/IEventInfo.java

Purpose: `IEventInfo` is an optional payload-side metadata interface for events that want queue/execution latency tracking.

Important APIs/types/functions: `getCreateTime()` returns the event creation timestamp, expected to be comparable with `Time.monotonicNow()`. `getEventId()` defaults to an empty string and can be overridden for log context.

Control flow: `FixedThreadPoolWithAffinityExecutor.ContainerReportProcessTask` checks whether a queued report implements this interface. If so, it computes queue wait and total execution time against configured thresholds and increments slow-event metrics.

State and persistence: no state in the interface; implementations carry their own timestamp/id fields.

Dependencies/integration: integrated with the fixed-affinity executor and report payload classes. It avoids making all event payloads depend on a concrete base type.

Risks: callers must supply monotonic timestamps, not wall-clock values, or threshold comparisons become invalid. The default event id limits diagnostic value unless implementations override it.

Test signals: fixed-pool executor tests and report-processing integration paths provide indirect coverage of slow queue/execution accounting when payloads implement this contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/IEventInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/IdentifiableEventPayload.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/IdentifiableEventPayload.java

Purpose: `IdentifiableEventPayload` marks event payloads that have a stable long id. It is the identity contract for `EventWatcher` start and completion correlation.

Important APIs/types/functions: the only method is `getId()`.

Control flow: `EventWatcher` stores timeout payloads by id, acquires/releases leases by id, and matches completion payload ids to started payloads. Subclasses receive the original start payload in `onTimeout()` or `onFinished()`.

State and persistence: no state in the interface. Implementations must provide an id that remains stable across hash/equals lifecycle and across the related start/completion events.

Dependencies/integration: used as generic bounds for `EventWatcher<TIMEOUT_PAYLOAD, COMPLETION_PAYLOAD>`.

Risks: duplicate ids collapse tracking state. Completion events with ids that have already timed out are logged as missing leases. Id reuse before old state is cleared can cause mis-correlated completion or timeout behavior.

Test signals: `TestEventWatcher` defines simple identifiable payloads for under-replication and replication-completion flows and verifies correlation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/IdentifiableEventPayload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/SingleThreadExecutor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/SingleThreadExecutor.java

Purpose: `SingleThreadExecutor` is the default `EventExecutor` used by `EventQueue.addHandler(event, handler)`. It serializes handler invocations for one handler/executor name on a dedicated thread.

Important APIs/types/functions: constructor creates `EventExecutorMetrics` and a Java `ExecutorService` with a named single thread. `onMessage()` increments queued/scheduled/done/failed counters and catches handler exceptions. Counter accessors implement the `EventExecutor` API. `close()` shuts down the executor and unregisters metrics.

Control flow: `EventQueue.fireEvent()` calls `onMessage()`, which enqueues a runnable. The runnable calls the target handler with the original publisher. Handler exceptions are logged and counted without propagating to the publisher.

State and persistence: in-process executor queue and metrics only. There is no explicit await termination in `close()`, so outstanding work may continue until executor shutdown drains according to Java executor semantics.

Dependencies/integration: depends on `EventExecutor`, `EventHandler`, `EventPublisher`, `EventExecutorMetrics`, `Executors`, and SLF4J. Used by default for most event handlers.

Risks: unbounded single-thread executor queue can grow under sustained overload. No dropped/slow-event methods are overridden here beyond basic counters if the `EventExecutor` interface has defaults. Handler latency directly delays later events for that handler.

Test signals: `TestEventQueue` and `TestEventQueueChain` cover default asynchronous dispatch and drain behavior; many component tests rely on this executor through `EventQueue`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/SingleThreadExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/TypedEvent.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/TypedEvent.java

Purpose: `TypedEvent<T>` is a basic `Event<T>` implementation that binds an event name to a payload class.

Important APIs/types/functions: constructors accept `(Class<T> payloadType, String name)` or default the name to `payloadType.getSimpleName()`. `getPayloadType()`, `getName()`, and `toString()` implement the event contract.

Control flow: components declare static `TypedEvent` instances and register handlers against them in `EventQueue`. The event object is the map key, so object identity/equality behavior is inherited from `Object`; the same event instance must be used for registration and publication unless a wrapper implements equality.

State and persistence: immutable in-memory fields only.

Dependencies/integration: implements the local `Event<T>` interface and is heavily used in tests and SCM event declarations.

Risks: no runtime validation confirms payload instances match `payloadType` during `fireEvent()`. Event name participates in executor naming; names containing `For` are rejected by `EventQueue`.

Test signals: `TestEventQueue`, `TestEventQueueChain`, and `TestEventWatcher` instantiate `TypedEvent` directly for unit event streams.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/TypedEvent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/package-info.java

Purpose: this package-info documents `org.apache.hadoop.hdds.server.events` as the simple event queue implementation for HDDS/Ozone server components.

Important APIs/types/functions: it declares only the package and package-level Javadoc. The substantive APIs in the package include `EventQueue`, `EventPublisher`, `EventHandler`, `EventExecutor`, `SingleThreadExecutor`, `FixedThreadPoolWithAffinityExecutor`, and watcher/metrics support classes.

Control flow: package-level documentation has no runtime control flow.

State and persistence: none.

Dependencies/integration: the package forms the asynchronous event bus used by SCM, Recon, safe mode, node/container/pipeline handlers, and tests.

Risks: none in this file; the operational risks belong to the concrete queue/executor classes.

Test signals: package functionality is covered by framework unit tests such as `TestEventQueue`, `TestEventQueueChain`, and `TestEventWatcher`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/AdminAuthorizedServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/AdminAuthorizedServlet.java

Purpose: `AdminAuthorizedServlet` is a Jetty `DefaultServlet` variant that gates static content access behind `HttpServer2` administrator authorization.

Important APIs/types/functions: it overrides `doGet()` and delegates to `HttpServer2.hasAdministratorAccess(getServletContext(), request, response)`. Only authorized requests call `super.doGet()`.

Control flow: default apps use this servlet for the `/logs` context. If admin access fails, `HttpServer2` writes the forbidden response and the servlet returns without serving content.

State and persistence: no servlet state beyond inherited Jetty state.

Dependencies/integration: depends on `HttpServer2` admin ACL context attributes and Jetty `DefaultServlet`. Integrated by `HttpServer2.addDefaultApps()` when log serving is enabled.

Risks: authorization behavior depends on the servlet context having `CONF_CONTEXT_ATTRIBUTE` and admin ACL attributes set. If Hadoop security authorization is disabled, `HttpServer2.hasAdministratorAccess()` permits access.

Test signals: `HttpServer2` admin access and default-app behavior are covered by `TestHttpServer2` and related base server tests; log context access is indirectly exercised through embedded server setup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/AdminAuthorizedServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/BaseHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/BaseHttpServer.java

Purpose: `BaseHttpServer` is the abstract superclass for Ozone component web servers. It converts component-specific configuration keys into a configured `HttpServer2`, installs default Ozone servlets, Prometheus/profile support, security, SSL, and bind-address updates.

Important APIs/types/functions: constructor wires the server if `getEnabledKey()` is true. `newHttpServer2BuilderForOzone()` builds HTTP/HTTPS endpoints from `HttpConfig.Policy`. `start()`, `stop()`, and `close()` manage lifecycle. `updateConnectorAddress()` writes real bound addresses back to the mutable config. Protected abstract methods provide component-specific config keys, bind defaults, principal/keytab keys, and auth prefixes. `loadSslConfiguration()` and `loadSslConfToHttpServerBuilder()` bridge SSL config into `HttpServer2.Builder`.

Control flow: construction determines policy, computes bind addresses, disables Hadoop's built-in Prometheus endpoint, configures auth/SPNEGO when HTTP security is enabled, applies X-Frame headers, optionally disables default apps, builds `HttpServer2`, adds Ozone `/conf` and `/logstream`, configures `/prom` with optional bearer token, optionally enables `/prof`, and sets Jetty temp base dir. `start()` starts Jetty, registers the Prometheus sink with Metrics2, and updates connector addresses.

State and persistence: mutable runtime state includes the `HttpServer2`, bind addresses, policy, component name, Prometheus sink, and booleans. It writes resolved listen addresses and HTTP policy back to configuration. It creates a base temp directory under configured `ozone.http.basedir` or metadata dir.

Dependencies/integration: depends on Ozone/Hdds config helpers, `HttpServer2`, `PrometheusMetricsSink`, `PrometheusServlet`, `ProfileServlet`, `HddsConfServlet`, `LogStreamServlet`, SSLFactory, UGI, ACLs, and Metrics2. Extended by OM, SCM, datanode, Recon, and gateway servers.

Risks: security posture changes based on several flags: Hadoop security, Ozone security, HTTP security, auth type, and Prometheus token. A tokenless `/prom` is added as a regular servlet to remain behind auth in secure clusters. Missing SSL resource properties are warned, not always fatal. Base dir creation failure prevents server startup.

Test signals: `TestBaseHttpServer` covers temp dir and connector-address update behavior. Component HTTP server tests cover policy combinations. Prometheus authorization, SSL, and HTTP config tests exercise adjacent behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/BaseHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HtmlQuoting.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HtmlQuoting.java

Purpose: `HtmlQuoting` provides low-level escaping/unescaping of HTML-active characters for servlet input/output hardening.

Important APIs/types/functions: `needsQuoting(byte[], off, len)` and `needsQuoting(String)` detect `&`, `<`, `>`, `'`, and `"`. `quoteHtmlChars(OutputStream, byte[], off, len)` streams escaped bytes. `quoteHtmlChars(String)` returns an escaped string. `quoteOutputStream()` wraps an output stream and escapes all written bytes. `unquoteHtmlChars()` reverses recognized entities and rejects unknown entity forms.

Control flow: quoting scans UTF-8 bytes and writes entity byte constants for active characters. Unquoting searches for `&`, appends unescaped spans, matches known entity prefixes, and throws `IllegalArgumentException` for malformed/unknown quoting.

State and persistence: stateless utility class with constant byte arrays only.

Dependencies/integration: used by `HttpServer2.QuotingInputFilter.RequestQuoter` to quote request parameters, URLs, and server names. Also available for other servlet output hardening.

Risks: byte-level processing is appropriate for ASCII HTML metacharacters but does not implement full HTML sanitizer semantics. `unquoteHtmlChars()` intentionally throws on unknown entities, so callers should only pass values they expect to be generated by this utility or handle exceptions.

Test signals: `TestHtmlQuoting` covers needs-quoting detection, quote/unquote round trips, null handling, malformed input rejection, and `RequestQuoter` integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HtmlQuoting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpConfig.java

Purpose: `HttpConfig` centralizes Ozone HTTP/HTTPS policy parsing for HDDS web servers.

Important APIs/types/functions: `Policy` has `HTTP_ONLY`, `HTTPS_ONLY`, and `HTTP_AND_HTTPS`, plus `fromString()`, `isHttpEnabled()`, and `isHttpsEnabled()`. `getHttpPolicy(MutableConfigurationSource)` reads `OZONE_HTTP_POLICY_KEY`, validates it, normalizes the config value to the enum name, and returns the policy.

Control flow: Base and component HTTP servers call `getHttpPolicy()` during setup to decide which endpoints to bind. Invalid strings produce `IllegalArgumentException`.

State and persistence: stateless utility class. It mutates the provided configuration by writing the normalized policy name.

Dependencies/integration: depends on Ozone config keys and the mutable configuration abstraction. Used by `BaseHttpServer` and component tests.

Risks: policy parsing is case-insensitive but only accepts exact enum names. Because the method writes back to configuration, callers must expect this normalization side effect.

Test signals: component HTTP server tests and Recon endpoint tests exercise policy combinations; `TestHddsDatanodeService` checks HTTP port behavior for policies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpServer2.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpServer2.java

Purpose: `HttpServer2` is Ozone's embedded Jetty server wrapper. It hosts status, static, metrics, configuration, JMX, log, and component servlets while applying Hadoop/Ozone security filters, SSL, request logging, input quoting, no-cache headers, and metrics.

Important APIs/types/functions: `Builder` configures name, endpoints, host, configuration, SSL stores, SPNEGO keys, auth filter prefix, ACLs, port search/ranges, ciphers/protocols, X-Frame options, and default-app skipping. Runtime APIs include `start()`, `stop()`, `join()`, `isAlive()`, `addServlet()`, `addInternalServlet()`, `addFilter()`, `addGlobalFilter()`, `addJerseyResourcePackage()`, `addContext()`, `setAttribute()`, `getConnectorAddress()`, `setThreads()`, and static admin helpers. Inner `StackServlet` exposes thread dumps, `QuotingInputFilter` wraps requests and sets security headers, and `XFrameOption` validates header values.

Control flow: builder validation creates `HttpServer2`, optionally initializes SPNEGO, loads SSL configuration if any HTTPS endpoint exists, configures header sizes and idle timeout, creates HTTP/HTTPS connectors, and loads listeners. Server initialization creates `WebAppContext`, constructs the signer secret provider, sets Jetty thread pool/metrics/session security, installs context/request-log handlers, default contexts, global quoting filter, configured filter initializers, default servlets, and path-specific filters. `start()` opens listeners, starts Jetty, and checks handler/context failures. Binding supports port incrementing or configured ranges. `stop()` closes listeners, destroys secret provider, clears/stops context, unregisters metrics, and stops Jetty while aggregating exceptions.

State and persistence: in-process Jetty `Server`, connectors, handlers, servlet contexts, admin ACL, filter names, metrics, signer secret provider, X-Frame settings, and port-search settings. It reads webapps from development paths or classpath and can create temporary HTTP base dirs through `setHttpBaseDir()`. No durable application state is stored here.

Dependencies/integration: depends on Jetty server/servlet/webapp APIs, Jersey, Hadoop security/auth filters, Metrics2, Ozone configuration wrappers, SSLFactory, Ratis/Prometheus-adjacent metrics, and local helpers `HtmlQuoting`, `NoCacheFilter`, and `ServletElementsFactory`. It is used by `BaseHttpServer` and therefore by Ozone service HTTP endpoints.

Risks: security depends on correct config propagation into servlet context and filter initializers. `addInternalServlet()` bypasses normal filters except optional Kerberos, so it must be reserved for internal endpoints. `getConnectorAddress()` checks `index > length` rather than `>=`, so equal length would still index out of bounds. `QuotingInputFilter` quotes parameters rather than sanitizing all servlet output. Default sessions are marked secure, which can affect plain HTTP behavior but improves cookie posture.

Test signals: `TestHttpServer2` covers basic server construction/start behavior; `TestHttpServer2SSL` covers cipher/protocol SSL configuration; `TestHttpServer2Metrics` covers thread-pool metrics; `TestHtmlQuoting` covers the request wrapper; `TestBaseHttpServer` and component HTTP tests cover lifecycle integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpServer2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpServer2Metrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpServer2Metrics.java

Purpose: `HttpServer2Metrics` exposes Jetty queued thread pool state through Hadoop Metrics2.

Important APIs/types/functions: `create(QueuedThreadPool, name)` registers a metrics source named `HttpServer2Metrics`. `getMetrics()` emits gauges for total threads, idle threads, max threads, and queued waiting tasks, tagged with server name. `unRegister()` unregisters the source. The nested `HttpServer2MetricsInfo` enum supplies Metrics2 names/descriptions.

Control flow: `HttpServer2.initializeWebServer()` creates this metrics source after configuring the Jetty thread pool. `HttpServer2.stop()` calls `unRegister()`.

State and persistence: stores a reference to the live Jetty `QueuedThreadPool` and server name. Metrics are sampled live; no durable state.

Dependencies/integration: depends on Jetty `QueuedThreadPool`, Hadoop Metrics2, and `DefaultMetricsSystem`. Exportable through the Prometheus sink once Metrics2 emits records.

Risks: `SOURCE_NAME`/`NAME` are static, so multiple simultaneous `HttpServer2` instances can conflict in the metrics system. The server name tag disambiguates records but not source registration.

Test signals: `TestHttpServer2Metrics` mocks a collector and thread pool to verify record name, tag, and gauge values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpServer2Metrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/LogStreamServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/LogStreamServlet.java

Purpose: `LogStreamServlet` streams current Log4j root logger output to an HTTP response for live diagnostics.

Important APIs/types/functions: `doGet()` creates a `WriterAppender` using pattern `%d [%p|%c|%C{1}] %m%n`, sets threshold TRACE, adds it to the root logger, sleeps until interrupted, and removes the appender in `finally`.

Control flow: requests attach a writer-backed appender to the global root logger. The servlet thread blocks for a very long sleep, so the connection remains open while logs are written to the response. On interruption or completion, the appender is removed.

State and persistence: no servlet fields; transient appender attached to global Log4j state. No persistence.

Dependencies/integration: added by `BaseHttpServer` as `/logstream` when default Ozone apps are enabled. Depends on Log4j 1.x APIs and servlet response writer.

Risks: each request can hold a servlet thread indefinitely. Access control is whatever normal servlet filters provide; exposing logs can leak sensitive operational details if not protected. Writer failures rely on appender behavior.

Test signals: no direct test was found for this servlet; integration is through `BaseHttpServer` default servlet registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/LogStreamServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/NoCacheFilter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/NoCacheFilter.java

Purpose: `NoCacheFilter` adds no-cache response headers to servlet contexts served by `HttpServer2`.

Important APIs/types/functions: `doFilter()` casts the response to `HttpServletResponse`, sets `Cache-Control: no-cache`, `Expires`, `Date`, and `Pragma: no-cache`, then delegates to the filter chain. `init()` and `destroy()` are no-ops.

Control flow: `HttpServer2` installs this filter on the main web app and default contexts. Each request receives cache-control headers before the target servlet executes.

State and persistence: stateless.

Dependencies/integration: depends on Java Servlet filter APIs. Integrated through `HttpServer2.createWebAppContext()`, `addNoCacheFilter()`, and `addContext()`.

Risks: forcibly disables caching even for static resources, which is safer for admin/status pages but can reduce browser/cache efficiency. The response cast assumes HTTP servlet usage.

Test signals: indirect coverage through `HttpServer2` tests and embedded server context setup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/NoCacheFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/ProfileServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/ProfileServlet.java

Purpose: `ProfileServlet` exposes async-profiler through the Ozone HTTP server. It starts profiler runs for a target JVM process and serves completed profile files.

Important APIs/types/functions: constructor resolves `ASYNC_PROFILER_HOME` or `async.profiler.home`, resolves PID from `JVM_PID` or runtime MXBean, and creates `OUTPUT_DIR`. `doGet()` validates profiler availability, handles `file` downloads, parses query parameters, acquires a lock, builds a `profiler.sh` command, starts it asynchronously, and responds with auto-refresh. `doGetDownload()` validates filenames and streams completed files. `generateFileName()` and `validateFileName()` are visible for tests. Enums `Event` and `Output` map supported profiler events/output formats.

Control flow: a request without `file` starts a profile if no profiler process is alive and the lock is acquired within 3 seconds. It writes output into `java.io.tmpdir/prof-output-ozone` with a constrained filename pattern and responds `202 Accepted` plus a `Refresh` header. A request with `file` validates the filename, returns an auto-refresh page while the file is short/incomplete, then streams HTML/SVG/tree or raw output.

State and persistence: servlet fields hold profiler home, PID, lock, and current `Process`. Profile artifacts persist under the temp output directory until cleaned externally.

Dependencies/integration: optionally added by `BaseHttpServer` at `/prof` when profiler support is enabled. Depends on async-profiler shell script, servlet APIs, Apache Commons IO/Lang, JVM management APIs, and OS/kernel profiler permissions.

Risks: powerful diagnostic endpoint; `BaseHttpServer` logs a production warning when enabled. Query parameters are intentionally limited but still execute an external command. File download safety depends on the strict filename regex. Only one profiler run per servlet instance is allowed at a time.

Test signals: `TestProfileServlet` validates generated filenames and rejects path traversal/newline filename attempts. Operational behavior is integration-dependent because it requires async-profiler and OS settings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/ProfileServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/PrometheusMetricsSink.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/PrometheusMetricsSink.java

Purpose: `PrometheusMetricsSink` is a Hadoop Metrics2 sink that caches counter/gauge metrics in Prometheus text exposition format for the `/prom` servlet.

Important APIs/types/functions: constructor stores a server name label. `putMetrics()` iterates metrics records, accepts counters and gauges, normalizes metric names through `PrometheusMetricsSinkUtil`, builds Prometheus sample keys with labels/tags, and stores values in `nextMetricLines`. `flush()` atomically swaps `nextMetricLines` into `metricLines`. `writeMetrics(Writer)` writes cached `# TYPE` lines and samples.

Control flow: Metrics2 calls `putMetrics()` repeatedly and then `flush()`. HTTP requests call `writeMetrics()` to stream the last flushed snapshot. Nested sorted synchronized maps keep deterministic output order.

State and persistence: in-memory snapshot maps only. No durable metrics history.

Dependencies/integration: registered by `BaseHttpServer.start()` when Prometheus support is enabled. Consumed by `PrometheusServlet`. Depends on Metrics2, Commons Configuration, and `PrometheusMetricsSinkUtil`.

Risks: label values are appended directly; correctness depends on upstream tag escaping/normalization. Only counters and gauges are exported; other metric types are ignored. The synchronized map plus method-level synchronization protects swaps, but the map values themselves are mutable synchronized maps.

Test signals: `TestPrometheusMetricsIntegration`, `TestPrometheusMetricsSinkUtil`, and volume IO Prometheus tests verify formatting, tag additions, name normalization, and integration output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/PrometheusMetricsSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/PrometheusServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/PrometheusServlet.java

Purpose: `PrometheusServlet` serves Ozone/Hadoop metrics and Ratis Dropwizard metrics in Prometheus text format.

Important APIs/types/functions: `SECURITY_TOKEN` is the servlet-context attribute for optional bearer-token auth. `getPrometheusSink()` retrieves `BaseHttpServer.PROMETHEUS_SINK`. `doGet()` checks optional `Authorization: Bearer <token>`, writes sink metrics, writes a Dropwizard header, and exports `CollectorRegistry.defaultRegistry` via `TextFormat.write004()`.

Control flow: if a token is configured and the header is missing, wrong prefix, or mismatched, the servlet returns 403. Otherwise it writes Metrics2-derived sink content followed by default Prometheus registry metrics.

State and persistence: no servlet-local state. Reads sink/token from servlet context and collector registry live state.

Dependencies/integration: installed by `BaseHttpServer` at `/prom`, either as internal servlet when bearer-token auth is configured or regular servlet otherwise. Integrates with `PrometheusMetricsSink`, Prometheus Java client, and Ratis Dropwizard exporters.

Risks: bearer token comparison is direct string comparison. Tokenless secure clusters rely on the normal HTTP auth filter path. The servlet assumes a non-null sink context attribute.

Test signals: `TestPrometheusServletAuthorization` covers token acceptance/rejection behavior. Prometheus integration tests cover sink output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/PrometheusServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/RatisDropwizardExports.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/RatisDropwizardExports.java

Purpose: `RatisDropwizardExports` adapts Ratis Dropwizard metrics for Prometheus while using Ozone's Ratis-specific name rewrite builder.

Important APIs/types/functions: constructor passes a `MetricRegistry` and `RatisNameRewriteSampleBuilder` to Prometheus `DropwizardExports`. `registerRatisMetricReporters()` installs JMX and Prometheus reporter registrations into Ratis global metric registries. `clear()` unregisters collectors and removes global reporter registrations. `getName()` builds a Dropwizard registry name from `MetricRegistryInfo`. Private register/deregister methods manage `CollectorRegistry.defaultRegistry`.

Control flow: registration creates two `MetricReporter` wrappers, adds them globally, and future Ratis metric registry creation invokes reporter consumers. The Prometheus reporter creates a `RatisDropwizardExports` for each registry unless the supplied stopped check is true, stores it by name, and registers it with the default collector registry. Deregistration removes and unregisters the collector.

State and persistence: caller-supplied map stores active exports; reporter list stores global registrations. No durable state.

Dependencies/integration: depends on Ratis metrics APIs, Dropwizard metrics, Prometheus Java client, and `RatisNameRewriteSampleBuilder`. `PrometheusServlet` emits the default registry that these collectors populate.

Risks: `clear()` removes while streaming over `entrySet()`, which can be fragile depending on map implementation. CollectorRegistry unregistering a non-registered collector can throw, so map discipline matters. Global Ratis registry side effects must be cleaned between tests/servers.

Test signals: `TestRatisNameRewrite` covers sample normalization. Prometheus integration tests exercise default registry output; Ratis metrics paths provide broader integration coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/RatisDropwizardExports.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/RatisNameRewriteSampleBuilder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/RatisNameRewriteSampleBuilder.java

Purpose: `RatisNameRewriteSampleBuilder` rewrites Ratis Dropwizard metric names into Prometheus samples with useful labels for instance, group, and follower identity.

Important APIs/types/functions: constructor initializes follower regex patterns. `createSample()` intercepts metrics whose Dropwizard name starts with Ratis's metrics application prefix, calls `normalizeRatisMetric()`, and delegates to `DefaultSampleBuilder`; non-Ratis metrics are delegated unchanged. `normalizeRatisMetric()` splits dotted name parts, moves the second identifier segment into `instance`/`group` labels, and extracts follower ids from known follower metric forms.

Control flow: Prometheus Dropwizard export calls `createSample()` for each metric. Ratis metric names are normalized before sample creation and trace-logged when enabled.

State and persistence: immutable pattern list after construction; no persisted state.

Dependencies/integration: used by `RatisDropwizardExports`. Depends on Prometheus client Dropwizard sample builder, Ratis metrics prefix, Commons Lang `StringUtils`, regex, and SLF4J.

Risks: regex/name-shape assumptions are specific to current Ratis metric naming. Changes in Ratis names may lose labels or generate unexpected metric names. Labels are appended to existing additional labels, so duplicate label names could occur if upstream uses the same names.

Test signals: `TestRatisNameRewrite` validates normalization of Ratis metric names, including instance/group/follower extraction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/RatisNameRewriteSampleBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/ServletElementsFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/ServletElementsFactory.java

Purpose: `ServletElementsFactory` centralizes construction of Jetty filter holders and mappings for `HttpServer2`.

Important APIs/types/functions: private constructor throws `UnsupportedOperationException`. `createFilterMapping(mappingName, urls)` creates a `FilterMapping`, sets path specs, dispatches to `FilterMapping.ALL`, and filter name. `createFilterHolder(filterName, classname, parameters)` creates a `FilterHolder`, sets name/class, and optional init parameters.

Control flow: `HttpServer2.addFilter()` and `addGlobalFilter()` use these helpers to install filters consistently across contexts.

State and persistence: stateless utility class.

Dependencies/integration: depends on Jetty `FilterHolder` and `FilterMapping`.

Risks: class names are strings; invalid class names fail later when Jetty initializes filters. `urls` can be null, which is used for SPNEGO in `HttpServer2` through a different path but would need Jetty-compatible handling if passed here.

Test signals: indirect coverage through `HttpServer2` filter tests and startup paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/ServletElementsFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/package-info.java

Purpose: this package-info documents `org.apache.hadoop.hdds.server.http` as the servlets and utilities for embedded Ozone service web servers.

Important APIs/types/functions: no runtime API is declared here. The package contains the embedded server wrapper (`HttpServer2`), component base class (`BaseHttpServer`), security/quoting/cache filters, diagnostics servlets, and Prometheus/Ratis metrics exporters.

Control flow: none in this file.

State and persistence: none.

Dependencies/integration: package is the HTTP surface for OM, SCM, datanode, Recon, and related components.

Risks: none in this file; package-level risk centers on admin endpoint exposure and correct HTTP security configuration.

Test signals: package behavior is covered by HTTP server, SSL, base server, Prometheus, profile, and HTML quoting tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/package-info.java

Purpose: this package-info documents `org.apache.hadoop.hdds.server` as common server-side utilities for HDDS/Ozone server components.

Important APIs/types/functions: it only declares package-level Javadoc. Subpackages in this research group include `events` and `http`, which provide event dispatch and embedded web server support.

Control flow: none.

State and persistence: none.

Dependencies/integration: establishes the common server namespace used by SCM, OM, datanode, Recon, and shared framework code.

Risks: none directly.

Test signals: no direct tests needed; functionality is in concrete classes under subpackages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSLayoutVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSLayoutVersionManager.java

Purpose: `HDDSLayoutVersionManager` manages HDDS layout features and registers SCM/datanode upgrade actions for storage layout finalization.

Important APIs/types/functions: constructor calls `init(layoutVersion, HDDSLayoutFeature.values())` and registers upgrade actions discovered by Reflections. `maxLayoutVersion()` returns the layout version of the last `HDDSLayoutFeature`. Visible-for-testing `registerUpgradeActions(Object... classNames)` scans supplied packages/classes. Private `registerUpgradeActions(Set<Class<?>>)` instantiates annotated `HDDSUpgradeAction` classes, reads `UpgradeActionHdds`, and attaches actions to the target feature as SCM or datanode action.

Control flow: Reflections scans configured HDDS upgrade packages (`hdds.scm.server`, `ozone.container`). Each annotated class is checked for `HDDSUpgradeAction` assignability. Actions whose feature layout version is greater than current metadata layout version are registered; finalized/older actions are skipped. Non-action annotated classes are warned.

State and persistence: inherited layout-version state comes from `AbstractLayoutVersionManager`. This class mutates `HDDSLayoutFeature` action lists in memory during construction. Persistent layout version is external metadata read by callers and passed into the constructor.

Dependencies/integration: depends on HDDS layout feature/action types, Ozone upgrade framework, `UpgradeActionHdds` annotation, Reflections classpath scanning, and SLF4J. Used by SCM and datanode startup/finalization code.

Risks: classpath scanning can miss actions if packages move or shaded/reflection behavior changes. `newInstance()` requires no-arg constructors and logs rather than failing hard on instantiation errors. Adding actions to enum feature instances can have global JVM side effects if managers are constructed repeatedly.

Test signals: `TestHDDSLayoutVersionManager` covers max layout version and action registration; SCM/datanode upgrade and finalization integration tests use this manager across layout scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/upgrade/HDDSLayoutVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/upgrade/package-info.java

Purpose: this package-info documents `org.apache.hadoop.hdds.upgrade` as containing SCM upgrade-related classes.

Important APIs/types/functions: no runtime API is declared here. In this package, `HDDSLayoutVersionManager`, layout features, and upgrade actions coordinate HDDS storage layout upgrades/finalization.

Control flow: none in this file.

State and persistence: none.

Dependencies/integration: package integrates with the broader Ozone upgrade framework and SCM/datanode startup/finalization flows.

Risks: none directly.

Test signals: upgrade package behavior is covered by layout-version manager and SCM/datanode finalization tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/Archiver.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/Archiver.java

Purpose: `Archiver` creates and extracts tar archives for Ozone/HDDS file trees and checkpoint/container transfer workflows.

Important APIs/types/functions: `create(tarFile, from)` tars a directory tree. `extract(tarFile, dir)` untars into a target directory. `includePath()` recursively adds directories/files. `includeFile()` adds a single file. `linkAndIncludeFile()` hard-links a file into a temp dir before archiving and removes the link afterward. `extractEntry()` validates target paths and writes entries. `tar()`, `untar()`, `readEntry()`, and `getBufferSize()` provide archive stream helpers.

Control flow: tar creation opens a `TarArchiveOutputStream`, adds a directory entry before children, lists directory contents, and recursively writes files with size/mode/time metadata. Extraction opens a `TarArchiveInputStream`, resolves each entry under the destination, calls `HddsUtils.validatePath()` to prevent escaping the ancestor, creates directories, and copies file bytes with a bounded buffer.

State and persistence: stateless utility class. It reads/writes filesystem archives and preserves basic file timestamps. Tar output uses POSIX long-file and big-number modes.

Dependencies/integration: depends on Apache Commons Compress/IO, Hadoop/Ozone constants, `HddsUtils.validatePath`, and Java NIO. Used by container packers and DB checkpoint/snapshot transfer code.

Risks: `includePath()` constructs entry names with `subdir + "/" + fileName`, producing leading slash-like names when `subdir` is empty depending on path handling. Hard-link inclusion requires filesystem support and same-device semantics. Extraction safety depends on `validatePath()` handling malicious tar entries.

Test signals: `TestArchiver` covers buffer sizing and hard-link inclusion success/failure. Container packer tests exercise archive entry creation. DB checkpoint paths indirectly use archive streaming helpers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/Archiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundService.java

Purpose: `BackgroundService` is an abstract scheduler for periodic Ozone background work. Each interval obtains a `BackgroundTaskQueue`, runs tasks concurrently on a scheduled pool, waits for prior tasks before starting the next batch, and logs slow tasks.

Important APIs/types/functions: constructors configure service name, interval/unit, pool size, timeout, and optional thread prefix. `start()` schedules the `PeriodicalTask` with fixed delay. `shutdown()` stops the executor safely. `setPoolSize()`, `setServiceTimeoutInNanos()`, `setInterval()`, and `getIntervalMillis()` adjust runtime behavior. Subclasses implement `getTasks()` and may override `execTaskCompletion()`. Test helpers expose executor/thread count and `runPeriodicalTaskNow()`.

Control flow: each `PeriodicalTask.run()` joins the previous `future`, calls completion hook, gets tasks, and chains each task into `future` via `CompletableFuture.runAsync(..., exec).exceptionally(...)` combined with prior future. Each task call logs result size, catches `Throwable`, rethrows `Error`, and warns if elapsed nanos exceed timeout.

State and persistence: state includes scheduled executor, thread group, service interval, timeout, pool size, service task, and current completion future. No durable persistence.

Dependencies/integration: used by block deletion, disk balancer, snapshot maintenance, and other periodic services. Depends on Guava thread factories, Ratis `TimeDuration`, Java concurrency, and local background task/result queues.

Risks: tasks run on the same scheduled executor used to schedule periods, so pool sizing affects both scheduling and work. The future chain can grow over many intervals if not reset, though completed futures are lightweight. `ThreadGroup.destroy()` is deprecated and only attempted when active count is zero. Shutdown must not be called while holding the instance monitor, as documented.

Test signals: `TestBackgroundService` verifies waiting for task completion and single-thread behavior. Component tests such as block deletion and disk balancer exercise subclasses and timeout logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTask.java

Purpose: `BackgroundTask` is the callable unit executed by `BackgroundService`.

Important APIs/types/functions: extends `Callable<BackgroundTaskResult>` and narrows `call()` to return `BackgroundTaskResult`. `getPriority()` defaults to `0`; lower numeric values sort earlier in `BackgroundTaskQueue` because it uses `Comparator.comparingInt`.

Control flow: `BackgroundService` polls tasks from `BackgroundTaskQueue` and runs `call()` asynchronously. Result sizes may be logged for debugging.

State and persistence: interface only; implementations may hold service-specific state.

Dependencies/integration: used by all subclasses of `BackgroundService` and by `BackgroundTaskQueue`.

Risks: priority semantics are implicit; callers expecting larger values to run first would be wrong. Task exceptions are caught/logged by `BackgroundService` and do not stop the scheduler unless they are `Error`.

Test signals: `TestBackgroundService` uses tasks to verify scheduling; disk balancer and block deletion tests cover concrete task behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTaskQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTaskQueue.java

Purpose: `BackgroundTaskQueue` is a synchronized priority queue for `BackgroundTask` instances used by `BackgroundService`.

Important APIs/types/functions: constructor creates a `PriorityQueue` ordered by `BackgroundTask.getPriority()`. `add()`, `poll()`, `isEmpty()`, and `size()` are synchronized.

Control flow: service subclasses fill the queue in `getTasks()`. `BackgroundService.PeriodicalTask` polls until empty and submits each task for asynchronous execution.

State and persistence: in-memory priority queue only.

Dependencies/integration: depends on `BackgroundTask`; used by framework unit tests and component background services.

Risks: synchronization protects individual queue operations, but callers that check `isEmpty()` then `poll()` depend on external single-consumer behavior. Equal-priority ordering is not stable because `PriorityQueue` does not preserve insertion order.

Test signals: `TestBackgroundService` and disk balancer tests call/get task queues; background service behavior validates priority queue consumption.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTaskQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTaskResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTaskResult.java

Purpose: `BackgroundTaskResult` is the result contract returned by background tasks, mainly to report a result size for logging/metrics-like diagnostics.

Important APIs/types/functions: `getSize()` returns the number of entries represented by the result. Nested `EmptyTaskResult` provides `newResult()` and returns size `0`.

Control flow: `BackgroundService` logs `result.getSize()` at debug level after each task completes.

State and persistence: interface only; `EmptyTaskResult` instances are stateless but `newResult()` creates a new object each call.

Dependencies/integration: used by `BackgroundTask` and concrete services.

Risks: result size semantics are service-defined, so cross-service comparisons may be misleading. Returning null from a task would cause `BackgroundService` to throw/log when calling `getSize()`.

Test signals: background service tests use simple results to verify execution; component tests cover concrete result sizes indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTaskResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BooleanTriFunction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BooleanTriFunction.java

Purpose: `BooleanTriFunction` is a generic three-argument functional interface with a composable return type. Despite its name, it is not constrained to boolean output.

Important APIs/types/functions: `apply(T, U, V)` returns `R`. `andThen(Function<? super R, ? extends K>)` composes a post-processing function and returns a new `BooleanTriFunction<T, U, V, K>`.

Control flow: callers invoke `apply()` directly or through composed functions. `andThen()` null-checks the follow-up function with `Objects.requireNonNull`.

State and persistence: no state beyond captured lambda state in implementations.

Dependencies/integration: depends on `java.util.function.Function`. Used where a tri-argument lambda is needed without introducing a concrete class.

Risks: class name suggests boolean-specific behavior but generic signature permits any `R`, which can confuse readers. No checked exception support.

Test signals: no direct test found for this tiny interface; usage sites provide compile-time coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BooleanTriFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/CollectionUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/CollectionUtils.java

Purpose: `CollectionUtils` provides static helpers for immutable map construction, flattening iterators, and top-N selection.

Important APIs/types/functions: `newUnmodifiableMap(values, getKey, existing)` merges values into a copy of an existing map and rejects duplicate keys. `newUnmodifiableMultiMap(values, getKey)` groups values by key and wraps both outer map and inner lists. `newIterator(Collection<List<T>>)` lazily flattens a collection of lists. `findTopN()` overloads keep the largest N items by natural order or comparator with optional filter.

Control flow: map helpers iterate all values and build new collections before wrapping. Flattening iterator advances through inner lists only when needed. Top-N maintains a min-heap of at most N accepted items, then drains it into reverse order so the result is descending by comparator.

State and persistence: stateless utility interface with static methods. Returned maps/lists are unmodifiable views/copies; contained objects remain mutable if their types are mutable.

Dependencies/integration: used across HDDS/Ozone code for collection transformations. Depends only on Java collections and functional interfaces.

Risks: `findTopN()` with `n <= 0` still adds then immediately polls, returning empty but doing work; null comparator/filter inputs are not guarded. Duplicate key error only reports previous value class, not new value details. Multi-map uses `Collectors.toMap` without merge function but keys are unique at that stage.

Test signals: `TestCollectionUtils` covers map duplicate rejection, flattened iteration, top-N ordering, limits, comparators, and filters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/CollectionUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/CpuMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/CpuMetrics.java

Purpose: `CpuMetrics` exposes JVM process CPU load, system CPU load, and available processors through Hadoop Metrics2.

Important APIs/types/functions: constructor captures `com.sun.management.OperatingSystemMXBean`. Static `create()` registers a source named `JvmMetricsCpu` only if one is not already present. `getMetrics()` adds gauges `jvmLoad`, `systemLoad`, and `availableProcessors`.

Control flow: services call `CpuMetrics.create()` during metrics initialization. Metrics2 later invokes `getMetrics()` to sample live MXBean values.

State and persistence: holds an MXBean reference; no persistence. Metrics values are live samples.

Dependencies/integration: depends on `ManagementFactory`, `OperatingSystemMXBean`, Hadoop Metrics2, `DefaultMetricsSystem`, and Ozone metrics context constants. Exportable via Prometheus sink.

Risks: `com.sun.management.OperatingSystemMXBean` is a JDK-specific extension; alternate JVMs may behave differently. CPU load methods can return negative values if unavailable depending on JVM implementation.

Test signals: integration test class `TestCpuMetrics` verifies CPU metrics availability through the Ozone metrics path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/CpuMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBCheckpointMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBCheckpointMetrics.java

Purpose: `DBCheckpointMetrics` tracks timing and count statistics for database checkpoint creation and streaming.

Important APIs/types/functions: `create(parent)` registers the source with Metrics2. `unRegister()` unregisters it. Setters update gauges for last creation time, last streaming time, and number of excluded SST files. Increment methods update checkpoint, failure, and incremental-checkpoint counters. Visible-for-testing getters expose current values.

Control flow: `DBCheckpointServlet` updates creation time after checkpoint creation, streaming time after writing, excluded SST count, total checkpoint count, incremental count when exclusions are used, and failure count on exceptions.

State and persistence: in-process Metrics2 gauges/counters only; no durable history.

Dependencies/integration: depends on Hadoop Metrics2 annotations/mutable metrics. Used by OM/SCM checkpoint servlet paths and exposed through service metrics.

Risks: static `SOURCE_NAME` can conflict if multiple DB checkpoint metrics are registered in one metrics system without namespacing. Metrics fields require Metrics2 registration.

Test signals: OM/SCM DB checkpoint servlet tests assert metrics such as checkpoint count, creation time, and streaming time. Transfer tests assert incremental/failure metric behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBCheckpointMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBCheckpointServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBCheckpointServlet.java

Purpose: `DBCheckpointServlet` serves current OM/SCM metadata database checkpoints as tar streams and supports optional SST exclusion for incremental snapshot transfer.

Important APIs/types/functions: `initialize()` binds a `DBStore`, metrics, authorization flags, admin users/groups, SPNEGO flag, no-op bootstrap lock, and temp bootstrap directory. `doGet()` handles query-parameter requests; `doPost()` requires multipart form data. `generateSnapshotCheckpoint()` performs authorization and flush parsing. `processMetadataSnapshotRequest()` creates temp dir, obtains checkpoint, writes tar data, updates metrics, and cleans up. Static helpers parse form data and extract SST exclusion lists. `writeDbDataToStream()` delegates to `HddsServerUtil.writeDBCheckpointToStream()` and is overrideable. `NoOpLock` implements a bootstrap lock that does nothing.

Control flow: requests are rejected if DB store is null, authorization fails, or POST is not multipart. Authorized requests parse `flush` and SST exclusions, acquire a write lock, create a temp bootstrap subdirectory, call `dbStore.getCheckpoint(flush)`, set tar response headers, stream checkpoint data excluding requested SSTs, update timing/count metrics, then delete temp directories and clean checkpoint resources. Exceptions set HTTP 500 and increment failure count.

State and persistence: servlet fields hold DB store, metrics, authorization/admin state, lock, and bootstrap temp directory. It creates/cleans temporary directories under the DB parent. Checkpoints are filesystem artifacts managed by `DBCheckpoint.cleanupCheckpoint()`.

Dependencies/integration: used by OM/SCM DB checkpoint servlet subclasses. Depends on servlet APIs, Commons FileUpload/IO, Ozone admins, DBStore/DBCheckpoint, BootstrapStateHandler, Ratis `UncheckedAutoCloseable`, and RocksDB SST naming constants.

Risks: local variable `excludedSstList` is never populated from `receivedSstFiles`, so logging, incremental metric, and excluded-count metric appear inconsistent with actual exclusions passed to streaming. Authorization only checks admin membership when both authorization and SPNEGO are enabled; otherwise authorization-enabled requests still require a principal but `hasPermission()` returns true if SPNEGO is disabled. Temp directory cleanup failure is logged but not surfaced after response streaming.

Test signals: `TestOMDbCheckpointServlet`, `TestSCMDbCheckpointServlet`, inode-based transfer tests, and Ratis snapshot transfer tests cover authorization, metrics, checkpoint streaming, locks, SST exclusion handling, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBCheckpointServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBStoreHAManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBStoreHAManager.java

Purpose: `DBStoreHAManager` is an extension interface for DB stores that can expose HA transaction metadata for SCM and OM.

Important APIs/types/functions: default `getTransactionInfoTable()` returns `null`; implementations can override to return a `Table<String, TransactionInfo>`.

Control flow: callers can check whether a DB store/manager supplies a transaction info table and use it for HA state, snapshot, or transaction tracking.

State and persistence: interface only. The returned table, when implemented, is persistent DB-backed state.

Dependencies/integration: depends on local DB `Table` abstraction and `TransactionInfo`. Used by HA-aware DB implementations.

Risks: default null return requires callers to handle absence explicitly. A default no-op can hide missing implementation if callers assume HA metadata exists.

Test signals: HA DB and checkpoint tests provide indirect coverage through concrete managers; no direct unit test for this interface was found.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBStoreHAManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DecayRpcSchedulerUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DecayRpcSchedulerUtil.java

Purpose: `DecayRpcSchedulerUtil` normalizes DecayRpcScheduler metrics for Prometheus by extracting caller usernames from metric names and converting them to labels.

Important APIs/types/functions: `splitMetricNameIfNeeded(recordName, metricName)` returns `Volume` or `Priority` for DecayRpcScheduler caller metrics, otherwise the original metric name. `checkMetricNameForUsername()` extracts the username inside `Caller(...)` for matching metrics. `createUsernameTag()` returns an optional Metrics2 tag named `username`.

Control flow: Prometheus metrics normalization calls these helpers when building metric names/tags. Matching is based on lowercase contains checks for `decayrpcscheduler` and `caller(`, then string splitting by `.` and parentheses.

State and persistence: stateless utility class.

Dependencies/integration: used by `PrometheusMetricsSinkUtil` and metrics export code. Depends on Guava `Strings`, Metrics2 `MetricsInfo`/`MetricsTag`, and Java `Optional`.

Risks: parsing assumes exactly the expected `Caller(user).Metric` shape; malformed matching strings can cause array index exceptions. Usernames containing `.` or parentheses would break parsing assumptions.

Test signals: `TestDecayRpcSchedulerUtil` covers metric-name splitting, unchanged names, username extraction, null username behavior, and username tag creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DecayRpcSchedulerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/FaultInjector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/FaultInjector.java

Purpose: `FaultInjector` is a testing hook base class for injecting pauses, exceptions, and container command types into Ozone workflows.

Important APIs/types/functions: visible-for-testing methods include `init()`, `pause()`, `resume()`, `reset()`, `setException(Throwable)`, `getException()`, `setType(ContainerProtos.Type)`, and `getType()`. The base implementation is no-op/null-returning.

Control flow: production code can hold a `FaultInjector` reference defaulting to this no-op base, while tests install subclasses that block, throw, or record state at specific injection points.

State and persistence: base class has no state. Test subclasses usually keep exception/type/latch state in memory.

Dependencies/integration: depends on container protobuf command type. Used by disk balancer, key/container operations, lease recovery, snapshot transfer, and other fault-injection tests.

Risks: injection hooks must be carefully reset after tests to avoid cross-test contamination. No-op defaults make production safe, but broad visible-for-testing methods can hide unused or stale injection points.

Test signals: disk balancer tests define custom subclasses; lease recovery and OM Ratis snapshot transfer tests use `FaultInjectorImpl` to simulate failures and pauses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/FaultInjector.java -->
