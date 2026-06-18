# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.20.0.xml lines 18734-25017

## Scope And Purpose

This chunk is a JDiff XML API snapshot for Hadoop Core 0.20.0. It covers the tail of `org.apache.hadoop.ipc`, the IPC metrics package, the public metrics API and SPI, network utilities, and most of the Hadoop Record I/O runtime. The file is documentation metadata rather than executable Java source, but it is still a compatibility contract: class names, public and protected constructors, method signatures, field visibility, deprecation text, checked exceptions, and Javadoc behavior are the observable API that downstream Hadoop users and compatibility tooling compare across releases.

The chunk begins inside the `org.apache.hadoop.ipc` package at `RPC.Server` and ends inside the long package-level documentation for `org.apache.hadoop.record`. It does not include implementation bodies, so control-flow and persistence analysis below is inferred from the public API and embedded documentation.

## IPC APIs

The visible IPC surface centers on Hadoop's Writable-based RPC service model:

- `org.apache.hadoop.ipc.RPC.Server` extends `Server` and binds a concrete protocol implementation object to an RPC listener. Its constructors accept the served instance, `Configuration`, bind address, port, optional handler count, and verbose logging flag. `call(Class, Writable, long)` dispatches a single RPC and `authorize(Subject, ConnectionHeader)` delegates connection authorization.
- `RPC.VersionMismatch` is an `IOException` carrying protocol-interface name, client version, and server version. The accessors expose those values so clients can report or branch on version negotiation failures.
- `org.apache.hadoop.ipc.Server` is the abstract IPC service. It exposes static request-context helpers (`get`, `getRemoteIp`, `getRemoteAddress`), socket binding, lifecycle (`start`, `stop`, `join`), listener-address inspection, connection/call-queue gauges, and two `call` overloads. The older `call(Writable,long)` is explicitly deprecated in favor of `call(Class,Writable,long)`.
- `VersionedProtocol` is the base interface for RPC protocols. Implementations are expected to expose a static `versionID` field and implement `getProtocolVersion(String protocol, long clientVersion)`.

Important state in `Server` includes public static wire constants `HEADER` and `CURRENT_VERSION`, the public `LOG`, and protected `rpcMetrics`. The documented control flow is listener startup, accepting connections, optional authorization, queuing calls, invoking `call`, then recording queue/processing metrics. `getRemoteIp` and `getRemoteAddress` only make sense while executing inside an RPC; callers must tolerate `null`.

Risks in this API are mostly compatibility and operational: protocol methods are documented to throw only `IOException`, the signature migration from `call(Writable,long)` to `call(Class,Writable,long)` must preserve old subclasses, authorization errors are surfaced as `AuthorizationException`, and bind failures should distinguish invalid host names from ordinary `IOException`.

## RPC Metrics

`org.apache.hadoop.ipc.metrics` exposes the IPC metrics bridge:

- `RpcMetrics` implements `Updater`, registers RPC activity metrics, and publishes them through `doUpdates(MetricsContext)`. Public metric variables include `rpcQueueTime`, `rpcProcessingTime`, `numOpenConnections`, and `callQueueLen`, all stored in a `MetricsRegistry`.
- `RpcActivityMBean` wraps a `MetricsRegistry` as a dynamic JMX MBean named by RPC service and port, with a `shutdown` method for unregistering.
- `RpcMgtMBean` is a management view exposing operation counts, average/min/max processing times, average/min/max queue times, open connection count, call queue length, and `resetAllMinMax`.

The persistence model is in-memory sampled metrics plus JMX registration. The docs note that sampled/averaged metrics are collected regardless of context, but a context with periodic update calls is needed to view moving averages when using otherwise-null metrics contexts.

## Log Level Utility

`org.apache.hadoop.log.LogLevel` provides a small operational endpoint for runtime log-level inspection and mutation. `main(String[])` is the CLI entry point, `USAGES` documents command usage, and nested `LogLevel.Servlet` handles HTTP `doGet` requests. It integrates with the servlet API and Hadoop's commons-logging stack. The risk is security and exposure: a servlet that changes logging must be protected by deployment configuration, and CLI/HTTP behavior should validate logger names and levels.

