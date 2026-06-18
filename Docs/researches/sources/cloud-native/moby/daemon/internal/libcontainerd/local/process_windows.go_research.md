<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/process_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/local/process_windows.go

Purpose: provides small Windows HCS process I/O helpers used by the local libcontainerd implementation.

Important APIs and types: `autoClosingReader` wraps an `io.ReadCloser` and closes it once a read returns an error. `createStdInCloser` wraps an HCS process stdin pipe so closing Docker's writer also closes HCS stdin.

Control flow: `autoClosingReader.Read` delegates to the wrapped reader and uses `sync.Once` to close it on any read error. `createStdInCloser` closes the pipe first, then calls `process.CloseStdin`; it suppresses expected HCS not-exist/already-closed and selected invalid-state errors.

State and persistence: no persistent state; `sync.Once` prevents duplicate close calls. It mutates HCS process state through `CloseStdin`.

Dependencies and integration: depends on `hcsshim` error classification and Docker `ioutils.NewWriteCloserWrapper`. `local_windows.go` uses these helpers when converting HCS process stdio into `cio.DirectIO`.

Risks: any HCS error classification drift can expose benign shutdown races as user-visible errors. Closing on every read error assumes EOF/error means no future data should be read.

Test signals: no direct test in this subset; behavior is exercised only through Windows process I/O integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/process_windows.go -->
