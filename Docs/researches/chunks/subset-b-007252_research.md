# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml lines 24706-25944

## Scope

This chunk is the tail of the Hadoop Core 0.21.0 JDiff public API snapshot. The range begins inside `org.apache.hadoop.security.SaslRpcServer.AuthMethod` and continues through the end of the XML file, covering security/SASL helper APIs, token exception and delegation-token metadata APIs, common utility contracts, command-line tool helpers, and the public Bloom filter classes. Because the source is generated API metadata rather than implementation source, this research records public contracts, signatures, inheritance, stated behavior, serialization surfaces, and compatibility risks inferred from those contracts.

## Purpose

The covered API surface provides:

- RPC authentication and SASL callback contracts for Hadoop IPC.
- Token invalidation/renewal metadata types used by security token managers.
- General utility exceptions and callbacks for disk checks, progress reporting, reflection, shell command execution, binary-prefix parsing, and generic Hadoop CLI tools.
- Probabilistic membership data structures in `org.apache.hadoop.util.bloom`, including standard, counting, dynamic, and retouched Bloom filters.

## Important APIs and Types

### `org.apache.hadoop.security`

- `SaslRpcServer.AuthMethod` is an enum-like public API for RPC authentication methods. This chunk includes `values()`, `valueOf(String)`, `getMechanismName()`, static `read(DataInput)`, instance `write(DataOutput)`, and public final fields `code`, `mechanismName`, and `authenticationMethod`. The read/write methods make the auth method part of Hadoop IPC's binary negotiation protocol.
- `SaslRpcServer.SaslDigestCallbackHandler` is a public static `CallbackHandler` for SASL DIGEST-MD5. Its constructor accepts a `SecretManager` and `org.apache.hadoop.ipc.Server.Connection`, and `handle(Callback[])` may throw `SecretManager.InvalidToken` or `UnsupportedCallbackException`.
- `SaslRpcServer.SaslGssCallbackHandler` is a public static `CallbackHandler` for SASL GSSAPI/Kerberos. Its no-arg constructor and `handle(Callback[])` expose the Kerberos SASL callback path, with `UnsupportedCallbackException` as the declared failure.
- `SaslRpcServer.SaslStatus` is an enum-like public status with `values()`, `valueOf(String)`, and a public final integer `state`. This is likely serialized or compared in SASL RPC handshake state exchange.
- `UserGroupInformation.AuthenticationMethod` is the public enum-like UGI authentication method surface exposed here through `values()` and `valueOf(String)`. It is referenced by `SaslRpcServer.AuthMethod.authenticationMethod`.

### `org.apache.hadoop.security.authorize`

- The package is present but empty in this chunk. Its presence still matters for API baseline tooling: it records that the package existed in the public API snapshot even though no public types are listed in this line range.

### `org.apache.hadoop.security.token`

- `SecretManager.InvalidToken` extends `IOException` and has a public `InvalidToken(String)` constructor. The doc states that the message explains why the token was invalid. It is part of the checked exception flow from token lookup/validation into SASL DIGEST callback handling.

### `org.apache.hadoop.security.token.delegation`

- `AbstractDelegationTokenSecretManager.DelegationTokenInformation` is a public static holder for a delegation token's renew date and password. The constructor accepts `(long renewDate, byte[] password)`, and `getRenewDate()` exposes the renewal timestamp. The password is not directly exposed in this chunk's public API.

### `org.apache.hadoop.util`