## Metrics API

`org.apache.hadoop.metrics` defines the version of Hadoop's original metrics abstraction used by this Hadoop release:

- `ContextFactory` is a singleton factory initialized from `hadoop-metrics.properties` on the classpath. It stores attributes, creates named `MetricsContext` instances by configured implementation class, and can return a no-op null context.
- `MetricsContext` defines monitoring lifecycle (`init`, `startMonitoring`, `stopMonitoring`, `close`), record creation, updater registration, and period lookup. `DEFAULT_PERIOD` is the default reporting cadence in seconds.
- `MetricsRecord` is the mutable record API. It has typed `setTag`, `removeTag`, typed `setMetric`, typed `incrMetric`, `update`, and `remove`. Its documentation is the main behavioral contract: records are buffered in an internal table keyed by record name and tag set; `update` atomically adds or modifies rows; values are emitted periodically rather than immediately.
- `MetricsUtil` provides convenience context lookup and record creation, including a host tag, and logs failures before falling back to a null context.
- `Updater` is the periodic callback interface invoked immediately before records are emitted.
- `MetricsException` is the unchecked exception for configuration/type conflicts.

This API is intentionally provider-neutral. `ContextFactory` state persists for the process lifetime as singleton configuration and context cache. `MetricsRecord` data persists in each context's buffered table until replaced, removed, closed, or emitted by implementation-specific lifecycle. Threading guidance is explicit: multiple threads may call `update` on separate `MetricsRecord` instances with identical tags, but the same `MetricsRecord` instance should not be shared concurrently.

## Metrics Implementations And SPI

The implementation packages provide file, Ganglia, JVM, SPI, and utility pieces:

- `metrics.file.FileContext` extends the SPI context to write records to a configured file or standard output. It exposes `FILE_NAME_PROPERTY`, `PERIOD_PROPERTY`, `getFileName`, lifecycle overrides, `emitRecord`, and `flush`.
- `metrics.ganglia.GangliaContext` emits metrics to Ganglia after `init`, with implementation-specific `emitRecord`.
- `metrics.jvm.EventCounter` is a log4j appender-like counter for fatal/error/warn/info events. `JvmMetrics` is an `Updater` with `init` overloads and `doUpdates` for JVM process metrics.
- `metrics.spi.AbstractMetricsContext` is the base provider implementation. It owns context/factory initialization, attribute parsing, monitoring lifecycle, record creation, updater registration, periodic `update`, row `remove`, `emitRecord`, `flush`, period management, and a protected `newRecord` factory method.
- `CompositeContext` fans one metrics context into multiple child contexts; lifecycle, record creation, emit, flush, updater registration, and close operations are propagated.
- `MetricsRecordImpl`, `MetricValue`, `NullContext`, `NullContextWithUpdateThread`, `OutputRecord`, and `Util.parse` provide the default row implementation, absolute/increment metric markers, no-op contexts with or without an update thread, immutable output views, and parsing helpers.
- `metrics.util` supplies JMX and metric primitives: `MBeanUtil`, abstract `MetricsBase`, `MetricsDynamicMBeanBase`, point-in-time `MetricsIntValue`/`MetricsLongValue`, `MetricsRegistry`, and time-varying int/long/rate metrics with previous/current interval state and min/max tracking.

The key control flow is context initialization from factory attributes, optional monitoring thread startup, periodic `Updater.doUpdates`, buffered record update, provider-specific `emitRecord`, and final `flush`. Test signals for this area should assert configuration fallback, record-table update/remove semantics, updater registration ordering, metric increment versus absolute values, min/max reset behavior, MBean registration/unregistration, and no-op contexts not leaking resources.

## Network Utilities

`org.apache.hadoop.net` provides DNS, rack topology, socket factory, and timeout stream APIs used throughout HDFS and MapReduce:

