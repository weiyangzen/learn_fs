# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-acls.xml

## Purpose
`kms-acls.xml` is the default KMS ACL configuration file. Comments state it is hot-reloaded when it changes.

## Important Properties
Global KMS operation ACLs are all set to `*`: `hadoop.kms.acl.CREATE`, `DELETE`, `ROLLOVER`, `GET`, `GET_KEYS`, `GET_METADATA`, `SET_KEY_MATERIAL`, `GENERATE_EEK`, and `DECRYPT_EEK`. Default per-key ACLs are also `*` for `default.key.acl.MANAGEMENT`, `GENERATE_EEK`, `DECRYPT_EEK`, and `READ`.

## Control Flow
KMS authorization code loads this XML and checks user identities/groups against global operation ACLs and key-specific/default key ACLs. Hot reload means changes can alter authorization behavior in a running KMS process.

## State And Persistence
The file persists ACL policy. Runtime KMS maintains an in-memory parsed view and refreshes it when the file changes.

## Dependencies And Integration Points
It integrates with KMS REST/API authorization, key management operations, crypto extension operations, and ACL reload handling.

## Risks
The shipped defaults are fully permissive and must be tightened for secure deployments. Hot reload is useful but also means accidental edits can immediately broaden access. CREATE and ROLLOVER descriptions note that GET ACL membership controls whether key material is returned, so ACL combinations matter.

## Test Signals
KMS ACL tests should verify default allow behavior, operation-specific checks, key ACL fallback, and hot-reload behavior after file changes.
