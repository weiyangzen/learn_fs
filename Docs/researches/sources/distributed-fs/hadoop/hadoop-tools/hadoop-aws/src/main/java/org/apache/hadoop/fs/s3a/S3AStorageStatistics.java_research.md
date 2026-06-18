# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AStorageStatistics.java

## Purpose
`S3AStorageStatistics` adapts S3A `IOStatistics` into Hadoop `StorageStatistics` with the scheme/name expected by filesystem consumers.

## Important APIs, Types, and Functions
The class exposes constant `NAME = "S3AStorageStatistics"` and two constructors: one wrapping a provided `IOStatistics`, and one wrapping `emptyStatistics()`.

## Control Flow and State
Construction delegates to `StorageStatisticsFromIOStatistics` with name `S3AStorageStatistics` and scheme `s3a`. There is no additional logic.

## State and Persistence Behavior
State is whatever `IOStatistics` instance is supplied. The default constructor is an empty, non-updating statistics view.

## Dependencies and Integration Points
Dependencies are `IOStatistics`, `StorageStatisticsFromIOStatistics`, and `IOStatisticsBinding.emptyStatistics()`. `S3AFileSystem#getStorageStatistics()` can expose this adapter to Hadoop callers.

## Risks and Test Signals
Risks are low, but using the default constructor in live contexts would hide actual counters. Tests should verify the name/scheme, dynamic reflection of wrapped IOStatistics counters, and empty behavior for the no-arg constructor.
