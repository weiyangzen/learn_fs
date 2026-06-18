<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenManager.java

Source read size: 233 lines, 8442 bytes.

## Purpose
Facade used by HTTP authentication handlers to create, renew, cancel, and verify web delegation tokens while hiding whether the underlying secret manager is local in-memory or ZooKeeper-backed.

## Important APIs, Types, and Functions
Important config keys are `zk-dt-secret-manager.enable` and timing keys under `delegation-token.*`. Nested `DelegationTokenSecretManager` and `ZKSecretManager` create `DelegationTokenIdentifier` instances and decode tokens with the configured kind. Public APIs are `setExternalDelegationTokenSecretManager()`, `init()`, `destroy()`, `createToken()`, `renewToken()`, `cancelToken()`, `verifyToken()`, and `getDelegationTokenSecretManager()`.

## Control Flow, State, and Persistence Behavior
Construction chooses ZK or local secret manager and marks it managed. `init()` starts managed secret-manager threads; `destroy()` stops them. External secret-manager injection stops the initially created manager and transfers lifecycle ownership to the caller. Token creation derives owner/real user from UGI, defaults renewer to the caller short name, creates a Hadoop `Token`, and optionally sets its service. Cancel uses the verifier to infer canceller when none is supplied.

## Dependencies and Integration Points
Integrates web handlers with `AbstractDelegationTokenSecretManager`, `ZKDelegationTokenSecretManager`, `DelegationTokenIdentifier`, `UserGroupInformation`, and Hadoop `Token`.

## Risks and Test Signals
Risks include raw generic casts, lifecycle confusion when replacing secret managers, token kind mismatch during decode, and default renewer behavior affecting authorization. Test local vs ZK construction, managed lifecycle, external manager replacement, create with service/real user, renew authorization, cancel with explicit and inferred canceller, verify password failure, and token kind mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenManager.java -->
