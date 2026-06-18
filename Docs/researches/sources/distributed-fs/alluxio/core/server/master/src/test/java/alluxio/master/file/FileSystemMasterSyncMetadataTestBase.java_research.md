# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataTestBase.java

## Purpose
This base fixture supports metadata sync tests that need a real `DefaultFileSystemMaster` and a controllable local UFS. It centralizes temporary UFS setup, static UFS factory mocking, metric reset, master startup, UFS helpers, and a `FlakyLocalUnderFileSystem` implementation for failure injection.

## Important APIs, Types, and Functions
- `before()` reloads configuration, creates local UFS and journal directories, installs `UnderFileSystem.Factory.createWithRecorder` mocking, builds `MetricsMaster`, `BlockMaster`, and `DefaultFileSystemMaster`, starts the journal, gains primacy, starts the registry, and resets metrics.
- `after()` stops the registry and shuts down metadata sync executor services.
- `createUfsDir`, `createUfsFile`, and `cleanupUfs` provide direct UFS mutation helpers.
- `createUfsStatusWithName()` builds a synthetic `UfsFileStatus` for cache metric tests.
- `FlakyLocalUnderFileSystem` extends `LocalUnderFileSystem` and can throw `IOException`, throw `RuntimeException`, sleep, or fail selected path substrings from `getStatus` and `listStatus`.
- `createUfsHierarchy()` recursively creates mixed directory/file trees.

## Control Flow
Subclasses call `super.before()` to get a complete master environment. The base configures the root mount to point at the temporary UFS and enables `MASTER_METADATA_SYNC_INSTRUMENT_EXECUTOR`. It creates two executor services: one for the file system master and one for UFS status cache tests. UFS operations go through the same local UFS object that production code receives from the mocked factory.

## State and Persistence Behavior
The fixture uses a UFS-backed journal and starts the journal in primary mode. It does not test replay itself, but it gives each test a fresh temporary root, inode tree, master registry, and reset metric namespace. The flaky UFS mutable flags are shared state that tests must reset when changing failure modes.

## Dependencies and Integration Points
It integrates Alluxio configuration, journal test utilities, master registry, metrics master, block master, file system master, local UFS, PowerMockito static mocking, and path utilities. Subclasses rely on protected fields such as `mFileSystemMaster`, `mInodeTree`, `mUfs`, and executor services.

## Risks
- Static mocking of `UnderFileSystem.Factory` can affect other tests if setup/teardown fails.
- `FlakyLocalUnderFileSystem` throws generic `RuntimeException` for path failures, which is useful for broad failure paths but not fine-grained exception semantics.
- Slow UFS injection uses real sleep, which can make tests sensitive to timing and timeouts.
- `after()` shuts down executor services but does not await termination.

## Test Signals
This file is a fixture, so signals appear in subclasses: successful registry startup, inode-tree population, metrics reset, controlled UFS failures, and deterministic temporary UFS hierarchy construction.
