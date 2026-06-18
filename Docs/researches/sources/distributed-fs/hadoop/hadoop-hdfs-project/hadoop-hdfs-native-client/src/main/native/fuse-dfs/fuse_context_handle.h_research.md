# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_context_handle.h

## Purpose
Defines mount-level private context stored in FUSE and retrieved by operation callbacks.

## Important APIs, Types, And Functions
`dfs_context` contains `debug`, `usetrash`, `direct_io`, `protectedpaths`, and `rdbuffer_size`.

## Control Flow
`dfs_init` allocates and fills this structure, returns it to FUSE, and callbacks retrieve it through `fuse_get_context()->private_data`.

## State, Persistence, And Dependencies
The context persists for the lifetime of the mount and stores parsed options plus protected path array.

## Integration Points
Used by nearly every FUSE operation to read mount settings, protected path behavior, trash behavior, and read-buffer size.

## Risks
`dfs_destroy` currently does not free this context or `protectedpaths`, so unmount cleanup is incomplete. Callbacks use assertions rather than defensive errors if private data is missing.

## Test Signals
Mount initialization should populate the context, and operation callbacks should see consistent option values.
