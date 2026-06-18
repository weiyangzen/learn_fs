# sources/cloud-native/containerd/internal/dmverity/dmverity_other.go

## Purpose
Provides non-Linux stubs for the dm-verity API so packages can compile across platforms.

## Important APIs, Types, And Functions
`errUnsupported` is returned by `IsSupported`, `Format`, `Open`, `Close`, and `VerifyDevice`.

## Control Flow
Every operation immediately reports unsupported; `IsSupported` also returns `false`.

## State And Persistence
No state and no side effects.

## Dependencies And Integration Points
Uses only `fmt`. It preserves the same API surface as the Linux implementation under a `!linux` build tag.

## Risks
Callers must check support or handle errors; otherwise integrity features will fail on non-Linux platforms.

## Test Signals
No direct non-Linux tests in this subset. Compile coverage is the main signal.
