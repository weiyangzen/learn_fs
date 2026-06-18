# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 37252-43530

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.2, not Java implementation source. It begins inside the already-open `org.apache.hadoop.net.SocketOutputStream` class, closes the `org.apache.hadoop.net` package, covers all of `org.apache.hadoop.record`, `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, `org.apache.hadoop.record.compiler.generated`, `org.apache.hadoop.record.meta`, `org.apache.hadoop.security`, and `org.apache.hadoop.tools`, then starts `org.apache.hadoop.util` and ends inside `StringUtils.hexStringToByte`. The XML records API compatibility data: package names, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, return types, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The covered surface spans Hadoop's socket factories and timed socket output stream, the legacy Hadoop Record I/O serialization framework and record compiler, record type metadata, user/group identity APIs, distributed-copy/archive/log-analysis command-line tools, and a large utility subset covering checksums, disk checks, generic option parsing, sorting, host-file loading, line reading, process-tree management, progress reporting, reflection, jar launching, servlet helpers, shell command execution, and string formatting/conversion.

## Purpose and Major API Surface

`SocketOutputStream` provides timed writes over a `WritableByteChannel` or a socket's channel. Its constructors configure the channel as non-blocking and treat timeout zero as infinite. It implements `WritableByteChannel`, exposes `write(int)`, `write(byte[], int, int)`, `write(ByteBuffer)`, synchronized `close()`, `isOpen()`, `getChannel()`, `waitForWritable()`, and `transferToFully(FileChannel, long, int)`. The contract explicitly warns that normal socket stream reads/writes on the same socket will fail after the channel is put into non-blocking mode, and callers should use the matching Hadoop socket input stream for reads.

`SocksSocketFactory` and `StandardSocketFactory` are `SocketFactory` implementations. `SocksSocketFactory` is configurable, can be constructed with a `Proxy`, and has all standard `createSocket` overloads plus `getConf`, `setConf`, `equals`, and `hashCode`. `StandardSocketFactory` exposes the same socket-creation overloads and equality/hash operations without `Configurable`.

`org.apache.hadoop.record` is the legacy record serialization API. `RecordInput` and `RecordOutput` define tag-aware primitive, string, buffer, record, vector, and map read/write contracts. `BinaryRecordInput` and `BinaryRecordOutput` implement those contracts over `DataInput`/`DataOutput` or streams and expose thread-local `get(...)` factories. `CsvRecordInput`/`CsvRecordOutput` and `XmlRecordInput`/`XmlRecordOutput` implement the same contract for textual formats. `Index` supplies `done()` and `incr()` for vector/map traversal.

`Buffer` is the record framework's byte-sequence value type. It is mutable, resizable, cloneable, comparable, and tracks count separately from capacity. It can adopt an existing byte array via `set`, copy a byte range via `copy`, expose the backing array via `get`, report `getCount`/`getCapacity`, change capacity, reset, truncate capacity to count, append ranges or whole arrays, compare lexicographically, convert to strings, and clone itself.

`Record` is the generated-record base contract. It supports serialization/deserialization through `RecordOutput`/`RecordInput`, binary wire compatibility through `DataOutput`/`DataInput`, Hadoop `Writable` hooks `write` and `readFields`, comparability, and `toString`. `RecordComparator` extends `WritableComparator`, compares two serialized record byte ranges, and has a static `define(Class, RecordComparator)` registration method.

`org.apache.hadoop.record.Utils` provides low-level serialization helpers: float/double reads from byte arrays, variable-length integer/long reads from byte arrays or `DataInput`, variable-length integer size calculation, variable-length writes to `DataOutput`, byte-array comparison, and the `hexchars` table. These helpers underpin binary record encoding and comparison.

`org.apache.hadoop.record.compiler` models the record compiler's type system. `CodeBuffer` renders accumulated generated source text. `Consts` exposes code-generation symbol constants such as record I/O prefixes, runtime type-info variables/filters, record input/output names, and tag names. Primitive and composite type nodes include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, `JRecord`, `JType`, and `JCompType` subclasses. `JField<T>` names a typed field. `JFile` represents a record compiler input file, its included files, and records, and exposes `genCode(String language, String destDir)` returning an integer status.

`RccTask` is the Ant integration point for the record compiler. It extends `org.apache.tools.ant.Task` and accepts `language`, single `file`, `failonerror`, `destdir`, and nested `FileSet` inputs before `execute()`.

`org.apache.hadoop.record.compiler.generated` contains JavaCC-generated parser and lexer API. `Rcc` parses record compiler input from `InputStream`, `Reader`, or `RccTokenManager`, exposes grammar productions such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, plus `driver`, `usage`, `main`, `ReInit`, token access, parse exception generation, and tracing toggles. `RccConstants` defines token IDs for module/record/include keywords, primitive types, vector/map punctuation, identifiers, string tokens, comment states, and `tokenImage`.

`ParseException`, `TokenMgrError`, `RccTokenManager`, `SimpleCharStream`, and `Token` provide parser error reporting and tokenization state. `ParseException` carries current token, expected token sequences, token images, and message formatting. `RccTokenManager` exposes debug stream control, lexical reinitialization, lexical state switching, token creation, next-token retrieval, and lexer tables/state. `SimpleCharStream` tracks reader/input-stream character buffers, line/column positions, tab size, backup state, suffix/image extraction, reinitialization overloads, and cleanup. `Token` stores token kind, image, source span, next/special-token links, and a static factory.

`org.apache.hadoop.record.meta` supplies runtime type metadata for records. `TypeID` defines primitive singleton IDs and byte-valued RIO type constants, with equality/hash behavior and `getTypeVal()`. `MapTypeID`, `VectorTypeID`, and `StructTypeID` add key/value, element, and field-list metadata. `FieldTypeInfo` pairs field names with type IDs and supports compatibility equality checks. `RecordTypeInfo` extends `Record`, names a record schema, adds fields, retrieves nested struct metadata, serializes/deserializes the schema, and compares records. `meta.Utils.skip` skips values in a `RecordInput` according to a `TypeID`.

`org.apache.hadoop.security` contains legacy user/group identity APIs. `AccessControlException` subclasses the filesystem permission exception. `UnixUserGroupInformation` extends `UserGroupInformation`, is writable through `readFields`/`write`, exposes user/group accessors, immutable creation, configuration save/load through `UGI_PROPERTY_NAME`, login overloads from default environment, configuration, or explicit user/group state, and equality/hash/string behavior. `UserGroupInformation` exposes global current UGI get/set, user/group accessors, login, `readFrom(Configuration)`, and a Commons Logging `LOG`.

`org.apache.hadoop.tools` covers command-line MapReduce tools. `DistCp` implements configurable distributed copy through constructor, `setConf`, `getConf`, `copy(String[] args)`, `run(String[] args)`, `main`, `getRandomId`, and logging; `DistCp.DuplicationException` has an `ERROR_CODE` field. `HadoopArchives` similarly exposes configurable archive creation through `archive(String[] args)`, `run`, and `main`. `Logalyzer` exposes `doArchive`, `doAnalyze`, and `main` for archiving and analyzing logs with MapReduce. Its `LogComparator` extends `Text.Comparator`, is configurable, and compares byte ranges. `LogRegexMapper` extends `MapReduceBase`, configures itself from a `JobConf`, and maps log records to text outputs.

`org.apache.hadoop.util` begins with `CyclicIteration`, `Daemon`, `DataChecksum`, `DiskChecker`, `GenericOptionsParser`, `GenericsUtil`, `HeapSort`, `HostsFileReader`, `IndexedSortable`, `IndexedSorter`, `LineReader`, `MergeSort`, `NativeCodeLoader`, `PlatformName`, `PrintJarMainClass`, `PriorityQueue`, `ProcfsBasedProcessTree`, `ProgramDriver`, `Progress`, `Progressable`, `QuickSort`, `ReflectionUtils`, `RunJar`, `ServletUtil`, `Shell`, `Shell.ExitCodeException`, `Shell.ShellCommandExecutor`, and the beginning of `StringUtils`.

Important utility contracts in this range include `DataChecksum` factory methods from type/bytes/checksum size, header serialization, checksum value writes, value comparison, reset/update, and constants for null/CRC32 checksum type and header sizing. `DiskChecker` creates directories with existence checks and validates directories, throwing `DiskErrorException` or `DiskOutOfSpaceException`. `GenericOptionsParser` parses generic Hadoop CLI options into a `Configuration`, exposes remaining app args, the Commons CLI `CommandLine`, libjars URLs, and generic usage printing.

Sorting and collection helpers use Hadoop's indexed sorting contracts. `IndexedSortable` supplies `compare` and `swap`; `IndexedSorter` sorts half-open ranges with or without `Progressable`; `HeapSort` and `QuickSort` implement that interface, with `QuickSort.getMaxDepth` documenting the fallback threshold to heapsort. `MergeSort` is a separate array merge sort over `int[]` with `Comparator<IntWritable>`. `PriorityQueue<T>` is an abstract heap where subclasses define `lessThan`; callers initialize capacity and then use `put`, `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.

