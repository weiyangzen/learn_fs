# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.2.xml lines 30580-36846

## Scope

This chunk is part of the Hadoop Common 2.10.2 JDiff XML API snapshot. It begins in the tail of the deprecated `org.apache.hadoop.record.RecordInput` interface, then covers the rest of the deprecated Hadoop Record I/O runtime, compiler, generated parser, and metadata APIs. It then moves into public Hadoop security APIs: access-control exceptions, token/secret-key credentials, group and ID mapping SPIs, Kerberos/UGI utilities, credential providers, authorization helpers, HTTP security filters, and token primitives. The range ends inside `org.apache.hadoop.security.token.delegation.web.DelegationTokenAuthenticatedURL`, after the start of a third `openConnection(URL, ...)` overload, so that class is only partially covered here.

The source is generated compatibility metadata rather than executable Java. It records packages, public/protected API signatures, inheritance, implemented interfaces, fields, declared exceptions, deprecation strings, and Javadoc text. Runtime behavior below is inferred from those public contracts; implementation bodies live in the corresponding Hadoop Common Java sources.

## Purpose

The chunk preserves the Hadoop Common 2.10.2 public API baseline for two broad areas.

First, it documents Hadoop's legacy Record I/O stack. These APIs define serializers/deserializers, XML record streams, variable-length integer helpers, a DDL compiler model, JavaCC parser artifacts, and runtime type metadata. Every record I/O package in this chunk is explicitly deprecated in favor of Avro, but the JDiff file keeps the signatures stable for compatibility with downstream code that still compiles against them.

Second, it documents core security APIs used across Hadoop clients, servers, and filesystem implementations. These APIs manage credentials and delegation tokens, convert and log in Kerberos principals, create and proxy `UserGroupInformation` identities, map users/groups/IDs, load credential providers, authorize proxy users, add HTTP CSRF/frame protections, create token passwords through secret managers, renew/cancel tokens, and select tokens for service endpoints.

## Important APIs, Types, and Functions

### Deprecated Record I/O Runtime

`org.apache.hadoop.record.RecordInput` is already open when this chunk starts. The visible tail includes `readString`, `readBuffer`, `startRecord`, `endRecord`, `startVector`, `endVector`, `startMap`, and `endMap`, all taking XML/tagged-format tags and throwing `IOException` where stream parsing can fail.

`RecordOutput` is the symmetric serializer interface. It writes primitive values (`writeByte`, `writeBool`, `writeInt`, `writeLong`, `writeFloat`, `writeDouble`), strings, buffers, record boundaries, vectors, and maps. Composite boundaries carry the source `Record`, `ArrayList`, or `TreeMap` plus the format tag.

`org.apache.hadoop.record.Utils` exposes static low-level encoding helpers: `readFloat`, `readDouble`, byte-array and `DataInput` variants of `readVLong`/`readVInt`, `getVIntSize`, `writeVLong`, `writeVInt`, and `compareBytes`. It also exposes public `hexchars`. The documented variable-length integer encoding is a zero-compressed format with one-byte storage for small values and a leading length/sign byte for larger positive or negative values.

`XmlRecordInput` implements `RecordInput` over an `InputStream`. It provides XML deserialization for the same primitive and composite methods as `RecordInput`, returning `Index` instances for vector/map iteration.

`XmlRecordOutput` implements `RecordOutput` over an `OutputStream`. It writes XML representations for primitive values, buffers, strings, records, vectors, and maps.

The package documentation for `org.apache.hadoop.record` is large and descriptive. It explains the deprecated Hadoop DDL, generated Java/C++ record mappings, and binary/CSV/XML encodings. The binary format uses zero-compressed ints/longs, UTF-8 strings with encoded lengths, and raw buffer lengths. CSV uses explicit delimiters for strings, buffers, structs, vectors, and maps. XML follows XML-RPC-style value elements with Hadoop extensions for bytes, longs, floats, and buffers.

### Deprecated Record Compiler and Parser

`org.apache.hadoop.record.compiler.CodeBuffer` is a `StringBuffer`-style indentation helper with `toString()`.

