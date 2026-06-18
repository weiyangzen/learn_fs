# sources/cloud-native/containerd/pkg/imageverifier/bindir/testdata/verifiers/accept_reason_b.go

Purpose: second successful verifier fixture used to prove multiple accepting verifiers are executed and their reasons are ordered by directory entry sorting.

Important APIs/types/functions: `main` prints `Reason B` to stdout and returns normally.

Control flow: single stdout write followed by implicit zero exit.

State/persistence: no state.

Dependencies/integration: built into a standalone binary for `bindir_test.go`. It is commonly placed after `accept_reason_a` in temporary verifier directories.

Risks: exact output is part of test expectations. The fixture intentionally does not inspect argv or stdin, so it only validates aggregation behavior.

Test signals: confirms successful verifier reasons are appended after prior success reasons with the expected comma separator and verifier binary name prefix.
