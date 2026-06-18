# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsForLocalFS.java

## Purpose
`TestCryptoStreamsForLocalFS` adapts the shared `CryptoStreamsTestBase` contract to Hadoop's `LocalFileSystem`. It verifies crypto input/output streams over real local filesystem streams while documenting which base tests cannot run through the local checksum wrappers.

## Important APIs, Types, and Functions
The class extends `CryptoStreamsTestBase` and supplies `getOutputStream(int, byte[], byte[])` and `getInputStream(int, byte[], byte[])`. These create a `CryptoOutputStream` around `fileSys.create(file)` and a `CryptoInputStream` around `fileSys.open(file)`. The static `init()` method builds a minimal `Configuration`, binds `fs.file.impl` to `LocalFileSystem`, initializes `fileSys`, and resolves the shared `CryptoCodec`.

## Control Flow
Each test starts by deleting the temp root in `setUp()`, then delegates common key, IV, read, write, seek, and stream-behavior setup to the base class. The overridden stream factories route all data through one temp path. Cleanup makes the root writable, recursively deletes it, and asserts that the directory no longer exists.

## State and Persistence
State is persisted as an encrypted file under `GenericTestUtils.getTempPath("work-dir/testcryptostreamsforlocalfs")`. The static `fileSys` and base-class static `codec` are shared across tests, while each test removes on-disk state before and after execution.

## Dependencies and Integration Points
The test integrates `CryptoInputStream`, `CryptoOutputStream`, `CryptoCodec`, `FileSystem.getLocal`, `LocalFileSystem`, `FileUtil`, and JUnit 5 lifecycle annotations. It also inherits the broader crypto stream contract from `CryptoStreamsTestBase`.

## Risks and Edge Cases
Many inherited interface-specific tests are disabled because the wrapped local checksum streams do not support byte-buffer reads, byte-buffer positioned reads, `Syncable`, enhanced byte-buffer access, `seekToNewSource`, or `unbuffer`. These disabled methods are important compatibility signals: failures in subclasses may reflect missing wrapped-stream capabilities, not crypto logic.

## Test Signals
Passing enabled inherited tests signal correct encryption/decryption over `LocalFileSystem`, temp-file lifecycle cleanup, and ordinary stream semantics. Disabled tests preserve explicit expectations for unsupported local checksum stream features.