`Consts` exposes string constants used by generated record I/O code, including `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.

`JType` is the abstract base for DDL types. Primitive and compound wrappers include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JVector`, `JMap`, and `JRecord`. `JField` wraps a field name and type. `JFile` models a record definition file, included files, and defined records, with `genCode(language, destDir, options)` as the public code-generation entry point.

`org.apache.hadoop.record.compiler.ant.RccTask` exposes an Ant task for the deprecated record compiler. It accepts language, single file, destination directory, fail-on-error behavior, and nested `FileSet`s, then runs the compiler from `execute()`.

`org.apache.hadoop.record.compiler.generated` contains JavaCC-generated parser artifacts. `ParseException` stores current token, expected token sequences, token images, and custom message formatting. `Rcc` is the parser/driver with constructors for `InputStream`, `Reader`, and `RccTokenManager`; it exposes grammar methods such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, plus `ReInit`, token access, parse-exception generation, and tracing toggles. `RccConstants` enumerates token IDs and lexical states. `RccTokenManager` owns lexer state, debug stream, literal images, lexical state tables, input stream, and `getNextToken()`. `SimpleCharStream` handles character buffering, line/column accounting, token begin/end positions, backup, reinitialization, and buffer cleanup. `Token` carries token kind, image, source positions, next token, and special token links. `TokenMgrError` formats lexical errors.

### Deprecated Record Metadata

`FieldTypeInfo` pairs a field ID with a `TypeID` and defines equality/hash behavior.

`TypeID` models primitive type IDs with shared public constants for boolean, buffer, byte, double, float, int, long, and string, plus a protected `typeVal` and equality/hash methods.

`MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` for compound map, vector, and record/struct types, exposing key/value, element, or field metadata and equality/hash behavior.

`RecordTypeInfo` extends `org.apache.hadoop.record.Record`; it stores a record name and field type metadata, can add fields, retrieve nested struct type info, serialize/deserialize itself through `RecordOutput`/`RecordInput`, and has a `compareTo` contract that is effectively not intended for ordering.

`org.apache.hadoop.record.meta.Utils.skip(RecordInput, tag, TypeID)` skips serialized data based on runtime type metadata.

### Core Security and Credentials

`org.apache.hadoop.security.AccessControlException` extends the older `org.apache.hadoop.fs.permission.AccessControlException` and provides default, message, and cause constructors. The default constructor exists for unwrapping from `RemoteException`.

`Credentials` implements `Writable` and stores tokens and secret keys in memory. It has empty and copy constructors; token APIs `getToken`, `addToken`, `getAllTokens`, and `numberOfTokens`; secret-key APIs `getSecretKey`, `addSecretKey`, `removeSecretKey`, `getAllSecretKeys`, and `numberOfSecretKeys`; file/stream APIs `readTokenStorageFile(Path|File, conf)`, `readTokenStorageStream`, `writeTokenStorageToStream`, and `writeTokenStorageFile`; raw `write`/`readFields`; and merge APIs `addAll` and `mergeAll`. `addAll` overwrites existing entries, while `mergeAll` preserves existing entries.

`GroupMappingServiceProvider` is the SPI behind `Groups`, with `getGroups(user)`, `cacheGroupsRefresh()`, `cacheGroupsAdd(groups)`, and `GROUP_MAPPING_CONFIG_PREFIX`.

`IdMappingServiceProvider` maps user/group names and numeric IDs in both directions, including `getUidAllowingUnknown` and `getGidAllowingUnknown` variants for fallback-tolerant mapping.

`KerberosAuthException` is an unrecoverable `IOException` for UGI Kerberos login/logout/subject failures. It carries optional user, principal, keytab path, ticket-cache path, and initial message fields via setters/getters and overrides `getMessage()`.

