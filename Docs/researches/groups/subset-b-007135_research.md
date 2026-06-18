# subset-b-007135 Hadoop auth server, signer, Kerberos, ZooKeeper, and tests research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/KerberosAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/KerberosAuthenticationHandler.java

## Purpose
Implements server-side HTTP Kerberos/SPNEGO authentication for Hadoop Auth. It validates keytab/principal configuration, builds a JAAS `Subject` for one or more HTTP service principals, optionally installs Kerberos name mapping rules, and turns a completed GSS acceptor exchange into an `AuthenticationToken`.

## Important APIs, types, and functions
`TYPE`, `PRINCIPAL`, `KEYTAB`, `NAME_RULES`, `RULE_MECHANISM`, and `ENDPOINT_WHITELIST` are the main configuration surface. `init()` loads the keytab and service principals, including wildcard principal expansion through `KerberosUtil.getPrincipalNames()`. `authenticate()` handles whitelist bypass, `Authorization: Negotiate` challenge/response, token decoding, and server principal validation. `runWithPrincipal()` creates `GSSCredential`/`GSSContext`, accepts the client token, emits response SPNEGO tokens, and constructs a short-name token via `KerberosName`.

## Control flow
Filter initialization requires a non-empty principal and keytab path and checks keytab existence. If the configured principal is `*`, all keytab principals matching `HTTP/.*` are added to the server subject; otherwise the single configured principal is used. Runtime authentication first returns anonymous for exact servlet-path whitelist hits. Requests without a valid Negotiate header receive `WWW-Authenticate: Negotiate` and `401`; requests with a token decode the GSS token, require an `HTTP/` server principal, and run GSS acceptor work inside the server subject.

## State and persistence
State is in-memory only: `type`, `keytab`, `gssManager`, `serverSubject`, and a whitelist set. The handler mutates global static `KerberosName` rule state when configured. `destroy()` nulls the keytab and subject, but there is no durable persistence.

## Dependencies and integration points
Integrates with `AuthenticationFilter`, servlet request/response APIs, `KerberosAuthenticator` header constants, JGSS, JAAS `Subject`, `KerberosPrincipal`, `KeyTab`, Commons Codec Base64, `KerberosUtil`, and `KerberosName`. It is also used behind `MultiSchemeAuthenticationHandler`.

## Risks and test signals
Security-sensitive risks include accepting malformed GSS tokens, wildcard principal selection from multi-principal keytabs, global name-rule side effects, exact-only whitelist matching, and leaking sensitive Authorization values in warning logs. Tests should cover missing config, missing keytabs, wildcard principal selection, invalid server principal decoded from tokens, SPNEGO continuation tokens, short-name mapping failures, endpoint whitelist validation, and destroy/re-init behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/KerberosAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/LdapAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/LdapAuthenticationHandler.java

## Purpose
Implements HTTP Basic authentication backed by LDAP bind verification. It supports either base-DN construction (`uid=user,<baseDN>`) or Active Directory-style bind-domain usernames, plus optional LDAP StartTLS.

## Important APIs, types, and functions
Configuration constants include `PROVIDER_URL`, `BASE_DN`, `LDAP_BIND_DOMAIN`, and `ENABLE_START_TLS`. `authenticate()` validates the Basic scheme, decodes RFC 7617 credentials as UTF-8, and calls `authenticateUser()`. `authenticateUser()` checks username/password, appends a bind domain when needed, builds the bind DN, and delegates to StartTLS or non-TLS bind helpers. `authenticateWithTlsExtension()` negotiates StartTLS with `InitialLdapContext`; `authenticateWithoutTlsExtension()` performs a simple JNDI bind through `InitialDirContext`. `hasDomain()` and `indexOfDomainMatch()` detect existing `@` or `/` domains.

## Control flow
Initialization requires a provider URL and exactly one of base DN or bind domain. StartTLS cannot be combined with an `ldaps` provider URL. Runtime requests without Basic auth are challenged with `WWW-Authenticate: Basic` and `401`. Valid Basic payloads are split at the first colon; valid LDAP binds return an `AuthenticationToken` whose user, principal, and type are the LDAP username and `ldap`.

## State and persistence
The handler stores LDAP connection settings and StartTLS/hostname-verification flags in memory. It creates and closes a JNDI context per authentication attempt and persists no state. The hostname-verification override is test-only and dangerous outside tests.

## Dependencies and integration points
Depends on servlet APIs, JNDI LDAP classes, `StartTlsRequest`/`StartTlsResponse`, Commons Codec Base64, `AuthenticationHandlerUtil`, and Hadoop Auth `AuthenticationToken`. It can be selected directly by `AuthenticationFilter` or configured as a Basic scheme backend in multi-scheme auth.

## Risks and test signals
Risks include cleartext LDAP when StartTLS/LDAPS is not used, accepting malformed Basic payloads by returning null without setting a failure status after a bad credential split, unsafe username-to-DN string concatenation, disabled hostname verification in tests, and domain detection ambiguity when both `/` and `@` are present. Tests should cover missing and mutually exclusive config, StartTLS with `ldaps` rejection, UTF-8 passwords, empty/NUL-leading password rejection, bind-domain appending, provider failures, and TLS hostname verification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/LdapAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/MultiSchemeAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/MultiSchemeAuthenticationHandler.java

## Purpose
Provides a composite server authentication handler that advertises and dispatches multiple HTTP authentication schemes, such as `Negotiate` and `Basic`, while preserving the token types of the delegated handlers.

