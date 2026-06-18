# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_symlink.c

## Purpose
Declares symlink unsupported for the FUSE HDFS client.

## Important APIs, Types, And Functions
`dfs_symlink(const char *from, const char *to)` ignores arguments and returns `-ENOTSUP`.

## Control Flow
Trace and return unsupported.

## State, Persistence, And Dependencies
No state changes and no HDFS calls.

## Integration Points
Registered as `.symlink`.

## Risks
Applications expecting symlink support fail. This is safer than silent success, unlike `mknod`.

## Test Signals
Native workload TODO notes symlink tests are absent; a test should assert `ENOTSUP`.
