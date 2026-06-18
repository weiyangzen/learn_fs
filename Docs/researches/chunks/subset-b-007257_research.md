# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.22.0.xml lines 24655-28377

## Scope

This chunk is a generated JDiff API snapshot for Hadoop Core 0.22.0. It is not executable implementation source; it records public API metadata, inherited type relationships, method signatures, fields, exceptions, visibility flags, and embedded Javadocs. The chunk starts inside the `org.apache.hadoop.record` package documentation for Record I/O serialization formats, continues through deprecated Record I/O compiler and metadata APIs, covers selected security, token, utility, and Bloom filter APIs, and ends with an empty `org.apache.hadoop.util.hash` package marker and the closing `</api>`.

Because this is a line-bounded chunk, the opening `org.apache.hadoop.record` package documentation is partial. The merge lane must combine this chunk with adjacent chunks before making whole-package claims about `org.apache.hadoop.record`.

## Purpose

The opening Record I/O documentation describes Hadoop's legacy record serialization contract. It defines compact binary encodings for numeric and byte/string data, a structured CSV grammar for primitive and composite record values, and an XML-RPC-inspired XML representation for primitive values, structs, vectors, and maps. The documentation is important compatibility material because it describes wire formats independent of Java method signatures.

The `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, and `org.apache.hadoop.record.compiler.generated` packages expose the legacy Hadoop record compiler. These APIs parse record definition files, model record types and fields, generate language-specific code, and integrate the compiler into Ant builds. Nearly every type in this family is deprecated with guidance to use Avro, but the API remains visible in this 0.22.0 snapshot.

The `org.apache.hadoop.record.meta` package exposes runtime type metadata for Record I/O. It models primitive, vector, map, and struct type IDs, field type descriptors, and serializable `RecordTypeInfo` metadata. These classes support schema-aware reading, writing, and skipping of legacy record streams.

The `org.apache.hadoop.security` portion documents public authentication and identity helper APIs: group lookup providers, JNI-backed Unix group mapping, Kerberos name exception types, a Jetty SSL connector variant that can require Kerberos-backed SSL behavior, SASL RPC authentication enums and callback handlers, and `UserGroupInformation.AuthenticationMethod`.

The token packages expose public exception and delegation-token metadata surfaces: `SecretManager.InvalidToken` and `AbstractDelegationTokenSecretManager.DelegationTokenInformation`.

The `org.apache.hadoop.util` portion documents small but widely used utility contracts: disk exception types, typed varargs options, progress callbacks, reflection/configuration helpers, shell command execution wrappers, binary size-prefix parsing, and the standard `Tool`/`ToolRunner` command-line integration pattern.

The `org.apache.hadoop.util.bloom` portion documents Bloom-filter implementations and related algorithms: standard, counting, dynamic, and retouched Bloom filters, plus hash-function and selective-clearing scheme APIs. These classes provide probabilistic set membership, deletion/counting support, dynamic growth, and retouched false-positive handling.

## Important APIs, Types, and Functions

### Record I/O serialization documentation

- The binary serialization text describes zero-compressed integer and long encodings, IEEE 754 float/double values in network byte order, UTF-8 strings with a zero-compressed length prefix, and raw buffers with the same length prefix.
- The CSV format defines primitive encodings for booleans, ints, longs, floats, doubles, strings, and buffers. Strings start with `'`, buffers start with `#`, and composites use `s{}`, `v{}`, and `m{}` delimiters for structs, vectors, and maps.
- The XML format uses XML-RPC-style `<value>` wrappers. Primitive tags include `ex:i1`, `boolean`, `i4`/`int`, `ex:i8`, `ex:float`, `double`, and string/hex data encodings. Composite records are represented through `struct` members or `array` data elements.
- String escaping rules are part of the contract. CSV escapes null, newline, percent, and comma; XML strings percent-escape XML-disallowed characters, carriage returns, and percent signs.

### Deprecated record compiler model