Process, launcher, and system utilities include `ProcfsBasedProcessTree` for Linux `/proc`-based process-tree discovery, liveness, destroy, cumulative virtual-memory accounting, pid-file parsing, and SIGKILL delay configuration; `ProgramDriver` for command registry/dispatch; `RunJar` for jar extraction and main-class invocation; and `Shell` for template-method shell execution with environment/working-directory controls, interval gating, process/exit-code access, static command helpers, and `ShellCommandExecutor` for small-output command execution.

`StringUtils` is only partially covered here. The visible methods stringify exceptions, shorten fully qualified hostnames, format large integers and percentages, join string arrays, convert byte ranges or whole arrays to hex, and begin `hexStringToByte`.

## Control Flow and Behavioral Contracts

The JDiff file does not include method bodies, but the public contracts imply several important flows. Socket output setup constructs `SocketOutputStream` from a selectable channel or socket, forces non-blocking mode, and routes writes through readiness waits governed by the configured timeout. `transferToFully` loops until the requested number of bytes has been transferred from the `FileChannel`, surfacing EOF if the source ends early and socket timeout if the destination blocks too long.

Record I/O flow is symmetric: generated records call `startRecord`, emit or read fields by tag through primitive/string/buffer methods, recurse into vectors or maps by obtaining an `Index`, increment until `done()`, then close each vector/map/record. Binary implementations are used for Hadoop `Writable` persistence; CSV and XML implementations are alternate textual encodings with the same method shape.

