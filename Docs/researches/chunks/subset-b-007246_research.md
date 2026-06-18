# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.20.0.xml lines 25018-31507

## Scope

This chunk is a JDiff/API XML slice for Hadoop 0.20.0 common classes, plus a large embedded Record I/O package document. It covers:

- Hadoop Record I/O design, DDL syntax, generated language bindings, and binary/CSV/XML encodings.
- `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, `org.apache.hadoop.record.compiler.generated`, and `org.apache.hadoop.record.meta`.
- `org.apache.hadoop.security` and `org.apache.hadoop.security.authorize` public APIs.
- A broad section of `org.apache.hadoop.util` utilities.
- The beginning of `org.apache.hadoop.util.bloom` through `DynamicBloomFilter.write`.

Because the source is generated API documentation rather than Java implementation, control flow and persistence notes below are derived from the documented public contracts, method names, parameters, exceptions, and class relationships.

## Purpose

The first section documents Hadoop Record I/O as a translator-based serialization system. Users write a simple record DDL; the `rcc` compiler generates Java or C++ code for marshaling records to stream abstractions. Goals include common primitive/composite types, recursive composition, multi-language code generation, runtime support packages, multiple encodings, and forward/backward compatibility via optional fields, though optional fields are noted as planned rather than specified in this document. Non-goals include arbitrary C++ object serialization, complex structures such as trees/linked lists, indexing/compression/checksums, and dynamic object construction from XML schemas.

The API inventory then follows the generated and runtime support surfaces that make this system and Hadoop Common's utility/security layer usable: compiler model types, Ant integration, JavaCC parser artifacts, metadata/type identifiers, user/group/security policy helpers, command-line/runtime utilities, shell/process wrappers, checksum utilities, sort/progress helpers, string/XML utilities, and probabilistic membership filters.

## Important APIs, Types, and Functions

### Record I/O documentation and compiler APIs

- Record I/O supports primitive DDL types `byte`, `boolean`, `int`, `long`, `float`, `double`, `ustring`, and `buffer`; composite types are `record`, `vector<type>`, and `map<type,type>`.
- Generated code serializes composite fields sequentially. Vectors and maps include lengths in binary encodings; records are member sequences.
- DDL grammar has `include`, one `module`, and zero or more `class` declarations. Includes are recursive and expose types but do not force code generation for included files.
- C++ support is described around `hadoop::InStream`, `OutStream`, `RecordReader`, `RecordWriter`, and abstract `Record` with `type`, `signature`, `validate`, `serialize`, and `deserialize`.
- Java generation creates one `.java` file per record class, maps modules to Java packages, and generates getters/setters plus `equals`, `hashCode`, and `compareTo`.
- `org.apache.hadoop.record.compiler.CodeBuffer` is an indentation-aware `StringBuffer` wrapper.
- `Consts` exposes public constants for generated Record I/O symbol names such as record input/output, tags, and runtime type info variables.
- `JType` is the abstract base for supported Record I/O compiler types. Concrete subclasses model primitives and composites: `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`.
- `JField` is a thin wrapper around a record field; `JFile` is the top-level DDL container with filename, included files, and record list. Its important operation is `genCode(language, destDir, options)`, which emits code and throws `IOException`.
- `org.apache.hadoop.record.compiler.ant.RccTask` exposes Ant setters for `language`, `file`, `failonerror`, `destdir`, and nested `FileSet`s, then `execute()` invokes the record compiler. Build behavior is configurable: failures can either throw `BuildException` or be tolerated depending on `failonerror`.
- `org.apache.hadoop.record.compiler.generated.Rcc` is the JavaCC parser/driver. It has constructors for input streams, readers, and token managers; static `main`, `usage`, and `driver`; grammar entry points such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`; stream/token-manager `ReInit` methods; token accessors; and parse-exception generation.
- Parser support classes include `ParseException`, `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError`. These carry token IDs, lexical states, source line/column tracking, escaping helpers, and recoverable parser diagnostics.

### Record metadata APIs

