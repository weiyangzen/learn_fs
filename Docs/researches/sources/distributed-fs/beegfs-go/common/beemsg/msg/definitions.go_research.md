# sources/distributed-fs/beegfs-go/common/beemsg/msg/definitions.go

## Purpose
`definitions.go` contains small BeeMsg protocol message definitions for connection authentication, heartbeat, and generic debug commands.

## APIs and Control Flow
`AuthenticateChannel` has message ID `4007`, serializes/deserializes a uint64 auth secret, and must be sent before other TCP BeeMsg traffic. `HeartbeatRequest` has message ID `1019` and no payload. `GenericDebug` has message ID `1029` and serializes a command as a CStr aligned to one byte. `GenericDebugResp` has message ID `1030` and deserializes the response CStr with the same alignment.

## State, Dependencies, and Integration
These types depend on the BeeSerde package and implement the repository's message interface pattern through `MsgId`, `Serialize`, and/or `Deserialize`. They integrate with BeeMsg node-store and debug tooling.

## Risks and Test Signals
There is no validation on generic debug command size or content in this file. Authentication semantics depend on callers sending the message in the correct order. No direct tests are listed for these message definitions.
