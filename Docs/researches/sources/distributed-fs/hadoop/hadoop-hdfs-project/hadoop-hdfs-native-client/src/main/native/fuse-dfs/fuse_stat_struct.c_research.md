# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_stat_struct.c

## Purpose
Translates libhdfs `hdfsFileInfo` metadata into POSIX `struct stat`.

## Important APIs, Types, And Functions
`fill_stat_structure(hdfsFileInfo *info, struct stat *st)` uses `getpwnam`, `getgrnam`, global mutexes from `fuse_users.c`, `default_id=99`, and `blksize=512`.

## Control Flow
Zero stat, derive link count, map HDFS owner/group names to local UID/GID with fallback, derive file type and permissions, set size/block fields, and copy access/modification times.

## State, Persistence, And Dependencies
No persistent changes. Depends on local passwd/group databases, global lookup mutex ordering, HDFS metadata, and math `ceil`.

## Integration Points
Used by `getattr` and `readdir` to present HDFS metadata to POSIX consumers.

## Risks
Owner/group names may not exist locally and fall back to nobody id. `ceil(st_size/st_blksize)` uses integer division before conversion, undercounting partial blocks. Directory mode defaults to permissive 0777 when HDFS permissions are absent.

## Test Signals
Stat tests should validate file type, size, permission bits, owner/group fallback, and timestamps.
