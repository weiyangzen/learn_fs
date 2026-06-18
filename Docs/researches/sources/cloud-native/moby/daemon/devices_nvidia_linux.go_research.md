# sources/cloud-native/moby/daemon/devices_nvidia_linux.go

## Purpose
Implements Linux NVIDIA GPU device request support through the NVIDIA CDI hook and/or legacy `nvidia-container-runtime-hook`.

## Important APIs, Types, And Functions
- `getNVIDIADeviceDrivers` discovers helper binaries and returns driver entries for `nvidia.cdi`, `nvidia.runtime-hook`, and composite `nvidia`.
- `firstSuccessfulUpdater` tries multiple OCI spec updaters and returns on the first success.
- `injectNVIDIARuntimeHook` sets `NVIDIA_VISIBLE_DEVICES`, optional `NVIDIA_DRIVER_CAPABILITIES`, and appends a prestart hook.
- `getRequestedDevicesIDs` converts `DeviceRequest` count/IDs into device names.
- `countToDevices` creates numeric IDs.
- `cdiDeviceInjector.injectDevices` and `normalizeDeviceID` map Docker device IDs into fully qualified CDI names.

## Control Flow
Discovery registers CDI support if `nvidia-cdi-hook` exists and runtime-hook support if `nvidia-container-runtime-hook` exists. The composite `nvidia` driver advertises GPU/NVIDIA capabilities and tries the available updaters in order. Runtime-hook injection rejects `Count` plus `DeviceIDs`, treats negative count as `all`, zero count as no devices, appends environment variables, resolves the hook path, and adds a prestart hook. CDI injection normalizes IDs and delegates to the generic `cdi` device driver.

## State And Persistence
Mutates the OCI spec process environment and hooks, or CDI device requests through the CDI driver. It reads process environment for hook env passthrough but writes no daemon metadata.

## Dependencies And Integration Points
Depends on helper binaries on `PATH`, CDI device driver registration, Docker `DeviceRequest`, OCI runtime specs, internal capabilities, and shared error types. The prestart hook is deprecated in OCI but retained for compatibility.

## Risks And Edge Cases
Using deprecated prestart hooks may need future replacement. If CDI injection is selected but the generic CDI driver is not registered, the request fails. `Count == 0` returns no devices for NVIDIA while AMD's legacy path sets `void`. Simultaneous `Count` and `DeviceIDs` is rejected.

## Test Signals
Direct unit tests are absent here; expected signals are GPU integration tests verifying environment variables, CDI device injection, hook presence, and conflict errors.
