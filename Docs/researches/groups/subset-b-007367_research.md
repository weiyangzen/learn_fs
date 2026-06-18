# subset-b-007367 Research

This grouped report covers Hadoop common security, credential provider, and HTTP proxy-user authentication sources. Each file section preserves its source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslRpcServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslRpcServer.java

Purpose: server-side SASL wiring for Hadoop RPC. It maps RPC authentication methods to SASL mechanisms, creates `SaslServer` instances for token and Kerberos flows, and provides callback handlers for DIGEST/TOKEN and GSSAPI negotiation.

Important APIs/types/functions: `QualityOfProtection` exposes SASL QOP strings. `AuthMethod` serializes RPC auth method bytes and maps simple, kerberos, token/digest, and plain to mechanism names. The constructor derives mechanism/protocol/serverId; Kerberos extracts service and host from the current user's principal. `create(Connection, Map, SecretManager)` chooses the callback handler and creates the SASL server, running as current UGI for Kerberos. `encodeIdentifier`, `decodeIdentifier`, `getIdentifier`, and `encodePassword` adapt token identifiers/passwords for SASL.

Control flow: callers initialize static factory via `init`, instantiate per-auth-method server metadata, then call `create`. Token SASL uses `SaslDigestCallbackHandler`: decode token identifier, set `connection.attemptingUser`, retrieve password from `SecretManager.retriableRetrievePassword`, authorize only matching auth/authz IDs, and optionally delegate unknown callbacks to configured `CustomizedCallbackHandler`. Kerberos uses `SaslGssCallbackHandler` and similarly requires auth ID equality.

State/persistence: static `saslFactory`; instance fields hold selected auth method and derived Kerberos protocol/host. No persistence, but token password lookup and connection attempting user mutate RPC authentication state.

Dependencies/integration: `Server.Connection`, `SecretManager`, `TokenIdentifier`, `UserGroupInformation`, `FastSaslServerFactory`, `SaslPlainServer`, and Hadoop security config. Risks: Kerberos principals without host fail late; authorization is strict equality; callback extension must not leak passwords. Test signals include mechanism selection, auth byte serialization, token identifier decoding errors, custom callbacks, and Kerberos host validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslRpcServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SecurityInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SecurityInfo.java

Purpose: a small ServiceLoader extension point used by RPC security code to discover protocol-specific Kerberos and token metadata.

Important APIs/types/functions: abstract `getKerberosInfo(Class<?> protocol, Configuration conf)` returns a `KerberosInfo` annotation or equivalent provider result for a protocol; `getTokenInfo(Class<?> protocol, Configuration conf)` returns `TokenInfo`. Both are public to limited private Hadoop subsystems and evolving.

Control flow: this file defines no concrete behavior. `SecurityUtil.getKerberosInfo` and `SecurityUtil.getTokenInfo` iterate test providers first, then ServiceLoader providers implementing this class, returning the first non-null match.

State/persistence: no fields, no persistence, no caching in this abstraction. State is owned by provider implementations and `SecurityUtil`'s provider arrays/loaders.

Dependencies/integration: used by RPC clients/servers, protocol implementations, and service-provider metadata. It depends only on `Configuration`, `KerberosInfo`, and `TokenInfo`.

Risks: provider ordering controls which metadata wins; a provider returning broad non-null results can shadow later providers. Null returns are part of normal lookup semantics, so tests should cover missing metadata and multiple provider priority.

Test signals: mock `SecurityInfo` providers installed through `SecurityUtil.setSecurityInfoProviders`, protocol classes with/without token and Kerberos metadata, and null-return fallthrough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SecurityInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SecurityUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SecurityUtil.java

Purpose: central security utility class for Kerberos principal expansion, token service naming, DNS resolution, RPC security metadata discovery, privileged execution, authentication configuration, ZooKeeper auth parsing, and ZooKeeper SSL client setup.

Important APIs/types/functions: `setConfiguration` configures token service IP/hostname mode, DNS cache expiry, slow lookup logging, and `DomainNameResolver`. `getServerPrincipal` replaces `_HOST` in service principals. `login` resolves configured keytab/principal and delegates to `UserGroupInformation.loginUserFromKeytab`. `buildTokenService`, `setTokenService`, and `getTokenServiceAddr` define token service identities. `getKerberosInfo`, `getClientPrincipal`, and `getTokenInfo` query `SecurityInfo` providers. `doAsLoginUser`, `doAsCurrentUser`, and `doAsLoginUserOrFatal` wrap UGI `doAs`. `getZKAuthInfos`, `validateSslConfiguration`, `setSslConfiguration`, and `TruststoreKeystore` integrate ZooKeeper auth and TLS.

