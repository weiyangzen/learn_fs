## sources/control-plane/csi-driver-iscsi/.github/workflows/windows.yaml

Purpose: verifies Go package tests on Windows.

Control flow uses a matrix with Go `^1.18` and `windows-latest`, checks out code, prints `go version`, and runs `go test -v -race ./pkg/...`. State is workflow output only.

Dependencies are setup-go, checkout, and package portability. Risks include most runtime iSCSI behavior being Linux/host-specific and therefore untested; compile-only portability is still useful for shared code. Test signal is race-test pass/fail.
