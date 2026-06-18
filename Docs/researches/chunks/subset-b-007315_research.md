# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.0.xml lines 25037-31420

## Chunk Scope

This chunk is a large middle segment of the generated JDiff public API snapshot for Hadoop 0.20.0. It is XML API metadata, not Java implementation source. The range starts inside the tail of `org.apache.hadoop.record.compiler.generated.ParseException`, completes the generated record-compiler parser package, then covers record metadata, security and service-authorization APIs, a broad part of `org.apache.hadoop.util`, Bloom filter and hash utilities, and the beginning of the legacy `org.apache.hadoop.mapred` package through `Counters.sum`.

The XML captures public compatibility surface: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, modifiers, visibility, deprecation state, and embedded Javadoc. Control flow, state, persistence, and risk notes below are therefore inferred from signatures and documentation rather than method bodies.

## Purpose

The covered API surface is cross-cutting Hadoop common infrastructure:

- generated JavaCC classes for the record compiler (`Rcc`, token manager, token stream, parse and lexical errors);
- record I/O metadata (`TypeID`, `RecordTypeInfo`, map/vector/struct type descriptors, and skip utilities);
- user/group identity and service-level authorization (`UserGroupInformation`, ACLs, policies, permissions, refresh protocol);
- shared utility classes for checksums, disk validation, generic CLI parsing, sorting, shell execution, process-tree management, progress tracking, reflection, JAR execution, strings, version metadata, and XML transforms;
- probabilistic data structures and non-cryptographic hashing (`BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, `RetouchedBloomFilter`, `HashFunction`, `JenkinsHash`, `MurmurHash`);
- early legacy MapReduce client status/counter APIs (`ClusterStatus`, start of deprecated `Counters`).

As a JDiff artifact, this chunk is mainly useful for compatibility research: it shows which APIs were public in 0.20.0, which APIs were synchronized or abstract, which exceptions were declared, and which contracts were explicitly documented.

## Important APIs and Types

### `org.apache.hadoop.record.compiler.generated`

The chunk begins with fields and documentation from `ParseException`. The visible fields are `specialConstructor`, `currentToken`, `expectedTokenSequences`, `tokenImage`, and `eol`. They are part of JavaCC parse-error reporting: the exception stores the last successfully consumed token, expected token sequences, token images from the generated constants interface, and machine-specific line separators used in messages.

`Rcc` is the generated record compiler parser. It implements `RccConstants` and can be constructed from `InputStream`, `InputStream` plus encoding, `Reader`, or an existing `RccTokenManager`. Important parser entry points are `Input()`, `Include()`, `Module()`, `ModuleName()`, `RecordList()`, `Record()`, `Field()`, `Type()`, `Map()`, and `Vector()`, returning compiler model objects such as `JFile`, `JRecord`, `JField`, `JType`, `JMap`, and `JVector`. These parser methods declare `ParseException`. The class also exposes `main`, `usage`, `driver(String[])`, parser reuse via several `ReInit` overloads, token access via `getNextToken()` and `getToken(int)`, and `generateParseException()`.

`RccConstants` is the generated token constant interface. It defines token IDs for `EOF`, IDL keywords (`MODULE_TKN`, `RECORD_TKN`, `INCLUDE_TKN`, primitive type tokens, `VECTOR_TKN`, `MAP_TKN`), punctuation (`LBRACE_TKN`, `RBRACE_TKN`, `LT_TKN`, `GT_TKN`, `SEMICOLON_TKN`, `COMMA_TKN`, `DOT_TKN`), string/identifier tokens, lexical states (`DEFAULT`, `WithinOneLineComment`, `WithinMultiLineComment`), and `tokenImage`.

`RccTokenManager` is the lexer. It implements `RccConstants`, is constructed with a `SimpleCharStream` and optionally an initial lexical state, can switch lexical state with `SwitchTo(int)`, can be reused with `ReInit`, and emits tokens through `getNextToken()`. Public/static lexer metadata includes `jjstrLiteralImages`, `lexStateNames`, and `jjnewLexState`; mutable lexer state includes `debugStream`, `input_stream`, and `curChar`.

`SimpleCharStream` is the generated ASCII character stream. It supports `Reader` and `InputStream` constructors with start-line/start-column/buffer-size and optional encoding, buffer expansion/fill, `BeginToken()`, `readChar()`, `backup(int)`, line/column tracking getters, multiple `ReInit` overloads, `GetImage()`, `GetSuffix(int)`, `Done()`, and `adjustBeginLineColumn(int, int)`. Its fields expose buffer positions, line/column arrays, current line/column, CR/LF flags, the underlying `Reader`, buffer contents, unread count, and tab size.

`Token` is the generated token object with `kind`, source positions (`beginLine`, `beginColumn`, `endLine`, `endColumn`), `image`, `next`, and `specialToken`. `newToken(int)` is a factory hook for token subclasses, and `toString()` returns the token image.

`TokenMgrError` is the generated lexical error type. It exposes constructors for default, message/reason, and detailed lexical error state; `addEscapes(String)` and `LexicalError(...)` build escaped diagnostic text; `getMessage()` returns the final message.

### `org.apache.hadoop.record.meta`

`FieldTypeInfo` pairs a field ID/name with a `TypeID`, exposing `getTypeID()`, `getFieldID()`, `equals(Object)`, `equals(FieldTypeInfo)`, and `hashCode()`.

`TypeID` represents base record-I/O types. It exposes shared constants for basic types (`BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, `StringTypeID`), a protected `typeVal`, `getTypeVal()`, equality, and hash code. Nested static class `TypeID.RIOType` defines byte constants for `BOOL`, `BUFFER`, `BYTE`, `DOUBLE`, `FLOAT`, `INT`, `LONG`, `MAP`, `STRING`, `STRUCT`, and `VECTOR`.

