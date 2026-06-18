# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSWithZK.java

## Purpose
`TestKMSWithZK.java` verifies that multiple MiniKMS instances can share ZooKeeper-backed signer secrets so an authentication token issued through one instance is accepted by another.

## Important APIs, Types, and Functions
- `createBaseKMSConf(File)` builds a JCEKS-backed simple-auth KMS configuration with key authorization disabled and `GET_KEYS` limited to user `foo`.
- `testMultipleKMSInstancesWithZKSigner()` starts a Curator `TestingServer`, configures `AuthenticationFilter.SIGNER_SECRET_PROVIDER=zookeeper`, sets ZooKeeper connection string and path, starts two `MiniKMS` instances, and performs HTTP requests through `DelegationTokenAuthenticatedURL`.

## Control Flow and State
The test writes shared KMS config, starts KMS instance 1 and KMS instance 2, obtains an authenticated token as `foo` through the first URL, reuses the same token as `bar` against the second URL, and verifies an empty token as `bar` receives HTTP 403. KMS and ZooKeeper are stopped in `finally`.

## Dependencies and Integration Points
It integrates `MiniKMS`, `KMSAuthenticationFilter`, Hadoop authentication `ZKSignerSecretProvider`, Curator `TestingServer`, `DelegationTokenAuthenticatedURL`, and KMS REST key-name resource paths.

## Risks and Edge Cases
The test relies on shared ZooKeeper state and HTTP authentication cookies/tokens. It intentionally demonstrates that signer-secret sharing is authentication-level state, independent of the current UGI used for the second request.

## Test Signals
This is a targeted HA signal for ZooKeeper signer configuration, complementing the more extensive ZooKeeper delegation token tests in `TestKMS.java`.
