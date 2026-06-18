# sources/distributed-fs/juicefs/pkg/meta/benchmarks_test.go

## Purpose

This file defines microbenchmarks for JuiceFS metadata operations and slice decoding. It measures common directory, file, xattr, link, and data paths across Redis, SQL/sqlite, and TKV/badger metadata engines. The benchmark suite is not correctness-comprehensive like `base_test.go`; instead it provides comparable performance signals for hot metadata APIs.

## Important APIs And Functions

`encodeSlices` and `encodeSlicesAsBuf` build fixed encoded slice records in two formats: a string slice consumed by `readSlices` and a contiguous byte buffer consumed by `readSliceBuf`. `BenchmarkReadSlices` and `BenchmarkReadSliceBuf` run small, mid, and large sizes to compare decoding costs.

`prepareParent` removes any previous benchmark directory and recreates it under root. The `bench*` helpers each isolate one operation: `benchMkdir`, `benchMvdir`, `benchRmdir`, `benchResolve`, `benchReaddir`, `benchMknod`, `benchCreate`, `benchRename`, `benchUnlink`, `benchLookup`, `benchGetAttr`, `benchSetAttr`, `benchAccess`, xattr operations, hardlink/symlink, `benchNewChunk`, `benchWrite`, and `benchRead`.

`benchmarkDir`, `benchmarkFile`, `benchmarkXattr`, `benchmarkLink`, and `benchmarkData` group those helpers into sub-benchmarks. `benchmarkAll` initializes a format with directory stats, creates a session, and runs all groups. `BenchmarkRedis`, `BenchmarkSQL`, and `BenchmarkTKV` instantiate the target engine URLs.

## Control Flow

Most benchmark helpers prepare a clean parent directory outside the timed section, create any prerequisite file or xattr while stopped or before `ResetTimer`, then loop `b.N` over the target metadata call. Delete-like benchmarks stop the timer while recreating an entry and measure only the remove operation. Rename benchmarks move one existing entry through incrementing names so each iteration remains valid. Read benchmarks prepopulate slices and repeatedly call `Read` into a reused slice variable.

`benchResolve` detects unsupported backend implementations with `ENOTSUP` and skips. `benchmarkData` registers no-op `DeleteSlice` and `CompactChunk` callbacks before exercising slice allocation/writes/reads so data-related background message hooks do not fail the benchmark.

## State And Persistence Behavior

Benchmarks create real metadata state in the target backend: directories, inodes, xattrs, hardlinks, symlinks, slices, and sessions. The Redis benchmark points at `redis://127.0.0.1/1`, while SQL and TKV use temporary sqlite/badger paths under `b.TempDir()`. Because `benchmarkAll` does not explicitly reset every backend at entry, benchmark directories are cleaned per helper through `prepareParent`, but backend-wide session or format state may persist during one benchmark invocation.

## Dependencies And Integration Points

The file depends on the `Meta` interface and common metadata constants (`RootInode` via literal `1`, `RmrDefaultThreads`, `ChunkSize`, `sliceBytes`), `utils.NewBuffer`, log setup through `utils.SetLogLevel`, and `logrus`. It integrates with `NewClient` and all registered backend URL schemes. The benchmark labels are stable sub-benchmark names useful for comparing engine changes.

## Risks And Test Signals

These benchmarks can be misleading if external Redis is unavailable, preloaded, or running with different persistence settings. Some helpers grow state proportional to `b.N`; long runs can create many entries/slices. The SQL and TKV benchmarks are more hermetic because they use temporary local stores. Performance regressions here point to hot metadata operations, but correctness must still be validated through the normal tests.
