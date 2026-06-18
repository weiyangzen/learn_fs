# sources/control-plane/csi-driver-nfs/.github/workflows/darwin.yaml

Purpose: runs NFS driver package unit tests on macOS.

Important APIs and types: triggers on all pushes and pull requests. The job uses `macos-latest`, setup-go `^1.16`, checkout, and `go test -v -race ./pkg/...`.

Control flow: setup Go, checkout source, print Go version, run race-enabled tests for package code.

State and persistence: no repo writes; GitHub test logs only.

Dependencies and integration: validates cross-platform package behavior outside Linux-specific container build paths.

Risks: Go `^1.16` is old relative to current build/scanning workflows. Tests that require Linux-only behavior should be guarded or skipped in package code.

Test signals: macOS race test pass/fail.
