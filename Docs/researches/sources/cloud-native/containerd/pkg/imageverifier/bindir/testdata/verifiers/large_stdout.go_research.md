# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/large_stdout.go

Purpose: stdout stress fixture for returned verifier reason truncation. It emits more stdout than `outputLimitBytes`, forcing the caller to retain a bounded reason and discard the rest safely.

Important APIs/types/functions: `main` writes an informational line to stderr, prints 50000 repeated `A` bytes to stdout in one call, reports stdout write errors to stderr, and logs the written count.

Control flow: single large stdout write followed by normal exit.

State/persistence: none.

Dependencies/integration: used by `bindir_test.go` in the large-output suite. `runVerifier` reads stdout with a limited reader, marks truncation, then drains the remainder.

Risks: pipe buffering can expose deadlocks if the parent stops reading after the limit without discarding. Exact length is chosen to exceed the 32 KiB limiter.

Test signals: validates bounded `Judgement.Reason` size and confirms large stdout does not prevent process completion.
