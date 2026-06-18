# subset-b-007366 grouped research

This grouped report covers the Hadoop portmap and security sources assigned to `subset-b-007366`. Each source file has its own marker-bounded section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/RpcProgramPortmap.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/RpcProgramPortmap.java

Purpose: `RpcProgramPortmap` is the Netty handler that implements the ONC RPC portmapper program number `100000`, version `2`, used by Hadoop's RPCB/portmap service. It starts with built-in TCP and UDP mappings for the portmapper itself and maintains runtime program/version/protocol to port registrations.

Important APIs and types: The class is package-private, `@ChannelHandler.Sharable`, and extends Netty `IdleStateHandler`. It exposes portmap constants for `NULL`, `SET`, `UNSET`, `GETPORT`, `DUMP`, and `GETVERSADDR`, stores mappings in `ConcurrentHashMap<String, PortmapMapping>`, tracks active channels through a `ChannelGroup`, and has `getMap()` for tests or package inspection.

Control flow: `channelRead()` casts inbound messages to `RpcInfo`, extracts the `RpcCall`, creates an XDR reader over the request payload, dispatches by procedure id, serializes a reply into a new `XDR`, wraps it in a Netty `ByteBuf`, and sends an `RpcResponse` to the request remote address. `set()` decodes a mapping and stores it, `unset()` removes it, `getport()` returns a matching port or zero, `dump()` serializes all values, and unknown procedures return `PROC_UNAVAIL`.

State and persistence: All state is in-memory and process-local. There is no disk persistence, authentication, or durable recovery; restarting the portmap service resets registrations to the two defaults. The map is concurrent, but procedure handling does not validate ownership or reject replacement of existing keys despite the comment describing refusal of duplicate mappings.

Dependencies and integration: It depends on Hadoop ONC RPC classes (`RpcCall`, `RpcInfo`, `RpcAcceptedReply`, `RpcUtil`, `XDR`), portmap request/response/mapping helpers, Netty channels, and SLF4J. It integrates with the server pipeline by adding active channels to the group and closing idle or exceptional channels.

Risks and test signals: Tests should exercise all procedure ids, duplicate `SET` behavior, `GETVERSADDR` aliasing to `GETPORT`, unknown procedure replies, idle close behavior, and concurrent `SET`/`UNSET` visibility. Security-sensitive deployments should note that the class accepts registration mutations from any caller reaching the handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/RpcProgramPortmap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/package-info.java

Purpose: This package descriptor declares `org.apache.hadoop.portmap` as Hadoop's ONC RPC port mapper implementation package.

Important APIs and types: It attaches Hadoop classification annotations, marking the package `InterfaceAudience.Private` and `InterfaceStability.Evolving`. There are no executable APIs.

Control flow and state: There is no runtime control flow or mutable state. The file provides package metadata consumed by documentation and annotation-aware tooling.

Dependencies and integration: It imports Hadoop classification annotations and applies them at package scope. The package is used by Hadoop's ONC RPC/NFS-adjacent services for program-to-port registration and lookup.

Risks and test signals: The main risk is classification drift if public consumers start depending on private evolving classes. Tests are not needed for this descriptor beyond compile/package checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AccessControlException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AccessControlException.java

Purpose: `AccessControlException` is Hadoop's public IOException subtype for authorization and permission-denied failures.

Important APIs and types: It is `InterfaceAudience.Public` and `InterfaceStability.Evolving`. Constructors support a default "Permission denied." message for `RemoteException` unwrapping, an explicit detail string, and a throwable cause.

Control flow and state: The class carries only exception state inherited from `IOException`. There is no custom control flow beyond constructor selection and the fixed `serialVersionUID`.

Dependencies and integration: It is thrown across Hadoop security, filesystem, and IPC authorization paths and can cross RPC boundaries through Hadoop's remote exception handling.

Risks and test signals: Tests should verify default-message compatibility and cause retention. Callers should avoid treating all `IOException` instances as retryable when this subtype indicates an authorization decision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AccessControlException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AnnotatedSecurityInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AnnotatedSecurityInfo.java

Purpose: `AnnotatedSecurityInfo` adapts protocol-interface annotations into Hadoop `SecurityInfo` metadata.

Important APIs and types: It overrides `getKerberosInfo(Class<?>, Configuration)` and `getTokenInfo(Class<?>, Configuration)`, returning the protocol class annotations `@KerberosInfo` and `@TokenInfo`.

Control flow and state: Calls are pure lookups against runtime annotations. The `Configuration` argument is accepted to satisfy the parent contract but is not used.

Dependencies and integration: It integrates with `SecurityUtil` and RPC client/server setup that asks protocols for Kerberos principal keys and token selectors. It depends on Java runtime annotation retention.

Risks and test signals: Protocols missing annotations return null, causing later auth selection to skip Kerberos or token support. Tests should cover annotated and unannotated protocol interfaces and confirm no configuration side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AnnotatedSecurityInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AuthenticationFilterInitializer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AuthenticationFilterInitializer.java

Purpose: `AuthenticationFilterInitializer` wires Hadoop HTTP servers to hadoop-auth's `AuthenticationFilter` for pseudo, anonymous, and Kerberos/SPNEGO HTTP authentication.

Important APIs and types: `initFilter(FilterContainer, Configuration)` builds a filter config map and registers the filter named `authentication`. `getFilterConfigMap()` copies all `hadoop.http.authentication.` properties after stripping the prefix, sets cookie path to `/`, and resolves Kerberos `_HOST` principals.

Control flow and state: The initializer is stateless. At initialization time it collects configuration, resolves `KerberosAuthenticationHandler.PRINCIPAL` through `SecurityUtil.getServerPrincipal()` using `HttpServer2.BIND_ADDRESS`, and throws a runtime exception if principal resolution fails.