Control flow: static initialization calls `setConfigurationInternal(new Configuration())`. Changing token service mode swaps between `StandardHostResolver` and `QualifiedHostResolver`. Qualified resolution handles IP literals, rooted FQDNs, dotted hostnames, search domains, and loopback without unnecessary reverse lookups. SSL configuration validates four required fields before setting ZooKeeper secure client properties.

State/persistence: static resolver mode, host resolver, DNS resolver, logging thresholds, cache interval, ServiceLoader, and test provider array. No durable writes. Host resolver may own a Guava cache.

Dependencies/integration: `UserGroupInformation`, `HadoopKerberosName`, `NetUtils`, `DNS`, `DomainNameResolverFactory`, `SecurityInfo`, `Token`, `ZKUtil`, ZooKeeper `ZKClientConfig`, DNSJava resolver config, and Hadoop common configuration keys.

Risks: global static configuration affects all callers in-JVM; token service identity changes can break token matching; hostname canonicalization and DNS search behavior are security-sensitive; `doAsLoginUserOrFatal` exits JVM on failure; SSL passwords are read as plain strings in config object. Test signals include `_HOST` substitution, null/0.0.0.0 host behavior, IP-vs-host token services, resolver cache error propagation, provider priority, invalid auth method config, ZK auth indirection, and missing SSL fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SecurityUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedIdMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedIdMapping.java

Purpose: shell-backed `IdMappingServiceProvider` mapping Unix user/group names to numeric IDs and back, mainly for NFS gateway style integration.

Important APIs/types/functions: constructors read update interval and static mapping file config. `getUid`, `getGid`, `getUserName`, `getGroupName`, `getUidAllowingUnknown`, and `getGidAllowingUnknown` implement lookup. `updateMaps`, `clearNameMaps`, `loadFullUserMap`, `loadFullGroupMap`, and `updateMapIncr` maintain caches. `parseStaticMap` supports `uid|gid remote local` mapping lines. `updateMapInternal` runs shell commands and populates `BiMap`s with duplicate detection.

Control flow: initialization loads static mappings and either clears or fully loads caches. Each lookup checks expiry, refreshes static map when modified, then uses cached entries. Missing names/IDs trigger targeted shell commands; numeric group names force full group map loading. Unsupported platforms log and fall back.

State/persistence: in-memory `uidNameMap`, `gidNameMap`, `lastUpdateTime`, `staticMapping`, and static file modification timestamp. Reads a configured static mapping file but writes nothing. Unknown name fallback uses Java string hash codes.

Dependencies/integration: Hadoop `IdMappingConstant`, Guava `BiMap`, OS commands (`getent`, `id`, `dscl`, `cut`, `awk`, `sed`), `Shell.bashQuote`, and `Time`.

Risks: command parsing is platform-dependent; duplicate names/IDs are ignored after warning; static mapping interpretation is easy to misconfigure; command failure can preserve stale maps; hash-code fallback can collide and should not be used for authorization decisions. Test signals include Linux/Mac command parsing, uint32-to-int32 conversion, static map reload/delete, duplicate entries, numeric group names, unsupported OS, and unknown fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedIdMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedUnixGroupsMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedUnixGroupsMapping.java

Purpose: shell-based `GroupMappingServiceProvider` that obtains Unix group memberships for a user by executing Hadoop `Shell` group commands.

Important APIs/types/functions: `setConf` reads shell timeout. `getGroups` returns a list; `getGroupsSet` returns an ordered set. `createGroupExecutor` and `createGroupIDExecutor` construct timed shell command executors. `resolveFullGroupNames`, `resolvePartialGroupNames`, and `parsePartialGroupNames` parse normal and partial command outputs. `cacheGroupsRefresh` and `cacheGroupsAdd` are no-ops because this provider does not cache.

Control flow: `getUnixGroups` executes the group-name command. On success it tokenizes output into a `LinkedHashSet`. On `ExitCodeException`, it treats timeout as empty and otherwise attempts partial resolution: if the shell returned some group names but complained about unresolved names, it invokes the group-ID command and filters numeric unresolved names.

State/persistence: only per-instance timeout and inherited configuration. No persistent storage and no cache.

Dependencies/integration: `Groups`, UGI group lookup, `Shell.ShellCommandExecutor`, `Shell.getGroupsForUserCommand`, `Shell.getGroupsIDForUserCommand`, Hadoop common timeout config, and commons/string utilities.

