# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stdout_chunked.go

Purpose: chunked stdout stress fixture. It verifies that many small stdout writes are truncated and drained without hanging the verifier.

Important APIs/types/functions: `main` loops 500000 times, writes `A` to stdout, tracks total bytes, and logs progress and final count to stderr.

Control flow: repeated stdout writes; every 10000 iterations a progress line is written to stderr. Write errors are logged but do not stop the loop.

State/persistence: no persistent state.

Dependencies/integration: runs under `bindir.runVerifier` where stdout is read to a limit and then drained to avoid broken pipes.

Risks: high iteration count can make the test sensitive to slow CI. It intentionally exercises a worst-case path for scanner/pipe scheduling.

Test signals: catches regressions in stdout draining, truncation marker logic, and timeout handling for verbose verifier programs.