- `DNSToSwitchMapping` maps host names or IP addresses to rack/network paths with one-to-one result ordering. `CachedDNSToSwitchMapping` wraps another mapping and caches resolved network locations.
- `DNS` performs reverse DNS using a named server, enumerates IPs for a network interface, and resolves host names/default hosts for interface addresses.
- `NetUtils` chooses RPC socket factories from `Configuration`, builds `InetSocketAddress` values from `host:port` or URI strings, handles migration from separate bind/port config keys to a combined address key, stores static host resolutions for tests and multi-daemon local setups, converts wildcard server bind addresses to connectable loopback addresses, wraps sockets in timeout-aware input/output streams, connects with timeout, and normalizes host names.
- `NetworkTopology` maintains a rack-aware tree of `Node` leaves. Public operations add/remove nodes, locate nodes, count racks/leaves/available nodes, compute distance, test same-rack placement, choose random nodes, stringify topology, and pseudo-sort candidates by distance.
- `Node` and `NodeBase` define named network-location tree nodes. `NodeBase` tracks `name`, `location`, `parent`, `level`, and constants for path separators and root/default paths.
- `ScriptBasedMapping` implements rack resolution through the configured `topology.script.file.name`.
- `SocketInputStream` and `SocketOutputStream` wrap NIO selectable channels, configure them non-blocking, and use select-style waits to enforce read/write timeouts. They expose the underlying channel, `isOpen`, wait helpers, byte-array and `ByteBuffer` operations, close, and `transferToFully` for output.
- `SocksSocketFactory` and `StandardSocketFactory` implement the socket-factory abstraction. The SOCKS variant is `Configurable`, supports a supplied `Proxy`, and implements equality/hash semantics.

State and persistence are process-local: static host resolutions, DNS-to-rack caches, network topology trees, configurable socket factory instances, and channel open/closed state. The documented risks are important operationally: timeout stream construction changes the socket channel to non-blocking mode, after which ordinary `Socket#getInputStream`/`getOutputStream` may fail; wildcard bind addresses are not valid client targets; rack mapping must preserve list cardinality/order; and topology mutations need correct parent/level bookkeeping.

## Record I/O Runtime

`org.apache.hadoop.record` is Hadoop's pre-Avro record serialization system. This chunk covers the runtime APIs and documentation for language-neutral record descriptions, generated code, and multiple encodings:

- `RecordInput` and `RecordOutput` are the core deserializer/serializer interfaces. They cover primitive values, strings, `Buffer`, record boundaries, vectors, and maps, with tags used by tagged formats such as XML.
- `BinaryRecordInput` and `BinaryRecordOutput` implement the interfaces over `InputStream`/`DataInput` and `OutputStream`/`DataOutput`. Both have static thread-local `get` helpers for wrapping a supplied data stream.
- `CsvRecordInput` and `CsvRecordOutput` provide CSV deserialization/serialization for the same primitives and compound boundaries.
- `XmlRecordInput` and `XmlRecordOutput` provide XML deserialization/serialization.
- `Index` is the vector/map iteration contract with `done` and `incr`.
- `Record` is the generated-record base class. It supports `serialize`, `deserialize`, `compareTo`, Hadoop `Writable` interop through `write`/`readFields`, and text conversion.
- `RecordComparator` provides record-specific comparator registration through `define(Class, RecordComparator)` and byte-level `compare`.
- `Buffer` is the record runtime byte-sequence type. It distinguishes count from backing capacity, supports direct backing assignment, copying, append, reset, truncate, capacity changes, lexicographic comparison, equality/hash, cloning, and string conversion with optional charset.
- `Utils` implements low-level record encoding helpers: float/double parsing, variable-length int/long read/write from byte arrays and `DataInput`/`DataOutput`, encoded-size calculation, byte comparison, and hex characters.

The record package's control flow is mechanical serialization: generated `Record` classes call `startRecord`, write or read fields in order, call vector/map start methods to obtain an `Index` for iteration, and close compound values with matching end methods. Binary encoding uses Hadoop-style zero-compressed variable-length integers; XML and CSV preserve the same logical model with tagged or textual framing. Thread-local binary wrappers avoid repeated allocation but require careful stream reassignment and thread confinement.

