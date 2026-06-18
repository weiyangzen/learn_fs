# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 30886-37174

## Chunk Scope

This chunk is a JDiff API XML slice for Hadoop 0.18.2. It begins inside `org.apache.hadoop.metrics.spi.MetricValue`, covers complete packages for metrics utilities, networking, record I/O, record compiler/runtime metadata, security user/group identity, and tools, then ends inside `org.apache.hadoop.util.GenericsUtil`. Because the source is API metadata rather than Java implementation, it exposes public/protected signatures, inheritance, exceptions, fields, and Javadoc, but not method bodies.

## Purpose

The slice documents several common Hadoop infrastructure surfaces:

- Metrics contexts and value helpers used to collect, buffer, and publish metrics, including no-op contexts, JMX registration helpers, point-in-time values, and time-varying counters/rates.
- Network helpers for DNS/interface lookup, rack topology modeling, socket factories, and timeout-aware socket streams.
- The legacy Hadoop Record I/O runtime, including binary/CSV/XML serializers, deserializers, mutable buffers, raw comparators, record interfaces, and zero-compressed numeric encoding utilities.
- The Record I/O compiler API and JavaCC-generated parser/token support for `.jr` record definition files, plus an Ant task wrapper.
- User/group identity abstractions for Unix-backed Hadoop security state.
- Operational Hadoop tools for distributed copy, Hadoop archive creation, and log archiving/analysis.
- Early generic utility classes for daemon threads, disk checks, generic command-line option parsing, and Java generics helpers.

## Important APIs, Types, And Functions

### Metrics SPI and Utility APIs

- `org.apache.hadoop.metrics.spi.MetricValue` wraps a `Number` as either `ABSOLUTE` or `INCREMENT`, with `isIncrement()`, `isAbsolute()`, and `getNumber()`.
- `NullContext` extends `AbstractMetricsContext` and deliberately implements `startMonitoring()`, `emitRecord(...)`, `update(MetricsRecordImpl)`, and `remove(MetricsRecordImpl)` as no-ops. It is documented as the default context when no metrics configuration is found.
- `NullContextWithUpdateThread` also extends `AbstractMetricsContext`; it keeps the update thread behavior from the abstract context but emits no data. This is useful for metrics systems such as JMX that sample values by reading them externally.
- `OutputRecord` exposes read-only metric output shape: tag names, tag lookup, metric names, and metric lookup.
- `metrics.spi.Util.parse(String specs, int defaultPort)` parses comma/space separated `host` or `host:port` server specs into `InetSocketAddress` values, defaulting to localhost when specs are null.
- `MBeanUtil.registerMBean(serviceName, nameName, theMbean)` and `unregisterMBean(ObjectName)` integrate Hadoop metrics with JMX under the documented `hadoop.dfs:service=...,name=...` naming convention.
- `MetricsIntValue` and `MetricsLongValue` are synchronized mutable scalar metrics with `set`, `get`, increment/decrement overloads, and `pushMetric(MetricsRecord)`. They publish only after being updated and only once per update.
- `MetricsTimeVaryingInt` publishes interval deltas through `pushMetric(...)` and exposes `getPreviousIntervalValue()`.
- `MetricsTimeVaryingRate` tracks operation count and elapsed time through `inc(numOps, time)` / `inc(time)`, then exposes previous interval count, average time, min time, max time, and `resetMinMax()`.

### Networking APIs

