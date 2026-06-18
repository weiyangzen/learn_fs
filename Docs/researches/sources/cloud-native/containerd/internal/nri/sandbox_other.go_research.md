# sources/cloud-native/containerd/internal/nri/sandbox_other.go

## Purpose
Provides non-Linux pod sandbox conversion without Linux-specific fields.

## Important APIs, Types, And Functions
`podSandboxToNRI` returns `commonPodSandboxToNRI(pod)`.

## Control Flow
Build-tagged for `!linux`.

## State And Persistence
No state.

## Dependencies And Integration Points
Keeps the NRI package portable on non-Linux platforms.

## Risks
Non-Linux NRI plugins receive only platform-neutral pod metadata.

## Test Signals
No direct tests; compile coverage is the main signal.
