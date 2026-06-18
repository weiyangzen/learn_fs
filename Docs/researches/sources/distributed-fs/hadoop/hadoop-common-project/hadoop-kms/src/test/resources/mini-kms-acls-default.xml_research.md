# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/resources/mini-kms-acls-default.xml

## Purpose
`mini-kms-acls-default.xml` is a test resource containing permissive default ACLs for MiniKMS test deployments.

## Important Configuration Entries
- Global KMS ACLs allow `*` for `CREATE`, `DELETE`, `ROLLOVER`, `GET`, `GET_KEYS`, `GET_METADATA`, `SET_KEY_MATERIAL`, `GENERATE_EEK`, and `DECRYPT_EEK`.
- Default per-key ACLs allow `*` for `MANAGEMENT`, `GENERATE_EEK`, `DECRYPT_EEK`, and `READ`.
- The file notes that it is hot-reloaded when changed.

## Control Flow and State
This XML is not executable. KMS loads it as `kms-acls.xml` style configuration and interprets property names via `KMSACLs` and `KeyAuthorizationKeyProvider`.

## Dependencies and Integration Points
It is consumed by MiniKMS/KMS test configuration. The property names must align with `KMSConfiguration`, `KMSACLs.Type`, and default key ACL prefixes.

## Risks and Edge Cases
Because all values are wildcard-permissive, this resource is appropriate for tests that need broad access but should not be mistaken for a secure production ACL sample. Hot reload semantics mean test failures can arise if property names drift.

## Test Signals
The file supports integration tests that require permissive defaults while focused tests override ACLs explicitly.
