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