`MapTypeID`, `VectorTypeID`, and `StructTypeID` describe compound record types. `MapTypeID` stores key and value `TypeID`s; `VectorTypeID` stores an element `TypeID`; `StructTypeID` wraps a `RecordTypeInfo` and exposes its field metadata.

`RecordTypeInfo` extends `org.apache.hadoop.record.Record`. It stores record type metadata, has empty and named constructors, and exposes `getName()`, `setName(String)`, `addField(String, TypeID)`, `getFieldTypeInfos()`, `getNestedStructTypeInfo(String)`, `serialize(RecordOutput, String)`, `deserialize(RecordInput, String)`, and `compareTo(Object)`. The Javadoc states it is for reading/writing type information rather than normal ordering.

`Utils.skip(RecordInput, String, TypeID)` skips serialized bytes based on a type descriptor, making it a compatibility helper for forward/backward record decoding.

### `org.apache.hadoop.security`

`AccessControlException` extends the filesystem permission exception and provides default, message, and cause constructors. The default constructor is explicitly needed for unwrapping from `RemoteException`.

`User` and `Group` are simple `java.security.Principal` implementations with name, `toString`, equality, and hash code behavior. They are building blocks for `Subject` principals.

`SecurityUtil` exposes `setPolicy(Policy)`, `getPolicy()`, and `getSubject(UserGroupInformation)`. Its nested `AccessControlList` parses ACL strings and exposes `allAllowed()`, `getUsers()`, `getGroups()`, and public wildcard constant `WILDCARD_ACL_VALUE`.

`UserGroupInformation` is an abstract `Writable` and `Principal`. It exposes current-thread identity through `getCurrentUGI()`, deprecated `setCurrentUGI(UserGroupInformation)`, test/exceptional `setCurrentUser(UserGroupInformation)`, abstract `getUserName()` and `getGroupNames()`, static `login(Configuration)`, static `readFrom(Configuration)`, and public logger `LOG`.

`UnixUserGroupInformation` is the concrete Unix implementation. It has constructors for empty, user plus groups, and string-array forms; supports `createImmutable(String[])`; implements `getGroupNames()`, `getUserName()`, `readFields(DataInput)`, `write(DataOutput)`, `saveToConf(Configuration, String)`, `readFromConf(Configuration, String)`, and several `login` overloads. Public constants include `DEFAULT_USERNAME`, `DEFAULT_GROUP`, and `UGI_PROPERTY_NAME`.

### `org.apache.hadoop.security.authorize`

`AuthorizationException` extends Hadoop `AccessControlException` and deliberately suppresses stack traces for security. It provides constructors plus overrides for `getStackTrace()` and all `printStackTrace` forms.

`ConfiguredPolicy` extends `java.security.Policy` and implements `Configurable`. It is constructed from a `Configuration` and `PolicyProvider`, exposes `getConf()`, `setConf(Configuration)`, `implies(ProtectionDomain, Permission)`, `getPermissions(ProtectionDomain)`, `refresh()`, and `HADOOP_POLICY_FILE`. The Javadoc frames it as a configuration-backed policy for service-level authorization.

