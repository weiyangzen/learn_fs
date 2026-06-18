# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.0.xml lines 18726-25036

## Chunk Scope

This chunk is a JDiff API snapshot for Hadoop 0.20.0, not implementation source. It starts in the middle of `org.apache.hadoop.ipc.Server`, completes the IPC protocol and RPC metrics surface, then covers runtime log-level control, the old Hadoop metrics framework, network and topology utilities, the Hadoop Record I/O runtime, and the beginning of the record compiler generated parser exception class.

Because the file is generated API XML, the control-flow, state, and persistence notes below are inferred from exposed signatures, inheritance, synchronized/static/final markers, checked exceptions, fields, deprecation metadata, and API docs rather than method bodies.

## Purpose

The chunk captures a compatibility surface used by early Hadoop common/core services. It documents how Hadoop servers expose RPC lifecycle hooks and metrics, how daemons publish metrics to file/Ganglia/JMX, how clients resolve network addresses and rack topology, and how generated Hadoop record classes serialize binary, CSV, and XML data.

The network and record packages are especially important integration layers: `org.apache.hadoop.net` feeds rack-aware placement, RPC socket construction, and timeout-aware socket streams, while `org.apache.hadoop.record` provides the schema/compiler/runtime system used by older Hadoop services before later Avro/Protocol Buffer migrations.

## Important APIs and Types

### IPC and RPC metrics

The visible tail of `org.apache.hadoop.ipc.Server` exposes service lifecycle and request handling: `setSocketSendBufSize(int)`, synchronized `start()`, `stop()`, `join()`, synchronized `getListenerAddress()`, deprecated `call(Writable,long)`, abstract protocol-aware `call(Class, Writable, long)`, `authorize(Subject, ConnectionHeader)`, `getNumOpenConnections()`, and `getCallQueueLen()`. Public fields include the RPC connection `HEADER`, `CURRENT_VERSION`, `LOG`, and protected `rpcMetrics`.

`VersionedProtocol` is the base interface for Hadoop RPC protocols. Its `getProtocolVersion(String protocol, long clientVersion)` method reports the server version for a named protocol; subclasses are expected to expose a static `versionID`.

`RpcMetrics` implements `Updater` and owns a public `MetricsRegistry` plus `MetricsTimeVaryingRate` fields for queue and processing time and `MetricsIntValue` fields for open connections and call queue length. `doUpdates(MetricsContext)` pushes these values to the metrics subsystem, and `shutdown()` cleans up. `RpcActivityMBean` wraps the registry in a dynamic MBean named by RPC service and port, while `RpcMgtMBean` defines JMX getters for operation count, average/min/max processing time, average/min/max queue time, min/max reset, open connections, and queue length.

### Runtime log-level control

`org.apache.hadoop.log.LogLevel` exposes a command-line `main(String[])`, `USAGES`, and nested `LogLevel.Servlet`. The servlet's `doGet(HttpServletRequest, HttpServletResponse)` allows changing or inspecting log levels over HTTP, integrating with daemon web UIs and servlet containers.

### Metrics API

`ContextFactory` is the singleton factory for metrics contexts. It stores attributes loaded from `hadoop-metrics.properties`, exposes attribute get/set/remove/list operations, and creates named `MetricsContext` instances by class name from `<contextName>.class`, defaulting to `NullContext`.

`MetricsContext` is the main metrics interface: `init`, `getContextName`, `startMonitoring`, `stopMonitoring`, `isMonitoring`, `close`, `createRecord`, `registerUpdater`, `unregisterUpdater`, and `getPeriod`. Its `DEFAULT_PERIOD` is the default emission period. `MetricsRecord` represents a record with typed tags and metrics; it supports `setTag` for string/int/long/short/byte, `removeTag`, `setMetric` and `incrMetric` for int/long/short/byte/float, plus `update()` and `remove()`. Docs specify an internal table keyed by record name and tag values, with atomic `update()` but no thread-safe sharing of the same `MetricsRecord` instance.

`MetricsUtil` is a convenience entry point for acquiring contexts and creating host-tagged records. `Updater.doUpdates(MetricsContext)` is the periodic callback contract. `MetricsException` is the unchecked error type for metrics configuration and type conflicts.

### Metrics implementations and SPI

