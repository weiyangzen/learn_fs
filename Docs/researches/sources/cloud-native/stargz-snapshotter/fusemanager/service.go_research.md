# sources/cloud-native/stargz-snapshotter/fusemanager/service.go

## Purpose
Implements the fuse manager gRPC server. It owns current snapshot filesystem configuration, handles lifecycle/status, delegates mount/check/unmount operations, and manages BoltDB handles for persisted fuse state.

## Important APIs, Types, And Functions
`Config` wraps service config plus IPFS, metadata store, and default image service settings. `ConfigContext`, `ConfigFunc`, and `RegisterConfigFunc` let other packages add service options during `Init`. `dbOpener` deduplicates Bolt handles. `Server` implements protobuf RPCs: `Status`, `Init`, `Mount`, `Check`, `Unmount`, `Close`, and internal `mount`.

## Control Flow
`NewFuseManager` creates the fusestore directory and opens Bolt. `Init` marks status wait-init, unmarshals config, stops any previous CRI server, runs registered config funcs, creates a new filesystem through `service.NewFileSystem`, restores persisted mounts, and marks ready. `Mount`, `Check`, and `Unmount` require ready status under read lock and delegate to the correct filesystem in `fsMap`. `Unmount` treats already-unmounted mountpoints as success if mountinfo confirms absence.

## State And Persistence
In-memory state includes status, root/config, current filesystem, mountpoint-to-filesystem map, CRI server, and shared Bolt opener. Persistent state is the main fusestore BoltDB plus any Bolt DBs opened via config funcs.

## Dependencies And Integration
Depends on generated protobufs, `service.NewFileSystem`, `snapshot.FileSystem`, bbolt, mountinfo, grpc, and containerd logging. It is hosted by `fusemanager.go` and called by `client.go`.

## Risks And Test Signals
Risks include global config func ordering, status set to ready even after deferred cleanup paths if not careful, ignored `storeFuseInfo`/`removeFuseInfo` errors, removing the fusestore on close, and mount restore semantics. `fusemanager_test.go` covers the RPC delegate path with a mock filesystem.