`ConnectionPermission` is a `Permission` representing permission to connect to a service protocol class. It implements equality, `getActions()`, hash code, `implies(Permission)`, and `toString()`.

`PolicyProvider` is an abstract source of service definitions. It exposes abstract `getServices()`, configuration key `POLICY_PROVIDER_CONFIG`, and `DEFAULT_POLICY_PROVIDER` with no services.

`RefreshAuthorizationPolicyProtocol` extends `VersionedProtocol`, has `versionID` set to initial version semantics, and exposes `refreshServiceAcl()` for live policy refresh.

`Service` binds a service configuration key to a required `Permission`. It exposes `getServiceKey()` and `getPermission()`.

`ServiceAuthorizationManager.authorize(Subject, Class)` is the central static authorization check for an incoming protocol request. It can throw `AuthorizationException`; `SERVICE_AUTHORIZATION_CONFIG` controls service-level authorization.

### `org.apache.hadoop.util`

The `org.apache.hadoop.util` segment is broad:

- `CyclicIteration` creates an `Iterable` over a `NavigableMap` that begins after a supplied key and wraps from the last entry to the first.
- `Daemon` is a `Thread` subclass whose constructors create daemon threads and which exposes the wrapped `Runnable`.
- `DataChecksum` implements `java.util.zip.Checksum` for DFS data transfer checksums. It has factories from type/bytes-per-checksum, serialized header bytes, or `DataInputStream`; writes headers and current values to streams or buffers; compares stored checksum bytes; exposes checksum type, size, bytes-per-checksum, bytes represented by the current sum, header length, current value, reset, and update operations. Public constants include `HEADER_LEN`, `CHECKSUM_NULL`, `CHECKSUM_CRC32`, and `SIZE_OF_INTEGER`.
- `DiskChecker` provides `mkdirsWithExistsCheck(File)` and `checkDir(File)`, plus `DiskErrorException` and `DiskOutOfSpaceException`.
- `GenericOptionsParser` parses generic Hadoop CLI options, with constructors for caller options, default options, and mutable `Configuration`. It exposes remaining args, modified configuration, Commons CLI `CommandLine`, `getLibJars(Configuration)`, and generic usage printing.
- `GenericsUtil` exposes class inference and array conversion helpers.
- `HeapSort` and `QuickSort` implement `IndexedSorter`; `IndexedSortable` supplies `compare(int,int)` and `swap(int,int)`, and `IndexedSorter` supplies `sort` overloads with optional progress callbacks.
- `HostsFileReader` manages include/exclude host files with refresh, getters, setters, and filename updates.
- `LineReader` reads lines from an `InputStream` into `Text` with overloads that cap bytes or line length, and is `Closeable` through `close()`.
- `LinuxMemoryCalculatorPlugin` and abstract/configured `MemoryCalculatorPlugin` expose virtual and physical memory sizes and plugin selection through configuration.
- `MergeSort` provides comparator-backed merge sorting.
- `NativeCodeLoader` reports and controls native library loading through `isNativeCodeLoaded()`, `getLoadNativeLibraries(Configuration)`, and `setLoadNativeLibraries(Configuration, boolean)`.
- `PlatformName` and `PrintJarMainClass` expose small command-line diagnostics.
- `PriorityQueue` is an abstract heap-like queue with `lessThan(Object,Object)`, `initialize(int)`, `put`, `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.
- `ProcfsBasedProcessTree` reads Linux procfs process trees by root PID, supports SIGKILL delay configuration, availability checks, refreshing process-tree state, liveness checks, destruction, cumulative virtual memory, PID-file parsing, and string rendering.
- `ProgramDriver` maps command names to main classes via `addClass(String, Class, String)` and dispatches with `driver(String[])`.
- `Progress` models hierarchical phased progress with `addPhase`, `startNextPhase`, `phase`, `complete`, `set(float)`, `get()`, `setStatus(String)`, and `toString()`. `Progressable` is the small callback interface with `progress()`.
- `ReflectionUtils` integrates reflection with Hadoop configuration and writable cloning/copying: `setConf(Object, Configuration)`, `newInstance(Class, Configuration)`, contention tracing controls, thread-info printing/logging, `getClass(T)`, `copy(Configuration, T, T)`, and `cloneWritableInto(Writable, Writable)`.
- `RunJar` can unjar a `File` into a directory and run a JAR main through `main(String[])`.
- `ServletUtil` provides servlet/web UI helpers: `initHTML(ServletResponse, String)`, `getParameter(ServletRequest, String)`, `htmlFooter()`, percentage-graph overloads, and `HTML_TAIL`.
- `Shell` is an abstract command runner with platform command helpers, environment and working-directory setters, rate-limited `run()`, abstract `getExecString()` and `parseExecResult(BufferedReader)`, process/exit-code access, static `execCommand` overloads, command constants, platform flag `WINDOWS`, and public logger. Nested `ExitCodeException` carries an exit code; nested `ShellCommandExecutor` runs a string-array command and exposes output and command rendering.
- `StringUtils` exposes exception stringification, hostname simplification, human-readable numbers, percent formatting, array/string conversion, byte/hex conversion, URI/path conversions, elapsed time formatting, comma-separated splitting and escaping, hostname fallback, startup/shutdown logging, HTML escaping, byte-size descriptions, and decimal limiting. Public constants include `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`.
- `StringUtils.TraditionalBinaryPrefix` is an enum for binary units KILO through EXA with public final `value` and `symbol`, `valueOf(char)`, and `string2long(String)`.
- `Tool` is the standard configurable command-line interface with `run(String[])`; `ToolRunner` parses generic Hadoop arguments, installs the modified configuration on the tool, invokes `Tool.run`, and prints generic usage.
- `UTF8ByteArrayUtils` scans UTF-8 byte arrays for bytes, byte sequences, and nth occurrences without converting to `String`.
- `VersionInfo` returns Hadoop build metadata (`version`, `revision`, `date`, `user`, `url`, combined build version) and has `main`.
- `XMLUtils.transform(InputStream, InputStream, Writer)` applies an XSLT stylesheet to XML and declares standard transformer exceptions.

### `org.apache.hadoop.util.bloom`

`Filter` is the abstract `Writable` base class for Bloom-like filters. It stores `vectorSize`, `HashFunction hash`, `nbHash`, and `hashType`, has protected constructors, abstract `add(Key)`, `membershipTest(Key)`, logical `and`, `or`, `xor`, and `not`, plus convenience `add` overloads for byte arrays and strings, and shared `write/readFields` metadata serialization.

`BloomFilter` implements a standard bit-vector Bloom filter. It supports default construction for `readFields`, parameterized construction with vector size, hash count, and hash type, membership insertion/testing, logical operations, `toString`, `getVectorSize`, and `Writable` serialization.

`CountingBloomFilter` is final and uses counters rather than bits. It supports `add`, `delete`, membership tests, `approximateCount(Key)`, logical operations, rendering, and serialization. The Javadoc warns that inserting a same key more than 15 times can overflow filter positions and raise error rates.

`DynamicBloomFilter` grows by adding Bloom-filter rows when a row reaches a configured threshold. It has default and parameterized constructors, standard add/membership/logical operations, string rendering, and serialization.

`HashFunction` wraps the configured non-cryptographic hash implementation to produce multiple vector positions. It is constructed from vector size, number of hashes, and hash type; exposes `clear()` and `hash(Key)`.

`Key` implements `WritableComparable` and carries a byte-array key plus a weight. It has empty, byte-array, and byte-array-plus-weight constructors; `set`, `getBytes`, `getWeight`, weight increment overloads, equality, hash code, `write/readFields`, and `compareTo`.

`RemoveScheme` defines selection constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` for retouched Bloom filters.

`RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`. It allows known false positives to be recorded through multiple `addFalsePositive` overloads, then applies `selectiveClearing(Key, short)` to reduce false positives according to a scheme. It also serializes its extra false-positive state.

### `org.apache.hadoop.util.hash`

`Hash` is the abstract common API for non-cryptographic hashing. It exposes constants `INVALID_HASH`, `JENKINS_HASH`, and `MURMUR_HASH`; parsing from a name; reading configured hash type from `Configuration`; singleton lookup by type or configuration; convenience `hash(byte[])` and `hash(byte[], int)` overloads; and abstract `hash(byte[], int, int)`.

`JenkinsHash` implements Bob Jenkins lookup3-style 32-bit hashing. It has a singleton getter, `hash(byte[], int, int)`, and a `main(String[])` utility for hashing a file.

`MurmurHash` implements MurmurHash 2.0 ported to Java, with singleton getter and `hash(byte[], int, int)`.

### `org.apache.hadoop.mapred`

`ClusterStatus` implements `Writable` and captures JobTracker cluster status visible through `JobClient#getClusterStatus()`. It exposes task tracker counts, active and blacklisted tracker names, blacklisted count, task-tracker expiry interval, running map/reduce counts, max map/reduce capacity, JobTracker state, used heap memory, max heap memory, and `write/readFields`.

