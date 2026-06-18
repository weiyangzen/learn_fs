# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 37235-43512

## Scope

This chunk covers a JDiff API XML slice from Hadoop 0.19.1. It is not executable Hadoop source; it is a generated public API inventory used by JDiff/dev-support tooling to compare class, method, field, signature, visibility, inheritance, exception, and Javadoc metadata across Hadoop releases.

The range starts in the tail of `org.apache.hadoop.net.SocketInputStream` documentation, then covers `org.apache.hadoop.net.SocketOutputStream`, socket factory classes, the complete `org.apache.hadoop.record` API surface visible in this range, record compiler and generated parser classes, record metadata classes, security UGI types, tool entry points, and much of `org.apache.hadoop.util` through the first overload of `StringUtils.byteToHexString`. The chunk ends inside `StringUtils`; later string utility methods are outside this chunk and must be reconciled by the merge lane.

## Purpose

The purpose of this XML region is to preserve Hadoop Common's public Java API as structured data for compatibility checks. Each `<package>`, `<class>`, `<interface>`, `<constructor>`, `<method>`, and `<field>` element records the contract that downstream code may compile against. The embedded CDATA documentation captures intended semantics, such as timeout behavior for socket streams, serialization formats for records, Hadoop generic command-line options, UGI persistence, and utility behavior.

Because this file is a JDiff baseline, the operational impact is indirect. Build or release tooling compares a newer API dump against this baseline to detect additions, removals, signature changes, visibility changes, checked exception changes, inheritance changes, and documentation differences.

## Important APIs and Types

### Network classes

The chunk starts with `org.apache.hadoop.net.SocketOutputStream`, a public `OutputStream` that also implements `WritableByteChannel`. It can be constructed from a `WritableByteChannel` or `Socket` plus a non-negative timeout. The documented behavior configures the socket channel as non-blocking; after this, the socket's ordinary Java blocking streams may throw `IllegalBlockingModeException`, so callers are expected to pair it with Hadoop's timeout-aware socket input stream. Important methods are `write(int)`, `write(byte[], int, int)`, channel-style `write(ByteBuffer)`, synchronized `close()`, `isOpen()`, `getChannel()`, `waitForWritable()`, and `transferToFully(FileChannel, long, int)`.

`SocksSocketFactory` and `StandardSocketFactory` both extend `javax.net.SocketFactory`. `SocksSocketFactory` also exposes `getConf()` and `setConf(Configuration)`, indicating Hadoop configuration integration for proxy behavior. Both factories expose the usual socket creation overloads for plain sockets and host/address plus port/local binding combinations, and both implement `equals()`/`hashCode()` for factory identity.

### Record I/O framework

The `org.apache.hadoop.record` package defines Hadoop's older record-serialization stack:

- `BinaryRecordInput` and `BinaryRecordOutput` wrap `InputStream`/`DataInput` and `OutputStream`/`DataOutput` and implement primitive, string, buffer, record, vector, and map read/write operations.
- `CsvRecordInput`/`CsvRecordOutput` and `XmlRecordInput`/`XmlRecordOutput` expose the same record input/output shape for tagged text formats.
- `RecordInput` and `RecordOutput` are the common serializer/deserializer interfaces, with methods for byte, boolean, int, long, float, double, string, `Buffer`, record boundaries, vector boundaries, and map boundaries. The tag parameter is meaningful for tagged formats such as XML.
- `Index` is the iteration cursor returned by `startVector()` and `startMap()`, with `done()` and `incr()` used to walk collection elements.
- `Buffer` is a mutable byte-sequence value type with constructors for empty, full-array, and array-slice content. It exposes `set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, append overloads, `hashCode`, `compareTo`, `equals`, `toString` overloads, and `clone`.
- `Record` is an abstract base for generated records. It implements `WritableComparable` and `Cloneable`, requires tagged `serialize`, tagged `deserialize`, and `compareTo`, and provides untagged `serialize`, `deserialize`, `write(DataOutput)`, `readFields(DataInput)`, and `toString`.
- `RecordComparator` extends `WritableComparator` and registers optimized raw comparators through synchronized static `define(Class, RecordComparator)`.
- `Utils` provides binary helpers for float/double parsing, zero-compressed variable-length int/long read/write on byte arrays and streams, encoded size calculation, byte comparison, and a public `hexchars` table.

### Record compiler APIs

`org.apache.hadoop.record.compiler` describes the Java-side record compiler model. `CodeBuffer` provides `toString()`. `Consts` exposes string constants such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`. Primitive and compound schema-model classes include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, `JRecord`, `JField<T>`, `JType`, and `JFile`. `JFile.genCode(String, String)` is the generation entry point for a file containing included files and records.

