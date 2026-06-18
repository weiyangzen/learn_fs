# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 36347-42401

## Scope

This chunk is a JDiff API descriptor slice for Hadoop Common 2.6.0. It is generated XML metadata, not implementation source, but it records the externally visible Java API surface: packages, classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, visibility, synchronization/finality flags, and Javadoc-derived contracts. The range starts inside the deprecated `org.apache.hadoop.record.Record` declaration and ends after `org.apache.hadoop.service.LifecycleEvent`, so adjacent chunks are needed for whole-file reconciliation.

The visible source areas are:

- `org.apache.hadoop.record`: the tail of `Record`, plus `RecordComparator`, `RecordInput`, `RecordOutput`, `Utils`, `XmlRecordInput`, `XmlRecordOutput`, and a long package-level description of the deprecated Hadoop Record I/O DDL, generated code, and binary/CSV/XML encodings.
- `org.apache.hadoop.record.compiler`, `.ant`, `.generated`, and `.meta`: deprecated record compiler model types, Ant task integration, JavaCC parser infrastructure, and runtime schema metadata.
- `org.apache.hadoop.security`: annotation-derived protocol security metadata, HTTP auth filter initialization, group/id mapping contracts, JNI fallback group mappers, provider URI helpers, SASL helpers, shell id mapping, UGI authentication-method enum metadata, and whitelist-based SASL property resolution.
- `org.apache.hadoop.security.alias`: credential-provider abstraction, nested credential entry, factory, command-line shell, password reader, and provider factories.
- `org.apache.hadoop.security.protocolPB`: protobuf client/server translators for refresh authorization-policy and user/group mapping protocols.
- `org.apache.hadoop.security.ssl`: hostname verifier helpers and a Jetty SSL connector subclass that disables SSLv3.
- `org.apache.hadoop.security.token.delegation.web`: delegation-token-aware HTTP authenticated URL classes and authenticators.
- `org.apache.hadoop.service`: the beginning of Hadoop's service lifecycle framework through `LifecycleEvent`.

## Purpose

The XML preserves Hadoop Common 2.6.0's public API contract for compatibility comparison. The record packages document a deprecated serialization and record compiler stack retained after replacement by Avro. The security packages expose contracts used by RPC, HTTP, SASL, credential storage, identity/group resolution, delegation-token web clients, and admin refresh protocols. The service package exposes a reusable lifecycle state machine used by Hadoop daemons and subsystems.

Because this is a JDiff dump, the research value is the API and behavior promised by signatures and documentation rather than executable method bodies. Compatibility tooling should treat the signatures, checked exceptions, deprecation markers, and documented side effects as the stable surface.

## Important APIs, Types, and Functions

### Deprecated Record I/O Runtime

- `org.apache.hadoop.record.Record` is an abstract base for generated record classes. It implements `WritableComparable` and `Cloneable`, requires tagged `serialize(RecordOutput, String)`, tagged `deserialize(RecordInput, String)`, and `compareTo(Object)`, and also exposes untagged `serialize(RecordOutput)`, `deserialize(RecordInput)`, `write(DataOutput)`, `readFields(DataInput)`, and `toString()`.
- `RecordComparator` extends `WritableComparator` for raw record comparison. It has a protected constructor taking a record `Class`, an abstract byte-array `compare(...)`, and a synchronized static `define(Class, RecordComparator)` registration hook.
- `RecordInput` defines deserializer operations for primitive values, strings, `Buffer`, record boundaries, vector boundaries, and map boundaries. Composite starts return `Index` so callers can iterate serialized vector/map elements.
- `RecordOutput` defines the matching serializer operations: primitive writes, `writeString`, `writeBuffer`, record start/end, vector start/end over `ArrayList`, and map start/end over `TreeMap`.
- `org.apache.hadoop.record.Utils` exposes low-level serialization helpers: byte-array and `DataInput` variants of `readVLong`/`readVInt`, `readFloat`, `readDouble`, `getVIntSize`, `writeVLong`, `writeVInt`, `compareBytes`, and a public `hexchars` table.
- `XmlRecordInput` implements `RecordInput` over an `InputStream`; `XmlRecordOutput` implements `RecordOutput` over an `OutputStream`. Both mirror the full primitive and composite record I/O contract for XML serialization.
- The package documentation describes record DDL includes, modules, classes, target-language generation for C++ and Java, field accessor generation, primitive/composite type mappings, and binary/CSV/XML data encodings. It states that the whole package is deprecated in favor of Avro.