- `CodeBuffer` wraps a `StringBuffer` and auto-indents generated code; it exposes `toString()`.
- `Consts` publishes compiler constant strings such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract base for Record I/O compiler types. Concrete or composite type classes include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`.
- `JField` is a thin wrapper for a record field, constructed from a name and a type parameter.
- `JFile` models one record definition file with included files and records; `genCode(String language, String destDir, ArrayList options)` generates code and returns an integer status while declaring `IOException`.

### Ant and generated parser APIs

- `RccTask` extends Ant `Task`. It supports `setLanguage(String)`, `setFile(File)`, `setFailonerror(boolean)`, `setDestdir(File)`, `addFileset(FileSet)`, and `execute()`. Its Javadoc describes `<recordcc>` usage for Java or C++ generation.
- `ParseException` is the JavaCC parse exception. It has a parser-generated constructor using `Token`, expected token sequences, and token images, plus default and message constructors. Public fields include `currentToken`, `expectedTokenSequences`, and `tokenImage`; `getMessage()` formats parser-aware errors.
- `Rcc` is the generated parser and command driver. Constructors accept `InputStream`, `InputStream` plus encoding, `Reader`, or `RccTokenManager`. Its grammar methods include `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`. It also exposes `main`, `usage`, `driver`, parser `ReInit` overloads, token access, `generateParseException`, and tracing toggles.
- `RccConstants` exposes token-kind constants for the record definition language: module, record, include, primitive type tokens, vector/map punctuation, string/identifier tokens, lexical states, and `tokenImage`.
- `RccTokenManager` accepts a `SimpleCharStream`, can switch lexical states, fill tokens, get the next token, and set a debug stream.
- `SimpleCharStream` is the JavaCC character stream with reader/input-stream constructors, optional encoding, line/column tracking, buffer expansion/filling, token start, backup, reinitialization overloads, image/suffix access, cleanup, and line/column adjustment.
- `Token` exposes JavaCC token state: kind, begin/end line and column, image, next token, and special-token links. `newToken(int)` is a static factory.
- `TokenMgrError` models lexical errors and exposes constructors, `addEscapes`, `LexicalError`, and `getMessage()`.

### Record metadata APIs

- `FieldTypeInfo` pairs a field ID/name with a `TypeID`, with getters, typed equality, object equality, and hash code.
- `TypeID` represents primitive type IDs. It exposes `getTypeVal()`, equality, hash code, shared constants for bool, buffer, byte, double, float, int, long, and string, and protected `typeVal` state.
- `TypeID.RIOType` is a public constants holder for byte codes for `BOOL`, `BUFFER`, `BYTE`, `DOUBLE`, `FLOAT`, `INT`, `LONG`, `MAP`, `STRING`, `STRUCT`, and `VECTOR`.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` for composite types. They expose element/key/value/field type accessors and composite equality/hash behavior.
- `RecordTypeInfo` extends `org.apache.hadoop.record.Record`. It has empty and named constructors, `getName`, `setName`, `addField`, `getFieldTypeInfos`, one-level `getNestedStructTypeInfo`, `serialize(RecordOutput, String)`, `deserialize(RecordInput, String)`, and `compareTo(Object)`.
- `Utils.skip(RecordInput, String, TypeID)` skips serialized record data according to type metadata.

### Security and token APIs

- `GroupMappingServiceProvider.getGroups(String)` returns all group memberships for a user, returns an empty list for a non-existing user, and may throw `IOException`.
- `JniBasedUnixGroupsMapping` implements group lookup by invoking libc through JNI.
- `KerberosName.BadFormatString` and `KerberosName.NoMatchingRule` are public static `IOException` subclasses for Kerberos name parsing failures.
- `Krb5AndCertsSslSocketConnector` extends Jetty `SslSocketConnector`. It has default and mode constructors, protected `createFactory()` and `newServerSocket(...)`, public `customize(...)`, and public static final `KRB5_CIPHER_SUITES`. Its purpose is to keep client authentication required when Kerberos support is enabled.
- `Krb5AndCertsSslSocketConnector.Krb5SslFilter` implements `javax.servlet.Filter` and passes the Kerberos principal and short name into servlet request handling.
- `Krb5AndCertsSslSocketConnector.MODE` is an enum-like public API with `values()` and `valueOf(String)`.
- `SaslRpcServer.AuthMethod` exposes enum values, `getMechanismName()`, serialized `read(DataInput)` and `write(DataOutput)`, and public final fields `code`, `mechanismName`, and `authenticationMethod`.
- `SaslRpcServer.QualityOfProtection` exposes `getSaslQop()` and public `saslQop`.
- `SaslRpcServer.SaslDigestCallbackHandler` and `SaslRpcServer.SaslGssCallbackHandler` implement JAAS `CallbackHandler` for DIGEST-MD5 token authentication and GSSAPI Kerberos respectively.
- `SaslRpcServer.SaslStatus` exposes enum values and a public final integer `state`.
- `UserGroupInformation.AuthenticationMethod` exposes the visible authentication method enum surface.
- `SecretManager.InvalidToken` is an `IOException` with a message constructor.
- `AbstractDelegationTokenSecretManager.DelegationTokenInformation` stores a token renew date and password and exposes `getRenewDate()`.

