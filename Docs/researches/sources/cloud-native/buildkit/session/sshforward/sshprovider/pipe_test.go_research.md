## sources/cloud-native/buildkit/session/sshforward/sshprovider/pipe_test.go

Purpose: provides an in-memory `net.Listener` built on `net.Pipe` for SSH provider tests.

Important APIs/types/functions: `pipeListener` implements `net.Listener`. `Accept` initializes channels lazily, waits for dialed connections, tracks accepted conns, and returns `net.ErrClosed` after close. `Dialer(ctx)` creates a pipe pair and sends one side to `Accept`, honoring context cancellation. `Addr` returns a simple `pipeAddr`. `Close` closes the accept channel and all tracked conns.

Control flow: `Dialer` and `Accept` rendezvous over `chConn`. Close sets `closed`, closes the channel, and closes accepted connections. `Accept` also handles nil receives from a closed channel.

State and persistence: only test-scoped in-memory state: mutex, closed flag, accepted conns, channel, and unused `closedCh` field. `closedCh` is initialized and selected in `Accept` but never closed, so channel closure via `chConn` is what actually unblocks accepts.

Dependencies and integration points: used by `raw_provider_test.go` to run both the gRPC server transport and echo backend without OS sockets.

Risks and test signals: the unused `closedCh` looks stale but does not break current tests because `chConn` is closed. Since it is test-only, production risk is none.
