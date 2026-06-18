# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSACLs.java

## Purpose
`TestKMSACLs.java` unit-tests `KMSACLs`, especially default access behavior, configured global ACLs, key ACL parsing, duplicate handling, and hot reload semantics.

## Important APIs, Types, and Functions
- `testDefaults()` verifies that an empty `Configuration(false)` allows every `KMSACLs.Type`.
- `testCustom()` sets each ACL config key to its type name and confirms only the matching user is authorized.
- `testKeyAclConfigurationLoad()` validates key ACL, default key ACL, and whitelist key ACL parsing, including rejection of invalid operations and disallowing `ALL` for default/whitelist key ACL prefixes.
- `testKeyAclDuplicateEntries()` verifies last-write-wins behavior in `Configuration`, wildcard handling, and empty ACL replacement.
- `testKeyAclReload()` calls `setKeyACLs()` repeatedly to ensure hot reload updates, idempotence, wildcard conversion, and clearing old maps when a new configuration omits previous entries.
- Helper methods inspect `KMSACLs.keyAcls`, `defaultKeyAcls`, and `whitelistKeyAcls` maps and compare `AccessControlList` users.

## Control Flow and State
Each test builds an isolated `Configuration`, constructs a `KMSACLs`, and inspects either `hasAccess()` results or the internal ACL maps. Reload tests mutate the same `Configuration`, call `setKeyACLs()`, and assert that old entries are either retained only when still configured or removed on a fresh config.

## Dependencies and Integration Points
The test uses `KMSConfiguration` ACL prefixes, `KeyAuthorizationKeyProvider.KEY_ACL`, `KeyOpType`, Hadoop `AccessControlList`, and `UserGroupInformation`. It validates the config contract consumed by KMS server authorization and `KeyAuthorizationKeyProvider`.

## Risks and Edge Cases
Important security edge cases include invalid operation names, duplicate configuration keys, empty values, wildcard `*`, `ALL` scope restrictions, and reload clearing. Because it directly inspects package-visible maps, changes to `KMSACLs` internals may require test updates even if behavior remains intact.

## Test Signals
The file gives focused unit coverage for ACL parsing and reload behavior, complementing the broader end-to-end authorization tests in `TestKMS.java`.