Risks: shell timeout logging reports seconds while timeout is configured in milliseconds; partial resolution is unsupported on Windows; numeric group names can be ambiguous; command output format differences can produce empty groups or exceptions. Test signals include timeout handling, command construction overrides, full and partial parsing, unresolved users, Windows partial failure, and duplicate group elimination with preserved primary-group order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedUnixGroupsMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedUnixGroupsNetgroupMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedUnixGroupsNetgroupMapping.java

Purpose: extends shell-based Unix group mapping with netgroup membership support, adding cached netgroups to ordinary Unix groups.

Important APIs/types/functions: overrides `getGroups` to append `NetgroupCache` netgroups to parent groups. `cacheGroupsRefresh` reloads current cached netgroup names. `cacheGroupsAdd` only caches entries beginning with `@`. `getUsersForNetgroup` parses `getent netgroup` style output. `execShellGetUserForNetgroup` calls `Shell.getUsersForNetgroupCommand`.

Control flow: users first get normal Unix groups from `ShellBasedUnixGroupsMapping`. Netgroups are maintained separately: refresh extracts known netgroup names, clears cache, then re-adds them. Adding a netgroup strips the leading `@` for shell execution, parses tuple output into user names, and stores users in `NetgroupCache`.

State/persistence: no local fields; uses global `NetgroupCache`. No durable writes.

Dependencies/integration: `ShellBasedUnixGroupsMapping`, `NetgroupCache`, OS `getent netgroup` command through `Shell`, and Hadoop `GroupMappingServiceProvider` cache refresh hooks.

Risks: parsing is simple string replacement and split logic and may mis-handle unusual netgroup tuple forms; failed shell lookup logs and returns an empty list rather than failing; only groups prefixed by `@` are cached. Test signals include `@` filtering, cache refresh preserving configured netgroup names, shell error behavior, tuple parsing with spaces/domains/hosts, and merged Unix plus netgroup results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedUnixGroupsNetgroupMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/UGIExceptionMessages.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/UGIExceptionMessages.java

Purpose: package-private constants for standard `KerberosAuthException` and UGI login/logout error messages.

Important APIs/types/functions: string constants such as `FAILURE_TO_LOGIN`, `INVALID_UID`, `LOGIN_FAILURE`, `LOGOUT_FAILURE`, `MUST_FIRST_LOGIN`, `MUST_FIRST_LOGIN_FROM_KEYTAB`, `SUBJECT_MUST_CONTAIN_PRINCIPAL`, `SUBJECT_MUST_NOT_BE_NULL`, and `USING_TICKET_CACHE_FILE`. Private constructor enforces utility class pattern.

Control flow: none locally. `UserGroupInformation` imports these constants statically when throwing or wrapping Kerberos and login errors.

State/persistence: no mutable state, no persistence.

Dependencies/integration: integrated with `KerberosAuthException` message construction in UGI.

Risks: changing literal strings can break tests or downstream code that matches messages. Since the class is package-private, binary API impact is limited, but log/error compatibility still matters.

