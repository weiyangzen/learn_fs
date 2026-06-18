# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSACLs.java

## Purpose
`KMSACLs.java` owns KMS authorization policy. It loads global KMS operation ACLs, optional operation blacklists, per-key ACLs, default key ACLs, and whitelist key ACLs from `kms-acls.xml`, and can hot-reload them while the server is running.

## Important APIs, Types, and Functions
The `Type` enum defines global ACL categories: `CREATE`, `DELETE`, `ROLLOVER`, `GET`, `GET_KEYS`, `GET_METADATA`, `SET_KEY_MATERIAL`, `GENERATE_EEK`, and `DECRYPT_EEK`. `INVALIDATE_CACHE_TYPES` allows either `ROLLOVER` or `DELETE` privilege to invalidate cache. Public authorization methods are `hasAccess`, `assertAccess` for a single type or an `EnumSet`, `hasAccessToKey`, and `isACLPresent`. It implements both `Runnable` and `KeyAuthorizationKeyProvider.KeyACLs`.

## Control Flow
Construction loads ACL configuration, then `setKMSACLs` builds volatile maps of global ACLs and blacklists. `setKeyACLs` parses keys matching `key.acl.<name>.<op>`, plus `default.key.acl.<op>` and `whitelist.key.acl.<op>`. `startReloader` schedules `run` every second; `run` checks `KMSConfiguration.isACLsFileNewer(lastReload)` and replaces maps if the ACL file changed. Denial paths mark the unauthorized meter, audit the unauthorized action, and throw `AuthorizationException`.

## State and Persistence
Authorization state lives in volatile map references that are atomically swapped on reload. There is no persistence written by this class; the persisted authority is `kms-acls.xml`. The scheduled executor is lifecycle-managed by `KMSWebApp`.

## Dependencies and Integration Points
It uses Hadoop `AccessControlList`, `Configuration`, `UserGroupInformation`, KMS operation enums, and per-key operation types from `KeyAuthorizationKeyProvider`. It is called directly by `KMS` for global operations and by `KeyAuthorizationKeyProvider` for metadata-driven per-key authorization.

## Risks
Default global ACLs use wildcard `*` when no property is set, so deployment safety depends on `kms-acls.xml` being explicitly configured. Per-key access denies when no matching ACL/default/whitelist is present, but global KMS ACLs may be broad. The reload checks call `loadACLs()` twice in one update path, so a changing file could theoretically produce mixed global/key views. Invalid per-key ACL names or operations are logged and ignored.

## Test Signals
Tests should verify wildcard defaults, blacklist override, hot reload, malformed key ACL logging/ignore behavior, `ALL` handling, default and whitelist precedence, and unauthorized audit/meter side effects. Existing visible-for-testing methods expose maps and `forceNextReloadForTesting`.