`SecurityUtil` is a final static helper class. Visible APIs include configuration refresh, TGT classification, server-principal expansion with `_HOST`, keytab login overloads, delegation-token service-name construction, host extraction from principals, lookup of `KerberosInfo` and `TokenInfo` annotations, token service address/build/set helpers, privileged `doAsLoginUserOrFatal`, `doAsLoginUser`, and `doAsCurrentUser` execution helpers, authentication-method get/set wrappers, and privileged-port detection. Public fields include `LOG`, `HOSTNAME_PATTERN`, and `FAILED_TO_GET_UGI_MSG_HEADER`.

`UserGroupInformation` is the central identity and authentication facade. This chunk exposes initialization/configuration hooks, security and Kerberos credential tests, current/login/best-user discovery, ticket-cache and subject-based user creation, keytab/ticket relogin flows, remote/proxy/test user factories, real-user accessors, short/full username and primary group accessors, token identifier and token attachment, credentials merging, group lookup, authentication method get/set, equality/hash, subject access, privileged `doAs` overloads, diagnostics, `main`, and `HADOOP_TOKEN_FILE_LOCATION`. The nested `AuthenticationMethod` enum exposes `values`, `valueOf`, `getAuthMethod`, and a conversion from `SaslRpcServer.AuthMethod`.

### Credential Providers, Authorization, and HTTP Filters

`org.apache.hadoop.security.alias.CredentialProvider` is the abstract/provider-facing API for named credential entries. It exposes transient/durable state via `isTransient`, persistence through `flush`, lookup with `getCredentialEntry`, enumeration with `getAliases`, mutation with `createCredentialEntry` and `deleteCredentialEntry`, password-state probes `needsPassword`, `noPasswordWarning`, and `noPasswordError`, and the `CLEAR_TEXT_FALLBACK` configuration key.

`CredentialProviderFactory` creates providers and resolves configured provider lists from `Configuration`; it exposes `CREDENTIAL_PROVIDER_PATH`.

`AccessControlList` models user/group ACL text. It has constructors for wildcard/string ACLs, `isAllAllowed`, mutation (`addUser`, `addGroup`, `removeUser`, `removeGroup`), collection accessors, membership checks, user authorization via `isUserAllowed`, string rendering, `getAclString`, and `Writable` serialization. Public constants include `WILDCARD_ACL_VALUE` and `USE_REAL_ACLS`.

`AuthorizationException` extends `org.apache.hadoop.security.AccessControlException` and intentionally overrides stack-trace getters/printers, which is a compatibility and diagnostic behavior to preserve.

`DefaultImpersonationProvider` implements `Configurable`-style proxy-user authorization. It exposes a test-provider accessor, `setConf`, `getConf`, `init`, `authorize`, helpers to build proxy superuser user/group/IP config keys, and accessors for proxy group/host maps.

`ImpersonationProvider` is the SPI with `init(prefix)` and `authorize(user, remoteAddress)`.

`RestCsrfPreventionFilter` is a servlet filter for REST CSRF protection. It exposes `init`, `doFilter`, `destroy`, `isBrowser`, `handleHttpInteraction`, `getFilterParams`, and constants for user-agent, browser-agent configuration, custom header, ignored methods, and the default header.

`XFrameOptionsFilter` is a servlet filter that emits X-Frame-Options protection. It exposes `init`, `doFilter`, `destroy`, `getFilterParams`, `X_FRAME_OPTIONS`, and `CUSTOM_HEADER_PARAM`.

The `org.apache.hadoop.security.protocolPB` and `org.apache.hadoop.security.ssl` packages appear as empty package entries in this range.

### Token Primitives and Delegation HTTP Start

`SecretManager<T extends TokenIdentifier>` creates and retrieves token passwords. It exposes abstract/overridable `createPassword(identifier)`, `retrievePassword(identifier)`, `retriableRetrievePassword(identifier)`, and `createIdentifier()`, read-availability checks, static secret generation, static password creation from identifier bytes and secret key, and static `createSecretKey(byte[])`.

`Token<T extends TokenIdentifier>` is the client-side token form. Constructors create a token from an identifier and secret manager, raw identifier/password/kind/service bytes, an empty token, or another token. Public APIs expose identifier/password/kind/service getters, service assignment, ID/password mutation, private-token cloning and private-clone checks, `Writable` serialization, URL-safe encode/decode, equality/hash/string rendering, cache-key construction, and delegation lifecycle calls `isManaged`, `renew(conf)`, and `cancel(conf)`. `LOG` is public static final.

