# subset-b-007368 Research

Grouped source research for Hadoop Common security authorization, HTTP security filters, protobuf refresh protocol translators, SSL support, and delegation-token primitives. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/AccessControlList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/AccessControlList.java

## Purpose

`AccessControlList` is Hadoop's public, Writable representation of a user/group ACL string. It parses strings in the form `users groups`, supports the wildcard `*`, and is used by service authorization and proxy-user authorization paths.

## Important APIs, Types, and Functions

The class exposes constructors from a combined ACL string or separate user/group strings, mutators `addUser`, `addGroup`, `removeUser`, `removeGroup`, accessors `getUsers`, `getGroups`, `isAllAllowed`, and checks `isUserInList`/`isUserAllowed`. It implements `Writable` through `write` and `readFields`, registers a `WritableFactory`, and defines the special `USE_REAL_ACLS` prefix `~` for proxied-user real-user ACL checks.

## Control Flow

Construction calls `buildACL`, which initializes hash sets, detects `*` in either ACL part, parses comma-separated users and groups with Hadoop string utilities, and preloads configured groups into the `Groups` cache. Authorization first checks wildcard and short username, then compares the user's group set, then permits a proxy user if the ACL contains `~` plus the real user's short name.

## State and Persistence Behavior

State is in-memory collections for users and groups plus the `allAllowed` flag. Persistence is only Hadoop Writable serialization of `getAclString`; because users/groups are hash-backed collections, serialized order is not a stable input-order guarantee.

## Dependencies and Integration Points

It depends on `UserGroupInformation`, `Groups`, Hadoop `Text`/`Writable`, `WritableFactories`, and `StringUtils`. It integrates with `DefaultImpersonationProvider`, `ServiceAuthorizationManager`, policy XML ACL keys, and any Hadoop service that persists ACLs through Writable.

## Risks and Edge Cases

Wildcard entries are only accepted when the trimmed part is exactly `*`; attempts to add or remove wildcard as a user/group throw. Empty ACLs deny all users. Real-user ACLs only work for proxied UGI objects. Returning mutable collections can let callers mutate state despite documentation. Hash-set ordering can make round-tripped ACL strings nondeterministic.

## Test Signals

Useful tests cover user-only, group-only, empty, wildcard, separate constructor, Writable round trip, proxied UGI with `~realUser`, mutation rejection for `*`, and group cache behavior after adding configured groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/AccessControlList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/AuthorizationException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/AuthorizationException.java

## Purpose

`AuthorizationException` is the service/proxy authorization failure exception used in Hadoop security code. It extends `AccessControlException` while deliberately suppressing stack trace exposure for security-sensitive failures.

## Important APIs, Types, and Functions

It provides default, message, and cause constructors. It overrides `getStackTrace` and all `printStackTrace` variants to return or print only the exception text, not frame details.

## Control Flow

Callers throw it when ACL, principal, proxy-user, or host checks fail. The overridden printing methods short-circuit normal throwable stack trace rendering.

## State and Persistence Behavior

The class has no mutable instance state beyond inherited exception fields. The shared static empty `StackTraceElement[]` is returned from `getStackTrace`.

## Dependencies and Integration Points

It depends on Hadoop `AccessControlException` and is thrown by `DefaultImpersonationProvider`, `ProxyUsers`, `ServiceAuthorizationManager`, and `ImpersonationProvider` default hostname resolution.

## Risks and Edge Cases

Suppressed stack traces are intentional but reduce operational debugging context. The cause constructor can still preserve cause metadata, but printed output hides stack frames.

## Test Signals

Tests should assert thrown type/messages from authorization failures and confirm stack trace access/printing does not expose frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/AuthorizationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/DefaultImpersonationProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/DefaultImpersonationProvider.java

## Purpose

`DefaultImpersonationProvider` implements Hadoop's standard proxy-user authorization. It reads `hadoop.proxyuser.<superuser>.users`, `.groups`, and `.hosts` style settings, then validates whether a real user may impersonate an effective user from a remote address.

## Important APIs, Types, and Functions

The class implements `ImpersonationProvider` with `setConf`, `getConf`, `init`, and `authorize`. It exposes key builders `getProxySuperuserUserConfKey`, `getProxySuperuserGroupConfKey`, and `getProxySuperuserIpConfKey`, plus testing accessors for loaded groups/hosts and a singleton `getTestProvider`.

## Control Flow

`init` normalizes the prefix, uses regex-based configuration scans to collect user/group ACLs and host lists, builds one `AccessControlList` per proxy superuser, and one `MachineList` per hosts key. `authorize` returns immediately for non-proxy UGI, otherwise loads the real user, checks the effective user against the real user's ACL, then checks the remote `InetAddress` against the configured host `MachineList`.

## State and Persistence Behavior

Loaded ACLs and host lists are in mutable maps on the provider instance. There is no file persistence; refresh is achieved by constructing/reinitializing provider instances through `ProxyUsers`.

## Dependencies and Integration Points

It depends on `Configuration.getValByRegex`, `AccessControlList`, `MachineList`, `UserGroupInformation`, and `ProxyUsers.CONF_HADOOP_PROXYUSER`. It is the default implementation selected by `ProxyUsers` unless configuration names another `ImpersonationProvider`.

## Risks and Edge Cases

Missing ACLs or missing hosts deny proxy authorization. The prefix regex uses non-whitespace superuser key matching, so malformed keys may be skipped. Host checks use resolved `InetAddress`, so DNS/address normalization matters. `getTestProvider` is shared mutable global test state.

## Test Signals

Tests should cover wildcard users/groups/hosts, user-only and group-only proxy permissions, denied host, denied effective user, non-proxy UGI bypass, custom prefixes, refresh replacement via `ProxyUsers`, and unresolved/malformed host settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/DefaultImpersonationProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ImpersonationProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ImpersonationProvider.java

## Purpose

`ImpersonationProvider` is the extension point for Hadoop proxy-user authorization policy. Implementations load proxy-user configuration and authorize doAs requests.

## Important APIs, Types, and Functions

It extends `Configurable`, defines `init(String configurationPrefix)`, `authorize(UserGroupInformation, InetAddress)`, and a default `authorize(UserGroupInformation, String)` that resolves the string to an `InetAddress`.

## Control Flow

The default string-address method performs DNS/address resolution and wraps `UnknownHostException` in `AuthorizationException`. Implementations own the policy-specific flow after initialization.

## State and Persistence Behavior

The interface owns no state. Implementations typically keep loaded configuration in memory and refresh by replacement.

## Dependencies and Integration Points

It depends on `UserGroupInformation`, `InetAddress`, Hadoop `Configurable`, and `AuthorizationException`. `ProxyUsers` instantiates implementations from `hadoop.security.impersonation.provider.class`.

## Risks and Edge Cases

The string overload can introduce DNS lookup cost or resolution failure; callers with an existing `InetAddress` should prefer the address overload. Custom providers must define refresh-safe state behavior.

## Test Signals

Tests should verify provider selection, init prefix handling, the string overload's unknown-host conversion, and parity between string and `InetAddress` authorization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ImpersonationProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/PolicyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/PolicyProvider.java

## Purpose

`PolicyProvider` supplies the set of Hadoop RPC services and protocol classes that participate in service-level authorization.

## Important APIs, Types, and Functions

