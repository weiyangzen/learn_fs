# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDelegationTokensWithHA.java

## Purpose
`TestDelegationTokensWithHA` validates delegation token issuance, renewal, cancellation, logical service names, token cloning, and observer-read behavior in an HA cluster. It covers both client-facing DFS APIs and low-level NameNode token verification during failover.

## Important APIs, Types, And Functions
The fixture enables `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`, configures auth-to-local rules, creates a two-NameNode HA cluster with no DataNodes, sets failover configurations, and captures `DelegationTokenSecretManager` from the active. Tests include `testObserverReadProxyProviderWithDT`, `testDelegationTokenDFSApi`, `testDelegationTokenDuringNNFailover`, `testDelegationTokenWithDoAs`, `testHAUtilClonesDelegationTokens`, `testDFSGetCanonicalServiceName`, `testHdfsGetCanonicalServiceName`, and `testCancelAndUpdateDelegationTokens`. Helpers include `getDelegationToken`, `doRenewOrCancel`, `TokenTestAction`, and a blocking `EditLogTailerForTest`.

## Control Flow
The DFS API test gets a token from the HA filesystem, decodes the identifier, verifies the password in the active secret manager, renews through both direct manager and client configuration, checks a bad configuration error, fails over to the second NameNode, then renews and cancels again. The failover-transition test stops the standby tailer, installs a tailer that waits on a monitor, creates a token, transitions the old active to standby, starts transition of the other NameNode to active in another thread, expects standby or retriable exceptions during the transition, then releases tailing and verifies renewal/cancel. Observer-read with delegation tokens recreates a filesystem under a UGI carrying the token and verifies standby/probe failure logging and routing.

## State And Persistence
Token state is stored in NameNode delegation token secret managers and replicated through edit logs. The tests observe token identifiers, passwords, services, UGI token collections, canonical service names, and the edit-log tailer's catch-up gate. `SecurityUtilTestHelper.setTokenServiceUseIp` switches service identity semantics between IP-based and host-based token services.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `HATestUtil`, `HAUtilClient`, `DelegationTokenIdentifier`, `DelegationTokenSelector`, `UserGroupInformation`, `SecurityUtil`, `SubjectInheritingThread`, `ObserverReadProxyProvider`, `AbstractFileSystem`, `DistributedFileSystem`, and `Whitebox`. The tests connect security token code to HA logical URIs, physical NameNode addresses, failover proxy providers, observer reads, and edit log tailing.

## Risks
Failures here can break secure HA clients even if unsecured HA works. Risk centers on token service names for logical URIs, stale secret-manager state during failover, incorrect exception types while transitioning, UGI token replacement after cancellation, and observer read probes that authenticate with delegation tokens. The test uses shared static configuration and mutates security helper state, so cleanup ordering matters.

## Test Signals
Signals include successful token password retrieval, renew/cancel calls before and after failover, expected IOException text for missing logical nameservice mapping, expected `StandbyException` or `RetriableException` during transition, correct UGI token counts and cloned physical-token selection, correct canonical service names, and successful filesystem access after token update.
