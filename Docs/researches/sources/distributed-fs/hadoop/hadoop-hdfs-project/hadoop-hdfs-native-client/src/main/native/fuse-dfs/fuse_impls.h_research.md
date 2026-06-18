# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls.h

## Purpose
Central declaration header for all FUSE operation callback implementations.

## Important APIs, Types, And Functions
Declares `dfs_mkdir`, `dfs_rename`, `dfs_getattr`, `dfs_readdir`, `dfs_read`, `dfs_statfs`, `dfs_rmdir`, `dfs_unlink`, `dfs_utimens`, `dfs_chmod`, `dfs_chown`, `dfs_open`, `dfs_write`, `dfs_release`, `dfs_mknod`, `dfs_create`, `dfs_flush`, `dfs_access`, `dfs_truncate`, and `dfs_symlink`.

## Control Flow
No executable flow; `fuse_dfs.c` uses these declarations to populate the FUSE operations table.

## State, Persistence, And Dependencies
Includes FUSE and mount context types. State lives in individual implementation files.

## Integration Points
This header is the contract between callback registration and operation implementations.

## Risks
Duplicate declarations for `dfs_mkdir` and `dfs_rename` are harmless but noisy. Signature mismatches with libfuse version would break callback registration.

## Test Signals
Compile success and callback dispatch through `fuse_main` validate this contract.
