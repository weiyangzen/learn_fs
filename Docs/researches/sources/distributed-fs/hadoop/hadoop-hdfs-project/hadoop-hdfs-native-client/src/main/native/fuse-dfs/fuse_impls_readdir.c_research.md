# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_readdir.c

## Purpose
Implements directory listing for FUSE.

## Important APIs, Types, And Functions
`dfs_readdir` calls `hdfsListDirectory`, `fill_stat_structure`, extracts basename with `strrchr`, and calls the FUSE `filler` callback for entries plus `.` and `..`.

## Control Flow
Borrow connection, list HDFS directory, map null result to errno or `ENOENT`, iterate entries, fill stat metadata and basename into FUSE buffer, then append synthetic dot entries with generic directory stats.

## State, Persistence, And Dependencies
No persistence. Depends on HDFS directory listing shape, where `mName` is a full path string.

## Integration Points
Registered as `.readdir` and exercised by `ls`, `find`, copy recursion, and native workload directory expectations.

## Risks
Filler errors are logged but do not stop iteration or change return code. Dot entries use placeholder ownership/timestamps. Offset and file-info parameters are ignored, so very large directories may not support incremental reads well.

## Test Signals
Workload checks directory membership before and after mkdir/rename; `find`/`ls` tests also validate this path.
