# sources/cloud-native/containerd/plugins/diff/erofs/dmverity_other.go

## Purpose
Provides the non-Linux dm-verity formatting stub for the EROFS differ.

## Important APIs, Types, And Functions
`formatDmverityLayer` returns an explicit unsupported-platform error.

## Control Flow
The method immediately fails when called.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Compiled under `!linux`. It preserves the common `erofsDiff.Apply` call shape while preventing silent dm-verity no-ops on unsupported platforms.

## Risks
If dm-verity is enabled through config on non-Linux builds, apply fails at runtime rather than formatting. Plugin-level checks should prevent most unsupported configurations.

## Test Signals
No direct tests. Build tags validate compilation.
