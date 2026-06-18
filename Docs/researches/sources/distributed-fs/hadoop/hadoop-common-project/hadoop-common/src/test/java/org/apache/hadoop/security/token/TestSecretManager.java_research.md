<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestSecretManager.java

## Purpose
Tests static key-generator configuration behavior in `SecretManager`, especially default algorithm/length, configurable stronger settings, unknown algorithm handling, and immutability after manager initialization.

## Important APIs, Types, And Functions
The tests call `SecretManager.update`, `SecretManager.generateSecret`, and a minimal anonymous `SecretManager<TokenIdentifier>` implementation. Configuration keys come from `CommonConfigurationKeysPublic`.

## Control Flow
Setup creates a fresh concrete anonymous manager. `testDefaults` checks default generated key metadata. `testUpdate` changes the global algorithm and length before generation. `testUnknownAlgorithm` updates to an invalid algorithm and expects `IllegalArgumentException`. `testUpdateAfterInitialisation` verifies a manager that already generated a secret continues using its initialized settings even after global update.

## State And Persistence
The important state is static `SecretManager` configuration plus per-instance initialized key generator state. Teardown resets static configuration to defaults.

## Dependencies And Integration Points
Depends on Hadoop configuration keys and Java `SecretKey`. It validates security-token secret generation used by token managers.

## Risks
Static configuration can leak across tests if teardown is skipped. The anonymous manager stubs token password methods, so only key generation is covered, not token password retrieval semantics.

## Test Signals
Signals are expected key algorithm names, encoded key bit lengths, an exception for an unknown algorithm, and unchanged per-manager key settings after a later static update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestSecretManager.java -->
