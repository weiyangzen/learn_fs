# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 30541-36776

## Scope

This chunk is a JDiff API descriptor slice for Hadoop Common 2.10.0. It starts in the middle of `org.apache.hadoop.record.RecordOutput`, covers the remaining legacy record I/O runtime/compiler/metadata APIs, then covers much of Hadoop Common's security API surface through the beginning of `org.apache.hadoop.security.token.delegation.web.DelegationTokenAuthenticatedURL`. It is generated API metadata, not executable implementation, but it documents public constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, and deprecation notes that downstream compatibility tooling consumes.

The visible package areas are:

- `org.apache.hadoop.record`: tail of `RecordOutput`, `Utils`, `XmlRecordInput`, and `XmlRecordOutput`.
- `org.apache.hadoop.record.compiler`, `.ant`, and `.generated`: deprecated record DDL compiler types, Ant task integration, JavaCC parser/token stream classes.
- `org.apache.hadoop.record.meta`: deprecated runtime type metadata for record I/O.
- `org.apache.hadoop.security`: access-control exception, credentials, group/id mapping interfaces, Kerberos exception utilities, `SecurityUtil`, `UserGroupInformation`, and `AuthenticationMethod`.
- `org.apache.hadoop.security.alias`: credential provider abstraction and factory.
- `org.apache.hadoop.security.authorize`: ACLs, authorization exception, impersonation provider contracts and default provider.
- `org.apache.hadoop.security.http`: REST CSRF and X-Frame-Options servlet filters.
- Empty package markers for `org.apache.hadoop.security.protocolPB` and `org.apache.hadoop.security.ssl`.
- `org.apache.hadoop.security.token`: secret manager, token, token identifier, renewer/selector contracts, and token metadata annotation.
- `org.apache.hadoop.security.token.delegation.web`: constructors and primary delegation-token HTTP methods for `DelegationTokenAuthenticatedURL`, ending before the class is complete.

## Purpose

The XML preserves the public API contract for compatibility comparison. For the deprecated record I/O packages, it documents the old Hadoop record serialization stack and record compiler retained for binary/source compatibility after Avro replacement. For the security packages, it captures the central contracts used by Hadoop clients, RPC, HTTP services, and filesystem integrations for credentials, Kerberos login, delegation tokens, proxy-user authorization, servlet-level request hardening, and token lifecycle operations.

The file's role is therefore twofold: it is an input to JDiff/API-change reporting, and it is a compact map of externally visible Hadoop Common classes that tests and downstream projects may compile against.

## Important APIs, Types, and Functions

### Legacy record I/O runtime

- `RecordOutput` exposes primitive and composite serialization callbacks such as `writeInt`, `writeLong`, `writeFloat`, `writeDouble`, `writeString`, `writeBuffer`, `startRecord`, `endRecord`, `startVector`, `endVector`, `startMap`, and `endMap`. Every method accepts a tag for tagged formats such as XML and can throw `IOException`.
- `org.apache.hadoop.record.Utils` provides low-level binary helpers: `readFloat`, `readDouble`, `readVLong`, `readVInt`, `getVIntSize`, `writeVLong`, `writeVInt`, and `compareBytes`, plus the public static `hexchars` table. The variable-length integer format is zero-compressed and is shared by stream and byte-array readers.
- `XmlRecordInput` implements `RecordInput` over an `InputStream`, exposing typed reads for primitives, strings, buffers, records, vectors, and maps. `startVector` and `startMap` return an `Index` iterator.
- `XmlRecordOutput` implements `RecordOutput` over an `OutputStream`, mirroring the typed write and composite-boundary API.
- These APIs are all deprecated in favor of Avro, but their signatures remain part of Hadoop Common 2.10.0 compatibility.

### Record compiler and generated parser