`Token.TrivialRenewer` is a `TokenRenewer` for unmanaged token kinds. Subclasses provide `getKind`; it implements kind handling, unmanaged status, no-op/unsupported renewal behavior, and cancellation signature compatibility.

`TokenIdentifier` is an abstract `Writable` that supplies `getKind()` and `getUser()`. It can serialize itself to bytes via `getBytes()` and produce a tracking ID documented as an MD5 of those bytes.

`TokenInfo` is a public annotation type indicating token-related metadata.

`TokenRenewer` is the plugin interface for token lifecycle operations: `handleKind`, `isManaged`, `renew`, and `cancel`.

`TokenSelector<T extends TokenIdentifier>` selects a token from a collection for a named service.

`DelegationTokenAuthenticatedURL` extends `AuthenticatedURL`. The covered portion includes four constructors accepting default/authenticator/configurator combinations, static default authenticator setter/getter, a protected switch for using URL query strings instead of the delegation-token HTTP header, `useQueryStringForDelegationToken()`, and two complete `openConnection` overloads. The first accepts a generic `AuthenticatedURL.Token` and only uses a delegation token if it is the nested delegation token type with a token present. The second accepts `DelegationTokenAuthenticatedURL.Token` directly and gives the delegation token precedence over configured authenticator authentication. The chunk ends at the parameter list of another `openConnection(URL, ...)` overload, so remaining overloads, nested classes, and package closure are outside this work item.

## Control Flow

The XML itself has no executable control flow. It is a serialized API inventory consumed by JDiff/release tooling. The runtime flows implied by the APIs are:

Record I/O serialization proceeds by generated record code calling `RecordOutput.startRecord`, field-level primitive/composite writes, and matching end calls. Deserialization performs the inverse through `RecordInput` and `Index` objects returned by `startVector`/`startMap`. Binary flows use `Utils.writeVInt`/`writeVLong` and matching readers for compact lengths and integral values; XML flows use `XmlRecordInput`/`XmlRecordOutput` around Java streams.

Record compiler flow starts with `RccTask` or the `Rcc` parser reading `.jr` DDL files, parsing includes/modules/records/fields/types into `JFile`, `JRecord`, `JField`, and `JType` objects, then `JFile.genCode()` emits target-language code. Parser errors flow through `ParseException` for grammar errors and `TokenMgrError` for lexical failures. Metadata flow uses `RecordTypeInfo` and `TypeID` objects to serialize schema/type information and to skip unknown or unwanted fields.

Credential flow stores tokens and secret keys in a `Credentials` instance, serializes them to a token-storage stream/file, later reads them back, and attaches them to `UserGroupInformation`. Merging credentials either overwrites (`addAll`) or preserves (`mergeAll`) existing aliases, which is important when multiple subsystems contribute tokens for the same service.

Kerberos and UGI flow starts with static configuration via `UserGroupInformation.setConfiguration` and `SecurityUtil.setConfiguration`. Login can come from the current subject, ticket cache, or keytab. Keytab/ticket-cache users can relogin, remote users can be constructed for RPC identities, proxy users carry a real user, and operations execute under identities through `doAs`. `SecurityUtil` converts configured principals, extracts hosts, discovers Kerberos/token annotations, and sets token service fields so clients can select the right credentials.

Authorization flow uses `DefaultImpersonationProvider.init` to load proxy superuser user/group/IP settings from configuration, then `authorize` validates proxy requests against a real user and remote address. `AccessControlList` provides lower-level string ACL parsing and user/group membership checks.

HTTP filter flow initializes servlet filters from parameters, then `doFilter` inspects requests. `RestCsrfPreventionFilter` checks browser-like user agents, custom header presence, and ignored methods before allowing or rejecting REST calls. `XFrameOptionsFilter` adds frame-protection headers before continuing the filter chain.

