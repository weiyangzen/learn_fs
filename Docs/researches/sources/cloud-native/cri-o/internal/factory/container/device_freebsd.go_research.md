# sources/cloud-native/cri-o/internal/factory/container/device_freebsd.go

## Purpose
Provides FreeBSD-specific stubs for container device setup. Device addition is a no-op on FreeBSD, while CDI injection is unsupported unless no CDI devices were requested.

## Important APIs, Types, And Functions
- `(*container).SpecAddDevices(configuredDevices, annotationDevices []devicecfg.Device, privilegedWithoutHostDevices, enableDeviceOwnershipFromSecurityContext bool) error` returns nil without mutating the spec.
- `(*container).SpecInjectCDIDevices() error` returns an unsupported-platform error only when `c.Config().CDIDevices` is non-empty.

## Control Flow
FreeBSD callers can invoke the same factory API as Linux code, but no Linux device nodes or cgroup device resources are added. CDI is treated as a conditional feature: empty CDI input succeeds, requested CDI input fails with a message including `runtime.GOOS`.

## State And Persistence
No state is persisted and no OCI device state is changed. The only observable behavior is error/no-error selection based on requested CDI devices.

## Dependencies And Integration Points
Keeps the common container factory interface buildable on FreeBSD while importing only `devicecfg`, `runtime`, and `fmt`. It avoids Linux-only runc device and CDI injection behavior.

## Risks And Edge Cases
FreeBSD callers expecting CRI device mappings to be enforced will get a silent no-op. CDI requests are rejected, but ordinary configured device lists are accepted without effect.

## Test Signals
No dedicated FreeBSD test is in this subset; coverage is primarily compile-time platform selection plus common factory interface expectations.
