<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSecretManager.java

Source read size: 1141 lines, 36805 bytes.

## Purpose
Base secret manager for Hadoop delegation tokens. It creates token passwords from rolling master keys, tracks live token metadata, validates/renews/cancels tokens, expires old tokens, and exposes hook methods for HDFS/RM and external persistence implementations.

## Important APIs, Types, and Functions
The class extends `SecretManager<TokenIdent>` for `AbstractDelegationTokenIdentifier` subtypes. Key APIs are `startThreads()`, `stopThreads()`, `createPassword()`, `retrievePassword()`, `verifyToken()`, `renewToken()`, `cancelToken()`, `addKey()`, `addPersistedDelegationToken()`, `rollMasterKey()`, and persistence hooks such as `storeDelegationKey()`, `storeToken()`, `updateToken()`, and `removeStoredToken()`. Nested `DelegationTokenInformation` serializes renew date, password, and optional tracking id. Nested metrics track store/update/remove latency and failures.

## Control Flow, State, and Persistence Behavior
`startThreads()` creates an initial key, marks the manager running, and launches `ExpiredTokenRemover`. Token creation assigns issue/max dates, master key id, and a sequence number under a fair read/write API lock, then stores token metadata. Renewal decodes the token, checks max lifetime, renewer, master key, and password, then extends renew time up to max date. Cancellation authorizes owner or renewer, removes the token, updates owner stats, and calls persistence hooks. The remover thread periodically rolls master keys and scans candidates for expired tokens. Default persistence is in-memory, while subclasses override hooks for edit logs, SQL, or ZK.

## Dependencies and Integration Points
Depends on Hadoop `Token`, `SecretManager`, `AbstractDelegationTokenIdentifier`, `DelegationKey`, `WritableUtils`, `HadoopKerberosName`, metrics2, IOStatistics, and daemon/thread utilities. HDFS and YARN/RM plug persistence through protected hook methods; web, SQL, and ZK managers build on the same API.

## Risks and Test Signals
Risks include lock ordering around persistence hooks, fatal JVM exit if the remover thread throws unexpectedly, sequence/key counter correctness in subclasses, and owner-stat drift when external caches are refreshed. Test signals include key rolling, recovery with missing keys, password mismatch, renewer authorization, cancel authorization, expired-token removal, persistence hook failures, metrics failure increments, and top owner stats after add/remove/sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSecretManager.java -->