## Important APIs, types, and functions
`SCHEMES_PROPERTY` configures the comma-separated scheme list, and `AUTH_HANDLER_PROPERTY` maps each scheme to a handler type/class. `getTokenTypes()` exposes delegated token types to `AuthenticationFilter`. `init()` normalizes schemes through `AuthenticationHandlerUtil.checkAuthScheme()`, resolves handler class names, instantiates them through the context class loader, initializes them with the same config, and stores scheme-to-handler mappings. `authenticate()` matches the incoming Authorization scheme and delegates to the selected handler.

## Control flow
Initialization fails if no scheme list exists, if a scheme is duplicated, or if a scheme lacks a handler mapping. Authentication loops configured schemes only when an Authorization header is present. A matching scheme delegates the whole request/response to its handler; otherwise the response gets `401` and one `WWW-Authenticate` header for each configured scheme.

## State and persistence
State is in-memory maps/sets: `schemeToAuthHandlerMapping`, supported token `types`, and `authType`. `destroy()` cascades to all delegated handlers. No state is persisted.

## Dependencies and integration points
Uses Guava `Splitter`, servlet APIs, `AuthenticationHandlerUtil`, and the `CompositeAuthenticationHandler` contract. It is configured through `AuthenticationFilter.AUTH_TYPE=multi-scheme` and shares the same properties with all child handlers.

## Risks and test signals
The class logs all config entries at info level, which can expose secrets such as keytabs, LDAP URLs, or signer values. `authenticate()` logs `token.getType()` without guarding against a delegated null token, so in-progress multi-step handlers can trigger a null dereference. Tests should cover duplicate schemes, case normalization, missing handler mappings, invalid scheme names, multiple `WWW-Authenticate` headers, delegated null tokens, and destroy ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/MultiSchemeAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/PseudoAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/PseudoAuthenticationHandler.java

## Purpose
Implements Hadoop "simple" pseudo-authentication for HTTP by trusting a `user.name` query parameter, with optional anonymous access.

## Important APIs, types, and functions
`TYPE` is `simple`; `ANONYMOUS_ALLOWED` controls anonymous fallback. `init()` reads the boolean flag. `getUserName()` parses the raw query string with `URLEncodedUtils` and UTF-8, returning the first `PseudoAuthenticator.USER_NAME` value. `authenticate()` returns anonymous, null with a forbidden response/challenge, or a new `AuthenticationToken` with user and principal set to the query value.

## Control flow
For each request, the handler parses the query string. Missing username returns `AuthenticationToken.ANONYMOUS` when anonymous mode is enabled; otherwise it sets `403` and `WWW-Authenticate: PseudoAuth` and returns null. Present username is accepted without external verification.

## State and persistence
Only `acceptAnonymous` and token `type` are kept in memory. There is no persistence and no external credential state.

## Dependencies and integration points
Used by `AuthenticationFilter` for simple auth and by client-side `PseudoAuthenticator`, including Kerberos client fallback paths. It relies on Apache HttpComponents query parsing.

## Risks and test signals
The mechanism intentionally trusts caller-supplied identity and should be limited to trusted environments. Risks include duplicate `user.name` parameters, empty values, URL encoding edge cases, and inconsistent status mapping through the filter. Tests should cover anonymous allowed/disallowed paths, GET/POST behavior, query decoding, multiple usernames, empty username values, and interaction with signed auth cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/PseudoAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/package-info.java

## Purpose
Defines package-level documentation and audience/stability annotations for the server-side Hadoop Auth framework.

## Important APIs, types, and functions
The package is annotated `@InterfaceAudience.LimitedPrivate({ "HBase", "HDFS", "MapReduce" })` and `@InterfaceStability.Evolving`. The Javadoc summary states that the package provides the server-side framework for authentication.

## Control flow
No runtime code is present.

## State and persistence
No state or persistence behavior exists.

## Dependencies and integration points
Imports Hadoop classification annotations. Build, generated Javadoc, and downstream API consumers use these annotations to understand compatibility expectations.

## Risks and test signals
Risk is documentation/API-classification drift if server classes become public or incompatible without updating package metadata. Tests are not applicable beyond compilation and documentation generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/AuthToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/AuthToken.java

## Purpose
Represents the serializable principal data stored inside Hadoop Auth cookies before signing. It carries user name, principal, auth type, expiration, and optional max-inactive timestamp.

## Important APIs, types, and functions
`AuthToken(String userName, String principal, String type)` validates required fields. `setExpires()` updates the expiration and regenerates the serialized token; `setMaxInactives()` stores the inactivity timestamp. `isExpired()` checks both expiration and max-inactive values. `toString()` returns the `u=...&p=...&t=...&i=...&e=...` representation. `parse()` strips surrounding quotes, splits key/value pairs, removes a signature field `s`, validates required attributes, parses timestamps, and creates a token.

## Control flow
Tokens start with unset expiration/inactivity. Serialization is generated when expiration is set or in the protected anonymous constructor. Parsing first tokenizes on `&`, then builds a map and rejects missing required attributes. Optional `i` is processed before `e`, which regenerates the final token string.

## State and persistence
The token is mutable in memory and its string form is persisted externally in signed cookies. Attribute values cannot contain `&`, but are otherwise not escaped, so the serialization format is a simple flat key-value protocol.

## Dependencies and integration points
Implements `Principal`; used by `AuthenticationToken`, `AuthenticationFilter`, `AuthenticatedURL`, and `Signer`. Throws client `AuthenticationException` on malformed token strings.

