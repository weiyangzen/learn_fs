# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockKey.java

## Purpose
`BlockKey` is the HDFS-specific key type used to generate and verify block access tokens and data encryption keys. It specializes Hadoop's generic `DelegationKey` without adding new fields.

## Important APIs and types
The class inherits key ID, expiry date, secret-key material, serialization, and equality behavior from `DelegationKey`. It provides constructors for empty keys, `SecretKey` inputs, and encoded byte-array keys.

## Control flow
There is no additional logic. Construction delegates directly to the superclass.

## State and persistence
State is the inherited key ID, expiry timestamp, and encoded secret. Persistence is inherited Writable serialization through `DelegationKey`, and is used by `ExportedBlockKeys`.

## Dependencies and integration points
It is produced and consumed by `BlockTokenSecretManager`, transported in `ExportedBlockKeys`, and used by DataNodes, NameNodes, balancer, and data-transfer encryption paths.

## Risks and edge cases
Because it is only a typed wrapper, all correctness depends on the superclass serialization and careful lifecycle management in `BlockTokenSecretManager`. Null or empty key material can be represented by the parent class and must be handled by callers.

## Test signals
Tests should cover constructor parity with `DelegationKey`, Writable round trips through `ExportedBlockKeys`, and compatibility when encoded key bytes are used instead of `SecretKey`.
