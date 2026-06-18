<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationHandler.java

Source read size: 423 lines, 16844 bytes.

## Purpose
Server-side authentication handler decorator that adds delegation-token management and token-based authentication to an underlying HTTP auth mechanism such as Kerberos or pseudo auth.

## Important APIs, Types, and Functions
Implements `AuthenticationHandler`. Key methods are `init()`, `initTokenManager()`, `initJsonFactory()`, `managementOperation()`, `authenticate()`, `isManagementOperation()`, `destroy()`, and `setExternalDelegationTokenSecretManager()`. It recognizes token ops from `KerberosDelegationTokenAuthenticator`: get, renew, and cancel.

## Control Flow, State, and Persistence Behavior
Initialization starts the wrapped handler, creates a `DelegationTokenManager` for configured token kind, and optionally configures Jackson generator features. Management operations validate HTTP method, authenticate with the wrapped handler when Kerberos credentials are required, build proxy UGI for `doAs`, and execute create/renew/cancel through the token manager. Successful get/renew responses are JSON. Normal authentication first checks delegation token header or query parameter, verifies the token, creates an ephemeral `AuthenticationToken`, and stores the token UGI on the request; otherwise it falls back to the wrapped handler.

## Dependencies and Integration Points
Depends on Hadoop Auth server interfaces, `DelegationTokenManager`, `ProxyUsers`, servlet APIs, Jackson, `HttpExceptionUtils`, and client-side operation names shared with `DelegationTokenAuthenticator`.

## Risks and Test Signals
Risks include management-op method mismatches, exposing cancel without Kerberos credentials by design, JSON feature misconfiguration, broad `Throwable` catch during token auth becoming 403, and proxy authorization failures. Test all three operations, missing token parameter errors, bad token decode, method mismatch, doAs success/failure, JSON response shape, header vs query token auth, and fallback handler invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationHandler.java -->
