# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMetadataSyncV2BenchmarkTest.java

## Purpose
This ignored benchmark/debug test compares metadata sync V2 against legacy V1 loading on a large local UFS tree. It is not intended as a normal unit test; it requires pre-generated files under a hard-coded `/tmp/s3-test-files/bucket` layout.

## Important APIs, Types, and Functions
- Class-level `@Ignore` disables the benchmark by default.
- `syncV2()` mounts `file:///tmp/s3-test-files/bucket/0/0/0/0` at `/local_mount`, runs `getMetadataSyncer().syncPath` with `DescendantType.ALL` and `DirectoryLoadType.BFS`, waits indefinitely, and prints task stats twice.
- `syncV1()` mounts the same path, calls `listStatus` with recursive `LoadMetadataPType.ALWAYS`, and prints elapsed time.
- `generateTestFiles()` is separately ignored and writes a large nested tree of small files for benchmark input.
- `listSync()` builds the V1 recursive list context with `syncIntervalMs(0)`.

## Control Flow
The benchmark extends `FileSystemMasterTestBase`, mounts the configured local UFS path, and then either invokes V2 sync directly or V1 metadata loading through list status. The file generator uses nested loops to create paths like `/tmp/s3-test-files/bucket/i/j/k/l/n/fm` and logs every 10,000 files.

## State and Persistence Behavior
This test creates and reads real local filesystem data outside the repository under `/tmp`. It does not assert replay behavior and prints performance data rather than checking exact state, though it uses the normal master fixture and journal-backed setup from the base class.

## Dependencies and Integration Points
It depends on the local filesystem, Apache Commons `FileUtils`, `DefaultFileSystemMaster` metadata sync V2, legacy `listStatus` metadata loading, `MountContext`, and file master contexts. The benchmark assumes the Alluxio local UFS adapter can access the hard-coded path.

## Risks
- Hard-coded `/tmp` paths and huge file counts make accidental execution expensive.
- The test uses `System.out` timing/stats instead of assertions.
- `syncV2` hardcodes `DirectoryLoadType.BFS`, so it does not compare all V2 modes.
- Generated data volume is large enough to affect disk usage and local performance.

## Test Signals
Because the class is ignored, signals are manual: printed `TaskStats` from V2 first/second pass and elapsed milliseconds from V1 recursive list status. It is best treated as a local profiling tool, not a CI regression test.
