# sources/distributed-fs/beegfs-go/watch/internal/subscriber/subscriber.go

## Purpose

This file defines the common subscriber abstraction and thread-safe lifecycle state used by subscriber handlers independent of transport type.

## Important APIs, Types, And Functions

`Interface` requires `Connect`, `Send`, `Receive`, and `Disconnect`. The unexported `state` enum has `DISCONNECTED`, `CONNECTING`, `CONNECTED`, and `DISCONNECTING`. `State` wraps the current state with an RW mutex and provides `GetState`/`SetState`. `Subscriber` embeds `Config`, `State`, and the transport `Interface`. `ComparableSubscriber` is a test-only comparable view.

## Control Flow

The interface is intentionally lifecycle-oriented: handlers own state transitions, while concrete subscribers only perform connection operations. This separation lets `subscribermgr.Handler.Handle` implement common reconnection and send/receive logic.

## State And Persistence

State is process-local and thread-safe. No subscriber state is persisted in BeeWatch; durable acknowledgement state is expected to live in the subscriber service itself.

## Dependencies And Integration Points

It depends on generated `beewatch` protobuf event and response types. `subscriber/config.go` constructs subscribers, `grpc.go` implements the current interface, and `subscribermgr/handler.go` drives state transitions.

## Risks And Test Signals

The contract says `Disconnect` must be idempotent and `Connect` is not expected to be idempotent; concrete implementations must honor that or handlers can leak resources. The exported state constants are unexported type values, limiting misuse but still package-visible. Tests indirectly validate initial state through config tests.
