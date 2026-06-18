# sources/cloud-native/cri-o/internal/factory/container/device_test.go

## Purpose
Tests Linux device handling in the container factory, including host-device exposure policy, device node ownership, and CDI device injection from both structured CRI fields and legacy annotations.

## Important APIs, Types, And Functions
- Exercises `sut.SpecAddDevices` and `sut.SpecInjectCDIDevices`.
- Uses `devices.HostDevices()` to choose real host device fixtures and `types.ContainerConfig.Devices` for CRI device requests.
- Defines `writeCDISpecFiles` to create temporary CDI YAML specs and configure the CDI registry for each test.

## Control Flow
The first table toggles privileged state and `privilegedWithoutHostDevices` to assert whether host devices are copied into the spec. The second table builds a single CRI device request from an actual host device and checks UID/GID selection with or without `deviceOwnershipFromSecurityContext`. The CDI table writes optional CDI spec files, configures container annotations or `CDIDevices`, calls injection, and verifies either errors or expected env/device edits.

## State And Persistence
Uses temporary CDI spec directories and mutates the package-global CDI registry configuration during tests. The OCI spec generator records injected devices and process environment entries. No CRI-O persistent container state is written.

## Dependencies And Integration Points
Integrates runc device discovery, CRI API security contexts and CDI fields, runtime-spec Linux devices, and the CNCF CDI registry/parser. It relies on the shared test framework and the factory `sut` initialized in `suite_test.go`.

## Risks And Edge Cases
Tests depend on host device availability and on at least one host device for ownership assertions. CDI registry global state can leak if not reset by framework/process isolation. Root-owned devices and equal UID/GID devices are handled by fallback selection logic.

## Test Signals
Strong signal for host-device policy and CDI behavior. It covers nil/empty CDI input, malformed CDI names, unresolved devices, successful multi-vendor injection, annotation-based injection, and expected device/env edits.
