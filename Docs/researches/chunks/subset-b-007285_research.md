# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 30887-37164

## Chunk Scope

This chunk is a JDiff XML API snapshot for Hadoop 0.18.3. It starts immediately after `org.apache.hadoop.metrics.spi.MetricsRecordImpl` and covers complete API descriptions for several packages plus the opening portion of `org.apache.hadoop.util.GenericOptionsParser`. The document is metadata, not implementation source: control flow, state, persistence, and risk notes below are inferred from public signatures, visibility, declared exceptions, implemented interfaces, constants, and embedded Javadocs.

Covered package areas:

- `org.apache.hadoop.metrics.spi` and `org.apache.hadoop.metrics.util`
- `org.apache.hadoop.net`
- `org.apache.hadoop.record`, `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, `org.apache.hadoop.record.compiler.generated`, and `org.apache.hadoop.record.meta`
- `org.apache.hadoop.security`
- `org.apache.hadoop.tools`
- `org.apache.hadoop.util`

## Purpose

The chunk records public Hadoop common APIs for metrics emission, network/rack topology, socket timeout streams, Hadoop Record I/O serialization, the record compiler parser surface, record schema metadata, Unix-style user/group identity, command-line tools, and low-level utilities. Its direct purpose is compatibility research: every `<class>`, `<interface>`, constructor, method, field, implemented type, visibility flag, synchronization flag, deprecation marker, and declared exception is part of the API comparison surface used by JDiff.

At the subsystem level, the APIs expose:

- Metrics contexts and mutable metrics wrappers that bridge Hadoop metrics records and JMX registration.
- Network utilities for DNS, socket factories, non-blocking socket streams with read/write timeouts, rack topology, and script-backed host-to-switch mapping.
- A legacy Hadoop Record I/O stack: tagged and untagged serializers/deserializers, generated `Record` base classes, raw comparators, variable-length encodings, XML/CSV/binary formats, an IDL compiler, and schema/type metadata.
- Security identity classes based on Unix users and groups, including writable serialization and configuration-backed persistence.
- Tool entry points for `DistCp`, Hadoop archives, and log analysis.
- Utility classes for cyclic map iteration, daemon threads, disk checks, and generic Hadoop option parsing.

## Important APIs, Types, and Functions

### Metrics SPI and Utilities

- `MetricValue` wraps a `Number` with a boolean mode, exposed through `isIncrement()`, `isAbsolute()`, `getNumber()`, and constants `ABSOLUTE` and `INCREMENT`. It models whether a metric update replaces the current value or increments it.
- `NullContext` extends `AbstractMetricsContext` and provides do-nothing `startMonitoring()`, `emitRecord(...)`, `update(...)`, and `remove(...)`. It is the default context when metrics configuration is absent.
- `NullContextWithUpdateThread` also extends `AbstractMetricsContext`, but its doc says it keeps periodic updater behavior while emitting no records. It initializes with `init(String, ContextFactory)` and leaves `emitRecord`, `update`, and `remove` as no-ops.
- `OutputRecord` exposes read-only metric output access through `getTagNames()`, `getTag(String)`, `getMetricNames()`, and `getMetric(String)`.
- `Util.parse(String specs, int defaultPort)` parses comma/space-delimited host specifications into `List<InetSocketAddress>`, defaulting null specs to localhost on the supplied port.
- `MBeanUtil.registerMBean(String serviceName, String nameName, Object theMbean)` and `unregisterMBean(ObjectName)` standardize Hadoop MBean names, using JMX `ObjectName`.
- `MetricsIntValue` and `MetricsLongValue` are synchronized mutable point metrics with `set`, `get`, `inc`, `dec`, and `pushMetric(MetricsRecord)`. Their docs say `pushMetric` only publishes when updated since the previous push and does not itself push to JMX.
- `MetricsTimeVaryingInt` is a synchronized interval counter with `inc`, `pushMetric`, and `getPreviousIntervalValue()`.
- `MetricsTimeVaryingRate` is a synchronized interval rate metric with `inc(numOps,time)`, `inc(time)`, `pushMetric`, previous-interval operation count and average time getters, min/max getters, and `resetMinMax()`.

### Network and Socket APIs

- `DNS` provides static reverse DNS and interface lookup helpers: `reverseDns(InetAddress,String)`, `getIPs(String)`, `getDefaultIP(String)`, `getHosts(String,String)`, `getHosts(String)`, `getDefaultHost(String,String)`, and `getDefaultHost(String)`. Declared failures include `NamingException` and `UnknownHostException`.
- `DNSToSwitchMapping` is the rack-resolution interface: `resolve(List<String>) -> List<String>`.
- `NetUtils` is the main networking utility class. It exposes configurable socket factories, address parsing, server-address synthesis, static host resolution overrides, connect-address rewriting, and socket stream adapters:
  - `getSocketFactory(Configuration, Class)` and `getDefaultSocketFactory(Configuration)`
  - `getSocketFactoryFromProperty(Configuration, String)`
  - `createSocketAddr(String)` and `createSocketAddr(String, int)`
  - `getServerAddress(Configuration, String, String, String)`
  - `addStaticResolution(String,String)`, `getStaticResolution(String)`, `getAllStaticResolutions()`
  - `getConnectAddress(Server)`
  - `getInputStream(Socket)`, `getInputStream(Socket,long)`, `getOutputStream(Socket)`, `getOutputStream(Socket,long)`
- `NetworkTopology` models a cluster as a tree of racks, switches, and leaves. Public operations include `add(Node)`, `remove(Node)`, `contains(Node)`, `getNode(String)`, rack and leaf counts, `getDistance(Node,Node)`, `isOnSameRack(Node,Node)`, `chooseRandom(String)`, `countNumOfAvailableNodes(String,List<Node>)`, `toString()`, and synchronized `pseudoSortByDistance(Node,Node[])`. Public constants include `DEFAULT_RACK`, `UNRESOLVED`, `DEFAULT_HOST_LEVEL`, and `LOG`.
- `Node` defines topology node shape: network location, name, parent, and level getters/setters.
- `NodeBase` implements `Node` and stores protected mutable fields `name`, `location`, `level`, and `parent`. It includes constructors from path, name/location, and explicit parent/level. Static helpers include `getPath(Node)` and `normalize(String)`, with path constants `PATH_SEPARATOR`, `PATH_SEPARATOR_STR`, and `ROOT`.
- `ScriptBasedMapping` is a final `Configurable` implementation of `DNSToSwitchMapping`, using `topology.script.file.name`.
- `SocketInputStream` extends `InputStream` and implements `ReadableByteChannel`. Constructors accept `ReadableByteChannel` or `Socket` plus timeout. It exposes `read()`, `read(byte[],int,int)`, `read(ByteBuffer)`, synchronized `close()`, `getChannel()`, `isOpen()`, and `waitForReadable()`. Its docs warn that it configures the channel non-blocking, so callers must use matching Hadoop socket stream wrappers after construction.
- `SocketOutputStream` extends `OutputStream` and implements `WritableByteChannel`. It mirrors input behavior with `write(int)`, `write(byte[],int,int)`, `write(ByteBuffer)`, synchronized `close()`, `getChannel()`, `isOpen()`, `waitForWritable()`, and `transferToFully(FileChannel,long,int)`.
- `SocksSocketFactory` extends `SocketFactory` and implements `Configurable`, with five `createSocket` overloads, configurable proxy support, and equality/hash behavior.
- `StandardSocketFactory` extends `SocketFactory` with the normal five socket-creation overloads and equality/hash behavior.

### Record I/O Runtime APIs

- `BinaryRecordInput` and `BinaryRecordOutput` implement `RecordInput` and `RecordOutput` respectively, with constructors over streams or `DataInput`/`DataOutput`, static `get(...)` factories, primitive read/write methods, string and `Buffer` support, and record/vector/map boundary methods.
- `CsvRecordInput` and `CsvRecordOutput` implement the same interfaces over CSV-style streams.
- `XmlRecordInput` and `XmlRecordOutput` implement the same interfaces for XML-tagged record serialization.
- `Buffer` is a resizable byte sequence with constructors from byte arrays, `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, append overloads, `hashCode`, `compareTo`, `equals`, `toString`, `toString(String charsetName)`, and `clone`.
- `Index` is the vector/map deserialization cursor interface with `done()` and `incr()`.
- `Record` is the abstract generated-record base. It implements `WritableComparable` and `Cloneable`, requires tagged `serialize(RecordOutput,String)`, tagged `deserialize(RecordInput,String)`, and `compareTo(Object)`, and supplies untagged serialize/deserialize plus Hadoop `Writable` `write(DataOutput)` and `readFields(DataInput)`.
- `RecordComparator` extends `WritableComparator`, defines raw byte-array `compare(...)`, and has synchronized static `define(Class, RecordComparator)` registration for optimized record comparators.
- `RecordInput` and `RecordOutput` are the core serializer interfaces. They enumerate primitive, string, buffer, record, vector, and map operations. Tags are explicitly for tagged formats such as XML.
- `org.apache.hadoop.record.Utils` provides byte/stream utility codecs: float and double parsing from byte arrays, zero-compressed variable-length int/long reads from byte arrays or `DataInput`, encoded-size calculation, variable-length writes to `DataOutput`, and byte comparison. It exposes `hexchars`.

