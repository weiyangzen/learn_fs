# sources/distributed-fs/beegfs-go/watch/internal/metadata/manager.go

## Purpose

This file implements BeeWatch metadata ingestion. It creates the Unix packet socket consumed by BeeGFS metadata services, negotiates v2 protocol state when needed, deserializes file events, assigns metadata identity fields, and pushes events into a shared multi-cursor ring buffer.

## Important APIs, Types, And Functions

`Manager` holds the `EventBuffer`, context, socket path/listener, last sequence ID, and selected event protocol version. `Config` defines event log target, buffer size, GC frequency, and event version. `newEventVersion` parses `major.minor` strings. `New` validates one metadata service, creates/removes socket paths, opens `net.Listen("unixpacket", ...)`, and returns a cleanup function. `Manage` accepts connections and dispatches `handleV1Connection` or `handleV2Connection`. `Sample` logs incoming event rate.

## Control Flow

`Manage` repeatedly starts an accept goroutine and waits for either shutdown or a connection. For each connection, it runs a reader goroutine and waits for app shutdown or connection failure. V2 handling sends a handshake, receives metadata ID/mirror ID, requests the message range, chooses a stream start sequence based on `lastSeqID` and available oldest event, sends `RequestMessageStreamStart`, and then receives `SendMessage` packets indefinitely. V1 handling simply reads packets and increments a local sequence counter.

## State And Persistence

Event state is in memory. `lastSeqID` prevents duplicate v2 pushes across reconnects and controls the v2 PMQ stream start point. The event buffer may drop old unacknowledged events on overflow and returns a dropped sequence ID for warning. The socket file is removed/recreated on startup and closed by the cleanup function.

## Dependencies And Integration Points

It integrates with `types.MultiCursorRingBuffer`, `serde.go`, `deserialize.go`, `fileEventConnHandler`, zap logging, and BeeGFS metadata service Unix packet protocol. `cmd/beegfs-watch/main.go` starts it only after subscribers are configured.

## Risks And Test Signals

`newEventVersion` uses `if major != 1 && major != 2 && minor != 0`, which accepts some unsupported major/minor combinations that may have been intended for rejection. `Manage` starts a new accept goroutine each loop and relies on socket close/context to retire blocked accepts. Event state is not durable, so process restart relies on metadata PMQ range plus subscriber acknowledgements. There are no direct manager tests; integration tests should cover v2 handshake, reconnect from `lastSeqID`, buffer overflow warnings, shutdown while blocked in read, and invalid event-version parsing.