It defines `POLICY_PROVIDER_CONFIG`, `DEFAULT_POLICY_PROVIDER`, and abstract `getServices()`. Each returned `Service` ties a configuration ACL key to a protocol class.

## Control Flow

There is no runtime algorithm in this class. `ServiceAuthorizationManager.refreshWithLoadedConfiguration` calls `getServices` and materializes ACL and host rules for each service.

## State and Persistence Behavior

The abstract class is stateless; persistence lives in Hadoop configuration resources such as `hadoop-policy.xml`.

## Dependencies and Integration Points

It integrates directly with `ServiceAuthorizationManager` and the configured policy provider class for HDFS, MapReduce, and related services.

## Risks and Edge Cases

A provider returning null or omitting a service leaves that protocol unknown to service authorization. Mis-keyed service definitions silently fall back to default ACLs/hosts.

## Test Signals

Tests should assert provider service arrays are complete and that service keys map to the intended protocol ACLs after authorization-manager refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/PolicyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ProxyServers.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ProxyServers.java

## Purpose

`ProxyServers` maintains the trusted HTTP proxy server allowlist used by Hadoop proxy-related security code.

## Important APIs, Types, and Functions

It defines `CONF_HADOOP_PROXYSERVERS`, `refresh()`, `refresh(Configuration)`, and `isProxyServer(String)`.

## Control Flow

`refresh` reads trimmed host strings from configuration, resolves each through `InetSocketAddress(host, 0)`, stores resolved IP addresses, and publishes the collection through a volatile static field. `isProxyServer` lazily refreshes with default configuration if needed and checks membership by remote address string.

## State and Persistence Behavior

State is a process-wide volatile collection of resolved IP address strings. There is no persistence beyond configuration reload.

## Dependencies and Integration Points

It depends on Hadoop `Configuration` and Java network address resolution. `ProxyUsers.refreshSuperUserGroupsConfiguration` refreshes proxy servers alongside proxy-user rules.

## Risks and Edge Cases

Unresolved hosts are ignored. Matching is by resolved IP string, so hostname aliases and DNS changes require refresh. The lazy default refresh can use an unexpected classpath configuration if callers did not explicitly refresh.

## Test Signals

Tests should cover resolved and unresolved hosts, explicit refresh replacement, lazy refresh behavior, and matching by IP address rather than hostname.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ProxyServers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ProxyUsers.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ProxyUsers.java

## Purpose

`ProxyUsers` is the static facade for Hadoop proxy-user authorization. It selects an `ImpersonationProvider`, refreshes proxy-user rules, and delegates doAs authorization checks.

## Important APIs, Types, and Functions

It defines `CONF_HADOOP_PROXYUSER`, refresh overloads, `authorize` overloads for string and `InetAddress`, deprecated `authorize(..., Configuration)`, and `getDefaultImpersonationProvider` for tests. It uses `hadoop.security.impersonation.provider.class` to select custom implementations.

## Control Flow

Refresh validates the prefix, creates a provider with `ReflectionUtils`, initializes it with the prefix, stores it in volatile `sip`, and refreshes `ProxyServers`. Authorization lazily refreshes if `sip` is null, then delegates to the current provider.

## State and Persistence Behavior

The current provider is a process-wide volatile singleton. Reconfiguration is atomic at the reference level; old provider instances may still be used by in-flight calls.

## Dependencies and Integration Points

It depends on `DefaultImpersonationProvider`, `ImpersonationProvider`, `Configuration`, `UserGroupInformation`, `ProxyServers`, and common security configuration keys. It is called by RPC, HTTP, and service components that support doAs.

## Risks and Edge Cases

Lazy default refresh can load default configuration unexpectedly. The test accessor assumes the active provider is `DefaultImpersonationProvider` and will fail for custom providers. Deprecated overload ignores the passed configuration except through already refreshed state.

## Test Signals

Tests should verify provider replacement, custom provider configuration, prefix validation, lazy refresh, string/address authorization parity, and proxy server refresh coupling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ProxyUsers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/RefreshAuthorizationPolicyProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/RefreshAuthorizationPolicyProtocol.java

## Purpose

`RefreshAuthorizationPolicyProtocol` is the RPC protocol for refreshing service-level authorization policy in a running Hadoop daemon.

## Important APIs, Types, and Functions

It defines protocol `versionID = 1L` and idempotent `refreshServiceAcl()`. `@KerberosInfo` points at the Hadoop service principal key.

## Control Flow

Implementing daemons receive the RPC and reload authorization ACL policy, typically through `ServiceAuthorizationManager.refresh`.

## State and Persistence Behavior

The interface owns no state. Its implementations mutate daemon-local authorization-manager state from configuration/policy resources.

## Dependencies and Integration Points

It integrates with Hadoop IPC, Kerberos principal discovery, protobuf translators in `protocolPB`, and admin refresh commands.

## Risks and Edge Cases

Failed reloads should surface as `IOException`; because the method is idempotent, clients may retry. Incorrect Kerberos principal configuration can prevent the refresh RPC from being invoked.

## Test Signals

Tests should cover protobuf translator invocation, method support lookup, Kerberos annotation metadata, successful reload, and propagation of implementation `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/RefreshAuthorizationPolicyProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/Service.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/Service.java

## Purpose

`Service` is the small data holder that binds a service-level authorization configuration key to a Hadoop RPC protocol class.

## Important APIs, Types, and Functions

It has a constructor `Service(String key, Class<?> protocol)` and getters `getServiceKey()` and `getProtocol()`.

## Control Flow

There is no internal branching. `PolicyProvider` returns arrays of `Service`, and `ServiceAuthorizationManager` iterates them to build ACL and host maps.

## State and Persistence Behavior

The object holds only the key and protocol reference in memory. Policy persistence is external in configuration resources.

## Dependencies and Integration Points

It is used by policy provider implementations for HDFS, MapReduce, and other Hadoop daemons.

## Risks and Edge Cases

The class does not validate null keys or protocols. Incorrect service keys can make services inherit defaults rather than explicit policy.

## Test Signals

Tests should verify provider arrays contain correct key/protocol pairs and that manager refresh maps them to the expected ACLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/Service.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ServiceAuthorizationManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ServiceAuthorizationManager.java

## Purpose

`ServiceAuthorizationManager` enforces service-level authorization for Hadoop RPC protocols. It checks allowed/blocked user ACLs, Kerberos client principal constraints, and allowed/blocked client host lists.

## Important APIs, Types, and Functions

Primary APIs are `authorize(UserGroupInformation, Class<?>, Configuration, InetAddress)`, `refresh(Configuration, PolicyProvider)`, and `refreshWithLoadedConfiguration`. It keeps `protocolToAcls` and `protocolToMachineLists` as volatile identity maps, defines suffixes `.blocked` and `.hosts`, and provides testing accessors for loaded ACLs/hosts.

## Control Flow

`refresh` copies configuration, loads the policy resource named by system property `hadoop.policy.file` or `hadoop-policy.xml`, then delegates to `refreshWithLoadedConfiguration`. Refresh builds fresh identity maps from provider services, using default allow/block ACLs and default allow/block machine lists when service-specific keys are absent, then atomically flips the volatile references. `authorize` fails unknown protocols, resolves the client principal when security is enabled, denies mismatched principal, denied allowed ACL, matched blocked ACL, non-included host, or matched blocked host, and logs audit success/failure.

## State and Persistence Behavior

Authorization state is held in volatile maps for lock-free reads and atomic refresh replacement. Policy persistence lives in Hadoop XML configuration and system property-selected policy files.

## Dependencies and Integration Points

It depends on `AccessControlList`, `MachineList`, `SecurityUtil`, `UserGroupInformation`, `CommonConfigurationKeys`, `PolicyProvider`, `Service`, and audit logging. It is invoked by Hadoop RPC server paths before dispatching protocol calls.

## Risks and Edge Cases

Identity maps require the exact protocol `Class<?>` object used during refresh. Defaults can unintentionally allow all users/hosts if policy keys are absent. Host authorization is skipped when `addr` is null. Principal resolution failures are converted to authorization failures.

## Test Signals

Tests should cover unknown protocols, allowed and blocked ACL precedence, allowed and blocked host precedence, security-enabled principal mismatch, null-address behavior, policy-file refresh, volatile map replacement, and default policy fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ServiceAuthorizationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.security.authorize` as Hadoop's service-level authorization support package.