## Risks and test signals
Risks include no escaping for `=`, duplicate attributes overwriting earlier values, `NumberFormatException` escaping from parse for bad timestamps, `setMaxInactives()` not regenerating until `setExpires()` is called, and clock-skew sensitivity. Tests should cover quoted cookies, missing attributes, duplicate keys, bad numeric values, max-inactive-only transitions, reserved separator rejection, and signature-field stripping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/AuthToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/CertificateUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/CertificateUtil.java

## Purpose
Parses an RSA public key from a configured PEM certificate body for authentication components that need an X.509 public key.

## Important APIs, types, and functions
`parseRSAPublicKey(String pem)` wraps the supplied body with certificate header/footer, feeds it to an X.509 `CertificateFactory`, extracts `X509Certificate.getPublicKey()`, and casts the result to `RSAPublicKey`.

## Control flow
The method constructs a full PEM string, parses it from a UTF-8 byte stream, and translates `CertificateException` into `ServletException` with a more specific message if the caller included header/footer text.

## State and persistence
The utility is stateless and persists nothing.

## Dependencies and integration points
Depends on Java security certificate APIs, `RSAPublicKey`, UTF-8 encoding, and servlet exceptions. It is typically used by servlet/filter configuration that carries public certificate material.

## Risks and test signals
The unchecked cast can throw `ClassCastException` for non-RSA certificates. `pem.startsWith(PEM_HEADER)` is only reached after a parsing failure and will throw if `pem` is null. Tests should cover valid RSA certs, certs with included header/footer, corrupt PEM, null input, and non-RSA public keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/CertificateUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/FileSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/FileSignerSecretProvider.java

## Purpose
Provides a fixed signing secret loaded from a UTF-8 text file for Hadoop Auth cookie signing.

## Important APIs, types, and functions
`init()` reads `AuthenticationFilter.SIGNATURE_SECRET_FILE`, streams the whole file as characters, converts it to UTF-8 bytes, rejects an empty secret, and exposes it as a one-element `byte[][]`. `getCurrentSecret()` returns the secret; `getAllSecrets()` returns the array used for verification.

## Control flow
If the secret-file property exists, the provider reads the file and initializes `secret`. I/O failures and empty files become runtime exceptions. Finally it sets `secrets = new byte[][] { secret }`.

## State and persistence
The configured secret file is persistent input. The provider keeps the byte secret and array in memory and never reloads the file after init.

## Dependencies and integration points
Used by `AuthenticationFilter` as a `SignerSecretProvider`. Depends on Java NIO file APIs, UTF-8, servlet context arguments, and filter config constants.

## Risks and test signals
If `init()` is called without a file property, `getCurrentSecret()` can return null even though the base contract says it should not. File contents include every character, including trailing newline. Tests should cover missing file property, nonexistent path, empty file fallback behavior in `AuthenticationFilter`, newline preservation, non-ASCII file content, and no-reload semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/FileSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/JaasConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/JaasConfiguration.java

## Purpose
Creates an in-memory JAAS configuration entry for Kerberos keytab login, mainly for ZooKeeper clients that need SASL without an external `jaas.conf`.

## Important APIs, types, and functions
The constructor builds an `AppConfigurationEntry` for the platform Kerberos login module with `keyTab`, `principal`, `useKeyTab`, `storeKey`, `useTicketCache=false`, and `refreshKrb5Config=true`. `getAppConfigurationEntry()` returns this entry for the configured name and delegates other names to the previous base configuration. `getKrb5LoginModuleName()` selects IBM or Sun login module by `java.vendor`.

## Control flow
Construction captures the current global JAAS config as a fallback. Later JAAS lookups for the entry name get the generated Kerberos options; unrelated entry names preserve existing behavior.

## State and persistence
Stores the generated entry and fallback config in memory. When installed with `Configuration.setConfiguration()`, it affects global JVM JAAS behavior until replaced.

## Dependencies and integration points
Used by `ZookeeperClient` for SASL/Kerberos Curator connections. Depends on JAAS `Configuration` and `AppConfigurationEntry`, JVM vendor properties, and optional `HADOOP_JAAS_DEBUG`.

## Risks and test signals
Global JAAS replacement can affect unrelated code in the same JVM. IBM module detection here is simpler than `PlatformName.IBM_JAVA`, which can diverge. Tests should cover entry-name matching, fallback delegation, debug env var, keytab/principal option contents, and IBM/Sun module selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/JaasConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosName.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosName.java

## Purpose
Parses Kerberos principals and applies `auth_to_local` rules to derive local short usernames. It supports Hadoop legacy rule evaluation and MIT-style behavior.

## Important APIs, types, and functions
The constructor parses `service[/host][@realm]`. `setRules()`, `getRules()`, and `parseRules()` manage static rule lists. `setRuleMechanism()` selects `hadoop` or `mit`. `getShortName()` applies rules to the principal components. Inner `Rule` handles `DEFAULT`, `RULE:[n:format](match)s/from/to/[g]/L`, parameter replacement, regex substitution, Hadoop simple-name enforcement, and optional lowercasing. `getDefaultRealm()` lazily obtains the JVM Kerberos default realm through `KerberosUtil`.

## Control flow
Simple names without a realm return immediately. Realm/service/host names become parameter arrays with realm at index 0. Rules are evaluated in order; the first non-null result wins. Hadoop mechanism rejects results containing `/` or `@`; MIT mechanism can return the original full name if no rule matches.

## State and persistence
Rules, rule mechanism, and default realm are static process-wide state. There is no persistence, but setting rules in one filter/test affects later users in the same JVM.

## Dependencies and integration points
Used by `KerberosAuthenticationHandler` and tests to map client Kerberos principals to local users. Depends on regex parsing, locale-aware lowercasing, logging, and `KerberosUtil.getDefaultRealm()`.

