<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/e/error.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/e/error.go

## Purpose

Provides small error helpers for command handlers and post-run code.

## Important APIs, Types, and Functions

`TypeErr(expected, actual)` returns a type mismatch error. `HandlerError` wraps an error with a debug stack. `New(err)` constructs `HandlerError`.

## Control Flow

`TypeErr` formats expected and actual dynamic types. `HandlerError.Error` prints the wrapped error plus stack trace. A compile-time assignment verifies `HandlerError` implements `error`.

## State and Persistence Behavior

No persistent state. `New` captures the current goroutine stack at construction time.

## Dependencies and Integration Points

Uses standard `fmt` and `runtime/debug`. Used by post-run handlers such as `get.go` and `filestore.go` when response values have unexpected types.

## Risks and Edge Cases

`New(nil)` is valid by compile check but calling `Error` on a nil wrapped error would panic. Stack traces may be verbose for user-facing output if surfaced directly.

## Test Signals

No direct tests. Coverage should include expected formatting and nil handling expectations if callers can pass nil.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/e/error.go -->
