# sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/handler_test.go

## Purpose

This file tests basic handler initialization and subscriber add/remove diffing logic for the subscriber manager.

## Important APIs, Types, And Functions

`TestNewHandler` constructs a logger, handler config, empty subscriber, and ring buffer, then asserts key handler fields are initialized. `TestEvaluateChangedSubscribers` builds current handler IDs 1 and 2 and new subscriber IDs 1 and 3, then asserts ID 3 is added, ID 2 removed, and ID 1 verified.

## Control Flow

The tests call package-private functions `newHandler` and `evaluateAddedAndRemovedSubscribers`, using testify assertions to validate returned state and maps.

## State And Persistence

No persistence exists. `TestNewHandler` also implicitly verifies `newHandler` adds a cursor by creating a usable buffer, although it does not assert cursor map contents directly.

## Dependencies And Integration Points

It depends on `subscriber.Subscriber`, `types.NewMultiCursorRingBuffer`, zap development logger, and testify. It protects manager update behavior used during dynamic config reload.

## Risks And Test Signals

The tests do not exercise `Handle`, `connectLoop`, send/receive loops, or disconnect paths. They are useful smoke tests for construction and diffing but leave the subscriber delivery state machine largely untested.
