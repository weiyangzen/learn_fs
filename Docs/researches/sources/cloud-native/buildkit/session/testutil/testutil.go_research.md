## sources/cloud-native/buildkit/session/testutil/testutil.go

Purpose: provides an in-memory session dialer for tests without opening network sockets.

Important APIs/types/functions: `Handler` handles an incoming connection and metadata. `Dialer` mirrors the session dialer signature. `TestStream(handler)` returns a dialer backed by `sockPair`. `sockPair` builds two cross-connected `io.Pipe` based `net.Conn` implementations. `sock` implements `net.Conn` methods with no-op deadlines and dummy addresses.

Control flow: each call to the returned dialer launches the handler in a goroutine with `context.WithoutCancel(ctx)` and one side of the pipe, logs handler errors, closes that side, and returns the other side to the session under test.

State and persistence: transient pipe pairs only.

Dependencies and integration points: used by session tests that need to connect `Session.Run` to a fake manager/handler. Uses `bklog` for handler error logging.

Risks and test signals: deadlines are no-ops, so tests using timeout behavior may not model real net.Conn semantics. `context.WithoutCancel` intentionally keeps handler work alive past dialer context cancellation, which is useful for sessions but can hide cancellation bugs.
