# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.1.xml lines 18817-25137

## Chunk Scope

This chunk is a generated JDiff public API slice from Hadoop 0.20.1. It starts inside `org.apache.hadoop.io.file.tfile.TFile.Writer`, covers the end of `org.apache.hadoop.io.file.tfile`, then documents public APIs in `org.apache.hadoop.io.retry`, `org.apache.hadoop.io.serializer`, `org.apache.hadoop.ipc`, `org.apache.hadoop.ipc.metrics`, `org.apache.hadoop.log`, `org.apache.hadoop.metrics`, `org.apache.hadoop.metrics.file`, `org.apache.hadoop.metrics.ganglia`, `org.apache.hadoop.metrics.jvm`, `org.apache.hadoop.metrics.spi`, `org.apache.hadoop.metrics.util`, `org.apache.hadoop.net`, and the beginning of `org.apache.hadoop.record`.

The range ends inside `org.apache.hadoop.record.CsvRecordInput`; the remaining `CsvRecordInput` methods and following record classes are outside this chunk. Because this source is API XML rather than implementation source, control flow, state, persistence behavior, and risks are inferred from public signatures, fields, modifiers, checked exceptions, and embedded Javadoc.

## Purpose

The chunk captures several cross-cutting Hadoop Common subsystems:

- TFile writer append/meta-block APIs and TFile utility encodings.
- Retry policies and dynamic retry proxy creation.
- Serialization/deserialization provider contracts for Writable and Java serialization.
- Hadoop IPC/RPC client, server, protocol versioning, and remote exception APIs.
- Metrics contexts, records, providers, JMX bridges, and metric value helpers.
- Runtime log-level adjustment command/servlet APIs.
- Network utilities, rack topology modeling, DNS-to-switch mapping, socket streams with timeout-aware NIO behavior, and socket factories.
- Binary record I/O and mutable byte buffer APIs, plus the start of CSV record input.

As a compatibility artifact, the XML is useful for tracking public method overloads, deprecations, public fields, exception contracts, configuration keys named in documentation, and API-level integration seams across Hadoop 0.20.1.

## Important APIs and Types

### `org.apache.hadoop.io.file.tfile`

The visible tail of `TFile.Writer` exposes the append and metadata-write contract:

- `append(byte[] key, byte[] value)` and `append(byte[], int, int, byte[], int, int)` add key/value pairs. The offset/length overload documents that an `IOException` can leave the TFile inconsistent, with only `close()` legitimate afterward.
- `prepareAppendKey(int length)` returns a `DataOutputStream` for streaming a key. It requires no active key or value append stream. A non-negative length must be matched exactly before closing the returned stream.
- `prepareAppendValue(int length)` returns a value stream and is only valid immediately after closing a key append stream. Advertising value length allows a single encoded chunk and avoids intermediate buffering.
- `prepareMetaBlock(String name, String compressName)` and `prepareMetaBlock(String name)` create meta-block streams. After adding a metadata block, no more key/value insertions are allowed. Duplicate names throw `MetaBlockAlreadyExists`; compression names must be supported by `TFile`.

`Utils` is a public final utility class for TFile support:

- `writeVInt`, `writeVLong`, `readVInt`, and `readVLong` encode signed integers with a custom variable-length big-endian scheme.
- `writeString` and `readString` serialize strings as a vint length followed by Text-format bytes.
- `lowerBound` and `upperBound` overloads implement binary-search insertion-point helpers with either an explicit `Comparator` or natural ordering.

`Utils.Version` is a public static final comparable value type. It can be constructed from `DataInput` or `short major, short minor`, written to `DataOutput`, compared, stringified, and checked for compatibility by major version. The serialized form is two big-endian shorts.

### `org.apache.hadoop.io.retry`

`RetryPolicy` defines `shouldRetry(Exception e, int retries)`, returning `true` to retry, `false` to suppress failure for void methods, or throwing to fail. Documentation requires immutable implementations.

`RetryPolicies` is a factory/constants class for common policy behavior:

- Public constants: `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, and `RETRY_FOREVER`.
- Fixed count/time retry: `retryUpToMaximumCountWithFixedSleep` and `retryUpToMaximumTimeWithFixedSleep`.
- Growing delays: `retryUpToMaximumCountWithProportionalSleep` and `exponentialBackoffRetry`.
- Policy dispatch: `retryByException` and `retryByRemoteException`, mapping exception classes or remote exception classes to policies with a default fallback.

`RetryProxy.create` wraps an implementation behind an interface proxy, either with one policy for all methods or with a method-name-to-policy map. Missing method-specific entries default to `TRY_ONCE_THEN_FAIL`.

### `org.apache.hadoop.io.serializer`

`Serializer` and `Deserializer` are stateful stream adapters. `open` binds an output/input stream, `serialize` or `deserialize` moves one object, and `close` closes the underlying stream and releases resources. The docs explicitly say they should not buffer across calls because other producers/consumers may share the stream.

`Serialization` pairs serializers and deserializers and selects supported classes via `accept(Class)`. `SerializationFactory` reads the comma-delimited `io.serializations` configuration property, then returns matching `Serialization`, `Serializer`, or `Deserializer` instances.

Concrete/utility types include:

- `WritableSerialization`, which delegates to `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`.
- `JavaSerialization`, an experimental provider for Java `Serializable` classes.
- `DeserializerComparator`, an abstract `RawComparator` that deserializes byte ranges before comparing objects.
- `JavaSerializationComparator`, which compares Java-serialized objects through their `Comparable` interface.

### `org.apache.hadoop.ipc`

`Client` is the writable-based IPC client. It is constructed with a value class, `Configuration`, and optionally a `SocketFactory`. It supports a static `setPingInterval`, lifecycle `stop`, single-call overloads, and parallel-call overloads returning `Writable[]`. Deprecated overloads omit the protocol class and/or `UserGroupInformation`; current overloads include protocol and ticket parameters. Parallel calls return `null` for timed out or errored calls.

`RemoteException` wraps a remote exception class name and message. It exposes `getClassName`, `unwrapRemoteException(Class[])`, general `unwrapRemoteException()`, XML serialization through `writeXml`, and `valueOf(Attributes)` for XML reconstruction.

`RPC` provides the higher-level proxy and server facade:

- `waitForProxy` and `getProxy` build client-side `VersionedProtocol` proxies with protocol class, client version, address, configuration, optional `UserGroupInformation`, and optional `SocketFactory`.
- `stopProxy` releases proxy resources.
- Static `call` overloads make parallel reflective method calls; the overload without `UserGroupInformation` is deprecated.
- `getServer` overloads create `RPC.Server` instances from an implementation object, bind address, port, handler count, verbosity, and configuration.

`RPC.Server` extends `Server`, dispatches `call(Class protocol, Writable param, long receivedTime)`, and authorizes incoming connections with a `Subject` and `ConnectionHeader`.

`RPC.VersionMismatch` records interface name, client version, and server version. `VersionedProtocol.getProtocolVersion(String protocol, long clientVersion)` is the base version-negotiation API; implementing protocol interfaces are expected to define a static `versionID`.

`Server` is the abstract base IPC service. It exposes protected constructors, context helpers (`get`, `getRemoteIp`, `getRemoteAddress`), `bind`, lifecycle (`start`, `stop`, `join`), listener address, `call` dispatch, authorization, open connection count, and call queue length. Public/protected fields include RPC header/version constants, `LOG`, and `rpcMetrics`.

### `org.apache.hadoop.ipc.metrics` and `org.apache.hadoop.log`

`RpcMetrics` implements `Updater`, owns a public `MetricsRegistry`, and exposes public metric objects for queue time, processing time, open connections, and call queue length. It pushes metrics during `doUpdates` and unregisters/shuts down through `shutdown`.

`RpcActivityMBean` extends `MetricsDynamicMBeanBase` and registers RPC activity under the documented `hadoop:service=<RpcServiceName>,name=RpcActivityForPort<port>` naming pattern. `RpcMgtMBean` defines JMX getters for operation counts, average processing/queue times, min/max values, queue length, open connections, and `resetAllMinMax`.

`LogLevel` provides runtime log-level adjustment through a command-line `main` and an HTTP servlet `LogLevel.Servlet.doGet`. The public `USAGES` field exposes command usage text.

### `org.apache.hadoop.metrics`

`ContextFactory` is the singleton factory for `MetricsContext` instances. It stores arbitrary attributes, reads `hadoop-metrics.properties` from the classpath in `getFactory()`, creates configured context classes based on `<contextName>.class`, and falls back to `org.apache.hadoop.metrics.spi.NullContext`.

`MetricsContext` is the main metrics interface:

- Lifecycle: `init`, `startMonitoring`, `stopMonitoring`, `isMonitoring`, and `close`.
- Record creation: `createRecord(String)`.
- Periodic callbacks: `registerUpdater` and `unregisterUpdater`.
- Timing: `getPeriod`, with public `DEFAULT_PERIOD`.

`MetricsRecord` represents a named record with tags and metrics. It supports typed `setTag`, `removeTag`, typed `setMetric`, typed `incrMetric`, `update`, and `remove`. The docs describe an internal buffered table keyed by record name and tag values, periodic emission, row removal, and atomic `update()` behavior. Different threads may update separate record instances with the same tags, but should not share one `MetricsRecord` concurrently.

`MetricsUtil` wraps common access: `getContext`, `getContext(refName, contextName)`, and `createRecord`, which tags records with the host name. `Updater.doUpdates(MetricsContext)` is the periodic callback contract. `MetricsException` is the unchecked metrics error type.

### Metrics providers and SPI

`FileContext` writes metrics to a configured file or standard output. `startMonitoring` opens the file in append mode, `stopMonitoring` closes it, `emitRecord` writes records, and `flush` forces updates to disk. Configuration uses context-prefixed properties such as `<context>.fileName` and `<context>.period`.

`GangliaContext` emits metrics to Ganglia through `emitRecord`. `EventCounter` is a Log4J appender that counts fatal, error, warn, and info logging events. `JvmMetrics` is a singleton `Updater` that periodically reports JVM metrics, initialized with process name, session ID, and optional record name.

`AbstractMetricsContext` implements the metrics SPI: initialization from `ContextFactory`, synchronized monitoring lifecycle, record creation, updater registration, abstract `emitRecord`, optional `flush`, buffered table `update` and `remove`, and period management. `CompositeContext` forwards records, lifecycle, flushing, and updater registration across subcontexts; `isMonitoring` is true only when all subcontexts monitor.

`MetricsRecordImpl` stores tags/metrics and delegates `update()` and `remove()` back to its `AbstractMetricsContext`. `MetricValue` wraps a `Number` as either `ABSOLUTE` or `INCREMENT`. `NullContext` discards updates; `NullContextWithUpdateThread` still runs periodic update callbacks for sampling/JMX while emitting no external data. `OutputRecord` exposes emitted tag and metric names/values. `metrics.spi.Util.parse` parses host or host:port specifications into `InetSocketAddress` values, defaulting null specs to localhost plus a default port.

`metrics.util` supplies JMX and metric value helpers:

- `MBeanUtil.registerMBean` and `unregisterMBean` use the `hadoop:service=<serviceName>,name=<nameName>` convention.
- `MetricsBase` is the abstract metric base with name, description, `NO_DESCRIPTION`, and `pushMetric`.
- `MetricsDynamicMBeanBase` implements `DynamicMBean` over a `MetricsRegistry`.
- `MetricsIntValue` and `MetricsLongValue` publish set-on-change gauges once on the next update.
- `MetricsRegistry` synchronizes metric registration and lookup.
- `MetricsTimeVaryingInt` and `MetricsTimeVaryingLong` accumulate interval deltas and reset after publishing.
- `MetricsTimeVaryingRate` tracks operations/time, interval average, min/max operation time, and min/max reset.

### `org.apache.hadoop.net`

`DNSToSwitchMapping.resolve(List)` maps host names/IPs to rack/network paths while preserving one-to-one ordering. `CachedDNSToSwitchMapping` wraps a raw mapping and caches resolved network locations. `ScriptBasedMapping` is a final configurable implementation backed by `topology.script.file.name`.

`DNS` exposes interface-aware DNS helpers: reverse lookup against a nameserver, IPs for an interface, default IP, host names for an interface with default or explicit nameserver, and default host with default or explicit nameserver.

`NetUtils` centralizes RPC/network helpers:

- Socket factory lookup from `hadoop.rpc.socket.factory.class.<ClassName>` with fallback to default and JVM socket factories.
- Socket address parsing from `host`, `host:port`, or URI-like strings.
- Configuration migration from old host/port properties to a combined address.
- Static hostname resolution for tests, plus listing and querying those resolutions.
- Client connect address adjustment for servers bound to `0.0.0.0`.
- Timeout-aware socket input/output stream creation, with channel-aware `SocketInputStream` and `SocketOutputStream`.
- Channel-aware `connect` to avoid JDK thread-local selector leakage.
- Hostname normalization to textual IP addresses.

`NetworkTopology` models a rack/datacenter tree. It can add/remove leaf nodes, test membership, resolve nodes by path, count racks/leaves, compute distance to closest common ancestor, test rack locality, choose a random node inside or outside a scope, count available nodes excluding a list, stringify the tree, and pseudo-sort replicas by distance to a reader.

`Node` defines topology node attributes: network location, name, parent, and level. `NodeBase` implements it with constructors from path/name/location/parent/level, path normalization, public path separator/root constants, and protected mutable fields for name, location, level, and parent.

`SocketInputStream` and `SocketOutputStream` wrap selectable channels, configure associated socket channels non-blocking, and provide read/write waits with stream-level timeouts. `SocketOutputStream.transferToFully` uses `FileChannel.transferTo` until a requested byte count is transferred, throwing `EOFException` or `SocketTimeoutException` as appropriate.

`SocksSocketFactory` and `StandardSocketFactory` implement the standard `SocketFactory` overload set. `SocksSocketFactory` is configurable and can be constructed with a `Proxy`; `StandardSocketFactory` is the default JVM socket path despite its copied doc text mentioning SOCKS.

### `org.apache.hadoop.record`

The visible record APIs start with binary record I/O:

- `BinaryRecordInput` implements `RecordInput` over an `InputStream` or `DataInput`. It provides a thread-local `get(DataInput)` and read methods for primitive types, strings, `Buffer`, records, vectors, and maps.
- `BinaryRecordOutput` implements `RecordOutput` over an `OutputStream` or `DataOutput`. It provides a thread-local `get(DataOutput)` and write/start/end methods for primitive types, strings, `Buffer`, records, vectors, and maps.

`Buffer` is a mutable byte sequence implementing `Comparable` and `Cloneable`. Constructors support empty, whole-array, and byte-range initialization. Methods include `set`, copying replacement, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, append overloads, `compareTo`, equality/hash/string conversion, charset-aware `toString`, and `clone`. Documentation distinguishes logical count from backing capacity.

The chunk ends after the beginning of `CsvRecordInput`, showing its constructor and read methods for primitives, strings, `Buffer`, and `startRecord`. The remainder of this class is outside the range.

## Control Flow and Behavioral Contracts

Important flows documented by the API surface include:

- TFile writing progresses from zero-position output stream construction, to key/value append operations, to optional metadata blocks, to idempotent `close()`. Meta-block creation closes the key/value insertion phase. Stream append methods enforce active-stream ordering: key stream first, close key, then value stream.
- Variable-length integer/string utility flow writes length or integer encodings to `DataOutput`, then reverses them from `DataInput`. `Utils.Version` persists major/minor version fields in a fixed four-byte form and uses major version equality for compatibility.
- Retry flow is policy-driven: a proxy intercepts interface method failures, consults a `RetryPolicy` based on method name or exception type, sleeps according to the selected policy if applicable, retries, returns silently for void suppression, or rethrows.
- Serialization flow is provider-selected by class: `SerializationFactory` finds the first configured provider whose `accept` method matches, then opens a serializer/deserializer against caller-owned streams for per-object movement.
- IPC/RPC flow uses `Client` for writable request/response calls and `RPC` for protocol proxies. Servers accept calls, authorize connection/protocol access, dispatch to `call(Class, Writable, long)`, and expose metrics. Protocol versions are negotiated through `VersionedProtocol`.
- Metrics flow starts with `ContextFactory`, creates a `MetricsContext`, creates `MetricsRecord` instances, updates/removes buffered table rows, periodically invokes registered `Updater`s, emits `OutputRecord`s through provider-specific contexts, and exposes selected metrics through JMX dynamic MBeans.
- Network topology flow resolves host names to rack paths, materializes `Node` paths, mutates a `NetworkTopology` tree, and uses distance/rack locality to reorder or choose nodes. This supports HDFS replica placement and network-aware scheduling.
- Socket stream flow replaces regular blocking socket streams with channel-backed non-blocking streams plus selector waits and timeouts. Once these wrappers configure non-blocking mode, direct use of the original socket input/output streams can throw `IllegalBlockingModeException`.
- Record I/O flow is schema/tag-driven at the API level: callers begin/end records, vectors, and maps, and read/write primitive values and buffers against a binary or CSV representation.

## State and Persistence Behavior

Persistent or mutable state appears in several areas:

- `TFile.Writer` persists key/value records and meta-blocks into an `FSDataOutputStream`, but deliberately does not close the underlying stream. Append failures can leave on-disk state inconsistent.
- `Utils.Version` persists a stable major/minor pair; applications built on TFile are encouraged to store it in meta-blocks.
- Retry policy instances should be immutable, while retry proxies maintain invocation behavior around a target implementation and method policy map.
- Serializers/deserializers are stateful while bound to streams, but must not buffer across object calls in ways that interfere with shared stream producers/consumers.
- `Client`, `Server`, and `RPC.Server` own runtime threads, socket connections, call queues, and metrics. `stop()`/`stopProxy()` are required lifecycle boundaries.
- `RemoteException` carries remote class/message metadata and can be serialized to/from XML attributes.
- Metrics state is intentionally buffered: `MetricsRecord.update()` creates or changes rows in an internal table, and rows continue to be emitted every period until removed. Gauge-style metrics publish only after set changes; time-varying metrics publish deltas and reset interval counters. JMX reads directly from metric objects and registries.
- `ContextFactory` persists process-local attributes and a singleton factory loaded from `hadoop-metrics.properties`.
- `NetUtils` keeps process-local static hostname resolutions for tests. `CachedDNSToSwitchMapping` caches rack resolutions. `NetworkTopology` and `NodeBase` maintain mutable parent/location/level tree state.
- `SocketInputStream` and `SocketOutputStream` mutate socket channel blocking mode and own timeout behavior.
- `Buffer` owns a mutable byte array plus logical count and capacity; `set(byte[])` uses caller-supplied backing storage, while `copy` creates replacement content.

## Dependencies and Integration Points

Visible dependencies include Java I/O, NIO channels, networking, reflection, JMX, servlet APIs, Log4J, Commons Logging, XML SAX/XML encoder types, and Java concurrency `TimeUnit`.

Hadoop integration points include:

- `Configuration`, `Configured`, and `Configurable` for metrics, serializers, socket factories, script-based topology, and IPC setup.
- `Writable`, `RawComparator`, `WritableComparator`, and record I/O types for binary serialization and RPC payloads.
- `FSDataOutputStream` and TFile meta-block APIs for sorted or unsorted key/value file storage.
- `UserGroupInformation`, `Subject`, `ConnectionHeader`, and authorization exceptions for secured RPC.
- `MetricsContext`, `MetricsRecord`, `Updater`, `MetricsRegistry`, and dynamic MBean utilities for subsystem observability.
- `Server`, `VersionedProtocol`, and `NetUtils` for RPC transport and proxy construction.
- Topology mapping interfaces that feed cluster rack-awareness.

Configuration names explicitly referenced in documentation include `io.serializations`, `hadoop-metrics.properties`, `<context>.class`, `<context>.fileName`, `<context>.period`, `rpc.class`, `rpc.period`, `hadoop.rpc.socket.factory.class.<ClassName>`, `hadoop.rpc.socket.factory.class.default` or `hadoop.rpc.socket.factory.default` as documented, and `topology.script.file.name`.

## Risks and Edge Cases

- The XML does not contain method bodies; null handling, argument validation, exact synchronization, resource cleanup, and error translation need implementation-source confirmation.
- Chunk boundaries are partial: prior lines are needed for full `TFile.Writer` context, and later lines are needed for full `CsvRecordInput`.
- TFile append APIs document an inconsistent state after some `IOException`s. Callers should treat `close()` as the only safe recovery action and avoid continuing writes.
- Length-announced key/value streams require exact byte counts; underwrite or overwrite behavior is not specified here but is likely format-critical.
- Adding a TFile meta-block permanently ends key/value insertion, so call ordering bugs can silently shape file layout.
- Variable-length integer encoding is format-defining. Boundary values, sign extension, and malformed first-byte sequences are high-risk compatibility points.
- Retry policies can hide failures for void methods (`TRY_ONCE_DONT_FAIL`) or retry forever, so callers must choose policies with service semantics and interruption behavior in mind.
- SerializationFactory depends on configured class names. Missing providers, provider ordering, classloader behavior, and non-default constructors are likely failure modes.
- `DeserializerComparator` trades convenience for deserialization cost; compare-heavy paths may need byte-level `RawComparator`s.
- Deprecated IPC/RPC overloads coexist with current overloads that include protocol and user identity; compatibility code can accidentally bypass newer security/version context.
- RPC parallel calls return arrays containing `null` for failures/timeouts, so callers must not assume all result slots are non-null.
- `Server.get()` and remote address helpers depend on being invoked in an RPC handling context; outside that context they can return null.
- Metrics records are not safe for concurrent use by multiple threads sharing the same instance, despite atomic update semantics for separate instances with identical tags.
- The default `NullContext` discards metrics and does not necessarily drive periodic sampling; JMX users may need `NullContextWithUpdateThread`.
- Metrics and MBean naming conflicts can occur if registries reuse metric names or services use duplicate `ObjectName`s.
- DNS and topology resolution are environment-sensitive. Cached mappings can become stale, and script-based mapping depends on external script availability and output ordering.
- Channel-backed socket streams change socket channel blocking mode, making mixed direct socket stream use unsafe.
- `NetUtils.connect` and timeout-aware streams are designed to avoid selector/file-descriptor leaks; regressions here can appear as resource exhaustion rather than immediate functional failures.
- `NetworkTopology` methods throw or assume membership for some operations; invalid nodes, null nodes, malformed paths, and exclusion scopes need coverage.
- `Buffer.set(byte[])` uses the caller-supplied array as backing storage, so later external mutation can alter buffer contents.
- `Buffer` count/capacity invariants, truncation, append growth, charset conversion, equality, and compare ordering are all data-format-sensitive.

## Test Signals

Useful tests inferred from this API slice include:

- TFile writer tests for byte-array append, stream append with known and unknown lengths, wrong length close behavior, duplicate meta-block names, meta-block compression names, no writes after meta-block creation, idempotent close, and IOException recovery expectations.
- `Utils` tests for VInt/VLong round trips at every documented boundary, malformed encodings, string encoding round trips, lower/upper bound behavior with duplicates, empty lists, custom comparators, and natural ordering.
- `Utils.Version` tests for DataInput/DataOutput round trips, size, comparison ordering, equality/hashCode, string output, and major-version compatibility.
- Retry tests for fixed count, max time, proportional sleep, exponential backoff bounds, exception class dispatch, remote exception dispatch, method-name dispatch, void suppression, rethrow behavior, and immutable policy reuse.
- SerializationFactory tests with `io.serializations` ordering, Writable and Java serialization acceptance, missing providers, stream open/close behavior, object reuse through `deserialize(t)`, and comparator correctness.
- IPC/RPC tests for single calls, parallel calls with partial failures/timeouts, protocol version mismatch, proxy stop, server lifecycle, listener binding, remote address helpers inside/outside RPC context, authorization rejection, and deprecated overload compatibility.
- RemoteException tests for XML write/read, unwrap by lookup type, unwrap by constructor reflection, unknown exception class fallback, and message preservation.
- Metrics tests for context factory property loading, fallback null context, updater registration/removal, start/stop/close idempotence, record update/remove row semantics, tag/metric type conflicts, periodic emission, file output append/flush, Ganglia emission stubbing, JMX MBean registration, min/max reset, and interval counter reset.
- LogLevel tests for servlet request handling, command-line argument parsing, usage text, valid/invalid logger names, and authorization/visibility behavior in web contexts if implemented elsewhere.
- DNS/NetUtils tests for address parsing forms, default ports, malformed URIs, static resolution add/get/list, `0.0.0.0` connect address adjustment, socket factory configuration, SOCKS proxy configuration, channel and non-channel stream paths, read/write timeouts, connect timeouts, and hostname normalization.
- NetworkTopology tests for add/remove leaf constraints, rack/leaf counts, contains/getNode, distance across same node/same rack/different rack, illegal node handling, scope negation with `~`, excluded-node counts, random selection constraints, and pseudo-sort ordering for local node/local rack/fallback random.
- NodeBase tests for path construction, normalization, root/path separator constants, parent/level mutation, and string representation.
- Record I/O tests for BinaryRecordInput/Output primitive round trips, thread-local `get` reuse, records/vectors/maps boundary methods, Buffer read/write, Buffer backing array aliasing, copy vs set behavior, capacity preservation/truncation, append growth, compare/equality/hashCode, charset conversion errors, clone independence, and visible CsvRecordInput primitive parsing.

## Chunk Boundary Notes

The previous chunk is required to complete the `TFile.Writer` constructor and any earlier writer methods. This chunk itself closes `org.apache.hadoop.io.file.tfile` and many complete packages, but the final `org.apache.hadoop.record.CsvRecordInput` class is incomplete here; the following chunk is required to finish its read/end-vector/end-map behavior and subsequent record package APIs.