Dependencies and integration: It depends on `FilterContainer`, `FilterInitializer`, hadoop-auth `AuthenticationFilter`, `KerberosAuthenticationHandler`, `HttpServer2`, and `SecurityUtil`. The output map becomes servlet filter init parameters.

Risks and test signals: Tests should verify prefix stripping, cookie path injection, `_HOST` substitution, and error wrapping when bind-address principal resolution fails. Misconfigured principals fail at web server startup rather than per request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AuthenticationFilterInitializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AuthorizationContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AuthorizationContext.java

Purpose: `AuthorizationContext` provides a process-local thread context for carrying an authorization header byte array during RPC handling.

Important APIs and types: It is a final utility class with `setCurrentAuthorizationHeader(byte[])`, `getCurrentAuthorizationHeader()`, and `clear()`, backed by a static `ThreadLocal<byte[]>`.

Control flow and state: State is scoped to the current thread. Callers set a header before invoking authorization-sensitive code, consumers retrieve it from the same thread, and `clear()` removes it to prevent leakage into later work on pooled threads.

Dependencies and integration: It has no external dependencies beyond `ThreadLocal`. It integrates implicitly with RPC server/client code that wants to bridge an authorization header without expanding method signatures.

Risks and test signals: The primary risk is stale authorization data if `clear()` is not called in finally blocks around thread-pool work. Tests should cover isolation across threads and cleanup after exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AuthorizationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/CompositeGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/CompositeGroupsMapping.java

Purpose: `CompositeGroupsMapping` composes multiple `GroupMappingServiceProvider` implementations so Hadoop can combine LDAP, shell, JNI, or custom providers without writing a new provider class.

Important APIs and types: It implements `GroupMappingServiceProvider` and `Configurable`. Configuration keys include `hadoop.security.group.mapping.providers`, `.providers.combined`, and `.provider.<name>`. `getGroups()` returns a sorted list via `TreeSet`; `getGroupsSet()` returns a `HashSet`.

Control flow: `setConf()` stores the configuration, reads whether providers are combined, and loads named provider classes. `prepareConf()` rewrites provider-scoped keys such as `.provider.foo.ldap.url` back to normal provider keys before instantiating each provider with `ReflectionUtils`. Lookup iterates providers in order, logs and skips provider exceptions, adds non-empty results, and either stops at the first hit or continues based on `combined`.

State and persistence: Provider instances and the `combined` flag are in-memory. No cache is implemented here; cache refresh/add calls are no-ops, leaving caching to outer `Groups` or inner providers.

Dependencies and integration: It integrates with `Groups` as a configurable mapping provider. It uses Hadoop `Configuration`, `ReflectionUtils`, SLF4J, and any provider classes specified in configuration.

Risks and test signals: Risks include silently missing providers when classes are not configured, result ordering differences between list and set paths, and provider-specific config rewrite mistakes. Tests should cover combined versus first-hit behavior, exception isolation, and scoped configuration translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/CompositeGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/Credentials.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/Credentials.java

Purpose: `Credentials` is Hadoop's in-memory and serialized container for delegation tokens and secret keys. It is used by MapReduce, YARN, HDFS, and IPC paths to pass authentication material between processes.

Important APIs and types: The class implements `Writable`. `SerializedFormat` supports `WRITABLE` and `PROTOBUF`. Public operations include token and secret CRUD, unmodifiable map views, file/stream read-write helpers, `writeTokenStorageToStream()`, `writeTokenStorageFile()`, `readTokenStorageFile()`, `addAll()`, and `mergeAll()`.

Control flow: Tokens are keyed by `Text` alias in `tokenMap`; secrets are byte arrays keyed by `Text` in `secretKeysMap`. `addToken()` ignores null tokens and, when replacing a token, updates private clones whose base alias matches the replaced alias. Storage files start with magic `HDTS`, then a format byte, then either Writable records or a delimited protobuf. Writable serialization writes token count and token entries first, then secret count and byte payloads. Protobuf serialization converts tokens through shaded protobuf helpers and stores alias bytes plus token/secret fields.

State and persistence: Runtime state is mutable and not synchronized. Persistence is explicit through Hadoop `Path`, Java `File`, `DataInputStream`, or `DataOutputStream`. The default writer keeps the older Writable format for compatibility, while protobuf can be requested.

Dependencies and integration: It depends on Hadoop `Token`, `TokenIdentifier`, `WritableUtils`, `Text`, filesystem APIs, shaded protobuf helpers, and IO cleanup utilities. It is a core integration type for token storage files, job credentials, and UGI token propagation.

Risks and test signals: Tests should cover format magic validation, unknown format handling, Writable/protobuf round trips, private clone replacement, overwrite versus merge behavior, null-token logging, and alias byte preservation. Security risks include mutable byte-array secrets returned directly and accidental persistence of sensitive keys to broadly readable files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/Credentials.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/CustomizedCallbackHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/CustomizedCallbackHandler.java

Purpose: `CustomizedCallbackHandler` is an extension point for SASL callback customization beyond Hadoop's built-in callback handling.

Important APIs and types: It is an interface with `handleCallbacks(List<Callback>, String, char[])`. Nested `Cache` memoizes configured handlers by configuration key. `DefaultHandler` rejects any non-empty callback list. `delegate(Object)` adapts legacy objects with a compatible `handleCallbacks` method through reflection.

Control flow and state: `Cache.get()` checks a static map, instantiates the class configured under a key, falls back to `DefaultHandler` on construction failure, wraps non-interface objects through reflection, and caches successful custom handlers. `clear()` resets the static cache for tests.

Dependencies and integration: It depends on Hadoop `Configuration`, JAAS callbacks, reflection, and SLF4J. It is intended to be called by SASL client/server paths after standard name/password handling to process custom callbacks.

