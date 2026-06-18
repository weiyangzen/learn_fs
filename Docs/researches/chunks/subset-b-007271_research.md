# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 37298-43567

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.1, not executable Java source. It begins inside the tail of `org.apache.hadoop.metrics.util.MetricsLongValue`, covers time-varying metrics, the full `org.apache.hadoop.net` package visible in this API file, the Hadoop Record I/O runtime, Record I/O compiler and generated JavaCC parser support, Record I/O metadata classes, early security user/group identity APIs, distributed tools, and utility classes through the beginning of `org.apache.hadoop.util.PriorityQueue.clear`. The final `PriorityQueue` method and class documentation continue past the requested line range, so the boundary class is partial.

The XML records public/protected compatibility surface: packages, classes/interfaces, inheritance, implemented interfaces, fields, constructors, methods, parameter and exception types, visibility, `static`/`final`/`abstract`/`synchronized` flags, deprecation markers, and Javadoc. The research below describes contracts implied by those signatures and docs; it does not infer hidden method-body details except where the Javadoc names behavior.

## Purpose and major API surface

The metrics tail covers mutable metrics primitives. `MetricsLongValue` exposes a synchronized `pushMetric(MetricsRecord)` that publishes only if changed since the last push. `MetricsTimeVaryingInt` tracks interval deltas with synchronized `inc()`, `inc(int)`, `pushMetric(MetricsRecord)`, and `getPreviousIntervalValue()`. `MetricsTimeVaryingRate` tracks operation counts and elapsed time with `inc(long)`, `inc(int,long)`, interval push, previous interval operation count, previous interval average time, min/max single-operation time, and `resetMinMax()`.

`org.apache.hadoop.net` provides host, rack, socket, and topology support. `DNS` offers static forward/reverse helpers for a named interface and optional nameserver: `reverseDns`, `getIPs`, `getDefaultIP`, `getHosts`, and `getDefaultHost`. `DNSToSwitchMapping` defines pluggable rack resolution from a list of host/IP names to network paths. `ScriptBasedMapping` implements that interface and `Configurable`, using a configured external script to resolve names.

`NetUtils` centralizes network setup. It chooses socket factories from `Configuration`, builds `InetSocketAddress` objects from `host[:port]` or URI-like strings, merges legacy split bind-address/port settings into a new address setting, maintains static hostname resolutions, normalizes wildcard server addresses into client-connect addresses, and wraps sockets with timeout-aware input/output streams. `SocketInputStream` and `SocketOutputStream` adapt Java NIO channels and sockets into `InputStream`/`OutputStream` plus `ReadableByteChannel`/`WritableByteChannel`, adding `waitForReadable`, `waitForWritable`, and `transferToFully` support. `SocksSocketFactory` and `StandardSocketFactory` implement `SocketFactory` overloads; the SOCKS variant is configurable and proxy-aware.

`NetworkTopology`, `Node`, and `NodeBase` define rack-aware cluster topology. `Node` exposes network location, name, parent, and tree level. `NodeBase` implements those attributes and provides path constants and `normalize`. `NetworkTopology` stores a hierarchical tree of leaves and racks, with constants such as `DEFAULT_RACK`, `UNRESOLVED`, and `DEFAULT_HOST_LEVEL`; it can add/remove leaves, test containment, look up nodes by path, report rack and leaf counts, compute node distance, test same-rack locality, choose random nodes under a scope excluding a scope, count available leaves, stringify the tree, and pseudo-sort replicas by distance from a reader.

`org.apache.hadoop.record` is the legacy Hadoop Record I/O runtime. `RecordInput` and `RecordOutput` define the serialization contract for primitive values, strings, buffers, records, vectors, and maps with string tags. Binary, CSV, and XML concrete input/output classes implement these interfaces. `BinaryRecordInput` and `BinaryRecordOutput` also expose thread-local `get(DataInput/DataOutput)` helpers. `Index` is the iterator-style cursor for reading maps and vectors. `Record` is the abstract generated-record base and implements `WritableComparable` plus `Cloneable`, with tagged and tagless `serialize`/`deserialize`, `write`, `readFields`, `compareTo`, and `toString`. `RecordComparator` extends `WritableComparator` and registers optimized raw comparators for generated records.

`Buffer` is the Record I/O native Java representation of a byte sequence. It tracks a backing byte array, count, and capacity; exposes constructors from empty, array, and array slice; distinguishes `set(byte[])` aliasing from `copy(byte[], offset, length)` copying; supports capacity changes, reset, truncate, append, comparison, equality, hash code, clone, and string conversion with default or explicit charset.

