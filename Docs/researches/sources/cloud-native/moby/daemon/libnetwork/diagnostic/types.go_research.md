<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/diagnostic/types.go -->
# sources/cloud-native/moby/daemon/libnetwork/diagnostic/types.go

## Purpose
Defines diagnostic response payloads and string renderers for libnetwork/networkdb HTTP diagnostics.

## Important APIs, Types, And Functions
`StringInterface` is the render contract. Constructors are `CommandSucceed`, `FailCommand`, and `WrongCommand`. Types include `HTTPResult`, `UsageCmd`, `StringCmd`, `ErrorCmd`, `TableObj`, `PeerEntryObj`, `TableEntryObj`, `TableEndpointsResult`, `TablePeersResult`, and `NetworkStatsResult`.

## Control Flow
Handlers create typed result objects, and `HTTPReply` in `server.go` renders either JSON or each object's `String` output. Table renderers print total counts plus entry lines.

## State And Persistence
No state; pure data structures.

## Dependencies And Integration Points
Used by diagnostic handlers and test clients that parse text phrases like `total entries` and `qlen`.

## Risks And Edge Cases
`NetworkStatsResult` has a typo in the JSON tag (`jsoin:"qlen"`), so JSON output will not use the intended `qlen` tag. `PeerEntryObj.Name` has an unusual tag `json:"-=name"`. The interface-typed `Details` can complicate JSON unmarshaling.

## Test Signals
Tests should cover plain text formatting, JSON tags, and compatibility with networkdb-test regex parsers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/diagnostic/types.go -->
