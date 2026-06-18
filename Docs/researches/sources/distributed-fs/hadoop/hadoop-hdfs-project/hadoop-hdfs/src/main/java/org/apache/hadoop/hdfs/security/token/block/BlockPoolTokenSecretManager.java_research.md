# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockPoolTokenSecretManager.java

## Purpose
`BlockPoolTokenSecretManager` multiplexes one `BlockTokenSecretManager` per HDFS block pool. It lets common token code route generation, verification, key import, and data encryption key operations by block pool ID.

## Important APIs and types
The class extends `SecretManager<BlockTokenIdentifier>`. It exposes `addBlockPool`, `get`, `isBlockPoolRegistered`, `createIdentifier`, `createPassword`, `retrievePassword`, multiple `checkAccess` overloads, `addKeys`, `generateToken`, `generateDataEncryptionKey`, and `retrieveDataEncryptionKey`.

## Control flow
Each public operation derives the block pool ID either from the token identifier, the `ExtendedBlock`, or an explicit argument, then dispatches to the registered `BlockTokenSecretManager`. Missing block pools fail fast with `IllegalArgumentException`. The map is a `ConcurrentHashMap`, so reads and registrations can occur concurrently.

## State and persistence
The only local state is the in-memory block-pool-to-secret-manager map. Key material, token passwords, and encryption keys are held in the per-pool managers and are not persisted here.

## Dependencies and integration points
It integrates with the NameNode/DataNode block token subsystem, `ExtendedBlock`, `BlockTokenIdentifier`, `Token`, storage-type and storage-ID constraints, and data transfer encryption. Federated or multi-block-pool deployments rely on this router to keep token keys isolated by pool.

## Risks and edge cases
Operations against unregistered pools throw unchecked exceptions, so callers must ensure registration before serving traffic. There is no removal path, which is acceptable for stable block pools but matters for tests or long-lived dynamic setups. Cross-pool misuse is guarded by routing through the block's pool ID and downstream identifier checks.

## Test signals
Tests should verify routing for every overload, missing-pool errors, concurrent registration/read behavior, clear-all test helper behavior, and that token/password/encryption-key operations never leak to the wrong block pool.