## Important APIs, Types, and Functions

It declares package annotations `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

The file owns no state or persistence.

## Dependencies and Integration Points

It imports Hadoop classification annotations and applies them to the package containing ACLs, proxy-user authorization, policy providers, and service authorization management.

## Risks and Edge Cases

The main risk is documentation/annotation drift if package audience or stability changes.

## Test Signals

Compile/package-javadoc generation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/CrossOriginFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/CrossOriginFilter.java

## Purpose

`CrossOriginFilter` is Hadoop's servlet CORS filter. It validates request origin, requested method, and requested headers against init-parameter allowlists, then emits CORS response headers when checks pass.

## Important APIs, Types, and Functions

The filter defines init params `allowed-origins`, `allowed-methods`, `allowed-headers`, and `max-age` with defaults. Core methods are `init`, `doFilter`, `destroy`, `doCrossFilter`, `encodeHeader`, `areOriginsAllowed`, `isMethodAllowed`, and `areHeadersAllowed`.

## Control Flow

Initialization splits comma-separated config values and detects `*` origin allowance. `doFilter` calls `doCrossFilter` and always continues the chain. `doCrossFilter` sanitizes `Origin` against CR/LF response splitting, returns without setting CORS headers for non-CORS, disallowed origins, methods, or headers, and otherwise sets `Access-Control-Allow-*` headers.

## State and Persistence Behavior

Allowed methods, headers, origins, `allowAllOrigins`, and `maxAge` are in-memory filter instance state. `destroy` clears the lists. No persistent state is written.

## Dependencies and Integration Points

It depends on the Servlet API, Apache Commons `StringUtils`, regex `Pattern`, SLF4J, and Hadoop test visibility annotations. Hadoop HTTP servers add it through filter initializers.

## Risks and Edge Cases

Legacy wildcard patterns without the `regex:` prefix are still accepted but discouraged. Header and method comparisons are case-sensitive. Multiple origins are split on whitespace. The filter does not reject requests; it only omits CORS headers. Regex patterns are compiled during request checks, so complex configs can add per-request cost.

## Test Signals

Tests should cover null origin, CR/LF header sanitization, wildcard origins, exact origins, `regex:` origins, legacy wildcard warnings, requested method/header denial, response header values, and destroy clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/CrossOriginFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/RestCsrfPreventionFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/RestCsrfPreventionFilter.java

## Purpose

`RestCsrfPreventionFilter` protects Hadoop REST endpoints by requiring browser-originated, state-changing requests to carry a configured anti-CSRF header.

## Important APIs, Types, and Functions

It exposes init params `browser-useragents-regex`, `custom-header`, and `methods-to-ignore`; defaults are browser regexes `^Mozilla.*`/`^Opera.*`, header `X-XSRF-HEADER`, and ignored methods `GET,OPTIONS,HEAD,TRACE`. Important methods are `init`, `parseBrowserUserAgents`, `parseMethodsToIgnore`, `isBrowser`, `handleHttpInteraction`, `doFilter`, and static `getFilterParams`. Nested `HttpInteraction` abstracts servlet and non-servlet integrations.

## Control Flow

Initialization compiles browser regex patterns and method ignore sets. `handleHttpInteraction` allows the request if the user agent is not considered a browser, the method is ignored, or the required header exists; otherwise it sends HTTP 400. The servlet adapter wraps `HttpServletRequest`, `HttpServletResponse`, and `FilterChain`.

## State and Persistence Behavior

State is per-filter instance: header name, ignored method set, and browser regex set. There is no persistence.

## Dependencies and Integration Points

It depends on Servlet APIs, Jetty `Response` for reason phrase handling, Hadoop `Configuration.getPropsWithPrefix`, and SLF4J. It integrates with Hadoop web UI/REST filter chains and can be used through the abstract `HttpInteraction`.

## Risks and Edge Cases

Method parsing does not trim values, so spaces in config can break matching. Browser detection depends entirely on regex config and ignores null user agents. Only header presence is checked, not value. Jetty-specific status reason behavior is conditional.

## Test Signals

Tests should cover browser/non-browser user agents, default ignored methods, custom header names, missing-header 400, custom method list whitespace behavior, `getFilterParams`, and servlet adapter response behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/RestCsrfPreventionFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/XFrameOptionsFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/XFrameOptionsFilter.java

## Purpose

`XFrameOptionsFilter` adds and preserves the `X-Frame-Options` response header to protect Hadoop web applications from clickjacking.

## Important APIs, Types, and Functions

It defines header `X-Frame-Options`, init param `xframe-options`, default option `DENY`, static `getFilterParams`, and nested `XFrameOptionsResponseWrapper` that blocks later changes to that header.

## Control Flow

`init` optionally replaces the default option. `doFilter` sets the configured header on the original response, then passes a wrapper down the chain. The wrapper suppresses subsequent add/set operations for the protected header while allowing other headers through.

## State and Persistence Behavior

The configured option is per-filter instance state. No persistent state is written.

## Dependencies and Integration Points

It depends on Servlet APIs and Hadoop `Configuration`. Hadoop HTTP servers can initialize it from prefixed configuration.

## Risks and Edge Cases

Header-name comparisons are case-sensitive, while HTTP header names are semantically case-insensitive. The wrapper's `containsHeader` implementation returns false for non-protected headers because it does not return `super.containsHeader(name)`, which can affect downstream filters.

## Test Signals

Tests should cover default/custom option, prevention of downstream overwrite/add, non-protected header pass-through, `containsHeader` behavior, and config prefix extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/XFrameOptionsFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.security.http` as the package for Hadoop HTTP security filters.

## Important APIs, Types, and Functions

