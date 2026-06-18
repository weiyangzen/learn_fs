# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getstubcontents.go

## Purpose
Fetches the remote target ID and URL/path embedded in an offloaded stub file through BeeRemote.

## Important APIs, Types, And Functions
Exports `GetStubContents(ctx, path)`.

## Control Flow
Obtains a BeeRemote client and sends `GetStubContentsRequest{Path: path}`.

## State And Persistence
No local state; reads BeeRemote/service interpretation of a stub path.

## Dependencies And Integration Points
Used by `rst/status.go` when clients cannot directly read offloaded stubs. Depends on BeeRemote protobuf API.

## Risks And Edge Cases
No local path normalization; callers must supply the path form expected by BeeRemote. Errors are passed through and interpreted by callers.

## Test Signals
No direct tests.
