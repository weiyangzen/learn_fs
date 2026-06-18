# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterTestBase.java

## Purpose
This shared fixture constructs a reusable in-process Alluxio master stack for file system master tests. It supplies common URIs, temporary UFS and journal roots, parameterized inode store factories, worker registration, block commit helpers, persisted-directory helpers, and service lifecycle management.

## Important APIs, Types, and Functions
- Static URI constants define common root, nested file, nested directory, and mount paths.
- `parameters()` provides heap, Rocks, and caching inode store factories for tests that use this base parameterization.
- `before()` configures the mock clock, resets group cache and metrics, creates the journal folder, and calls `startServices`.
- `startServices()` builds `MasterRegistry`, `JournalSystem`, `MetricsMaster`, `BlockMaster`, and a `DefaultFileSystemMaster` whose sync process is a `TestSyncProcessor`.
- `createFileWithSingleBlock()` creates a file, allocates a block, creates a UFS file for cache-through/through/async-through writes, commits a block to worker 1, and completes the file.
- Persisted-directory helpers build, load, mount, and verify deterministic local UFS directory trees.
- `stopServices()` stops registry, journal, and file master services.

## Control Flow
Tests using this base start with global configuration rules for UFS journaling, umask, work dir, root UFS, and retry-cache disabling. `startServices` registers two workers with memory and SSD tiers. Helper methods create local UFS trees through Java NIO, load metadata through `listStatus(... LoadMetadataPType.ALWAYS)`, and compare both UFS filesystem state and Alluxio inode IDs.

## State and Persistence Behavior
The fixture is explicitly journal-backed and supports simulated restarts by calling `stopServices` and `startServices` while retaining the same journal folder. It tracks `mInodeTree`, `mInodeStore`, `mBlockMaster`, worker IDs, metrics, and a mock clock. The file creation helper updates both inode metadata and block metadata, and may create persisted UFS files depending on write type.

## Dependencies and Integration Points
It integrates Alluxio configuration/test directory utilities, authentication rules, manual heartbeat rules, TTL interval rules, journal test utilities, heap/Rocks/caching inode stores, block metadata stores, metrics master, block master, file master, local filesystem paths, worker registration protobufs, and `TestSyncProcessor`.

## Risks
- Shared mutable fixture fields make test isolation dependent on correct `before`/`after` execution.
- `stopServices()` calls multiple stop/close methods and can mask lifecycle ordering assumptions in subclasses.
- The Rocks inode store parameter uses a shared directory per `parameters()` invocation, which may need care if tests are parallelized.
- The helper creates UFS files for certain write types but not file content, so tests should not infer data contents.

## Test Signals
The file itself is fixture code; downstream tests signal through successful master startup, registered worker IDs, deterministic block IDs/locations, replayable journal state, loaded persisted directories, and helper assertions for UFS/inode deletion.