It declares package annotations `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

The file owns no state or persistence.

## Dependencies and Integration Points

It imports Hadoop classification annotations for the package containing CORS, CSRF, and frame-options filters.

## Risks and Edge Cases

The main risk is annotation drift relative to the stability of the contained filter APIs.

## Test Signals

Compile and javadoc/package metadata generation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/package-info.java

## Purpose

This package descriptor documents the top-level `org.apache.hadoop.security` package.

## Important APIs, Types, and Functions

It applies `@InterfaceAudience.LimitedPrivate({"HDFS", "MapReduce", "YARN", "HBase"})` to the package.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

The file owns no state or persistence.

## Dependencies and Integration Points

It imports the Hadoop classification annotation and marks the package that contains UGI, security utilities, group mapping, SASL, credentials, and related security infrastructure.

## Risks and Edge Cases

The only substantive risk is stale audience metadata if top-level package exposure changes.

## Test Signals

Compilation and javadoc/package annotation generation are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolClientSideTranslatorPB.java

## Purpose

This client-side translator adapts the Java `RefreshAuthorizationPolicyProtocol` interface to the protobuf-based Hadoop IPC stub.

## Important APIs, Types, and Functions

It implements `ProtocolMetaInterface`, `RefreshAuthorizationPolicyProtocol`, and `Closeable`. Key methods are the constructor taking `RefreshAuthorizationPolicyProtocolPB`, `refreshServiceAcl`, `isMethodSupported`, and `close`.

## Control Flow

`refreshServiceAcl` sends a cached empty `RefreshServiceAclRequestProto` through `rpcProxy.refreshServiceAcl` using a null controller and Hadoop's shaded protobuf IPC helper. `isMethodSupported` delegates to `RpcClientUtil`; `close` stops the proxy.

## State and Persistence Behavior

State is only the RPC proxy reference and static empty request object. No persistence exists.

## Dependencies and Integration Points

It depends on Hadoop IPC `RPC`, `RpcClientUtil`, protobuf request types, and the PB protocol interface. It is used by admin clients invoking authorization-policy refresh.

## Risks and Edge Cases

The translator has no retry logic beyond the RPC layer. Failure conversion relies on `ShadedProtobufHelper.ipc`. Callers must close it to stop the proxy.

## Test Signals

Tests should verify one RPC call is issued, IOException propagation, method support lookup arguments, and `close` stopping the proxy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolPB.java

## Purpose

`RefreshAuthorizationPolicyProtocolPB` is the protobuf IPC surface for authorization-policy refresh.

## Important APIs, Types, and Functions

The interface extends generated `RefreshAuthorizationPolicyProtocolService.BlockingInterface` and carries `@KerberosInfo` plus `@ProtocolInfo` with protocol name `org.apache.hadoop.security.authorize.RefreshAuthorizationPolicyProtocol` and version `1`.

## Control Flow

There is no method implementation; generated protobuf service methods define the actual RPC shape.

## State and Persistence Behavior

No state or persistence is owned.

## Dependencies and Integration Points

It integrates the generated protobuf service with Hadoop IPC protocol registration, Kerberos principal lookup, client-side translators, and server-side translators.

## Risks and Edge Cases

Protocol name/version mismatches break compatibility with existing clients and servers. Kerberos annotation drift can break secure RPC setup.

## Test Signals

Tests should cover protocol metadata, server registration, client translator compatibility, and secure RPC principal lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolServerSideTranslatorPB.java

## Purpose

This server-side translator adapts protobuf refresh-authorization RPC calls to a Java `RefreshAuthorizationPolicyProtocol` implementation.

## Important APIs, Types, and Functions

It implements `RefreshAuthorizationPolicyProtocolPB`, stores an `impl`, and exposes `refreshServiceAcl(RpcController, RefreshServiceAclRequestProto)`.

## Control Flow

The RPC method calls `impl.refreshServiceAcl()`, wraps any `IOException` in `ServiceException`, and returns a cached empty response proto.

## State and Persistence Behavior

State is only the delegated implementation and static response instance. Persistence is handled by the implementation being refreshed.

## Dependencies and Integration Points

It depends on generated protobuf request/response types, `ServiceException`, and the Java refresh protocol. Hadoop RPC servers use it to expose refresh operations.

## Risks and Edge Cases

All implementation failures are collapsed into `ServiceException`. The request payload is ignored, so future request fields would require protocol evolution.

## Test Signals

Tests should verify delegate invocation, empty response return, and IOException-to-ServiceException conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolClientSideTranslatorPB.java

## Purpose

This client-side translator adapts `RefreshUserMappingsProtocol` to protobuf RPC calls for refreshing user-to-groups and proxy-user mappings.

## Important APIs, Types, and Functions

It implements `ProtocolMetaInterface`, `RefreshUserMappingsProtocol`, and `Closeable`. Methods are `refreshUserToGroupsMappings`, `refreshSuperUserGroupsConfiguration`, `isMethodSupported`, and `close`.

## Control Flow

Each refresh method sends a cached empty request proto to the matching PB method with a null controller through the shaded protobuf IPC helper. Method support and close behavior delegate to Hadoop IPC utilities.

## State and Persistence Behavior

State is the PB proxy reference and static empty request instances. Refreshed mapping state lives in the daemon-side implementation.

## Dependencies and Integration Points

It depends on `RefreshUserMappingsProtocolPB`, generated protobuf messages, Hadoop IPC, and the Java `RefreshUserMappingsProtocol`.

## Risks and Edge Cases

No payload fields are sent, and all error semantics depend on IPC helper conversion. Leaking translators can leave proxy resources active.

## Test Signals

Tests should assert both refresh RPCs call the correct PB methods, exceptions propagate as IOException, method support checks use the PB interface/version, and close stops the proxy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolPB.java

## Purpose

`RefreshUserMappingsProtocolPB` is the protobuf IPC protocol interface for refreshing user/group and proxy-user mappings.

## Important APIs, Types, and Functions

It extends generated `RefreshUserMappingsProtocolService.BlockingInterface` and carries Kerberos and protocol metadata with protocol name `org.apache.hadoop.security.RefreshUserMappingsProtocol` and version `1`.

## Control Flow

No implementation exists in this interface; generated protobuf service methods are implemented by server-side translators.

## State and Persistence Behavior

The interface owns no state or persistence.

## Dependencies and Integration Points

It integrates generated protobuf services with Hadoop IPC registration and secure principal lookup.

## Risks and Edge Cases

Changing protocol name/version or Kerberos key metadata would break wire compatibility or secure RPC setup.

## Test Signals

Tests should cover protocol metadata, translator compatibility, and secure RPC registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolServerSideTranslatorPB.java

## Purpose

This server-side translator adapts protobuf refresh-user-mappings RPC calls to a Java `RefreshUserMappingsProtocol` implementation.

## Important APIs, Types, and Functions

It implements `RefreshUserMappingsProtocolPB`, stores an `impl`, and exposes `refreshUserToGroupsMappings` and `refreshSuperUserGroupsConfiguration`.

## Control Flow

Each RPC method invokes the matching Java implementation method, catches `IOException`, wraps it in `ServiceException`, and returns a cached empty response proto.

## State and Persistence Behavior

State is the implementation reference and static empty responses. Actual mapping state is owned by the implementation.

## Dependencies and Integration Points

It depends on generated refresh-user-mappings protobuf types, `ServiceException`, and the Java refresh protocol. Hadoop daemons use it when exposing admin refresh RPCs.

## Risks and Edge Cases

Request messages are ignored; adding request fields would require protocol changes. Implementation errors are all represented as protobuf service failures.

## Test Signals

Tests should verify both delegate calls, response construction, and IOException-to-ServiceException conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/DelegatingSSLSocketFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/DelegatingSSLSocketFactory.java

## Purpose

`DelegatingSSLSocketFactory` is a singleton `SSLSocketFactory` that can use WildFly OpenSSL or JSSE, with compatibility modes for Java 8 GCM cipher behavior.

## Important APIs, Types, and Functions

The `SSLChannelMode` enum includes `OpenSSL`, `Default`, `Default_JSSE`, and `Default_JSSE_with_GCM`. Static APIs are `initializeDefaultFactory`, `getDefaultFactory`, and test-only `resetDefaultFactory`. Instance APIs expose provider name, channel mode, cipher suites, and all socket creation overloads.

## Control Flow

Initialization creates the singleton once. `Default` attempts OpenSSL registration and `openssl.TLS` context initialization, falling back to JSSE on linkage/algorithm/runtime errors. Explicit `OpenSSL` fails if binding fails. JSSE modes use the default context. On Java 8 in `Default_JSSE`, GCM cipher suites are removed before sockets are configured.

## State and Persistence Behavior

State is a static singleton plus instance provider name, SSL context, selected ciphers, channel mode, and OpenSSL registration flag. No file persistence is used.

## Dependencies and Integration Points

It depends on JSSE, WildFly OpenSSL by fully qualified reference inside the binding method, SLF4J, and Java util logging. It is primarily used by Hadoop components that optionally prefer OpenSSL-backed sockets.

## Risks and Edge Cases

`getDefaultFactory` may return null if initialization was not called. Singleton initialization means later preferred modes are ignored until reset in tests. Cipher filtering only removes `_GCM_` names in one mode on Java 8. OpenSSL provider loading depends on optional classpath/native setup.

## Test Signals

Tests should cover each mode, default fallback, singleton reset, provider name, cipher list cloning, Java 8 GCM filtering, all socket overloads setting enabled ciphers, and behavior when WildFly OpenSSL is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/DelegatingSSLSocketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/FileBasedKeyStoresFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/FileBasedKeyStoresFactory.java

## Purpose

`FileBasedKeyStoresFactory` loads SSL key managers and trust managers from configured keystore/truststore files and schedules reload checks when those files change.

## Important APIs, Types, and Functions

It implements `KeyStoresFactory` with `setConf`, `getConf`, `init`, `destroy`, `getKeyManagers`, and `getTrustManagers`. It defines client/server property templates for keystore, truststore, passwords, types, and reload intervals, plus `resolvePropertyName` and `getPassword`.

## Control Flow

`init` reads whether client certs are required, creates a daemon `Timer`, resolves mode-specific keystore/truststore type and paths, and either loads a reloading keystore manager or creates an empty keystore-backed manager for clients that do not need certs. If a truststore location is configured, it creates a `ReloadingX509TrustManager`. For positive reload intervals, it schedules `FileMonitoringTimerTask` instances that call manager `loadFrom`.

## State and Persistence Behavior

State includes loaded key manager arrays, trust manager arrays, optional reloading trust manager, and a timer. It reads local keystore/truststore files and credential-provider passwords but writes nothing. `destroy` cancels the timer and clears manager references when a trust manager exists.

## Dependencies and Integration Points

It depends on `SSLFactory.Mode`, `ReloadingX509KeystoreManager`, `ReloadingX509TrustManager`, `FileMonitoringTimerTask`, JSSE `KeyStore`/`KeyManagerFactory`, Hadoop `Configuration.getPassword`, and credential-provider integration.

## Risks and Edge Cases

Server mode and client-cert-required mode require keystore location and password. Empty truststore password is treated as null and allowed. `destroy` only clears manager arrays inside the `trustManager != null` branch, so client/server configurations without truststore keep arrays after timer cancellation. Reload failure logs and keeps existing managers.

## Test Signals

Tests should cover client/server property resolution, missing keystore failures, credential-provider password lookup, empty truststore password, reload interval zero and positive scheduling, truststore absence, timer cancellation, and reload preserving previous state on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/FileBasedKeyStoresFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/FileMonitoringTimerTask.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/FileMonitoringTimerTask.java

## Purpose

`FileMonitoringTimerTask` is a reusable timer task that detects local file modification-time changes and invokes a callback, used for SSL store reloads.

## Important APIs, Types, and Functions

It provides constructors for one path or a list of paths, stores an `onFileChange` callback and optional failure callback, and implements `run`.

## Control Flow

Construction snapshots each file's current `lastModified`. `run` scans paths until it finds the first changed timestamp, calls `onFileChange` for that path, catches any throwable and sends it to `onChangeFailure` or logs it, then updates that path's last-processed timestamp.

## State and Persistence Behavior

State is the monitored path list and matching last-modified timestamp list. It reads file metadata only and persists nothing.

## Dependencies and Integration Points

It depends on `TimerTask`, `Path`, Java functional `Consumer`, Hadoop `Preconditions`, and SLF4J. `FileBasedKeyStoresFactory` schedules it for keystore/truststore reload.

## Risks and Edge Cases

Only the first changed file is processed per run. Timestamp granularity can miss rapid successive changes. If a reload callback fails, the timestamp is still advanced after handling, so a failed reload may not retry until the file changes again.

## Test Signals

Tests should cover null argument rejection, single and multiple path detection, callback invocation, failure callback/log fallback, timestamp advancement, and first-change-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/FileMonitoringTimerTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/KeyStoresFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/KeyStoresFactory.java

## Purpose

`KeyStoresFactory` abstracts SSL key manager and trust manager creation for Hadoop's `SSLFactory`.

## Important APIs, Types, and Functions

It extends `Configurable` and declares `init(SSLFactory.Mode)`, `destroy`, `getKeyManagers`, and `getTrustManagers`.

## Control Flow

Implementations initialize key/trust managers for client or server mode and expose the arrays to `SSLFactory`.

## State and Persistence Behavior

The interface owns no state. Implementations may read keystore files, schedule reloads, or hold manager arrays.

## Dependencies and Integration Points

It depends on JSSE `KeyManager`/`TrustManager`, `SSLFactory.Mode`, and Hadoop configuration. `SSLFactory` creates the configured implementation through reflection.

## Risks and Edge Cases

Custom implementations must match JSSE expectations and clean up resources in `destroy`. Null trust managers may intentionally mean default trust behavior depending on SSL context setup.

## Test Signals

Tests should verify custom factory selection by configuration, mode-specific initialization, returned manager arrays, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/KeyStoresFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/ReloadingX509KeystoreManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/ReloadingX509KeystoreManager.java

## Purpose

`ReloadingX509KeystoreManager` is an `X509ExtendedKeyManager` wrapper that can atomically replace its delegate when a keystore file is reloaded.

## Important APIs, Types, and Functions

The constructor loads the initial key manager from type/location/passwords. `loadFrom(Path)` reloads and swaps the delegate. All `X509ExtendedKeyManager` alias, chain, and key methods delegate to the current manager held in an `AtomicReference`.

## Control Flow

`loadKeyManager` opens the keystore file, loads it with store password, initializes `KeyManagerFactory`, selects the first `X509ExtendedKeyManager`, and returns it. `loadFrom` wraps checked exceptions in `RuntimeException` for timer callback compatibility.

## State and Persistence Behavior

State is immutable keystore metadata and an atomic reference to the active key manager. It reads keystore files but writes nothing.

## Dependencies and Integration Points

It depends on JSSE `KeyStore`, `KeyManagerFactory`, `X509ExtendedKeyManager`, `SSLFactory.KEY_MANAGER_SSLCERTIFICATE`, and `FileBasedKeyStoresFactory` reload scheduling.

## Risks and Edge Cases

If no `X509ExtendedKeyManager` is produced, the reference can become null and delegate calls fail. Reload exceptions are unchecked and rely on caller failure handling to keep prior state. Store/key password mismatch fails reload.

## Test Signals

Tests should cover initial load, alias/key delegation, successful atomic reload, invalid keystore failure preserving previous manager via scheduler handling, null manager edge cases, and key password defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/ReloadingX509KeystoreManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/ReloadingX509TrustManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/ReloadingX509TrustManager.java

## Purpose

`ReloadingX509TrustManager` is an `X509TrustManager` wrapper that atomically reloads truststore contents when requested.

## Important APIs, Types, and Functions

The constructor loads an initial trust manager. It implements `checkClientTrusted`, `checkServerTrusted`, `getAcceptedIssuers`, and `loadFrom(Path)`.

## Control Flow

`loadTrustManager` reads the truststore file, initializes `TrustManagerFactory`, selects the first `X509TrustManager`, and returns it. Trust checks delegate to the current atomic reference or throw `CertificateException` if no manager is available. `loadFrom` wraps failures in `RuntimeException` with a reload message.

## State and Persistence Behavior

State is the truststore type/password and atomic delegate reference. It reads local truststore files and writes nothing.

## Dependencies and Integration Points

It depends on JSSE trust APIs, `SSLFactory.TRUST_MANAGER_SSLCERTIFICATE`, and `FileBasedKeyStoresFactory` file monitoring.

## Risks and Edge Cases

No selected X509 trust manager yields null and causes trust checks to fail. `getAcceptedIssuers` returns an empty static array when no delegate exists. Reload failures must be handled by scheduler callbacks to preserve operational behavior.

## Test Signals

Tests should cover initial truststore load, client/server trust delegation, accepted issuer output, successful reload, invalid reload failure, null-password truststore, and missing X509 manager behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/ReloadingX509TrustManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/SSLFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/SSLFactory.java

## Purpose

`SSLFactory` creates configured SSL contexts, engines, socket factories, and hostname verifiers for Hadoop HTTP clients and servers.

## Important APIs, Types, and Functions

It defines mode enum `CLIENT`/`SERVER`, config keys for client/server SSL resources, client cert requirements, hostname verifier, enabled protocols, keystore/truststore settings, and cipher include/exclude lists. Key methods are constructor, `readSSLConfiguration`, `init`, `destroy`, `createSSLEngine`, `createSSLServerSocketFactory`, `createSSLSocketFactory`, `getHostnameVerifier`, `isClientCertRequired`, and `configure(HttpURLConnection)`.

## Control Flow

The constructor reads the mode-specific SSL configuration resource or falls back to input config if unavailable, instantiates the configured `KeyStoresFactory`, reads enabled protocols and cipher filters, and stores client-cert requirements. `init` initializes stores, creates a TLS `SSLContext`, initializes it with key/trust managers, caches client socket factory, and resolves hostname verifier. Server engines set server mode, client auth, enabled protocols, and filtered cipher suites. HTTPS connections are configured with the client socket factory and verifier.

## State and Persistence Behavior

State includes configuration, mode, SSL context, cached socket factory, hostname verifier, keystores factory, enabled protocols, and cipher filters. It reads XML config and keystore/truststore files through the keystore factory; persistence is external.

## Dependencies and Integration Points

It depends on JSSE, `FileBasedKeyStoresFactory` by default, Hadoop `Configuration`, `ReflectionUtils`, `ConnectionConfigurator`, `SSLHostnameVerifier`, and Hadoop HTTP client/server setup.

## Risks and Edge Cases

Mode-specific methods throw if called in the wrong mode. Fallback to input configuration only occurs when the SSL resource is not loadable. Cipher include/exclude filters can produce an empty enabled suite list. `context.getDefaultSSLParameters().setProtocols` does not itself configure all future sockets; engines are explicitly configured.

## Test Signals

Tests should cover client/server modes, missing mode rejection, SSL resource fallback, custom keystore factory, verifier name selection and invalid verifier failure, enabled protocol setting, cipher include/exclude filtering, HTTPS configuration, and destroy delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/SSLFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/SSLHostnameVerifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/SSLHostnameVerifier.java

## Purpose

`SSLHostnameVerifier` defines Hadoop's hostname verification strategies for X.509 certificates and provides built-in verifier instances ranging from strict checks to allow-all.

## Important APIs, Types, and Functions

It extends `javax.net.ssl.HostnameVerifier` and adds `check` overloads for host/socket, host/certificate, CN/subjectAlt arrays, and multi-host checks. Built-ins are `DEFAULT`, `DEFAULT_AND_LOCALHOST`, `STRICT`, `STRICT_IE6`, and `ALLOW_ALL`. Nested `AbstractVerifier` implements most logic, and nested `Certificates` extracts CNs and DNS subjectAlt names.

## Control Flow

`verify` extracts the peer certificate and calls `check`. Socket checks force session/handshake availability when needed. Certificate checks extract CNs and subject alts, then strategy-specific implementations call the shared check with flags for IE6 multi-CN behavior and strict wildcard subdomain matching. Matching normalizes hosts, prefers subject alts plus the first CN, handles wildcards, rejects risky country-code wildcard patterns, and throws `SSLException` on mismatch.

## State and Persistence Behavior

Verifier instances are stateless singletons. Static sorted arrays define disallowed country-code second-level wildcard segments and localhost names.

## Dependencies and Integration Points

It depends on JSSE `SSLSession`, `SSLSocket`, `X509Certificate`, Hadoop `StringUtils`, and SLF4J. `SSLFactory` selects one of these verifiers from configuration.

## Risks and Edge Cases

`ALLOW_ALL` disables hostname verification. CN parsing uses string tokenization of the X500 principal and can be less robust than a full RFC 2253 parser. SubjectAlt extraction only uses DNS type 2, not IP address SANs. `isIP4Address` checks the first character repeatedly inside a loop, which is unusual and should be regression-tested before changes.

## Test Signals

Tests should cover exact CN, DNS SAN precedence, wildcard matching in default and strict modes, localhost relaxation, allow-all behavior, bad country wildcard rejection, IP and SAN edge cases, failed peer verification, and CN extraction with escaped/complex principals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/SSLHostnameVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DelegationTokenIssuer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DelegationTokenIssuer.java

## Purpose

`DelegationTokenIssuer` is the common interface for services that can issue delegation tokens and recursively collect tokens from dependent child services.

## Important APIs, Types, and Functions

Implementations provide `getCanonicalServiceName` and `getDelegationToken`. Defaults include `getAdditionalTokenIssuers`, `addDelegationTokens`, and static `collectDelegationTokens`.

## Control Flow

`addDelegationTokens` ensures a `Credentials` object exists, then calls `collectDelegationTokens`. Collection checks whether credentials already contain a token for the issuer's canonical service, fetches and stores a new token if absent, records new tokens in an output list, then recursively processes additional token issuers.

## State and Persistence Behavior

The interface owns no state. It mutates the supplied `Credentials` object by adding fetched tokens.

## Dependencies and Integration Points

It depends on `Credentials`, `Token`, `Text`, and SLF4J. File systems and services implement it so clients can gather all required delegation tokens before launching distributed work.

## Risks and Edge Cases

Null canonical service names skip token fetching for that issuer. Recursive child issuer graphs are not cycle-protected. Existing credentials suppress token refresh even if stale.

## Test Signals

Tests should cover absent and existing tokens, null service names, null input credentials, child issuer recursion, token list return values, and exception propagation from token acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DelegationTokenIssuer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtFetcher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtFetcher.java

## Purpose

`DtFetcher` is the ServiceLoader extension interface used by `dtutil` to fetch delegation tokens from service-specific implementations at runtime.

## Important APIs, Types, and Functions

It declares `getServiceName`, `isTokenRequired`, and `addDelegationTokens(Configuration, Credentials, String renewer, String url)`.

## Control Flow

`DtFileOperations.getTokenFile` discovers implementations, matches service name against URL scheme or explicit service option, verifies a token is required, and delegates token addition to the matching fetcher.

## State and Persistence Behavior

The interface owns no state. Implementations mutate the supplied `Credentials` and may return a token suitable for aliasing.

## Dependencies and Integration Points

It depends on `Configuration`, `Credentials`, `Text`, and `Token`. Implementations are loaded through Java `ServiceLoader`.

## Risks and Edge Cases

Multiple fetchers can match the same service. `isTokenRequired` false is treated as an error in dtutil get. Returning null prevents aliasing.

## Test Signals

Tests should cover ServiceLoader discovery, service matching, no-token-required errors, null returned token with alias, and successful credentials mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtFileOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtFileOperations.java

## Purpose

`DtFileOperations` implements the file-level operations behind `hadoop dtutil`: print, fetch, alias, append, remove/cancel, renew, and import delegation tokens.

## Important APIs, Types, and Functions

Public static APIs include `doFormattedWrite`, `printTokenFile`, `printCredentials`, `getTokenFile`, `aliasTokenFile`, `appendTokenFiles`, `removeTokenFromFile`, `renewTokenFile`, and `importTokenFile`. It supports output formats `protobuf` and legacy `java`.

## Control Flow

Operations read `Credentials` from local token files, transform token sets, and write back in the requested format. `getTokenFile` discovers `DtFetcher` implementations with `ServiceLoader`, matches by service/url, calls fetchers to add tokens, optionally aliases the returned token, and writes credentials. Remove optionally cancels managed tokens before dropping them; renew iterates managed matching tokens and writes renewed credentials.

## State and Persistence Behavior

The class is stateless but performs persistent local token-file reads and writes through `Credentials.readTokenStorageFile` and `writeTokenStorageFile`. It can overwrite token files.

## Dependencies and Integration Points

It depends on `Credentials`, `Token`, `TokenIdentifier`, `AbstractDelegationTokenIdentifier`, `DtFetcher`, Hadoop `Path`, local `File`, ServiceLoader, and SLF4J. It is called by `DtUtilShell`.

## Risks and Edge Cases

Append writes merged credentials to the last input file. ServiceLoader errors are logged and skipped. Alias matching compares token service fields. `removeTokenFromFile` drops all matching tokens even if cancel is false, and cancel only invokes `cancel` on managed tokens. Import trusts the provided base64 token encoding.

## Test Signals

Tests should cover both serialization formats, print output for decodable and undecodable identifiers, fetcher matching and aliasing, append destination behavior, remove/cancel/renew managed-token behavior, import with alias, and ServiceLoader failure tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtFileOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtUtilShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtUtilShell.java

## Purpose

`DtUtilShell` is the command-line shell for managing Hadoop delegation-token files through `hadoop dtutil`.

## Important APIs, Types, and Functions

It extends `CommandShell`, defines usage and subcommands `help`, `print`, `get`, `edit`, `append`, `cancel`, `remove`, `renew`, and `import`. It parses options `-keytab`, `-principal`, `-renewer`, `-service`, `-alias`, and `-format`.

## Control Flow

`init` optionally performs Kerberos login when both principal and keytab are supplied, selects a subcommand from the first argument, parses command options, records existing token files and first output file, validates format, and lets subcommands validate/execute. Each subcommand delegates to the corresponding `DtFileOperations` method.

## State and Persistence Behavior

Parsed command state is stored in fields for keytab/principal, alias/service/renewer, format, token files, and first file. Persistent token-file writes are performed by `DtFileOperations`.

## Dependencies and Integration Points

It depends on `CommandShell`, `ToolRunner`, `UserGroupInformation` keytab login, `DtFileOperations`, `Configuration`, `Text`, `File`, and SLF4J. It is the CLI entry point.

## Risks and Edge Cases

The parser is positional and increments indices directly, so missing option values can throw. It only adds existing files to `tokenFiles` but preserves the first filename for commands that create output. For HTTP/HTTPS token get, `-service` is required; for non-generic URLs it is rejected.

## Test Signals

Tests should cover each subcommand's validation, missing option values, login with both/one/no Kerberos options, format validation, output-file creation for get/import, generic URL service requirement, and delegation into `DtFileOperations`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtUtilShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/SecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/SecretManager.java

## Purpose

`SecretManager` is the server-side base class for issuing and validating Hadoop token passwords from token identifiers and secret keys.

## Important APIs, Types, and Functions

Subclasses implement `createPassword(T)`, `retrievePassword(T)`, and `createIdentifier`. Optional overrides include `retriableRetrievePassword` and `checkAvailableForRead`. Static crypto APIs include `update(Configuration)`, `createPassword(byte[], SecretKey)`, and `createSecretKey`. It defines nested `InvalidToken`.

## Control Flow

Static initialization calls `update` with default configuration. `update` selects the configured HMAC/key-generator algorithm and key length and warns if key generators, MACs, or secret keys were already initialized. `generateSecret` lazily creates a synchronized `KeyGenerator`. `createPassword` uses a thread-local `Mac` initialized with the supplied secret key to compute the token password.

## State and Persistence Behavior

Static state stores selected algorithm/length and initialization flags; each instance stores a volatile key generator guarded by a lock. No persistence is performed by the base class, but subclasses usually persist secret keys and token records.

## Dependencies and Integration Points

It depends on JCA/JCE `KeyGenerator`, `Mac`, `SecretKey`, Hadoop security configuration keys, `StandbyException`, and `RetriableException`. It underpins delegation-token secret manager implementations.

## Risks and Edge Cases

Changing configuration after crypto objects are initialized logs warnings because existing thread-local MACs/key generators keep older settings. Unsupported algorithms throw `IllegalArgumentException`. `validateSecretKeyLength` assumes byte length times eight equals configured bits.

## Test Signals

Tests should cover algorithm/key-length configuration, update-before/after initialization warnings, password determinism with known keys, unsupported algorithm failures, key length validation, retriable retrieve default behavior, and subclass invalid-token handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/SecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/Token.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/Token.java

## Purpose

`Token` is the client-side serialized form of a Hadoop security token, containing identifier bytes, password bytes, kind, and service. It also locates identifier classes and renewers at runtime.

## Important APIs, Types, and Functions

Constructors build tokens from identifiers/secret managers, raw components, defaults, or copies. APIs include getters/setters, `decodeIdentifier`, `privateClone`, Writable `readFields`/`write`, URL-safe base64 encode/decode, `equals`, `hashCode`, `toString`, `buildCacheKey`, `isManaged`, `renew`, and `cancel`. Nested `PrivateToken` hides HA failover clones, and nested `TrivialRenewer` is the fallback renewer.

## Control Flow

`decodeIdentifier` discovers `TokenIdentifier` implementations via `ServiceLoader`, caches kind-to-class mapping, instantiates the matching class, and reads identifier bytes. Writable serialization writes identifier/password lengths followed by kind and service. Renewer lookup uses a static `ServiceLoader<TokenRenewer>`, selects the first renewer handling the token kind, caches it per token, and falls back to `TRIVIAL_RENEWER`.

## State and Persistence Behavior

Token state is mutable byte arrays, kind, service, and cached renewer. Tokens persist through Writable and URL-safe base64 encodings, and are stored in `Credentials` token files. The identifier-class map and renewer loader are static process state.

## Dependencies and Integration Points

It depends on Hadoop `Writable`, `Text`, `ReflectionUtils`, `Configuration`, `TokenIdentifier`, `TokenRenewer`, `SecretManager`, ServiceLoader, Base64, and `Credentials` workflows. It is central to delegation tokens and authentication.

## Risks and Edge Cases

`getIdentifier` and `getPassword` expose mutable arrays. ServiceLoader implementation failures are skipped at debug level, which can leave identifiers undecodable or renewers missing. Equality requires exact runtime class, so `PrivateToken` differs from public tokens. Hash code only uses identifier bytes while equality includes password/kind/service.

## Test Signals

Tests should cover Writable and URL round trips, null constructor components, identifier decoding via ServiceLoader, unknown kind behavior, private clone equality/service behavior, renewer selection/fallback, managed renew/cancel delegation, mutable-array exposure assumptions, and cache key stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/Token.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenIdentifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenIdentifier.java

## Purpose

`TokenIdentifier` is the abstract Writable identity payload for a Hadoop token. It exposes token kind, token user, serialized bytes, and a tracking ID.

## Important APIs, Types, and Functions

Subclasses implement `getKind` and `getUser`. The base class provides `getBytes` and `getTrackingId`.

## Control Flow

`getBytes` serializes the identifier into a `DataOutputBuffer` and returns an exact-length copy. `getTrackingId` lazily computes and caches an MD5 hex digest of the serialized bytes.

## State and Persistence Behavior

The only base-class state is the cached tracking ID. Persistence is delegated to subclass Writable implementations.

## Dependencies and Integration Points

It depends on Hadoop `Writable`, `Text`, `DataOutputBuffer`, `UserGroupInformation`, and Apache Commons `DigestUtils`. `Token.decodeIdentifier` uses ServiceLoader to instantiate concrete identifiers.

## Risks and Edge Cases

`getBytes` wraps serialization I/O failures in a runtime exception. Tracking ID is cached and can become stale if a mutable subclass changes after first access. MD5 is used for tracking correlation, not cryptographic validation.

## Test Signals

Tests should cover subclass serialization bytes, tracking ID repeatability, mutation-after-tracking behavior, empty user semantics, and `getBytes` exception wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenInfo.java

## Purpose

`TokenInfo` is a runtime annotation that attaches a token selector type to a protocol or service type.

## Important APIs, Types, and Functions

The annotation has runtime retention, type target, and a single `value()` returning a `Class<? extends TokenSelector<? extends TokenIdentifier>>`.

## Control Flow

There is no executable flow; consumers inspect the annotation reflectively.

## State and Persistence Behavior

The annotation contributes class metadata only.

## Dependencies and Integration Points

It depends on Java annotation APIs and Hadoop token selector/identifier types. Hadoop security/RPC code can use it to choose tokens for a service.

## Risks and Edge Cases

Incorrect selector class metadata causes clients to select the wrong token or none at all. Runtime retention means classpath/reflection availability matters.

## Test Signals

Tests should verify annotated protocol classes expose the intended selector and that token selection code honors the annotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenRenewer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenRenewer.java

## Purpose

`TokenRenewer` is the plugin base class for determining whether a token is managed and for renewing or cancelling managed tokens.

## Important APIs, Types, and Functions

Subclasses implement `handleKind(Text)`, `isManaged(Token<?>)`, `renew(Token<?>, Configuration)`, and `cancel(Token<?>, Configuration)`.

## Control Flow

`Token` discovers implementations with ServiceLoader, asks each candidate whether it handles the token kind, then delegates management, renew, and cancel operations to the selected renewer.

## State and Persistence Behavior

The abstract class owns no state. Implementations may contact services and mutate server-side token state.

## Dependencies and Integration Points

It depends on `Token`, Hadoop `Configuration`, `Text`, and ServiceLoader integration through `Token`.

## Risks and Edge Cases

Multiple renewers claiming the same kind are resolved by ServiceLoader order. Incorrect `isManaged` results can suppress renew/cancel or cause unsupported operations.

## Test Signals

Tests should cover ServiceLoader ordering, handle-kind matching, managed/unmanaged behavior, renew expiration return values, cancel propagation, and interrupted/IO exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenRenewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenSelector.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenSelector.java

## Purpose

`TokenSelector` is the interface for choosing an appropriate token for a named service from a collection of available tokens.

## Important APIs, Types, and Functions

It declares `selectToken(Text service, Collection<Token<? extends TokenIdentifier>> tokens)`.

## Control Flow

Implementations inspect token kind/service fields and return a matching token or null.

## State and Persistence Behavior

The interface owns no state and does not mutate token persistence.

## Dependencies and Integration Points

It depends on `Text`, `Token`, and `TokenIdentifier`. It is referenced by `TokenInfo` and used by clients/RPC code selecting credentials.

## Risks and Edge Cases

Selectors must handle null or empty token collections consistently. Overly broad selectors can return tokens for the wrong service.

## Test Signals

Tests should cover matching service, non-matching service, multiple-token ordering, null/empty collections, and integration with `TokenInfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenSelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenIdentifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenIdentifier.java

