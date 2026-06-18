# sources/cloud-native/nydus-snapshotter/cmd/converter/main.go

Purpose: build-only executable for converter package compatibility.

Flow/APIs: imports `pkg/converter` for side effects/compile validation and has an empty `main`.

State/dependencies: no runtime state; depends on converter package compiling for the target platform.

Integration points: Makefile `converter` and CI cross-build matrix use this to ensure converter code builds on linux/windows/darwin for amd64/arm64.

Risks/tests: no behavior is executed, so this catches compile-time portability but not converter runtime correctness.
