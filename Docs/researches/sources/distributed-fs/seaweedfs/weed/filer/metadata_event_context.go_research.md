# sources/distributed-fs/seaweedfs/weed/filer/metadata_event_context.go

## Purpose

`metadata_event_context.go` provides a context flag to suppress automatic metadata event emission for nested filer operations that are part of one higher-level change.

## Important APIs, Types, and Functions

`WithSuppressedMetadataEvents` returns a derived context containing a private key. `metadataEventsSuppressed` reads the flag and treats nil contexts as not suppressed.

## Control Flow

Callers wrap a context before invoking lower-level filer operations. Event-producing code checks `metadataEventsSuppressed(ctx)` and skips local event emission when true.

## State and Persistence Behavior

There is no persistent state. Suppression is scoped to the context tree and disappears when the context is discarded.

## Dependencies and Integration Points

The file depends only on Go `context`. It integrates with filer operations such as rename or composite updates that would otherwise emit duplicate create/delete notifications.

## Risks and Edge Cases

The key type is private, avoiding collisions. Suppression does not cross goroutines unless the context is explicitly passed. Overuse can hide legitimate metadata events and break subscribers.

## Test Signals

Unit tests should verify nil context behavior, inherited suppression through derived contexts, and that composite filer operations emit only the intended outer event.
