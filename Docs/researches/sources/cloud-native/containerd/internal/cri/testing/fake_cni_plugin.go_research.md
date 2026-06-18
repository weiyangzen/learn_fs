# sources/cloud-native/containerd/internal/cri/testing/fake_cni_plugin.go

## Purpose
Implements a fake CNI plugin for CRI tests that need a `go-cni`-compatible object without invoking real network setup.

## Important APIs, Types, And Functions
`FakeCNIPlugin` carries injectable `StatusErr` and `LoadErr`. `NewFakeCNIPlugin` constructs it. `Setup`, `SetupSerially`, `Remove`, `Check`, and `GetConfig` are no-op stubs; `Status` and `Load` return configured errors.

## Control Flow
Tests install the fake, configure status/load errors when needed, and exercise CRI code paths without side effects. Network setup and teardown always return successful empty results unless the tested path calls `Status` or `Load`.

## State And Persistence
Only the two error fields are stateful. There is no network, namespace, or CNI config persistence.

## Dependencies And Integration Points
Depends on `context` and `github.com/containerd/go-cni`. It is an internal test helper for CRI networking paths.

## Risks
Because setup/remove/check are always successful, tests using this fake do not cover CNI result parsing, interface ordering, namespace options, or cleanup failures.

## Test Signals
The file itself is test infrastructure. Its behavior is validated indirectly by CRI tests that use `NewFakeCNIPlugin`.
