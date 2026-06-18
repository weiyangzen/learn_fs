# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 37384-43272

## Scope

This chunk is the tail of the Hadoop 0.17.0 JDiff API XML. It begins inside the already-open `org.apache.hadoop.record.CsvRecordOutput` class, covers the rest of `org.apache.hadoop.record`, the record compiler and generated parser packages, record type metadata, early security user/group APIs, the `Logalyzer` tool, most of the common utility package, and ends with `VersionInfo`, `XMLUtils`, the package summary for `org.apache.hadoop.util`, and the closing `</api>`.

Because the source is JDiff XML, this document describes the exported API contract rather than method bodies. Control-flow and state notes are inferred from signatures, inheritance, exceptions, fields, and Javadocs embedded in this chunk.

## Purpose

The chunk documents several foundational Hadoop Common surfaces from the 0.17.0 release:

- Hadoop Record I/O runtime APIs for generated records, record input/output encodings, raw comparators, XML serialization, and binary/variable-length utilities.
- Hadoop Record I/O compiler APIs, including the DDL model classes, Ant integration, JavaCC-generated parser, lexer, token stream, and parse/lexical error types.
- Record type metadata APIs that describe primitive, vector, map, and struct field types and can serialize `RecordTypeInfo`.
- User/group identity APIs for Unix-style users, groups, login, thread-local current UGI, and configuration persistence.
- Operational tools and utilities: log archiving/analyzing, recursive distributed copy, daemon threads, disk checks, generic command-line parsing, native library loading, shell execution, sorting helpers, progress reporting, reflection helpers, jar running, servlet helpers, string utilities, tool execution, build/version metadata, and XML transformation.

The APIs are cross-cutting infrastructure rather than one runtime subsystem. They support Hadoop serialization, command-line tools, MapReduce utilities, daemon diagnostics, filesystem/process interaction, and legacy security identity propagation.

## Important APIs, Types, and Functions

`org.apache.hadoop.record.Index` is a two-method iterator interface for deserializing vectors and maps. `done()` reports whether all elements have been consumed, and `incr()` advances to the next element. The Javadoc shows the expected loop shape: call `startVector()` or `startMap()`, process until `done()`, and call `incr()` after each element.

`org.apache.hadoop.record.Record` is the abstract base class for generated records. It implements `WritableComparable` and `Cloneable`, requires tagged `serialize(RecordOutput, String)`, tagged `deserialize(RecordInput, String)`, and `compareTo(Object)`, and provides untagged overloads plus Hadoop `Writable` adapters `write(DataOutput)` and `readFields(DataInput)`. `toString()` is exported, implying generated records can render through the record output layer.

`RecordComparator` extends `WritableComparator` for optimized raw byte comparisons of generated `Record` implementations. Subclasses implement raw `compare(byte[], int, int, byte[], int, int)`. The static synchronized `define(Class, RecordComparator)` registers a raw comparator for a record class.

`RecordInput` and `RecordOutput` define the core record serialization contract. Inputs read primitive and composite values by tag: `readByte`, `readBool`, `readInt`, `readLong`, `readFloat`, `readDouble`, `readString`, `readBuffer`, `startRecord`, `endRecord`, `startVector`, `endVector`, `startMap`, and `endMap`. Outputs provide the symmetric methods `writeByte`, `writeBool`, `writeInt`, `writeLong`, `writeFloat`, `writeDouble`, `writeString`, `writeBuffer`, `startRecord`, `endRecord`, `startVector`, `endVector`, `startMap`, and `endMap`. Tags are primarily for tagged encodings such as XML.

`org.apache.hadoop.record.Utils` provides record runtime helpers: float/double parsing from byte arrays, variable-length integer and long reads from byte arrays or streams, `getVIntSize(long)`, variable-length integer and long writes to `DataOutput`, and byte-array lexicographic comparison. The public `hexchars` field supports hex-oriented encoding.

`XmlRecordInput` and `XmlRecordOutput` implement `RecordInput` and `RecordOutput` over `InputStream`/`OutputStream`, exposing the same primitive/composite read/write methods. These are the XML serializer and deserializer for the record runtime.

