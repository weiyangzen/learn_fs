# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_init.h

## Purpose
Declares mount lifecycle callbacks for the FUSE client.

## Important APIs, Types, And Functions
Forward-declares `struct fuse_conn_info` and declares `dfs_init` and `dfs_destroy`.

## Control Flow
No executable flow; FUSE invokes the declared callbacks through the operations table.

## State, Persistence, And Dependencies
Lifecycle state is implemented in `fuse_init.c`. This header only exposes the callback signatures.

## Integration Points
Included by `fuse_dfs.c` for callback registration and by initialization-related code.

## Risks
Signature must match the libfuse API version selected by `FUSE_USE_VERSION 26`.

## Test Signals
Compile/link success and mount/unmount callback invocation validate the declarations.
