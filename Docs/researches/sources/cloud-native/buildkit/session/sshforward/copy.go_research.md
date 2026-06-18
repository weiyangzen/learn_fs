## sources/cloud-native/buildkit/session/sshforward/copy.go

Purpose: bridges an `io.ReadWriteCloser` such as an SSH agent socket and a bidirectional gRPC stream carrying `BytesMessage` chunks.

Important APIs/types/functions: `Stream` is the minimal gRPC-like interface with `SendMsg` and `RecvMsg`. `Copy(ctx, conn, stream, closeStream)` pumps bytes in both directions and closes resources on EOF, stream errors, connection errors, or context cancellation.

Control flow: an `errgroup` starts two goroutines. The receive-to-conn goroutine repeatedly receives a `BytesMessage`, writes its data to `conn`, and reuses the message buffer. If the stream returns EOF, it half-closes the write side when `conn` supports `CloseWrite`; otherwise it closes the connection. The conn-to-stream goroutine reads up to 32 KiB from `conn`, sends each chunk, and calls `closeStream` on connection EOF so gRPC clients can see CloseSend. Both goroutines check context cancellation after blocking I/O and return `context.Cause(ctx)` when canceled.

State and persistence: no persistent state; only transient buffers and a connection lifecycle. `defer conn.Close()` plus explicit closes make shutdown aggressive.

Dependencies and integration points: used by the SSH socket mount listener and provider server. It depends on `errgroup` and `pkg/errors` for concurrent error propagation and wrapping.

Risks and test signals: close races are expected and largely benign, but the first non-nil errgroup error wins. The code assumes byte framing is not semantically meaningful beyond ordering. `raw_provider_test.go` exercises bidirectional message flow, larger payloads, and stream adapters.
