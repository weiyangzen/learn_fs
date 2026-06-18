# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/fuse_workload.h

## Purpose
Declares the reusable FUSE workload test entry point.

## Important APIs, Types, And Functions
`runFuseWorkload(const char *root, const char *pcomp)` performs operations under `<root>/<pcomp>`.

## Control Flow
No executable flow; implementation creates and cleans a test subtree.

## State, Persistence, And Dependencies
Callers must provide a root directory and unique path component not used concurrently. The workload mutates and then removes that subtree.

## Integration Points
Included by `test_fuse_dfs.c` and linked into the native FUSE test executable.

## Risks
Concurrent callers sharing the same root/component would conflict. The API only returns negative error codes, not structured failure details.

## Test Signals
Return zero means the workload completed and cleanup succeeded.
