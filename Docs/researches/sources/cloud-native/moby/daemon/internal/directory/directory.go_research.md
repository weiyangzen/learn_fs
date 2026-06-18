# sources/cloud-native/moby/daemon/internal/directory/directory.go

## Purpose
Exposes a platform-neutral directory size API.

## APIs, Control Flow, and Integration
`Size(ctx, dir)` delegates to platform-specific `calcSize`. The public contract is to walk a tree and return total file bytes while honoring cancellation and platform-specific filesystem semantics.

## State, Dependencies, and Risks
No state is kept. The behavior is entirely determined by `directory_unix.go` or `directory_windows.go`. Callers must pass a context and handle errors for nonexistent roots. Tests in `directory_test.go` exercise the exported function rather than platform implementations directly.