Risks and test signals: Static caching means configuration changes may not take effect until `clear()`. Reflection-based delegates can fail at runtime if signatures drift. Tests should cover interface implementations, delegate objects, default rejection, construction failure fallback, and cache clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/CustomizedCallbackHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/FastSaslClientFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/FastSaslClientFactory.java

Purpose: `FastSaslClientFactory` caches available JVM `SaslClientFactory` instances by mechanism to avoid repeatedly enumerating security providers during RPC authentication.

Important APIs and types: It implements `SaslClientFactory`, stores `Map<String, List<SaslClientFactory>> factoryCache`, exposes cached mechanism names, and creates the first non-null `SaslClient` for the requested mechanisms.

Control flow and state: The constructor enumerates `Sasl.getSaslClientFactories()` once using the supplied props and populates the cache. `createSaslClient()` walks requested mechanisms in order, then factories for that mechanism, returning the first client that can be created.

Dependencies and integration: It depends on Java SASL and JAAS `CallbackHandler`. It is used by `SaslRpcClient` as a static factory for DIGEST/Kerberos client creation.

Risks and test signals: Provider changes after construction are not visible. Tests should cover mechanism ordering, null factory results, empty mechanisms, and behavior when provider lists differ by props.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/FastSaslClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/FastSaslServerFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/FastSaslServerFactory.java

Purpose: `FastSaslServerFactory` is the server-side companion to `FastSaslClientFactory`, caching JVM `SaslServerFactory` instances by mechanism.

Important APIs and types: It implements `SaslServerFactory`, stores mechanism-to-factory lists, returns cached mechanism names, and creates the first non-null `SaslServer` for a mechanism/protocol/serverName tuple.

Control flow and state: The constructor snapshots `Sasl.getSaslServerFactories()` for the supplied props. `createSaslServer()` looks up the mechanism and tries each cached provider in order until one accepts.

Dependencies and integration: It depends on Java SASL and JAAS callback handling. Hadoop RPC server setup uses it to reduce repeated provider scans.

Risks and test signals: As with the client factory, the cache is static from construction time. Tests should cover missing mechanisms, provider ordering, and policy props such as no-plaintext.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/FastSaslServerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/GroupMappingServiceProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/GroupMappingServiceProvider.java

Purpose: `GroupMappingServiceProvider` defines the pluggable contract for mapping users to operating-system, LDAP, or netgroup memberships.

Important APIs and types: Implementations must provide `getGroups(String)`, `cacheGroupsRefresh()`, and `cacheGroupsAdd(List<String>)`. The default `getGroupsSet(String)` converts the list result into a `LinkedHashSet` to preserve order while removing duplicates.

Control flow and state: The interface has no state. The default method is a convenience path that avoids forcing every legacy provider to implement a set-returning method.

Dependencies and integration: It exposes the shared prefix `CommonConfigurationKeysPublic.HADOOP_SECURITY_GROUP_MAPPING` and is consumed by `Groups`, `CompositeGroupsMapping`, JNI/shell providers, and LDAP providers.

Risks and test signals: Provider tests should verify empty results for unknown users, IOException behavior, and cache refresh/add semantics. High-cardinality group users should prefer implementations overriding `getGroupsSet()` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/GroupMappingServiceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/Groups.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/Groups.java

Purpose: `Groups` is Hadoop's central user-to-groups service. It wraps a configured `GroupMappingServiceProvider` with positive caching, optional negative caching, static overrides, metrics, and singleton access.

Important APIs and types: Constructors accept `Configuration` and optional `Timer`. Public APIs include deprecated list-returning `getGroups()`, preferred `getGroupsSet()`, background refresh counters, `refresh()`, `cacheGroupsAdd()`, singleton getters, loaded-configuration reset, and test reset. The inner `GroupCacheLoader` owns Guava cache load/reload behavior.

Control flow: Construction instantiates the configured provider, reads cache timeouts, warning thresholds, background reload settings, parses static overrides, builds a Guava `LoadingCache`, and optionally builds a negative cache. Lookup first checks static mapping, then negative cache, then `cache.get(user)`. Cache load traces and calls `impl.getGroupsSet(user)`, records metrics, warns on slow lookups, stores non-empty groups, and throws for empty groups to avoid positive caching of misses. Reload is synchronous unless background reload is enabled, in which case old values are returned while a daemon executor refreshes.

State and persistence: State is in-memory only: cache entries, negative cache entries, static override map, counters, and singleton instance. Static overrides are loaded from configuration and not persisted by the class. `refresh()` invalidates positive and negative caches and asks the provider to refresh its own state.

Dependencies and integration: It depends on Guava cache/listenable futures, Hadoop `Timer`, `Configuration`, `ReflectionUtils`, tracing, `UserGroupInformation.metrics`, and mapping providers such as JNI or shell fallback. Permission checks and UGI rely on this service for group membership.

Risks and test signals: Tests should cover static overrides, negative-cache expiration, no-groups exceptions, background reload counters, singleton reset, cache invalidation, and warning metrics. Operational risks include stale groups until refresh/expiry, thread-pool pressure during background reload, and treating empty provider results as hard user misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/Groups.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/HadoopKerberosName.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/HadoopKerberosName.java

Purpose: `HadoopKerberosName` bridges Hadoop configuration to hadoop-auth's `KerberosName` parsing and auth-to-local rule engine.

Important APIs and types: It extends `KerberosName`, has a constructor for full principal strings, and provides static `setConfiguration(Configuration)`. The `main()` helper prints short-name translations for command-line principals.

Control flow and state: `setConfiguration()` selects a default rule based on Hadoop authentication method. Kerberos modes require a resolvable default realm and default to `DEFAULT`; simple modes default to extracting the first component. It then reads `hadoop.security.auth_to_local` and auth-to-local mechanism config and installs them into static `KerberosName` state.