## Risks and test signals
Risks include global mutable rule state, regex parsing edge cases, unescaped substitution syntax, null `ruleMechanism` if `getShortName()` is called with no rules, MIT/Hadoop behavior drift, and default realm caching after krb5 config changes. Tests should cover malformed rules, parameter indexes, default rule behavior, lowercasing, global substitutions, non-simple Hadoop rejection, MIT no-match fallback, and reset of default realm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosName.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosUtil.java

## Purpose
Collects Kerberos/JGSS helper functions for login module selection, realm/principal construction, keytab principal enumeration, subject credential checks, and decoding the server principal from GSS/SPNEGO tokens.

## Important APIs, types, and functions
`getKrb5LoginModuleName()` selects IBM or Sun Kerberos login modules. Static OIDs identify SPNEGO, Kerberos V5, and Kerberos principal-name types. `getDefaultRealm()` and `getDomainRealm()` derive realm information from JVM Kerberos libraries. `getServicePrincipal()` builds lowercased `service/fqdn[@realm]` names. `getPrincipalNames()` reads Apache Kerby keytabs and filters by regex. `hasKerberosKeyTab()` and `hasKerberosTicket()` inspect JAAS subjects. `getTokenServerName()` uses an inner DER iterator to parse a raw GSS token and extract the AP-REQ ticket server principal.

## Control flow
Principal construction fills missing hostnames from the local canonical host and then asks Kerberos domain-realm mapping for a realm. Token decoding unwraps SPNEGO if present, verifies the Kerberos OID and AP-REQ token id, traverses ticket DER fields, and joins service components plus realm.

## State and persistence
The class is stateless except for static OID constants. It reads persistent keytab files but does not modify them.

## Dependencies and integration points
Depends on JGSS, JAAS subject classes, Java Kerberos principal/ticket/keytab types, Apache Kerby keytab parsing, reflection into Sun/IBM Kerberos internals, networking host lookup, and `PlatformName.IBM_JAVA`. Used by Kerberos server/client tests, `KerberosAuthenticationHandler`, and JAAS helpers.

## Risks and test signals
DER parsing is minimal and can throw runtime buffer/tag exceptions for malformed or truncated tokens. Reflection into internal Kerberos classes may fail under module restrictions. Keytab reading normalizes escaped slashes. Tests should cover malformed token lengths, SPNEGO and raw Kerberos tokens, non-Kerberos OIDs, keytab duplicate principals, wildcard filtering, default realm absence, service principal host normalization, and IBM/Sun login module behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RandomSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RandomSignerSecretProvider.java

## Purpose
Provides rolling random secrets for signing Hadoop Auth cookies when no shared configured secret is supplied.

## Important APIs, types, and functions
Extends `RolloverSignerSecretProvider`. The default constructor uses `SecureRandom`; the testing constructor uses deterministic `Random(seed)`. `generateNewSecret()` returns a new 32-byte secret.

## Control flow
The superclass initializes a current secret and schedules rollover at token-validity intervals. Each rollover calls `generateNewSecret()` to replace current/previous secrets.

## State and persistence
State is the random generator and inherited in-memory secret array. Secrets are not persisted, so process restart invalidates existing cookies unless a shared provider is used.

## Dependencies and integration points
Used by `AuthenticationFilter` fallback secret-provider selection. Depends on Java random APIs and inherited scheduler behavior.

## Risks and test signals
Random fallback is not cluster-stable and can log users out across restart or load-balanced instances. Tests should cover generated length, deterministic seeded output, inherited rollover acceptance of previous secret, and restart invalidation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RandomSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RolloverSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RolloverSignerSecretProvider.java

## Purpose
Base class for signer-secret providers that rotate secrets while keeping the immediately previous secret valid for cookie verification.

## Important APIs, types, and functions
`init()` creates the initial secret and starts a scheduled rollover. `initSecrets()` initializes `{current, previous}`. `startScheduler()` starts a single-thread fixed-rate executor. `rollSecret()` generates a new secret and shifts the old current secret into previous. `getCurrentSecret()` and `getAllSecrets()` expose secrets to `Signer`. `destroy()` shuts down the scheduler.

## Control flow
Subclasses implement `generateNewSecret()`. The scheduler first runs after `tokenValidity` milliseconds and then repeats at the same period. Reads observe a volatile `byte[][]` so sign/verify callers see atomically replaced secret arrays.

## State and persistence
State is in-memory only: current/previous secret array, scheduler, and lifecycle booleans. There is no durable persistence in this base class.

## Dependencies and integration points
Extended by `RandomSignerSecretProvider` and `ZKSignerSecretProvider`. Used by `Signer` through the `SignerSecretProvider` contract.

## Risks and test signals
Risks include scheduler thread lifecycle leaks, invalid token-validity values, null secrets from subclasses, returning mutable secret arrays, and lack of `awaitTermination()` on destroy. Tests should cover rollover timing, previous-secret verification, repeated destroy, concurrent reads during rollover, and subclass null-secret failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/RolloverSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/Signer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/Signer.java

## Purpose
Signs and verifies string values, primarily Hadoop Auth token cookies, using HMAC-SHA256 and secrets supplied by a `SignerSecretProvider`.

## Important APIs, types, and functions
`sign(String str)` rejects null/empty values, signs with the current secret, and appends `&s=<base64-hmac>`. `verifyAndExtract(String signedStr)` finds the final signature delimiter, verifies against all currently valid secrets, and returns the unsigned value. `computeSignature()` performs HmacSHA256 over UTF-8 bytes and Base64 encodes the MAC. `checkSignatures()` uses `MessageDigest.isEqual()` for comparison.

