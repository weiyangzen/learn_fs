# sources/distributed-fs/seaweedfs/weed/filer/read_remote.go

## Purpose

`read_remote.go` contains helpers for entries backed only by remote storage and for mapping paths between local mount points and remote storage locations. It also exposes a client helper to cache a remote object into the local SeaweedFS cluster.

## Important APIs, Types, and Functions

`Entry.IsInRemoteOnly` detects entries with no local chunks and positive remote size. `MapFullPathToRemoteStorageLocation` maps a local full path under a mounted directory into a remote location. `MapRemoteStorageLocationPathToFullPath` performs the inverse mapping. `CacheRemoteObjectToLocalCluster` calls the filer RPC to cache remote data locally.

## Control Flow

Mapping helpers copy remote location name/bucket/path and append the relative path between the local mount root and target full path. The inverse strips the remote mount path prefix and appends the remainder to the local mount directory. The caching helper opens a filer client, sends `CacheRemoteObjectToLocalClusterRequest` with directory/name and concurrency settings, and returns the updated protobuf entry.

## State and Persistence Behavior

Mapping functions are pure. Caching state changes happen remotely through the filer RPC, which downloads remote object data into local chunks and updates the entry. Concurrency values of zero defer to server defaults.

## Dependencies and Integration Points

The file depends on filer protobuf clients, remote storage protobufs, and path utilities. It integrates with remote mount/cache features and callers that need to materialize remote-only entries before local reads.

## Risks and Edge Cases

The path mapping functions assume `fp` starts with `localMountedDir` and `remoteLocationPath` starts with `remoteMountedLocation.Path`; otherwise slicing can produce invalid paths or panic. `IsInRemoteOnly` treats zero-size remote objects as not remote-only because it requires `RemoteSize > 0`.

## Test Signals

Tests should cover normal/inverse mappings, trailing slash behavior, invalid prefix inputs, zero-size remote entries, cache RPC success/error paths, and explicit versus default concurrency settings.