Dependencies and integration: It depends on `SecurityUtil`, `KerberosUtil`, and common configuration keys. UGI and RPC authorization paths rely on these rules to map principals to local user names.

Risks and test signals: Rule state is global in `KerberosName`, and this method does not reset already-set rules beyond calling `setRules`. Tests should cover simple versus Kerberos defaults, missing realm failures, configured rule strings, and mechanism selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/HadoopKerberosName.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/HttpCrossOriginFilterInitializer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/HttpCrossOriginFilterInitializer.java

Purpose: `HttpCrossOriginFilterInitializer` conditionally installs Hadoop's CORS servlet filter on HTTP servers.

Important APIs and types: `PREFIX` is `hadoop.http.cross-origin.`, `ENABLED_SUFFIX` is `enabled`, `initFilter()` registers a global `CrossOriginFilter` when enabled, and `getFilterParameters()` strips the prefix from matching configuration entries.

Control flow and state: The initializer is stateless. On startup it checks `<prefix>enabled`; if false it logs an informational message and does nothing. If true it passes all prefixed options to the global filter.

Dependencies and integration: It depends on Hadoop `FilterContainer`, `FilterInitializer`, `CrossOriginFilter`, and `Configuration`. It integrates with web UIs and REST endpoints exposed by Hadoop services.

Risks and test signals: Tests should cover disabled behavior, prefix stripping, enabled registration, and subclass overrides of `getPrefix()` or `getEnabledConfigKey()`. Misconfigured broad origins can weaken browser-side access controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/HttpCrossOriginFilterInitializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IdMappingConstant.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IdMappingConstant.java

Purpose: `IdMappingConstant` centralizes default configuration and sentinel values for user/group id mapping used by Hadoop NFS-related components.

Important APIs and types: It defines update interval key/default/minimum, unknown user/group names as `nobody`, and static mapping file key/default (`/etc/nfs.map`).

Control flow and state: There is no executable control flow and no mutable state.

Dependencies and integration: It is consumed by id mapping service implementations and NFS code that translate names to numeric uid/gid values and optionally read static maps.

Risks and test signals: Tests should verify consumers enforce the minimum update interval and honor configured static mapping paths. The constants file itself only needs compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IdMappingConstant.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IdMappingServiceProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IdMappingServiceProvider.java

Purpose: `IdMappingServiceProvider` defines the contract for converting between user/group names and numeric uid/gid identifiers.

Important APIs and types: It declares `getUid`, `getGid`, `getUserName`, `getGroupName`, `getUidAllowingUnknown`, and `getGidAllowingUnknown`. Name-to-id methods may throw `IOException`; id-to-name methods accept an unknown fallback string.

Control flow and state: The interface has no implementation state. The "allowing unknown" variants document a fallback policy where unmapped names can use string hash codes.

Dependencies and integration: It is public/evolving and supports Hadoop NFS and other POSIX-identity integration layers.

Risks and test signals: Implementations should test unknown-name fallbacks, collision handling for hash-code ids, IOException propagation, and static/dynamic map refresh behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IdMappingServiceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IngressPortBasedResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IngressPortBasedResolver.java

Purpose: `IngressPortBasedResolver` customizes SASL quality-of-protection properties by server ingress port, allowing one Hadoop daemon with multiple listeners to require different QOP levels per port.

Important APIs and types: It extends `SaslPropertiesResolver`, defines `ingress.port.sasl.configured.ports` and `ingress.port.sasl.prop.<port>`, and overrides `getServerProperties(InetAddress, int)`.

Control flow and state: `setConf()` first loads default SASL properties, then parses configured ports into a `HashMap<Integer, Map<String,String>>`. Missing per-port QOP defaults to privacy. At lookup, an unconfigured port logs a warning and returns default resolver properties.

Dependencies and integration: It depends on `SaslRpcServer.QualityOfProtection`, Hadoop `Configuration`, and server-side RPC code that passes ingress port to the resolver.

Risks and test signals: Tests should cover multiple ports, malformed port values, missing port-specific config defaulting to privacy, unconfigured port fallback, and immutability assumptions after `setConf()`. Misconfiguration can silently apply default QOP to a listener.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IngressPortBasedResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsMapping.java

Purpose: `JniBasedUnixGroupsMapping` uses Hadoop native code to resolve Unix group memberships for a user.

Important APIs and types: It implements `GroupMappingServiceProvider`, declares native `anchorNative()` and `getGroupsForUser(String)`, returns list and set forms, and has no-op cache methods.

Control flow and state: A static initializer requires `NativeCodeLoader.isNativeCodeLoaded()`, anchors JNI resources, and fails construction if native code is unavailable. Lookups call the native function, log exceptions, and return an empty group array on failure. `getGroupsSet()` preserves native order through `LinkedHashSet`.

Dependencies and integration: It depends on Hadoop native libraries, `NativeCodeLoader`, commons collection helpers, and `Groups` as the outer cache/service.

Risks and test signals: Tests should cover native-unavailable behavior through the fallback wrapper, native exceptions returning empty groups, and duplicate group removal. Operationally, empty results are later treated by `Groups` as no-groups failures and may populate the negative cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsMappingWithFallback.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsMappingWithFallback.java

Purpose: `JniBasedUnixGroupsMappingWithFallback` selects the native Unix group resolver when Hadoop native code is available and otherwise delegates to shell-based group lookup.

Important APIs and types: It implements `GroupMappingServiceProvider` and delegates all group lookup and cache calls to a private provider instance.

Control flow and state: Construction checks `NativeCodeLoader.isNativeCodeLoaded()`. Native availability creates `JniBasedUnixGroupsMapping`; absence logs a performance advisory and creates `ShellBasedUnixGroupsMapping`.