Test signals: UGI login failure paths, invalid UID OS-login path, null or principal-less subject login, relogin-before-login, keytab logout/relogin misuse, and message formatting in `KerberosAuthException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/UGIExceptionMessages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/User.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/User.java

Purpose: package-private JAAS `Principal` representing Hadoop's canonical user identity inside a `Subject`, storing full name, short name, authentication method, login context, and last login timestamp.

Important APIs/types/functions: constructors normalize short name with `HadoopKerberosName.getShortName`. `getName` returns full principal; `getShortName` returns local short user. `setAuthenticationMethod`/`getAuthenticationMethod`, `setLogin`/`getLogin`, and `setLastLogin`/`getLastLogin` support UGI state transitions and relogin throttling.

Control flow: created by `UserGroupInformation.HadoopLoginModule`, remote/proxy user constructors, and tests. Constructor rejects illegal Kerberos/user names by wrapping short-name resolution failures as `IllegalArgumentException`.

State/persistence: immutable full and short names; volatile mutable auth method, login context, and last login. No durable persistence.

Dependencies/integration: tightly coupled to `UserGroupInformation`, `AuthenticationMethod`, `LoginContext`, and `HadoopKerberosName` auth-to-local rules.

Risks: `equals` compares full name and auth method but `hashCode` only uses full name, which is legal but can increase collisions. Auth method mutability means equality can change after insertion into hash collections. Login context is volatile but its internals require UGI locking discipline.

Test signals: short-name rule failures, equality across auth methods, mutable auth method effects, last-login updates during relogin, and subject principal extraction by UGI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/User.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/UserGroupInformation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/UserGroupInformation.java

Purpose: Hadoop's central user identity and credential wrapper around JAAS `Subject`. It initializes authentication mode, logs in local/Kerberos users, manages proxy users, groups, delegation tokens, credentials, and Kerberos ticket/keytab relogin.

Important APIs/types/functions: static initialization/configuration (`setConfiguration`, `reset`, `isSecurityEnabled`), user lookup (`getCurrentUser`, `getLoginUser`, `getBestUGI`, `getUGIFromTicketCache`, `getUGIFromSubject`), login (`loginUserFromSubject`, `loginUserFromKeytab`, `loginUserFromKeytabAndReturnUGI`), relogin/logout (`checkTGTAndReloginFromKeytab`, `reloginFromKeytab`, `forceReloginFromKeytab`, `reloginFromTicketCache`, `logoutUserFromKeytab`), identity factories (`createRemoteUser`, `createProxyUser`, testing variants), group access, token/credential mutation, and `doAs`.

Control flow: `ensureInitialized` lazily configures authentication, Kerberos name rules, group service, metrics, and relogin intervals. `getLoginUser` atomically creates one login user, optionally wrapping it with `HADOOP_PROXY_USER`, then loads tokens from configured files and base64 values. JAAS login is built by `HadoopConfiguration`, combining OS login, Kerberos login, and `HadoopLoginModule`. Relogin synchronizes on subject private credentials, logs out, creates a new `HadoopLoginContext`, logs in, fixes TGT ordering, and updates the attached login context.

State/persistence: static `conf`, auth method, `Groups`, metrics, login user `AtomicReference`, and optional renewal executor. Each UGI holds a `Subject` and cached `User`. Tokens and secret credentials are in the subject private/public credentials; token files are read at login but not written here. Renewal threads update Kerberos credentials in memory.

Dependencies/integration: JAAS, Kerberos tickets/principals, Hadoop `Groups`, `Credentials`, `Token`, `SecurityUtil`, `Shell`, metrics2, retry policies, `SubjectUtil`, and environment/system properties (`HADOOP_USER_NAME`, `HADOOP_PROXY_USER`, `KRB5*`, token variables).

Risks: global mutable static config affects all security behavior; background renewal executor is static and single-user oriented; subject credential locking is security-critical; environment-driven proxy user and token loading can surprise services; private credential iteration can expose mutable state under incorrect locks. Test signals include simple vs Kerberos login, external subject validation, keytab/ticket relogin throttle and forced paths, TGT ordering fix, token loading, proxy real-user semantics, group fallback, `doAs` exception translation, metrics, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/UserGroupInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/WhitelistBasedResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/WhitelistBasedResolver.java

Purpose: `SaslPropertiesResolver` implementation that applies different RPC SASL QOP properties depending on whether a client IP is in a configured whitelist.

Important APIs/types/functions: configuration keys define fixed whitelist file, variable whitelist enable/file/cache, and non-whitelist RPC protection. `setConf` builds a `CombinedIPWhiteList` and precomputes non-whitelist SASL properties. `getServerProperties(InetAddress)` and `getServerProperties(String)` choose default properties for whitelisted clients and restricted properties for others. `getSaslProperties` defaults non-whitelisted clients to privacy.

Control flow: when configured, fixed file is always used; variable file/cache are used only when enabled. At request time, null client addresses get non-whitelist properties, otherwise the IP string is checked against the combined whitelist.

State/persistence: in-memory `CombinedIPWhiteList` and SASL property map. Whitelist files are read by the helper; this class does not write them.

Dependencies/integration: Hadoop RPC SASL resolver configuration, `CombinedIPWhiteList`, `SaslRpcServer.QualityOfProtection`, and `SaslPropertiesResolver`.

Risks: null client addresses take stricter non-whitelist path; bad whitelist file paths may silently reduce whitelist coverage depending on helper behavior; variable whitelist refresh cadence controls runtime policy changes; IP string matching must account for IPv4/IPv6 formats. Test signals include fixed-only, variable-enabled, cache expiry, null address, unknown host string path, and QOP parsing defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/WhitelistBasedResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/AbstractJavaKeyStoreProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/AbstractJavaKeyStoreProvider.java

Purpose: base `CredentialProvider` for Java `KeyStore`-backed credential stores, shared by Hadoop-filesystem and local-filesystem provider variants.

Important APIs/types/functions: constructor initializes backing filesystem/path, locates or creates keystore, and creates fair read/write locks. Abstract hooks define scheme, keystore type, key algorithm, streams, existence, and permission handling. Public operations implement `getCredentialEntry`, `getAliases`, `createCredentialEntry`, `deleteCredentialEntry`, `flush`, `needsPassword`, warning/error messages, and `toString`.

Control flow: `locateKeystore` obtains password from `HADOOP_CREDSTORE_PASSWORD` or configured password file, defaulting to `none`; then loads existing keystore with stashed permissions or creates a new empty keystore with `600` permissions. Reads take read lock; create/delete/flush take write lock. Credentials are stored as `SecretKeySpec` built from UTF-8 bytes of char material.

State/persistence: mutable path, password, `KeyStore`, changed flag, locks, URI, and config. Persistent state is the keystore file/object written on `flush` only when changed.

Dependencies/integration: Java security `KeyStore`, `SecretKeySpec`, Hadoop `ProviderUtils`, `Path`, credential provider API, and subclass filesystem implementations.

Risks: default password `none` is weak unless callers configure a password; char[] material is converted through immutable `String`; `innerSetCredential` takes the write lock even when caller already holds it, relying on reentrant lock behavior; failed flush leaves `changed` true. Test signals include password source precedence, missing/empty keystore creation, duplicate alias, delete missing alias, permission hooks, concurrent read/write behavior, and provider warning/error text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/AbstractJavaKeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/BouncyCastleFipsKeyStoreProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/BouncyCastleFipsKeyStoreProvider.java

Purpose: Hadoop filesystem credential provider using Bouncy Castle FIPS keystore format.

Important APIs/types/functions: constants `SCHEME_NAME=bcfks`, `KEYSTORE_TYPE=bcfks`, and `ALGORITHM=HMACSHA512`; overrides scheme/type/algorithm hooks from `KeyStoreProvider`; nested `Factory` returns this provider when a configured URI uses the `bcfks` scheme.

Control flow: factory receives each configured provider URI from `CredentialProviderFactory`; matching scheme constructs the provider, which delegates path unnesting, filesystem setup, keystore loading/creation, and flush behavior to `KeyStoreProvider` and `AbstractJavaKeyStoreProvider`.

State/persistence: no additional fields beyond inherited keystore state. Persists credentials to the unnested Hadoop `FileSystem` path on flush.

Dependencies/integration: Java/Bouncy Castle provider availability for BCFKS keystore type and HMACSHA512 secret-key entries, Hadoop `FileSystem`, ServiceLoader registration of factory, and credential provider path config.

Risks: runtime must have BCFKS support installed; algorithm/type strings are provider-sensitive; remote filesystem writes inherit `KeyStoreProvider` overwrite and permission semantics. Test signals include ServiceLoader factory selection, BCFKS keystore creation/opening, missing provider failure, flush to HDFS/file URI, and password-required warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/BouncyCastleFipsKeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialProvider.java

Purpose: public unstable abstraction for credential/password stores used by Hadoop applications.

Important APIs/types/functions: `CredentialEntry` pairs alias and char[] credential and exposes getters plus a diagnostic `toString`. Provider contract includes `flush`, `getCredentialEntry`, `getAliases`, `createCredentialEntry`, `deleteCredentialEntry`, `isTransient`, `needsPassword`, `noPasswordWarning`, and `noPasswordError`. `CLEAR_TEXT_FALLBACK` exposes the config key controlling clear-text fallback behavior.

Control flow: abstract class only defines contract and defaults. Implementations must be thread-safe. Durable providers override persistence/password methods; transient providers override `isTransient`.

State/persistence: no provider state in base class. `CredentialEntry` stores alias and char[] reference without copying.

Dependencies/integration: `Configuration.getPassword`, `CredentialProviderFactory`, Hadoop credential shell, key store providers, user provider, and common config keys.

Risks: `CredentialEntry.toString` includes credential contents and should not be used in logs; char[] is not defensively copied, so callers and providers can mutate shared material; implementations must enforce thread safety themselves. Test signals include provider contract conformance, transient filtering, password-required messaging, duplicate alias semantics, and avoidance of credential stringification in sensitive logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialProviderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialProviderFactory.java

Purpose: ServiceLoader-backed factory that turns configured credential provider URI paths into concrete `CredentialProvider` instances.

Important APIs/types/functions: `CREDENTIAL_PROVIDER_PATH` config key, abstract `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, static `serviceLoader`, and `SERVICE_LOADER_LOCKED` recursion guard.

