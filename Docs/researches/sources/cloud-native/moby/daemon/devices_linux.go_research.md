# sources/cloud-native/moby/daemon/devices_linux.go

## Purpose
Registers Linux GPU device drivers at daemon startup.

## Important APIs, Types, And Functions
- `RegisterGPUDeviceDrivers(cdiCache *cdi.Cache)` registers NVIDIA drivers if available, otherwise AMD if available.

## Control Flow
The function first calls `getNVIDIADeviceDrivers`; if any NVIDIA path is available it registers all returned NVIDIA drivers and returns. If NVIDIA is unavailable, it calls `getAMDDeviceDrivers` and registers the AMD driver if present.

## State And Persistence
Mutates the global in-memory `deviceDrivers` registry. No on-disk state is written.

## Dependencies And Integration Points
Depends on NVIDIA/AMD helper discovery and optional CDI cache. It is the platform entrypoint used by daemon initialization or device subsystem setup.

## Risks And Edge Cases
NVIDIA registration takes priority over AMD and returns early, so mixed-vendor hosts may not register AMD through this path. This prioritization mirrors `getFirstAvailableVendor` but can be limiting for heterogeneous GPU nodes.

## Test Signals
Vendor priority is indirectly tested in `devices_test.go`; full registration depends on helper binaries/CDI specs in integration environments.