`org.apache.hadoop.record.compiler.ant.RccTask` is an Ant `Task` wrapper with setters for language, file, fail-on-error behavior, destination directory, filesets, and `execute()`.

`org.apache.hadoop.record.compiler.generated` is the JavaCC-generated parser/lexer surface:

- `ParseException` records parser failures, current token, expected token sequences, token images, and newline text, with constructors for generated and custom messages plus `getMessage()` and `add_escapes()`.
- `Rcc` has constructors for input streams, readers, and token managers. It exposes `main`, `usage`, `driver`, grammar productions such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, plus `ReInit` overloads, token access, parse-exception generation, and tracing toggles.
- `RccConstants` defines token ids for module/record/include keywords, primitive types, map/vector syntax, braces, commas, dots, string and identifier tokens, lexical states, and `tokenImage`.
- `RccTokenManager` exposes token-manager construction, debug stream selection, reinitialization, lexical-state switching, token fill/get, and lexer state fields.
- `SimpleCharStream` exposes stream constructors for `Reader` and `InputStream` variants, tab sizing, buffer expansion/fill, token start, line/column update, char reads, begin/end line and column access, backup, reinitialization, image/suffix extraction, finalization through `Done`, and begin-line adjustment. It also exposes parser buffer and position fields.
- `Token` carries token kind, begin/end line and column, image, next-token link, and special-token link, with `toString()` and `newToken(int)`.
- `TokenMgrError` models lexical errors with constructors, escaping helpers, lexical-error text construction, and `getMessage()`.

### Record metadata

`org.apache.hadoop.record.meta` describes runtime type information for records. `FieldTypeInfo` exposes field id and `TypeID` plus equality/hash behavior. `TypeID` stores a byte type value and exposes singleton type ids for bool, buffer, byte, double, float, int, long, and string. `TypeID.RIOType` defines byte constants for primitive, map, struct, vector, and string-like record I/O types. `MapTypeID`, `VectorTypeID`, and `StructTypeID` represent compound type ids. `RecordTypeInfo` extends `Record`, stores a record name and field metadata, supports nested struct lookup, and implements record serialization/deserialization and comparison. `meta.Utils.skip(RecordInput, String, TypeID)` is a helper for skipping a typed value in serialized input.

### Security and identity

`org.apache.hadoop.security.AccessControlException` extends the filesystem permission exception and has a no-argument constructor for unwrapping from `RemoteException` plus a message constructor.

`UnixUserGroupInformation` extends abstract `UserGroupInformation`. It stores user and group names, can be created from user/group arrays, exposes an immutable factory, implements `Writable` read/write in a string-marked UGI format, saves to and reads from `Configuration` as comma-separated user/group properties, logs in from Unix or configuration, and implements equality, user-name hash code, and comma-separated string conversion. `UGI_PROPERTY_NAME` is the public property key. `UserGroupInformation` itself is a `Writable` abstraction with thread-current UGI get/set, abstract user and group accessors, `login(Configuration)`, `readFrom(Configuration)`, and a public commons-logging `LOG`.

### Tools