- `FieldTypeInfo` pairs a field ID/name with a `TypeID`, with equality and hash behavior.
- `TypeID` represents primitive/basic record type identifiers and exposes shared constants such as `BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, and `StringTypeID`.
- `TypeID.RIOType` defines byte constants for supported IDL types: bool, buffer, byte, double, float, int, long, map, string, struct, and vector.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` for composite shapes, exposing constituent key/value/element/field metadata and equality based on nested type shape.
- `RecordTypeInfo` extends `org.apache.hadoop.record.Record` and stores record-name plus field metadata. It can add fields, return field metadata, find one-level nested struct metadata, and serialize/deserialize itself through `RecordOutput`/`RecordInput`.
- `org.apache.hadoop.record.meta.Utils.skip(RecordInput, tag, TypeID)` skips stream data based on a type identifier, which is central to schema-evolution or selective-read behavior.

### Security APIs

- `org.apache.hadoop.security.AccessControlException` extends the filesystem permission exception and has constructors for remote-exception unwrapping, messages, and causes.
- `Group` and `User` implement `java.security.Principal` semantics over group/user names with `getName`, `toString`, `hashCode`, and `equals`.
- `SecurityUtil` manages a global `java.security.Policy`, provides `getSubject(UserGroupInformation)`, and includes nested `AccessControlList`.
- `SecurityUtil.AccessControlList` parses ACL strings of the form `"user1,user2 group1,group2"` and supports wildcard all-access checks plus user/group set accessors.
- `UnixUserGroupInformation` extends `UserGroupInformation` and is writable/persistable. It stores a username and ordered groups where the first group is the default, supports immutable instances, serialization, config storage via comma-separated strings, config reads, and Unix login.
- `UserGroupInformation` is the abstract `Writable` holder for user and groups. It supports thread-local current UGI operations, current-user setup, username/group access, login, and config reads.
- `org.apache.hadoop.security.authorize.AuthorizationException` extends access control failure with intentionally suppressed/overridden stack trace printing behavior.
- `ConfiguredPolicy` bridges Hadoop `Configuration` and Java `Policy`, with `implies`, `getPermissions`, `refresh`, and `HADOOP_POLICY_FILE`.
- `ConnectionPermission` is a service/protocol connection permission.
- `PolicyProvider` supplies service definitions and exposes provider configuration constants/default provider.
- `RefreshAuthorizationPolicyProtocol.refreshServiceAcl()` is an RPC protocol for reloading active authorization policy; `versionID` marks the protocol version.
- `Service` binds a service configuration key to a protocol/interface permission.
- `ServiceAuthorizationManager.authorize(user, protocol)` enforces service-level authorization gated by `SERVICE_AUTHORIZATION_CONFIG`.

### Utility APIs

