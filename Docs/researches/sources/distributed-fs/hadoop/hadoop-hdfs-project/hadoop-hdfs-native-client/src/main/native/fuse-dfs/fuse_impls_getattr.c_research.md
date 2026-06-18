# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_getattr.c

## Purpose
Implements stat/getattr by translating HDFS file metadata to POSIX `struct stat`.

## Important APIs, Types, And Functions
`dfs_getattr` calls `hdfsGetPathInfo`, `fill_stat_structure`, `hdfsListDirectory` for directory link counts, and `hdfsFreeFileInfo`.

## Control Flow
Borrow a connection, fetch path info, return `-ENOENT` if missing, fill stat metadata, list directories to set `st_nlink = entries + 2`, set regular files to one link, free HDFS info, release connection.

## State, Persistence, And Dependencies
No persistence. Depends on libhdfs metadata calls, `fuse_stat_struct.c`, and current HDFS namespace state.

## Integration Points
Registered as `.getattr` and used heavily by shell tools, readdir consumers, and test workload stat checks.

## Risks
Missing path is always `-ENOENT`; other I/O failures can be misreported. Directory `hdfsListDirectory` failure leaves `numEntries` at zero and may produce inaccurate link count. Time/owner translation risks live in `fill_stat_structure`.

## Test Signals
`stat`, `ls`, and workload checks for file type, size, and directory mtime validate this path.