`org.apache.hadoop.tools.DistCp` implements `Tool` and exposes configuration setters/getters, a static `copy(Configuration, String, String, Path, boolean, boolean)`, `run(String[])`, `main(String[])`, `getRandomId()`, and `LOG`. Its nested `DuplicationException` defines an `ERROR_CODE` for duplicate source files.

`HadoopArchives` implements `Tool` and exposes `archive(List<Path>, String, Path)`, `run`, `main`, and configuration setters/getters for creating HAR archives. `Logalyzer` exposes `doArchive`, `doAnalyze`, and `main` for archiving and analyzing Hadoop logs. Its nested `LogComparator` extends `Text.Comparator` and implements `Configurable`, while `LogRegexMapper` extends `MapReduceBase` and implements a mapper from writable keys and text values to text/count outputs.

### Utility classes

The `org.apache.hadoop.util` part of the chunk includes:

- `CyclicIteration<K,V>`: iterable over a `NavigableMap` starting after a supplied key and wrapping from the last entry to the first.
- `Daemon`: daemon `Thread` wrapper constructors and `getRunnable()`.
- `DataChecksum`: checksum abstraction over CRC32/null checksum types. It can construct from type/bytes-per-checksum, header bytes, or `DataInputStream`, write/read checksum headers and values, compare stored checksums, expose checksum metadata, and implement `Checksum.reset/update/getValue`.
- `DiskChecker`: mkdir-with-race-tolerant-exists-check, directory checking, and `DiskErrorException`/`DiskOutOfSpaceException`.
- `GenericOptionsParser`: Commons CLI parser for Hadoop generic options such as `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`; it exposes remaining arguments, the parsed `CommandLine`, libjar URL parsing, and usage printing.
- `GenericsUtil`: type-safe class extraction and list-to-array helpers, with the no-class overload requiring a non-empty list.
- `HeapSort`, `QuickSort`, `MergeSort`, `IndexedSortable`, and `IndexedSorter`: sort implementations and callback interfaces for index-addressed data. QuickSort documents fallback to HeapSort at max recursion depth and progress-reporting overloads.
- `HostsFileReader`: synchronized include/exclude hosts file name updates and refresh, plus getters for included and excluded hosts sets.
- `LineReader`: buffered line reader over `InputStream`, using explicit buffer size or `io.file.buffer.size`, with bounded `readLine` overloads and close.
- `NativeCodeLoader`: native `libhadoop` load status and configuration toggles for allowing native libraries.
- `PlatformName` and `PrintJarMainClass`: small main-class utilities for platform naming and jar manifest inspection.
- `PriorityQueue<T>`: abstract fixed-size priority queue requiring `lessThan(Object,Object)`, with `initialize`, `put`, conditional `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.
- `ProcfsBasedProcessTree`: Linux `/proc` process-tree tracker with availability, refresh, root aliveness, destroy, cumulative virtual memory, PID-file read, string rendering, and configurable SIGKILL interval.
- `ProgramDriver`: registry/dispatcher for named example or tool main classes.
- `Progress` and `Progressable`: hierarchical progress tree with named phases, synchronized phase advancement/status/progress, completion, and overall progress reporting; `Progressable.progress()` is used to prevent Hadoop timeouts during long operations.
- `ReflectionUtils`: configuration injection, new instance creation, contention tracing, thread-info printing/logging, and generic class extraction.
- `RunJar`: jar unpacking and job-jar execution.
- `ServletUtil`: servlet/JSP helpers for initial HTML output, trimmed parameter retrieval, HTML footer, and percentage graph generation.
- `Shell`, `Shell.ExitCodeException`, and `Shell.ShellCommandExecutor`: Unix command execution base, platform command constants, environment and working-directory configuration, interval-gated execution, command output parsing, static command execution, exit-code exceptions, and a concrete executor storing small command output.
- Start of `StringUtils`: exception stringification, hostname simplification, human-readable integer formatting, percent formatting, comma-joining arrays, and the first byte-array-to-hex overload.

## Control Flow

The XML itself has no executable control flow. Its structural flow is the JDiff hierarchy: package entries contain class/interface entries; classes contain constructors, methods, fields, implemented interfaces, inherited base classes, exceptions, parameters, and documentation. A JDiff consumer walks these elements to compare public API compatibility between releases.

The documented APIs describe several important runtime flows:

- Timeout socket writes configure channels non-blocking, wait for writability with stream timeout, and support complete `FileChannel.transferTo` loops that throw EOF or socket timeout on incomplete transfers.
- Record serialization flows start and end records, vectors, and maps, then read/write primitives and buffers. Collection reading uses `Index.done()` and `Index.incr()`.
- Generated records flow through `Record.write()`/`readFields()` via binary record input/output, while tagged formats pass field tags through the serializer/deserializer interface.
- Record compiler flow parses an Rcc input into `JFile`, included files, modules, record lists, fields, and type models, then `JFile.genCode()` emits target-language output. Ant integration wraps this parser/generator in `RccTask.execute()`.
- UGI flow reads identity from configuration or Unix shell commands, caches one UGI per user, can save back to configuration, and exposes a thread-current identity through static get/set.
- DistCp and HadoopArchives are `Tool` drivers: command-line args are parsed, source paths are listed, map tasks perform copying or archive-file creation, and reducers finish empty-copy or archive-index work.
- Generic option parsing mutates a `Configuration` before application-specific arguments are consumed by the actual command.
- Shell flow gates execution by interval, configures environment/working directory, starts a subprocess, parses output through subclass hooks, and records process/exit code. `ShellCommandExecutor` supplies the simple case where output is accumulated as a small string.
- Process-tree flow refreshes `/proc` state, checks root-process liveness, computes cumulative virtual memory, and can destroy a root process after a configured sleep-before-SIGKILL interval.

## State and Persistence Behavior

Persistent state in this XML file is API metadata: class names, package names, type signatures, inheritance, method parameters, checked exceptions, visibility, static/final/synchronized/native/abstract flags, deprecation status, and documentation. It should be treated as release-baseline data. Editing it changes what JDiff reports as the Hadoop 0.19.1 API.

The APIs represented here also define or expose stateful behavior:

- Socket stream instances hold a channel and timeout and alter the associated channel's blocking mode.
- `Buffer` owns mutable byte storage, count, and capacity; callers must distinguish copy semantics from direct `get()` access.
- Record input/output implementations hold underlying streams and collection cursors; variable-length integer encodings are persistent wire-format details.
- Parser/token-manager classes expose mutable lexer/parser state such as current token, next token, lexical state, buffers, positions, line/column arrays, and debug stream.
- `RecordTypeInfo` persists record names and field type metadata and can serialize/deserialize that metadata as a Hadoop record.
- UGI persists user/group identity in memory, thread-local/current context, writable streams, and configuration properties.
- Tool classes persist configuration through `Tool.setConf()`/`getConf()`, while DistCp/HadoopArchives/Logalyzer persist output into DFS paths and MapReduce output directories.
- `DataChecksum` persists checksum type, bytes-per-checksum, current checksum accumulator, and header layout used by DFS data transfer.
- `HostsFileReader` persists include/exclude file names and current host sets.
- `PriorityQueue`, `Progress`, `Shell`, and `ProcfsBasedProcessTree` all maintain mutable runtime state that is observable through their public methods.

## Dependencies and Integration Points

This API slice integrates many Hadoop Common subsystems:

- Java standard library dependencies include `java.io`, `java.net`, `java.nio`, `java.nio.channels`, collections, `java.util.zip.Checksum`, servlet request/response types, and reflection/thread/process APIs.
- Hadoop core dependencies include `Configuration`, `Path`, `Writable`, `WritableComparable`, `WritableComparator`, `Text`, `Text.Comparator`, MapReduce old API types (`Mapper`, `MapReduceBase`, `OutputCollector`, `Reporter`, `JobConf`), `Tool`, `Progressable`, and filesystem permission exceptions.
- External dependencies include Apache Commons Logging, Apache Commons CLI, Ant `Task`, and JAAS `LoginException`.
- `SocketOutputStream`, `Shell`, `DataChecksum`, `LineReader`, `GenericOptionsParser`, `Progressable`, and `ReflectionUtils` are broad integration utilities used across HDFS, MapReduce, and command-line tools.
- The record compiler generated classes connect `.jr`/record schema parsing to generated `Record` subclasses and the `RecordInput`/`RecordOutput` runtime.
- UGI and access-control classes connect configuration, IPC exception unwrapping, filesystem permission checks, and thread execution identity.
- DistCp, HadoopArchives, Logalyzer, RunJar, ProgramDriver, PlatformName, and PrintJarMainClass are command-line or job-driver entry points exposed to users and scripts.

## Risks

- This is a compatibility baseline. Removing or mis-editing method signatures, checked exceptions, visibility, abstract/final/static flags, or class inheritance can produce false JDiff reports and hide or invent API incompatibilities.
- The chunk begins and ends mid-context: it starts after the `SocketInputStream` class body has already begun and ends inside `StringUtils`. The final per-file report must merge adjacent chunks before making whole-file claims.
- Socket timeout APIs are sensitive to Java channel blocking mode. The documentation explicitly warns that standard socket streams can fail after the channel is made non-blocking.
- Record serialization APIs define stable wire-format behavior. Changes to variable-length integer encoding, buffer copy/direct semantics, collection indexing, or tagged record boundaries risk breaking old serialized data and generated classes.
- Generated parser classes expose many public mutable fields from JavaCC. Although awkward, they are part of the baseline and may be referenced by downstream code.
- UGI persistence as comma-separated strings and one-UGI-per-user caching can create compatibility and security-sensitive behavior. Misdocumenting or changing this API affects configuration, identity propagation, and IPC/security integration.
- Tool and utility APIs are widely used by command-line scripts and jobs. `GenericOptionsParser`, `Shell`, `RunJar`, `ProgramDriver`, and `Progressable` are especially exposed to application code.
- `DataChecksum`, `LineReader`, sorting interfaces, and `ReflectionUtils` are low-level utilities. Their signatures and documented edge cases, such as empty-list behavior in `GenericsUtil.toArray(List<T>)`, can affect many callers.

## Test and Validation Signals

Validation for this chunk should focus on API-baseline and downstream compatibility:

- Run the repository's JDiff or API comparison task against `hadoop_0.19.1.xml` and a generated current API XML to verify this baseline parses cleanly and reports expected deltas.
- XML well-formedness checks should cover package/class nesting across the adjacent chunk boundaries, because this slice starts and ends in partial contexts.
- Compile downstream Hadoop 0.19.x-era code or compatibility tests that use `SocketOutputStream`, record I/O, generated record compiler classes, UGI, DistCp, HadoopArchives, `GenericOptionsParser`, `DataChecksum`, `Shell`, and `ReflectionUtils`.
- Serialization compatibility tests should round-trip records through binary, CSV, and XML record input/output and verify `Buffer`, variable-length int/long, and raw `RecordComparator` behavior.
- Security tests should cover UGI read/write, configuration save/read, login fallback to Unix, current-thread UGI propagation, and access-control exception unwrapping.
- Command-line integration tests should exercise DistCp, HadoopArchives, Logalyzer, RunJar, ProgramDriver, generic option parsing, libjars/files/archives parsing, and shell command execution behavior.
- Utility tests should cover checksum header/value creation and comparison, hosts-file refresh, line reading with maximum length/bytes, indexed sorter progress callbacks, priority queue fixed-size behavior, process-tree PID-file and `/proc` availability handling, servlet percentage graph helpers, and string formatting helpers visible in this chunk.