### Record Compiler and Generated Parser APIs

- `CodeBuffer` only exposes `toString()`, acting as a code-generation buffer abstraction.
- `Consts` holds compiler string constants such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract compiler type base. Concrete and composite types include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JBuffer`, `JString`, `JMap`, `JVector`, and `JRecord`; `JMap`, `JVector`, and `JRecord` take nested type or field metadata in constructors.
- `JField<T>` stores a named compiler field. `JFile` aggregates included files and records and exposes `genCode(String language, String destDir) -> int`.
- `RccTask` is an Ant task wrapper for the record compiler. It supports `language`, `file`, `failonerror`, `destdir`, nested `FileSet`s, and `execute()`, which invokes record compilation.
- `ParseException`, `Rcc`, `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError` are JavaCC-generated parser components for the record compiler. `Rcc` parses `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, and exposes token access, parser reinitialization, parse-exception generation, and tracing toggles.
- `RccConstants` defines token IDs for module, record, include, primitive types, vector/map, punctuation, strings, identifiers, lexical states, and token images.
- `SimpleCharStream` manages parser input buffering, line/column tracking, backup, reinitialization over readers or input streams with optional encodings, image/suffix retrieval, and buffer cleanup. Its doc says it assumes ASCII and does not process Unicode.
- `Token` stores token kind, position, image, next token, and special-token chain; `Token.newToken(int)` is the extensibility hook.
- `TokenMgrError` formats lexical errors and can escape unprintable characters.