Control flow: static initializer eagerly iterates ServiceLoader to avoid lazy-loading synchronization races. `getProviders` iterates every configured URI string, parses it, synchronizes on ServiceLoader, sets recursion guard, asks each factory to create a provider, and adds the first non-null match. Bad URI syntax and unknown schemes become IOExceptions; recursive loads become `PathIOException`.

State/persistence: static ServiceLoader and atomic recursion guard. No persistence.

Dependencies/integration: providers register factories through Java ServiceLoader; Hadoop `Configuration` supplies comma/string collection provider paths; `PathIOException` reports recursive filesystem credential loading.

Risks: synchronized global ServiceLoader can serialize provider creation; recursion guard is global and can reject nested loads; factory ordering controls scheme resolution; unknown provider path aborts the whole call. Test signals include multiple configured paths, bad URI, unknown scheme, recursive load guard, concurrent access, and first-match factory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialProviderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialShell.java

Purpose: command-line implementation for `hadoop credential`, exposing list, create, check, and delete operations over configured credential providers.

Important APIs/types/functions: `init` parses subcommands and flags (`-provider`, `-f`, `-strict`, `-value`, `-help`). Inner `Command` selects provider, preferring first non-transient provider unless user supplied provider explicitly. `ListCommand`, `DeleteCommand`, `CheckCommand`, and `CreateCommand` implement validation and execution. `promptForCredential` double-prompts and clears mismatched buffers. `PasswordReader` wraps `System.console`.