## Purpose

`AbstractDelegationTokenIdentifier` is the shared identifier payload for Hadoop delegation tokens, carrying owner, renewer, real user, issue/max dates, sequence number, and master key id.

## Important APIs, Types, and Functions

It extends `TokenIdentifier`, leaves `getKind` abstract, and provides getters/setters for all fields, `getUser`, equality/hash code, Writable `readFields`/`write`, test-visible `writeImpl`, `toString`, and stable CLI string `toStringStable`.

## Control Flow

Construction normalizes null texts to empty texts and converts renewer Kerberos principals to short names. `getUser` returns null for empty owner, creates a remote user when no distinct real user exists, or creates a proxy UGI when real user differs, then marks the real UGI authentication method as `TOKEN`. Serialization writes version byte 0 and fields using Text/WritableUtils; deserialization rejects unknown versions.

## State and Persistence Behavior

All token identity fields are mutable in memory and persisted through Writable serialization. `write` enforces `Text.DEFAULT_MAX_LEN` limits for owner, renewer, and real user before writing.

## Dependencies and Integration Points

It depends on `TokenIdentifier`, `Text`, `WritableUtils`, `HadoopKerberosName`, and `UserGroupInformation`. It is the base for HDFS/YARN/HTTP delegation token identifiers and is decoded by token-printing tools.

## Risks and Edge Cases

Renewer short-name conversion can throw at setter time. Hash code uses only sequence number despite equality including all fields. `getUser` sets the authentication method on `realUgi`, which is the same object as `ugi` for non-proxy tokens. Version changes require compatibility handling.

## Test Signals

Tests should cover Writable round trips, version rejection, max-length enforcement, owner/renewer/real-user null handling, Kerberos renewer short-name conversion, proxy and non-proxy UGI creation, equality/hash behavior, and stable string compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenIdentifier.java -->