Token flow starts with a `SecretManager` creating a password for a `TokenIdentifier`, producing a `Token` containing identifier bytes, password bytes, kind, and service. Clients serialize tokens with `Writable` or URL-safe encodings, attach them to UGI/credentials, select them by service through `TokenSelector`, and ask `TokenRenewer` plugins whether a token is managed before renew/cancel operations. `DelegationTokenAuthenticatedURL` uses an existing delegation token for HTTP connections when present; otherwise it falls back to the configured delegation-token authenticator.

## State and Persistence Behavior

The JDiff XML is persistent build output under `dev-support/jdiff`; its state is the Hadoop Common 2.10.2 public API surface. Any stale generation, truncated package, or signature mismatch can make compatibility reports inaccurate.

Record I/O runtime state is stream-local. `XmlRecordInput`/`XmlRecordOutput` wrap input/output streams; `Index` values track vector/map iteration; `RecordTypeInfo` stores record names and field metadata; `TypeID` compound subclasses retain element/key/value/struct type references. The deprecated compiler/parser APIs hold parser token streams, JavaCC lexical state, line/column buffers, include lists, and code-generation model objects.

`Credentials` persists token and secret-key maps via Hadoop `Writable` token-storage files/streams. The object is also an in-memory container that can be copied, merged, and attached to UGI. Alias collisions are stateful: overwrite versus preserve behavior differs between `addAll` and `mergeAll`.

`UserGroupInformation` owns process-wide security initialization, login-user state, current/subject-derived identities, attached credentials, token identifiers, group caches, authentication methods, and relogin state. Keytab and ticket-cache relogin APIs mutate login credentials and can affect all code using the static login user. `HADOOP_TOKEN_FILE_LOCATION` is the environment/config integration point for token files.

Credential providers may be transient or durable. `flush()` is the persistence boundary for provider-backed credential changes; `needsPassword` and warning/error methods expose whether provider state is usable without a password. `CredentialProviderFactory` resolves provider paths from configuration.

Authorization and group/ID mapping APIs usually cache external state: group memberships, user/group numeric mappings, proxy superuser allowlists, and host allowlists. `cacheGroupsRefresh` and `cacheGroupsAdd` are explicit cache mutation hooks.

Token state is security-sensitive byte-array state. A token contains identifier bytes, password bytes, kind, service, and possible private-clone/cache-key identity. `TokenIdentifier.getBytes()` serializes public identifier state; `getTrackingId()` derives a stable tracking value from those bytes. Renew/cancel state is held by external token services and accessed through `TokenRenewer` plugins.

## Dependencies and Integration Points

The deprecated record APIs integrate with `java.io` streams, `DataInput`/`DataOutput`, Hadoop `Record`, `Buffer`, `Index`, Ant `Task`/`FileSet`, JavaCC-generated parser infrastructure, and Avro as the documented replacement path.

Security APIs integrate widely across Hadoop Common:

- `Credentials`, `Token`, `TokenIdentifier`, `TokenRenewer`, `TokenSelector`, and `SecretManager` integrate authentication material with RPC, filesystem clients, delegation-token services, and UGI.
- `SecurityUtil` integrates Kerberos principals, keytabs, token service names, annotations (`KerberosInfo`, `TokenInfo`), privileged execution, and network addresses.
- `UserGroupInformation` integrates JAAS `Subject`, Hadoop credentials, Kerberos tickets/keytabs, proxy-user handling, group lookup, and privileged actions/exceptions.
- `GroupMappingServiceProvider` and `IdMappingServiceProvider` integrate Hadoop with operating-system, LDAP, NFS, or custom identity providers.
- `CredentialProvider` and `CredentialProviderFactory` integrate configuration secret lookup with provider-backed stores and cleartext fallback policy.
- `AccessControlList`, `DefaultImpersonationProvider`, and `ImpersonationProvider` integrate service authorization, proxy-user rules, and remote-address checks.
- `RestCsrfPreventionFilter` and `XFrameOptionsFilter` integrate Hadoop HTTP endpoints with servlet filter chains and browser-facing security headers.
- `DelegationTokenAuthenticatedURL` integrates Hadoop Auth's `AuthenticatedURL`, `ConnectionConfigurator`, delegation-token authenticators, Kerberos delegation authentication, HTTP headers, URL query-string fallback for WebHDFS compatibility, `HttpURLConnection`, and `AuthenticationException`.