- `DiskChecker.DiskErrorException` and `DiskChecker.DiskOutOfSpaceException` both extend `IOException` and expose message constructors. They separate general disk errors from capacity exhaustion in callers that need distinct handling.
- `Progressable` is a public callback interface with `progress()`. The doc makes it a liveness signal: clients and applications call it during long operations so the Hadoop framework does not assume the operation has timed out.
- `ReflectionUtils` is a general public utility class. APIs in this chunk include `setConf(Object, Configuration)`, `newInstance(Class, Configuration)`, `setContentionTracing(boolean)`, `printThreadInfo(PrintWriter, String)`, `logThreadInfo(Log, String, long)`, `getClass(T)`, `copy(Configuration, T src, T dst)`, and `cloneWritableInto(Writable dst, Writable src)`. It integrates object construction/config injection, thread diagnostics, and `Writable` serialization-based cloning/copying.
- `Shell.ExitCodeException` extends `IOException`, adds a constructor `(int exitCode, String message)`, and exposes `getExitCode()`. It is the observable exception type for failed shell commands.
- `Shell.ShellCommandExecutor` extends `Shell` and provides constructors for command string arrays with optional working directory, environment map, and timeout. Public methods include `execute()`, `getExecString()`, protected `parseExecResult(BufferedReader)`, `getOutput()`, and `toString()`. It is intended for commands whose output is small and does not need custom parsing.
- `StringUtils.TraditionalBinaryPrefix` is an enum-like parser/model for binary units kilo through exa. It exposes `values()`, `valueOf(String)`, `valueOf(char)`, `string2long(String)`, and public final fields `value` and `symbol`. The parser trims input and accepts case-insensitive suffixes such as `k` or `g`, converting by powers of 1024.
- `Tool` extends `Configurable` and standardizes Hadoop command-line applications through `run(String[] args)`. The documentation defines the pattern: let `ToolRunner` process generic Hadoop options, then handle application-specific arguments in `run`.
- `ToolRunner` is a public utility with static `run(Configuration, Tool, String[])`, static `run(Tool, String[])`, and `printGenericCommandUsage(PrintStream)`. It parses generic Hadoop CLI options, mutates or supplies the tool `Configuration`, invokes `Tool.run`, and passes application arguments through.

### `org.apache.hadoop.util.bloom`

- `BloomFilter` extends `Filter`. It has a default constructor for `readFields`, a parameterized constructor `(vectorSize, nbHash, hashType)`, mutation and set-operation methods `add(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, query method `membershipTest(Key)`, `toString()`, `getVectorSize()`, and `Writable`-style `write(DataOutput)`/`readFields(DataInput)`. Its documented semantics are the standard Bloom filter tradeoff: no false negatives for inserted keys, possible false positives.
- `CountingBloomFilter` is final and extends `Filter`. It adds `delete(Key)` and `approximateCount(Key)` to the same broad Bloom filter operation set. The count API is approximate and documented as reliable only for small counts; inserting the same key more than 15 times can overflow all associated buckets, and deletes can underflow, increasing error or creating false negatives.
- `DynamicBloomFilter` extends `Filter` and adds a constructor `(vectorSize, nbHash, hashType, nr)` where `nr` is the maximum number of keys per row. It grows by adding Bloom filter rows when no active row has capacity. Membership succeeds when a key's hash positions are set in any row.
- `HashFunction` is final and maps a `Key` to several integer positions. Constructor parameters are `(maxValue, nbHash, hashType)`, `clear()` is explicitly a no-op, and `hash(Key)` returns an `int[]` of hash positions. It depends on `org.apache.hadoop.util.hash.Hash`.
- `RemoveScheme` defines public `short` constants for retouched Bloom filter bit clearing: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` is final, extends `BloomFilter`, and implements `RemoveScheme`. It can record known false positives through overloads accepting one `Key`, a `Collection`, a `List`, or a `Key[]`, then `selectiveClearing(Key, short)` removes a false positive according to the selected scheme. It also exposes `write(DataOutput)` and `readFields(DataInput)`.
- `org.apache.hadoop.util.hash` appears as an empty package at the end of this chunk; `HashFunction` references its `Hash` type even though the package's public classes are outside this range or absent from the final tail.

## Control Flow and State Behavior

