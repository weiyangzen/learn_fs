<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticationHandler.java

Source read size: 55 lines, 2477 bytes.

## Purpose
Delegation-token HTTP authentication handler for Hadoop simple/pseudo authentication deployments.

## Important APIs, Types, and Functions
Extends `DelegationTokenAuthenticationHandler` by wrapping a `PseudoAuthenticationHandler` with type suffix `-dt`.

## Control Flow, State, and Persistence Behavior
The parent handler implements all token management and token verification. The wrapped pseudo handler supplies simple user-name based authentication for management operations and fallback requests. No additional state or persistence is introduced here.

## Dependencies and Integration Points
Selected by `DelegationTokenAuthenticationFilter` when the configured auth type is pseudo/simple. Integrates with `PseudoDelegationTokenAuthenticator` clients and the same `DelegationTokenManager` used for Kerberos mode.

## Risks and Test Signals
Risks are mostly security posture: pseudo auth trusts request user identity, so token issuance is only appropriate where simple auth is acceptable. Test filter rewrite, simple user token issuance, renew/cancel authorization, token-authenticated request identity, and doAs proxy authorization in pseudo mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticationHandler.java -->
