<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/attach_context.go -->
# sources/cloud-native/moby/daemon/container/attach_context.go

## Purpose
Manages a lazily-created cancelable context shared by attach calls for one container.

## Important APIs, Types, And Functions
`attachContext` holds a mutex, context, and cancel function. `init` creates or returns the current context. `cancel` cancels and clears it.

## Control Flow
Both methods lock around context state. After cancellation, a future `init` creates a fresh background-derived context.

## State And Persistence Behavior
In-memory only; cancellation is used to detach active attach operations.

## Dependencies And Integration Points
Used by `Container.AttachContext` and `Container.CancelAttachContext` in `container.go`.

## Risks And Test Signals
Risks include background context lacking daemon cancellation and concurrent attach calls observing a context just before cancellation. Attach behavior tests/integration are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/attach_context.go -->
