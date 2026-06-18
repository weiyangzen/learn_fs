# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/UserProvider.java

## Purpose
`UserProvider` is a transient `KeyProvider` backed by the current user's Hadoop `Credentials`. It lets jobs carry key material in credentials, commonly after copying keys from a persistent provider for task execution.

## Important APIs and types
The provider scheme is `user`. It overrides `isTransient()`, key lookup, metadata lookup, create, delete, roll, `flush()`, `getKeys()`, and `getKeyVersions()`. Nested `Factory` creates the provider for `user://` URIs.

## Control flow
Construction captures `UserGroupInformation.getCurrentUser()` and that user's `Credentials`. Key versions are stored as secret keys under `Text(versionName)`, while metadata is stored under `Text(name)` as serialized `Metadata`. Create validates non-existence and material length, writes metadata and `name@0`. Roll updates metadata version count and adds a new version secret. Delete removes all version secrets and metadata. `flush()` adds the credentials back to the user.

## State and persistence
State is in-memory credentials associated with the current UGI plus a metadata cache. It is explicitly transient: keys are not a long-term persistent store. Synchronization is method-level to protect credentials/cache mutation.

## Dependencies and integration points
It depends on Hadoop `UserGroupInformation`, `Credentials`, and `Text`. It integrates with MapReduce and other job submission flows that distribute secrets through credentials rather than opening persistent providers in tasks.

## Risks
The provider exposes key material in process credentials. Metadata cache must remain coherent with credential updates; this implementation updates/removes cache on mutations. Because it is transient, using it accidentally for administration without explicit `-provider user:///` should be avoided; `KeyShell` warns and normally skips transient providers.

## Test signals
Tests should cover create/get/roll/delete in credentials, `flush()` adding credentials to UGI, transient status, factory scheme matching, synchronization under concurrent access, and correct filtering of base names versus `@` version aliases.