Control flow: parsed subcommand validates provider and password requirements. `create` prompts or uses test value, creates entry, flushes. `delete` confirms unless forced, deletes, flushes. `check` reads supplied/prompted value and compares to stored char[] with `Arrays.equals`. `list` prints aliases. Strict mode fails when a provider needs a password but none was supplied; non-strict prints warning.

State/persistence: shell instance tracks interactivity, strictness, user-supplied provider flag, test value, and password reader. Persistence occurs through provider `flush`.

Dependencies/integration: `CommandShell`, `ToolRunner`, `CredentialProviderFactory`, provider implementations, console IO, and Hadoop generic options.

Risks: `-value` exposes secrets through command line and is marked testing-only but parsed generally; console absence fails create/check; transient provider modification is allowed with warning; provider selection can surprise when `user:///` appears before durable stores unless filtered. Test signals include argument parsing, strict/non-strict password-required handling, no valid providers, forced delete, prompt mismatch clearing, check success/failure/missing alias, and command help paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/JavaKeyStoreProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/JavaKeyStoreProvider.java

Purpose: Hadoop `FileSystem` credential provider using Java JCEKS keystore format.

Important APIs/types/functions: constants `SCHEME_NAME=jceks`, `KEYSTORE_TYPE=jceks`, and `ALGORITHM=AES`; overrides scheme/type/algorithm hooks; nested `Factory` creates instances for `jceks://` URIs.

Control flow: provider URI is unnested by inherited logic, for example `jceks://hdfs@nn/path` becomes an HDFS path. Inherited `KeyStoreProvider` opens or creates the keystore through Hadoop `FileSystem`; inherited abstract provider handles aliases, credentials, password lookup, and flush.

State/persistence: no new fields; persistent credentials live in a JCEKS keystore at the target Hadoop filesystem path.

Dependencies/integration: Java JCEKS support, `KeyStoreProvider`, `CredentialProviderFactory`, Hadoop `FileSystem`, and service provider registration.

Risks: JCEKS is legacy compared with FIPS formats; default keystore password still applies if none configured; remote filesystem permissions and overwrite semantics come from `KeyStoreProvider`. Test signals include factory scheme selection, URI unnesting, JCEKS read/write, duplicate/missing alias behavior, and password source handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/JavaKeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/KeyStoreProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/KeyStoreProvider.java

Purpose: abstract filesystem-backed keystore provider for credential stores located on any Hadoop `FileSystem`.

Important APIs/types/functions: extends `AbstractJavaKeyStoreProvider`; fields `FileSystem fs` and `FsPermission permissions`; implements output/input/existence/permission hooks and filesystem initialization.

Control flow: `initFileSystem` delegates URI unnesting to base class then obtains the target path's Hadoop filesystem. Existing keystores stash current `FsPermission`; new stores use requested permissions. `getOutputStreamForKeystore` calls `FileSystem.create(fs, path, permissions)` and `flush` in the base class writes the keystore through that stream.

State/persistence: stores filesystem handle and permissions. Persistent state is the keystore file on the Hadoop filesystem.

Dependencies/integration: Hadoop `FileSystem`, `FSDataOutputStream`, `FileStatus`, `FsPermission`, and concrete scheme providers (`jceks`, `bcfks`).

Risks: `FileSystem.create` overwrite behavior and permission support depend on filesystem implementation; remote filesystems may not enforce POSIX-like permissions; stashed permissions are only as accurate as `getFileStatus`. Test signals include local and remote FS paths, existing permission preservation, new `600` permissions, missing parent/error propagation, and flush overwrite behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/KeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalBouncyCastleFipsKeyStoreProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalBouncyCastleFipsKeyStoreProvider.java

