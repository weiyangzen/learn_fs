<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenManager.java

## Purpose
Parameterized smoke test for web `DelegationTokenManager` create, verify, renew, cancel, and post-cancel invalidation behavior with and without the ZK-key option flag.

## Important APIs, Types, And Functions
Targets `DelegationTokenManager.init`, `createToken`, `verifyToken`, `renewToken`, `cancelToken`, and `destroy`. Config keys include update interval, max lifetime, renew interval, removal scan interval, and `ENABLE_ZK_KEY`.

## Control Flow
The parameterized test initializes manager configuration with day-long intervals, creates a manager for token kind `foo`, creates a token for the current user and renewer `foo`, verifies and renews it, cancels it, and then expects verification to fail with `IOException`.

## State And Persistence
State is the manager's token secret manager and background threads. The test does not create a ZooKeeper server, and the line using `conf.getBoolean` reads rather than sets `ENABLE_ZK_KEY`, so the intended parameter may not actually affect configuration.

## Dependencies And Integration Points
Depends on Hadoop web delegation-token manager, `UserGroupInformation`, JUnit parameterization, and token APIs. It is a quick lifecycle contract for the web token manager.

## Risks
The `ENABLE_ZK_KEY` parameter appears ineffective because it is read from the configuration instead of written into it. This limits coverage of the ZK-enabled path here, leaving that path mostly to `TestZKDelegationTokenSecretManager`.

## Test Signals
Signals are non-null token creation, successful verification, renew time greater than current wall clock, successful cancellation, and verification failure after cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenManager.java -->
