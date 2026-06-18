# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/posix_util.h

## Purpose
Header for POSIX test utilities.

## Important APIs, Types, And Functions
Declares `recursiveDeleteContents`, `recursiveDelete`, `createTempDir`, and `sleepNoSig`.

## Control Flow
No executable flow; exposes cleanup/temp/sleep helpers.

## State, Persistence, And Dependencies
State changes are local filesystem mutations and sleep timing in the implementation.

## Integration Points
Included by FUSE workload and test runner.

## Risks
Callers must not pass paths that should be preserved; recursive delete is destructive.

## Test Signals
Compile inclusion and successful temp/cleanup operations validate this API.
