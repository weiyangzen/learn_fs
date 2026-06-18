# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EncryptionFaultInjector.java

## Purpose
`EncryptionFaultInjector` is a visible-for-testing singleton that provides no-op hooks for injecting failures around encrypted file creation and re-encryption processing.

## Important APIs and Types
The class exposes static `instance` and `getInstance`. Hook methods include `startFileNoKey`, `startFileBeforeGenerateKey`, `startFileAfterGenerateKey`, `reencryptEncryptedKeys`, `reencryptUpdaterProcessOneTask`, `reencryptUpdaterProcessCheckpoint`, and `ensureKeyIsInitialized`.

## Control Flow
Production behavior is no-op. Tests replace or mutate the singleton with a subclass that throws `IOException` at specific encryption lifecycle points.

## State and Persistence
Only the static singleton is stateful. It is not persisted.

## Dependencies and Integration
Used by encryption-zone, encrypted file creation, and re-encryption code paths to exercise failure handling.

## Risks and Test Signals
Like other global test injectors, it can leak state across tests if not reset. The methods are instance methods but `instance` is public, so tests can replace it directly. Test suites should verify reset behavior and each hook's effect on edit-log rollback, key generation, and re-encryption updater recovery.
