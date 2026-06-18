# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_stat_struct.h

## Purpose
Header for HDFS-to-POSIX stat conversion.

## Important APIs, Types, And Functions
Declares `fill_stat_structure`, `default_id`, and `blksize`.

## Control Flow
No executable flow; used by metadata callbacks.

## State, Persistence, And Dependencies
Exposes constants defined in `fuse_stat_struct.c`; depends on `hdfs/hdfs.h` and POSIX stat types.

## Integration Points
Included by `getattr` and `readdir`.

## Risks
The conversion helper assumes valid `hdfsFileInfo` lifetime. Constants are globally visible and not configurable.

## Test Signals
Compile-time inclusion plus stat/readdir behavior validate the header contract.
