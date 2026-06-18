# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/posix_util.c

## Purpose
Small POSIX utility library for native FUSE tests.

## Important APIs, Types, And Functions
Implements `recursiveDeleteContents`, `recursiveDelete`, `createTempDir`, and `sleepNoSig`. Uses static mutex `gTempdirLock` and nonce for temp names.

## Control Flow
Recursive deletion stats paths, descends into directories, skips dot entries, unlinks files, and removes directories. Temp dir creation chooses `$TMPDIR` or `/tmp`, canonicalizes relative TMPDIR, combines pid and nonce, and calls mkdir. Sleep loops on `EINTR`.

## State, Persistence, And Dependencies
Mutates local filesystem and sleeps. The nonce is process-global and protected by a mutex. Depends on POSIX dir/stat/unlink/rmdir/realpath/nanosleep APIs.

## Integration Points
Used by native FUSE workload and test runner for temp mount dirs and cleanup.

## Risks
Deletion follows `stat`, not `lstat`, so symlink behavior may be unsafe if symlinks appear. Temp names are predictable and `mkdir` failure is returned rather than retried. Some error sign conventions are inconsistent (`rmdir` returns positive errno in one path).

## Test Signals
Local workload verification and cleanup success exercise these utilities.
