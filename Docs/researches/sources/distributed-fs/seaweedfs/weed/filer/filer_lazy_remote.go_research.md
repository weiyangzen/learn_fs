<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote.go

## Purpose
Implements lazy remote object lookup and remote deletion for filer paths mapped to remote storage mounts.

## Important APIs and Types
`lazyFetchContextKey` prevents recursion. `maybeLazyFetchFromRemote` stats a remote object on local store miss and persists a local `Entry`. `maybeDeleteFromRemote` deletes remote files or directories for local-origin metadata deletes.

## Control Flow and State
Lazy fetch first checks recursion guard, remote storage availability, mount mapping, and client resolution. It maps filer path to remote location, uses singleflight keyed by path, calls `StatFile`, builds an entry with remote metadata, and persists it with a timeout context marked to skip recursive lazy fetch. Store write failure still returns the in-memory entry and forgets the singleflight key for retry. Remote delete skips nil/non-mounted entries, resolves the named client, maps path, and calls `RemoveDirectory` or `DeleteFile`.

## Persistence Behavior
Lazy fetch writes metadata into the filer store via `CreateEntry`; it does not copy file content locally. Delete removes remote object before local metadata deletion through callers in `filer_delete_entry.go`.

## Dependencies and Integration Points
Uses `FilerRemoteStorage`, remote storage clients, `remote_pb.RemoteStorageLocation`, `singleflight`, `CreateEntry`, and delete paths. `FindEntry` invokes lazy fetch when the store misses.

## Risks
Availability-over-consistency behavior can return entries that were not persisted. Remote errors except client resolution are swallowed on fetch. Delete-before-metadata ordering can remove remote data even if local metadata deletion later fails. Context is decoupled for persistence with a fixed 30 second timeout.

## Test Signals
`filer_lazy_remote_test.go` covers fetch hits, not-under-mount, not found, persist failure, longest prefix, recursion guard, `FindEntry` integration, and many delete paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote.go -->