`org.apache.hadoop.record.Utils` provides low-level binary compatibility helpers: parse floats/doubles from byte arrays, read/write zero-compressed variable-length ints and longs from byte arrays or streams, compute encoded integer size, compare byte arrays lexicographically, and expose hex characters. The XML/XML and CSV/Binary serializer classes rely on these stable primitive encodings.

`org.apache.hadoop.record.compiler` contains the public Record I/O compiler model. `JType` is the base for supported IDL types, with scalar specializations `JBoolean`, `JByte`, `JDouble`, `JFloat`, `JInt`, and `JLong`, plus composite/special types such as `JBuffer`, `JString`, `JVector`, `JMap`, and `JRecord`. `JField<T extends JType>` wraps a field name and type. `JFile` models a parsed Record DDL file and generates code in a requested language. `CodeBuffer` handles indentation, and `Consts` exposes compiler string constants such as record input/output and runtime type information names.

`org.apache.hadoop.record.compiler.ant.RccTask` integrates the Record I/O compiler with Ant. It accepts language, input file, destination directory, `failonerror`, and file sets, then invokes the compiler on each record definition file.

`org.apache.hadoop.record.compiler.generated` is JavaCC-generated parser/lexer support for the Record I/O compiler. `Rcc` parses includes, modules, record lists, records, fields, primitive/composite types, maps, and vectors from `InputStream`, `Reader`, or token-manager sources; it also exposes `main`, `usage`, `driver`, `ReInit`, token access, parse-exception generation, and tracing toggles. `RccConstants` defines token IDs and lexical states. `RccTokenManager`, `SimpleCharStream`, `Token`, `ParseException`, and `TokenMgrError` expose lexer/parser state, token images, line/column tracking, token chains, parse diagnostics, and lexical error formatting.

`org.apache.hadoop.record.meta` represents runtime type metadata for Record I/O. `TypeID` exposes singleton base type IDs and a `typeVal` byte using `TypeID.RIOType` constants. `MapTypeID`, `VectorTypeID`, and `StructTypeID` describe composite types. `FieldTypeInfo` binds field names to type IDs. `RecordTypeInfo extends Record` so type information can itself be serialized/deserialized, named, augmented with fields, queried for nested struct type info, and compared in a compatibility-oriented way. `meta.Utils.skip` can consume serialized values from a `RecordInput` according to a `TypeID`.

`org.apache.hadoop.security` exposes the early user/group identity API. `UserGroupInformation` is a `Writable` abstract class for user and group data with per-thread current UGI access (`getCurrentUGI`, `setCurrentUGI`), username/groups access, `login(Configuration)`, and `readFrom(Configuration)`. `UnixUserGroupInformation` implements it for Unix systems, adds constructors for username/group arrays, immutable creation, serialization/deserialization, config persistence through `saveToConf` and `readFromConf`, Unix/config login variants, equality, hash code, and string conversion. `UGI_PROPERTY_NAME` is a public config key.

`org.apache.hadoop.tools` contains command-line/distributed utilities. `DistCp implements Tool` and recursively copies directories between filesystems, exposing `copy(Configuration, srcPath, destPath, logPath, srcAsList, ignoreReadFailures)`, `run`, `main`, and random job ID generation; its nested `DuplicationException` carries an `ERROR_CODE`. `HadoopArchives implements Tool` creates Hadoop archives from source paths into a destination. `Logalyzer` archives and analyzes Hadoop logs, while `LogComparator` is a configurable raw UTF8 comparator and `LogRegexMapper` is a MapReduce mapper that extracts text matching a configured regular expression.

