# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestSaslRPC.java

## Purpose

`TestSaslRPC` is the main SASL-over-Hadoop-RPC integration test. It parameterizes over Hadoop RPC protection/QOP choices and validates token, Kerberos, simple-auth fallback, SASL PLAIN, connection cache, bad-token error, and postponed-response behavior for protobuf RPC.

## Important APIs, Types, And Functions

The class extends `TestRpcBase`. Its parameter source `data()` covers each `QualityOfProtection` plus mixed privacy/authentication cases, including an `AuthSaslPropertiesResolver` that forces server QOP to authentication. Key fixtures include `BadTokenSecretManager`, `CustomSecurityInfo`, `TestPlainCallbacks`, patterns for expected auth failures, `UseToken`, and helpers `createConfForAuth()`, `createServerSecretManager()`, `setupServerUgi()`, `setupClientUgi()`, `setupTokenIfNeeded()`, and `createClientAndQueryAuthMethod()`.

## Control Flow

Each parameterized test calls `initTestSaslRPC()`, which resets configuration to simple auth, sets `hadoop.rpc.protection`, optional SASL resolver class, UGI configuration, global secret-manager flags, fallback behavior, and the protobuf RPC engine. Digest/token tests start a test server with a token secret manager, install a token on the current user, call `getAuthMethod()`, and inspect connection SASL QOP plus server-side `saslServer` retention. The auth matrix starts servers under SIMPLE, TOKEN, or KERBEROS UGIs and creates clients with optional valid, invalid, unrelated, or absent tokens, then compares success or failure strings to expected auth methods and regular expressions.

## State And Persistence Behavior

State is mostly global test configuration: `conf`, UGI authentication configuration, static booleans controlling secret-manager enablement, Java security provider registration for PLAIN, and client connection caches. Token state is held on UGI instances, and tests explicitly stop servers/proxies or clear client connection IDs where cache reuse affects results. There is no durable storage except optional Kerberos keytab use in the manual `main()` path.

## Dependencies And Integration Points

The file exercises `SaslRpcClient`, `SaslRpcServer`, `SaslPlainServer`, UGI, `SecurityUtil`, Hadoop tokens, RPC client fallback flags, `SaslPropertiesResolver`, protobuf RPC service methods from `TestRpcBase`, and `Client.ConnectionId`. It also references HADOOP-17975 and validates a connection-cache fallback flag regression for multiple clients.

## Risks And Test Signals

Risks include global UGI/security leakage, brittle error-message regexes, environment-dependent Kerberos behavior, timing in postponed-response futures, and hidden connection reuse. Test signals include negotiated `AuthMethod`, connection `saslQop`, server `saslServer` disposal behavior, invalid-token `RemoteException` unwrapping, fallback atomic booleans for first and second clients, PLAIN callback completion, and ordered completion of ten randomly released postponed calls under SASL protection.
