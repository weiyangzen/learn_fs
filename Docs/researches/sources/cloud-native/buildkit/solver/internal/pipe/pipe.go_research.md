<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/internal/pipe/pipe.go -->
## sources/cloud-native/buildkit/solver/internal/pipe/pipe.go

Purpose: implements a small generic request/status pipe between scheduler senders and receivers, including cancellation propagation to function-backed work.

Important APIs and types: `Pipe`, `Request`, `Sender`, `Receiver`, `Status`, `New`, and `NewWithFunction`. Internal `channel` uses `atomic.Pointer` to publish the latest value and detect whether a receiver has already consumed it.

Control flow: `New` wires a sender status channel and receiver cancel channel, with optional completion callbacks. `Sender.Update` publishes intermediate status; `Finalize` marks completion, stores error/value, and sets `Canceled` when the sender observed a canceled request and the error is `context.Canceled`. `Receiver.Cancel` sends a canceled request back to the sender. `NewWithFunction` wraps a function with a cancelable context and finalizes the pipe when the function returns.

State and dependencies: state is in-memory; sender protects request mutation with a mutex, receiver stores last status locally, and atomic channels hold most recent messages. Dependencies are `context`, `sync`, `sync/atomic`, and `pkg/errors`.

Integration points: scheduler request dispatch uses pipes to communicate edge requests, function requests, status updates, and cancellation.

Risks and test signals: the channel is latest-value rather than queueing, so intermediate updates may be coalesced. `pipe_test.go` covers normal completion and cancellation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/internal/pipe/pipe.go -->