The `org.apache.hadoop.record` package-level documentation is unusually substantive. It defines Record I/O as a language-neutral DDL and translator for generating serialization/deserialization code. It documents primitive types (`byte`, `boolean`, `int`, `long`, `float`, `double`, `ustring`, `buffer`), composite types (`record`, `vector`, `map`), DDL syntax with `include`, `module`, and `class`, `rcc` invocation with `-l/--language`, Java and C++ type mappings, and binary/CSV/XML encodings.

`org.apache.hadoop.record.compiler.CodeBuffer` wraps a `StringBuffer` with automatic indentation and exposes `toString()`. `Consts` exports string constants used by generated compiler output: `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.

The DDL model classes are `JType` plus concrete primitive/composite subclasses: `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`. `JField<T>` wraps a field name and type. `JFile` represents a DDL compilation unit with a filename, included `JFile`s, and records, and exposes `genCode(String language, String destDir, ArrayList<String> options)`.

`org.apache.hadoop.record.compiler.ant.RccTask` is the Ant integration for the record compiler. It has setters for output language, single input file, fail-on-error behavior, destination directory, and nested `FileSet`s, and `execute()` invokes the compiler. Its Javadoc says default language is Java, default destination is `.`, and `failonerror` defaults to true.

The `org.apache.hadoop.record.compiler.generated` package is JavaCC-generated parser infrastructure. `ParseException` carries `currentToken`, `expectedTokenSequences`, `tokenImage`, and `specialConstructor`, and can produce a parse error message through `getMessage()`. `Rcc` implements `RccConstants` and exposes `main`, `usage`, `driver`, grammar productions (`Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, `Vector`), parser reinitialization overloads, token access, parse exception generation, and tracing toggles. `RccConstants` defines token ids for EOF, module/record/include keywords, primitive types, vector/map, braces, angle brackets, semicolon, comma, dot, string literal, identifier, lexical states, and `tokenImage`.

`RccTokenManager` is the generated lexer with debug stream support, `ReInit`, lexical-state switching, token creation, and `getNextToken()`. `SimpleCharStream` is the generated character stream for ASCII input, with constructors over `Reader` and `InputStream` plus optional encoding, line/column tracking, buffer expansion/fill, token start, character reading, backup, reinitialization, image/suffix extraction, cleanup, and begin-line/column adjustment. `Token` exposes token kind, begin/end position, image, next token, special-token chain, and `newToken(int)`. `TokenMgrError` represents lexer errors and provides escaping, lexical-error message creation, and `getMessage()`.

