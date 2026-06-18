# sources/cloud-native/moby/daemon/oci_linux_test.go

## Purpose
This file tests selected Linux OCI spec assembly regressions and helper behavior.

## Important APIs, Types, And Functions
`setupFakeDaemon` creates a temporary rootfs, libnetwork controller, and fake image service. Tests exercise `Daemon.createSpec`, `getSourceMount`, `sysctlExists`-conditioned sysctls, and resource defaults. `fakeImageService.StorageDriver` supports snapshotter-related paths.

## Control Flow
Tests construct minimal containers/daemon state, call `createSpec`, and inspect the resulting spec. Root-only tests are skipped for non-root users. Cleanup detaches leaked `/dev/shm` mounts. CDI test registers a temporary CDI device definition and verifies additional GIDs are preserved after user setup and device injection.

## State, Persistence, And Dependencies
The tests create temp directories, libnetwork data dirs, optional mounts, and mutate package-level `deviceDrivers` around CDI registration. Dependencies include libnetwork, config store, container API types, OCI specs, Unix unmount, and gotest assertions/skips.

## Integration Points
These tests protect OCI spec interactions among CDI, tmpfs, IPC, read-only rootfs, sysctls, user namespace settings, mountinfo, and default resource structs.

## Risks And Edge Cases
Several tests require root because spec assembly can mount or inspect privileged paths. The cleanup loop repeatedly detaches `ShmPath` to handle over-mounts. Sysctl assertions depend on kernel support files existing.

## Test Signals
Coverage is regression-focused: CDI supplementary group preservation, no duplicate `/dev/shm`, `/dev/shm` not made read-only under read-only rootfs, explicit sysctls overriding implicit ones, host network suppressing implicit network sysctls, `getSourceMount("/")`, and empty/default resource structures.