Dependencies and integration: It is the default provider used by `Groups` in this code path. It depends on native loader status, the JNI provider, shell provider, and Hadoop performance advisory logging.

Risks and test signals: Tests should verify provider selection, delegation for list/set paths, and cache method forwarding. Behavior can differ between environments depending on native library availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsMappingWithFallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMapping.java

Purpose: `JniBasedUnixGroupsNetgroupMapping` extends native Unix group resolution with netgroup support for ACLs.

Important APIs and types: It extends `JniBasedUnixGroupsMapping`, declares native `getUsersForNetgroupJNI(String)`, overrides `getGroups(String)`, and uses `NetgroupCache` for inverted user-to-netgroup lookup.

Control flow and state: `getGroups()` first obtains Unix groups from the parent, then appends cached netgroups for the user. Netgroup cache population is driven by `cacheGroupsAdd()`, which clears/rebuilds requested netgroup entries by calling synchronized `getUsersForNetgroup()` because libc netgroup iteration is not reentrant. Native calls strip leading `@` from netgroup names.

Dependencies and integration: It depends on native code, `NetgroupCache`, and the `Groups` refresh/add API. It integrates with ACL code that preloads netgroups of interest rather than trying to enumerate all netgroups for a user.

Risks and test signals: Tests should cover netgroup names versus Unix group names, cache refresh, synchronized JNI calls, and native failures returning empty users. The model only returns netgroups already cached, so ACL preload behavior is critical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMappingWithFallback.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMappingWithFallback.java

Purpose: `JniBasedUnixGroupsNetgroupMappingWithFallback` chooses native or shell-based netgroup-aware group resolution.

Important APIs and types: It implements `GroupMappingServiceProvider` and delegates to either `JniBasedUnixGroupsNetgroupMapping` or `ShellBasedUnixGroupsNetgroupMapping`.

Control flow and state: The constructor checks native code availability and creates the appropriate delegate. All public methods forward directly to that delegate.

Dependencies and integration: It depends on `NativeCodeLoader`, both native and shell netgroup providers, and `Groups` as the outer service.

Risks and test signals: Tests should cover native-present and native-absent selection and delegate forwarding. Production behavior can change across hosts if native Hadoop libraries are inconsistently installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMappingWithFallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KDiag.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KDiag.java

Purpose: `KDiag` is a command-line Kerberos diagnostics tool for Hadoop. It inspects JVM, OS, configuration, SASL, token, keytab, JAAS, and UGI state and exits with a Hadoop-specific failure code when probes fail.

Important APIs and types: The class extends `Configured`, implements `Tool` and `Closeable`, and exposes `exec(Configuration, String...)`, `main(String[])`, and nested `KerberosDiagsFailure`. Options include `--keytab`, `--principal`, `--keylen`, `--secure`, `--nofail`, `--nologin`, `--jaas`, `--out`, `--resource`, and `--verifyshortname`.

Control flow: `run()` parses options, optionally loads configuration resources, selects output, and invokes `execute()`. `execute()` prints diagnostic sections, validates JCE key length, dumps system properties/environment/configuration, checks whether Hadoop authentication is simple, enables Kerberos/SPNEGO debug temporarily, configures UGI, validates token files, krb5 config/default realm, SASL resolvers, kinit executable, JAAS, NTP config, optional short-name mapping, and optionally logs in from keytab or current login user. Failures go through `verify`, `failif`, and `fail`, which either throw immediately or record `probeHasFailed` under `--nofail`.

State and persistence: Tool state includes output writer, keytab/principal options, min key length, mode flags, and failure flag. It reads local files such as `/etc/krb5.conf`, `/etc/ntp.conf`, keytabs, JAAS config, and token files, but does not persist Hadoop state. It temporarily changes system properties for Kerberos debug and restores them in a finally block.

Dependencies and integration: It depends on Hadoop CLI helpers, UGI, token APIs, keytab utilities, SaslPropertiesResolver, filesystem/configuration constants, Kerberos utilities, and OS/JVM system properties. It is intended for operators troubleshooting secure clusters.

Risks and test signals: Tests should cover argument parsing, `--nofail` accumulation, output file handling, secure-required behavior, keytab login, short-name validation, missing krb5/JAAS/NTP paths, and system-property restoration. Diagnostic output may expose environment and configuration values, so usage should account for sensitive logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KDiag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KerberosAuthException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KerberosAuthException.java

Purpose: `KerberosAuthException` is an IOException subtype for unrecoverable UGI Kerberos login/logout/subject errors where callers should not retry blindly.

Important APIs and types: It stores optional user, principal, keytab file, ticket cache file, and initial message fields with setters and getters. Constructors accept a message, cause, or initial message plus cause.

Control flow and state: `getMessage()` builds a contextual message from optional fields and the superclass message, using UGI exception message constants for labels. The object is mutable after construction so call sites can enrich context before throwing.

Dependencies and integration: It is used by `UserGroupInformation` Kerberos authentication flows and imports labels from `UGIExceptionMessages`.

Risks and test signals: Tests should verify message composition for each optional field and null initial message behavior. Since it can contain keytab and ticket-cache paths, logs should treat messages as security-sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KerberosAuthException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KerberosInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KerberosInfo.java

Purpose: `KerberosInfo` is a runtime-retained protocol annotation that tells Hadoop RPC security which configuration keys contain Kerberos principals.

Important APIs and types: It targets types, has `serverPrincipal()` as a required element and `clientPrincipal()` defaulting to the empty string. It is limited-private and evolving.

Control flow and state: There is no runtime logic in the annotation itself. Consumers such as `AnnotatedSecurityInfo` and `SecurityUtil` read it reflectively.

