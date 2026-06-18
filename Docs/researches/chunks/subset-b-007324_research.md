# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.1.xml lines 25138-31469

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.20.1. It is XML metadata, not Java implementation source. The range starts inside the tail of `org.apache.hadoop.record.CsvRecordInput`, covers complete API entries for record I/O, record compiler, record metadata, security/authorization, and many `org.apache.hadoop.util` classes, then ends inside the second `ToolRunner.run(Tool, String[])` method documentation. The final `ToolRunner` class entry continues after this chunk.

The XML records compatibility-facing declarations: class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, checked exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc. Because bodies are absent, control flow, persistence, and state behavior below are inferred from signatures and Javadoc contracts.

## Purpose

This slice captures a broad public API surface that sits between Hadoop's generated record serialization framework, command-line tooling, security policy model, and common utility layer.

The `org.apache.hadoop.record` APIs define typed record serialization/deserialization contracts for binary-like records, CSV, XML, generated record classes, raw comparators, and schema/type metadata. These APIs matter for persisted job metadata and wire/data compatibility because generated records implement `WritableComparable` and expose stable field/type descriptors.

The `org.apache.hadoop.record.compiler` and `org.apache.hadoop.record.compiler.generated` APIs expose the record compiler model and parser generated from the record IDL grammar. They are build/tooling surfaces used by `rcc` and Ant tasks to turn record descriptions into language-specific generated classes.

The `org.apache.hadoop.security` and `org.apache.hadoop.security.authorize` APIs define historical Hadoop user/group identity, ACL, Java `Policy`, service permissions, and policy-refresh integration. These are administrative and RPC authorization surfaces.

The `org.apache.hadoop.util` portion provides reusable process, checksum, disk, command-line, sorting, host-file, line-reading, memory, native-code, reflection, jar, servlet, shell, string, progress, and tool-runner utilities. These are cross-cutting APIs used by daemons, CLIs, MapReduce jobs, tests, and web UIs.

## Important APIs and Types

### Record I/O and Serialization

The chunk begins with the final visible methods of `CsvRecordInput`: `endRecord(String tag)`, `startVector(String tag)`, `endVector(String tag)`, `startMap(String tag)`, and `endMap(String tag)`, all public instance methods declaring `IOException`; the `start*` methods return `org.apache.hadoop.record.Index`.

`CsvRecordOutput` implements `RecordOutput` and is constructed from an `OutputStream`. It writes primitive and structured values through `writeByte`, `writeBool`, `writeInt`, `writeLong`, `writeFloat`, `writeDouble`, `writeString`, `writeBuffer`, `startRecord`, `endRecord`, `startVector`, `endVector`, `startMap`, and `endMap`. Structured output receives `Record`, `ArrayList`, or `TreeMap` values plus a tag.

`Index` is the iterator-like interface returned by record input implementations for vectors and maps. It exposes `done()` and `incr()`. The Javadoc example shows the expected loop: call `startVector`, read elements while `!idx.done()`, then call `idx.incr()` after each element.

`Record` is an abstract base class for generated records. It implements `WritableComparable` and `Cloneable`, has abstract tagged `serialize(RecordOutput,String)`, `deserialize(RecordInput,String)`, and `compareTo(Object)`, plus concrete untagged `serialize(RecordOutput)`, `deserialize(RecordInput)`, `write(DataOutput)`, `readFields(DataInput)`, and `toString()`. It bridges Hadoop `Writable` binary I/O with the record framework's tagged and untagged formats.

`RecordComparator` extends `WritableComparator` and provides a protected constructor for a record class, an abstract raw `compare(byte[], int, int, byte[], int, int)`, and a synchronized static `define(Class, RecordComparator)` registration method for optimized raw comparators.

`RecordInput` and `RecordOutput` are the main format-neutral interfaces. `RecordInput` declares typed reads for primitive values, strings, `Buffer`, records, vectors, and maps, with tags used by tagged formats such as XML. `RecordOutput` mirrors this with typed writes and structured start/end hooks. Implementations in this chunk include CSV and XML record input/output classes.