### Deprecated Record Compiler

- `CodeBuffer` wraps a string buffer with indentation-aware `toString()`.
- `Consts` publishes compiler constants such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract base for Hadoop record compiler type descriptors. Visible subclasses cover primitive and composite DDL types: `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JBuffer`, `JString`, `JVector`, `JMap`, and `JRecord`.
- `JField` wraps a record field name and type. `JFile` represents a parsed record-definition file with included files and record declarations, and exposes `genCode(language, destDir, options)`.
- `RccTask` extends Ant `Task` and invokes the record compiler from builds. It accepts language, file, fail-on-error, destination directory, and nested filesets before `execute()`.
- `ParseException`, `Rcc`, `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError` are JavaCC-generated parser components for record DDL. `Rcc` exposes parser entry points for includes, modules, records, fields, maps, vectors, token access, parser reinitialization, tracing, and command-line driver/main flow.

### Record Metadata

- `FieldTypeInfo` pairs a field id with a `TypeID` and defines equality/hash behavior.
- `TypeID` models primitive record type ids and publishes shared constants for bool, buffer, byte, double, float, int, long, and string types; nested `TypeID.RIOType` defines byte constants for primitive and composite kinds.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` to represent map key/value types, vector element types, and struct field metadata.
- `RecordTypeInfo` extends `Record` and serializes/deserializes schema metadata. It tracks a record name, supports adding fields, exposes field type info collections, can return one-level nested struct metadata, and has a comparison method documented as not intended for meaningful ordering.
- `org.apache.hadoop.record.meta.Utils.skip(RecordInput, String, TypeID)` skips encoded data based on runtime type metadata.

### Security and Identity

- `AnnotatedSecurityInfo` extends `SecurityInfo` and reads `KerberosInfo` and `TokenInfo` annotations from protocol interfaces.
- `AuthenticationFilterInitializer` extends `FilterInitializer` and propagates `hadoop.http.authentication.*` configuration into the hadoop-auth `AuthenticationFilter`, enabling Kerberos/SPNEGO HTTP authentication.
- `GroupMappingServiceProvider` defines user-to-group lookup plus group cache refresh/add operations and exposes `GROUP_MAPPING_CONFIG_PREFIX`.
- `IdMappingConstant` publishes user/group id mapping configuration keys, defaults, minimum update interval, unknown user/group labels, and static mapping file configuration.
- `IdMappingServiceProvider` maps user and group names to numeric ids and back, including variants that allow unknown users/groups.
- `JniBasedUnixGroupsMappingWithFallback` and `JniBasedUnixGroupsNetgroupMappingWithFallback` implement group mapping through native Unix/JNI paths with fallback behavior.
- `ProviderUtils.unnestUri(URI)` translates nested credential-provider URIs into Hadoop `Path` values for provider implementations.
- `SaslPlainServer.SaslPlainServerFactory` creates SASL/PLAIN servers and advertises mechanism names; `SaslPlainServer.SecurityProvider` registers the SASL provider.
- `SaslPropertiesResolver` is configurable and returns default, server, and client SASL property maps. It also has a static `getInstance(Configuration)` factory.
- `SaslRpcServer.AuthMethod` and `SaslRpcServer.QualityOfProtection` are enum-like nested types for RPC SASL mechanisms and QOP settings. `AuthMethod` can read/write itself to `DataInput`/`DataOutput`.
- `SaslRpcServer.SaslDigestCallbackHandler` and `SaslRpcServer.SaslGssCallbackHandler` expose JAAS callback handling for token/digest and Kerberos/GSS flows.
- `SecurityUtil.QualifiedHostResolver` resolves host names to qualified `InetAddress` values.
- `ShellBasedIdMapping` maps ids and names by shelling out to platform commands, supports static mappings, periodically updates maps, and exposes synchronized lookup/update methods.
- `UserGroupInformation.AuthenticationMethod` exposes conversion between UGI auth methods and `SaslRpcServer.AuthMethod`.
- `WhitelistBasedResolver` extends `SaslPropertiesResolver` and changes server SASL properties based on whether a client address is in fixed, variable, or constant IP allowlists. It exposes configuration keys for whitelist files, cache intervals, enablement, and non-whitelist RPC protection.

### Credential Providers

- `CredentialProvider` abstracts credential/password storage. It exposes transient-provider detection, `flush()`, alias lookup/listing, credential creation/deletion, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProvider.CredentialEntry` stores an alias and `char[]` credential and exposes alias, credential, and string rendering methods.
- `CredentialProviderFactory` creates providers from configured URI paths, exposes `CREDENTIAL_PROVIDER_PATH`, and discovers implementations through provider factories.
- `CredentialShell` is a `Configured` `Tool` for `hadoop credential` operations. It parses create/list/delete commands, prompts for credentials, allows stdout/stderr capture, uses an injectable `PasswordReader`, and provides a `main` entry point.
- `CredentialShell.PasswordReader` reads passwords and formats prompts/messages.
- `JavaKeyStoreProvider.Factory` and `UserProvider.Factory` implement provider creation for Java keystore-backed and user-backed credential stores.

