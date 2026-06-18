# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/expect.c

## Purpose
Implements read-statistics expectation helper for native libhdfs tests.

## Important APIs, Types, And Functions
`expectFileStats` calls `hdfsFileGetReadStatistics`, compares selected fields with `EXPECT_UINT64_EQ`, prints observed and expected counters, and frees stats with `hdfsFileFreeReadStatistics`.

## Control Flow
Fetch stats, log expected/actual counters, skip fields whose expected value is `UINT64_MAX`, compare specified fields, free stats, return zero or first expectation failure.

## State, Persistence, And Dependencies
Reads per-file libhdfs statistics and frees allocated stats object. No persistent state.

## Integration Points
Used by native libhdfs tests, especially zero-copy/direct-read tests, to verify read accounting.

## Risks
If an expectation fails before the final free, stats may leak because macros return immediately. The implementation signature uses `hdfsFile` while header forward-doc refers to internal struct, but typedef compatibility is expected.

## Test Signals
Counter mismatch errors include file/line and observed counters; success means read path accounting matched expectations.