`FileContext` extends `AbstractMetricsContext`, writes metrics to a configured append-mode file or standard output, and flushes the writer after emission. Configuration is attribute-based, with `fileName` and `period` properties under the context prefix.

`GangliaContext` extends `AbstractMetricsContext` and sends records to Ganglia. `EventCounter` is a Log4J appender that counts fatal/error/warn/info logging events. `JvmMetrics` is a singleton `Updater` initialized with process/session metadata and periodically emits JVM metrics.

`AbstractMetricsContext` is the SPI base. It maintains the internal buffered metrics table and a timer, exposes synchronized lifecycle/updater registration methods, creates final public records through `createRecord`, and delegates actual output to abstract `emitRecord(contextName, recordName, OutputRecord)`. It also supports subclass `flush`, protected `update(MetricsRecordImpl)`, protected `remove(MetricsRecordImpl)`, attribute lookup, and configurable periods.

`CompositeContext` fans records and lifecycle calls out to subcontexts. `MetricsRecordImpl` stores mutable tags and metric values and delegates `update()`/`remove()` back to its context. `MetricValue` wraps a `Number` as either absolute or incremental. `NullContext` discards records and is the default when no metrics configuration exists. `NullContextWithUpdateThread` also discards output but keeps the periodic update thread running for readers such as JMX. `OutputRecord` exposes emitted tag and metric maps. `Util.parse(String,int)` parses host or host:port server specs into `InetSocketAddress` values.

### Metrics utility classes and JMX

`MBeanUtil` registers and unregisters MBeans using the standard `hadoop:service=<serviceName>,name=<nameName>` object-name format. `MetricsDynamicMBeanBase` implements `DynamicMBean` over a `MetricsRegistry`, exposing metrics as JMX attributes and operations.

`MetricsBase` is the abstract base for named metrics with descriptions and `pushMetric(MetricsRecord)`. `MetricsRegistry` synchronously registers metrics by name and returns metric names or metric objects. `MetricsIntValue` and `MetricsLongValue` are set-on-change gauges pushed once after update. `MetricsTimeVaryingInt` and `MetricsTimeVaryingLong` accumulate interval deltas and reset after push. `MetricsTimeVaryingRate` accumulates operation counts and elapsed time, publishes previous-interval averages, and tracks min/max operation time until `resetMinMax()`.

### Network utilities and topology

`CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping` and caches resolved rack paths. `DNSToSwitchMapping.resolve(List)` maps hostnames/IPs one-to-one to network location paths such as `/datacenter/rack`. `ScriptBasedMapping` is a final configurable implementation that runs the script configured by `topology.script.file.name`.

`DNS` provides direct and reverse lookup helpers: `reverseDns(InetAddress, String)`, `getIPs(String)`, `getDefaultIP(String)`, `getHosts(String[, String])`, and `getDefaultHost(String[, String])`.

`NetUtils` centralizes socket and address handling. It loads per-protocol or default socket factories from `Configuration`, builds socket addresses from host:port or filesystem-style URIs, migrates old host/port config pairs to a combined address, maintains static hostname resolutions for tests, returns client-safe addresses for servers bound to `0.0.0.0`, wraps sockets in timeout-aware `SocketInputStream`/`SocketOutputStream` when channels are available, connects channel-backed sockets through Hadoop selectors, and normalizes hostnames to textual IP addresses.

`NetworkTopology` models a hierarchical cluster tree. It can add/remove leaf nodes, check membership, lookup paths, count racks/leaves, compute node distance by closest common ancestor, test same-rack placement, choose random nodes inside or outside a scope, count available nodes excluding a list, print the topology, and pseudo-sort replica nodes by locality to a reader. Constants include `DEFAULT_RACK` and `DEFAULT_HOST_LEVEL`.

`Node` is the topology node interface: name, network location, parent, and tree level. `NodeBase` implements it with constructors from path, name/location, and explicit parent/level, plus static `getPath(Node)` and `normalize(String)`.

### Socket stream and socket factory APIs

`SocketInputStream` extends `InputStream` and implements `ReadableByteChannel`. Its constructors accept a `ReadableByteChannel` or `Socket` plus timeout, configure the channel non-blocking, and expose byte-array reads, `ByteBuffer` reads, `waitForReadable()`, `getChannel()`, `isOpen()`, and synchronized `close()`. Docs warn that after wrapping a socket channel, direct `Socket.getInputStream()`/`getOutputStream()` use can throw `IllegalBlockingModeException`.

