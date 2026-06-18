# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KeyAuthorizationKeyProvider.java

## Purpose
`KeyAuthorizationKeyProvider.java` is a security wrapper around `KeyProviderCryptoExtension` that enforces per-key ACLs based on the current Hadoop user and metadata-stored ACL names.

## Important APIs, Types, and Functions
`KeyOpType` defines `ALL`, `READ`, `MANAGEMENT`, `GENERATE_EEK`, and `DECRYPT_EEK`. `KeyACLs` abstracts ACL lookup and authorization. Key methods override create, roll, delete, invalidate cache, warm-up, generate EEK, decrypt EEK, reencrypt EEK, batch reencrypt, read key versions/metadata/current key, and provider plumbing. `KEY_ACL_NAME` is the metadata attribute `key.acl.name`.

## Control Flow
Create operations take a write lock, derive or validate an ACL name, persist it into key metadata when absent and a matching key ACL exists, and require MANAGEMENT or ALL. Management mutations take the write lock and call `doAccessCheck`. EEK and read operations take the read lock. Decrypt and reencrypt first verify that the supplied encrypted key version belongs to its named key by reading the provider key version. Batch reencrypt validates every item, checks access for the first key name, and delegates.

## State and Persistence
The wrapper holds delegate provider and ACL references plus fair read/write locks. Persistent state is the `key.acl.name` metadata attribute written during key creation, which allows multiple keys to share an ACL name distinct from the key name.

## Dependencies and Integration Points
It integrates with `KMSACLs` through `KeyACLs`, `UserGroupInformation.getCurrentUser`, `KeyProviderCryptoExtension`, and KMS metadata. `KMSWebApp` installs this wrapper when `hadoop.kms.key.authorization.enable` is true.

## Risks
Authorization only occurs when metadata exists; `doAccessCheck` silently allows operations for missing metadata because it cannot resolve an ACL name. Batch reencrypt validates all items but checks `GENERATE_EEK` access only against the first key name; upstream `KMS.reencryptEncryptedKeys` enforces same key name before calling it. Create authorization mutates the caller's `Options` attributes. The source comment says some read operations are not checked, but the implementation does check them.

## Test Signals
Tests should cover create with implicit and explicit ACL names, default and whitelist ACL behavior through `KMSACLs`, missing metadata behavior, read/write lock concurrency, encrypted-key version/key mismatch rejection, batch same-key expectations, and disabled wrapper behavior in `KMSWebApp`.