- `CyclicIteration` iterates a `NavigableMap` cyclically from a specified starting key.
- `Daemon` is a `Thread` subclass that always sets daemon status and exposes the runnable.
- `DataChecksum` creates and operates on DFS data-transfer checksums. It supports null and CRC32 types, header parsing from byte arrays or `DataInputStream`, header writing, checksum value writing to streams or buffers, checksum comparison, value/type/size accessors, reset, and update.
- `DiskChecker` validates local directories and creates directory trees with an existence check that tolerates concurrent creators; nested exceptions distinguish disk errors and out-of-space conditions.
- `GenericOptionsParser` parses standard Hadoop command-line options using Commons CLI. It modifies `Configuration`, returns remaining application args, exposes the parsed `CommandLine`, resolves `-libjars`, and prints generic usage. Supported options include `-conf`, `-D`, `-fs`, `-jt`, `-files`, `-libjars`, and `-archives`.
- `GenericsUtil` provides typed class discovery and list-to-array helpers.
- `IndexedSortable` and `IndexedSorter` abstract sorting over index-addressable data using `compare` and `swap`; `HeapSort` and `QuickSort` implement the sorter interface, and `MergeSort` provides array-index merge sorting.
- `HostsFileReader` maintains include/exclude host sets from files with synchronized refresh and filename update methods.
- `LineReader` reads lines from `InputStream` into Hadoop `Text`, handling `\n`, `\r`, `\r\n`, EOF, max line length, max bytes to consume, and configurable buffer size.
- `MemoryCalculatorPlugin` is an abstract configured plugin for physical/virtual memory sizing. `LinuxMemoryCalculatorPlugin` implements it for Linux and includes a test `main`.
- `NativeCodeLoader` reports whether native Hadoop code is loaded and controls whether native libraries may be used via configuration.
- `PlatformName`, `PrintJarMainClass`, `ProgramDriver`, and `RunJar` support platform identification, jar manifest/main-class discovery, multi-program dispatch, and Hadoop job jar launching/unpacking.
- `PriorityQueue` is an abstract heap-like queue where subclasses supply `lessThan`; it supports `initialize`, `put`, bounded `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`.
- `ProcfsBasedProcessTree` is Linux `/proc`-based process tree tracking. It refreshes tree state, tests availability/aliveness, destroys a process tree, reports cumulative virtual memory, reads PIDs from pid files, and stringifies tracked PIDs.
- `Progress` builds a tree of phases and leaf progress values, with named/weighted phases, current phase movement, completion, status, and aggregate progress. `Progressable.progress()` is the callback interface used by long-running operations.
- `ReflectionUtils` sets configuration on configurable objects, creates configured instances, toggles contention tracing, logs/prints thread dumps, copies `Writable`s through serialization, and clones writable state into existing instances.
- `ServletUtil` provides small servlet/JSP helpers for HTML headers/footers, request parameters, and percentage graph markup.
- `Shell` is an abstract command runner with interval gating, environment/working-directory setup, platform-specific helper command arrays, ulimit command construction, process/exit-code access, and static simple command execution. `Shell.ExitCodeException` adds exit status to `IOException`; `Shell.ShellCommandExecutor` stores small command output as-is.
- `StringUtils` covers exception stringification, host simplification, human-readable numbers, percentages, byte/hex conversion, URI/path conversion, time formatting, comma-separated string parsing, separator-aware escaping/unescaping, hostname discovery, startup/shutdown logging, HTML escaping, byte descriptions, and decimal limiting. Nested `TraditionalBinaryPrefix` parses suffixes from `k` through `e` into powers of 1024.
- `Tool` is the standard interface for Hadoop command-line applications that need generic options. `ToolRunner` parses generic options, injects configuration into the tool, invokes `Tool.run`, and can print generic usage.
- `UTF8ByteArrayUtils` finds bytes, byte sequences, and nth byte occurrences in UTF-8 byte arrays.
- `VersionInfo` exposes build version, revision, date, user, URL, and composed build version, with a `main` printer.
- `XMLUtils.transform` applies an XSLT stylesheet to XML input and writes transformed output.

### Bloom filter APIs

- `BloomFilter` extends `Filter` and implements standard Bloom set membership. It supports zero-arg construction for `readFields`, parameterized construction with vector size, hash count, and hash type, mutation with `add`, set operations `and`, `or`, `xor`, complement `not`, `membershipTest`, stringification, vector size access, and `Writable` serialization.
- `CountingBloomFilter` extends `Filter` and adds deletion plus approximate counts. Its documented counter bucket limit means adding the same key more than 15 times can overflow all associated positions and increase error rates; deletes can introduce underflow and possible false negatives in counts.
- `DynamicBloomFilter` extends `Filter`, adds row growth controlled by a per-row threshold `nr`, and exposes the same add/membership/set-operation/write surface in this chunk.

## Control Flow

Record I/O flow starts from a DDL file: `Rcc.driver/main` parse command-line arguments; `Rcc.Input` parses includes, module, and records; parser productions build `JFile`, `JRecord`, `JField`, and `JType` instances; then `JFile.genCode` dispatches language-specific generation into the destination directory. The Ant wrapper follows the same core path but obtains its inputs from a single file or nested `FileSet`s and applies Ant-style failure behavior.

