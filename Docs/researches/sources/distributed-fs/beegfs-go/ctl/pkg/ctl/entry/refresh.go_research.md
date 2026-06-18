# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/refresh.go

## Purpose
Refreshes metadata information for one or more BeeGFS entries by sending `RefreshEntryInfoRequest` to the owning metadata node. It is a path-processing wrapper around the metadata refresh RPC.

## Important APIs, Types, And Functions
Exports `RefreshEntryResult` and `RefreshEntriesInfo(ctx, paths)`. Internal helper `refreshEntryInfo` resolves an entry and owner with `GetEntryAndOwnerFromPath`, sends `msg.RefreshEntryInfoRequest`, and returns path, entry ID, and `beegfs.OpsErr` status.

## Control Flow
`RefreshEntriesInfo` gets a `NodeStore`, fetches entity mappings, tolerates `util.ErrMappingRSTs`, and delegates path iteration to `util.ProcessPaths`. For each path, `refreshEntryInfo` resolves entry ownership, sends the refresh request to `ownerNode.Uid`, converts transport errors into setup/processing errors, and returns server result status.

## State And Persistence
The function itself keeps no durable local state. The durable effect is on BeeGFS metadata, where the metadata node refreshes entry information. Results are streamed asynchronously and errors can terminate processing through `ProcessPaths`.

## Dependencies And Integration Points
Depends on `config.NodeStore`, `util.GetMappings`, entry lookup helpers in the same package, BeeMsg `RefreshEntryInfo*` messages, and path streaming/filtering infrastructure.

## Risks And Edge Cases
RST mapping errors are ignored, but other mapping failures abort setup. A non-success server status is returned both as a result and as an error, which may stop `ProcessPaths` after sending valid earlier results depending on pipeline timing. Returned empty `RefreshEntryResult{}` on lookup or transport error loses path context unless the error wraps it elsewhere.

## Test Signals
No direct tests. Mocked node-store tests should cover success, non-success `OpsErr`, owner lookup failure, and tolerance of unavailable RST mappings.