## Control flow
Signing uses only `getCurrentSecret()`. Verification accepts any non-null secret returned by `getAllSecrets()`, allowing current and previous rollover secrets. Invalid or missing signatures throw `SignerException`.

## State and persistence
The signer stores only the provider reference. Signed strings are externally persisted in cookies or headers, with the raw value and signature delimiter in one string.

## Dependencies and integration points
Used by `AuthenticationFilter` and tests for cookie signing. Depends on JCE `Mac`, `SecretKeySpec`, Commons Codec Base64/StringUtils, and `SignerSecretProvider`.

## Risks and test signals
The delimiter is searched with `lastIndexOf`, so raw values can contain earlier `&s=` fragments. Null provider secrets can fail at sign time. Signature error messages include the full signed text for missing signatures. Tests should cover current/previous secret verification, tampering, delimiter collisions, empty input, null provider output, constant-time comparison behavior, and algorithm availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/Signer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerException.java

## Purpose
Defines the checked exception thrown when signed text is missing a signature or fails signature verification.

## Important APIs, types, and functions
`SignerException(String msg)` stores a failure message. `serialVersionUID` is fixed at zero.

## Control flow
No internal control flow beyond exception construction.

## State and persistence
Carries only the inherited exception message/cause state. No persistence occurs.

## Dependencies and integration points
Thrown by `Signer.verifyAndExtract()` and propagated to authentication-token parsing paths.

## Risks and test signals
The class has no cause-taking constructor, so callers cannot preserve underlying crypto/provider exceptions as causes. Tests should assert expected messages for missing and invalid signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerSecretProvider.java

## Purpose
Defines the abstraction that supplies signing secrets to `Signer`, allowing fixed, file, random, ZooKeeper-backed, and custom providers.

## Important APIs, types, and functions
`init(Properties, ServletContext, long)` initializes provider state using filter configuration and token validity. `destroy()` is a lifecycle hook. `getCurrentSecret()` returns the secret for new signatures. `getAllSecrets()` returns every still-valid secret for verification.

## Control flow
Subclasses implement initialization and secret retrieval. The base class only supplies a no-op destroy.

## State and persistence
No base state exists. Subclasses decide whether secrets are in-memory only, file-backed, or ZooKeeper-backed.

## Dependencies and integration points
Used by `Signer` and selected by `AuthenticationFilter`. Accepts servlet context so providers can share clients or externally supplied objects.

## Risks and test signals
The contract says current secret should never be null and callers should not mutate returned arrays, but this is not enforced. Tests for each implementation should verify non-null current secret, all-secrets includes current, lifecycle cleanup, and mutation isolation or documented mutability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SubjectUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SubjectUtil.java

## Purpose
Provides a compatibility layer over JAAS `Subject` APIs across Java versions where Security Manager-related APIs are deprecated, disabled, or replaced by `Subject.callAs()`/`Subject.current()`.

## Important APIs, types, and functions
Static method handles are resolved for `Subject.callAs`, `Subject.doAs`, `Subject.doAs(PrivilegedExceptionAction)`, and current subject lookup. `THREAD_INHERITS_SUBJECT` captures whether new threads inherit the subject on the current Java version. Public `callAs()`, `doAs(PrivilegedAction)`, `doAs(PrivilegedExceptionAction)`, and `current()` invoke the best available API. Helper adapters convert between `Callable` and privileged actions, and `sneakyThrow()` preserves exception behavior.

## Control flow
Class initialization probes Java APIs reflectively. Java 18+ uses `callAs` when available; older JVMs use `doAs`. Current subject lookup prefers `Subject.current()` and falls back to `Subject.getSubject(AccessController.getContext())`. Exception wrapping is adjusted so public methods mimic legacy API expectations.

## State and persistence
All state is static method-handle and Java-version metadata. No persistence exists.

## Dependencies and integration points
Used by Hadoop code that needs JAAS subject context without binding directly to Security Manager APIs. Depends on method handles, JAAS `Subject`, privileged action types, `Callable`, and Java specification version.

## Risks and test signals
Risks include Java-version parsing assumptions, class-initialization failure if fallback APIs are unavailable, behavior differences in checked exception wrapping across versions, and incorrect thread-subject inheritance assumptions on Java 22/23. Tests should run on multiple Java versions, cover runtime and checked exceptions, null actions, current-subject lookup, and thread inheritance decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SubjectUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZKSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZKSignerSecretProvider.java

## Purpose
Synchronizes rolling signer secrets across multiple servers through a ZooKeeper znode so load-balanced Hadoop Auth instances can validate each other's cookies.

## Important APIs, types, and functions
Configuration constants cover connection string, znode path, auth type, Kerberos keytab/principal, TLS keystore/truststore settings, custom Curator client sharing, and disconnect behavior. `init()` obtains or creates a Curator client, creates the znode if absent, pulls shared data, and schedules rollover aligned with the znode timestamp. `rollSecret()` shifts local secrets, advances `nextRolloverDate`, proposes new znode data, and pulls the winning next secret. `generateZKData()` serializes data version, next/current/previous secret lengths and values, and next rollover time. `pullFromZK()` parses znode data and znode version. `createCuratorClient()` delegates to `ZookeeperClient`.

## Control flow
On startup, every instance attempts to create the secret znode; one wins, others read existing data. Writes use ZooKeeper version checks so concurrent rollovers let one server's proposal win. New servers compute initial delay from the stored next rollover date, advancing by token-validity intervals if the date is already in the past.

