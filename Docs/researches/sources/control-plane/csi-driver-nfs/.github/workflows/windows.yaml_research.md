# sources/control-plane/csi-driver-nfs/.github/workflows/windows.yaml

Purpose: runs NFS driver package unit tests on Windows.

Important APIs and types: matrix contains Go `^1.16` on `windows-latest`, checkout, and `go test -v -race ./pkg/...`.

Control flow: install Go, checkout source, print Go version, run race-enabled tests.

State and persistence: workflow logs only.

Dependencies and integration: validates that package-level code compiles and tests outside Linux.

Risks: Windows cannot exercise Linux mount behavior, so coverage is limited to portable package code. Go `^1.16` is old compared with current build tooling.

Test signals: Windows race test status.