- SASL RPC negotiation uses `AuthMethod` as a compact state token: callers can map enum names through `valueOf`, expose the SASL mechanism name through `getMechanismName`, and serialize/deserialize the method through `write(DataOutput)` and `read(DataInput)`. `SaslStatus.state` provides a public integer status code for handshake progress or result signaling.
- SASL callback handling flows through Java's `CallbackHandler.handle(Callback[])` contract. The DIGEST-MD5 handler integrates token validation and connection context; invalid tokens are reported as checked `SecretManager.InvalidToken`. The GSSAPI handler reports unsupported callback shapes through `UnsupportedCallbackException`.
- Token-manager state is represented by `DelegationTokenInformation`: creation stores renew date plus password bytes, while the public accessor in this chunk exposes only the renew date. The actual password lifecycle is intentionally not visible through the listed API.
- `Progressable.progress()` is a callback from long-running user or framework code into the scheduler/framework liveness path. It has no return value, so state change is external to the interface and likely recorded by the caller or framework.
- `ReflectionUtils.newInstance` control flow is constructor invocation followed by optional `Configuration` injection through `setConf`; `copy` and `cloneWritableInto` use writable serialization into a buffer or target object, so the source object's `write` method and destination object's `readFields` method define the effective copy behavior.
- `ShellCommandExecutor.execute()` runs the configured command, captures output for small-result commands, throws `IOException` or `ExitCodeException` on failure, and lets `parseExecResult(BufferedReader)` consume stdout. The timeout constructor parameter marks commands as timed out and kills them after the configured duration.
- `ToolRunner.run` is the CLI control-flow adapter: parse generic Hadoop arguments, set the resulting configuration on the `Tool`, call `run(String[])`, and return its exit code to the application's `main`.
- Bloom filters are mutable in-memory structures. `add` hashes keys and mutates bit/counter/row state; `membershipTest` checks hashed positions; `and`, `or`, `xor`, and `not` mutate or derive filter bit state according to implementation; counting filters decrement on `delete`; dynamic filters append rows as thresholds are exceeded; retouched filters clear selected bits to suppress known false positives at the cost of possible false negatives.

## Persistence and Compatibility Notes

- This XML is a compatibility baseline. Public names, nested class names, signatures, visibility, inheritance, exceptions, fields, and deprecation status are durable facts for downstream source and binary compatibility analysis.
- `AuthMethod.read/write` serializes RPC authentication choices. Changing numeric `code` assignments, mechanism names, or read/write formats would break interoperability between clients and servers using this API baseline.
- `SaslStatus.state` is public and final, so numeric state values are part of the public contract even though enum constants are not shown in this chunk's XML excerpt.
- `DelegationTokenInformation` stores renewal time and password bytes; persistence of token state in actual managers must preserve the relationship between renew date, token password, and token validity windows.
- Bloom filter classes expose `write(DataOutput)` and `readFields(DataInput)`. Serialized compatibility depends on preserving vector size, hash count, hash type, bit vectors, counting vectors, dynamic rows, and retouched false-positive metadata layouts.
- `ReflectionUtils.copy` and `cloneWritableInto` depend on `Writable` binary formats. Any `Writable` implementation copied through these helpers must maintain stable `write/readFields` semantics.
- `ShellCommandExecutor` exposes the command array through `getExecString()` and formats it in `toString()`. Quoting behavior for arguments with spaces is documented and may be asserted by tests or logs.
- `StringUtils.TraditionalBinaryPrefix.string2long` is a public parser. Accepted suffixes, case-insensitivity, trimming, negative values, and overflow handling are observable compatibility points.

## Dependencies and Integration Points

- Security APIs depend on Java SASL callback interfaces, `java.io.DataInput/DataOutput`, `org.apache.hadoop.security.UserGroupInformation.AuthenticationMethod`, `org.apache.hadoop.security.token.SecretManager`, and `org.apache.hadoop.ipc.Server.Connection`.
- Token APIs integrate with Hadoop token secret managers and checked `IOException`-based failure handling.
- Utility APIs depend on `org.apache.hadoop.conf.Configuration`, `org.apache.hadoop.conf.Configurable`, `org.apache.hadoop.io.Writable`, Apache Commons Logging `Log`, `PrintWriter`, `PrintStream`, process execution, environment maps, and Java IO streams/readers.
- `Tool`/`ToolRunner` integrate with Hadoop generic command-line options, `Configured`-style application classes, and MapReduce-era application launch patterns.
- Bloom filter APIs depend on `Filter`, `Key`, `RemoveScheme`, `HashFunction`, and `org.apache.hadoop.util.hash.Hash`, plus `DataInput/DataOutput` serialization.
- Disk-check exceptions integrate with filesystem/storage health checks that must distinguish disk error causes.

## Risks and Edge Cases