### Protobuf Refresh Protocol Translators

- `RefreshAuthorizationPolicyProtocolClientSideTranslatorPB` implements `ProtocolMetaInterface`, `RefreshAuthorizationPolicyProtocol`, and `Closeable`; it forwards `refreshServiceAcl()`, supports `isMethodSupported`, and closes its PB proxy.
- `RefreshAuthorizationPolicyProtocolServerSideTranslatorPB` implements `RefreshAuthorizationPolicyProtocolPB` and maps protobuf `refreshServiceAcl` requests to the server-side `RefreshAuthorizationPolicyProtocol`.
- `RefreshUserMappingsProtocolClientSideTranslatorPB` implements `ProtocolMetaInterface`, `RefreshUserMappingsProtocol`, and `Closeable`; it forwards user-to-group and superuser-groups refresh calls and supports `isMethodSupported`.
- `RefreshUserMappingsProtocolServerSideTranslatorPB` implements `RefreshUserMappingsProtocolPB` and translates protobuf refresh requests into the server-side `RefreshUserMappingsProtocol`.

### SSL and Delegation-Token Web Auth

- `SSLHostnameVerifier.AbstractVerifier` implements Hadoop's hostname verifier contract. It provides `verify(host, SSLSession)` plus overloaded `check(...)` methods for sockets, certificates, CN arrays, subjectAlt arrays, and multiple hostnames, and helper methods for IPv4 detection, country wildcard acceptability, localhost detection, and dot counting.
- `SSLHostnameVerifier.Certificates` extracts common names and DNS SubjectAlt names from `X509Certificate` instances.
- `SslSocketConnectorSecure` extends Jetty `SslSocketConnector` and overrides `newServerSocket` to reject SSLv3 while allowing TLS 1.x, explicitly addressing CVE-2014-3566/POODLE.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with Hadoop delegation-token support. It has constructors for default authenticator, supplied `DelegationTokenAuthenticator`, `ConnectionConfigurator`, or both. It manages a static default authenticator class, controls header versus query-string token transmission, opens authenticated HTTP(S) connections with optional `doAs`, fetches tokens, renews tokens, and cancels tokens.
- `DelegationTokenAuthenticatedURL.Token` extends `AuthenticatedURL.Token` and stores a Hadoop `Token`, with getter and setter.
- `DelegationTokenAuthenticator` wraps another `Authenticator` and adds delegation-token operations. It supports connection configurators, authentication, token fetch, token renewal, and token cancellation, with optional `doAsUser` variants. Public constants describe operation/query/header/json parameter names.
- `KerberosDelegationTokenAuthenticator` uses Kerberos SPNEGO for HTTP authentication and falls back to `PseudoDelegationTokenAuthenticator` when the endpoint does not trigger SPNEGO.
- `PseudoDelegationTokenAuthenticator` uses Hadoop pseudo authentication by passing the current user as a query parameter while still supporting delegation-token operations.