`SocketOutputStream` similarly extends `OutputStream` and implements `WritableByteChannel`, with timeout-aware writes, `waitForWritable()`, `transferToFully(FileChannel,long,int)`, `getChannel()`, and synchronized `close()`. `transferToFully` loops until the requested count is transferred or throws EOF/timeout/IO errors.

`SocksSocketFactory` extends `SocketFactory` and implements `Configurable`, constructing sockets through an optional SOCKS proxy and implementing equality/hash based on proxy configuration. `StandardSocketFactory` exposes the normal socket creation overloads and equality/hash behavior.

### Record I/O runtime

`BinaryRecordInput`/`BinaryRecordOutput`, `CsvRecordInput`/`CsvRecordOutput`, and `XmlRecordInput`/`XmlRecordOutput` implement the common `RecordInput` and `RecordOutput` contracts for primitive values, strings, buffers, records, vectors, and maps. Binary input/output include static thread-local `get(DataInput)` and `get(DataOutput)` helpers. All read/write methods use field tags even when the underlying format is positional.

`Buffer` is a mutable byte sequence used as the record system's native buffer type. It distinguishes logical count from backing capacity, can replace or copy backing bytes, append ranges, reset, truncate capacity to count, expose backing storage, compare lexicographically, clone, and convert to strings with default or named charset.

`Index` is the iteration contract returned by `startVector` and `startMap`, with `done()` and `incr()`. `Record` is the abstract base for generated records and implements `WritableComparable` and `Cloneable`; it defines serialization/deserialization through `RecordInput`/`RecordOutput`, archive-based overloads, `write(DataOutput)`, `readFields(DataInput)`, `compareTo`, and `toString`. `RecordComparator` registers class-specific comparators and compares serialized records.

`Utils` contains record wire-format helpers: parse float/double from byte arrays, read/write zero-compressed variable-length ints/longs from byte arrays or streams, compute variable-length encoded sizes, lexicographically compare byte ranges, and expose hex digits.

### Record compiler APIs

