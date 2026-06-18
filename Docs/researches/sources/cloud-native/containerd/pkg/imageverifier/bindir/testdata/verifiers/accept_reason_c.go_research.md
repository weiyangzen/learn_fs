# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_c.go

Purpose: third successful verifier fixture for max-verifier and ordering tests.

Important APIs/types/functions: `main` prints `Reason C` and exits with status 0.

Control flow: linear stdout write.

State/persistence: none.

Dependencies/integration: used by `bindir_test.go` with other accept fixtures to verify that `MaxVerifiers` limits execution after the configured number of sorted entries.

Risks: low. Output text is an asserted test contract.

Test signals: helps detect regressions where `MaxVerifiers` is ignored, directory ordering changes, or skipped verifiers still influence the final reason.