- `CodeBuffer` wraps `StringBuffer` with indentation support for generated source.
- `Consts` exposes compiler constants such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the deprecated base for record compiler type descriptors. Primitive and composite subclasses in this chunk include `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JBuffer`, `JString`, `JVector`, `JMap`, and `JRecord`; `JField` wraps a named field and its type.
- `JFile` represents a parsed record DDL file and exposes `genCode(language, destDir, options)` to generate source for a selected language.
- `RccTask` is an Ant `Task` wrapper around the record compiler with setters for language, file, fail-on-error, destination directory, filesets, and an `execute()` entry point.
- `ParseException`, `Rcc`, `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError` are JavaCC-generated parser infrastructure for record DDL. `Rcc` exposes parser methods for `Input`, `Include`, `Module`, `RecordList`, `Record`, `Field`, `Type`, `Map`, and `Vector`, plus token access and parser reinitialization.

### Record metadata

- `FieldTypeInfo` pairs a field name with a `TypeID` and implements equality/hash behavior.
- `TypeID` represents primitive type IDs and publishes shared constants such as `BoolTypeID`, `BufferTypeID`, `ByteTypeID`, `DoubleTypeID`, `FloatTypeID`, `IntTypeID`, `LongTypeID`, and `StringTypeID`.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` model composite record types and expose accessors for element, key/value, or field metadata.
- `RecordTypeInfo` extends `Record` and serializes/deserializes record type metadata through `RecordOutput` and `RecordInput`. It tracks the record name, fields, nested struct information, and comparison behavior.
- `org.apache.hadoop.record.meta.Utils.skip()` skips encoded data from a `RecordInput` based on a `TypeID`.

### Core security and identity APIs

- `AccessControlException` extends filesystem permission access-control exceptions and provides default, message, and cause constructors.
- `Credentials` implements `Writable` for in-memory and persisted token/secret-key sets. It can add, fetch, remove, merge, read, and write tokens and secret keys, including helpers for token storage files and streams.
- `GroupMappingServiceProvider` defines user-to-group lookup and cache management methods. `IdMappingServiceProvider` defines UID/GID/name mapping methods, including variants that allow unknown identities.
- `KerberosAuthException` is an `IOException` carrying user, principal, keytab, ticket-cache, and initial-message context for unrecoverable UGI/Kerberos failures.
- `SecurityUtil` provides process-wide security helpers: Kerberos principal substitution, login from configuration/keytab, delegation-token service name construction and parsing, annotation lookup for `KerberosInfo` and `TokenInfo`, execution as login/current user, authentication-method mapping, and privileged-port detection.
- `UserGroupInformation` is the central identity container. The public surface includes static configuration/initialization, login/current/best UGI lookup, ticket-cache and keytab login/relogin/logout, proxy and remote user creation, test users, username/group accessors, token and credential attachment, authentication-method accessors, equality/hash behavior, subject access, `doAs` execution, debug logging, and a diagnostic `main`.
- `UserGroupInformation.AuthenticationMethod` is an enum-like nested type exposing `values`, string `valueOf`, `getAuthMethod`, and conversion from `SaslRpcServer.AuthMethod`.

### Credential providers and authorization

- `CredentialProvider` abstracts password/credential storage. It exposes transient-provider detection, `flush`, credential lookup, alias listing, credential creation/deletion, password-required status, and user-facing warning/error strings for missing provider passwords. `CLEAR_TEXT_FALLBACK` is visible as a public constant.
- `CredentialProviderFactory` creates credential providers from configured paths and exposes the `CREDENTIAL_PROVIDER_PATH` configuration key.
- `AccessControlList` implements `Writable` ACL parsing and mutation. It supports wildcard ACLs, users, groups, add/remove operations, membership checks against `UserGroupInformation`, string rendering, and wire serialization.
- `AuthorizationException` extends Hadoop security `AccessControlException`; the API also exposes stack trace and print methods.
- `ImpersonationProvider` extends `Configurable`, with `init(configurationPrefix)` and `authorize(proxyUser, remoteAddress)`.
- `DefaultImpersonationProvider` implements that contract, exposes a test provider, reads proxy-user groups/hosts from configuration, authorizes doAs users, and publishes helper methods for proxy-user config keys.

### HTTP filters

- `RestCsrfPreventionFilter` implements `javax.servlet.Filter` for CSRF protection. It identifies browser user agents, enforces a custom header except for configured methods, supports a testable `HttpInteraction` path, and exposes config-key constants such as `HEADER_USER_AGENT`, browser-user-agent and custom-header parameters, ignored-method parameters, and default header name.
- `XFrameOptionsFilter` implements `Filter` and adds clickjacking protection through an `X-Frame-Options` header. It exposes `X_FRAME_OPTIONS`, custom header configuration, filter lifecycle methods, and a `getFilterParams` configuration helper.

### Tokens and delegation-token HTTP client APIs

- `SecretManager<T extends TokenIdentifier>` is the server-side token secret contract. It creates passwords, retrieves passwords, supports retriable password lookup with standby/retriable/IO exceptions, creates empty identifiers, checks read availability, generates random secret keys, computes HMAC password bytes, and converts raw bytes to `SecretKey`.
- `Token<T extends TokenIdentifier>` implements `Writable` as the client-side token form. It stores identifier bytes, password bytes, kind, and service; supports cloning, decoding identifiers, service mutation, private token clones, URL-safe encode/decode, equality/hash/string/cache-key behavior, managed-token detection, renewal, and cancellation.
- `Token.TrivialRenewer` is a `TokenRenewer` for unmanaged token kinds. Subclasses provide a kind; managed checks and renew/cancel are trivial or unsupported as appropriate.
- `TokenIdentifier` implements `Writable` and defines token kind, associated `UserGroupInformation`, identifier bytes, and MD5-based tracking IDs.
- `TokenInfo` is an annotation marker for protocols that carry token information.
- `TokenRenewer` is the plugin interface for token lifecycle handlers: `handleKind`, `isManaged`, `renew`, and `cancel`.
- `TokenSelector<T extends TokenIdentifier>` chooses a token from a collection for a named service.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` and is the HTTP client bridge for delegation-token-aware web endpoints. This chunk includes constructors using the default authenticator, a supplied `DelegationTokenAuthenticator`, a `ConnectionConfigurator`, or both; static default-authenticator setters/getters; query-string-versus-header transmission controls; authenticated connection opening with optional `doAs`; delegation-token fetch with optional `doAsUser`; token renewal with optional `doAsUser`; and cancellation with optional `doAsUser`.

