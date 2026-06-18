# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/fuse_workload.c

## Purpose
Portable C workload that exercises common filesystem operations against a FUSE mount, also self-validated on a local filesystem.

## Important APIs, Types, And Functions
Main entry `runFuseWorkload`. Helpers include directory readers, `safeWrite`, `safeRead`, `closeWorkaroundHdfs2551`, optional `testOpenTrunc`, and `runFuseWorkloadImpl`. `struct fileCtx` tracks test files.

## Control Flow
The workload verifies root directory, creates/removes directories, checks readdir results, renames, calls statvfs and utime, creates several files, writes and reads back varied string sizes, truncates them to zero, unlinks them, optionally tests `open(O_TRUNC)`, then recursively deletes the base directory.

## State, Persistence, And Dependencies
Mutates the filesystem under `<root>/<pcomp>`. Uses local POSIX syscalls, FUSE headers for capability guards, test macros, and `sleepNoSig`. The close workaround polls stat to account for asynchronous FUSE release.

## Integration Points
Called by `test_fuse_dfs.c` against both local FS and mounted HDFS FUSE. It validates operation callbacks in combination rather than as isolated units.

## Risks
TODO comments call out missing coverage for access, mknod, symlink, non-dir rmdir, non-empty rmdir, unlink during write, weird open flags, chown, and chmod. Polling for close visibility can make failures slow.

## Test Signals
Any nonzero return pinpoints a POSIX operation mismatch. Directory membership, file contents, truncate sizes, and cleanup are the strongest signals.
