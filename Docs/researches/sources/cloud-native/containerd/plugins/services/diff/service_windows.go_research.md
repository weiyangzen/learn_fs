# sources/cloud-native/containerd/plugins/services/diff/service_windows.go

## Purpose
Defines Windows default differ ordering.

## Important APIs, Types, And Functions
`defaultDifferConfig` sets `Order` to `["windows", "windows-lcow"]` and `SyncFs` false.

## Control Flow
Loaded as package-level config for Windows diff service registration.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Pairs the WCOW differ with LCOW fallback in `local.go`.

## Risks
Startup requires both configured differ plugins to load. Fallback depends on WCOW differ returning `ErrNotImplemented` for LCOW mounts.

## Test Signals
No direct tests.