## State and persistence
Persistent state is the znode payload containing secrets and next rollover time. Local state includes `nextSecret`, `zkVersion`, `nextRolloverDate`, `tokenValidity`, Curator client, disconnect policy, and inherited current/previous secrets.

## Dependencies and integration points
Extends `RolloverSignerSecretProvider`, uses Curator/ZooKeeper APIs, `ZookeeperClient`, servlet context custom-client attribute, and filter configuration. It integrates with `AuthenticationFilter` as a shared signer provider.

## Risks and test signals
Secrets are stored raw in ZooKeeper, so ACL/TLS/SASL configuration is critical. `pullFromZK()` logs and swallows unexpected parse/read failures, which can leave stale or null `nextSecret`. Rollover timing depends on local clocks. Tests should cover first creator vs joiner, BadVersion races, corrupt/newer znode data, missing path, custom Curator lifecycle, disconnect flag, TLS/SASL config propagation, delayed startup after missed rollovers, and cookie verification across instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZKSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZookeeperClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZookeeperClient.java

## Purpose
Builds configured Curator `CuratorFramework` clients for ZooKeeper connections, including optional SASL/Kerberos ACLs and SSL/TLS client settings.

## Important APIs, types, and functions
The fluent builder methods set connection string, namespace, auth type, keytab, principal, JAAS login entry, timeouts, retry policy, ZooKeeper factory, SSL enablement, and keystore/truststore paths/passwords. `create()` validates mandatory state and builds a Curator framework. `aclProvider()` configures open ACLs for `none` auth or installs a global JAAS configuration and SASL owner ACLs for `sasl`. `zkClientConfig()` fills ZooKeeper SSL client properties. `SASLOwnerACLProvider` returns all-permission SASL ACLs for one principal short name.

## Control flow
`create()` composes Curator builder state in one pass. SASL mode requires non-empty keytab, principal, and login entry, installs JVM-wide ZooKeeper auth properties, and creates a restricted ACL provider. SSL mode requires keystore and truststore locations and sets the Netty secure client socket.

## State and persistence
Builder state is held in instance fields until `create()`. It mutates JVM-global JAAS and ZooKeeper system properties in SASL mode. No ZooKeeper data is persisted by this class directly.

## Dependencies and integration points
Used by `ZKSignerSecretProvider` and Hadoop common ZooKeeper delegation-token code. Depends on Curator, ZooKeeper client config/X509 utilities, `JaasConfiguration`, and Hadoop classification/testing annotations.

## Risks and test signals
Global JAAS/system-property changes can affect all ZooKeeper clients in the JVM. Principal ACL uses `principal.split("[/@]")[0]`, which may not match server-side SASL identities in every deployment. Passwords are passed as strings. Tests should cover auth-type validation, missing SASL inputs, SSL missing store paths, namespace/timeouts/retry propagation, ACL principal derivation, and interaction between multiple clients with different JAAS entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZookeeperClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/util/PlatformName.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/util/PlatformName.java

## Purpose
Exposes JVM/platform identity constants and detects IBM Java Technology Edition modules for code paths that need vendor-specific security classes.

## Important APIs, types, and functions
`PLATFORM_NAME` combines OS name, architecture, and data-model system properties. `JAVA_VENDOR_NAME` stores `java.vendor`. `IBM_JAVA` is true only when the vendor contains `IBM` and at least one IBM Technology Edition security/login module is loadable. `SystemClassAccessor` exposes `findSystemClass()` for module-aware probing. `main()` prints `PLATFORM_NAME`.

## Control flow
Static initialization computes the platform string and vendor flag. IBM module detection checks a fixed list of module class names through a privileged action.

## State and persistence
State is static process metadata derived from system properties and class availability. No persistence occurs.

## Dependencies and integration points
Used by Kerberos utilities and tests to select IBM vs Sun login-module behavior. Depends on `AccessController`, `PrivilegedAction`, and Hadoop classification annotations.

## Risks and test signals
`AccessController` is deprecated for removal, and `sun.arch.data.model` may be missing on some JVMs. Vendor-name checks can misclassify Semeru or future IBM runtimes without module probing. Tests should cover standard OpenJDK, IBM/Semeru-like module presence, Windows `os` environment behavior, missing data-model property, and `main()` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/util/PlatformName.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/site/site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/site/site.xml

## Purpose
Defines Maven Site metadata for the Hadoop Auth module.

## Important APIs, types, and functions
The XML declares project name `Hadoop Auth`, selects the `maven-stylus-skin` with a version property, and adds a body link to the Apache Hadoop website.

## Control flow
Maven site generation reads this descriptor to render module documentation. There is no application runtime flow.

## State and persistence
The file is persistent build/documentation configuration. It does not affect runtime authentication state.

## Dependencies and integration points
Integrates with Maven Site Plugin and module documentation under `src/site`. The skin version is supplied by Maven properties.

## Risks and test signals
Risks are broken site generation if the skin version property is missing or the external link changes. Tests/signals are Maven site build success and generated navigation correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/site/site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/KerberosTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/KerberosTestUtils.java

## Purpose
Provides shared test utilities for MiniKDC-backed Kerberos authentication tests, including canonical test principals, keytab path generation, and helper methods that run callables as client or server subjects.

## Important APIs, types, and functions
`getRealm()`, `getClientPrincipal()`, `getServerPrincipal()`, and `getKeytabFile()` centralize test identity values. Inner `KerberosConfiguration` builds JAAS login options for IBM and non-IBM JVMs, including keytab, ticket cache, and debug options. `doAs()`, `doAsClient()`, and `doAsServer()` create a `LoginContext`, login with the test principal, run a callable through `Subject.doAs()`, and logout.

