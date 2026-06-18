# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/reject_reason_d.go

Purpose: rejection verifier fixture. It emits a reason and exits nonzero so `VerifyImage` can convert verifier failure into `Judgement.OK=false` rather than a Go error.

Important APIs/types/functions: `main` prints `Reason D` to stdout and calls `os.Exit(1)`.

Control flow: stdout reason write, then explicit exit code 1.

State/persistence: none.

Dependencies/integration: used by bindir tests to verify rejection short-circuiting and reason formatting.

Risks: output and exit code are test contracts. If changed, rejection semantics assertions lose signal.

Test signals: confirms `cmd.Wait` `ExitError` is treated as verifier judgement data, not infrastructure failure, and that subsequent verifiers are not executed after rejection.