Dependencies and integration: It integrates with protocol interfaces used by Hadoop IPC. `SaslRpcClient` uses the server principal key to validate the server-advertised Kerberos identity.

Risks and test signals: Tests should cover annotation discovery and missing/empty principal keys. Protocols with incorrect keys can fail SASL negotiation or accept the wrong principal pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KerberosInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/LdapGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/LdapGroupsMapping.java

Purpose: `LdapGroupsMapping` implements `GroupMappingServiceProvider` by querying LDAP directories for user group membership, including Active Directory `memberOf`, generic group membership filters, POSIX group semantics, nested group traversal, failover URLs, bind-user rotation, and SSL stores.

Important APIs and types: It is configurable through many `hadoop.security.group.mapping.ldap.*` keys for URLs, SSL, keystore/truststore, bind users/passwords/aliases/files, base DNs, user/group filters, member attributes, POSIX attributes, hierarchy depth, timeouts, attempts, and context factory. Public methods include synchronized `getGroups()`, `getGroupsSet()`, `setConf()`, `getConf()`, `getLdapUrls()`, no-op cache methods, and nested `LdapSslSocketFactory`.

Control flow: `setConf()` validates URLs, cycles LDAP URLs, loads SSL and bind-user config, derives user and group base DNs, selects one-query mode when `memberOf` is set, configures POSIX/custom filter state, sets `SearchControls`, selects a JNDI context factory, and stores retry/failover counts. `getGroupsSet()` retries up to `numAttempts`, rotating bind users on `AuthenticationException`, failing over LDAP URLs after configured attempts, clearing `ctx` after failures, and returning empty set after all attempts. `doGetGroups()` obtains a `DirContext`, searches for the user, optionally extracts groups from `memberOf`, otherwise does a second group search, and optionally walks parent groups recursively.

State and persistence: Runtime state includes a cached `DirContext`, current LDAP URL, bind-user iterator/current bind user, SSL store paths/passwords, filters, attributes, and retry settings. The context is intentionally used under synchronized access because the underlying LDAP context is not thread-safe. Passwords can be read from credential providers, config, or files; no state is persisted.

Dependencies and integration: It depends on JNDI LDAP classes, SSL key/trust manager APIs, Hadoop `Configuration`, credential providers, and `Groups` for outer caching. `LdapSslSocketFactory` uses static configuration because JNDI creates socket factories by class name.

Risks and test signals: Tests should cover one-query fallback, POSIX lookup, custom group filter args, nested group traversal, empty user search, LDAP URL failover, bind-user rotation, password source precedence, SSL factory setup, context-classloader workaround, and search timeout attributes. Risks include static SSL factory state, broad synchronized lookup latency, sensitive password handling, and filter injection/misconfiguration through custom LDAP filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/LdapGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/NetgroupCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/NetgroupCache.java

Purpose: `NetgroupCache` inverts cached netgroup-to-users data into a user-to-netgroups map for fast ACL membership checks.

Important APIs and types: Static APIs include `getNetgroups(user, List<String>)`, `getNetgroupNames()`, `isCached(group)`, `clear()`, and `add(group, users)`. The backing map is `ConcurrentHashMap<String, Set<String>>`.

Control flow and state: `add()` iterates users, creates a concurrent set for each absent user using `putIfAbsent`, and adds the group. `getNetgroups()` appends any cached groups for a user to a caller-supplied list. `getGroups()` scans all values to derive known netgroup names.

Dependencies and integration: It is used by netgroup-aware JNI and shell group mapping providers. ACL code calls provider cache-add paths to populate netgroups of interest.

Risks and test signals: Tests should cover concurrent adds for the same user, clear behavior, duplicate group handling, and `isCached()` derived from values. The cache is process-global and unbounded except for explicit clear/rebuild.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/NetgroupCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/NullGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/NullGroupsMapping.java

Purpose: `NullGroupsMapping` is a test or special-purpose `GroupMappingServiceProvider` that resolves every user to no groups.

Important APIs and types: It implements list and set lookup methods returning empty collections and no-op cache refresh/add methods.

Control flow and state: There is no mutable state. Every lookup returns empty, which the outer `Groups` service may convert into a no-groups IOException and negative-cache entry.

Dependencies and integration: It integrates with `Groups` through the provider interface and is useful for configurations that intentionally disable group mapping or tests that need deterministic misses.

Risks and test signals: Tests should account for the distinction between this provider returning empty and `Groups` throwing for empty results. It should not be used accidentally in authorization-sensitive deployments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/NullGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ProviderUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ProviderUtils.java

Purpose: `ProviderUtils` contains shared helpers for Hadoop credential/key provider integrations, especially provider URI nesting, recursive filesystem-provider exclusion, and password discovery.

Important APIs and types: Public APIs include `unnestUri(URI)`, `nestURIForLocalJavaKeyStoreProvider(URI)`, `excludeIncompatibleCredentialProviders(Configuration, Class<? extends FileSystem>)`, `locatePassword(String, String)`, `noPasswordWarning()`, and `noPasswordError()`.

Control flow: URI helpers convert nested provider URIs such as local JCEKS wrappers to underlying `Path` forms and validate that local keystore nesting only accepts file URIs without authority. Provider exclusion parses the configured credential provider path, resolves filesystem-backed providers, drops providers whose filesystem class is assignable from the target filesystem to avoid recursion, and returns either the original configuration or a cloned configuration with a rewritten/unset provider path. Password lookup prefers an environment variable, then a classpath resource file, trimming file content.

State and persistence: The class is stateless. It reads environment variables and classpath resources and may clone configuration, but does not write files.

Dependencies and integration: It depends on Hadoop `FileSystem`, `Path`, credential provider factory classes, keystore provider classes, commons IO, and SLF4J. Filesystems and credential providers call it to avoid bootstrapping cycles.

