# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/driver.rs

## Purpose
Implements the Rust Nova DRM auxiliary driver, DRM device registration, file/object type binding, and ioctl table.

## Important APIs, Types, And Functions
`NovaDriver`, `NovaDevice`, `NovaData`, `INFO`, and the auxiliary device table are central. The `auxiliary::Driver` impl probes `nova-drm` auxiliary devices. The `drm::Driver` impl declares `NOVA_GETPARAM`, `NOVA_GEM_CREATE`, and `NOVA_GEM_INFO` ioctls.

## Control Flow
Probe stores an `ARef` to the auxiliary device, creates a DRM device with that data, registers it as foreign-owned, and returns a driver instance holding the DRM reference.

## State, Persistence, And Dependencies
State is the DRM device reference in `NovaDriver` and the auxiliary device reference in `NovaData`. DRM core owns file and GEM object state.

## Integration Points
Depends on Rust-for-Linux auxiliary and DRM abstractions, Nova core auxiliary devices named `NovaCore.nova-drm`, and the file/GEM modules.

## Risks
The driver version is 0.0.0 and the driver is experimental. Registration lifetime relies on `ARef` and foreign-owned DRM registration semantics.

## Test Signals
Signals include auxiliary probe, DRM device node creation, ioctl registration, and successful open/GEM ioctl smoke tests.
