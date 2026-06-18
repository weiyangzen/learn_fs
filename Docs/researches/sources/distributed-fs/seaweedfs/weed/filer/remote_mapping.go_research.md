# sources/distributed-fs/seaweedfs/weed/filer/remote_mapping.go

## Purpose

`remote_mapping.go` reads, inserts, and deletes remote-storage mount mappings stored inside the filer. It was read as a complete 125-line file.

## Important APIs, Types, and Functions

`ReadMountMappings`, `InsertMountMapping`, `DeleteMountMapping`, `addRemoteStorageMapping`, and `removeRemoteStorageMapping` operate on `/etc/remote/mount.mapping` protobuf content.

## Control Flow

Read opens a filer client, reads the mapping file, treats not-found as empty content, and unmarshals mappings. Insert/delete read current content through `WithFilerClient`, modify the protobuf map, marshal, and save it back with `SaveInsideFiler`.

## State and Persistence Behavior

Mappings persist as a serialized `remote_pb.RemoteStorageMapping` file inside the filer metadata namespace. Updates are read-modify-write and not locally transactional.

## Dependencies and Integration Points

Depends on filer gRPC clients, `ReadInsideFiler`, `SaveInsideFiler`, `DirectoryEtcRemote`, `remote_pb`, and protobuf serialization.

## Risks and Edge Cases

Concurrent insert/delete operations can overwrite each other. `addRemoteStorageMapping` ignores unmarshal errors and starts from an empty map, which can discard corrupt existing content. Delete returns unmarshal errors.

## Test Signals

Remote storage tests in this subset cover lookup behavior, not mapping read-modify-write. Needed tests should cover not-found, corrupt protobuf, concurrent update, and save failure.