### Service Lifecycle

- `AbstractService` implements `Service` and provides the base lifecycle state machine. The visible API includes construction by name, state/failure/config/start-time/history accessors, `init(Configuration)`, `start()`, `stop()`, `close()`, failure recording, wait-for-stop, protected extension hooks `serviceInit`, `serviceStart`, and `serviceStop`, local and global listener registration, state checks, string rendering, and blocker map management.
- `CompositeService` extends `AbstractService` to manage child services. It exposes a cloned child service list, protected `addService`, `addIfService`, `removeService`, and lifecycle overrides that initialize/start/stop children. The `STOP_ONLY_STARTED_SERVICES` policy controls whether shutdown stops only started children or all children.
- `CompositeService.CompositeServiceShutdownHook` is a `Runnable` that stops a composite service during JVM shutdown.
- `LifecycleEvent` is a serializable state-transition record with public `time` and `state` fields.

## Control Flow

Record I/O control flow is stream-oriented and callback based. Generated `Record` subclasses call `RecordOutput.startRecord`, serialize each field through typed primitive/composite methods, then call `endRecord`; readers mirror that through `RecordInput.startRecord`, typed `read*` calls, `Index` iteration for vectors/maps, and `endRecord`. Untagged `Record.write`/`readFields` adapt this generated-record flow to Hadoop `Writable` APIs. `Utils` supplies the variable-length integer and byte-comparison primitives that binary encoders and comparators rely on.

Record compiler flow is: JavaCC scanner/parser classes read DDL text, recognize includes/modules/records/fields/types, build compiler model objects (`JFile`, `JRecord`, `JField`, `JType` subclasses), and `JFile.genCode()` emits target-language source. `Rcc.main`/`driver` and `RccTask.execute` are the command-line and Ant entry points into the same compiler path.

Security control flow is mostly configuration and protocol driven. HTTP containers call `AuthenticationFilterInitializer.initFilter`, which copies prefixed Hadoop config into a servlet filter. RPC setup uses `AnnotatedSecurityInfo` and token/Kerberos annotations, then SASL handlers and property resolvers decide authentication mechanism and protection level. Group and id mapping calls flow through provider interfaces to JNI, shell, or configured implementations; `WhitelistBasedResolver` applies allowlist checks before returning SASL properties.

Credential control flow starts with `CredentialProviderFactory.getProviders(Configuration)`, which resolves configured provider URIs, delegates URI handling to provider factories, then exposes provider instances to callers. Callers create/read/delete entries, and durable providers persist buffered changes at `flush()`. `CredentialShell` wraps the same provider operations behind a command-line `Tool`.

Refresh-protocol control flow crosses the protobuf boundary. Client-side translators implement old Java protocol interfaces and call PB proxies; server-side translators receive protobuf request/response calls and delegate to non-PB protocol implementations, translating thrown exceptions into `ServiceException` as declared.

Delegation-token web control flow starts with normal `AuthenticatedURL` authentication unless a delegation token is already present in the nested token object. Token fetch/renew operations authenticate with the configured authenticator, optionally use `doAsUser`, and exchange JSON/HTTP parameters with the service endpoint. Cancellation is documented as not requiring authentication by the configured authenticator. Connection opening can transmit the delegation token through an HTTP header by default or query string for compatibility.

Service lifecycle control flow is state-transition based. `AbstractService.init` calls `serviceInit`, `start` calls `serviceStart`, and `stop` calls `serviceStop`; failures are recorded and can trigger stop behavior. Listeners observe state changes locally or globally. `CompositeService` sequences those transitions across child services and its shutdown hook delegates JVM shutdown to `stop()`.