The record metadata package describes runtime type information. `FieldTypeInfo` pairs a field id/name with a `TypeID` and implements equality/hash behavior. `TypeID` represents primitive types with shared constants such as `BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, and `StringTypeID`; `TypeID.RIOType` contains byte constants for supported IDL types. `VectorTypeID`, `MapTypeID`, and `StructTypeID` describe composite element/key/value/struct metadata. `RecordTypeInfo` extends `Record`, stores a record name and a collection of `FieldTypeInfo`, supports adding fields, looking up one-level nested struct type info, and serializing/deserializing the metadata. `org.apache.hadoop.record.meta.Utils.skip(RecordInput, String, TypeID)` skips data in a record stream based on type metadata.

`UnixUserGroupInformation` extends abstract `UserGroupInformation`. It has constructors from user/group names, `createImmutable(String[])`, user and group getters, `Writable` serialization/deserialization, `saveToConf(Configuration, String, UnixUserGroupInformation)`, `readFromConf(Configuration, String)`, and login overloads from Unix or configuration. Public `UGI_PROPERTY_NAME` identifies the default property name. Equality and hash code are user/group identity oriented, with hash code based on username.

`UserGroupInformation` is the abstract base for identity state. It implements `Writable`, exposes static `getCurrentUGI()` and `setCurrentUGI(UserGroupInformation)` for current-thread identity, abstract user/group getters, static `login(Configuration)`, static `readFrom(Configuration)`, and public logging field `LOG`.

`org.apache.hadoop.tools.Logalyzer` is a utility for archiving and analyzing Hadoop logs. `doArchive(String logListURI, String archiveDirectory)` archives logs listed by a URI. `doAnalyze(String inputFilesDirectory, String outputDirectory, String grepPattern, String sortColumns, String columnSeparator)` runs grep/sort analysis. `LogComparator` extends `Text.Comparator` and implements `Configurable` for optimized raw log-key sorting. `LogRegexMapper` extends `MapReduceBase` and implements `Mapper<K, Text, Text, LongWritable>` to emit matches for a configured regular expression.

`CopyFiles` implements `Tool` and provides recursive MapReduce-based copying between filesystems. It exposes configuration setters/getters, a static `copy(Configuration, String srcPath, String destPath, Path logPath, boolean srcAsList, boolean ignoreReadFailures)`, `run(String[])`, and `main(String[])`. `CopyFiles.DuplicationException` is an `IOException` subtype with public `ERROR_CODE`.

`Daemon` is a `Thread` subclass whose constructors mark the thread as daemon; it can wrap a `Runnable` and exposes `getRunnable()`.

`DiskChecker` provides `mkdirsWithExistsCheck(File)` and `checkDir(File)`, with `DiskErrorException` and `DiskOutOfSpaceException` as `IOException` subtypes. The mkdir helper explicitly tolerates races where another process creates a parent directory between existence check and mkdir.

`GenericOptionsParser` parses Hadoop-generic command-line options into a `Configuration`, optionally alongside caller-supplied Commons CLI `Options`. It exposes remaining application args, the parsed `CommandLine`, and static generic usage output. The documented generic options are `-conf`, `-D`, `-fs`, and `-jt`.

`GenericsUtil` exposes `getClass(T)`, `toArray(Class<T>, List<T>)`, and `toArray(List<T>)`. The no-class overload requires a non-empty list and can throw `ArrayIndexOutOfBoundsException` on an empty list.

`HostsFileReader` reads include and exclude host files through a constructor taking two path strings, `refresh()`, `getHosts()`, and `getExcludedHosts()`.

`IndexedSortable` and `IndexedSorter` define index-addressed sorting. Sortable collections expose `compare(int, int)` and `swap(int, int)`. Sorters expose `sort(IndexedSortable, int l, int r)` over `[l, r)`. `QuickSort` implements `IndexedSorter` with `sort` overloads, including one that accepts a `Progressable`. `MergeSort` exposes `mergeSort(int[] src, int[] dest, int low, int high)` over integer index arrays and is constructed with a comparator over `IntWritable`.

`NativeCodeLoader` exposes `isNativeCodeLoaded()` and job-level native-library controls `getLoadNativeLibraries(JobConf)` and `setLoadNativeLibraries(JobConf, boolean)`. `PlatformName` reports the JVM platform string. `PrintJarMainClass` prints a jar's main class. `RunJar` can `unJar(File, File)` and run a Hadoop job jar from `main(String[])`.

`PriorityQueue` is an abstract heap-like queue. Subclasses define `lessThan(Object, Object)` and call `initialize(int maxSize)`. The API includes `put`, bounded `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.

`ProgramDriver` registers and dispatches named programs with `addClass(String name, Class mainClass, String description)` and `driver(String[] args)`.

`Progress` models hierarchical progress. It supports adding named/unnamed phases, advancing to the next phase, returning the current phase, completing a node, setting leaf progress, computing overall root progress, setting status text, and `toString()`. `Progressable` is the single-method callback interface `progress()`.

`ReflectionUtils` provides configuration injection and reflective construction through `setConf(Object, Configuration)` and `newInstance(Class, Configuration)`, plus thread diagnostics and contention tracing via `setContentionTracing(boolean)`, `printThreadInfo(PrintWriter, String)`, and `logThreadInfo(Log, String, long)`.

