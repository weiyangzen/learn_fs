# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stderr_chunked.go

Purpose: stderr stress fixture that writes many small chunks instead of one large buffer. It covers a different pipe-buffer and scanner interaction than `large_stderr.go`.

Important APIs/types/functions: `main` loops 500000 times, printing one `A` byte to stderr each iteration, tracking bytes written, and periodically reporting progress to stdout.

Control flow: repeated stderr writes with progress messages every 10000 iterations; write errors are reported to stdout and execution continues.

State/persistence: none.

Dependencies/integration: used by the bindir truncation test to ensure long-running chunked stderr output does not block verifier completion.

Risks: slow on loaded systems because it performs many small formatted writes. Output sizes and progress messages are part of a stress profile rather than exact assertions.

Test signals: catches regressions where stderr draining only works for one large write but deadlocks or times out when the verifier writes incrementally.
