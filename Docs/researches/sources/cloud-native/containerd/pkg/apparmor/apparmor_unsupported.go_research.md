# sources/cloud-native/containerd/pkg/apparmor/apparmor_unsupported.go

## Purpose
Provides non-Linux AppArmor support detection.

## Important APIs, Types, And Functions
`hostSupports` returns false under a `!linux` build tag.

## Control Flow
Immediate false result.

## State And Persistence
No state.

## Dependencies And Integration Points
Keeps the AppArmor package portable.

## Risks
No AppArmor behavior is available on non-Linux builds.

## Test Signals
No direct tests; compile coverage is the signal.
