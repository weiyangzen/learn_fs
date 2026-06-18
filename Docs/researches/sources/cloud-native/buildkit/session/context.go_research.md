<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/context.go -->
# sources/cloud-native/buildkit/session/context.go

Purpose: links request contexts to session caller contexts so requests cancel when the underlying session closes.

Important APIs, types, and functions: `contextWithCaller(ctx, callerCtx)` returns a context canceled either by the base request context or by `callerCtx` via `context.AfterFunc`, preserving the caller cancellation cause when present.

Control flow and state: no persistence. It creates a cancel-cause context and registers an AfterFunc on the caller context.

Dependencies and integration: used by `client.Context` in `manager.go`, affecting every session caller request.

Risks and test signals: AfterFunc is not explicitly stopped, relying on context lifecycle. `context_test.go` verifies caller cancellation and request cancellation causes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/context.go -->