`org.apache.hadoop.record.Utils` exposes low-level record encoding helpers: `readFloat`, `readDouble`, variable-length integer reads from `DataInput` and byte arrays, `getVIntSize`, `writeVLong`, `writeVInt`, `compareBytes`, and a `hexchars` field. These APIs support compact numeric encoding and raw byte comparison in record serialization.

`XmlRecordInput` and `XmlRecordOutput` implement `RecordInput` and `RecordOutput` over streams. They expose the same primitive, string, buffer, record, vector, and map APIs as CSV, with constructor inputs of `InputStream` or `OutputStream`.

### Record Compiler and Generated Parser

`CodeBuffer` is a small code-generation buffer with a public `toString()`. `Consts` defines public static final string constants used by generated code, including `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.

Compiler model classes represent record IDL types and fields: `JBoolean`, `JByte`, `JDouble`, `JFloat`, `JInt`, and `JLong` extend `JType`; `JBuffer`, `JString`, `JMap`, `JRecord`, and `JVector` extend composite type machinery; `JField` pairs a field name with a type object; `JFile` is constructed from a filename and module/record lists and exposes `genCode(String language, String destDir)` returning an int. `JMap` carries key/value `JType`s, `JVector` carries an element `JType`, and `JRecord` carries a name and field list.

`RccTask` is an Ant integration point extending `org.apache.tools.ant.Task`. It has setters for language, file, fail-on-error, destination directory, and filesets, plus `execute()`. This allows record compiler invocation from build files.

`ParseException`, `Rcc`, `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError` are JavaCC-style generated parser/lexer APIs. `Rcc` has constructors for `InputStream`, `InputStream` with encoding, `Reader`, and `RccTokenManager`; parser methods include `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, `Vector`, reinitialization overloads, token access, parse-exception generation, and tracing toggles. `RccConstants` defines token ids such as module, record, include, primitive types, vector/map tokens, punctuation, strings, identifiers, lexical states, and `tokenImage`.

`RccTokenManager` exposes lexer reinitialization, lexical-state switching, token filling, and `getNextToken()`, with public fields for debug stream, literal images, lexical state names, new lexical states, input stream, and current char. `SimpleCharStream` manages buffered reader/input-stream character access, line/column tracking, backup, suffix/image retrieval, and buffer expansion. `Token` stores token kind, source span, image, linked next token, special token, and factory/toString helpers. `TokenMgrError` wraps lexical errors and exposes escape/error-message helpers.

### Record Metadata

`FieldTypeInfo` exposes field id and `TypeID`, with equality and hashing. `TypeID` is the base representation for primitive and composite record types. It exposes singleton/static fields for bool, buffer, byte, double, float, int, long, and string type IDs, a `typeVal` byte, `getTypeVal()`, equality, and hashing. Nested `TypeID.RIOType` defines byte constants for all record I/O type tags: bool, buffer, byte, double, float, int, long, map, string, struct, and vector.

`MapTypeID`, `VectorTypeID`, and `StructTypeID` model composite types. `MapTypeID` exposes key and value type IDs; `VectorTypeID` exposes element type ID; `StructTypeID` wraps a `RecordTypeInfo` and exposes field metadata. All have equality/hash behavior where applicable.

`RecordTypeInfo` extends `Record` and stores schema metadata for a record name and fields. It provides constructors with and without a name, `getName`, `setName`, `addField`, `getFieldTypeInfos`, `getNestedStructTypeInfo(String)`, and record serialization/deserialization/compareTo methods. `org.apache.hadoop.record.meta.Utils.skip(RecordInput, String, TypeID)` is the visible metadata utility for skipping fields by type during deserialization/filtering.

### Security and Authorization

`AccessControlException` in `org.apache.hadoop.security` extends `org.apache.hadoop.fs.permission.AccessControlException` and provides default, message, and throwable constructors.

`User` and `Group` are simple identity value objects constructed from a name and exposing `getName`, `toString`, `hashCode`, and `equals`.