## Risks and Edge Cases

The record APIs are deprecated but public. Removing or changing them can still break downstream builds or compatibility reports. Because these APIs include generated parser classes and public fields, even seemingly internal JavaCC changes can become API deltas.

Record serialization risks include malformed XML/CSV/binary data, vector/map count mismatches, invalid UTF-8 or disallowed XML characters, variable-length integer edge cases, and byte-array bounds when reading from `Utils` byte-array decoders. `RecordTypeInfo.compareTo` is documented as not meaningfully implemented, so callers should not rely on ordering.

Credential and token APIs expose raw byte arrays for secrets, token identifiers, and passwords. Callers must treat returned arrays as sensitive mutable data unless implementations defensively copy. URL-safe token encoding is convenient but can leak credentials if logged or placed in query strings.

`Credentials` alias collisions are subtle. `addAll` overwrites existing secrets/tokens while `mergeAll` does not; wrong choice can silently replace a fresher token or preserve a stale one.

UGI and Kerberos APIs are process-wide and timing-sensitive. Static login user state, relogin-from-keytab/ticket-cache behavior, and current-subject lookup can affect unrelated clients in the same JVM. `KerberosAuthException` is documented as unrecoverable, so retry loops around it are a bug signal.

Principal conversion and token service construction depend on hostnames, canonicalization, configured principals, and socket addresses. Incorrect `_HOST` replacement or service text can cause token selection and Kerberos authentication failures that are hard to diagnose.

Group and ID mapping providers depend on external identity systems and caches. Empty groups for nonexistent users, unknown UID/GID fallbacks, and cache refresh semantics need tests around authorization boundaries.

HTTP security filters can break legitimate clients if custom headers, browser user-agent matching, or ignored methods are configured incorrectly. Conversely, weak defaults or broad ignore lists can reduce CSRF or clickjacking protection.

`TokenRenewer` plugins are selected by token kind. Missing or ambiguous renewers can make `Token.isManaged`, `renew`, or `cancel` fail at runtime even though token serialization succeeds. `Token.TrivialRenewer` is only appropriate for unmanaged token kinds.

The chunk ends mid-`DelegationTokenAuthenticatedURL` method, so final analysis of all delegation-web APIs must be reconciled with the next chunk before making compatibility claims about that package.

## Test Signals

Useful validation signals for this API area include:

- JDiff regeneration diff showing no unintended public signature, visibility, deprecation, or exception changes.
- Record I/O round trips for binary, CSV, and XML across primitive, string, buffer, vector, map, and nested record data, including variable-length integer boundary values.
- Record compiler tests for `.jr` includes, modules, primitive/compound fields, generated Java/C++ output paths, Ant task file/file-set handling, and parser error messages.
- `Credentials` serialization/deserialization tests for token and secret-key maps, plus `addAll` versus `mergeAll` collision behavior.
- UGI tests for current/login user creation, keytab and ticket-cache login/relogin, proxy-user real-user state, token/credential attachment, group lookup, and `doAs` exception propagation.
- Kerberos principal and token-service tests for `_HOST` substitution, host extraction, socket-address token services, annotation lookup, and privileged-port detection.
- Credential-provider tests for lookup, create/delete, flush persistence, transient providers, password-required warnings/errors, and cleartext fallback behavior.
- Authorization tests for ACL parsing/rendering, wildcard ACLs, user/group membership checks, proxy-user group/host allowlists, and denied remote addresses.
- Servlet filter tests for CSRF header enforcement, browser user-agent detection, ignored methods, custom header names, and X-Frame-Options output.
- Token tests for secret-manager password creation/retrieval, token encode/decode, private clone behavior, equality/hash/cache key stability, renewer plugin selection, renew/cancel failures, and token selector service matching.
