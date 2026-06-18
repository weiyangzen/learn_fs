# sources/cloud-native/containerd/internal/fsverity/fsverity_other.go

## Purpose
Provides non-Linux stubs for the fs-verity API.

## Important APIs, Types, And Functions
`IsSupported`, `IsEnabled`, and `Enable` all return errors stating fs-verity is Linux-only.

## Control Flow
Every call exits immediately without side effects.

## State And Persistence
No state and no filesystem mutation.

## Dependencies And Integration Points
Uses only `fmt` and preserves the package API for non-Linux builds.

## Risks
Callers must not assume integrity support is available on non-Linux platforms.

## Test Signals
No direct non-Linux tests in this subset; compile coverage is the main signal.
