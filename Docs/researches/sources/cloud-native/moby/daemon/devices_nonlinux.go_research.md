# sources/cloud-native/moby/daemon/devices_nonlinux.go

## Purpose
Provides a no-op GPU device registration function on non-Linux platforms.

## Important APIs, Types, And Functions
- `RegisterGPUDeviceDrivers(_ *cdi.Cache)` intentionally does nothing.

## Control Flow
Returns immediately.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Selected by `!linux` build tag while preserving the same public function name for generic callers.

## Risks And Edge Cases
GPU device requests on non-Linux cannot be satisfied by this registration path and will fall through to incompatible device errors.

## Test Signals
Compilation on non-Linux platforms and API behavior for unsupported device requests are the main signals.
