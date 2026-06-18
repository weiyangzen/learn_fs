# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslPlainServer.java


Purpose: `SaslPlainServer` implements a SASL PLAIN server mechanism and provider registration for Hadoop authentication paths that need plaintext username/password callbacks.

Important APIs and types: It implements `SaslServer`. Nested `SecurityProvider` registers `SaslServerFactory.PLAIN`; nested `SaslPlainServerFactory` creates servers for mechanism `PLAIN` unless policy forbids plaintext. Core methods include `evaluateResponse()`, `isComplete()`, `getAuthorizationID()`, `getNegotiatedProperty()`, `wrap()`, `unwrap()`, and `dispose()`.

Control flow and state: `evaluateResponse()` accepts one UTF-8 PLAIN payload split into authz, authn, and password by NUL characters. Empty authz defaults to authn. It invokes a callback handler with `NameCallback`, `PasswordCallback`, and `AuthorizeCallback`; if authorized it stores the authorized id. Completion is set in finally, so failed attempts also mark the server complete. QOP is always `auth`; wrap/unwrap throw because PLAIN has no integrity/privacy.

Dependencies and integration: It depends on Java SASL, JAAS callbacks, and Java security provider APIs. Hadoop must register the provider where PLAIN server support is needed.

Risks and test signals: Tests should cover corrupt payloads, null responses, empty authz, authorization failure, callback exceptions, post-completion calls, no-plaintext policy, and dispose cleanup. Plaintext passwords require transport-layer protection if used outside an already protected channel.