Purpose: local-filesystem credential provider using Bouncy Castle FIPS keystore format.

Important APIs/types/functions: constants `SCHEME_NAME=localbcfks`, `KEYSTORE_TYPE=bcfks`, and `ALGORITHM=HMACSHA512`; overrides inherited hooks; factory creates provider for `localbcfks://` URIs.

Control flow: factory match constructs the provider. `LocalKeyStoreProvider` resolves the local file URI, handles local streams and permissions, while `AbstractJavaKeyStoreProvider` handles keystore loading and credential operations.

State/persistence: no fields beyond inherited local file, permissions, keystore, and changed flag. Persists to a local BCFKS file on flush.

Dependencies/integration: BCFKS-capable Java security provider, `LocalKeyStoreProvider`, ServiceLoader factory, and local filesystem permission APIs or Windows winutils.

Risks: fails if BCFKS support is unavailable; local permission restoration differs between POSIX and Windows; `localbcfks` URI must unnest to a valid file URI. Test signals include factory selection, provider availability, local create/open/flush, permission preservation, and password-required behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalBouncyCastleFipsKeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalJavaKeyStoreProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalJavaKeyStoreProvider.java

Purpose: local-filesystem credential provider using Java JCEKS keystore format.

Important APIs/types/functions: constants `SCHEME_NAME=localjceks`, `KEYSTORE_TYPE=jceks`, and `ALGORITHM=AES`; factory creates instances for `localjceks://` provider URIs.

Control flow: URI selection happens in the nested factory. Local file resolution, zero-length handling, permission stashing/restoration, keystore load/create, credential mutation, and flush are inherited from `LocalKeyStoreProvider` and `AbstractJavaKeyStoreProvider`.

State/persistence: inherited state only. Persists credentials to a local JCEKS file after `flush`.

Dependencies/integration: Java JCEKS keystore support, local filesystem, Hadoop credential provider path config, and ServiceLoader.

Risks: local file URI syntax must be valid; default password remains weak; JCEKS has legacy security properties; permission behavior varies on Windows. Test signals include creating a new local keystore, loading existing non-empty keystore, ignoring zero-length file as missing, preserving permissions, and factory non-match on other schemes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalJavaKeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalKeyStoreProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalKeyStoreProvider.java

Purpose: abstract local-file implementation for Java keystore credential providers.

Important APIs/types/functions: local `File file`, POSIX permission set, stream/existence hooks, `createPermissions`, `stashOriginalFilePermissions`, `initFileSystem`, `flush`, and `modeToPosixFilePermission`.

Control flow: base URI unnesting creates a Hadoop `Path`, then this class converts it to a local `File`. Existing non-zero files are loaded; zero-length files are treated as absent because keystore loading cannot handle them. New stores compute permissions from octal mode. Flush writes through base class and then resets permissions via POSIX APIs or Windows `FileUtil.setPermission`.

State/persistence: local file and permission set are stored in instance fields. Persistent state is the local keystore file and restored mode.

Dependencies/integration: Java NIO files/permissions, Hadoop `FileUtil`, `FsPermission`, `Shell`/winutils permission command, and concrete local provider formats.

Risks: conversion through `new URI(getPath().toString())` is sensitive to malformed paths; permissions may be null if earlier setup failed; Windows permission translation depends on winutils output; local write is not atomic. Test signals include POSIX mode conversion, Windows permission parsing, zero-length file behavior, invalid URI handling, permission restoration after flush, and read/write stream failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/LocalKeyStoreProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/UserProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/UserProvider.java

Purpose: transient credential provider backed by the current user's in-memory Hadoop `Credentials`.

Important APIs/types/functions: `SCHEME_NAME=user`; constructor captures `UserGroupInformation.getCurrentUser()` and a copy of its credentials via `getCredentials`. `isTransient` returns true. Credential operations map aliases to `Text` secret keys. `flush` adds the provider's credentials back to the user. Nested factory creates provider for `user:///`.

Control flow: reads get secret bytes and decode UTF-8 to char[]. Creates reject duplicate aliases, store UTF-8 bytes, and return entry. Deletes require existing secret key. Listing returns all secret-key aliases.

State/persistence: in-memory UGI and `Credentials`. Transient provider does not write durable storage; flush mutates the user's in-memory credentials.

Dependencies/integration: `UserGroupInformation`, `Credentials`, `Text`, credential provider factory, and jobs that distribute credentials through UGI rather than external keystore files.