### Record Metadata APIs

- `FieldTypeInfo` couples a field ID/name to a `TypeID`, with getters, `equals`, and `hashCode`.
- `TypeID` represents primitive type identifiers, exposes `getTypeVal()`, equality, hash code, singleton constants for primitive record types, and protected `typeVal`.
- `TypeID.RIOType` contains byte constants for supported IDL types: bool, buffer, byte, double, float, int, long, map, string, struct, and vector.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` to describe composite element/key/value/record types.
- `RecordTypeInfo` extends `Record` and can serialize/deserialize schema metadata. It supports `getName`, `setName`, `addField`, `getFieldTypeInfos`, one-level `getNestedStructTypeInfo`, `serialize`, `deserialize`, and `compareTo`.
- `org.apache.hadoop.record.meta.Utils.skip(RecordInput,String,TypeID)` skips data in a record input according to type metadata.

### Security APIs

- `UnixUserGroupInformation` extends `UserGroupInformation`. It can be constructed from username/groups or array form, can create immutable instances, exposes username and groups, implements `readFields(DataInput)` and `write(DataOutput)`, persists to configuration with `saveToConf(Configuration,String,UnixUserGroupInformation)`, reads from configuration with `readFromConf`, and has three `login` overloads for Unix/config-backed identity. It also defines equality, hash code, string conversion, and `UGI_PROPERTY_NAME`.
- `UserGroupInformation` is an abstract `Writable` identity base. It exposes thread-local current identity with `getCurrentUGI()` and `setCurrentUGI(UserGroupInformation)`, abstract `getUserName()` and `getGroupNames()`, static `login(Configuration)`, static `readFrom(Configuration)`, and `LOG`.

### Tools and General Utilities

- `DistCp` implements `Tool`, has configuration accessors, static `copy(Configuration,String,String,Path,boolean,boolean)`, `run(String[])`, `main(String[])`, and `getRandomId()`. Its run doc describes recursive cross-filesystem directory copy using MapReduce mappers and no reducer.
- `DistCp.DuplicationException` is an `IOException` for duplicate source files with public `ERROR_CODE`.
- `HadoopArchives` implements `Tool`, has configuration accessors, `archive(List<Path>,String,Path)`, `run(String[])`, and `main(String[])` for Hadoop archive creation.
- `Logalyzer` archives and analyzes Hadoop logs via `doArchive(String,String)`, `doAnalyze(String,String,String,String,String)`, and `main(String[])`.
- `Logalyzer.LogComparator` extends `Text.Comparator`, implements `Configurable`, and compares raw text keys using configurable sort columns.
- `Logalyzer.LogRegexMapper` extends `MapReduceBase` and implements `Mapper<K,Text,Text,LongWritable>`, with `configure(JobConf)` and `map(...)`.
- `CyclicIteration<K,V>` is an `Iterable<Map.Entry<K,V>>` over a `SortedMap`, starting after a given key and wrapping from end to beginning.
- `Daemon` extends `Thread`, has constructors for empty, `Runnable`, and `ThreadGroup/Runnable`, stores a retrievable runnable via `getRunnable()`, and is documented as setting daemon mode true.
- `DiskChecker` exposes `mkdirsWithExistsCheck(File)` and `checkDir(File)`, plus nested `DiskErrorException` and `DiskOutOfSpaceException`.
- `GenericOptionsParser` begins at the end of the chunk. Visible APIs include constructors for Hadoop generic options alone or generic plus caller-supplied commons-cli `Options`, `getRemainingArgs()`, `getCommandLine()`, and `printGenericCommandUsage(PrintStream)`. The visible docs list generic Hadoop CLI flags such as `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`; the class body continues after this chunk.

## Control Flow

Because this is an API descriptor, executable control flow is not present directly. The main inferred flows are:

- Metrics update flow: callers mutate synchronized metric wrappers, periodic metrics context updates call `pushMetric(MetricsRecord)`, and each wrapper emits only data changed since the prior interval. JMX uses getters rather than `pushMetric`.
- Null metrics flow: when no metrics configuration exists, `NullContext` absorbs lifecycle, update, remove, and emit calls. `NullContextWithUpdateThread` keeps the `AbstractMetricsContext` updater thread active while suppressing emission, supporting pull-style systems such as JMX.
- Network resolution flow: host/interface names are resolved through `DNS`, mapped to racks through `DNSToSwitchMapping` or `ScriptBasedMapping`, represented as `Node`/`NodeBase`, and inserted into `NetworkTopology`. Replica placement/read optimization can ask the topology for distance, rack locality, random choices under a scope, and pseudo-sorting by distance.
- Socket timeout flow: `NetUtils` chooses a socket factory from configuration and wraps channel-backed sockets in `SocketInputStream`/`SocketOutputStream` when timeout-aware channel I/O is needed. Those wrappers convert blocking channels to non-blocking selectable channels and wait for readiness before read/write or file-channel transfer.
- Record serialization flow: generated `Record` subclasses call `serialize`/`deserialize` with a `RecordOutput`/`RecordInput`; concrete binary, CSV, or XML implementations handle primitive values and structural boundaries. `Index` controls vector/map deserialization loops.
- Record compiler flow: Ant or CLI invokes `Rcc`, which lexes through `SimpleCharStream` and `RccTokenManager`, parses includes/modules/records/fields/types into `JFile`, `JRecord`, `JField`, and `JType` objects, and then generates code through `JFile.genCode(...)`.
- Record metadata flow: `RecordTypeInfo` serializes schema information as a `Record`; `TypeID` and composite subclasses describe field types; metadata utilities can skip unknown or unwanted fields based on type IDs.
- UGI flow: callers establish thread-local identity with `UserGroupInformation.setCurrentUGI`, read/write identity through Hadoop `Writable`, and either login from Unix state or load/save comma-separated user/group strings in `Configuration`.
- Tool flow: `DistCp`, `HadoopArchives`, and `Logalyzer` expose `Tool.run`/`main` entry points that translate command-line arguments into MapReduce jobs or filesystem/archive operations.

## State and Persistence Behavior

- Metrics wrappers hold mutable in-memory counters, previous-interval values, and update flags. Method synchronization on metric mutation and push APIs is explicitly part of the public signature for the utility metric classes.
- `MetricValue` holds a numeric value plus absolute/increment mode. `OutputRecord` exposes collected tag/metric maps as read-only lookup APIs.
- `MBeanUtil` persists no local state in the API, but registers and unregisters process-level JMX MBeans through the platform MBean server.
- `NetworkTopology` maintains a mutable tree of `Node` objects plus rack and leaf counts. `NodeBase` stores mutable parent/level/location/name fields, making topology correctness dependent on consistent updates.
- `NetUtils` exposes static host-resolution overrides, implying JVM-wide mutable resolution state through `addStaticResolution`, `getStaticResolution`, and `getAllStaticResolutions`.
- `SocketInputStream` and `SocketOutputStream` hold channel, timeout, and open/closed state; synchronized `close()` marks an important concurrency boundary.
- `Buffer` separates logical count from capacity and supports in-place resize, truncate, reset, append, clone, and byte-array exposure.
- `Record` implementations persist through Hadoop `Writable` streams and through tagged/untagged Record I/O formats. `RecordTypeInfo` persists schema metadata using the same record serialization framework.
- `UnixUserGroupInformation` persists identity both as writable binary data and as a comma-separated configuration property. Its docs mention a UGI map/cache keyed by user identity, so repeated logins/config reads can return cached objects.
- `UserGroupInformation` stores current identity per thread.
- `DistCp`, `HadoopArchives`, and `Logalyzer` persist outputs in distributed filesystems: copies, archive contents/indexes, archived logs, and analysis output directories.
- `GenericOptionsParser` mutates a supplied `Configuration` according to generic CLI arguments and retains remaining arguments / parsed `CommandLine` state.

## Dependencies and Integration Points

- Metrics APIs depend on `org.apache.hadoop.metrics.MetricsRecord`, `ContextFactory`, and SPI classes such as `AbstractMetricsContext`, `MetricsRecordImpl`, and `OutputRecord`.
- JMX integration uses `javax.management.ObjectName`.
- Network APIs depend on Java networking/NIO/JNDI classes (`Socket`, `SocketFactory`, `Proxy`, `InetSocketAddress`, `NetworkInterface` by implication, channels, selectors, DNS naming exceptions), Hadoop `Configuration`, `Configurable`, and IPC `Server`.
- Topology APIs integrate with HDFS/MapReduce placement logic through `Node`, rack names, and distance/locality sorting.
- Socket wrappers integrate with Java `FileChannel.transferTo/transferFrom`, Hadoop RPC sockets, and `NetUtils` factory-created sockets.
- Record I/O depends on Hadoop `WritableComparable`, `WritableComparator`, and Java `DataInput`/`DataOutput`/streams. It also provides interoperability across binary, CSV, and XML encodings.
- Compiler APIs integrate with Ant (`Task`, `FileSet`, `BuildException`) and JavaCC-generated parsing classes.
- Record metadata integrates with record serialization to support schema-aware skipping and nested type descriptions.
- Security APIs integrate with Hadoop `Configuration`, `Writable`, Unix OS account/group discovery, JAAS `LoginException`, and thread-local execution identity.
- Tool APIs integrate with Hadoop `Tool`, `Path`, `FileSystem` behavior, MapReduce `Mapper`, `OutputCollector`, `Reporter`, `JobConf`, and text comparators.
- `GenericOptionsParser` integrates Hadoop generic CLI handling with Apache Commons CLI.

## Risks and Edge Cases

- This XML chunk exposes public API but not implementation bodies. Any behavioral claim beyond signatures and embedded docs must be validated against the corresponding Java sources.
- The chunk starts at the end marker for `MetricsRecordImpl` and ends inside `GenericOptionsParser`, so neither class is fully represented here.
- Many APIs are public and not deprecated in this snapshot; compatibility-sensitive changes include method visibility, synchronization flags, checked exceptions, generic signatures, field constants, and implemented interfaces.
- Metrics wrappers rely on synchronized methods for thread safety. Removing synchronization or changing push-on-update semantics would affect metrics consistency and JMX visibility.
- `NullContextWithUpdateThread` intentionally keeps sampling without emission. Treating it as a pure no-op could break pull-based metrics systems.
- `SocketInputStream` and `SocketOutputStream` switch channels to non-blocking mode. Mixing them with raw `Socket.getInputStream()` or `Socket.getOutputStream()` after wrapper creation is explicitly unsafe.
- Timeout semantics differ depending on whether sockets have associated channels. `NetUtils` docs warn that fallback raw socket streams ignore wrapper timeout arguments and use socket-level SO_TIMEOUT or blocking behavior.
- `NetworkTopology` operations can throw or behave incorrectly for null nodes, non-leaf additions, nodes not in the cluster, malformed paths, or inconsistent parent/level state.
- `ScriptBasedMapping` depends on external script configuration, making rack resolution vulnerable to missing scripts, bad output cardinality, or slow/failed script execution.
- `Buffer.get()` exposes byte-array storage; callers can mutate buffer contents unless implementation copies defensively. Count/capacity differences must be respected.
- CSV/XML/binary Record I/O formats share an interface but have different tagging and escaping rules. Tagged `tag` parameters matter for XML and may be ignored elsewhere.
- JavaCC parser classes expose many mutable public/protected fields. These are compatibility liabilities and are easy to misuse directly.
- `SimpleCharStream` is documented as ASCII-only, so Unicode record definitions may fail or produce incorrect positions unless the underlying implementation handles more than this doc promises.
- `RecordTypeInfo.compareTo` is documented ambiguously: it says the class is not meant for comparison and also says it returns zero for another `RecordTypeInfo`. Callers should not rely on meaningful ordering.
- `UnixUserGroupInformation` string persistence is comma-separated; malformed strings, too few fields, null entries, or group names containing separators are risk areas.
- Thread-local UGI state can leak across pooled threads if not reset.
- `DistCp` duplicate handling and source-list behavior are API-visible through `DuplicationException`, `srcAsList`, and `ignoreReadFailures`; regressions here can affect large filesystem copy jobs.
- `DiskChecker.mkdirsWithExistsCheck` exists specifically for concurrent directory creation races. Replacing it with plain `File.mkdirs()` would reintroduce race failures.
- `GenericOptionsParser` mutates caller-supplied configuration. Parse ordering and remaining-argument behavior are important for tools that layer their own options on top of generic Hadoop options.

## Test Signals

Useful validation signals for implementations represented by this chunk include:

- JDiff/API tests verifying all listed classes, interfaces, constructors, methods, fields, visibility, abstract/final/static flags, synchronized flags, implemented interfaces, return types, parameter types, and checked exceptions remain compatible.
- Metrics tests for one-shot `MetricsIntValue`/`MetricsLongValue` push behavior, interval reset behavior for `MetricsTimeVaryingInt`, rate average/min/max behavior for `MetricsTimeVaryingRate`, and no-emission behavior for both null contexts.
- JMX tests for `MBeanUtil` name formation and unregister behavior.
- DNS and `NetUtils` tests for interface lookup fallbacks, static resolution override precedence, address parsing with default ports, and server/connect address rewriting.
- Network topology tests for add/remove counters, rack counts, distance calculation, same-rack checks, random scope selection including `~` exclusions, excluded-node counts, and `pseudoSortByDistance` local/local-rack ordering.
- Socket stream tests for channel-backed timeout reads/writes, zero timeout, negative timeout rejection if implemented, close idempotence, readiness waits, `SocketTimeoutException`, and `transferToFully` EOF handling.
- Socket factory tests for configured SOCKS proxy behavior, equality/hash code, and all overloads.
- Record I/O round-trip tests across binary, CSV, and XML for primitives, strings, buffers, records, vectors, and maps, including tagged and untagged paths.
- Variable-length integer/long codec tests for boundary values around one-byte and multi-byte encodings, negative values, and stream/byte-array parity.
- `Buffer` tests for count vs capacity, append/truncate/reset, comparison ordering, charset conversion, equality, hash code, clone independence, and byte-array mutation behavior.
- Record compiler tests for IDL parsing of includes, modules, primitive/composite fields, parse errors, lexical errors, Ant task filesets, destination directories, fail-on-error behavior, and generated code compilation.
- Metadata tests for `TypeID` equality/hash behavior, composite type equality, `RecordTypeInfo` serialization/deserialization, nested struct lookup, and schema-based skip behavior.
- Security tests for UGI read/write round trips, configuration save/read, current-thread UGI isolation, Unix login fallback, malformed configuration handling, equality/hash code, immutable instance behavior, and group order preservation.
- Tool integration tests for `DistCp` source list mode, duplicate detection, read-failure ignore mode, MapReduce copy outputs, archive generation/indexing, log archive/analyze jobs, log comparator sorting columns, and regex mapper output counts.
- Utility tests for `CyclicIteration` wraparound ordering, daemon-thread flag and runnable retention, concurrent directory creation with `mkdirsWithExistsCheck`, `checkDir` failure modes, and `GenericOptionsParser` parsing of visible generic flags plus remaining-argument preservation.