Persistence is external to the runtime objects: serialized bytes are written to files, network streams, or memory buffers supplied by callers. Internal mutable state exists in `Buffer` capacity/count, parser/writer stream state, thread-local binary input/output wrappers, and comparator registrations.

## Dependencies And Integration Points

This chunk connects several core Hadoop subsystems:

- IPC depends on `org.apache.hadoop.io.Writable`, `Configuration`, Java networking, `Subject`, authorization exceptions, and RPC metrics.
- Metrics depend on commons-logging, Java properties/class loading, JMX, log4j-style event counting, file output, Ganglia transport, and the provider SPI.
- Network utilities depend on `Configuration`, Java `Socket`/NIO channels/selectors, JNDI naming for DNS, socket factories, and the Hadoop IPC `Server` connect-address helper.
- Record I/O depends on Java `DataInput`/`DataOutput`, `InputStream`/`OutputStream`, collections (`ArrayList`, `TreeMap`), Hadoop `Writable`/comparators, and generated record classes.

These APIs are integration glue. NameNode, DataNode, JobTracker, TaskTracker, clients, and tests can all depend on them indirectly through RPC setup, metrics emission, rack awareness, socket configuration, or wire-format serialization.

## Risks And Compatibility Notes

The JDiff snapshot makes compatibility risk visible even without implementation bodies:

- Public method signatures and exception lists are part of downstream source and binary compatibility. Removing checked exceptions, changing primitive overloads, or altering visibility would break consumers.
- The metrics package has both API and SPI contracts. Providers rely on lifecycle ordering and record buffering semantics; applications rely on null-context fallback when metrics configuration is absent or broken.
- Metrics documentation contains a subtle default-context inconsistency: `ContextFactory.getContext` method docs mention defaulting to `NullContext`, while the package-level configuration docs mention defaulting to `FileContext`. Compatibility research should verify actual 0.20.0 implementation before changing defaults.
- Socket timeout wrappers change channel blocking mode. Mixing wrapped streams with ordinary socket streams is a documented error path and should be tested.
- Static host resolutions and cached DNS-to-switch mappings are process state; tests must isolate or clear them to avoid order dependence.
- Rack topology algorithms are correctness-sensitive for data placement. Distance, same-rack checks, random choice exclusions, and pseudo-sorting should be validated on multi-rack trees.
- Record I/O depends on exact byte encodings and field order. Changes to variable-length integer encoding, `Buffer.compareTo`, CSV/XML escaping, or thread-local wrapper reuse can silently break stored data and cross-language interoperability.
- `Buffer(byte[])` adopts the supplied array as backing storage while range construction copies; callers must understand aliasing.

## Test Signals

Useful verification signals for this chunk include:

- API compatibility tests generated from this JDiff file: class existence, constructor/method signatures, field visibility/static/final flags, deprecation text, and checked exceptions.
- IPC tests that bind servers, validate wildcard-address connect conversion, version mismatch reporting, old and new `call` overload behavior, authorization denial, remote-address context, queue length, open connection metrics, and clean `start`/`stop`/`join`.
- Metrics tests covering `hadoop-metrics.properties` loading, context implementation selection, null-context fallback, updater invocation before emit, buffered row update/remove behavior, typed tag/metric overloads, increment versus absolute values, file/Ganglia emission stubs, JVM event counters, dynamic MBean attributes, registry contents, and time-varying rate min/max reset.
- Network tests for interface DNS lookup failure paths, static host resolution, URI and `host:port` parsing, socket factory property loading, connect/read/write timeouts, non-blocking channel side effects, `transferToFully` EOF/timeout behavior, SOCKS proxy configuration, rack mapping cache hits, and topology distance/sort/count behavior.
- Record I/O round-trip tests across binary, CSV, and XML encodings for primitives, strings, buffers, records, vectors, and maps; variable-length int/long boundary values; byte lexicographic comparisons; `Buffer` alias/copy/capacity behavior; comparator registration; and generated `Record` `Writable` interop.
