# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/cli/FormatTest.java

## Purpose
`FormatTest` verifies worker-format behavior for tiered storage directories, including directory cleanup, permissions, and replacement of files that conflict with worker data directory names.

## Important APIs, Types, and Functions
The tests are `formatWorker()` and `formatWorkerDeleteFileSameName()`. They exercise `Format.format(Format.Mode.WORKER, Configuration.global())`, `ConfigurationRule`, worker tier directory keys, `WORKER_DATA_FOLDER_PERMISSIONS`, `CommonUtils.getWorkerDataDirectory()`, `FileUtils`, `PathUtils`, and POSIX permissions APIs.

## Control Flow, State, and Persistence
Each test creates temporary tier directories and configures three storage levels. `formatWorker()` pre-creates subdirectories/files under worker data folders, runs format, and asserts the parent tiers and worker data folders exist, permissions match, and data folders are empty. `formatWorkerDeleteFileSameName()` pre-creates files where worker data directories should be, runs format, and verifies they become empty directories with configured permissions.

## Dependencies and Integration Points
It depends on JUnit `TemporaryFolder`, Alluxio configuration test utilities, local filesystem permissions, and worker formatting code.

## Risks and Test Signals
Risks covered include stale worker data surviving format, wrong permissions, and file-vs-directory conflicts. Signals are local filesystem cleanup correctness; portability depends on POSIX permission support.