- The requested line range begins after the opening metadata for `SaslRpcServer.AuthMethod`, so enum constants and class header details just before line 24706 must be reconciled with adjacent chunks when producing the final per-file report.
- SASL auth compatibility is fragile: mismatched `AuthMethod.code`, mechanism names, or `SaslStatus.state` values can break RPC authentication before higher-level protocol errors are available.
- `SaslDigestCallbackHandler.handle` can surface invalid tokens during authentication. Callers must avoid collapsing token invalidation into a generic unsupported-callback failure, because the remediation and audit signal are different.
- Public final fields such as `AuthMethod.code`, `AuthMethod.mechanismName`, `AuthMethod.authenticationMethod`, `SaslStatus.state`, and `TraditionalBinaryPrefix.value/symbol` make internal encoding choices observable.
- `DelegationTokenInformation` accepts raw `byte[]` password data. If implementation stores the array by reference, callers could mutate token password state after construction; implementation review should verify defensive copying where needed.
- `Progressable` is a liveness API with no enforcement in the interface. Long-running operations that fail to invoke it can still time out even if they are otherwise healthy.
- `ReflectionUtils.copy` destroys or overwrites the destination object through deserialization. Incompatible source/destination writable types, partial reads, or non-idempotent serialization can leave `dst` in a corrupt state.
- Thread diagnostics in `ReflectionUtils.printThreadInfo/logThreadInfo` can be expensive and may expose sensitive stack information in logs.
- `ShellCommandExecutor` is explicitly for small command output. Using it for large output risks memory pressure because output is stored as a string.
- Shell execution is platform-sensitive: command quoting, working directory, environment injection, timeout killing, exit code propagation, and parsing failures all vary by OS and process behavior.
- `TraditionalBinaryPrefix.string2long` can overflow for large numeric prefixes and high suffixes; tests should cover bounds and invalid suffixes.
- `ToolRunner` mutates the tool configuration before calling `run`; tools that cache configuration-derived state before `ToolRunner.run` may observe stale state.
- Standard Bloom filters can return false positives by design. Counting filters can overflow above the documented counter range and underflow after deletes. Retouched Bloom filters intentionally introduce false negatives when clearing bits.
- Bloom filter set operations require compatible filter sizes/hash settings. The API accepts generic `Filter`, so implementations need type and parameter checks to avoid invalid combinations.

## Test Signals

- SASL API tests should round-trip each `AuthMethod` through `write(DataOutput)` and `read(DataInput)`, verify `code` uniqueness, verify mechanism-name mapping, and check `authenticationMethod` mapping into UGI auth methods.
- Callback-handler tests should cover supported and unsupported callback arrays, invalid-token propagation for DIGEST-MD5, Kerberos/GSSAPI callback behavior, and connection-context effects.
- Token tests should validate `InvalidToken` message preservation and `DelegationTokenInformation.getRenewDate()` for boundary timestamps; implementation tests should also check password byte-array ownership if source is available.
- Disk utility tests should distinguish `DiskErrorException` from `DiskOutOfSpaceException` in catch paths.
- `Progressable` tests should verify that long-running framework operations invoke progress callbacks frequently enough to prevent timeout behavior.
- `ReflectionUtils` tests should cover configuration injection, default-constructor instantiation, class return typing, writable copy/clone round trips, IO failure propagation, and thread-info throttling through `logThreadInfo`.
- Shell tests should cover constructor variants, environment and working-directory propagation, timeout handling, nonzero exit code via `ExitCodeException.getExitCode()`, stdout capture, `parseExecResult` behavior, `getExecString()`, and `toString()` quoting for arguments with spaces.
- `TraditionalBinaryPrefix` tests should cover case-insensitive `valueOf(char)`, trimmed values, negative values, each supported suffix, no-suffix numeric strings, invalid suffixes, and overflow/underflow boundaries.
- `ToolRunner` tests should exercise generic option parsing, null or explicit configuration behavior, `Tool.setConf` effects, pass-through of application arguments, returned exit codes, thrown exceptions, and generic usage output.
- Bloom filter tests should verify constructor parameter validation, add/query behavior with no false negatives for standard filters, expected false-positive behavior statistically, bitwise operations on compatible filters, serialization round trips, `CountingBloomFilter.delete` and `approximateCount` including overflow/underflow boundaries, `DynamicBloomFilter` row growth at `nr`, `HashFunction.hash` bounds and determinism, `RemoveScheme` constants, and `RetouchedBloomFilter.selectiveClearing` tradeoffs for each scheme.