`ServletUtil` provides simple servlet/JSP helpers: `initHTML(ServletResponse, String)`, `getParameter(ServletRequest, String)` returning null for all-whitespace values, `htmlFooter()`, and public `HTML_TAIL`.

`Shell` is an abstract base for executing platform commands with an optional minimum re-execution interval. It exposes helpers for Unix groups, permission, and ulimit commands; protected environment and working-directory setters; protected `run()`; abstract `getExecString()` and `parseExecResult(BufferedReader)`; process and exit-code getters; static `execCommand(String[])`; command constants; and `WINDOWS`. `Shell.ExitCodeException` is an `IOException` with an exit code. `Shell.ShellCommandExecutor` stores small command output as-is and supports command/working-directory/environment constructors plus `execute()`, `getOutput()`, and inherited execution hooks.

`StringUtils` provides exception stringification, hostname shortening, human-readable integer formatting using `k/m/g`, percentage formatting, comma-separated array formatting, hex conversion, URI/path string conversion, elapsed-time formatting, comma-separated string parsing, escaped splitting, escaping/unescaping of separators, hostname retrieval without propagating exceptions, and startup/shutdown log messages. Public constants are `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`.

`Tool` is the standard Hadoop command interface. It extends `Configurable` and defines `run(String[] args)`. `ToolRunner` runs a `Tool` with generic option parsing, sets the tool configuration, delegates remaining args, and can print generic usage.

`VersionInfo` exposes static build metadata getters for Hadoop version, Subversion revision, build date, build user, and source URL, plus `main(String[])`. `XMLUtils.transform(InputStream styleSheet, InputStream xml, Writer out)` runs an XML transform and surfaces `TransformerConfigurationException` and `TransformerException`.

## Control Flow

Record I/O control flow starts with generated record classes extending `Record`. A caller writes a record through `Record.write(DataOutput)` or `serialize(RecordOutput, tag)`. The generated implementation calls `RecordOutput.startRecord`, writes each field with the correct primitive/composite method, iterates vectors/maps, and closes the record. Reads reverse the sequence through `RecordInput.startRecord`, primitive reads, `startVector`/`startMap` returning an `Index`, repeated `done()`/`incr()` iteration, and `end*` calls. Untagged `serialize`/`deserialize` are convenience adapters over tagged methods; `Writable` methods adapt records to Hadoop's `DataInput`/`DataOutput` ecosystem.

The record compiler flow is DDL text to generated code. `Rcc.main()` or `Rcc.driver()` parses arguments, the JavaCC parser walks grammar productions from `Input()` through includes, module names, records, fields, and nested type productions. It creates `JFile`, `JRecord`, `JField`, and `JType` model objects. `JFile.genCode()` then dispatches to a lower-level language generator for Java or C++ output. `RccTask.execute()` wraps this flow for Ant by gathering a single file and/or filesets, applying language/destination/fail-on-error options, and invoking the compiler for each record definition.

The parser/lexer flow is JavaCC-standard. `SimpleCharStream` buffers characters and tracks token positions. `RccTokenManager` reads the stream, applies lexical states including comment states, and returns `Token` objects. `Rcc` consumes tokens through grammar methods, throws `ParseException` on grammar mismatch, and exposes `generateParseException()` for detailed expected-token errors. Lexical failures are represented by `TokenMgrError`.

Record metadata flow uses `TypeID` instances to describe fields independent of generated Java classes. Callers build a `RecordTypeInfo`, set its name, add fields with `addField(fieldName, TypeID)`, and serialize it through the normal `Record` path. During deserialization, a `RecordTypeInfo` can reconstruct metadata from a `RecordInput`. `meta.Utils.skip()` uses the type id to consume and discard a matching value from an input stream.

UGI control flow has both configuration-backed and OS-backed paths. `UnixUserGroupInformation.login()` reads the current Unix username and groups, while `login(Configuration, boolean)` first tries configured identity and falls back to Unix lookup. `readFromConf()` loads comma-separated user/group identity from a configuration property and can reuse an existing per-user UGI cache according to the Javadoc. `saveToConf()` writes the comma-separated identity back to configuration. `UserGroupInformation.setCurrentUGI()` and `getCurrentUGI()` provide current-thread identity propagation.

