# sources/cloud-native/moby/daemon/devices_amd_linux.go

## Purpose
Implements Linux AMD GPU device request support through CDI when available or the legacy `amd-container-runtime` environment variable path.

## Important APIs, Types, And Functions
- `setAMDGPUs` sets `AMD_VISIBLE_DEVICES` from `DeviceIDs`, `Count`, all devices, or `void`.
- `createAMDCDIUpdater` discovers CDI vendors and injects normalized `amd.com/gpu` CDI device names.
- `getAMDDeviceDrivers` builds a composite updater from CDI and/or `amd-container-runtime`.

## Control Flow
AMD driver setup adds a CDI updater if a CDI cache exists, adds a runtime-env updater if the helper binary is on `PATH`, and returns nil if neither path is available. At runtime, the composite updater tries CDI first, then environment injection. `setAMDGPUs` rejects simultaneous `Count` and `DeviceIDs`.

## State And Persistence
Mutates only the OCI spec process environment or CDI device annotations through the delegated CDI updater. No daemon persistent state is written.

## Dependencies And Integration Points
Uses CDI cache vendor discovery, shared `cdiDeviceInjector` from NVIDIA support, the global device driver registry, and external `amd-container-runtime` discovery through `exec.LookPath`.

## Risks And Edge Cases
CDI vendor discovery must find `amd.com`; otherwise CDI update fails and the composite may fall back to env injection. A request with `Count == 0` produces `AMD_VISIBLE_DEVICES=void`, which is a meaningful legacy-runtime behavior but differs from NVIDIA's no-op for zero.

## Test Signals
Direct tests cover vendor priority through `getFirstAvailableVendor`. Full AMD behavior depends on CDI specs or helper binary integration tests.
