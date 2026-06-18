# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestScrLazyPersistFiles.java

## Purpose

`TestScrLazyPersistFiles` validates lazy-persisted RAM_DISK replicas when read through HDFS short-circuit read paths. It checks reads before and after eviction, interaction with open short-circuit handles, legacy reader fallback behavior, and checksum detection when block or metadata files are corrupted after lazy persistence.

## Important APIs and types

- The class extends `LazyPersistTestCase`, using its cluster builder, file creation, storage-type assertions, eviction trigger, and read verification helpers.
- `HdfsDataInputStream` read statistics expose total bytes and short-circuit bytes.
- `StorageType.RAM_DISK` and `StorageType.DEFAULT` represent pre- and post-eviction locations.
- `BlockMetadataHeader.getHeaderSize()` distinguishes RAM_DISK metadata header-only files from lazy-persisted checksum metadata.
- `DomainSocket`, `NativeCodeLoader`, and `NativeIO.POSIX` gate the test environment.

## Control flow

`@BeforeAll` disables domain socket bind-path validation. `@BeforeEach` assumes native code, non-Windows, working domain sockets, and block size aligned to OS page size. The basic SCR test creates a lazy-persist file, waits for `RamDiskBlocksLazyPersisted`, opens it, reads a buffer by position, and asserts all bytes were short-circuit reads.

The eviction-with-open-handle test reads once from an open SCR handle, triggers eviction, reads again through the same stream, and expects both reads to count as short-circuit bytes. The after-eviction helper runs for modern and legacy readers: it verifies RAM_DISK read, confirms metadata length is header-only, triggers eviction, waits for DEFAULT storage, checks metadata now includes checksum data, and verifies random file contents.

Corruption tests run for modern and legacy SCR paths. After lazy persistence and eviction, they corrupt either the block file or metadata file through `MiniDFSCluster` helpers and assert `ChecksumException` when reading the file buffer.

## State and persistence behavior

The tests create real block and checksum files in a MiniDFSCluster configured with faked RAM_DISK backed by local disk. State transitions include lazy-persist metrics, replica storage-type migration from RAM_DISK to DEFAULT, metadata file growth, client context state for legacy SCR, and on-disk corruption.

## Dependencies and integration points

This file integrates HDFS lazy persistence, DataNode eviction, local block readers, domain sockets, native IO page alignment, checksum metadata, client read statistics, and cluster corruption helpers. It is Linux/native-code-specific by design.

## Risks and edge cases

- Environment assumptions skip broad platforms; failures may hide on Windows or without native code.
- The test uses faked RAM_DISK on physical disk, not true memory hardware.
- Metric waits and eviction timing can be sensitive to slow CI.
- Legacy SCR behavior is checked only for not disabling the client context after a successful after-eviction read.

## Test signals

Strong signals include short-circuit byte counters, storage-type assertions before and after eviction, metadata header-size checks, open-handle survival through eviction, legacy reader non-disablement, and `ChecksumException` for both block and metadata corruption.