Record compiler flow starts from an `Rcc` parser reading a record IDL. Grammar methods build `JFile`, `JRecord`, `JField`, and `JType` objects. `JFile.genCode` then emits code for a requested language into a destination directory. `RccTask.execute` wraps that flow for Ant by collecting a configured file or filesets, selecting a language and destination, and honoring `failonerror`.

Parser control flow is JavaCC-style. `SimpleCharStream` supplies buffered characters with source positions to `RccTokenManager`; the token manager switches lexical states for comments and returns `Token` objects; `Rcc` consumes tokens through grammar methods and emits `ParseException` or `TokenMgrError` when syntactic or lexical expectations fail. `ReInit` methods allow parser, token manager, and char stream objects to be reused with new inputs.

Record metadata flow serializes schema descriptions as records. `RecordTypeInfo` accumulates `FieldTypeInfo` objects, can nest struct metadata, serializes/deserializes itself through the same `Record` framework, and uses `TypeID` byte values for primitive/composite type identity. `meta.Utils.skip` consumes serialized data based on metadata, which is useful when filtering or evolving schemas.

Security identity flow centers on static/global current UGI and configuration persistence. `UnixUserGroupInformation.login` discovers user/group state, `saveToConf` writes it under a named property, and `readFromConf` or base `UserGroupInformation.readFrom` restores it. Writable methods allow UGI instances to travel across Hadoop RPC or job configuration paths.