## Control Flow

For record I/O, the public control flow is format-neutral and callback based. Generated records call `startRecord`, per-field primitive/composite write methods, then `endRecord` on a `RecordOutput`; readers mirror that by calling `startRecord`, typed `read*` methods, vector/map `Index` iteration, and `endRecord`. The XML serializer/deserializer are concrete implementations of those contracts, while `Utils` supplies the binary primitive encoding support used by other formats.

The record compiler flow is: JavaCC tokenizes and parses record DDL through `RccTokenManager`, `SimpleCharStream`, `Token`, and parser methods on `Rcc`; parsed modules, records, fields, and types become `JFile`, `JRecord`, `JField`, and `JType` objects; `JFile.genCode()` emits target-language code. `RccTask.execute()` wraps the same flow for Ant builds.

The security identity flow centers on `UserGroupInformation`: configuration initializes authentication behavior; callers obtain login/current/remote/proxy UGIs; Kerberos logins use ticket caches or keytabs and can relogin; tokens and credentials attach to the subject; privileged work runs under a selected identity via `doAs`. `SecurityUtil` supplies the glue for principal resolution, token-service naming, and annotation-driven protocol security metadata.

Credential and authorization flow is configuration driven. `CredentialProviderFactory` resolves provider paths into provider instances; clients create/read/delete entries and flush durable providers. Proxy-user checks pass an effective proxy UGI and remote address through an `ImpersonationProvider`, with `DefaultImpersonationProvider` consulting configured users, groups, and hosts. `AccessControlList` then provides a lower-level user/group membership predicate for service authorization.

HTTP hardening flow is servlet-filter based. The CSRF filter initializes from servlet configuration or Hadoop configuration parameters, classifies user agents, and rejects browser-originating unsafe requests that lack the required custom header. The X-Frame-Options filter initializes a configured header value and adds it while passing the request down the filter chain.