### General utilities

- `DiskChecker.DiskErrorException` and `DiskChecker.DiskOutOfSpaceException` are message-bearing `IOException` subclasses.
- `Options.getOption(Class, base[])` searches varargs options for the first instance of a required class. `Options.prependOptions(T[], T[])` prepends new options to an existing option array.
- Typed abstract option wrappers include `BooleanOption`, `ClassOption`, `FSDataInputStreamOption`, `FSDataOutputStreamOption`, `IntegerOption`, `LongOption`, `PathOption`, `ProgressableOption`, and `StringOption`, each with a protected value constructor and public `getValue()`.
- `Progressable.progress()` lets long-running operations report progress to Hadoop frameworks to avoid timeout assumptions.
- `ReflectionUtils` exposes `setConf(Object, Configuration)`, `newInstance(Class, Configuration)`, `setContentionTracing(boolean)`, `printThreadInfo(PrintWriter, String)`, `logThreadInfo(Log, String, long)`, `getClass(T)`, `copy(Configuration, T, T)`, and `cloneWritableInto(Writable, Writable)`.
- `Shell.ExitCodeException` preserves process exit code through `getExitCode()`.
- `Shell.ShellCommandExecutor` wraps a fixed command, optional working directory, environment, and timeout. It exposes `execute()`, `getExecString()`, protected `parseExecResult(BufferedReader)`, `getOutput()`, and `toString()`.
- `StringUtils.TraditionalBinaryPrefix` maps case-insensitive binary prefix symbols to powers of 1024. It exposes `valueOf(char)`, `string2long(String)`, and public final `value` and `symbol`.
- `Tool` extends `Configurable` and declares `run(String[])`. `ToolRunner` runs tools after generic Hadoop command-line parsing and exposes overloads with explicit or tool-provided `Configuration`, plus `printGenericCommandUsage(PrintStream)`.

### Bloom filter APIs

