# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stderr.go

Purpose: stress fixture for verifier stderr handling. It emits a large single write to stderr while returning success, so `bindir.runVerifier` must drain stderr without blocking or inflating the returned reason.

Important APIs/types/functions: `main` sets `n := 50000`, announces the intended write on stdout, writes `n` repeated `A` bytes to stderr, reports write errors to stdout, and prints the byte count written.

Control flow: one large stderr write through `fmt.Fprint(os.Stderr, strings.Repeat(...))`, then normal exit.

State/persistence: no persistent state.

Dependencies/integration: compiled and run by the `large output is truncated` subtest, alongside stdout variants.

Risks: pipe buffer behavior is platform-dependent; the fixture specifically guards against deadlocks when stderr exceeds `outputLimitBytes`.

Test signals: proves stderr is scanned/logged up to a bound, truncated remainder is discarded, and successful verification can complete even when stderr is much larger than the retained limit.