Token flow splits server and client responsibilities. A server-side `SecretManager` creates identifiers, secrets, and passwords and validates retrieval. A client-side `Token` serializes identifier/password/kind/service, can be decoded from URL-safe strings, can select a service, and delegates lifecycle operations to registered `TokenRenewer` implementations. `DelegationTokenAuthenticatedURL` uses normal authentication to obtain or renew tokens, prefers an existing delegation token when opening HTTP connections, and can cancel tokens without an additional configured-authenticator login path.

## State and Persistence Behavior

Most record I/O state is stream-local. `XmlRecordInput` and `XmlRecordOutput` wrap input/output streams; metadata objects such as `RecordTypeInfo`, `FieldTypeInfo`, and `TypeID` describe schemas and can be serialized through the record I/O interfaces. The JDiff XML records only method contracts, but the exposed APIs imply persistent wire formats for primitive values, variable-length integers, record metadata, and generated record definitions.

The generated parser classes maintain mutable lexical/parser state: current tokens, token source, input stream, token images, lexical state arrays, buffer positions, line/column arrays, and parse-exception context. These are reinitialized through overloaded `ReInit` methods.

`Credentials` is explicitly persistent. It is a `Writable` containing token and secret-key maps, can read/write token storage streams/files, and can merge or overwrite entries from another `Credentials` instance. `AccessControlList` is also `Writable`, preserving ACL strings across Hadoop configuration or RPC/storage boundaries.

`UserGroupInformation` carries both static process state and per-identity state. Static configuration determines security mode and login user behavior; individual UGIs carry subject, authentication method, real/effective user relationship, groups, token identifiers, tokens, and credentials. Kerberos keytab and ticket-cache paths are represented in failure context through `KerberosAuthException` and used by login/relogin APIs.

Credential providers may be transient or durable. `flush()` is the persistence boundary for providers that buffer changes, while `needsPassword`, `noPasswordWarning`, and `noPasswordError` expose provider-state constraints to callers.

Tokens persist as `Writable` byte arrays and can also be encoded as URL-safe strings for transport. Token identifiers provide raw bytes and tracking IDs; token service fields are text keys used by clients, selectors, and renewers. `DelegationTokenAuthenticatedURL` stores a delegation token inside its nested token type outside the visible range, and this chunk documents the operations that mutate or consume that state.

## Dependencies and Integration Points

- Record I/O APIs depend on `java.io` streams, `DataInput`, `DataOutput`, `IOException`, Java collections, and Hadoop record primitives such as `Buffer`, `Record`, `RecordInput`, `RecordOutput`, and `Index`.
- The record compiler integrates with JavaCC-generated parser types and Ant via `org.apache.tools.ant.Task`, `BuildException`, and `FileSet`.
- Security APIs integrate with Hadoop core types: `Configuration`, `Configurable`, `Text`, `Writable`, filesystem permission exceptions, `UserGroupInformation`, `SaslRpcServer.AuthMethod`, `KerberosInfo`, `TokenInfo`, `TokenIdentifier`, and IPC exceptions such as `StandbyException` and `RetriableException`.
- Kerberos and authentication dependencies include JAAS `Subject`, `KerberosTicket`, principal/keytab/ticket-cache concepts, and privileged action execution through generic `doAs` methods.
- Credential-provider APIs are consumed by configuration and applications that need secret material without embedding cleartext values directly.
- Authorization packages integrate with proxy-user configuration naming conventions, group mappings, remote client addresses, and service ACL checks.
- HTTP filters integrate with the servlet API (`Filter`, `FilterConfig`, `FilterChain`, `ServletRequest`, `ServletResponse`, `ServletException`) and Hadoop `Configuration` prefix extraction.
- Token APIs integrate with secret-key/HMAC primitives (`javax.crypto.SecretKey`), Hadoop token renewer discovery, RPC service naming, URL encoding, and HTTP authentication via `AuthenticatedURL`, `ConnectionConfigurator`, `AuthenticationException`, `DelegationTokenAuthenticator`, and Kerberos delegation-token authenticators.

## Risks and Edge Cases

