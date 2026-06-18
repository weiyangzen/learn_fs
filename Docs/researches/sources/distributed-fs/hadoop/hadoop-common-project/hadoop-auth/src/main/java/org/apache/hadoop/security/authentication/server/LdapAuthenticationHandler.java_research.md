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