`CodeBuffer` wraps `StringBuffer` with automatic indentation. `Consts` exposes string constants used by generated Record I/O code, including record input/output variable names and tags. `JType` is the abstract compiler type base; concrete or composite type classes include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`. `JField` wraps a record field. `JFile` models one record DDL file with includes and record definitions and can `genCode(language, destDir, options)` for lower-case language names.

`RccTask` is the Ant task for invoking the Hadoop record compiler. It accepts a single `file` or nested `FileSet`, `language` (`java` or `c++`), destination directory, and `failonerror`; `execute()` compiles each record definition file.

The chunk ends in `org.apache.hadoop.record.compiler.generated.ParseException`, a JavaCC-style checked exception. It has the generated-parser constructor using `Token`, expected token sequences, and token images; default/string constructors; `getMessage()` that builds parse diagnostics from token state; and a protected `add_escapes(String)` helper.

## Control Flow and Behavioral Contracts

RPC server flow is lifecycle driven: bind/start the service, accept connections with a versioned header, authorize the `Subject` against `ConnectionHeader`, queue calls, dispatch to the protocol-aware abstract `call(Class, Writable, long)`, track queue and processing time through `RpcMetrics`, then stop and join. The non-protocol `call(Writable,long)` is explicitly deprecated in favor of the class-aware overload.

Metrics flow starts with `ContextFactory.getFactory()` loading `hadoop-metrics.properties`, then `MetricsUtil` or callers obtain a `MetricsContext`, create `MetricsRecord` objects, set tags and metrics, and call `update()`. `AbstractMetricsContext` periodically invokes registered `Updater` instances, converts buffered `MetricsRecordImpl` rows into `OutputRecord` values, calls subclass `emitRecord`, and then `flush()`. JMX reads the registry through dynamic MBeans, while null contexts can either discard all data or keep periodic updates active for sampled metrics.

Network flow has three main paths: address parsing and socket factory selection through `NetUtils`, topology resolution through `DNSToSwitchMapping` and `NetworkTopology`, and timeout-aware socket IO through channel-backed stream wrappers. `NetUtils.connect` avoids JDK thread-local selector leakage for channel-backed sockets by using Hadoop's selector logic.

Topology control flow is tree based: `NodeBase` normalizes path-like rack locations, `NetworkTopology.add/remove` updates leaf/rack counters, distance is computed through parent chains to a common ancestor, and replica ordering uses a locality-biased pseudo-sort rather than a full stable sort.

Record serialization flow is generated-code friendly. Generated `Record` subclasses call `RecordOutput.startRecord`, write each field with a tag, emit nested vectors/maps through `startVector`/`startMap`, and finish with `endRecord`; deserialization mirrors that through `RecordInput`. Binary, CSV, and XML implementations share the same logical contract but differ in on-wire representation.

Record compiler flow is DDL to generated sources: an Ant `RccTask` gathers `.jr` files, configures language and destination, invokes compiler structures represented by `JFile`, `JRecord`, `JField`, and `JType` instances, and reports JavaCC parse errors through `ParseException`.

## State and Persistence

RPC state includes the server's bound listener address, open connection count, call queue length, socket send buffer size, connection header/version state, and `RpcMetrics` registry values. Metrics around queue and processing times are interval based and persisted only in memory until pushed to the configured metrics sink or exposed via JMX.

Metrics state is split across factory attributes, context instances, buffered record rows, registered updaters, metric registries, and individual metric objects. `FileContext` persists emitted records to an append-mode file when configured; `GangliaContext` sends them over the network; JMX MBeans expose process-local state. `MetricsIntValue`/`MetricsLongValue` push only after being set, while time-varying metrics roll current interval counters into previous interval fields on push.

Network state includes DNS-to-rack caches in `CachedDNSToSwitchMapping`, static host resolutions in `NetUtils`, `NetworkTopology`'s mutable tree of `Node` objects plus rack/leaf counters, and non-blocking selector/channel state inside socket streams. `SocksSocketFactory` persists proxy settings through Hadoop `Configuration`.

Record I/O state includes mutable `Buffer` backing arrays/count/capacity, `Record` subclass fields, archive/stream cursor position, `Index` iteration state for vectors/maps, and record compiler AST-like structures. Binary record input/output thread-local helpers reuse wrapper objects around caller-supplied `DataInput`/`DataOutput`; callers must treat backing storage and mutable wrappers carefully.

The XML file itself is a persistence artifact for JDiff compatibility, recording public API signatures, deprecations, checked exceptions, inheritance, and docs for Hadoop 0.20.0.

## Dependencies and Integration Points

Visible dependencies include Java IO/NIO/networking (`InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `Socket`, `SocketAddress`, `SocketFactory`, `InetSocketAddress`, `FileChannel`, selectable channels), Java management (`DynamicMBean`, `ObjectName`, JMX exceptions), servlet APIs, JavaCC parser classes, Log4J, Apache Commons Logging, and Ant.

Hadoop dependencies include `Configuration`, `Configurable`, `Writable`, `WritableComparable`, IPC `ConnectionHeader` and `Server`, security `AuthorizationException`, and the metrics interfaces. The metrics packages integrate with daemon metrics such as NameNode/DataNode/RPC/JVM metrics through `Updater`, `MetricsRecord`, `MetricsRegistry`, and MBeans.

Network classes are integration points for HDFS block placement, rack-aware MapReduce scheduling, RPC client creation, daemon tests with fake hostnames, and file-transfer loops that rely on timeout-aware streams. Record I/O classes integrate with generated record classes, Hadoop RPC payloads that still use `Writable`, Ant builds, and JavaCC-generated parser code.

## Risks and Edge Cases