Tool flow follows Hadoop's configurable command pattern. `DistCp` and `HadoopArchives` are constructed with a `Configuration`, can be used programmatically through `copy` or `archive`, and expose `run`/`main` for CLI execution. `Logalyzer.doArchive` stages logs, `doAnalyze` runs MapReduce analysis, `LogRegexMapper` processes records according to job configuration, and `LogComparator` controls sort ordering for log keys.

Generic CLI parsing happens before tool-specific execution. `GenericOptionsParser` mutates or augments the supplied `Configuration`, separates Hadoop generic options from application args, tracks `-libjars` URLs, and exposes the parsed Commons CLI command line. Tool runners outside this chunk rely on these semantics.

Sorting flow adapts caller-owned data to `IndexedSortable`, then passes index bounds to `HeapSort` or `QuickSort`. Implementations mutate only through `swap` and compare only through `compare`; progress-aware overloads can call `Progressable.progress()` in long sorts. `QuickSort`'s documented maximum recursion depth guards worst-case behavior by switching to heapsort.

Shell execution is template-method based. Subclasses supply a command vector and parse stdout. `run()` gates execution by interval, starts a process using the configured environment and working directory, records process/exit state, and throws `IOException` or `ExitCodeException` for failures. `ShellCommandExecutor` implements the simple case by collecting output as a string, and its docs state that output should be small.

Progress flow is tree-shaped. A root `Progress` gets phases added, moves through phases, lets leaves set progress/status, computes aggregate progress through the hierarchy, and can mark nodes complete. Several methods are synchronized in the API, signaling expected concurrent reads and updates by framework and task threads.

## State, Persistence, and Side Effects

The XML itself is persistent compatibility metadata used by JDiff. Runtime state described by these APIs includes socket channels and timeout values, thread-local binary record input/output wrappers, mutable `Buffer` backing arrays and counts, generated-record field values, record compiler ASTs, parser token/stream buffers, record type metadata, UGI user/group arrays, tool configurations, MapReduce job state, checksum values, parsed CLI arguments, host include/exclude sets, priority queue heap contents, process-tree snapshots, progress trees, shell process handles, shell output buffers, and servlet output writers.

Persistence and external effects are broad. Record APIs read and write binary, CSV, and XML data to streams. `Record`, `RecordTypeInfo`, and `UnixUserGroupInformation` participate in Hadoop's `Writable` persistence. `UnixUserGroupInformation.saveToConf` and `readFromConf` persist identities into `Configuration`. `JFile.genCode` and `RccTask.execute` write generated code to destination directories. `DistCp`, `HadoopArchives`, and `Logalyzer` interact with Hadoop filesystems and submit or run MapReduce jobs. `RunJar.unJar` writes jar contents to disk and `RunJar.main` executes arbitrary job code.

System side effects include opening sockets, configuring channels to non-blocking mode, running shell commands, setting process environments and working directories, checking or creating directories, reading host include/exclude files, reading `/proc`, destroying process trees, loading or checking native Hadoop libraries, writing servlet responses, and logging through Commons Logging.

Not all mutable classes are documented as thread-safe. `Progress` has synchronized methods, `SocketOutputStream.close` is synchronized, and binary record factories are explicitly thread-local. By contrast, parser objects, `Buffer`, record metadata builders, `PriorityQueue`, tool instances, `HostsFileReader`, and `ShellCommandExecutor` carry mutable state without a visible thread-safety contract in this XML.

## Dependencies and Integration Points

Network APIs depend on `java.net.Socket`, `java.net.Proxy`, `SocketFactory`, `InetAddress`, `UnknownHostException`, NIO `WritableByteChannel`, `SelectableChannel`, `ByteBuffer`, and `FileChannel`. Hadoop configuration integration appears through `org.apache.hadoop.conf.Configurable` and `Configuration`.