The chunk begins `Counters`, which is deprecated in favor of `org.apache.hadoop.mapreduce.Counters`. The visible class implements `Writable` and `Iterable`; most visible methods are synchronized. It exposes `getGroupNames()`, `iterator()`, `getGroup(String)`, `findCounter(Enum)`, `findCounter(String,String)`, deprecated `findCounter(String,int,String)`, increment methods by enum or group/name, `getCounter(Enum)`, `incrAllCounters(Counters)`, and the start of static `sum(Counters, Counters)`.

## Control Flow and Behavioral Contracts

The generated parser flow is input stream or reader -> `SimpleCharStream` -> `RccTokenManager` -> `Rcc` grammar entry points -> compiler model objects. `ParseException` and `TokenMgrError` represent parse and lexical failures. `ReInit` methods allow parser, lexer, and stream objects to be reused with new input, so callers must treat token/line/buffer state as mutable between parses.

Record metadata flow maps schema information into `TypeID` and `RecordTypeInfo` objects. Serialized record type information is written through `RecordOutput` and read through `RecordInput`; `Utils.skip` uses a `TypeID` to advance through serialized data without materializing values. Compound type equality recursively depends on child type descriptors.

Security identity flow starts from login or configuration loading into `UserGroupInformation`, translates UGI into a JAAS `Subject` through `SecurityUtil`, and then uses Java `Policy`/`Permission` objects and service definitions to authorize protocol access. Service authorization flow is configuration-controlled: `PolicyProvider` supplies services, `ConfiguredPolicy` loads policy from configuration, `ServiceAuthorizationManager.authorize` checks a `Subject` against a protocol class, and `RefreshAuthorizationPolicyProtocol.refreshServiceAcl` refreshes policy state.

Utility flows are mostly small, but several are infrastructure critical. `DataChecksum` serializes checksum headers, updates checksum state as bytes are processed, writes checksum values, and compares serialized checksum bytes. `GenericOptionsParser` and `ToolRunner` parse generic CLI options before tool-specific execution and mutate the tool's configuration. `Shell` builds an executable command, starts a process, parses output through subclass logic, stores process/exit state, and raises `ExitCodeException` for nonzero exits. `ProcfsBasedProcessTree` refreshes process-tree state from procfs before exposing liveness or memory totals.

Sorting flow is decoupled through index interfaces: sorters call `IndexedSortable.compare` and `swap`, optionally reporting through `Progressable`. `Progress` composes weighted phases and reports a cumulative float; callers advance phases or mark completion as subtasks finish.

Bloom filter flow hashes a `Key` through `HashFunction`, maps the resulting positions into a bit/counter matrix, and then tests future keys against those positions. Logical operations mutate `this` filter according to the Javadoc invariant. Dynamic filters choose an active row or create a new row when the configured row threshold is reached. Retouched filters add known false positives and selectively clear positions according to a removal scheme.

Hash selection flow maps configured strings or integer constants to singleton `Hash` implementations. Bloom utilities depend on stable hash output, vector sizing, number of hashes, and hash type for serialization compatibility.

MapReduce status flow is remote state snapshot -> `ClusterStatus` writable -> client getters. Counter flow is group/name or enum lookup -> counter creation/retrieval -> synchronized increments -> aggregation through `incrAllCounters` or `sum`.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent compatibility metadata. It does not include Java bodies or runtime values, but it records API contracts for Hadoop 0.20.0.

Generated parser classes are highly stateful. `Rcc` holds `token_source`, current `token`, and lookahead `jj_nt`; `RccTokenManager` holds the current stream, lexical state, debug stream, and current char; `SimpleCharStream` holds mutable buffers and source-position arrays. Reusing these objects through `ReInit` is an intentional state reset path.