`Logalyzer` has two high-level flows. Archiving reads a URI that serves log-file URIs and copies those logs into an archive directory. Analysis configures a MapReduce job around regex extraction and sorted output: `LogRegexMapper` reads text lines, emits matching text with counts, and `LogComparator` sorts raw UTF8 keys according to configured columns/separators.

`CopyFiles.run()` is the command driver for recursive distributed copy. Its Javadoc describes listing the source recursively, distributing copy work across map input files in round-robin fashion, copying in mappers, and using no reducer. The static `copy()` entry point exposes this workflow directly for callers that already have a configuration and copy flags.

`GenericOptionsParser` and `ToolRunner` define the legacy Hadoop CLI flow. Generic options mutate the configuration and are removed from the application argument list. `ToolRunner.run(conf, tool, args)` parses those options, sets the resulting configuration on the tool, and invokes `tool.run()` with only the remaining command-specific arguments. `ToolRunner.run(tool, args)` delegates using the tool's existing configuration.

Sorting flow is decoupled from storage. `QuickSort` and any `IndexedSorter` implementation call only `IndexedSortable.compare(i, j)` and `swap(i, j)` for indices in `[l, r)`. This lets sort algorithms operate over arrays, buffers, or other structures without owning the data.

`Progress` flow is tree-shaped. Applications build phases with `addPhase()`, enter work through `phase()`/`startNextPhase()`, report leaf progress with `set(float)`, complete nodes with `complete()`, and query aggregate root progress with `get()`. `QuickSort` can receive a `Progressable` callback to report activity during long sorts.

`Shell` flow checks the configured minimum interval, prepares environment and working directory, runs `getExecString()` through a subprocess, lets `parseExecResult()` consume stdout, records the process and exit code, and throws `ExitCodeException` on non-zero exit. `ShellCommandExecutor` implements the abstract hooks by returning a fixed command and collecting output into an internal string.

`RunJar` flow unpacks a job jar into a directory, discovers or accepts the main class, constructs an execution environment, and invokes the jar's main entry point. `PrintJarMainClass` is the smaller manifest-inspection utility.

## State and Persistence Behavior

The XML file itself is generated API metadata and does not persist runtime state. The APIs described here, however, expose several stateful contracts.

Generated `Record` classes are stateful data containers. Their persistent form is controlled by `RecordOutput`/`RecordInput` implementations and Hadoop `Writable` adapters. Binary encoding persists vector/map lengths, zero-compressed integers/longs, UTF-8 strings with lengths, raw buffers with lengths, and network-order floating-point values. CSV and XML encodings persist additional delimiters/tags and escaping.

`RecordComparator.define()` mutates global comparator registration state for a record class. This state affects subsequent raw comparisons by Hadoop sorting/shuffle code that consults `WritableComparator` registrations.

The record compiler model (`JFile`, `JRecord`, `JField`, `JType`) is in-memory compilation state. `genCode()` persists generated Java/C++ source files under the destination directory. `RccTask` persists nothing itself but writes generated source files as an Ant build side effect.

JavaCC parser state is mutable: `Rcc` stores `token_source`, current `token`, and `jj_nt`; `SimpleCharStream` stores buffer positions, line/column arrays, previous newline flags, input reader, and tab size; tokens carry linked-list references for regular and special tokens. Reuse is supported through `ReInit()` methods rather than constructing new parser objects.

`RecordTypeInfo` persists metadata as a record. It stores record name and fields, serializes/deserializes through normal record streams, and provides nested-struct lookup limited to one nesting level. `TypeID` primitive constants are shared singleton-like public objects; composite `TypeID` objects carry references to element/key/value/record metadata.

`UnixUserGroupInformation` persists identity in two forms: Hadoop `Writable` binary/string-format serialization and comma-separated configuration properties. The configuration format starts with username followed by default group and other groups. The API also implies a per-user UGI cache, so repeated login/read operations can return an existing object.

