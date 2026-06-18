# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/signal_wasm.go

Purpose: Provides the WASM-compatible interrupt handler implementation for the `cmd/ipfs/util` package. It avoids OS signal APIs and instead models interruption as a cancelable `context.Context`.

Important APIs/types/functions: `ctxCloser` adapts a `context.CancelFunc` to `io.Closer`. `SetupInterruptHandler(ctx)` returns that closer plus a derived context.

Control flow, state, and persistence: The only state is the derived context cancellation function. Calling `Close` cancels the context and returns nil. No persistent data, goroutines, or signal subscriptions are created in this WASM variant.

Dependencies and integration points: Depends only on `context` and `io`. It must match the non-WASM platform API so callers can call `SetupInterruptHandler` uniformly.

Risks and test signals: The main risk is behavioral drift from other platform implementations: WASM callers receive cancellation only when the returned closer is closed, not from OS signals. No direct tests in this subset cover it; compile/build-tag coverage is the primary signal.