- `BloomFilter` extends `Filter` and exposes default and `(vectorSize, nbHash, hashType)` constructors, `add`, logical `and`, `or`, `xor`, `not`, `membershipTest`, `toString`, `getVectorSize`, and `Writable` `write`/`readFields`.
- `CountingBloomFilter` is final and extends `Filter`. It supports `add`, `delete`, set operations, `membershipTest`, `approximateCount(Key)`, string conversion, and Writable serialization. Its Javadoc warns that inserting the same key more than 15 times can overflow buckets and raise error rates.
- `DynamicBloomFilter` extends `Filter` and adds a constructor with row threshold `nr`. Its Javadoc describes row creation when the active Bloom filter is full.
- `HashFunction` returns multiple hash positions for a `Key`; it is constructed from maximum value, number of hashes, and hash type, and provides `clear()` as a no-op plus `hash(Key)`.
- `RemoveScheme` defines public short constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` for retouched Bloom filter selective-clearing strategies.
- `RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`. It accepts false-positive information through overloads for a single `Key`, `Collection`, `List`, or `Key[]`, and performs `selectiveClearing(Key, short)` before standard `write`/`readFields`.

## Control Flow and Behavioral Contracts

The XML itself has no runtime control flow, but the documented APIs imply several important paths.

Record compiler flow begins with `RccTask.execute()` or `Rcc.driver(String[])`, reads one or more `.jr` record definition files, tokenizes input with `SimpleCharStream` and `RccTokenManager`, parses grammar productions through `Rcc`, builds `JFile`, `JRecord`, `JField`, and `JType` instances, and finally emits generated code through `JFile.genCode()`. Parse failures flow through `ParseException`; lexical failures flow through `TokenMgrError`.

Record metadata flow uses `RecordTypeInfo` to build or read a schema description, stores each field as `FieldTypeInfo`, and uses `TypeID` subclasses to represent primitive or composite field shapes. Serialization and deserialization flow through `RecordOutput` and `RecordInput`, while `Utils.skip()` uses `TypeID` to advance past fields without materializing values.

Security group resolution flows through the `GroupMappingServiceProvider` interface. The JNI implementation delegates user/group lookup to native libc calls, while callers see a Java `List` result or `IOException`.

Kerberos SSL flow extends Jetty connector creation. The connector builds SSL server socket factories and sockets, customizes Jetty requests, and a servlet filter projects Kerberos principal state into servlet request handling. The documented behavior is stricter than the base connector because disabling need-authentication is not honored when Kerberos support is active.

SASL RPC authentication flow serializes an `AuthMethod` code to `DataOutput` and reconstructs it from `DataInput`. Callback handlers process JAAS callbacks for either token-based DIGEST-MD5 or Kerberos GSSAPI. SASL status enum values carry integer protocol state.

Tool execution flow runs generic Hadoop option parsing before delegating to `Tool.run(String[])`. `ToolRunner.run(conf, tool, args)` also installs the possibly modified configuration onto the tool.

Shell command flow fixes command, directory, environment, and timeout at construction, then `execute()` runs the process. Output is collected for `getOutput()` and can be parsed by overriding `parseExecResult()`. Non-zero exits surface through `ExitCodeException`.

Reflection utility flow instantiates classes and injects configuration when objects implement Hadoop configuration contracts. Writable copy and clone helpers flow through serialization buffers, so they exercise each object's `write` and `readFields` implementations.

Bloom filter flow hashes a `Key` to `nbHash` positions using `HashFunction`. Standard Bloom filters set or test those positions. Counting filters maintain counters and can delete keys if counters are positive. Dynamic filters add rows when the active row reaches the configured threshold. Retouched filters first collect known false positives, then clear selected bits according to a removal scheme, trading selected false-positive removal against possible false negatives.

## State and Persistence Behavior

The JDiff XML persists the public API surface and Javadocs for compatibility comparison. Runtime state belongs to the APIs described by the XML.

Record I/O serialization state is durable wire-format state. The binary, CSV, and XML encodings documented in this chunk must remain stable for legacy records to interoperate across languages and Hadoop versions. Changes to zero-compressed integer rules, UTF-8 normalization, escaping, or composite delimiters would break stored data and generated clients.

Record compiler state includes in-memory schema ASTs (`JFile`, `JRecord`, `JField`, `JType` subclasses), token streams, parse error context, code-generation buffers, and Ant task configuration. Generated source files are the main persistent side effect of `JFile.genCode()` and `RccTask.execute()`.

Generated parser state is mutable and public in several JavaCC classes. `Rcc` exposes `token_source`, `token`, and `jj_nt`; `ParseException` exposes current-token and expected-token data; `Token` exposes token image, location, next-token, and special-token links; `SimpleCharStream` exposes or protects buffer, position, line, column, and stream state. Compatibility consumers may observe or mutate these fields directly.

Record metadata state persists through `RecordTypeInfo.serialize()` and `deserialize()`. `TypeID` singleton constants share primitive type instances. Composite type IDs store nested type IDs or field collections. Equality and hash code are part of schema matching behavior even though Javadocs say the hash implementation is basic.

Security and token state includes group membership results, Kerberos principal/short-name request attributes, serialized SASL auth method codes, SASL QOP values, delegation token renew dates, and token passwords. `DelegationTokenInformation` stores password bytes in memory and exposes only the renew date in this slice.

Utility state includes typed option arrays, process-local progress callbacks, reflection constructor/configuration caches or behavior in implementation, shell executor command/output/timeout state, and thread dump logging intervals. `ToolRunner` mutates a tool's configuration before invoking `run()`.

Bloom filters persist probabilistic membership data through `Writable` `write` and `readFields`. Constructors marked "use with readFields" create empty objects for deserialization. Counting filters persist counters rather than bits, dynamic filters persist a matrix of rows and row thresholds, and retouched filters persist the base filter plus false-positive tracking or retouched state as implemented.

## Dependencies and Integration Points

The Record I/O compiler integrates with JavaCC-generated parser components, Ant `Task` and `FileSet`, Java `InputStream`, `Reader`, `File`, `ArrayList`, and `IOException`, and Hadoop Record I/O classes such as `Record`, `RecordInput`, and `RecordOutput`. The entire compiler and metadata surface is deprecated in favor of Avro, so migration and compatibility tooling need to recognize both APIs.

The security APIs integrate with Hadoop `Groups`, `UserGroupInformation`, `SaslRpcServer`, token `SecretManager`, IPC `Server.Connection`, JAAS callbacks, servlet filters, Jetty `SslSocketConnector`, Jetty `Request`, Jetty `EndPoint`, Java SSL socket factories, and Hadoop's binary RPC protocol streams.

The utility APIs integrate with `Configuration`, `Configurable`, Hadoop `Writable`, `FSDataInputStream`, `FSDataOutputStream`, `Path`, `Progressable`, Commons Logging `Log`, Java `PrintWriter` and `PrintStream`, shell process execution, and MapReduce-style command-line processing through `GenericOptionsParser`.

The Bloom filter APIs integrate with `org.apache.hadoop.util.bloom.Filter`, `Key`, `org.apache.hadoop.util.hash.Hash`, Java collections, and Hadoop `Writable` serialization through `DataInput` and `DataOutput`. The `org.apache.hadoop.util.hash` package marker at the end of the chunk has no public classes in this line range, but Bloom filters refer to hash implementations from that package.

## Risks and Edge Cases

- The chunk starts inside package documentation and not at a package boundary. Adjacent chunks are required to reconstruct the full `org.apache.hadoop.record` API documentation.
- JDiff metadata omits method bodies. Validation rules, exact serialization byte order for all composite metadata, parser grammar details, JNI behavior, Jetty customization details, and Bloom filter internal layouts require implementation-source review.
- Most Record I/O compiler and metadata APIs are deprecated but still public. Removing or changing them would break source or binary compatibility for legacy users even if Avro is the recommended replacement.
- The documented binary, CSV, and XML Record I/O formats are compatibility-critical. Escaping mistakes, malformed length prefixes, XML control-character handling, and composite delimiter parsing can corrupt cross-language data exchange.
- JavaCC-generated classes expose mutable public parser fields. External code could depend on or mutate `Token`, `ParseException`, or parser state directly.
- `RecordTypeInfo.compareTo()` has confusing documentation: it says the class is not meant to be comparable and also says it always returns 0 for another `RecordTypeInfo`. Tests need to pin actual behavior.
- `getNestedStructTypeInfo()` only considers one level of nesting, which is a schema traversal limitation.
- `JniBasedUnixGroupsMapping` depends on native libraries and host NSS/group configuration. Missing JNI support, platform differences, large group lists, and non-existing users are likely failure modes.
- Kerberos SSL connector behavior is security-sensitive. Accidentally honoring disabled client authentication while in Kerberos mode would weaken authentication.
- SASL auth method serialization depends on stable byte codes. Reordering or changing enum fields can break RPC negotiation.
- Callback handlers must reject unsupported callbacks and invalid tokens correctly; swallowing failures can authenticate the wrong user.
- `DelegationTokenInformation` stores password bytes. Copies, exposure, and lifecycle behavior need careful review outside this JDiff metadata.
- `Options.getOption()` returns the first matching dynamic class. Option ordering and subclass matching can change behavior when multiple typed options are present.
- `ReflectionUtils.copy()` uses serialization to destroy and refill the destination object according to its Javadoc. Callers must not assume object identity or prior destination state survives.
- `ShellCommandExecutor` expects small command output. Large outputs, timeouts, quoting, platform shell differences, and environment handling are risk points.
- `TraditionalBinaryPrefix.string2long()` can overflow for large values or unsupported symbols. Case-insensitive parsing needs explicit coverage.
- `Progressable` is often used to avoid framework timeouts. Callers that forget progress callbacks on long operations may be killed even if making progress.
- Bloom filters are probabilistic. Tests must account for false positives while still validating deterministic behavior for added keys, serialization, and operations on compatible filters.
- Counting Bloom filters can overflow 4-bit-style bucket limits after repeated insertions, as documented for counts above 15. Deletes after underflow can introduce false negatives.
- Dynamic Bloom filters must choose the active row correctly and preserve row thresholds across serialization.
- Retouched Bloom filters intentionally trade false positives for false negatives. Incorrect selective clearing strategy can degrade both membership accuracy and repeatability.

## Test Signals

Useful validation for this chunk should include:

- JDiff/XML checks that the line range remains well formed when combined with adjacent chunks and that every public class, interface, field, constructor, method, exception, visibility flag, final/static/abstract flag, and deprecation marker in this slice is stable.
- Record I/O binary serialization tests for zero-compressed int/long boundaries, negative values, float/double network byte order, UTF-8 string normalization, and raw buffer length/data round trips.
- CSV serialization tests for every primitive, percent escaping of null/newline/percent/comma, struct/vector/map delimiters, empty vectors and maps, nested composites, and malformed grammar rejection.
- XML serialization tests for primitive tags, struct member names, vector/map arrays, UTF-8 handling, percent escaping of disallowed characters and carriage returns, and binary buffer hex encoding.
- Record compiler tests that parse valid `.jr` files with modules, includes, records, fields, primitive types, vectors, and maps, then generate Java and C++ outputs to configured destinations.
- Ant `RccTask` tests for single `file`, nested `fileset`, default language/destination, `failonerror` true and false behavior, and build-exception propagation.
- Parser error tests for `ParseException.getMessage()`, expected token sequences, token image escaping, lexical errors from `TokenMgrError`, stream line/column tracking, backup, and reinitialization with reader/input-stream encodings.
- Record metadata tests for primitive singleton `TypeID` equality, composite `MapTypeID`/`VectorTypeID`/`StructTypeID` equality and hash code, `FieldTypeInfo` typed and object equality, `RecordTypeInfo` field addition, nested struct lookup, serialize/deserialize round trips, and `Utils.skip()` for each type.
- Group mapping tests for existing users, non-existing users returning an empty list, JNI library absence, IOException propagation, and platform-specific group ordering.
- Kerberos SSL connector tests for mode construction, cipher-suite availability, server socket factory creation, enforced client authentication, request customization, and servlet filter principal propagation.
- SASL tests for `AuthMethod` byte-code read/write round trips, mechanism name and authentication-method mapping, QOP string mapping, DIGEST-MD5 valid and invalid token callbacks, GSSAPI callbacks, unsupported callbacks, and SASL status integer state.
- Token tests for `InvalidToken` messages and `DelegationTokenInformation.getRenewDate()` with password-byte lifecycle review.
- Utility tests for each typed `Options` wrapper, first-match option lookup, option prepending order, progress callback invocation in long operations, reflection instantiation with configuration injection, Writable copy/clone behavior, and thread dump logging interval behavior.
- Shell tests for command success, non-zero exit codes, captured output, timeout killing, working directory and environment handling, `parseExecResult()` override behavior, and `toString()` quoting of spaced arguments.
- Binary prefix tests for every prefix symbol, case-insensitive parsing, negative values, whitespace trimming, invalid symbols, and overflow handling.
- `ToolRunner` tests for generic option parsing, configuration mutation, pass-through of application arguments, exit-code propagation, and generic usage output.
- Bloom filter tests for construction, add, membership, logical and/or/xor/not compatibility, `getVectorSize`, serialization round trips, string rendering, and rejection or behavior with incompatible filter parameters.
- Counting Bloom filter tests for deletion of present and absent keys, approximate counts, repeated insert overflow behavior above 15, underflow effects, and serialization.
- Dynamic Bloom filter tests for row growth after threshold `nr`, membership across rows, logical operations with compatible filters, and `readFields` construction.
- Retouched Bloom filter tests for adding false positives through all overloads, null false-positive no-op behavior, each `RemoveScheme` constant, selective clearing side effects, false-negative tradeoffs, and serialization.