Risks: constructor uses `getCredentials`, which filters private tokens but copies secret keys; provider may not reflect later UGI credential mutations until flush/add. Secrets pass through immutable `String` for encoding/decoding. Because it is transient, CLI normally avoids selecting it unless explicitly supplied. Test signals include transient filtering, duplicate/missing alias, flush updating current UGI, alias listing, and UTF-8 credential round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/UserProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/package-info.java

Purpose: package-level documentation marker for the Hadoop credential provider API package.

Important APIs/types/functions: declares package `org.apache.hadoop.security.alias` and documents that it provides the Hadoop credential provider API. No classes or methods are defined.

Control flow: none.

State/persistence: none.

Dependencies/integration: Javadoc/package metadata for credential provider classes such as `CredentialProvider`, factories, keystore providers, `CredentialShell`, and `UserProvider`.

Risks: low behavioral risk. Documentation wording affects generated API docs only.

Test signals: package-info compilation and Javadoc generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/ProxyUserAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/ProxyUserAuthenticationFilter.java

Purpose: servlet authentication filter extension that supports Hadoop proxy-user `doAs` query parameter semantics after base HTTP authentication.

Important APIs/types/functions: `init` extracts proxyuser config and refreshes `ProxyUsers`. `doFilter` lowercases request parameters, reads `doas`, creates remote and proxy UGIs, authorizes with `ProxyUsers.authorize`, and wraps request remote user/principal on success. `getProxyuserConfiguration` copies filter init params with `proxyuser.` prefix. `toLowerCase` wraps requests when parameter names contain uppercase characters. `containsUpperCase` supports that normalization.

Control flow: initialize proxy authorization config before `AuthenticationFilter` init. Per request, if `doas` exists and differs from remote user, and a user principal exists, build real-user UGI from remote user, wrap effective doAs user, authorize against remote address, then pass a request wrapper reporting effective user. Authorization failure sends HTTP 403 and stops. Finally calls `super.doFilter`.

State/persistence: no fields; proxy authorization state is maintained by `ProxyUsers` static configuration.

Dependencies/integration: Hadoop auth `AuthenticationFilter`, servlet API, `ProxyUsers`, `UserGroupInformation`, `AuthorizationException`, `HttpExceptionUtils`, and HTTP filter initializer config.

Risks: lowercasing can merge distinct parameter names and preserves all values under the lower-case key; doAs only applies when authenticated remote principal exists; remote address trust depends on servlet/container proxy configuration; request wrapper principal returns full proxy UGI user while remote user returns short name. Test signals include uppercase `DoAs`, duplicate case-folded params, self-doAs no-op, missing principal, forbidden proxy user, successful wrapper values, and config extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/ProxyUserAuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/ProxyUserAuthenticationFilterInitializer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/ProxyUserAuthenticationFilterInitializer.java

Purpose: Hadoop HTTP `FilterInitializer` that installs `ProxyUserAuthenticationFilter` with both normal authentication settings and proxy-user authorization settings.

Important APIs/types/functions: constructor sets `configPrefix` to `hadoop.http.authentication.`. `createFilterConfig` starts from `AuthenticationFilterInitializer.getFilterConfigMap` and then copies properties under `ProxyUsers.CONF_HADOOP_PROXYUSER`, prefixing each with `proxyuser`. `initFilter` adds the filter to the container under name `ProxyUserAuthenticationFilter`.

Control flow: at HTTP server startup, Hadoop calls `initFilter`; configuration map is built once and passed to the servlet filter. The filter later reconstructs proxyuser config from init params.

State/persistence: only instance `configPrefix`; no persistence.

Dependencies/integration: Hadoop HTTP `FilterContainer`, `FilterInitializer`, `AuthenticationFilterInitializer`, `ProxyUsers`, and `ProxyUserAuthenticationFilter`.

Risks: prefix composition must preserve expected `proxyuser.<name>.<setting>` keys; mistakes can silently disable proxy authorization. This initializer always uses default Hadoop HTTP auth prefix and does not expose a constructor override. Test signals include config map contents for auth and proxy settings, filter name/class registration, and round trip with `ProxyUserAuthenticationFilter.getProxyuserConfiguration`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/ProxyUserAuthenticationFilterInitializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/package-info.java

Purpose: package-level documentation for the server-side Hadoop authentication framework package.

Important APIs/types/functions: declares package `org.apache.hadoop.security.authentication.server` and states that the package provides server-side authentication framework functionality. No executable code.

Control flow: none.

State/persistence: none.

Dependencies/integration: Javadoc/package metadata for HTTP authentication server filters, including proxy-user filter integration.

Risks: no runtime risk; documentation changes only affect generated docs.

Test signals: package-info compilation and Javadoc generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/package-info.java -->