- This is API XML, so implementation details such as exact locking, cache invalidation, selector cleanup, file format bytes, and error recovery paths must be verified in source code.
- The chunk starts mid-`Server`; constructors and earlier fields/methods are outside this range. It also ends before `ParseException.add_escapes` is complete.
- `Server.call(Writable,long)` is deprecated; callers implementing only the old hook may not participate correctly in protocol-version-aware dispatch.
- Metrics records are atomic on `update()` but individual `MetricsRecord` instances are not safe for concurrent shared mutation.
- The default metrics context silently discards data, so missing `hadoop-metrics.properties` can look like a monitoring failure even when code is updating metrics.
- Sampled/averaged metrics require a context with periodic update calls; plain `NullContext` does not drive interval rollovers.
- `MetricsRegistry.add` rejects duplicate names, so holding classes need unique metric names across a registry.
- Socket channel wrappers force non-blocking mode; using the original socket streams afterward can fail.
- Timeout arguments may not apply when sockets do not have channels and fall back to JDK stream behavior.
- Static hostname resolutions and cached DNS-to-switch mappings can create stale topology behavior in long-running tests or daemons.
- Network topology methods assume valid leaf nodes and rack paths; null, non-leaf, or out-of-cluster nodes can trigger `IllegalArgumentException`.
- Synchronized markers are present on metric value operations and some lifecycle methods, but many topology and NetUtils methods are not declared synchronized in the API snapshot.
- `Buffer.get()` exposes backing storage beyond logical length; consumers must honor `getCount()`.
- Binary record input/output thread-local reuse can surprise callers if wrappers are retained while underlying streams change.
- CSV/XML tagged serialization may diverge from binary positional assumptions; generated records need format-specific round-trip tests.
- `RccTask` can continue or fail based on `failonerror`, so build behavior depends on Ant configuration.
- JavaCC `ParseException` diagnostic quality depends on token images and expected token sequences being populated by generated parser code.

## Test Signals

Good test coverage inferred from this API slice should include:

- RPC server lifecycle tests for bind/start/stop/join, listener address reporting, open connection and queue metrics, authorization success/failure, and compatibility of deprecated versus protocol-aware `call` overrides.
- RPC metrics tests that increment queue/processing times, update open connection and queue length gauges, push through `RpcMetrics.doUpdates`, expose JMX attributes through `RpcActivityMBean`, and reset min/max values through `RpcMgtMBean`.
- Metrics framework tests for context factory property loading, class-based context creation, null-context fallback, record tag/metric typing, `update()` replacing rows with matching tags, `remove()` semantics, updater registration/unregistration, and file/Ganglia/null/composite contexts.
- Metric utility tests for one-shot int/long gauge pushes, interval delta reset for time-varying int/long metrics, average/min/max behavior for `MetricsTimeVaryingRate`, duplicate registry names, and dynamic MBean attribute access.
- LogLevel tests for CLI argument handling and servlet `doGet` behavior in daemon web contexts.
- DNS and NetUtils tests for reverse lookup failures, interface IP/host resolution, socket factory config fallback, malformed socket factory properties, URI and host:port address parsing, old/new server address migration, static resolution lifecycle, `0.0.0.0` connect-address rewriting, and hostname normalization.
- Socket stream tests for channel-backed read/write timeouts, zero timeout behavior, close idempotency, `waitForReadable`/`waitForWritable`, `transferToFully` EOF handling, and failure when mixing wrapped non-blocking channels with original socket streams.
- Network topology tests for path normalization, add/remove counters, duplicate or non-leaf additions, distance and same-rack calculations, random choice within and outside scopes, excluded-node counts, and pseudo-sort locality ordering.
- Record I/O tests for binary/CSV/XML round trips of all primitive types, strings, buffers, records, vectors, and maps; malformed input handling; tag handling; and `Index` iteration behavior.
- `Buffer` tests for capacity versus count, copy versus set backing behavior, append growth, truncate/reset, charset conversion, clone independence, equality/hash, and lexicographic comparison.
- `Record` and `RecordComparator` tests for `Writable` round trips, archive overloads, compare ordering, string conversion, and custom comparator registration.
- `Utils` tests for variable-length int/long boundary values, negative encoding, encoded size calculation, byte-array and stream decoding parity, float/double byte parsing, and byte-range comparison.
- Record compiler tests for `JFile.genCode` language selection, included files, primitive/composite type code generation, Ant `RccTask` file and fileset modes, `failonerror`, destination directory handling, and `ParseException.getMessage()` diagnostics.

## Chunk Boundary Notes

The previous chunk is needed for the start of `org.apache.hadoop.ipc.Server` and any earlier IPC classes. The following chunk is needed for the rest of `ParseException.add_escapes` and subsequent generated compiler/parser classes. Final reconciliation should keep this document source-tree-aligned and treat the APIs here as a Hadoop 0.20.0 compatibility snapshot, not current Hadoop behavior.