Record metadata classes persist through Hadoop record I/O. `RecordTypeInfo.serialize/deserialize`, `TypeID` constants, compound type descriptors, and `Utils.skip` all affect schema evolution and the ability to read older or newer serialized records.

Security APIs persist identity and policy through configuration and thread-local/current-user state. `UnixUserGroupInformation.saveToConf/readFromConf`, `UserGroupInformation.getCurrentUGI/setCurrentUser`, Java `Policy` installation, configured ACLs, and live policy refresh are all state-bearing. `AuthorizationException` intentionally hides stack traces, which is a security side effect visible to diagnostics.

Several utility classes mutate or reflect external state. `DiskChecker` creates/checks directories; `HostsFileReader` reads host files and refreshes include/exclude sets; `Shell` launches OS processes and stores process/exit/output state; `RunJar.unJar` writes files; `NativeCodeLoader` controls configuration flags for native libraries; `ProcfsBasedProcessTree` sends termination signals and reads procfs; `ServletUtil` writes web responses; `XMLUtils.transform` writes transformed output.

`DataChecksum`, Bloom filters, `Progress`, `PriorityQueue`, and `Counters` hold mutable in-memory state and serialize parts of that state through `Writable` APIs. Bloom filters and keys persist their configuration and contents through `write/readFields`. `ClusterStatus` and `Counters` persist over Hadoop RPC or job history/status paths as writable data structures.

Many utility APIs are stateless static helpers (`StringUtils`, `UTF8ByteArrayUtils`, `VersionInfo`, hash singleton lookup), but they still shape persisted text, configuration, logs, diagnostics, and binary compatibility.

## Dependencies and Integration Points

The generated record compiler package integrates JavaCC-generated parser infrastructure with Hadoop record compiler model classes (`JFile`, `JRecord`, `JField`, `JType`, `JMap`, `JVector`) and Java IO streams/readers.

Record metadata depends on the older Hadoop record I/O interfaces (`Record`, `RecordInput`, `RecordOutput`) and Java collections. It is an integration layer between schema descriptors and serialized record streams.

Security APIs integrate with Hadoop configuration, Hadoop IPC (`RemoteException`, `VersionedProtocol`), Java security (`Principal`, `Subject`, `Policy`, `Permission`, `ProtectionDomain`, `PermissionCollection`), JAAS login, and filesystem permission exceptions.

Core utility dependencies include Commons CLI, Commons Logging, servlet request/response types, Hadoop `Configuration`, `Configured`, `Writable`, `WritableComparable`, `Text`, filesystem `Path`, Java IO, Java XML transform APIs, Java reflection, ZIP/JAR handling, process execution, procfs, and platform/native-code detection.

Bloom filters depend on Hadoop `Writable` serialization, `Key`, `HashFunction`, and `org.apache.hadoop.util.hash.Hash` implementations. Hash type constants and configuration parsing connect `org.apache.hadoop.util.hash` to Bloom filter serialization and behavior.

The legacy `mapred` APIs integrate with JobTracker/JobClient status paths and old MapReduce counters. `Counters` is explicitly deprecated in favor of the newer `org.apache.hadoop.mapreduce.Counters`, so compatibility must account for old and new APIs coexisting.

## Risks and Compatibility Notes

This chunk starts mid-`ParseException` and ends mid-`Counters`, so final per-file reconciliation needs adjacent chunks to avoid treating partial class coverage as complete.

Generated parser APIs expose many public mutable fields inherited from JavaCC output. Changing token constants, lexical state names, token image ordering, parser method return types, or `ReInit` behavior can break generated record compiler compatibility and error reporting.

`SimpleCharStream` is documented as ASCII-only. Supplying non-ASCII input or changing Unicode handling would affect parsing positions, token images, and error messages. Buffer expansion, backup, CR/LF, and tab-size behavior are off-by-one sensitive.

Record metadata equality and hash-code implementations are documented as basic and not necessarily optimized for hash-map keys. Any changes to `TypeID` constants, compound type equality, or serialized `RecordTypeInfo` shape risk breaking schema compatibility.

Security code is high-risk despite small signatures. `setCurrentUser` is documented as test/exceptional only; accidental production use can impersonate users. ACL parsing must preserve wildcard semantics. Suppressing stack traces in `AuthorizationException` is security-sensitive. Service policy refresh must update the active authorization view without weakening checks.