Risks and test signals: Tests should cover malformed provider URIs, non-filesystem providers, exclusion and non-exclusion cases, local URI validation, password env/file precedence, missing password files, and generated warning text. Risks include silently skipping invalid provider URIs and exposing default-password warnings too late in startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ProviderUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/RefreshUserMappingsProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/RefreshUserMappingsProtocol.java

Purpose: `RefreshUserMappingsProtocol` is the IPC protocol for refreshing user/group and superuser proxy-group mappings in running Hadoop daemons.

Important APIs and types: It declares protocol version `1L`, `refreshUserToGroupsMappings()`, and `refreshSuperUserGroupsConfiguration()`, both throwing `IOException`. The interface is annotated with `@KerberosInfo(serverPrincipal=HADOOP_SECURITY_SERVICE_USER_NAME_KEY)`, and both methods are marked `@Idempotent`.

Control flow and state: The interface contains no implementation state. Server implementations perform actual cache invalidation or configuration reload when invoked.

Dependencies and integration: It is annotated with `@KerberosInfo` in related Hadoop code and used by admin refresh commands against NameNode, ResourceManager, and other services that expose mapping refresh operations.

Risks and test signals: Implementations should test authorization, Kerberos service principal configuration, RPC compatibility, cache invalidation, idempotent retry behavior, and propagation of IO failures. The interface itself needs compile and protocol-version compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/RefreshUserMappingsProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/RuleBasedLdapGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/RuleBasedLdapGroupsMapping.java

Purpose: `RuleBasedLdapGroupsMapping` decorates `LdapGroupsMapping` by applying a configured case-conversion rule to LDAP group names.

Important APIs and types: It extends `LdapGroupsMapping`, defines a conversion rule configuration key, supports enum-style rules such as no change, lower-case, and upper-case, and overrides group lookup methods to transform results.

Control flow and state: `setConf()` delegates to LDAP setup, reads the conversion rule, and parses it with `Rule.valueOf(value.toUpperCase())`. Invalid rules are logged, but the field is not explicitly assigned to `NONE`, so a bad value can leave `rule` null and make later switch-based lookups fail. Lookup calls the parent implementation, then maps each group through the selected conversion.

Dependencies and integration: It depends on the full LDAP provider and `StringUtils`/locale-safe case conversion behavior. It is selected as a group mapping provider via Hadoop configuration.

Risks and test signals: Tests should cover lower/upper/noop rules, invalid config values including null-rule behavior after invalid parsing, duplicate group collapse after case conversion, and interaction with nested groups. Case conversion can change authorization semantics in mixed-case LDAP directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/RuleBasedLdapGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslInputStream.java

Purpose: `SaslInputStream` wraps an `InputStream` with SASL unwrap processing when negotiated QOP requires integrity or privacy, while passing bytes through unchanged for authentication-only QOP.

Important APIs and types: It extends `InputStream` and implements `ReadableByteChannel`. Constructors accept either an initialized `SaslServer` or `SaslClient`. It overrides byte/array reads, skip, available, close, markSupported, isOpen, and channel `read(ByteBuffer)`.

Control flow: Construction inspects negotiated `Sasl.QOP`; any value other than `auth` enables wrapping. Wrapped reads consume a 4-byte big-endian unsigned length, read that many SASL token bytes, unwrap with the client or server, and serve from an internal output buffer. Zero-length unwrapped buffers are skipped in blocking read loops; EOF on the length read returns -1. Unwrapped mode delegates directly to the underlying `DataInputStream`.

State and persistence: State is per-stream: underlying input, SASL endpoint, wrap flag, token and length buffers, current unwrapped buffer, offsets, and open flag. `close()` disposes the SASL endpoint and closes the input.

Dependencies and integration: It depends on Java SASL, Hadoop classification annotations, and is used by Hadoop data/RPC paths that still rely on stream-based SASL framing.

Risks and test signals: Tests should cover auth pass-through, auth-int/auth-conf unwrap framing, EOF during token boundaries, zero-length tokens, ByteBuffer array and direct paths, disposal on SASL exceptions, and oversized length handling. A malformed length can allocate large arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslMechanismFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslMechanismFactory.java

Purpose: `SaslMechanismFactory` resolves the effective Hadoop SASL mechanism, allowing an environment variable to override configuration.

Important APIs and types: It exposes `getMechanism()`, `isDefaultMechanism(String)`, `isDigestMechanism(String)`, and a `main()` printer. It uses `HADOOP_SASL_MECHANISM`, `hadoop.security.sasl.mechanism`, and the configured default.

Control flow and state: The resolved mechanism is stored in a volatile static field. `getMechanism()` returns the cached value or synchronizes to read environment and a new `Configuration`, with environment taking precedence over config and config over default.

Dependencies and integration: It depends on Hadoop configuration defaults and SLF4J. SASL client/server setup can use it to choose DIGEST variants or default mechanisms.

Risks and test signals: Tests should cover env precedence, config default, cache behavior, and digest-prefix detection. Static caching means changes to environment or configuration after first access are ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslMechanismFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslOutputStream.java

Purpose: `SaslOutputStream` wraps outgoing bytes with SASL when negotiated QOP requires integrity or privacy and otherwise delegates directly to the underlying output stream.

Important APIs and types: It extends `OutputStream`. Constructors accept either initialized `SaslServer` or `SaslClient`, inspect `Sasl.QOP`, and buffer wrapped output with a 64 KiB `BufferedOutputStream`. It overrides single-byte and array writes, flush, and close.

Control flow: In pass-through mode writes go directly to `outStream`. In wrapped mode, writes call `saslServer.wrap()` or `saslClient.wrap()`, then write a 4-byte length prefix followed by the wrapped token. Single-byte writes reuse a one-byte input buffer. `close()` disposes the SASL endpoint after flushing/closing behavior in the implementation.

