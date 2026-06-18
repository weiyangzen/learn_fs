<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestZKDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestZKDelegationTokenSecretManager.java

## Purpose
Tests ZooKeeper-backed delegation-token secret-manager behavior across multiple token-manager instances, startup/restart, cancellation propagation, sequence-number batching, ACLs, namespace creation, concurrent initialization, and shutdown.

## Important APIs, Types, And Functions
Uses Curator `TestingServer`, `CuratorFramework`, `ACLProvider`, `DelegationTokenManager`, `ZKDelegationTokenSecretManager`, and `DelegationTokenIdentifier`. Helpers include `getSecretConf`, `verifyDestroy`, `verifyTokenFail`, `verifyTokenFailWithRetry`, and `verifyACL`.

## Control Flow
Setup starts an in-process ZooKeeper server for each test. Multi-node tests create two or three `DelegationTokenManager` instances sharing the same ZK path, create/verify/renew/cancel tokens across nodes, and retry invalid-token checks to allow watcher propagation. Restart tests ensure cancelled tokens are not reloaded and live tokens are loaded then removed after expiry. Namespace and multiple-init tests exercise Curator parent-container creation and races. ACL tests inject a digest-auth Curator client and verify the working path ACL.

## State And Persistence
Persistent state lives in ZooKeeper znodes under the configured working path, including token records, key records, and sequence counters. Each manager also has in-memory token/key caches and background threads that are destroyed after tests.

## Dependencies And Integration Points
Depends on Apache Curator, ZooKeeper ACL/digest auth, Hadoop web `DelegationTokenManager`, `UserGroupInformation`, token APIs, and Hadoop test wait utilities. It validates distributed token state sharing for HA services.

## Risks
Tests are integration-heavy and timing-sensitive because watcher propagation and cleanup are eventually consistent. Static `ZKDelegationTokenSecretManager.setCurator` must be reset to avoid leaking clients. Method ordering indicates possible historical interdependence or resource sensitivity.

## Test Signals
Signals include cross-node token verification/renew/cancel success, invalid-token failure after cancellation, sequence numbers jumping by configured batch size for a second node, clean destroy, digest ACL equality, cancelled-token absence after restart, expired-token ZK removal, namespace existence, expected `NodeExists` on repeated creation, and successful concurrent init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/TestZKDelegationTokenSecretManager.java -->
