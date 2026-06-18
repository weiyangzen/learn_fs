# sources/distributed-fs/seaweedfs/weed/filer/leveldb/object_size_metric_test.go

## Purpose

`object_size_metric_test.go` verifies that filer object-size metrics are recorded when new file entries are created with the LevelDB store. It guards the user-facing Prometheus histogram behavior rather than LevelDB internals.

## Important APIs, Types, and Functions

`histogramState` snapshots `stats.FilerObjectSizeBytesHistogram`. `TestCreateEntryRecordsObjectSize` uses `filer.CreateEntry` with files and a directory, then inspects histogram sample counts and buckets.

## Control Flow

The test initializes a temp LevelDB-backed filer, captures histogram state, creates a small file, a 5 MB file, a directory, and then overwrites the small file. It expects only the two new file creates to increment the histogram and checks that they landed in expected bucket ranges.

## State and Persistence Behavior

The histogram is global process state, so the test compares before/after counts rather than expecting an empty histogram. File metadata is persisted only in a temp LevelDB directory. Directory creation and overwrite update the store but should not count as new object-size samples.

## Dependencies and Integration Points

The file depends on Prometheus DTO metric encoding, SeaweedFS `stats`, the filer create path, and LevelDB as a concrete store. It validates metrics integration at the filer layer.

## Risks and Edge Cases

Global metric state can be affected by other tests running in the same process. Bucket assertions are cumulative, so they check lower bounds rather than exact placement. The test assumes the create path distinguishes new files from directories and overwrites.

## Test Signals

Signals are a sample-count delta of two, one <=1024-byte bucket increment for the small file, and one object in the 1 MB to 100 MB cumulative range for the 5 MB file.
