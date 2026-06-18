# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenSecretManager.java

## Purpose
`DelegationTokenSecretManager` is the HDFS-specific `AbstractDelegationTokenSecretManager` implementation for NameNode delegation tokens. It manages token passwords, persisted token/key state, edit-log updates, HA standby behavior, and credential creation.

## Important APIs and types
Public APIs include constructors, `createIdentifier`, `retrievePassword`, `retriableRetrievePassword`, `getTokenExpiryTime`, compatibility and protobuf fsimage load/save methods, persisted token/key update methods, `getNumberOfKeys`, and static `createCredentials`. `SecretManagerState` carries protobuf fsimage state, while nested `SerializerCompat` handles legacy Writable fsimage format.

## Control flow
Token password retrieval first asks `FSNamesystem` whether a READ operation is allowed. A standby exception is wrapped as `InvalidToken` in the legacy method but surfaced directly in `retriableRetrievePassword`; during transition to active, unknown-token errors become `RetriableException` so clients can retry while edit logs catch up. Loading state is allowed only when the secret manager is not running. Protobuf loading restores current key/token sequence fields, all keys, then persisted tokens. Saving creates a `SecretManagerSection` plus key and token protobuf lists. Persisted add/renew/cancel methods replay fsimage/edit-log records into `currentTokens`. Key and token expiry logging acquire the FSNamesystem read lock and synchronize on `noInterruptsLock` to avoid interruption during edit-log sync.

## State and persistence
Core mutable state is inherited: current master key ID, delegation token sequence number, `allKeys`, `currentTokens`, running flag, and tracking-ID option. This class persists that state to fsimage in protobuf and legacy formats and writes key/token expiry changes to the NameNode edit log through `FSNamesystem`.

## Dependencies and integration points
It integrates tightly with `FSNamesystem`, `NameNode`, startup progress reporting, fsimage protobufs, delegation token identifiers, `Credentials`, `SecurityUtil`, `UserGroupInformation`, edit logs, HA operation gating, and RPC token authentication.

## Risks and edge cases
State-loading methods intentionally refuse to run while active; bypassing that would corrupt live token maps. Persisted tokens whose master key is missing are skipped with a warning, which can invalidate client tokens after image/edit-log inconsistency. The legacy `retrievePassword` standby wrapping is a compatibility hack that depends on RPC unwrapping. Interrupt handling in edit-log logging is delicate because interrupted log sync can close edit files.

## Test signals
Tests should cover protobuf and legacy fsimage round trips, edit-log replay add/renew/cancel, missing master-key behavior, duplicate persisted token failure, standby and transition-to-active password retrieval, credential creation with token service, startup progress counters, and interruption behavior around master-key/token-expiry logging.
