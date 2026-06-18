# sources/cloud-native/containerd/core/runtime/v2/bundle_test.go

## Purpose
Keeps the shared bundle test package importing `testutil` on all platforms so test flags and platform-specific test wiring remain available even when Linux-only tests are excluded.

## APIs, Flow, State, Dependencies, Risks, And Tests
The file has no executable tests and no exported API. It contains a blank import of `github.com/containerd/containerd/v2/pkg/testutil`.

There is no runtime state or control flow. Integration is with Go's test binary construction: when `bundle_linux_test.go` is not compiled, this file still ensures the package-level test utility side effects and flags are present.

Risks are minimal; removing it could create cross-platform test flag drift. The test signal is successful package test compilation on non-Linux platforms.