`SecurityUtil` provides static policy and subject helpers: `setPolicy(Policy)`, `getPolicy()`, and `getSubject(UserGroupInformation)`. Nested `SecurityUtil.AccessControlList` parses an ACL string, exposes `allAllowed()`, `getUsers()`, `getGroups()`, and the wildcard constant `WILDCARD_ACL_VALUE`.

`UnixUserGroupInformation` extends `UserGroupInformation` and implements a concrete user/group identity. It exposes constructors for current/default identity, explicit user plus groups, or string arrays; immutable creation; user and group accessors; Hadoop `Writable` `readFields`/`write`; configuration persistence via `saveToConf(Configuration,String)` and `readFromConf(Configuration,String)`; multiple `login` overloads; equality, hash, toString, and name access. Public constants include `DEFAULT_USERNAME`, `DEFAULT_GROUP`, and `UGI_PROPERTY_NAME`.

`UserGroupInformation` is the base user identity API. It exposes `getCurrentUGI()`, `setCurrentUGI(UserGroupInformation)`, `setCurrentUser(UserGroupInformation)`, abstract or overridable user/group/login APIs, `readFrom(DataInput)`, and a public static commons-logging `LOG`.

Authorization classes include `AuthorizationException`, `ConfiguredPolicy`, `ConnectionPermission`, `PolicyProvider`, `RefreshAuthorizationPolicyProtocol`, `Service`, and `ServiceAuthorizationManager`. `AuthorizationException` extends `AccessControlException` and suppresses or customizes stack trace APIs through visible `getStackTrace` and `printStackTrace` overloads. `ConfiguredPolicy` extends Java `Policy`, is constructed from a `Configuration` and `PolicyProvider`, implements `Configurable`, checks `implies`, returns permission collections, refreshes policy, and exposes `HADOOP_POLICY_FILE`. `ConnectionPermission` is a `Permission` keyed by protocol class. `PolicyProvider` exposes service definitions and policy provider config/default constants. `RefreshAuthorizationPolicyProtocol` defines `versionID` and `refreshServiceAcl()`. `Service` pairs a service key with a protocol class permission. `ServiceAuthorizationManager.authorize(Subject, ConnectionHeader, Configuration)` is the public service authorization check, with `SERVICE_AUTHORIZATION_CONFIG` as a configuration switch.

### Utility APIs

`CyclicIteration` iterates a `NavigableMap` starting from a supplied key. `Daemon` extends `Thread`, can wrap a `Runnable` and optional `ThreadGroup`, and exposes `getRunnable()`.

`DataChecksum` represents checksum state and configuration. Static factory overloads create checksums from type and bytes-per-checksum, from a header byte array and offset, or from a `DataInputStream`. It writes/returns headers, writes checksum values to byte arrays or `DataOutputStream`, compares checksum bytes, exposes checksum type/size/header sizing/value, resets, and updates from byte arrays or single bytes. Public constants include `HEADER_LEN`, `CHECKSUM_NULL`, `CHECKSUM_CRC32`, and `SIZE_OF_INTEGER`.

`DiskChecker` provides `mkdirsWithExistsCheck(File)` and `checkDir(File)`. Nested `DiskErrorException` and `DiskOutOfSpaceException` are `IOException` subclasses with message constructors.

`GenericOptionsParser` parses Hadoop generic command-line options. Constructors accept `Options`, `Configuration`, and argument arrays in several combinations. It exposes remaining application args, resulting `Configuration`, commons-cli `CommandLine`, libjar URLs, and `printGenericCommandUsage(PrintStream)`.

`GenericsUtil` exposes type/array helpers: `getClass(T)`, and `toArray` overloads for lists or arrays. `HeapSort`, `QuickSort`, and `MergeSort` implement `IndexedSorter`-style or comparator-based sorting: `HeapSort` and `QuickSort` have whole/ranged `sort(IndexedSortable,...)` methods, while `MergeSort` is constructed from a `Comparator` and exposes `mergeSort(Object[], Object[], int, int)`.

`HostsFileReader` manages include/exclude host files. It is constructed from include and exclude file names, can `refresh()`, return included and excluded host sets, update individual file names, and update both file names. This is a daemon configuration integration point for host admission/exclusion lists.