## State and Persistence Behavior

The JDiff XML itself is persistent generated metadata. Within the APIs it describes, record I/O state is stream-local for `XmlRecordInput`/`XmlRecordOutput`, while generated records persist data through `Writable` and the record serialization formats. `RecordTypeInfo`, `TypeID`, and related metadata objects persist schema descriptions through `RecordInput`/`RecordOutput`; equality and hash behavior provide schema comparison signals.

The record parser classes are mutable. `Rcc` holds token source and current/next tokens, `RccTokenManager` holds lexical state and current characters, `SimpleCharStream` holds buffer positions and line/column arrays, and `ParseException` holds current token, expected token sequences, token images, and constructor mode. Reinitialization methods reset this parser state for reused parser instances.

Security state is distributed across process configuration, caches, and external systems. Group mapping providers have refreshable caches. Shell id mapping stores user/group maps and periodically refreshes them from system commands and static mapping files. SASL property resolvers hold `Configuration` and may cache whitelist contents. UGI authentication-method metadata ties public enum values to RPC SASL method codes.

Credential providers distinguish transient and durable stores. The `CredentialProvider` API makes `flush()` the persistence boundary, while the nested `CredentialEntry` keeps credential material in a `char[]`. Java keystore providers persist to keystore-backed storage; user providers are intended for transient job/user credential use.

Delegation-token APIs mutate authentication state carried by `DelegationTokenAuthenticatedURL.Token`: fetched tokens are stored there, renew operations return new expiration times, and cancellation invalidates server-side token state. Header versus query-string token transmission is per-URL object behavior controlled by `setUseQueryStringForDelegationToken`.

Service state is explicit and queryable. `AbstractService` stores current state, failure cause/state, configuration, start time, lifecycle event history, listeners, and blockers. `LifecycleEvent` persists transition time and state as a serializable object. `CompositeService` holds child-service state indirectly by maintaining its service list.

## Dependencies and Integration Points

- Record I/O depends on Hadoop `WritableComparable`, `WritableComparator`, `Buffer`, `Index`, `RecordInput`, `RecordOutput`, Java I/O streams, `DataInput`, `DataOutput`, and collection types such as `ArrayList` and `TreeMap`.
- The record compiler integrates with JavaCC-generated parser classes and Ant (`Task`, `BuildException`, `FileSet`).
- Record metadata integrates with the deprecated record runtime, especially `Record`, `RecordInput`, `RecordOutput`, and `TypeID`.
- Security APIs integrate with `Configuration`, `FilterInitializer`, `FilterContainer`, hadoop-auth `Authenticator` and `AuthenticatedURL`, JAAS callbacks, SASL server factories, `SecretManager`, IPC server connections, `InetAddress`, `BiMap`, and Hadoop `Path`.
- Credential providers integrate with `Configuration`, provider URI paths, Java service loading, `Tool`, `Configured`, console/password readers, and keystore/user-backed provider factories.
- ProtocolPB translators integrate old Java admin refresh interfaces with protobuf service interfaces and `com.google.protobuf.RpcController`/`ServiceException`.
- SSL classes integrate Java `SSLSession`, `SSLSocket`, `SSLException`, `X509Certificate`, and Jetty's `SslSocketConnector`.
- Delegation-token web auth integrates HTTP(S) URLs, `HttpURLConnection`, Hadoop security tokens, `ConnectionConfigurator`, Kerberos SPNEGO, pseudo auth, and service-side delegation-token operation parameters.
- Service lifecycle integrates `Configuration`, `Closeable`, `IOException`, listener interfaces, JVM shutdown hooks, and child `Service` implementations.

## Risks and Edge Cases

