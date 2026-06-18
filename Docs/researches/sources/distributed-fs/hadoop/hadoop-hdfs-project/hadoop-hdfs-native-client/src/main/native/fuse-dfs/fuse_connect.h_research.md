# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_connect.h

## Purpose
Public interface for the `fuse_dfs` libhdfs connection cache.

## Important APIs, Types, And Functions
Forward-declares `struct hdfsConn`, `struct hdfs_internal`, and exposes `fuseConnectInit`, `fuseConnectAsThreadUid`, `fuseConnectTest`, `hdfsConnGetFs`, and `hdfsConnRelease`.

## Control Flow
Callers initialize once during mount setup, borrow a connection for each operation, use the returned hdfsFS, and release the handle when finished.

## State, Persistence, And Dependencies
The header hides connection-cache state behind opaque types. It depends on caller discipline: every successful borrow requires `hdfsConnRelease`.

## Integration Points
Included by FUSE operation implementations, `fuse_init.c`, and `fuse_dfs.c`.

## Risks
The API does not express ownership in types, so missed releases leak refs and prevent expiry. `hdfsConnGetFs` returns an internal libhdfs pointer tied to the borrowed connection lifetime.

## Test Signals
Static and runtime validation should check that all operation paths release successful connections on cleanup.