`UserGroupInformation` keeps current identity per thread. That state is process-local and can affect downstream filesystem, RPC, or job behavior that queries the current UGI.

`HostsFileReader` maintains in-memory include and exclude host sets loaded from files. `refresh()` reloads them, and getters expose the current sets.

`NativeCodeLoader` exposes process-level native-code load state through `isNativeCodeLoaded()` and job-level configuration state through `getLoadNativeLibraries()`/`setLoadNativeLibraries()`.

`PriorityQueue`, `Progress`, and `Shell` are stateful utility objects. `PriorityQueue` stores heap contents and max size. `Progress` stores a phase tree, current phase, per-node progress, and status text. `Shell` stores command interval, process, exit code, environment, and working directory; `ShellCommandExecutor` additionally stores captured output.

`StringUtils` and most simple utility classes are stateless, but methods such as `startupShutdownMessage()` write to logs, `getHostname()` observes host environment, and URI/path conversion allocates domain objects. `VersionInfo` observes build metadata embedded in the artifact. `XMLUtils.transform()` streams transformed output to a caller-provided `Writer`.

## Dependencies and Integration Points

Record I/O integrates with `org.apache.hadoop.io.WritableComparable`, `WritableComparator`, `DataInput`, `DataOutput`, `RecordInput`, `RecordOutput`, `Buffer`, Java collections (`ArrayList`, `TreeMap`), and Java I/O streams. The design docs explicitly connect generated Java and C++ code to binary, CSV, and XML encodings.

The record compiler integrates with JavaCC-generated parser classes, Ant (`Task`, `FileSet`, `BuildException`), filesystem paths for source/destination files, and lower-level language generators referenced in package documentation (`CppGenerator` and `JavaGenerator`). Generated Java code maps DDL modules to packages and DDL records to `.java` classes; generated C++ maps modules to namespaces and DDL files to `.cc/.hh` pairs.

Record metadata integrates back into the record runtime: `RecordTypeInfo` is itself a `Record`, `meta.Utils.skip()` consumes a `RecordInput`, and `TypeID` constants mirror the Record I/O DDL type system.

Security APIs integrate with `Configuration`, `Writable`, `Shell`-style Unix group/user discovery, `javax.security.auth.login.LoginException`, and logging. The configuration-persistence methods make UGI data available to clients/jobs without requiring every component to re-run OS login.

`Logalyzer` integrates with the old `org.apache.hadoop.mapred` API (`Mapper`, `MapReduceBase`, `JobConf`, `OutputCollector`, `Reporter`), Hadoop IO types (`Text`, `LongWritable`, `WritableComparable`), raw comparators, and DFS/local files used for archived logs and analysis output.

`CopyFiles` integrates with `Tool`, `Configuration`, `Path`, MapReduce execution, recursive filesystem listing, map input splitting, and job log paths. It is an early precursor to distributed copy behavior.

Common utilities integrate broadly: `GenericOptionsParser` uses Apache Commons CLI; `ToolRunner` depends on `Tool` and `Configuration`; `NativeCodeLoader` and `Shell` integrate with OS/platform capabilities; `ReflectionUtils` integrates with `Configurable` objects and logging; `ServletUtil` integrates with `javax.servlet`; `XMLUtils` integrates with `javax.xml.transform`; `RunJar` and `PrintJarMainClass` integrate with jar manifests and dynamic application launch.

## Risks and Edge Cases

This chunk starts in the middle of `CsvRecordOutput`, so the final per-file reconciliation should combine it with the prior chunk for the full CSV output API. Likewise, many compiler superclass details such as `JCompType` and generator internals are referenced but not declared here.

Record I/O compatibility is sensitive to field order, type signatures, container lengths, tag handling, and encoding choice. The package documentation says optional fields/backward-forward compatibility were planned but not described in this version, so generated records in 0.17.0 should be treated as schema-order-sensitive.