- This chunk starts inside `Record` and ends before later service classes, so merge/reconciliation must combine adjacent chunks before drawing whole-file conclusions.
- The record APIs are deprecated but still public. Generated legacy code may still depend on exact method names, checked exceptions, comparator registration, and wire encodings.
- Variable-length integer encoding and XML/CSV escaping are compatibility-sensitive. Any behavioral mismatch in sign handling, byte count, percent escaping, UTF-8 normalization, or buffer hex encoding can corrupt persisted records.
- JavaCC-generated parser classes expose mutable public/protected fields and many reinitialization overloads. Generated-code regeneration can accidentally change token ids, token images, lexical states, or parse error text.
- `RecordTypeInfo.compareTo` is documented as not providing meaningful ordering despite satisfying the abstract `Record` contract; callers relying on sorted behavior would be fragile.
- Group/id mapping depends on native libraries, shell command output, static mapping files, update intervals, and unknown-user fallbacks. Platform differences can cause subtle authorization or NFS identity errors.
- SASL whitelist resolution changes protection settings based on client address. Bad subnet parsing, stale variable-list caches, or hostname/address normalization issues can weaken RPC protection or block legitimate clients.
- Credential APIs handle secret material. `toString()`, shell output, merge behavior, and provider fallback to cleartext need careful testing to avoid leakage or unexpected downgrade.
- PB translators are thin adapters; exception translation and `isMethodSupported` behavior must remain compatible across mixed-version clients and servers.
- Hostname verification and SSL protocol filtering are security-critical. Wildcard matching, subjectAlt extraction, localhost shortcuts, IPv4 handling, and SSLv3 disabling need regression coverage.
- Delegation tokens sent in query strings are more likely to appear in logs than header-carried tokens. The compatibility switch is useful but carries exposure risk.
- `AuthenticatedURL` instances are documented as not thread-safe. Sharing `DelegationTokenAuthenticatedURL` or its mutable token object across threads can cause race-sensitive authentication behavior.
- Service lifecycle hooks are intended to run once per service instance and are not required to be synchronized by subclasses. Incorrect state transition handling, listener callbacks, or composite stop ordering can leave services partially initialized or not fully stopped.

## Test Signals

- API compatibility tests should verify all visible classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, visibility flags, and deprecation markers in this range.
- Record I/O tests should round-trip generated records through tagged and untagged serializers, including primitives, strings, buffers, nested records, vectors, maps, XML, CSV, binary encodings, and positive/negative variable-length integers.
- Record compiler tests should parse DDL includes, modules, primitive/composite fields, comments, invalid syntax, and recursive includes; they should exercise both `Rcc` command-line/driver flow and Ant `RccTask`.
- Metadata tests should serialize/deserialize `RecordTypeInfo`, compare `TypeID`/`FieldTypeInfo`/map/vector/struct metadata, and verify `meta.Utils.skip()` for every supported type.
- Security tests should cover annotation-derived `SecurityInfo`, auth filter parameter propagation, JNI fallback group mapping, shell id mapping refresh/static mappings, unknown id handling, SASL auth-method read/write, callback handlers, and whitelist-based QOP selection.
- Credential tests should cover provider discovery from configured paths, JKS and user provider factory selection, alias listing, create/delete/read, duplicate aliases, `flush()`, transient provider behavior, password prompting, and shell stdout/stderr capture without leaking credential values.
- PB translator tests should run client/server translator pairs for refresh-service-ACL, user-group mapping refresh, superuser-group refresh, close behavior, unsupported methods, and exception propagation as `IOException` or `ServiceException`.
- SSL tests should verify CN and DNS SubjectAlt extraction, wildcard matching rules, IPv4 and localhost handling, hostname mismatch failures, and that `SslSocketConnectorSecure` refuses SSLv3 while allowing TLS.
- Delegation-token web tests should cover default authenticator selection, custom authenticator/configurator constructors, header versus query-string token transport, `doAs` handling, get/renew/cancel operations, unauthenticated cancellation path, Kerberos fallback to pseudo auth, and non-thread-safe token mutation assumptions.
- Service tests should cover legal and illegal state transitions, null configuration rejection, hook call ordering, failure recording, listener/global-listener notification, wait-for-stop behavior, blocker map updates, composite child ordering, shutdown hook behavior, and lifecycle event serialization.
