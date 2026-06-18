# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/MockDelegationTokenSecretManager.java

Purpose: simple running mock secret manager for router security tests.

Important APIs/types/functions: extends `AbstractDelegationTokenSecretManager<DelegationTokenIdentifier>`, uses `Configuration`, `IOException`, and HDFS `DelegationTokenIdentifier`. The constructor accepts a `Configuration` for reflective creation compatibility and configures delegation token timing values through the superclass constructor.

Control flow: the class provides the minimum implementation needed by `RouterSecurityManager`: construct successfully and return a new `DelegationTokenIdentifier` from `createIdentifier()`. It does not add custom storage, token validation, or lifecycle behavior beyond the superclass.

State and persistence behavior: superclass in-memory token/key state applies; there is no external persistence. Integration points are reflective secret-manager instantiation via router config and tests that need a functioning manager without ZooKeeper or SQL. Risks are that it may not represent production persistence or background lifecycle behavior, so it is useful for unit-level security manager tests only. Test signals are indirect: router security tests can create the manager and issue/verify tokens.