- This XML chunk begins and ends in the middle of larger API declarations. Merge tooling must combine adjacent chunks before making final per-file claims about the complete `RecordOutput` and `DelegationTokenAuthenticatedURL` surfaces.
- The record I/O packages are deprecated but still public. Removing or changing signatures can break old generated records or downstream projects even though Avro is the replacement.
- Variable-length integer encoding in `org.apache.hadoop.record.Utils` is wire-format sensitive. Any compatibility change in sign handling, byte order, or size calculation would corrupt stored or transferred data.
- The record compiler parser classes are generated and mutable. Manual edits to generated code or token constants can break DDL parsing in ways that only appear for specific grammar paths.
- `RecordTypeInfo` and metadata `TypeID` equality/hash behavior influence schema comparison and skipping logic; subtle mismatches can cause incorrect compatibility decisions for nested records, maps, or vectors.
- `Credentials` mixes public token identifiers and secret key material. Serialization, string rendering, merge semantics, and token-file handling need tests that prevent accidental leakage or data loss.
- `UserGroupInformation` has process-global configuration and login-user state. Tests that mutate static state, keytab relogin behavior, immediate-renewal flags, or metrics attachment can be order-dependent if cleanup is incomplete.
- Kerberos principal substitution and token service construction depend on hostnames and network addresses. Canonicalization, unresolved hosts, and `_HOST` substitution are common compatibility risks.
- Proxy-user authorization depends on configuration key construction and remote-address matching. Incorrect prefix handling, wildcard ACL parsing, or group cache behavior can create privilege-escalation or false-denial bugs.
- HTTP CSRF and X-Frame filters sit in front of service endpoints. Bad defaults, case-sensitive header handling, browser user-agent classification errors, or incorrectly ignored methods can either break legitimate clients or weaken protections.
- Token lifecycle APIs cross client/server boundaries. Incorrect renewer selection, private-token service semantics, URL-safe encoding/decoding, or cancellation authentication assumptions can lead to leaked, non-renewable, or uncancellable tokens.
- `DelegationTokenAuthenticatedURL` explicitly supports query-string token transmission for backwards compatibility. That path has higher exposure risk than header transmission because URLs are commonly logged.

## Test Signals

- API compatibility tests should verify that every public class, interface, constructor, method, field, checked exception, inheritance edge, and deprecation flag in this chunk remains stable unless an intentional compatibility change is recorded.
- Record I/O tests should round-trip primitives, strings, buffers, records, vectors, maps, XML format boundaries, and variable-length positive/negative integer encodings across old generated code.
- Record compiler tests should parse DDL files with includes, modules, records, primitive fields, strings, buffers, vectors, maps, comments, and syntax errors, and should validate generated code through both direct `Rcc.driver()` and Ant `RccTask.execute()` paths.
- Metadata tests should serialize and deserialize `RecordTypeInfo`, compare nested structs/maps/vectors, and exercise `meta.Utils.skip()` for each supported `TypeID`.
- Credentials tests should cover token/secret-key add, overwrite, remove, merge versus add-all semantics, token storage file/stream read-write, and secure string/log behavior.
- UGI/Kerberos tests should cover simple and Kerberos security modes, keytab login/relogin/logout, ticket-cache login, proxy user creation, real/effective authentication methods, token attachment, credential copying, and `doAs` exception propagation.
- `SecurityUtil` tests should cover `_HOST` principal substitution, host extraction, token service build/decode, protocol annotation lookup, privileged-port detection, and unavailable-login failure handling.
- Authorization tests should cover wildcard ACLs, explicit user/group ACLs, serialization, proxy-user config key construction, group/host allowlists, denied users, and remote-address mismatch behavior.
- HTTP filter tests should use mock servlet requests to verify CSRF browser detection, custom-header enforcement, ignored method configuration, X-Frame-Options header injection, and Hadoop-configuration parameter extraction.
- Token tests should cover secret generation, password creation/retrieval failure paths, identifier decode, URL-safe encode/decode, private clone behavior, renewer dispatch, managed versus unmanaged renew/cancel, tracking IDs, and delegation-token HTTP operations with and without `doAs`.