`RecordInput` vector/map iteration relies on callers correctly pairing `start*`, `Index.done()/incr()`, element reads, and `end*`. Off-by-one loops or missing `incr()` can desynchronize the stream. Tagged formats can also fail if generated field tags do not match expected XML names.

Variable-length integer encoding must preserve sign and boundary cases. The documented compact range for integers/longs and multi-byte length marker creates risk around values near `-120`, `127`, max/min int, and max/min long.

CSV and XML encodings include escaping rules for nulls, line feeds, percent signs, commas, control characters, and binary buffers. Incorrect escaping can produce data loss, invalid XML, or records that are readable in one implementation but not another.

`RecordComparator` raw comparators must match object-level `compareTo()` semantics. Divergence can break MapReduce sorting/grouping because raw bytes may be used without object deserialization.

The record compiler parser is generated and exposes mutable public fields. Reusing parser/token-manager instances without `ReInit()` or across threads is risky. `TokenMgrError` extends `Error`, so lexical failures may bypass normal checked-exception handling.

`RecordTypeInfo.compareTo()` is documented as not meaningful for normal ordering. Code should not use it for sorted collections despite the class extending `Record` and therefore inheriting `WritableComparable` expectations.

UGI identity is weak by modern security standards: it stores user/group names, reads from Unix/configuration, and serializes comma-separated strings. Malformed configuration raises `LoginException`, and trusting configuration-sourced users can be unsafe unless the caller controls that configuration. Thread-local current UGI can also leak identity across reused threads if not reset.

`Shell` and `NativeCodeLoader` are platform-dependent. `getUlimitMemoryCommand()` may return null on Windows/Cygwin or when unspecified. Shell command output is expected to be small in `ShellCommandExecutor`; using it for large outputs risks memory pressure. Environment/working-directory mutation affects subprocess behavior and must be tested separately on supported platforms.

`DiskChecker.mkdirsWithExistsCheck()` is designed for races but still depends on filesystem permissions and eventual directory writability. `checkDir()` can surface disk errors through custom exceptions.

`GenericOptionsParser` mutates the provided `Configuration`. Applications that parse generic options too late or reuse a configuration across tests can observe surprising defaults for `fs.default.name`, `mapred.job.tracker`, or custom `-D` values.

`GenericsUtil.toArray(List<T>)` is unsafe for empty lists per its own Javadoc. Prefer the overload taking `Class<T>` when the list may be empty.

`PriorityQueue.insert()` is bounded by initialized max size, and subclasses define ordering through `lessThan()`. Incorrect `lessThan()` consistency can corrupt queue semantics. `adjustTop()` must be called after mutating the top element.

`ReflectionUtils.newInstance()` may run arbitrary constructors and then inject configuration. Constructors with side effects or missing no-arg constructors can fail before configuration is set.

`StringUtils.split`/`escapeString`/`unEscapeString` must keep escaping semantics aligned, especially around trailing escape characters, escaped commas, and double escaping. Hex conversion requires even-length valid hex strings.

`RunJar` executes user-supplied jar code and unpacks archives, so callers must consider classpath isolation, manifest correctness, extraction paths, and error propagation from invoked main methods.

## Test Signals

Record runtime tests should round-trip generated records through binary, CSV, and XML `RecordInput`/`RecordOutput` implementations; cover every primitive type; cover nested records, vectors, and maps; verify null/empty strings and buffers; exercise non-ASCII `ustring` data; and compare tagged versus untagged `serialize`/`deserialize` paths.

Variable-length utility tests should cover compact and expanded encodings for `int` and `long`, boundary values around `-120` and `128`, min/max integer values, stream and byte-array reads, encoded-size calculation, and lexicographic byte comparison behavior.

Comparator tests should assert that registered `RecordComparator` raw comparisons produce the same ordering as deserialized `Record.compareTo()` for representative records and edge values.

Record compiler tests should parse valid DDL with includes, modules, primitive fields, vectors, maps, and record references; reject malformed DDL with useful `ParseException` messages; verify token line/column reporting; generate Java and C++ into expected destination directories; and verify Ant `RccTask` behavior for file, fileset, language, destination, and fail-on-error combinations.