- `DNS` provides reverse and forward lookup helpers: `reverseDns`, `getIPs`, `getDefaultIP`, `getHosts`, and `getDefaultHost`, with overloads for explicit or default nameservers and `UnknownHostException` / `NamingException` failure modes.
- `DNSToSwitchMapping.resolve(List<String>)` is the pluggable contract for resolving host/IP values to rack names, returning `NetworkTopology.DEFAULT_RACK` when topology cannot be determined.
- `NetUtils` centralizes socket factory and address handling: configurable socket factory lookup, default factory creation, proxy property interpretation, `createSocketAddr`, old host/port configuration transition via `getServerAddress`, static host resolution mappings, client connect address normalization, and timeout-aware socket input/output streams.
- `NetworkTopology` models the cluster as a rack/host tree. Public operations include adding/removing leaves, membership lookup, rack and leaf counts, distance and same-rack checks, scoped random choice, availability counting with exclusions, string rendering, and distance-based pseudo-sort.
- `Node` is the topology node interface with network location, name, parent, and tree level accessors/mutators. `NodeBase` implements it and adds path normalization and constants such as `PATH_SEPARATOR`, `ROOT`, and backing fields for name, location, level, and parent.
- `ScriptBasedMapping` implements both `Configurable` and `DNSToSwitchMapping`, using a configured script to map DNS names/IP addresses to switch or rack paths.
- `SocketInputStream` and `SocketOutputStream` wrap NIO channels or sockets to add read/write timeout behavior. They expose channel access, open checks, readiness waits, and byte/block read/write methods; output also provides `transferToFully(FileChannel, position, count)`.
- `SocksSocketFactory` is a `SocketFactory` with optional SOCKS `Proxy` and `Configurable` support. `StandardSocketFactory` is the ordinary non-proxy factory despite a copied Javadoc line claiming SOCKS behavior.

### Record I/O Runtime

- `BinaryRecordInput` / `BinaryRecordOutput` implement `RecordInput` / `RecordOutput` over `DataInput` and `DataOutput`, including thread-local `get(...)` factories and primitive/string/buffer/record/vector/map read/write methods.
- `CsvRecordInput` / `CsvRecordOutput` provide the same serializer interfaces for CSV-like textual record data.
- `XmlRecordInput` / `XmlRecordOutput` provide XML deserialization/serialization.
- `Buffer` is a mutable byte sequence implementing `Comparable` and `Cloneable`. It supports adopting or copying byte arrays, capacity changes, reset/truncate/append, lexicographic comparison, equality/hash, string conversion with optional encoding, and clone.
- `Index` is the iterator-like return type from `RecordInput.startVector` and `startMap`; callers loop with `done()` and `incr()` to deserialize collection elements.
- `Record` is the abstract base for generated records. It implements Hadoop `WritableComparable` and `Cloneable`, requires tagged `serialize`, tagged `deserialize`, and `compareTo`, and provides untagged serialization/deserialization plus `write(DataOutput)`, `readFields(DataInput)`, and `toString()`.
- `RecordComparator` extends `WritableComparator` for raw byte comparison and exposes synchronized static `define(Class, RecordComparator)` registration.
- `RecordInput` and `RecordOutput` are the core serializer/deserializer contracts for byte, boolean, int, long, float, double, string, `Buffer`, record, vector, and map boundaries. Tags are explicitly for tagged formats such as XML.
- `org.apache.hadoop.record.Utils` contains variable-length and zero-compressed numeric helpers: `readFloat`, `readDouble`, `readVLong`, `readVInt`, stream-based `readVLong` / `readVInt`, `getVIntSize`, `writeVLong`, `writeVInt`, and `compareBytes`.

### Record Compiler And Parser APIs

- `CodeBuffer` wraps `StringBuffer` with indentation behavior for generated code text.
- `Consts` defines Record I/O compiler constants such as `RIO_PREFIX`, runtime type info variables/filters, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract base for compiler type models. Concrete primitive and composite models include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`. `JField<T>` wraps a named field and type. `JFile` represents one record definition file, its includes, and records, and can `genCode(language, destDir, options)`.
- `RccTask` is an Ant `Task` that invokes the record compiler. It accepts `language`, single `file`, nested `FileSet`s, `destdir`, and `failonerror`; `execute()` throws `BuildException`.
- Generated parser classes in `org.apache.hadoop.record.compiler.generated` include:
  - `Rcc`, the JavaCC parser and command-line driver. It parses `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, returns compiler model objects, supports `ReInit`, and exposes token navigation and parse exception generation.
  - `RccConstants`, token ids for Record I/O grammar tokens including module, record, include, primitive types, vector/map delimiters, punctuation, string and identifier tokens, lexical states, and token images.
  - `RccTokenManager`, the lexer with debug stream, lexical state switching, token filling, and `getNextToken()`.
  - `SimpleCharStream`, the JavaCC character stream implementation with line/column tracking, buffer expansion/refill, backup, reinitialization overloads, image/suffix access, and cleanup.
  - `Token`, the token node structure with kind, begin/end positions, image, regular-token chain, and special-token chain.
  - `ParseException` and `TokenMgrError`, generated error-reporting classes that build parse/lexical diagnostics from current token, expected token sequences, token images, lexical state, and offending character context.