## Control flow
Tests create principals in the shared keytab, then wrap authenticated work in `doAsClient()` or `doAsServer()`. The helper preserves checked exceptions from the callable by unwrapping `PrivilegedActionException`.

## State and persistence
The generated keytab path is static and lives under `test.dir` or `target`. Login state is transient per helper invocation. It may interact with `KRB5CCNAME` environment/system properties.

## Dependencies and integration points
Used by Kerberos client/server tests and MiniKDC setup. Depends on JAAS, Kerberos principals, `KerberosUtil`, `PlatformName.IBM_JAVA`, and test keytab files.

## Risks and test signals
The static keytab path can leak across tests in the same JVM. Debug mode is always enabled. Tests using this helper are sensitive to local Kerberos/JDK behavior, ticket caches, and IBM option names. Signals include successful MiniKDC principal creation, login/logout cleanup, and both client/server principal execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/KerberosTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/AuthenticatorTestCase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/AuthenticatorTestCase.java

## Purpose
Provides an embedded Jetty test harness for client authenticator integration tests against `AuthenticationFilter`.

## Important APIs, types, and functions
`setAuthenticationHandlerConfig()` supplies filter configuration to `TestFilter`. `startJetty()` creates a Jetty server under `/foo`, installs the authentication filter, and serves `/bar` with `TestServlet`. `_testAuthentication()` verifies `AuthenticatedURL` behavior for GET/POST, connection configurator invocation, cookie token reuse, and echo POSTs. `_testAuthenticationHttpClient()` configures Apache HttpClient with SPNEGO support and validates GET plus optional non-repeatable POST entity behavior.

## Control flow
Each test starts Jetty on a free local port, performs authenticated client operations, and stops/destroys the server in a finally block. The POST path writes request bytes and expects the servlet to echo them.

## State and persistence
State is test-local Jetty server, host/port, servlet context, and static authenticator properties. No durable state is written.

## Dependencies and integration points
Used by pseudo and Kerberos client tests. Depends on Jetty, servlet APIs, Apache HttpClient/SPNEGO, `AuthenticationFilter`, `AuthenticatedURL`, and test connection configurators.

## Risks and test signals
Static configuration can bleed between tests if not reset. Free-port selection has a bind race. Signals include successful cookie reuse, no renegotiation for non-repeatable POST entities, configurator invocation, and proper server teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/AuthenticatorTestCase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestAuthenticatedURL.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestAuthenticatedURL.java

## Purpose
Unit-tests client-side `AuthenticatedURL` token handling, connection configuration, and cookie extraction behavior.

## Important APIs, types, and functions
Tests cover `AuthenticatedURL.Token` set/unset state, `injectToken()` adding a Cookie request property, `extractToken()` on successful and unauthorized responses, lower-case `set-cookie` response headers, connection configurator invocation, and `getAuthenticator()`.

## Control flow
Mockito mocks `HttpURLConnection` headers and response codes. Successful extraction reads `Set-Cookie`; unauthorized extraction clears the existing token and throws `AuthenticationException`.

## State and persistence
State is confined to test `Token` objects and mocked header maps. No external state is used.

## Dependencies and integration points
Exercises client code that interacts with server `AuthenticationFilter` cookies. Depends on JUnit 5 and Mockito.

## Risks and test signals
Signals include case-insensitive cookie header handling and token clearing on auth failure. Gaps include multiple cookies in one header, cookie attributes, malformed cookie values, null header maps, and redirect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestAuthenticatedURL.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestKerberosAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestKerberosAuthenticator.java

## Purpose
Integration and unit tests for the client-side Kerberos/SPNEGO authenticator, including fallback to pseudo auth and multi-scheme handler operation.

## Important APIs, types, and functions
`setup()` creates client and server principals in the MiniKDC keytab. Helper methods build Kerberos and multi-scheme filter configs. Tests cover pseudo fallback with and without anonymous access, unauthenticated `401` Negotiate challenge, Kerberos GET/POST through `AuthenticatedURL`, Apache HttpClient SPNEGO GET/POST, multi-scheme Negotiate configuration, exception wrapping, and private `isNegotiate()`/`readToken()` handling for normal and lower-case headers.

## Control flow
Kerberos integration tests run client operations inside `KerberosTestUtils.doAsClient()`. The embedded Jetty filter is configured for Kerberos or multi-scheme auth and expected to issue/accept signed auth cookies after SPNEGO negotiation.

## State and persistence
State includes MiniKDC principals and the shared keytab file. Test configuration is static through `AuthenticatorTestCase`.

## Dependencies and integration points
Depends on MiniKDC, Kerberos test utilities, `AuthenticationFilter`, `KerberosAuthenticationHandler`, `MultiSchemeAuthenticationHandler`, `PseudoAuthenticationHandler`, Apache Commons reflection utilities, Mockito, and JUnit timeouts.

## Risks and test signals
Signals cover end-to-end SPNEGO, cookie reuse for POST, multi-scheme challenge handling, and lower-case header compatibility. Gaps include malformed SPNEGO server tokens, expired Kerberos credentials, proxy/redirect behavior, and multiple `WWW-Authenticate` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestKerberosAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestPseudoAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestPseudoAuthenticator.java

## Purpose
Tests client-side pseudo authentication against the server pseudo handler, including anonymous access behavior and POST handling.