Serialization flow for generated records is sequential and type-directed. Primitive values are encoded according to the chosen format; records serialize fields in declaration order; vectors and maps serialize size then elements/pairs in binary format. Runtime metadata flow uses `RecordTypeInfo` and `TypeID` to describe and serialize schema/type information, while `Utils.skip` allows a reader to consume unknown or unneeded fields based on metadata.

Security authorization flow is layered. UGI discovery or config loading produces a `UserGroupInformation`; `SecurityUtil.getSubject` maps UGI to JAAS subject; ACL strings and policy providers define access rules; `ConfiguredPolicy` and `ServiceAuthorizationManager.authorize` decide whether a user can access a protocol/service. The refresh protocol allows live service ACL reload without process restart.

Utility flows are mostly helper-oriented: command-line programs should enter through `ToolRunner.run`, which consumes Hadoop generic options before invoking application-specific `Tool.run`; shell wrappers build commands, run them with optional environment/working-directory, parse output, and surface exit codes; process tree and memory plugins query platform state; sorters repeatedly call caller-supplied indexed compare/swap operations.

Bloom filter flow is hash-driven: constructors define vector size, hash count, and hash implementation; `add` maps a key to hash positions and mutates internal state; membership checks query the same positions; logical operations combine compatible filters; writable methods persist or restore filter state.

## State and Persistence Behavior

- Record generated objects hold in-memory fields and can persist themselves through `RecordInput`/`RecordOutput` in binary, CSV, or XML forms. Encodings are part of compatibility: binary uses zero-compressed integers and UTF-8 normalized strings; CSV percent-escapes reserved bytes/chars; XML uses XML-RPC-like value elements with extra tags and escaping for disallowed string data.
- `RecordTypeInfo` persists schema/type metadata as a record. Its nested lookup is documented as only one level deep, so deeper nested-struct compatibility must not assume recursive discovery from this API.
- JavaCC parser objects keep mutable token-manager, current token, next token, lexical state, stream buffers, and line/column arrays. `ReInit` allows reuse with new streams/managers.
- UGI can be serialized to `DataOutput` with a format marker and can be stored in `Configuration` as comma-separated user/group strings. `readFromConf` and login paths cache a single UGI per user in a map according to the docs.
- `SecurityUtil` stores global JVM security policy, and `UserGroupInformation` stores thread-local current identity.
- `ConfiguredPolicy.refresh` reloads policy from Hadoop configuration and policy-provider service definitions.
- `DataChecksum` persists compact checksum headers and current checksum values; callers must keep bytes-per-checksum, checksum type, and checksum size consistent with data streams.
- `HostsFileReader` maintains mutable include/exclude sets that are refreshed from configured files.
- `Progress` stores a tree of phases and current phase state; `Shell` stores process, working directory, environment, interval, and exit code; `ShellCommandExecutor` stores command output.
- Bloom filters persist through Hadoop `Writable` `write/readFields`; zero-argument constructors are explicitly intended for deserialization.

## Dependencies and Integration Points

- Record I/O depends on Hadoop record runtime classes (`Record`, `RecordInput`, `RecordOutput`, `Buffer`), JavaCC-generated parser support, Ant (`Task`, `FileSet`, `BuildException`), and language-specific generated code consumers.
- The metadata layer integrates with the record runtime and with code generated by `rcc` for schema descriptions.
- Security code integrates with Java security (`Policy`, `Permission`, `Subject`, `Principal`), Hadoop `Configuration`, Hadoop IPC remote exception handling, and service protocol definitions.
- Authorization refresh depends on Hadoop IPC protocol versioning via `versionID`.
- Utility classes integrate widely with Hadoop `Configuration`, `Path`, `Text`, `Writable`, `Progressable`, Commons CLI/logging, servlet APIs, XSLT (`javax.xml.transform`), Java process APIs, Linux `/proc`, native Hadoop libraries, and MapReduce command-line/job launching conventions.
- Bloom filters depend on `org.apache.hadoop.util.bloom.Filter`, `Key`, Hadoop `Writable` I/O, and `org.apache.hadoop.util.hash.Hash`.