`org.apache.hadoop.util` begins with process and filesystem helpers. `Daemon extends Thread` and always constructs daemon threads around optional `Runnable` and `ThreadGroup` inputs. `DiskChecker` creates directories with stricter exists semantics and validates directories, throwing `DiskErrorException` or `DiskOutOfSpaceException`. `GenericOptionsParser` uses Commons CLI to parse Hadoop generic command-line options (`-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, `-archives`) into a `Configuration`, remaining application args, and a `CommandLine`. `GenericsUtil` converts generic lists to arrays and extracts runtime classes.

The utility sorting and platform classes expose reusable building blocks. `IndexedSortable` supplies index-based `compare` and `swap`; `IndexedSorter` sorts an index range, optionally reporting progress; `HeapSort` implements that interface. `MergeSort` sorts integer index arrays using an `IntWritable` comparator. `HostsFileReader` reads include/exclude host files and can refresh. `NativeCodeLoader` reports whether native Hadoop code is loaded and stores per-job native-library loading preference in `JobConf`. `PlatformName` reports the JVM platform string. `PrintJarMainClass` prints a jar manifest main class. `PriorityQueue` is an abstract heap whose subclasses define `lessThan`, then call `initialize(maxSize)` and use `put`, `insert`, `top`, `pop`, `adjustTop`, `size`, and the partially visible `clear`.

## Control flow and behavioral contracts

Metrics flow is interval-based. Callers mutate counters/rates with synchronized `inc` or set-like operations, then the metrics system calls `pushMetric(MetricsRecord)`. Time-varying values publish deltas since the last push and retain previous-interval values for JMX-style reads. Rate metrics derive average time from operation count and total time, while min/max are independent state that can be reset.

Network identity flow starts with local interface discovery through `DNS`, optional reverse lookup through a nameserver, and batch host-to-rack resolution through `DNSToSwitchMapping`. `ScriptBasedMapping` adds configuration before resolution, so caller behavior depends on both the host list and the configured script. `NetworkTopology` expects leaves to be represented as `Node`s with normalized paths; add/remove update tree membership, distance calculations walk tree relationships, and `pseudoSortByDistance` reorders an array so local and near-rack nodes are favored for data locality.

Socket setup flow goes through `NetUtils`. Hadoop components resolve a configured socket factory for a protocol class or fall back to default JVM sockets, parse textual endpoints into `InetSocketAddress`, then request timeout-capable streams over sockets. The stream wrappers expose blocking stream APIs while using channel readiness waits for read/write timeouts; callers must close streams/channels to release socket resources.

Record I/O flow is generated-code driven. A `.jr`-style record definition is parsed by `Rcc`, represented as `JFile`, `JRecord`, `JField`, and `JType` objects, then emitted in a target language. At runtime, generated `Record` subclasses serialize each field sequentially through a chosen `RecordOutput` and deserialize sequentially through `RecordInput`. Collection deserialization uses an `Index`: call `startVector` or `startMap`, loop until `done()`, consume each element, call `incr()`, then close the vector/map with `endVector` or `endMap`.

Record metadata flow mirrors data flow. `RecordTypeInfo` can serialize a record schema, deserialize it back, and find direct nested struct metadata. `meta.Utils.skip` uses a supplied `TypeID` to advance over serialized data without materializing it, which is important for schema-evolution or filtered-read paths.

Security flow is config and thread scoped. `UnixUserGroupInformation.login()` can discover the current Unix user/groups, while `login(conf, save)` can read configured identity and optionally persist it. `UserGroupInformation.getCurrentUGI()` returns the per-thread identity, and `setCurrentUGI()` changes that thread-local context for downstream filesystem/RPC actions.

Tool flow follows the Hadoop `Tool` pattern. Tools are constructed or configured with `Configuration`, parse command-line arguments in `run(String[])`, then submit or run MapReduce/filesystem workflows. `DistCp.copy` is the programmatic entry point for recursive copy, `HadoopArchives.archive` is the archive creation entry point, and `Logalyzer` splits work into archive and analyze phases.

Utility control flow is mostly lifecycle-oriented. `GenericOptionsParser` mutates or augments the supplied `Configuration` before application-specific parsing. `HostsFileReader.refresh()` rereads include/exclude files. `DiskChecker.checkDir()` validates directory existence/writability and usable space. `PriorityQueue` requires subclass ordering plus initialization before use; `put` and `pop` maintain heap order, while `insert` keeps only acceptable elements when the queue is full.

## State, persistence, and side effects

The JDiff XML itself is persistent API compatibility metadata. Runtime state described by this chunk includes metrics current and previous interval values, min/max timing history, DNS results, static hostname resolutions, configured socket factories, socket/channel readiness state, network topology tree nodes, Record I/O byte buffers, serialized records, parser token streams, type metadata records, user/group identities, tool job configuration, host include/exclude sets, native-library flags, and heap contents.

Metrics classes are mutable and synchronized, but their values are intentionally interval scoped. `pushMetric` changes publication state by resetting or rolling current values into previous-interval state. Rate min/max state persists until `resetMinMax()` rather than automatically resetting every interval.

Network topology state is in-memory but influences persistent distributed behavior such as HDFS replica placement and block read ordering. `NodeBase` has public/protected-style state fields (`name`, `location`, `level`, `parent`) and path constants, so serialized logs, tests, and subclass behavior can depend on path normalization and root/rack naming. `NetUtils` static resolutions are process-global overrides for host lookup.

Record I/O persists data in binary, CSV, or XML encodings. Binary compatibility depends on field ordering, tag handling, collection size markers, buffer byte contents, and zero-compressed variable-length integer encoding. `Buffer.set(byte[])` adopts caller storage while `copy(...)` duplicates it, so aliasing can leak later caller mutations into serialized values if used carelessly.

The compiler-generated parser has explicit mutable state: token source, current token, next token, character buffers, line/column arrays, lexical states, debug streams, and parse exception fields. Reuse through `ReInit` changes this state in place. Public parser/token fields make compatibility sensitive to JavaCC output shape.

Security APIs persist user/group identity through Hadoop `Configuration` strings and Hadoop `Writable` streams. Per-thread current UGI is mutable process state. Unix login depends on host OS user/group lookup and may throw `LoginException`.

Tools have filesystem and MapReduce side effects. `DistCp` copies data between filesystems and writes logs; duplicate source paths can raise `DuplicationException`. `HadoopArchives` creates archive files under a destination path. `Logalyzer` reads and writes log archives and analysis output through filesystem and MapReduce APIs.

Utility side effects include directory creation/checking, native library loading or disabled-use flags in `JobConf`, host-file rereads, daemon thread creation, command-line configuration mutation, and jar manifest inspection.

## Dependencies and integration points

Metrics APIs integrate with `org.apache.hadoop.metrics.MetricsRecord` and the older Hadoop metrics/JMX update flow.

Network APIs depend on Java networking and naming (`InetAddress`, `InetSocketAddress`, `Socket`, `SocketFactory`, `Proxy`, DNS/JNDI naming exceptions), Java NIO channels, Hadoop `Configuration`, commons logging, and cluster components that consume rack topology. `NetUtils` also bridges old and new config keys during server-address migration.

Record I/O runtime depends on Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, collections (`ArrayList`, `TreeMap`), `WritableComparable`, `WritableComparator`, `Text.Comparator`, and `IOException`. Its generated-code model and compiler depend on the Record IDL grammar, JavaCC parser artifacts, Ant tasks, and code generation target language selection.

Record metadata integrates with the Record runtime by extending `Record` and using `RecordInput`/`RecordOutput`. `TypeID` constants bridge runtime values, metadata skipping, and compiler-generated type declarations.

Security APIs depend on Hadoop `Configuration`, Hadoop `Writable`, Java security login exceptions, Unix user/group lookup, and per-thread caller context used by filesystem and RPC code.

Tools integrate with `Tool`, `Configuration`, Hadoop filesystems (`Path`), old MapReduce APIs (`JobConf`, `Mapper`, `MapReduceBase`, `OutputCollector`, `Reporter`), Hadoop writables (`Text`, `LongWritable`, `WritableComparable`), and command-line `main` entry points.

Utility classes integrate with Commons CLI, Java files, Java threads, Java comparators, Hadoop `Progressable`, `JobConf`, and native Hadoop library loading.

## Risks and compatibility notes

This is a line-bounded chunk with partial boundary classes. `MetricsLongValue` starts before the range and `PriorityQueue.clear` completes after the range, so final per-file reconciliation should merge adjacent chunks before making whole-file conclusions.

The XML is a public API contract for an old Hadoop release. Even misspelled Javadocs and unusual signatures are compatibility-relevant because downstream consumers may compare JDiff output exactly or depend on generated API shapes.

Metrics classes are synchronized and interval-sensitive. Changing reset timing, previous-interval visibility, min/max reset semantics, or whether unchanged values are published would alter metrics dashboards and JMX consumers.

Rack topology APIs affect placement and scheduling. Bad path normalization, wrong distance calculations, incorrect same-rack checks, or inconsistent random selection under include/exclude scopes can cause poor data locality or placement imbalance. Static DNS resolutions and script-based mappings are process/configuration sensitive and can hide real DNS changes.

Socket wrappers are resource and timeout sensitive. NIO channel readiness, socket close semantics, transfer loops, and factory equality/hash behavior can affect RPC connection reuse and failure modes. `NetUtils.createSocketAddr` must preserve support for legacy endpoint string formats.

Record I/O is a legacy serialization surface, so wire compatibility is the main risk. Variable-length integer encoding, binary float/double parsing, CSV/XML escaping, buffer aliasing, record field order, collection traversal, and raw comparator behavior must remain stable for existing data and generated classes.

The Record compiler exposes generated JavaCC internals as public API. Token IDs, lexical state names, parser method names, public fields, exception message formatting, and stream line/column accounting can be consumed by tests or downstream tools even though they look implementation-specific.

Security identity APIs predate later Hadoop UGI designs and rely on mutable thread-local state plus configuration persistence. Incorrect save/read formatting, immutable UGI handling, group order, equality/hash code, or thread scoping can create authorization bugs.

Tools are high-blast-radius utilities. DistCp and HadoopArchives operate on distributed data and can overwrite, duplicate, omit, or incorrectly archive large path sets if argument parsing, path listing, duplicate detection, logging, or failure handling changes.

Utility algorithms have hidden assumptions. `PriorityQueue` has fixed maximum size and throws if `put` exceeds capacity; `insert` drops elements based on `lessThan(element, top())`. Sorters assume `IndexedSortable.compare` is consistent and `swap` is correct. `GenericsUtil.toArray(List)` documents failure on empty lists, so callers may depend on that exception.

## Test signals

JDiff validation should check this XML range remains well-formed when combined with neighbors and preserves package/class/interface boundaries, inheritance, implemented interfaces, field names and types, method overloads, declared exceptions, synchronized/static/final flags, visibility, deprecation markers, and embedded Javadocs.

Metrics tests should cover unchanged-value push suppression for `MetricsLongValue`, interval delta rollover for `MetricsTimeVaryingInt`, operation count and average-time reporting for `MetricsTimeVaryingRate`, min/max timing updates, `resetMinMax`, and synchronized concurrent increments.

Network tests should cover DNS interface lookup fallback, reverse DNS failure propagation, rack mapping one-to-one list behavior, script mapping configuration and missing-script behavior, socket factory lookup from class-specific and default config keys, static hostname resolution add/get/list, wildcard server-address conversion, socket stream timeout waits, channel close behavior, SOCKS proxy configuration, socket factory equality/hash code, topology add/remove/contains, rack and leaf counts, distance, same-rack checks, random choice with exclusions, available-node counting, and pseudo-sort ordering.

Record I/O runtime tests should cover binary/CSV/XML round trips for every primitive plus string, buffer, record, vector, and map; tagged and tagless generated-record serialization; `Index.done/incr` collection traversal; `Buffer` set/copy alias behavior, append, reset, truncate, capacity growth, comparison, equality, clone, and charset conversion; zero-compressed int/long edge cases; byte-array lexicographic compare; raw `RecordComparator` registration; and legacy encoded-data compatibility.

Record compiler tests should cover parsing modules, includes, records, fields, primitive types, maps, vectors, comments, and syntax errors; `Rcc.driver` return codes; `ReInit` reuse; parse exception message content; token line/column positions; token-manager lexical states; Ant `RccTask` file and fileset handling; destination directory output; and `failonerror` behavior.

Record metadata tests should cover base `TypeID` singleton equality/hash code, map/vector/struct equality, `FieldTypeInfo` equality, `RecordTypeInfo` add/get/nested lookup behavior, metadata serialize/deserialize round trips, `compareTo` behavior, and `meta.Utils.skip` for each primitive and composite type.

Security tests should cover Unix login success/failure paths, config save/read of UGI strings, immutable UGI creation, `Writable` serialization round trips, username/group accessors, equality/hash code, string conversion, `getCurrentUGI` and `setCurrentUGI` thread isolation, and `UserGroupInformation.readFrom(Configuration)`.

Tool tests should cover `DistCp.copy` with single sources, source lists, duplicate sources, missing/unreadable files, log path use, ignore-read-failure behavior, `run` exit codes, random ID format, archive creation with multiple paths, Logalyzer archive/analyze flows, regex mapper matches and nonmatches, and log comparator raw-byte ordering.

Utility tests should cover daemon constructors setting daemon status and preserving runnable, directory creation and disk-error exceptions, generic option parsing effects on `Configuration` and remaining args, generic usage printing, generic array conversion including empty-list failure for the one-argument overload, heap sort with and without `Progressable`, host include/exclude refresh, merge sort index behavior, native library loaded/unloaded reporting and JobConf flag persistence, platform name output, jar main-class detection, and `PriorityQueue` heap operations including full-queue insert/drop behavior and `adjustTop`.
