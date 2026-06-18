# sources/cloud-native/moby/daemon/devices.go

## Purpose
Defines the daemon's pluggable device request registry and generic device selection logic, primarily used for GPU requests.

## Important APIs, Types, And Functions
- `deviceDrivers` is the process-global registry by driver name.
- `deviceDriver` holds a capability set, an OCI spec updater, and optional device listing function.
- `deviceInstance` pairs a Docker `DeviceRequest` with selected capabilities.
- `registerDeviceDriver` inserts a driver.
- `getFirstAvailableVendor` chooses the first known GPU vendor in NVIDIA-then-AMD priority.
- `Daemon.handleDevice` selects a driver by capability match or explicit driver name and invokes its `updateSpec`.

## Control Flow
For requests without an explicit driver, `handleDevice` scans registered drivers for a matching capability set and uses the first match. For explicit drivers, it uses the named driver if registered and logs that capabilities may be ignored. If no suitable driver exists, it returns `incompatibleDeviceRequest`.

## State And Persistence
Device driver registration is global in process memory. `handleDevice` mutates the supplied OCI spec through the selected driver's updater but writes no daemon metadata itself.

## Dependencies And Integration Points
Integrates Docker API device requests, internal capability matching, OCI runtime specs, GPU registration from platform files, and error typing in `errors.go`.

## Risks And Edge Cases
Map iteration order can affect implicit driver selection when multiple registered drivers match the same capability set, though current Linux registration returns after registering one vendor family. Explicit driver requests bypass strict capability validation by design.

## Test Signals
`devices_test.go` covers vendor selection priority and error cases. Device spec mutation is covered by GPU-specific tests/integration outside this subset.
