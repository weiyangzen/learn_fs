# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/RouterSecurityManager.java

## Purpose
`RouterSecurityManager` owns the router delegation token secret manager and exposes token issue, renew, cancel, credential creation, and verification operations.

## Important APIs, Types, And Functions
Constructors either create a secret manager through `FederationUtil.newSecretManager(conf)` when Kerberos authentication is configured or accept one for tests. Public methods include `getSecretManager`, `stop`, `getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, static `createCredentials`, and `verifyToken`. Internal helpers inspect remote-user authentication and audit token operations.

## Control Flow
Initialization only starts token management for Kerberos-configured routers. Token issue and renewal first verify that the connection auth method is Kerberos, Kerberos SSL, or certificate when security is enabled. Issue constructs a `DelegationTokenIdentifier` from owner, renewer, and real user, then creates a `Token` backed by the secret manager. Renewal and cancel delegate to the secret manager and decode token identifiers for audit logging on success or access-control failure.

## State, Persistence, And Dependencies
The manager stores one `AbstractDelegationTokenSecretManager<DelegationTokenIdentifier>`. Actual token/key persistence is delegated to the configured secret manager implementation, such as SQL or ZooKeeper. It depends on `RouterRpcServer.getRemoteUser`, Hadoop security classes, `DFSUtil`, and router RPC address for token service setup.

## Integration Points
Router RPC token protocol methods call this manager. WebHDFS uses `createCredentials` and `verifyToken` for URL-token flows. `FederationUtil.newSecretManager` selects the backing implementation.

## Risks
If security is enabled but the secret manager is absent or stopped, token issue returns null or initialization fails. Audit logging is debug-only and local. Auth checks depend on correctly unwrapping proxy users. `cancelDelegationToken` does not call `isAllowedDelegationTokenOp`, relying on secret-manager authorization instead.

## Test Signals
Tests should cover Kerberos and non-Kerberos initialization, token issue for proxy and non-proxy users, rejected simple-auth operations, renew/cancel access-control failures with audit token IDs, WebHDFS credential token service assignment, and `stop` calling `stopThreads`.