### Record Metadata APIs

- `FieldTypeInfo` pairs a field id with a `TypeID`, and implements equality and hash code.
- `TypeID` represents primitive Record I/O type ids and exposes shared constants for bool, buffer, byte, double, float, int, long, and string. Nested `TypeID.RIOType` declares byte constants for all supported IDL types, including map, struct, and vector.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` to model nested map, vector, and record/struct shapes.
- `RecordTypeInfo` extends `Record` to serialize and deserialize runtime record type metadata. It stores a record name, supports adding fields, returns field metadata, finds nested struct type info by name, and deliberately throws/does not implement meaningful `compareTo` because it is not intended as a key.
- `record.meta.Utils.skip(RecordInput, String tag, TypeID typeID)` skips serialized values based on type metadata.

### Security APIs

- `UserGroupInformation` is an abstract `Writable` for user/group identity. It includes thread-local current UGI accessors (`getCurrentUGI`, `setCurrentUGI`), abstract `getUserName`, `getGroupNames`, and `login`, plus `readFrom(Configuration)`. It has a Commons Logging `LOG`.
- `UnixUserGroupInformation` extends `UserGroupInformation` with Unix-backed user and group arrays. It supports mutable constructors, `createImmutable`, serialization/deserialization, saving to configuration under `UGI_PROPERTY_NAME`, reading from configuration, several `login` overloads including current Unix user/group lookup, and equality/hash/toString.

### Tool And Utility APIs

- `DistCp` implements `Tool`, with configuration accessors, `copy(srcPaths, dstPath, srcAsList, ignoreReadFailures)`, `run(args)`, `main(args)`, and static `getRandomId()`. Nested `DuplicationException` extends `IOException` and exposes an `ERROR_CODE`.
- `HadoopArchives` implements `Tool` for creating Hadoop archives, with `archive(srcPaths, archiveName, dest)`, `run(args)`, and `main(args)`.
- `Logalyzer` archives and analyzes Hadoop logs. `doArchive(logListURI, archiveDirectory)` archives listed logs, and `doAnalyze(inputFilesDirectory, outputDirectory, grepPattern, sortColumns, columnSeparator)` runs grep/sort-style MapReduce analysis. Nested `LogComparator` is a configurable raw `Text.Comparator`, and `LogRegexMapper` is a MapReduce mapper that emits regular-expression matches as `Text` and `LongWritable`.
- `Daemon` is a daemon `Thread` wrapper with constructors for no runnable, runnable, and thread group plus runnable, and exposes the backing runnable.
- `DiskChecker` provides `mkdirsWithExistsCheck(File)` for race-tolerant directory creation and `checkDir(File)` for disk/directory validation. Nested `DiskErrorException` and `DiskOutOfSpaceException` are `IOException` subclasses.
- `GenericOptionsParser` parses Hadoop generic command-line options into a `Configuration` and optional Commons CLI `CommandLine`; it exposes `getRemainingArgs`, `getCommandLine`, and `printGenericCommandUsage`. Its documented options include `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`.
- The chunk ends at `GenericsUtil.getClass(T)`, after showing `GenericsUtil` as a utility holder with a public constructor. The following lines outside this chunk likely continue `GenericsUtil` methods.

## Control Flow And Data Flow

- Metrics flow is producer driven: callers mutate metrics (`set`, `inc`, `dec`), metrics helpers remember whether/what changed, and `pushMetric(MetricsRecord)` emits values during context update intervals. `NullContext` suppresses the emission branch, while `NullContextWithUpdateThread` preserves sampling cadence without a sink.
- Record I/O flow is generated-record driven: a generated `Record` calls `RecordOutput.startRecord`, writes primitive/composite fields using tag names, and closes record/vector/map scopes. Deserialization mirrors that flow with `RecordInput.startRecord`, primitive reads, and `Index` loops for vectors/maps.
- Binary, CSV, and XML input/output classes share the same interface but differ in wire representation. Tagged names matter for XML and are ignored or positional in less tagged formats.
- Record compiler flow starts with `Rcc.driver` or `RccTask.execute`, parses `.jr` definitions through JavaCC parser methods into `JFile`, `JRecord`, `JField`, and `JType` models, then `JFile.genCode` emits code for the requested language and destination directory.
- Network topology flow maps hostnames/IPs to rack paths through `DNSToSwitchMapping`, represents the cluster as `Node`/`NodeBase` leaves in `NetworkTopology`, and uses distance or rack checks for placement decisions.
- Socket stream flow wraps a socket channel, waits for readiness with timeout, and delegates actual byte transfer through NIO channel operations. `NetUtils.getInputStream` / `getOutputStream` choose these wrappers when a channel exists.
- Security flow centers on obtaining or deserializing a `UserGroupInformation`, storing it in thread-local current identity, optionally persisting it as configuration text, and serializing it through Hadoop `Writable`.
- Tool flow follows the `Tool` pattern: construct with `Configuration`, parse `run(String[] args)`, execute filesystem/MapReduce work, and return an integer status to `main`.

## State And Persistence Behavior

- Metrics value classes hold in-memory counters, previous interval values, dirty/update flags, and min/max rate state. Public methods are synchronized for scalar and time-varying metrics, signaling thread sharing between metric producers and updater threads.
- `OutputRecord` is a read-only view of tags and metrics being emitted from a metrics context.
- `NetworkTopology` maintains an in-memory tree of racks and leaves, parent pointers, levels, and counts. `NetUtils` also maintains static host resolution overrides visible through add/get/list methods.
- `NodeBase` persists path identity in `name`, `location`, `level`, and `parent`; normalization protects topology path consistency.
- `Buffer` owns mutable backing byte storage and count/capacity metadata. `set` adopts caller-provided arrays, while `copy` replaces contents by copying, which is an important aliasing distinction.
- Record serialization persists generated records to `DataOutput`, CSV, XML, or other `RecordOutput` implementations. `RecordTypeInfo` persists schema/type metadata as a `Record`.
- JavaCC parser classes hold mutable parser state (`token_source`, `token`, `jj_nt`), lexer state, character buffer, line/column arrays, and token chains.
- `UnixUserGroupInformation` persists user/group state via `Writable` methods and configuration property `UGI_PROPERTY_NAME`.
- `DistCp`, `HadoopArchives`, and `Logalyzer` persist external data by creating destination copies, archives, archive indexes, and analysis output directories, but the XML slice only documents method contracts, not output layout details.

## Dependencies And Integration Points

- Metrics APIs depend on `org.apache.hadoop.metrics.MetricsRecord`, SPI classes such as `AbstractMetricsContext` and `MetricsRecordImpl`, JMX (`javax.management.ObjectName`), and JDK networking collections.
- Networking depends on JNDI (`NamingException`) for DNS, `java.net`, NIO channels, Hadoop `Configuration` / `Configurable`, Commons Logging, and topology consumers elsewhere in HDFS/MapReduce.
- Record I/O depends on Hadoop `WritableComparable`, `WritableComparator`, Java collections, streams, and generated record classes.
- Record compiler APIs integrate with Ant, JavaCC-generated parser/lexer code, compiler model objects, and generated Java/C++ record code.
- Security integrates with Hadoop `Configuration`, `Writable`, Java login exceptions, Unix user/group discovery, and thread-local execution context.
- Tool classes integrate with Hadoop `Tool`, filesystem `Path`, MapReduce old API classes (`Mapper`, `MapReduceBase`, `OutputCollector`, `Reporter`, `JobConf`), `Text`, `LongWritable`, and `Text.Comparator`.
- `GenericOptionsParser` integrates Hadoop command launchers with Commons CLI and configuration mutation.

## Risks And Edge Cases

- This is API XML only; implementation details such as validation logic, internal data structures, exact exception paths, and synchronization granularity beyond method modifiers must be confirmed in Java sources.
- `NullContext` intentionally drops metrics. Misconfiguration can therefore silently suppress operational visibility.
- Metrics helpers publish only on update intervals and often only once after a change; callers expecting cumulative every-interval values can misread point-in-time versus time-varying semantics.
- `Buffer.set(byte[])` aliases caller-provided storage; mutation outside the buffer can affect serialized or compared values. `copy` is safer when ownership is unclear.
- Record I/O compatibility depends on exact field order, tags for XML, and variable-length numeric encoding. Comparator and `compareBytes` behavior are test-critical for sorted MapReduce keys.
- `RecordTypeInfo.compareTo` is not meaningful by design, so use as a `WritableComparable` key is risky despite inheritance from `Record`.
- DNS and script-based rack mapping can fail or return unresolved/default racks, affecting placement/rack-awareness logic.
- Static host resolution overrides in `NetUtils` can affect all callers in-process.
- Socket timeout stream behavior is likely sensitive to channel presence, zero timeout semantics, readiness polling, and partial transfer handling.
- `SocksSocketFactory` equality/hash and configuration behavior can affect connection pooling or factory caching. `StandardSocketFactory` has misleading Javadoc copied from SOCKS factory.
- `UnixUserGroupInformation` stores identities in configuration as comma-separated text; malformed, missing, or stale configuration can change effective user/group behavior.
- `GenericOptionsParser` mutates `Configuration` from command-line options, so downstream tools may observe filesystem, jobtracker, file, libjar, and archive changes.
- Parser classes are generated and stateful; reuse requires correct `ReInit`, and lexical/parser error messages expose token/image arrays.

## Test Signals

- Metrics tests should verify dirty/one-shot push behavior, previous interval snapshots, min/max reset, synchronized increments/decrements, JMX object name registration/unregistration, and no-op context suppression.
- Networking tests should cover DNS lookup fallbacks, static host resolution, socket address parsing, old/new server address transition, proxy/default socket factories, timeout read/write behavior, `transferToFully`, topology add/remove/distance/same-rack/random selection, and script mapping default-rack behavior.
- Record I/O tests should round-trip generated records through binary, CSV, and XML serializers; verify `Index` loop boundaries; compare raw bytes through `RecordComparator`; validate `Buffer` capacity/aliasing/comparison/string conversion; and test zero-compressed integer read/write compatibility.
- Record compiler tests should parse modules, includes, primitive fields, maps, vectors, nested records, syntax errors, Ant task file/file-set inputs, fail-on-error behavior, destination directory output, and Java/C++ language option handling.
- Metadata tests should serialize/deserialize `RecordTypeInfo`, compare `TypeID` / map / vector / struct equality and hash codes, and verify `meta.Utils.skip` over every supported type.
- Security tests should cover UGI serialization, configuration save/read, login overloads, thread-local current UGI behavior, immutable UGI behavior, and equality/hash/toString consistency.
- Tool tests should exercise `DistCp` duplicate source detection and random id generation, Hadoop archive command parsing and archive creation, Logalyzer archive/analyze argument handling, regex mapper output, and log comparator sorting.
- Utility tests should validate `Daemon` daemon-thread flag/runnable retention, `DiskChecker` race-tolerant mkdirs and failure cases, generic option parsing for all documented options, remaining args extraction, and generic usage printing.

## Unresolved Cross-Chunk References

- The preceding chunk contains the start of `MetricValue` and the end of `MetricsRecordImpl`, including the full buffered metrics mutation contract feeding into this chunk.
- The `DNSToSwitchMapping`, `Node`, `Index`, `RecordInput`, `RecordOutput`, and `RccConstants` interface starts are visible in this chunk even though the high-level class-boundary inventory comments in the XML omit some interface start/end markers in the package map.
- The following chunk continues `GenericsUtil` after `getClass(T)` and likely includes `toArray(...)` methods shown just beyond the requested line boundary.