## Risks and Edge Cases

- The Record I/O compatibility story is incomplete in this chunk: optional fields are described as a future mechanism, while generated serialization is order-based. Schema evolution needs careful metadata/skipping behavior and tests against older/newer generated classes.
- XML and CSV escaping rules are non-trivial. String/buffer data containing nulls, line feeds, percent signs, commas, carriage returns, or XML-disallowed characters can corrupt round trips if escaping/unescaping differs across languages.
- Binary integer zero-compression and network byte order must match Java and C++ generated code exactly. Cross-language tests are important because the APIs promise multi-language support.
- `RecordTypeInfo.getNestedStructTypeInfo` only considers one nesting level, which is a compatibility limitation for recursive/deep schemas.
- Parser classes expose mutable public token fields and generated buffers; parser reuse via `ReInit` can carry stale state if all associated fields are not reset correctly.
- `RccTask` file-set processing plus `failonerror=false` may hide partial code-generation failures in builds.
- ACL parsing is string-based and whitespace/comma sensitive. Wildcard handling must be tested because `allAllowed()` bypasses user/group checks.
- Global security policy and thread-local UGI state are process-wide/thread-sensitive. Tests that mutate them can leak authorization identity between test cases if not reset.
- `AuthorizationException` suppresses stack traces by design; this reduces noise but can hide debugging context if unexpected authorization failures occur.
- `Shell.execCommand` and process tree utilities are platform-sensitive. `Shell.WINDOWS`, `getUlimitMemoryCommand`, and `/proc` availability checks must guard Windows/Cygwin/non-Linux behavior.
- `ShellCommandExecutor` expects small command output and stores it in memory; large outputs risk memory pressure.
- `LineReader` intentionally may consume beyond `maxBytesToConsume` by up to a buffer length when a line crosses the threshold. Split readers must account for this overshoot.
- `DataChecksum` callers must validate header length/type and compare expected checksum sizes. Incorrect bytes-per-checksum causes downstream block-transfer corruption.
- `CountingBloomFilter` can overflow small counters after repeated inserts of the same key and can underflow after deletes, changing expected false-positive/false-negative behavior.
- Logical Bloom operations require compatible filter parameters; combining mismatched vector sizes/hash counts would be semantically unsafe even if the API accepts a general `Filter`.

## Test Signals

- Record I/O: compile DDLs with includes, nested modules, primitive/composite fields, maps/vectors, and generated Java/C++ targets; round-trip all primitive values and composites through binary, CSV, and XML; verify generated package/namespace/file naming; compare equality/hash/ordering behavior in generated Java; assert include recursion does not generate included files unless requested.
- Parser: invalid tokens, malformed includes/modules/classes, nested map/vector grammar, source line/column diagnostics, `ReInit` reuse, lexical comments, and escaped string literals.
- Metadata: equality/hash of primitive/composite `TypeID`s, `RecordTypeInfo` serialize/deserialize, one-level nested struct lookup, and `Utils.skip` for every primitive/composite type.
- Ant task: single file vs fileset, destination directory creation, language option normalization, and `failonerror` true/false behavior.
- Security: UGI serialization/config round trips, login/config fallback, immutable UGI mutation attempts, thread-local current user isolation, ACL wildcard/user/group parsing, configured policy refresh, service authorization allowed/denied cases, and refresh protocol invocation.
- Utilities: generic option parsing with each documented option, `ToolRunner` configuration injection and remaining args, sort correctness with `IndexedSortable` plus progress callbacks, line terminators and long-line discard behavior in `LineReader`, disk checker concurrent mkdir behavior, checksum header/value round trips and mismatch detection, shell exit-code handling, platform guards for native/procfs/memory plugins, and string escape/split/unescape round trips.
- Bloom filters: add/membership positives, expected false positives but no false negatives for standard Bloom filters, writable round trips, set operations, counting delete and approximate-count behavior, overflow around count 15, dynamic row expansion at threshold `nr`, and rejection or safe handling of incompatible filters.