## Important APIs, types, and functions
`getAuthenticationHandlerConfiguration()` sets `AUTH_TYPE=simple` and anonymous mode. Tests cover `PseudoAuthenticator.getUserName()`, raw server behavior with anonymous allowed/disallowed, and full `AuthenticatorTestCase._testAuthentication()` for GET and POST with anonymous allowed/disallowed.

## Control flow
The tests configure the embedded filter for simple auth, start Jetty through the shared harness, and assert expected HTTP codes or authenticated request success.

## State and persistence
Only static test filter properties and JVM `user.name` are used. No durable state exists.

## Dependencies and integration points
Depends on `AuthenticatorTestCase`, `AuthenticationFilter`, `PseudoAuthenticationHandler`, `PseudoAuthenticator`, and JUnit assertions.

## Risks and test signals
Signals include anonymous disallowed producing unauthorized filter behavior and pseudo client adding username for successful auth. Gaps include URL encoding of usernames, duplicate `user.name` query parameters, empty username values, and non-default system user names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestPseudoAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/LdapConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/LdapConstants.java

## Purpose
Defines shared constants for LDAP integration tests.

## Important APIs, types, and functions
`LDAP_BASE_DN` is `dc=example,dc=com` and `LDAP_SERVER_ADDR` is `localhost`. The private constructor prevents instantiation.

## Control flow
No runtime control flow beyond class loading.

## State and persistence
Static constant state only. No persistence exists.

## Dependencies and integration points
Consumed by LDAP authentication handler tests that need a consistent local LDAP address and base DN.

## Risks and test signals
Hard-coded localhost assumptions require tests to provision a local LDAP server. Signals are compile-time access and integration-test configuration consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/LdapConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAltKerberosAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAltKerberosAuthenticationHandler.java

## Purpose
Tests alternate Kerberos handler behavior for browser-like user agents while reusing the standard Kerberos handler test suite for non-browser cases.

## Important APIs, types, and functions
Overrides `getNewAuthenticationHandler()` to instantiate an anonymous `AltKerberosAuthenticationHandler` whose `alternateAuthenticate()` returns a fixed token. `getExpectedType()` expects `alt-kerberos`. Tests configure `alt-kerberos.non-browser.user-agents` and assert browser/non-browser routing.

## Control flow
Browser-like user agents invoke alternate authentication and return token `A/B`. Non-browser user-agent configuration defers to inherited Kerberos tests for missing, invalid, valid, and invalid-Kerberos Authorization headers.

## State and persistence
Uses inherited MiniKDC/keytab handler state from `TestKerberosAuthenticationHandler`. No durable state is created by this subclass beyond test keytabs.

## Dependencies and integration points
Depends on `AltKerberosAuthenticationHandler`, inherited `TestKerberosAuthenticationHandler`, servlet mocks, Mockito, and JUnit timeouts.

## Risks and test signals
Signals include configurable non-browser user-agent matching and alternate token type preservation. Gaps include null User-Agent, mixed-case user-agent matching, overlapping browser/non-browser substrings, and real SPNEGO browser negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAltKerberosAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationFilter.java

## Purpose
Unit-tests the core server `AuthenticationFilter` lifecycle, configuration parsing, signer-provider selection, cookie token validation, request wrapping, expiration/inactivity behavior, and management-operation short circuiting.

## Important APIs, types, and functions
`DummyAuthenticationHandler` simulates success, failure, expiration, and management operation outcomes. Tests cover config-prefix stripping, missing auth type, random/file/custom signer providers, empty secret-file fallback, cookie domain/path, case-insensitive auth type, request URL reconstruction, signed token parsing, expired/invalid token rejection, unauthenticated responses, successful authentication cookie issuance, invalid cookie replacement, wrapped remote user/principal, failure clearing cookies, max-inactive interval renewal, and management operations.

## Control flow
Most tests initialize a filter with mocked `FilterConfig`/`ServletContext`, build mocked servlet requests/responses, and verify response headers/status or filter-chain invocation. Signed cookies are produced with `Signer` and parsed back through `AuthenticationToken`.

## State and persistence
State is mocked servlet context attributes, temporary secret files, generated cookies, and filter fields. Cookies represent externally persisted auth state for the duration of requests.

## Dependencies and integration points
Exercises `AuthenticationFilter`, `AuthenticationHandler`, `AuthenticationToken`, `AuthenticatedURL.AUTH_COOKIE`, `Signer`, `SignerSecretProvider`, and `StringSignerSecretProviderCreator`. Depends on Mockito, AssertJ, and JUnit.

## Risks and test signals
Signals are strong for cookie signing, expiry, inactivity renewal, and lifecycle behavior. Gaps include real servlet-container header casing, concurrent requests during secret rollover, malformed cookie parsing beyond simple invalid strings, SameSite/Secure/HttpOnly attributes, and custom provider failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationToken.java

## Purpose
Tests the server-facing `AuthenticationToken.ANONYMOUS` singleton.

## Important APIs, types, and functions
`testAnonymous()` asserts that the anonymous token exists, has null user/principal/type, has expiration `-1`, and is not expired.

## Control flow
Single assertion-only unit test; no setup or teardown.

## State and persistence
Reads static anonymous token state only. No persistence exists.

## Dependencies and integration points
Depends on `AuthenticationToken` and JUnit assertions. Covers behavior inherited from `AuthToken` anonymous construction.

## Risks and test signals
Signal is narrow but protects anonymous-token contract relied on by pseudo and whitelist authentication paths. Gaps include normal token serialization/parsing, max-inactive behavior, equality, and mutation of anonymous token state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationToken.java -->
