<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_io_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_io_windows.go

Purpose: implements Windows named-pipe stdio setup for the remote containerd client.

Important APIs and types: `delayedConnection` implements `Read`, `Write`, and `Close` over an eventually accepted pipe connection. `stdioPipes` groups stdin/stdout/stderr. `newStdioPipes` creates and accepts the named pipes from a `cio.FIFOSet`.

Control flow: for each configured pipe path, the client calls `winio.ListenPipe`, creates a `delayedConnection`, and starts a goroutine to accept the shim connection. Reads/writes block on a `WaitGroup` until accept succeeds or close unblocks waiters. On setup failure, deferred cleanup closes already-created listeners/connections.

State and persistence: state is in-memory listener/connection state plus Windows named pipe endpoints. `sync.Once` ensures waiters are unblocked once.

Dependencies and integration: used by `client_windows.go` `newDirectIO`, which adapts named pipes into `cio.NewDirectIOFromFIFOSet`.

Risks: failed accept closes the delayed connection and future I/O gets `net.ErrClosed`. Callers must close pipes to unblock waiters. There is no explicit accept timeout, so leaked listeners could block I/O users.

Test signals: no direct tests in this subset; behavior is platform integration with runhcs/containerd shims.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_io_windows.go -->
