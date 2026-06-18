# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getrstconfig.go

## Purpose
Fetches BeeRemote remote storage target configuration.

## Important APIs, Types, And Functions
Exports `GetRSTCfg` with `ShowSecrets` and `GetRSTConfig(ctx)`.

## Control Flow
`GetRSTConfig` obtains a BeeRemote client and calls `GetRSTConfig` with an empty request.

## State And Persistence
No local state. It reads BeeRemote configuration.

## Dependencies And Integration Points
Depends on CTL BeeRemote client setup and BeeRemote protobuf API. `GetRSTCfg.ShowSecrets` is declared here but not used by the fetch function, likely consumed by CLI formatting elsewhere.

## Risks And Edge Cases
No local handling of redaction or `ShowSecrets`; consumers must enforce display policy.

## Test Signals
No direct tests.
