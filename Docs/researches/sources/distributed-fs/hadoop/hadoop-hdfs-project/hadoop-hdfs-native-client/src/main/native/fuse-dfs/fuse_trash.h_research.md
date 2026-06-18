# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_trash.h

## Purpose
Public declaration for FUSE delete-with-trash support.

## Important APIs, Types, And Functions
Declares `hdfsDeleteWithTrash(hdfsFS userFS, const char *path, int useTrash)`.

## Control Flow
Callers pass a user-specific HDFS filesystem, path, and boolean trash flag; implementation either moves to trash or deletes.

## State, Persistence, And Dependencies
State changes occur in HDFS through the supplied `hdfsFS`. The header depends on libhdfs types.

## Integration Points
Included by unlink/rmdir implementations.

## Risks
The API returns integer error codes with mixed sign conventions internally; callers must treat nonzero as failure.

## Test Signals
Unlink/rmdir tests with trash enabled and disabled validate the contract.