State and persistence: State is per-stream: underlying output, SASL endpoint, wrap flag, one-byte buffer, and latest token buffer. It has no durable persistence.

Dependencies and integration: It depends on Java SASL and Hadoop classification annotations. It pairs with `SaslInputStream` in stream-based Hadoop protocols.

Risks and test signals: Tests should cover auth pass-through, wrapped framing, flush behavior, dispose on close, client and server variants, and SASL exceptions. Large writes are wrapped as one token, so negotiated max buffer constraints matter at callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslPlainServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslPlainServer.java

Purpose: `SaslPlainServer` implements a SASL PLAIN server mechanism and provider registration for Hadoop authentication paths that need plaintext username/password callbacks.

Important APIs and types: It implements `SaslServer`. Nested `SecurityProvider` registers `SaslServerFactory.PLAIN`; nested `SaslPlainServerFactory` creates servers for mechanism `PLAIN` unless policy forbids plaintext. Core methods include `evaluateResponse()`, `isComplete()`, `getAuthorizationID()`, `getNegotiatedProperty()`, `wrap()`, `unwrap()`, and `dispose()`.

Control flow and state: `evaluateResponse()` accepts one UTF-8 PLAIN payload split into authz, authn, and password by NUL characters. Empty authz defaults to authn. It invokes a callback handler with `NameCallback`, `PasswordCallback`, and `AuthorizeCallback`; if authorized it stores the authorized id. Completion is set in finally, so failed attempts also mark the server complete. QOP is always `auth`; wrap/unwrap throw because PLAIN has no integrity/privacy.

Dependencies and integration: It depends on Java SASL, JAAS callbacks, and Java security provider APIs. Hadoop must register the provider where PLAIN server support is needed.

Risks and test signals: Tests should cover corrupt payloads, null responses, empty authz, authorization failure, callback exceptions, post-completion calls, no-plaintext policy, and dispose cleanup. Plaintext passwords require transport-layer protection if used outside an already protected channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslPlainServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslPropertiesResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslPropertiesResolver.java

Purpose: `SaslPropertiesResolver` supplies SASL property maps for Hadoop RPC client and server connections, defaulting to QOP values from configuration.

Important APIs and types: It implements `Configurable`, has static `getInstance(Configuration)` for configurable subclass selection, `setConf()`, `getDefaultProperties()`, server/client property lookup overloads, and static `getSaslProperties()` for subclasses.

Control flow and state: `setConf()` reads `hadoop.rpc.protection`, maps configured `QualityOfProtection` names to SASL QOP strings, joins them, and sets `Sasl.SERVER_AUTH` to true. Default client and server lookup methods return the same stored property map; port-aware overloads delegate to address-only methods.

Dependencies and integration: It depends on Hadoop configuration keys, `SaslRpcServer.QualityOfProtection`, Java SASL constants, and `ReflectionUtils`. `SaslRpcClient`, RPC servers, and `IngressPortBasedResolver` use it.

Risks and test signals: Tests should cover QOP list mapping, invalid QOP names, custom resolver instantiation, and returned map contents. The stored map is mutable if exposed directly, so callers could accidentally alter resolver state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslPropertiesResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslRpcClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslRpcClient.java

Purpose: `SaslRpcClient` performs client-side Hadoop IPC SASL negotiation, selects a compatible authentication method, validates Kerberos principals or token credentials, and wraps RPC streams when negotiated QOP requires it.

Important APIs and types: Construction takes `UserGroupInformation`, protocol class, server address, and configuration. Public APIs include `saslConnect(IpcStreams)`, `getInputStream()`, `getOutputStream()`, `dispose()`, `getAuthMethod()`, and test-visible principal/property helpers. It uses protobuf RPC headers, `RpcSaslProto`, `AuthMethod`, `TokenInfo`, `KerberosInfo`, `SaslPropertiesResolver`, and a static `FastSaslClientFactory`.

Control flow: `saslConnect()` starts with a NEGOTIATE request, then loops over SASL RPC responses. On `NEGOTIATE`, `selectSaslClient()` chooses the first valid server-advertised auth method that the client supports and has credentials for; SIMPLE switches without a SASL client, TOKEN creates a DIGEST client using a selected delegation token, and KERBEROS verifies the real auth method and validates the server principal from protocol annotation/config or pattern. CHALLENGE responses are evaluated with the SASL client; SUCCESS verifies client completion. RPC ERROR/FATAL responses become `RemoteException`; non-SASL responses or malformed packets become `SaslException`.

State and persistence: State is per connection: UGI, protocol, server address, configuration, resolver, selected auth method, and `SaslClient`. There is no persistence. `dispose()` clears SASL resources. `getInputStream()` and `getOutputStream()` wrap streams only when negotiated QOP is not `auth`; wrapped RPC output sends `SaslState.WRAP` messages, and wrapped input rejects non-wrapped responses.

Dependencies and integration: It integrates deeply with Hadoop IPC framing, UGI tokens, `SecurityUtil`, Kerberos principal annotations, token selectors, `RpcWritable`, and SASL providers. It exposes attempted auth method so higher-level clients can decide whether Kerberos relogin may help after connection failure.

Risks and test signals: Tests should cover auth selection ordering, invalid advertised methods, missing tokens, token selector instantiation failures, Kerberos principal pattern and exact-match validation, bad Kerberos config mapped to non-retryable SASL errors, unsolicited challenges, premature server success, malformed packets, SIMPLE fallback, stream wrapping, and non-wrapped response rejection. Security risks include accepting SIMPLE when server offers it and configuration permits it, and relying on exact principal validation correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslRpcClient.java -->