`DataChecksum` header format and checksum value serialization are wire-format sensitive for DFS data transfer. Type IDs, bytes-per-checksum, checksum size, reset behavior after writes, and comparison endianness are likely compatibility surfaces.

Shell/process utilities are platform-sensitive. Command arrays, environment mutation, working directory, timeout/rate behavior, Windows command constants, nonzero exit handling, and output parsing must be tested separately on supported OSes.

`ProcfsBasedProcessTree` is Linux/procfs-specific. PID parsing, process liveness, memory accounting, and staged termination depend on OS semantics and can race with process exit.

String, URI/path, byte/hex, escaping, and binary-prefix utilities are configuration-visible. Small edge-case changes can break persisted comma-separated lists, CLI arguments, HTML/log output, and numeric configuration values.

Bloom filters are probabilistic and serialization-sensitive. Hash type, vector size, number of hashes, counter overflow behavior in `CountingBloomFilter`, dynamic row thresholds, and retouched clearing schemes directly affect false positive/negative behavior. `CountingBloomFilter.delete` can underflow if misused, as noted by the approximate-count documentation.

`Hash`, `JenkinsHash`, and `MurmurHash` are explicitly non-cryptographic. They should not be used for security decisions. Changing singleton mapping, hash seeds, byte order, or length handling breaks persisted Bloom filters and partitioning-style uses.

`ClusterStatus` and `Counters` are old MapReduce wire/status APIs. `Counters` methods are synchronized, so removing synchronization would affect thread-safety assumptions. Deprecation toward `mapreduce.Counters` should not remove old methods while old clients still deserialize or call them.

## Test Signals

JDiff-level checks should verify that this XML range remains well formed across package transitions, preserves class/interface boundaries, and keeps public signatures, modifiers, deprecation text, declared exceptions, field types, implemented interfaces, and Javadoc blocks stable.

Parser tests should compile and parse representative record IDL files with modules, includes, primitive fields, maps, vectors, nested records, comments, strings, and malformed input. They should assert token positions, parse exception expected-token messages, lexical error escaping, `ReInit` reuse, and encoding constructor behavior.

Record metadata tests should round-trip `RecordTypeInfo` through `RecordOutput`/`RecordInput`, cover all `TypeID.RIOType` constants, compare equal and unequal map/vector/struct descriptors, skip serialized primitive and compound values, and verify nested struct lookup behavior.

Security tests should cover UGI login/read/write/config persistence, current-user thread behavior, ACL wildcard/user/group parsing, `SecurityUtil.getSubject`, service permission equality/implies behavior, configured policy refresh, authorization success/failure, stack-trace suppression, and remote-exception unwrapping for access-control exceptions.

Utility tests should include checksum header round trips and corruption detection; concurrent directory creation and disk-error cases; generic option parsing for `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`; sorter correctness through `IndexedSortable`; line reading with long lines and byte caps; memory plugin selection; native-loader flags; priority queue ordering; process-tree PID-file parsing, memory accounting, and destroy timing; `ProgramDriver` dispatch errors; progress phase weighting; reflection with configurable and writable objects; JAR unjar/main execution; servlet HTML helper escaping and percentage graphs; shell command success/failure, output capture, environment, working directory, and platform command helpers.

`StringUtils` tests should cover exception stringification, hostname simplification, human-readable numbers, percent formatting, array/string conversion, byte/hex round trips including invalid input, URI/path conversion, time formatting, comma escaping/splitting/unescaping including custom separators, HTML escaping, byte descriptions, decimal limiting, and binary prefix parsing including upper/lower-case suffixes and overflow-adjacent values.

Bloom/hash tests should cover adding and testing keys, false-positive tolerance, logical operations on compatible and incompatible filters, writable round trips, counting delete and approximate counts including overflow/underflow boundaries, dynamic row growth, retouched false-positive clearing schemes, `Key` weight/equality/serialization/comparison, configured hash type parsing, singleton selection, Jenkins and Murmur deterministic vectors, seed handling, and invalid hash type behavior.

MapReduce API tests should cover `ClusterStatus` writable round trips and getters for active/blacklisted trackers, task capacity, running tasks, memory, and JobTracker state. `Counters` tests should cover synchronized group/counter lookup, enum and string counters, deprecated ID-based lookup, increments, zero for missing counters, aggregate increments, `sum`, iteration, writable serialization, and compatibility with the newer `mapreduce.Counters` migration path.
