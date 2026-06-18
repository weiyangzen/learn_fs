# sources/cloud-native/containerd/pkg/ioutil/read_closer_test.go

Purpose: unit test for `NewWrapReadCloser` read and close behavior.

Important APIs/types/functions: `TestWrapReadCloser` wraps a `bytes.Buffer` containing `abc`, reads one byte at a time, then calls `Close` and checks that a subsequent read returns `(0, io.EOF)` without modifying the destination buffer.

Control flow: create wrapper, read first byte, read second byte, close early before consuming `c`, then assert EOF.

State/persistence: only in-memory buffer and pipe state.

Dependencies/integration: uses Go `bytes`, `io`, `testing`, and testify assertions. Tests the implementation in the same package.

Risks: does not assert behavior when the underlying reader blocks, returns errors, or is larger than pipe buffering. It also does not assert goroutine exit explicitly.

Test signals: verifies the core adapter contract that explicit close maps closed-pipe reads to EOF and that partial reads preserve byte order.
