<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/fsinfo.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/fsinfo.cc

## Purpose
Implements display formatting for HDFS filesystem capacity statistics represented by `FsInfo`.

## Important APIs, Types, And Functions
The constructor zero-initializes capacity, used, remaining, under-replicated, corrupt, missing, missing-replication-one, and future-block counters. `str(fs_name)` prints a two-line table with filesystem, size, used, available, and use percentage.

## Control Flow
`str` computes column widths from labels and values, calculates `used * 100 / capacity`, and formats a header plus one data line.

## State And Persistence
State is per-object counters populated by namenode stats calls. No persistence exists.

## Dependencies And Integration Points
Used by C binding capacity/used APIs and any CLI-like display of `GetFsStats`.

## Risks
If `capacity` is zero, `str()` divides by zero. Formatting only covers a subset of stored counters, so callers needing under-replication or corruption data must read fields directly.

## Test Signals
Tests should cover nonzero stats formatting, large values, long filesystem names, and the zero-capacity edge case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/fsinfo.cc -->