`IndexedSortable` and `IndexedSorter` are small sorting interfaces: sortable objects compare and swap by index, while sorters provide two `sort` overloads, including one with explicit start/end.

`LineReader` reads lines from an `InputStream`, with constructors for default buffer, explicit buffer size, or `Configuration`. It exposes `close()` and `readLine(Text)` overloads with max line length and max bytes to consume. This is a text input primitive for Hadoop readers.

`MemoryCalculatorPlugin` extends `Configured` and defines virtual/physical memory access plus static `getMemoryCalculatorPlugin(Class<? extends MemoryCalculatorPlugin>, Configuration)`. `LinuxMemoryCalculatorPlugin` implements physical and virtual memory size access for Linux and has a `main` method.

`NativeCodeLoader` exposes native library load status and a mutable static load-native-libraries flag. `PlatformName` returns the platform name and has a `main`. `PrintJarMainClass` prints a jar's main class from `main`.

`PriorityQueue` is an abstract heap-like queue: subclasses implement `lessThan(Object,Object)`, then use `initialize`, `put`, bounded `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.

`ProcfsBasedProcessTree` represents a Linux procfs process tree rooted at a pid. It supports construction with pid and optional procfs dir, sigkill interval configuration, availability checks, tree refresh via `getProcessTree()`, liveness checks, destroy/kill behavior, cumulative virtual memory queries with and without age, pid-file parsing, `toString`, and `DEFAULT_SLEEPTIME_BEFORE_SIGKILL`.

`ProgramDriver` registers named command classes through `addClass(String, Class, String)` and dispatches via `driver(String[])`. `Progress` models nested progress phases with weighted and unweighted `addPhase`, `startNextPhase`, `phase`, `complete`, `set`, `get`, status setting, and `toString`. `Progressable.progress()` is the callback used by long-running operations to report liveness.

`ReflectionUtils` instantiates/configures objects and copies writables: `setConf`, `newInstance(Class, Configuration)`, contention tracing toggles, thread info printing/logging, `getClass(T)`, `copy(Configuration, T, T)`, and `cloneWritableInto(Writable, Writable)`.

`RunJar` exposes `unJar(File, File)` and `main(String[])`. `ServletUtil` supports servlet HTML output via `initHTML`, request parameter extraction, `htmlFooter`, percentage graph overloads, and `HTML_TAIL`.

`Shell` is the base shell-command wrapper. It exposes OS command constants/helpers for users, groups, permissions, ownership, group changes, ulimit memory, Windows detection, environment/working-directory setters, `run()`, abstract `getExecString()` and `parseExecResult(BufferedReader)`, process and exit-code getters, and static `execCommand` overloads. Nested `Shell.ExitCodeException` carries a command exit code. Nested `Shell.ShellCommandExecutor` executes a supplied command array, optional working directory, and optional environment, then exposes `execute`, command string, parsed output, `getOutput`, and `toString`.

`StringUtils` is a large general utility surface. In this chunk it includes exception stringification, simple hostname extraction, human-readable integer formatting, percent formatting, array joining, byte-to-hex and hex-to-byte conversion, URI/path conversion, time formatting, comma-separated string collection helpers, escaped splitting and `findNext`, escape/unescape overloads, hostname fallback, startup/shutdown logging, HTML escaping, byte-length descriptions, and synchronized two-decimal formatting. Public constants are `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`. Nested `StringUtils.TraditionalBinaryPrefix` is an enum with `KILO`, `MEGA`, `GIGA`, `TERA`, `PETA`, and `EXA`, public final `value` and `symbol` fields, Java enum helpers, `valueOf(char)`, and `string2long(String)`.

`Tool` extends `Configurable` and defines `run(String[] args) throws Exception`. `ToolRunner` begins in this chunk with a public constructor and two static `run` overloads. The complete first overload, `run(Configuration, Tool, String[])`, parses generic Hadoop arguments, creates or uses a configuration, installs the modified configuration on the tool, and returns the tool's exit code. The second overload `run(Tool, String[])` begins here and is documented as equivalent to `run(tool.getConf(), tool, args)`, but its XML entry continues beyond this range.

## Control Flow and Behavioral Contracts

Record serialization follows a structured start/read-or-write/end flow. Generated `Record` implementations call a `RecordOutput` to write each field with optional tags, or a `RecordInput` to read them back. Vectors and maps use `Index` as the deserialization cursor. CSV and XML implementations provide format-specific encoding while preserving the same typed method contract. `Record.write(DataOutput)` and `readFields(DataInput)` adapt generated records to Hadoop `Writable` persistence.

Raw comparison flow uses `RecordComparator.define` to register an optimized comparator for a record class. Hadoop sort/shuffle paths can then compare serialized byte ranges directly through `compare(byte[],...)`, avoiding full object materialization when an optimized implementation exists.

Record compiler flow starts from `Rcc` parsing an IDL input stream/reader. Parser methods construct model objects such as `JFile`, `JRecord`, `JField`, `JMap`, and `JVector`; `JFile.genCode` emits target-language source into a destination directory. `RccTask` wraps the same flow for Ant builds, with fail-on-error behavior controlling whether compiler failures stop the build.

Generated parser flow is stateful and token-driven. `SimpleCharStream` buffers characters and tracks line/column locations, `RccTokenManager` converts characters into `Token` instances according to lexical states and token constants, and `Rcc` consumes tokens into grammar productions. ReInit overloads reset this state for new input without constructing a new parser.

Record metadata flow carries type information alongside data. `RecordTypeInfo` serializes/deserializes schema-like field descriptors, composite `TypeID` subclasses describe nested vector/map/struct fields, and metadata `Utils.skip` can skip a field in a `RecordInput` based on its `TypeID`. This supports schema filtering and compatible deserialization when field sets differ.

Security identity flow stores a current `UserGroupInformation`, with concrete Unix user/group information capable of being written to `DataOutput`, read from `DataInput`, and persisted in `Configuration`. ACL flow parses users/groups from a string and supports a wildcard all-allowed case. Authorization flow maps services to `ConnectionPermission`, installs a configured Java `Policy`, and checks a caller `Subject` plus RPC connection header against service ACLs.

Utility control flows include:

- checksum factories read type/header metadata, then `update`, `writeValue`, and `compare` operate over stream or byte-array payloads;
- disk checks ensure a directory exists and is usable, throwing typed IO exceptions for disk errors or space exhaustion;
- generic option parsing consumes framework options, mutates `Configuration`, and preserves remaining args for applications;
- sorters manipulate caller-provided `IndexedSortable` objects only through `compare` and `swap`;
- host-file readers refresh include/exclude sets from filesystem paths;
- line readers consume bounded line bytes into Hadoop `Text`;
- shell executors build command arrays, run processes, parse output, capture exit code/output, and throw `ExitCodeException` on failures;
- `ToolRunner` parses generic Hadoop CLI options, sets the tool configuration, invokes `Tool.run`, and propagates the integer exit code.

`StringUtils` escaping flow is a round trip: escape separators before joining or storing values, split on unescaped separators, then unescape tokens. Time-formatting flow separates raw duration display from date-with-difference display. `TraditionalBinaryPrefix.string2long` trims input, resolves an optional final binary suffix case-insensitively, and multiplies the numeric part by the prefix value.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. It does not contain method bodies, but it fixes the public names, signatures, exceptions, and documentation that downstream compatibility checks compare.

Record APIs are persistence-sensitive. `Record.write/readFields`, `RecordInput/RecordOutput`, `Utils` variable-length integer helpers, `DataChecksum` headers, and record metadata serialization all influence bytes stored in files, RPC payloads, or job metadata. Changes to type tags, variable-length encoding, comparator byte ordering, or schema metadata can break cross-version reads.

Compiler/parser classes are stateful while parsing. `Rcc`, `RccTokenManager`, and `SimpleCharStream` expose mutable token, stream, buffer, position, and lexical state fields. They also have reset methods, so callers may reuse parser instances. `RccTask` has Ant task configuration state: language, source files, destination, filesets, and fail-on-error policy.

Security APIs carry process and configuration state. `UserGroupInformation` has current-user state, `UnixUserGroupInformation` can be saved to and restored from `Configuration`, `SecurityUtil` can install a process-wide Java `Policy`, and `ConfiguredPolicy.refresh()` reloads policy-derived permissions. Authorization manager behavior depends on configuration flags and policy provider services.

Many utility classes deliberately mutate caller-visible or process state. `ToolRunner` installs a parsed `Configuration` on a `Tool`; `GenericOptionsParser` returns a modified configuration and remaining args; `HostsFileReader.refresh()` replaces host sets from files; `Shell` updates environment/working directory and owns a `Process`; `ShellCommandExecutor` captures command output; `Progress` updates nested progress values and status; `NativeCodeLoader.setLoadNativeLibraries` changes global native-load behavior; `ReflectionUtils.copy` and `cloneWritableInto` mutate target writables.

Other utilities are mostly stateless: string formatting/escaping, byte-array search/hex conversion, `GenericsUtil`, platform/version helpers, and sorting implementations that operate through caller-supplied data structures. Even stateless helpers can affect persisted configuration strings, logs, servlet HTML, and CLI output because their formatting is user-visible.

## Dependencies and Integration Points

Record APIs integrate with Hadoop `WritableComparable`, `WritableComparator`, `DataInput`, `DataOutput`, streams, `Buffer`, `ArrayList`, and `TreeMap`. XML and CSV record formats integrate at stream boundaries. Metadata types integrate with `RecordInput` and generated record classes.

Record compiler APIs integrate with Ant (`org.apache.tools.ant.Task`, filesets), JavaCC-generated parser components, Java IO streams/readers, and generated source output directories. The grammar token constants and parser methods are a build-time contract for the record IDL compiler.

Security APIs integrate with Java security (`Policy`, `Permission`, `PermissionCollection`, `Subject`), Hadoop `Configuration`, Hadoop IPC connection headers, commons logging, and filesystem permission exceptions. `RefreshAuthorizationPolicyProtocol` is an RPC protocol surface for refreshing service ACLs without restarting daemons.

Utility APIs integrate broadly: commons-cli for generic options; Hadoop `Configuration`, `Path`, `Text`, and `Writable`; servlet request/response types; Java process execution; procfs on Linux; native library loading; jar inspection; thread and reflection APIs; Apache Commons Logging; and web UI HTML helpers.

`Tool` and `ToolRunner` are central MapReduce/Hadoop CLI integration points. Applications implement `Tool`, usually via `Configured`, delegate framework option parsing to `ToolRunner`, then use the resulting `Configuration` to configure jobs or administrative commands.

## Risks and Compatibility Notes

This chunk has partial boundaries. It starts inside `CsvRecordInput`, so earlier methods and the class header are in the previous slice. It ends inside `ToolRunner`, so the rest of `run(Tool,String[])`, any later `ToolRunner` methods, and closing class/package markers are in the next slice. The merge lane should reconcile adjacent chunks for complete per-file reporting.

Exact implementation behavior is not visible. Null handling, input validation, synchronization beyond XML flags, stream ownership, exception message text, performance, and platform-specific fallbacks require Java source inspection if needed.

Record serialization is highly compatibility-sensitive. Field tag handling, start/end marker ordering, vector/map index semantics, variable-length integer encoding, byte comparisons, XML/CSV escaping, and record comparator registration can all affect persisted data, sort order, and generated-record interoperability.

Record metadata risks include mismatched `TypeID` equality/hash behavior, incorrect composite type descriptors, schema-skipping bugs, and `RecordTypeInfo` serialization changes. These APIs are intended to help tolerate schema evolution, so regressions can silently misread fields.

Generated parser and compiler APIs expose mutable public fields and JavaCC internals. Reuse via `ReInit`, lexical-state switching, line/column tracking, and token linking are common sources of off-by-one and stale-state bugs. Public parser method names and token ids are compatibility surfaces even if they look generated.

Security and authorization APIs have high operational risk. ACL wildcard parsing, user/group equality, current-user state, configuration persistence, service key mapping, Java `Policy` refresh, and `AuthorizationException` stack trace behavior can affect daemon access control and diagnostics. Historical UGI serialization also matters for interoperability with older Hadoop components.

`DataChecksum` must preserve header layout, checksum type ids, bytes-per-checksum semantics, and comparison behavior. Any mismatch can cause false corruption reports or missed corrupt data.

`Shell`, `ProcfsBasedProcessTree`, `LinuxMemoryCalculatorPlugin`, and `DiskChecker` are platform-sensitive. Process-tree killing, procfs parsing, command arrays, Windows flags, permissions commands, environment handling, and disk-space detection depend on OS behavior and should be tested under supported platforms.

`StringUtils` is compatibility-sensitive because its output enters configuration files, logs, web UIs, and CLI parsing. Edge cases include escaped separators, trailing escape characters, odd-length hex strings, malformed URIs, negative time differences, zero sentinel timestamps, HTML escaping, binary-prefix overflow, and case-insensitive prefix symbols.

`ToolRunner` and `GenericOptionsParser` must preserve argument ordering, remaining-argument calculation, libjars handling, configuration mutation, exception propagation, and exit-code propagation. CLI tools often depend on these exact semantics.

## Test Signals

JDiff-level checks should assert this XML slice remains well formed within the full file, preserves every visible class/interface boundary, method signature, parameter type/name, declared exception, field type/modifier, visibility, static/final/abstract/synchronized/native flag, deprecation state, and Javadoc block.

Record I/O tests should cover CSV and XML primitive round trips, strings and buffers, record start/end tags, nested records, empty and non-empty vectors/maps, index iteration termination, malformed input, `IOException` propagation, and compatibility between generated `Record.write/readFields` and direct `RecordInput/RecordOutput` serialization.

Record comparator and encoding tests should cover variable-length int/long boundaries, float/double read/write, raw byte comparison ordering, comparator registration through `RecordComparator.define`, and sorting serialized records without deserialization.

Record compiler tests should run `Rcc.driver` and `RccTask` over simple and nested IDL files, includes, modules, all primitive types, maps, vectors, buffers, generated-code destination handling, fail-on-error behavior, parse errors with useful locations, lexical errors, parser `ReInit` reuse, and token stream line/column tracking.

Record metadata tests should serialize/deserialize `RecordTypeInfo`, compare primitive and composite `TypeID`s, hash equivalent descriptors consistently, retrieve nested struct info, add fields in stable order, and skip unknown fields by `TypeID`.

Security tests should cover user/group equality and string forms, UGI read/write and configuration save/read, current UGI mutation, login overload behavior under available system accounts, ACL parsing for users, groups, whitespace, empty ACLs, and wildcard ACLs, configured policy permission implication, service permission mapping, authorization success/failure, refresh protocol invocation, and sanitized `AuthorizationException` stack traces.

Utility tests should cover checksum header round trips and data comparisons, disk directory creation and failure cases, generic option parsing with `-conf`, `-D`, `-fs`, `-jt`, `-libjars`, remaining args, host include/exclude refresh, line reading with long lines and byte limits, memory plugin fallback and Linux procfs parsing, native-loader flags, priority queue ordering, progress phase aggregation, reflection new-instance/config/copy behavior, jar main-class extraction, servlet HTML helpers, shell command success/failure/output/environment/working directory, process-tree liveness/destroy, and platform-specific branches.

`StringUtils` tests should cover exception stringification, hostname simplification, human-readable integers, percentages, array joining, hex conversion including invalid inputs, URI/path conversions, positive/zero/negative time formatting, escaped split/findNext/escape/unescape round trips, HTML escaping, byte descriptions, two-decimal formatting synchronization, binary-prefix parsing for all symbols and cases, invalid suffixes, negative values, whitespace, and overflow-adjacent values.

`Tool` and `ToolRunner` tests should use a small `Tool` implementation to assert generic option parsing, configuration injection, use of null or preexisting configurations, delegation from `run(Tool,String[])`, preservation of command-specific args, return-code propagation, and checked exception propagation.
