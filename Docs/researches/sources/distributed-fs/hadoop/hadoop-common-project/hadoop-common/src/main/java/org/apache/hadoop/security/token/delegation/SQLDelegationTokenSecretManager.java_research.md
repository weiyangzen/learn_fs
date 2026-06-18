<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/SQLDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/SQLDelegationTokenSecretManager.java

Source read size: 483 lines, 19271 bytes.

## Purpose
SQL-backed delegation token secret manager for HA services that share tokens, keys, and sequence counters through an external relational database.

## Important APIs, Types, and Functions
Extends `AbstractDelegationTokenSecretManager`. It overrides token, key, and counter accessors and declares abstract SQL operations: `selectTokenInfo()`, `selectStaleTokenInfos()`, `insertToken()`, `updateToken()`, `deleteToken()`, `selectDelegationKey()`, `insertDelegationKey()`, `updateDelegationKey()`, `deleteDelegationKey()`, `selectSequenceNum()`, `updateSequenceNum()`, `incrementSequenceNum()`, `selectKeyId()`, `updateKeyId()`, and `incrementKeyId()`.

## Control Flow, State, and Persistence Behavior
Construction derives timing from delegation-token config and replaces `currentTokens` with `DelegationTokenLoadingCache`. Token store/update serializes `DelegationTokenInformation`, writes SQL first, then updates the local cache. Cancellation decodes and loads the token so the base manager can validate it. Cleanup asks SQL for stale rows by modification time, deserializes candidates, and double-checks renew date before deleting expired rows. Sequence numbers are locally batched from SQL; unused numbers in a batch are intentionally not reusable. Keys are cached locally but lazily fetched from SQL on miss.

## Dependencies and Integration Points
Requires concrete subclasses to implement database-specific SQL semantics and concurrency-safe counter increments. Integrates with `DelegationTokenManager` timing config, `DelegationKey`, `Token`, `Writable` serialization, and base manager metrics/hook flow.

## Risks and Test Signals
Risks include SQL transaction isolation around counter increments, duplicate insert handling, cache staleness, swallowed delete failures, and cleanup races with renewal by another router. Test concurrent managers allocating sequence/key ids, token store/update/cancel round trips, cache miss loading, stale cleanup with renewed token preservation, missing token `NoSuchElementException`, key lazy load, SQL exception conversion, and batch-boundary sequence allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/SQLDelegationTokenSecretManager.java -->