Record serialization depends on Java `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `IOException`, Hadoop `Writable`/`WritableComparable`/`WritableComparator`, and generated-code conventions from the record compiler. The compiler path depends on Ant `Task` and `FileSet`, JavaCC-generated parser classes, Java collections, and filesystem output directories.

Security APIs depend on Hadoop filesystem permission exceptions, configuration storage, logging, and Writable serialization. They are integration points for RPC, job submission, filesystem permission checks, and code paths that need current user/group identity.

Tools integrate with `Configuration`, MapReduce old API types such as `JobConf`, `MapReduceBase`, mapper output collectors/reporters, `Text.Comparator`, Hadoop filesystems, and CLI entry points. They are user-facing operational APIs, so signature or return-code compatibility matters.

Utility dependencies span Commons CLI, Commons Logging, servlet APIs, Java reflection, `Process`, files and readers, URI/URL handling, jar files/manifests, native libraries, Linux procfs, Hadoop `Path`, `IntWritable`, and `Progressable`. `DataChecksum` is a low-level integration point for HDFS block/data integrity code and any protocol that consumes its header/value layout.

## Risks and Compatibility Notes

This chunk starts mid-class for `SocketOutputStream`; adjacent earlier lines are needed for the class opening metadata, including its exact `extends` type. It also ends mid-class in `StringUtils`, so later lines are needed for the rest of that utility API and the package/API closure. Research for this chunk should therefore avoid claiming complete coverage of either class.

`SocketOutputStream` changes socket-channel blocking mode as part of construction. That side effect can break callers that continue to use `Socket.getInputStream()` or `Socket.getOutputStream()` directly; the Javadoc explicitly documents this incompatibility. Timeout handling and full-transfer semantics are also subtle because partial writes, EOF, and selector timeouts must be distinguished.

The record framework is a wire/storage compatibility surface. Changes to primitive encodings, variable-length integer encoding, `Buffer` compare order, field ordering, tags, map/vector delimiters, XML/CSV escaping, or record comparator behavior can break persisted data, generated-code interoperability, and sorted binary comparisons.

`Buffer.get()` exposes the backing array, and `set(byte[])` adopts the caller's array as backing storage. Aliasing can create surprising mutation bugs, but it is part of the documented API. Capacity/count separation must be preserved for callers that manage reusable buffers.

Record compiler generated classes expose many public parser fields and JavaCC implementation details. Although not ideal encapsulation, callers or build scripts may depend on those names. Regenerating the parser with different JavaCC versions could alter token constants, exception formatting, field visibility, or reinitialization signatures.

`RecordTypeInfo` and `TypeID` are schema-evolution primitives. Equality and hash-code behavior for nested map/vector/struct metadata must stay stable, and `meta.Utils.skip` must consume exactly the same wire representation as the active record input implementation.

UGI APIs are security-sensitive and legacy-global. Mutating current UGI, persisting user/group values in configuration, or creating immutable instances affects permission checks and job execution identity. Compatibility changes can become authorization regressions, especially where user/group arrays are trusted from configuration.

`DistCp`, `HadoopArchives`, and `Logalyzer` are operational tools. Their argument handling, return codes, exception behavior, configuration mutation, and MapReduce job setup are externally visible to scripts. `DistCp.DuplicationException.ERROR_CODE` suggests callers may branch on specific failure codes.

`DataChecksum` constants and header layout are protocol-sensitive. Any alteration to checksum type IDs, header length, bytes-per-checksum handling, or byte-order behavior would affect readers and writers of checksummed data.

`GenericOptionsParser` is a central CLI compatibility point. Changes to remaining-argument slicing, `-libjars` URL construction, `CommandLine` exposure, or usage output can break Hadoop tools and scripts.

`Shell`, `ProcfsBasedProcessTree`, native loading, and disk checking are platform-dependent. Unix command constants, Windows detection, `/proc` availability, process killing, directory permissions, disk-space errors, and native-library loading all depend on host OS behavior. Tests need explicit non-Linux or unavailable-feature coverage where possible.

`PriorityQueue` and indexed sorting expose caller-owned mutation hooks. Incorrect `lessThan`, `compare`, or `swap` semantics are caller bugs, but implementation changes can amplify them. Range interpretation for `IndexedSorter` is half-open `[l, r)`, and progress callbacks matter for long MapReduce tasks that otherwise risk timeout.

## Test Signals

JDiff validation should verify the XML remains well-formed across this slice's package transitions, preserves every public/protected API element in the listed packages, and keeps return types, parameter order, declared exceptions, visibility, static/final/abstract/synchronized flags, implemented interfaces, deprecation markers, and Javadoc contracts stable.

Socket tests should construct `SocketOutputStream` from socket channels and direct writable channels, verify non-negative timeout handling including zero-as-infinite behavior, check non-blocking side effects, exercise byte-array and `ByteBuffer` writes, close/idempotence behavior, `waitForWritable` timeout cases, and `transferToFully` success, partial-write, EOF, and timeout paths.

Record I/O tests should round-trip generated records through binary, CSV, and XML implementations; cover all primitive types, strings, buffers, records, vectors, and maps; verify thread-local binary wrapper reuse; assert `Index.done/incr` traversal behavior; and compare serialized records through `RecordComparator`.

`Buffer` tests should cover adopting versus copying arrays, offsets and lengths, appends, capacity growth/shrink, reset, truncate, backing-array exposure, lexicographic compare, equality/hash consistency, charset string conversion, cloning, and mutation aliasing.

Record utility and metadata tests should cover variable-length integer/long encoding boundaries, float/double byte decoding, byte comparison ordering, `TypeID` singleton equality/hash values, map/vector/struct equality, nested `RecordTypeInfo` lookup, schema serialization/deserialization, and `meta.Utils.skip` over primitive and nested serialized values.

Record compiler tests should parse simple and nested record IDL files, includes, maps, vectors, all primitive types, comments, bad syntax, and lexical errors; verify token source positions and parse exception messages; run `JFile.genCode` into a temporary directory; and exercise `RccTask` with single files, filesets, destination directory, language selection, and `failonerror` true/false.

Security tests should cover default and configured UGI login, explicit user/group constructors, immutable creation, `getUserName`, `getGroupNames`, Writable round trips, `saveToConf`/`readFromConf`, `setCurrentUGI`/`getCurrentUGI`, equality/hash/toString, and access-control exception propagation.

Tool tests should exercise `DistCp.copy/run/main` argument validation and duplicate-source handling, archive creation argument paths in `HadoopArchives`, `Logalyzer.doArchive` and `doAnalyze` configuration, `LogComparator` byte-range ordering, and `LogRegexMapper` configuration plus map output behavior. Return codes and logged/raised exceptions should be asserted because scripts may depend on them.

Utility tests should cover `DataChecksum` factory variants, header serialization/deserialization, checksum update/reset/value comparison, null versus CRC32 behavior, disk directory creation and error cases, generic option parsing and remaining args, libjars URL extraction, generic usage printing, `GenericsUtil` empty-list behavior, host include/exclude refreshes, line reading with different newline and max-length cases, and native-loader flags.

Sorting and queue tests should cover empty, single-element, duplicate-heavy, already-sorted, reverse-sorted, and subrange inputs for `HeapSort`, `QuickSort`, and `MergeSort`; verify `[l, r)` bounds; assert progress callbacks; test quicksort depth fallback indirectly with adversarial inputs; and cover priority queue capacity, ordering, rejection/acceptance by `insert`, `put`, `top`, `pop`, `adjustTop`, `size`, and `clear`.

Process and launcher tests should cover `ProcfsBasedProcessTree.isAvailable`, pid-file parsing, alive/dead detection, cumulative virtual memory, destroy and SIGKILL interval behavior in a controlled environment, `ProgramDriver` registration/dispatch/unknown command cases, `RunJar.unJar`, manifest main-class lookup, command-line main-class override, and `PrintJarMainClass` output.

Progress, reflection, servlet, shell, and string tests should cover progress-tree aggregation and concurrent updates, `ReflectionUtils` configuration injection and instance creation, thread-info logging interval suppression, servlet HTML/footer/parameter/percentage graph helpers, shell command environment and working directory propagation, interval gating, nonzero exit codes, output capture, Windows/non-Windows branches, and visible `StringUtils` methods for exception stringification, host shortening, number/percent formatting, array joining, and hex encode/decode.
