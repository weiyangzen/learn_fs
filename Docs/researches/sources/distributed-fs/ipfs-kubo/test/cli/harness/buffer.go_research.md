# sources/distributed-fs/ipfs-kubo/test/cli/harness/buffer.go

Purpose: provides `Buffer`, a concurrency-safe output sink for subprocess stdout/stderr captured by the CLI harness.

Important APIs/types/functions: `Buffer` wraps a `strings.Builder` and `sync.Mutex`. It implements `Write(p []byte)`, `String()`, `Trimmed()`, `Bytes()`, and `Lines()`. `Lines` delegates line splitting to `testutils.SplitLines`.

Control flow: process runners write concurrently into the buffer through `Write`; readers acquire the same mutex and snapshot the builder contents. `Trimmed` removes at most one trailing newline, preserving other whitespace for exact-output assertions.

State and persistence: state is in-memory only. There is no file or repo persistence; the buffer stores subprocess output for the lifetime of a harness command result.

Dependencies/integration: integrated by `Runner.Run` as the default stdout/stderr capture target and by tests that inspect `RunResult.Stdout`/`Stderr`.

Risks: `strings.Builder` contents are copied into byte slices and strings on read, so very large command output can allocate. `Trimmed` only handles `\n`, not `\r\n`, which may matter on Windows-style output. Test signals are exact output comparisons, line parsing, and error diagnostics.