Record metadata tests should build `RecordTypeInfo` with primitive and composite fields, serialize/deserialize it, compare `FieldTypeInfo` and `TypeID` equality/hash behavior, retrieve nested struct metadata, and verify `meta.Utils.skip()` consumes exactly the bytes for each type without corrupting subsequent reads.

UGI tests should cover constructor validation, immutable creation, group ordering with default group first, writable serialization round trips, comma-separated configuration save/read, malformed configuration failures, login fallback behavior, per-thread current UGI isolation, equality/hash code, and behavior when the Unix group command fails.

`Logalyzer` tests should cover archive input URI handling, archive destination creation, regex mapper configuration and match output, sort column/separator interpretation in `LogComparator`, and end-to-end analysis output on a small fixture.

`CopyFiles` tests should cover recursive source listing, multiple filesystem URI schemes, list-file source mode, duplicate source detection and `DuplicationException.ERROR_CODE`, ignored versus fatal read failures, log-path output, command-line argument validation, and `ToolRunner` integration.

Utility tests should cover `Daemon` daemon flag and wrapped runnable retention; `DiskChecker` directory creation races, non-directory paths, unwritable paths, and disk-space exceptions; `GenericOptionsParser` handling of `-conf`, `-D`, `-fs`, `-jt`, unknown options, remaining args, and custom Commons CLI options; and `GenericsUtil` empty-list behavior.

Sorting tests should verify `QuickSort` and `MergeSort` on empty, single-item, duplicate, already-sorted, reverse-sorted, and random data; assert that `IndexedSortable` swaps stay within `[l, r)`; and verify `Progressable.progress()` is invoked for long quicksort runs.

`PriorityQueue` tests should validate max-size initialization, `put`, bounded `insert`, `top`, `pop`, `adjustTop`, `size`, `clear`, and ordering when `lessThan()` defines reverse or equal-priority cases.

`Progress` tests should build multi-level phase trees, verify current phase transitions, complete propagation to parents, aggregate progress values, status text, and `toString()` output.

`Shell` tests should run simple commands, non-zero exit commands, custom environment, custom working directory, interval gating, stdout parsing, large-output guard behavior for `ShellCommandExecutor`, Windows/null command branches where applicable, and `ExitCodeException.getExitCode()`.

`ReflectionUtils` tests should instantiate configurable and non-configurable classes, verify configuration injection order, handle constructor failures, and exercise thread-info logging without assuming stable thread ordering.

`StringUtils` tests should cover exception stack rendering, hostnames with/without dots, human-readable integer thresholds, percentage precision, empty and non-empty arrays, byte/hex round trips, invalid hex strings, URI/path conversion, negative and zero time differences, escaped split/escape/unescape edge cases, hostname fallback, and startup/shutdown logging.

`Tool`/`ToolRunner` tests should verify configuration propagation, null configuration handling, remaining application arguments after generic parsing, returned exit codes, thrown exceptions, and generic usage output.

`VersionInfo` tests should verify all metadata getters return non-null stable strings for a packaged build and that `main()` prints the expected fields. `XMLUtils` tests should run a small XSLT transform, malformed stylesheet, malformed XML, and writer error propagation.

## Cross-Chunk Notes

The chunk begins after the start of `CsvRecordOutput`; earlier `org.apache.hadoop.record` declarations such as `Buffer`, `BinaryRecordInput`, `BinaryRecordOutput`, `CsvRecordInput`, and the beginning of `CsvRecordOutput` are expected in the preceding chunk.

The compiler package references `JCompType`, `CppGenerator`, and `JavaGenerator`, but this chunk only exposes the public DDL model and generated parser surfaces. The final reconciliation should connect those references to chunks containing their declarations or implementation details.

The `org.apache.hadoop.util` section in this chunk starts at `CopyFiles` and ends the package. Earlier utility classes, if any, are outside this chunk and should be merged into the final per-file research for complete Hadoop 0.17.0 utility coverage.
