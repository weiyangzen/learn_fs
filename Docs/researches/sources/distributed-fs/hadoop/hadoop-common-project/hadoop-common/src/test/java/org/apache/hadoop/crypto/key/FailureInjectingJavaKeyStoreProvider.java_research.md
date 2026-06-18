# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/FailureInjectingJavaKeyStoreProvider.java

## Purpose
`FailureInjectingJavaKeyStoreProvider` is a test-only `JavaKeyStoreProvider` wrapper that injects write and backup failures during flush/recovery tests.

## Important APIs, Types, and Functions
It defines scheme `failjceks`, wraps an existing `JavaKeyStoreProvider` via the copy constructor, exposes `setBackupFail(boolean)` and `setWriteFail(boolean)`, overrides `writeToNew(Path)` and `backupToOld(Path)`, and provides a nested `Factory` extending `KeyProviderFactory`.

## Control Flow
The factory recognizes `failjceks` URIs, rewrites them to normal `jceks` URIs, creates a real `JavaKeyStoreProvider`, and wraps it. During flush, `writeToNew()` throws when `writeFail` is true and `backupToOld()` throws when `backupFail` is true; otherwise calls delegate to the superclass.

## State and Persistence
The wrapper controls two boolean failure flags and otherwise uses the underlying keystore provider state. It is designed to perturb persistence steps involving `_NEW`, `_OLD`, and current keystore files.

## Dependencies and Integration Points
It integrates `JavaKeyStoreProvider`, `KeyProviderFactory`, Hadoop `Path`, URI parsing, and tests such as `TestKeyProviderFactory` that validate rollback after failed flushes.

## Risks and Edge Cases
`setWriteFail(boolean)` currently assigns `backupFail = b` rather than `writeFail = b`, which looks like a bug in the test helper and can make intended write-failure injection behave as backup-failure injection. The misspelled backup failure message is harmless but can weaken exact-message assertions.

## Test Signals
When used correctly, this provider should force flush exceptions and allow tests to assert that unflushed keys are rolled back and keystore recovery remains consistent.
