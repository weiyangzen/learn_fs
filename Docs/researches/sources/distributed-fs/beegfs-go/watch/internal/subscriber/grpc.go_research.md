# sources/distributed-fs/beegfs-go/watch/internal/subscriber/grpc.go

## Purpose

This file implements the gRPC subscriber client used by BeeWatch handlers to connect to external subscriber services, send event streams, receive acknowledgement responses, and disconnect cleanly.

## Important APIs, Types, And Functions

`GRPCSubscriber` embeds `GrpcConfig` and holds `grpc.ClientConn`, generated `pb.SubscriberClient`, bidirectional stream, response channel, and mutex-protected receive-loop state. `newGRPCSubscriber` applies the default disconnect timeout. `Connect` reads optional TLS CA cert, creates a client connection through `beegrpc.NewClientConn`, and opens `ReceiveEvents`. `Send` sends one protobuf event. `Receive` starts at most one goroutine receiving `pb.Response` messages. `Disconnect` closes the send side, drains responses until stream close or timeout, and closes the gRPC connection.

## Control Flow

Handlers call `Connect`, then `Receive`, then repeatedly call `Send`. `Receive` returns an existing channel if already active, preventing duplicate stream receivers. On stream receive error or EOF, the receive goroutine exits and closes the channel. `Disconnect` is defensive against partially initialized connections by nil-checking stream and connection fields.

## State And Persistence

Connection state is in memory only. Persistent delivery progress is externalized through subscriber acknowledgements, not stored by this client. `recvStreamActive` controls goroutine lifecycle across reconnects.

## Dependencies And Integration Points

It depends on common `beegrpc` helpers for TLS/proxy options, generated `beewatch` subscriber client, grpc-go, and `common/types.MultiError`. It is the concrete implementation behind `subscriber.Interface` used by `subscribermgr.Handler`.

## Risks And Test Signals

`Connect` uses `context.TODO()` for the stream, relying on `Disconnect` rather than context cancellation. Send failures cause handler reconnect without retrying the individual event send. `Receive` drops receive errors instead of surfacing them except via closed channel. `Disconnect` can block up to `DisconnectTimeout` draining responses. Unit tests only cover construction defaults; integration tests should cover TLS misconfiguration hints, reconnect loops, response draining, and idempotent disconnect.
