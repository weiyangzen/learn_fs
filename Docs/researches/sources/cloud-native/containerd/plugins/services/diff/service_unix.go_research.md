# sources/cloud-native/containerd/plugins/services/diff/service_unix.go

## Purpose
Defines default differ ordering for Unix platforms other than Windows and Darwin.

## Important APIs, Types, And Functions
`defaultDifferConfig` sets `Order` to `["walking"]` and `SyncFs` false.

## Control Flow
Loaded as package-level config for diff service registration.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Used by `local.go` to select diff plugins.

## Risks
Only walking differ is tried by default, so specialized differs must be configured or platform-specific defaults must change to use them.

## Test Signals
No direct tests.
