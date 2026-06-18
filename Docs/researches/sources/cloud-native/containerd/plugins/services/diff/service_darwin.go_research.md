# sources/cloud-native/containerd/plugins/services/diff/service_darwin.go

## Purpose
Defines Darwin default differ ordering.

## Important APIs, Types, And Functions
`defaultDifferConfig` sets `Order` to `["erofs", "walking"]` and `SyncFs` false.

## Control Flow
Loaded as package-level default config for the diff service on Darwin.

## State And Persistence
No state beyond default configuration.

## Dependencies And Integration Points
Used by `local.go` service registration.

## Risks
If EROFS plugin is unavailable and still listed as required, diff service startup can fail unless plugin loading/config generation accounts for support.

## Test Signals
No direct tests.
